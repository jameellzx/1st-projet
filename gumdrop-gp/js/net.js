// Online play over WebRTC (PeerJS). One player hosts; everyone else connects to the host,
// and the host relays messages between players.

const PREFIX = 'gumdropgp-v1-';
const ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';

export function makeCode() {
  let s = '';
  for (let i = 0; i < 5; i++) s += ALPHABET[Math.floor(Math.random() * ALPHABET.length)];
  return s;
}

export class Net {
  constructor() {
    this.peer = null;
    this.isHost = false;
    this.conns = new Map();
    this.hostConn = null;
    this.handlers = {};
    this.id = null;
  }

  on(ev, fn) { this.handlers[ev] = fn; }
  emit(ev, ...a) { if (this.handlers[ev]) this.handlers[ev](...a); }

  host(tries = 0) {
    return new Promise((resolve, reject) => {
      if (!window.Peer) return reject(new Error('Online library did not load. Check your internet connection.'));
      const code = makeCode();
      const peer = new window.Peer(PREFIX + code, { debug: 1 });
      let opened = false;
      peer.on('open', id => {
        opened = true;
        this.peer = peer; this.isHost = true; this.id = id;
        resolve(code);
      });
      peer.on('error', err => {
        if (!opened) {
          peer.destroy();
          if (err.type === 'unavailable-id' && tries < 4) this.host(tries + 1).then(resolve, reject);
          else reject(err);
        } else this.emit('error', err);
      });
      peer.on('connection', conn => {
        conn.on('open', () => { this.conns.set(conn.peer, conn); });
        conn.on('data', d => this._fromClient(conn, d));
        conn.on('close', () => { if (this.conns.delete(conn.peer)) this.emit('left', conn.peer); });
        conn.on('error', () => {});
      });
      peer.on('disconnected', () => { try { if (!peer.destroyed) peer.reconnect(); } catch (e) { /* ignore */ } });
    });
  }

  _fromClient(conn, d) {
    if (!d || typeof d !== 'object') return;
    d.from = conn.peer;
    if (d.t !== 'st' && d.t !== 'join') {
      for (const [id, c] of this.conns) if (id !== conn.peer && c.open) c.send(d);
    }
    this.emit('message', d);
  }

  join(code) {
    return new Promise((resolve, reject) => {
      if (!window.Peer) return reject(new Error('Online library did not load. Check your internet connection.'));
      const peer = new window.Peer({ debug: 1 });
      let done = false;
      const finish = (err) => {
        if (done) return;
        done = true; clearTimeout(timer);
        if (err) { try { peer.destroy(); } catch (e) { /* ignore */ } reject(err); } else resolve();
      };
      const timer = setTimeout(() => finish(new Error('Could not reach that room. Check the code.')), 15000);
      peer.on('open', id => {
        this.peer = peer; this.id = id;
        const conn = peer.connect(PREFIX + code, { reliable: true });
        conn.on('open', () => { this.hostConn = conn; finish(); });
        conn.on('data', d => this.emit('message', d));
        conn.on('close', () => this.emit('hostLeft'));
        conn.on('error', () => {});
      });
      peer.on('error', err => {
        if (!done) finish(err.type === 'peer-unavailable' ? new Error('No room with that code.') : err);
        else this.emit('error', err);
      });
    });
  }

  // Host: to every player. Player: to the host (who relays it on).
  send(d) {
    if (this.isHost) { for (const c of this.conns.values()) if (c.open) c.send(d); }
    else if (this.hostConn && this.hostConn.open) this.hostConn.send(d);
  }

  sendTo(id, d) { const c = this.conns.get(id); if (c && c.open) c.send(d); }

  close() {
    this.handlers = {};
    try { if (this.peer) this.peer.destroy(); } catch (e) { /* ignore */ }
    this.peer = null; this.conns.clear(); this.hostConn = null;
  }
}
