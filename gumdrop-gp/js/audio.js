// Small synthesized sound effects (no audio files needed).
export class Sfx {
  init() {
    if (this.ctx) { this.ctx.resume(); return; }
    const C = window.AudioContext || window.webkitAudioContext;
    if (!C) return;
    const c = this.ctx = new C();
    this.master = c.createGain();
    this.master.gain.value = 0.55;
    this.master.connect(c.destination);
    this.eng = c.createOscillator();
    this.eng.type = 'sawtooth';
    this.engF = c.createBiquadFilter();
    this.engF.type = 'lowpass';
    this.engF.frequency.value = 520;
    this.engG = c.createGain();
    this.engG.gain.value = 0;
    this.eng.connect(this.engF).connect(this.engG).connect(this.master);
    this.eng.start();
    const len = c.sampleRate * 0.5;
    this.noiseBuf = c.createBuffer(1, len, c.sampleRate);
    const d = this.noiseBuf.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
  }
  engine(frac, on) {
    if (!this.ctx) return;
    const t = this.ctx.currentTime;
    this.eng.frequency.setTargetAtTime(48 + frac * 150, t, 0.05);
    this.engG.gain.setTargetAtTime(on ? 0.05 : 0, t, 0.1);
  }
  tone(f, d = 0.12, type = 'square', vol = 0.12, slide = 0, delay = 0) {
    if (!this.ctx) return;
    const c = this.ctx, t = c.currentTime + delay;
    const o = c.createOscillator(), g = c.createGain();
    o.type = type;
    o.frequency.setValueAtTime(f, t);
    if (slide) o.frequency.exponentialRampToValueAtTime(Math.max(30, f * slide), t + d);
    g.gain.setValueAtTime(vol, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + d);
    o.connect(g).connect(this.master);
    o.start(t); o.stop(t + d + 0.02);
  }
  noise(d = 0.25, vol = 0.2, freq = 900) {
    if (!this.ctx) return;
    const c = this.ctx, t = c.currentTime;
    const s = c.createBufferSource(); s.buffer = this.noiseBuf;
    const f = c.createBiquadFilter(); f.type = 'bandpass'; f.frequency.value = freq;
    const g = c.createGain();
    g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.001, t + d);
    s.connect(f).connect(g).connect(this.master);
    s.start(t); s.stop(t + d);
  }
  count(n) { this.tone(n > 0 ? 440 : 880, n > 0 ? 0.2 : 0.5, 'square', 0.14); }
  boost() { this.tone(200, 0.45, 'sawtooth', 0.1, 3.5); this.noise(0.4, 0.12, 2000); }
  tick(tier) { this.tone(500 + tier * 220, 0.07, 'triangle', 0.1); }
  pick() { this.tone(880, 0.06, 'square', 0.08); this.tone(1320, 0.1, 'square', 0.08, 0, 0.06); }
  item() { this.tone(660, 0.1, 'triangle', 0.12, 0.6); }
  throw() { this.tone(400, 0.15, 'square', 0.1, 2); }
  hit() { this.noise(0.4, 0.3, 600); this.tone(320, 0.35, 'square', 0.1, 0.3); }
  bump() { this.noise(0.12, 0.18, 300); }
  shield() { this.tone(520, 0.3, 'sine', 0.12, 1.8); }
  lap() { this.tone(660, 0.12, 'square', 0.1); this.tone(990, 0.2, 'square', 0.1, 0, 0.12); }
  fanfare() { [523, 659, 784, 1046].forEach((f, i) => this.tone(f, 0.22, 'square', 0.12, 0, i * 0.14)); }
}
