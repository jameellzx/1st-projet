import * as THREE from 'three';
import { CHARACTERS, TRACKS, LAPS, MAX_RACERS, ITEM_INFO, rollItem, charById, trackById, hex } from './data.js';
import { Track } from './track.js';
import { buildKart, buildItemMesh, buildItemBox, Particles } from './models.js';
import { Net } from './net.js';
import { Sfx } from './audio.js';

const $ = id => document.getElementById(id);
const params = new URLSearchParams(location.search);
const sfx = new Sfx();

const G = {
  screen: 's-title', mode: null, name: 'Racer', charId: 'pip', trackId: 'gumdrop',
  net: null, myId: 'me', lobby: [], race: null, roomCode: null, joinCode: null,
  autopilot: params.has('autopilot'),
};
window.__game = G;

// ---------------------------------------------------------------- renderer
const renderer = new THREE.WebGLRenderer({ canvas: $('game'), antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(70, 1, 0.1, 2000);
scene.add(new THREE.HemisphereLight(0xffffff, 0x666677, 1.1));
const sun = new THREE.DirectionalLight(0xffffff, 1.2);
sun.position.set(120, 200, 80);
scene.add(sun);
function resize() {
  renderer.setSize(innerWidth, innerHeight, false);
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize);
resize();

// ---------------------------------------------------------------- helpers
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const wrapA = a => { while (a > Math.PI) a -= Math.PI * 2; while (a < -Math.PI) a += Math.PI * 2; return a; };
const lerpA = (a, b, t) => a + wrapA(b - a) * t;
const ord = n => (n % 10 === 1 && n !== 11) ? 'st' : (n % 10 === 2 && n !== 12) ? 'nd' : (n % 10 === 3 && n !== 13) ? 'rd' : 'th';
const fmtTime = t => { t = Math.max(0, t); const m = Math.floor(t / 60), s = t - m * 60; return `${m}:${s.toFixed(3).padStart(6, '0')}`; };
const cleanName = s => String(s || 'Racer').replace(/[<>&"']/g, '').slice(0, 12) || 'Racer';
const shuffle = a => { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };

function show(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.toggle('hidden', s.id !== id));
  $('screens').classList.toggle('hidden', !id);
  G.screen = id;
}
function toast(t) {
  const el = $('toast');
  el.textContent = t;
  el.classList.remove('show'); void el.offsetWidth; el.classList.add('show');
}

// ---------------------------------------------------------------- input
const KEYMAP = {
  ArrowUp: 'gas', KeyW: 'gas', ArrowDown: 'brake', KeyS: 'brake', ArrowLeft: 'left', KeyA: 'left',
  ArrowRight: 'right', KeyD: 'right', Space: 'drift', ShiftLeft: 'item', ShiftRight: 'item', KeyE: 'item', KeyX: 'item',
};
const keys = new Set();
const edge = { drift: false, item: false };
function press(k) { if (!keys.has(k)) { if (k === 'drift') edge.drift = true; if (k === 'item') edge.item = true; } keys.add(k); }
addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  const k = KEYMAP[e.code];
  if (!k) return;
  e.preventDefault();
  press(k);
});
addEventListener('keyup', e => { const k = KEYMAP[e.code]; if (k) keys.delete(k); });
addEventListener('blur', () => keys.clear());
document.querySelectorAll('#touch button').forEach(b => {
  const k = b.dataset.k;
  b.addEventListener('touchstart', e => { e.preventDefault(); press(k); }, { passive: false });
  b.addEventListener('touchend', e => { e.preventDefault(); keys.delete(k); }, { passive: false });
});
let steerSmooth = 0;
const NOINPUT = { gas: false, brake: false, steer: 0, drift: false, driftPressed: false, itemPressed: false };
function readPlayerInput(dt) {
  const target = (keys.has('right') ? 1 : 0) - (keys.has('left') ? 1 : 0);
  const rate = target === 0 ? 10 : 7;
  steerSmooth += clamp(target - steerSmooth, -rate * dt, rate * dt);
  const inp = {
    gas: keys.has('gas'), brake: keys.has('brake'), steer: steerSmooth, drift: keys.has('drift'),
    driftPressed: edge.drift, itemPressed: edge.item,
  };
  edge.drift = edge.item = false;
  return inp;
}

// ---------------------------------------------------------------- kart
const TIER_T = [0, 0.9, 1.9, 3.0];
const TIER_BOOST = [0, 0.55, 1.0, 1.5];
const TIER_COL = [0xe8e8e8, 0x4fb3ff, 0xff9a2f, 0xc65bff];
const tierOf = c => c >= TIER_T[3] ? 3 : c >= TIER_T[2] ? 2 : c >= TIER_T[1] ? 1 : 0;

class Kart {
  constructor(entry, ch, model) {
    this.id = entry.id; this.name = entry.name; this.ch = ch; this.bot = !!entry.bot; this.m = model;
    const s = ch.stats;
    this.stats = { max: 34 + s.speed * 1.6, acc: 9 + s.accel * 2.4, turn: 1.5 + s.handling * 0.14, weight: 0.6 + s.weight * 0.25 };
    this.pos = new THREE.Vector3(); this.vel = new THREE.Vector3();
    this.h = 0; this.speed = 0; this.vy = 0; this.ground = 0;
    this.drift = 0; this.charge = 0; this.tier = 0; this.boost = 0; this.spin = 0; this.shield = 0;
    this.spinAng = 0; this.bodyYaw = 0; this.roll = 0;
    this.item = null; this.uses = 0; this.rolling = 0; this.itemDelay = 0;
    this.lap = 0; this.idx = 0; this.idxF = 0; this.prog = 0; this.rank = 1;
    this.finished = false; this.finishTime = 0;
    this.offroad = false; this.rubber = 1; this.gasSince = null;
    this.botLine = (Math.random() - 0.5) * 0.6; this.botLineT = 0; this.botSkill = 0.94 + Math.random() * 0.05;
    this.gone = false; this.net = null; this.local = false; this.sim = false;
  }
}

// ---------------------------------------------------------------- race setup
function buildGrid(humans) {
  const used = new Set(humans.map(h => h.char));
  const pool = shuffle(CHARACTERS.filter(c => !used.has(c.id))).concat(shuffle(CHARACTERS.filter(c => used.has(c.id))));
  const bots = [];
  for (let i = 0; humans.length + bots.length < MAX_RACERS; i++) {
    const c = pool[i % pool.length];
    bots.push({ id: 'bot' + i, name: c.name, char: c.id, bot: true });
  }
  return [...shuffle(bots), ...shuffle([...humans])];
}

function clearRace() {
  const R = G.race;
  if (!R) return;
  scene.remove(R.group);
  G.race = null;
  $('hud').classList.add('hidden');
  sfx.engine(0, false);
}

function startRace(def) {
  clearRace();
  removeMenuScene();
  const tdef = trackById(def.trackId);
  const track = new Track(tdef);
  const group = new THREE.Group();
  group.add(track.group);
  scene.add(group);
  scene.background = new THREE.Color(tdef.sky);
  scene.fog = new THREE.Fog(tdef.sky, tdef.fog[0], tdef.fog[1]);

  const R = G.race = {
    def, track, group, karts: [], byId: new Map(), items: new Map(), boxes: [],
    t: -4, phase: 'count', laps: def.laps || LAPS, lastCount: null, sendT: 0, seq: 0,
    particles: new Particles(group), me: null, myFinishAt: null, resultsShown: false,
    camH: 0, camPos: new THREE.Vector3(), fov: 70,
  };

  def.grid.forEach((e, k) => {
    const ch = charById(e.char);
    const model = buildKart(ch);
    group.add(model.root);
    const kart = new Kart(e, ch, model);
    kart.local = e.id === G.myId;
    kart.sim = kart.local || (kart.bot && (G.mode === 'quick' || (G.net && G.net.isHost)));
    const row = Math.floor(k / 2), side = k % 2 ? 1 : -1;
    const back = 4 + row * 3.6 + (k % 2) * 1.4;
    const i = ((track.N - Math.round(back)) % track.N + track.N) % track.N;
    const p = track.pointAt(i, side * track.half * 0.42);
    kart.pos.copy(p);
    kart.h = track.heading(i);
    kart.idx = i; kart.idxF = i; kart.prog = i;
    kart.ground = p.y;
    R.karts.push(kart);
    R.byId.set(kart.id, kart);
  });
  R.me = R.byId.get(G.myId) || R.karts[R.karts.length - 1];
  R.camH = R.me.h;

  // item boxes
  for (const f of tdef.boxes) {
    const i = Math.floor(f * track.N);
    for (let b = 0; b < 4; b++) {
      const lat = (-0.36 + b * 0.24) * tdef.width;
      const mesh = buildItemBox();
      const p = track.pointAt(i, lat, 1.5);
      mesh.position.copy(p);
      group.add(mesh);
      R.boxes.push({ mesh, x: p.x, z: p.z, y: p.y, active: true, timer: 0, phase: Math.random() * 6 });
    }
  }

  // minimap
  const bg = document.createElement('canvas');
  bg.width = bg.height = 200;
  const b = track.bounds, size = Math.max(b.maxX - b.minX, b.maxZ - b.minZ);
  const sc = 180 / size;
  const ox = 10 + (180 - (b.maxX - b.minX) * sc) / 2, oz = 10 + (180 - (b.maxZ - b.minZ) * sc) / 2;
  const map = (x, z) => [ox + (x - b.minX) * sc, oz + (z - b.minZ) * sc];
  const cx = bg.getContext('2d');
  cx.lineJoin = 'round';
  for (const [w, c] of [[track.def.width * sc + 6, 'rgba(0,0,0,0.55)'], [track.def.width * sc, 'rgba(255,255,255,0.85)']]) {
    cx.beginPath();
    track.P.forEach((p, i) => { const [x, y] = map(p.x, p.z); i ? cx.lineTo(x, y) : cx.moveTo(x, y); });
    cx.closePath(); cx.lineWidth = w; cx.strokeStyle = c; cx.stroke();
  }
  const [sx, sy] = map(track.P[0].x, track.P[0].z);
  cx.fillStyle = '#ff4f7a'; cx.fillRect(sx - 4, sy - 4, 8, 8);
  R.mini = { bg, map };

  $('toast').classList.remove('show');
  $('toast').textContent = '';
  $('lap-total').textContent = R.laps;
  $('hud').classList.remove('hidden');
  show(null);
  sfx.init();
}

// ---------------------------------------------------------------- simulation
function onLap(k, d) {
  const R = G.race;
  k.lap += d;
  if (d < 0) return;
  if (k.lap > R.laps && !k.finished) finishKart(k);
  else if (k.local && k.lap > 1) { toast(k.lap === R.laps ? 'FINAL LAP!' : 'LAP ' + k.lap); sfx.lap(); }
}

function finishKart(k) {
  const R = G.race;
  k.finished = true;
  k.finishTime = R.t;
  if (G.net) G.net.send({ t: 'fin', id: k.id, time: k.finishTime });
  if (k.local) {
    R.myFinishAt = R.t;
    toast(`FINISH! ${k.rank}${ord(k.rank)}`);
    sfx.fanfare();
  }
}

function endDrift(k) {
  const t = tierOf(k.charge);
  if (t > 0) {
    k.boost = Math.max(k.boost, TIER_BOOST[t]);
    if (k.local) sfx.boost();
  }
  k.drift = 0; k.charge = 0; k.tier = 0;
}

function spinOut(k) {
  k.spin = 1.3;
  k.drift = 0; k.charge = 0; k.tier = 0; k.boost = 0;
  k.speed *= 0.25;
  if (k.local) { sfx.hit(); toast('OUCH!'); }
}

function simKart(k, inp, dt) {
  const R = G.race, tr = R.track, st = k.stats;
  if (k.spin > 0) { k.spin -= dt; inp = NOINPUT; k.speed *= Math.pow(0.2, dt); }
  const grounded = k.pos.y - k.ground < 0.08;

  if (inp.driftPressed && !k.drift && Math.abs(inp.steer) > 0.2 && k.speed > 14 && grounded) {
    k.drift = Math.sign(inp.steer); k.charge = 0; k.tier = 0; k.vy = 5;
  } else if (inp.driftPressed && !k.drift && grounded) {
    k.vy = 4; // small hop
  }
  if (k.drift && (!inp.drift || k.speed < 10)) endDrift(k);

  const boosting = k.boost > 0;
  let maxS = st.max * k.rubber * (boosting ? 1.32 : 1);
  if (k.offroad && !boosting) maxS *= 0.5;
  if (boosting) { k.boost -= dt; k.speed = Math.min(maxS, k.speed + 70 * dt); }
  if (inp.gas) {
    if (k.speed < maxS) k.speed += st.acc * dt * (k.speed < 0 ? 2.5 : 1) * (k.speed > st.max * 0.8 ? 0.6 : 1);
  } else if (inp.brake) {
    k.speed -= (k.speed > 0 ? 38 : 10) * dt;
    if (k.speed < -12) k.speed = -12;
  } else {
    k.speed -= Math.sign(k.speed) * Math.min(Math.abs(k.speed), 7 * dt);
  }
  if (k.speed > maxS) k.speed -= Math.min(k.speed - maxS, (k.speed - maxS) * 2.5 * dt + 4 * dt);

  let yaw;
  if (k.drift) {
    const s = inp.steer * k.drift;
    yaw = k.drift * st.turn * (0.8 + 0.45 * s);
    k.charge += dt * (0.75 + 0.5 * Math.max(0, s));
    const t = tierOf(k.charge);
    if (t !== k.tier) { k.tier = t; if (k.local && t > 0) sfx.tick(t); }
  } else {
    const sf = Math.min(1, Math.abs(k.speed) / 10) * (k.speed < 0 ? -1 : 1);
    yaw = inp.steer * st.turn * sf * (k.speed > st.max * 0.9 ? 0.92 : 1);
  }
  k.h = wrapA(k.h - yaw * dt);

  const fx = Math.sin(k.h), fz = Math.cos(k.h);
  let tx = fx * k.speed, tz = fz * k.speed;
  if (k.drift) { const out = -k.drift * k.speed * 0.12; tx += -fz * out; tz += fx * out; }
  const grip = k.drift ? 3.2 : (k.spin > 0 ? 1.5 : 9);
  const a = 1 - Math.exp(-grip * dt);
  k.vel.x += (tx - k.vel.x) * a;
  k.vel.z += (tz - k.vel.z) * a;
  k.pos.x += k.vel.x * dt;
  k.pos.z += k.vel.z * dt;

  const loc = tr.locate(k.pos.x, k.pos.z, k.idx);
  k.idx = loc.i; k.ground = loc.y;
  const L = tr.L[loc.i], al = Math.abs(loc.lat), sg = Math.sign(loc.lat);
  if (al > tr.wall + 15) {
    const p = tr.P[loc.i];
    k.pos.set(p.x, p.y, p.z); k.vel.set(0, 0, 0); k.speed = 0;
  } else if (al > tr.wall) {
    const push = al - tr.wall;
    k.pos.x -= L.x * sg * push; k.pos.z -= L.z * sg * push;
    const vl = k.vel.x * L.x + k.vel.z * L.z;
    if (vl * sg > 0) {
      k.vel.x -= L.x * vl * 1.5; k.vel.z -= L.z * vl * 1.5;
      if (Math.abs(vl) > 6) { k.speed *= 0.75; if (k.local) sfx.bump(); }
    }
  }
  k.offroad = al > tr.half + tr.curb;

  k.vy -= 30 * dt;
  k.pos.y += k.vy * dt;
  if (k.pos.y <= loc.y || (k.vy <= 0 && k.pos.y - loc.y < 0.5)) { k.pos.y = loc.y; if (k.vy < 0) k.vy = 0; }

  for (const p of tr.pads) {
    let di = loc.i - p.i; if (di < 0) di += tr.N;
    if (di < 6 && Math.abs(loc.lat - p.lat) < p.w / 2) {
      if (k.boost < 0.3 && k.local) sfx.boost();
      k.boost = Math.max(k.boost, 1.0);
    }
  }

  const nf = loc.idxF, N = tr.N;
  if (k.idxF > N * 0.75 && nf < N * 0.25) onLap(k, +1);
  else if (k.idxF < N * 0.25 && nf > N * 0.75) onLap(k, -1);
  k.idxF = nf;
  k.prog = k.lap * N + nf;
  if (k.shield > 0) k.shield -= dt;
}

function botInput(k, dt) {
  const R = G.race, tr = R.track, N = tr.N;
  k.botLineT -= dt;
  if (k.botLineT <= 0) { k.botLineT = 2 + Math.random() * 3; k.botLine = clamp(k.botLine + (Math.random() - 0.5) * 0.4, -0.25, 0.25); }
  const look = Math.round(8 + Math.max(0, k.speed) * 0.3);
  const ti = (k.idx + look) % N;
  const tp = tr.P[ti], L = tr.L[ti];
  const lat = k.botLine * tr.half;
  const dx = tp.x + L.x * lat - k.pos.x, dz = tp.z + L.z * lat - k.pos.z;
  const diff = wrapA(Math.atan2(dx, dz) - k.h);
  const inp = { gas: true, brake: false, steer: clamp(-diff * 2.6, -1, 1), drift: false, driftPressed: false, itemPressed: false };
  const ahead = (k.idx + Math.round(18 + k.speed * 0.4)) % N;
  const turn = wrapA(tr.heading(ahead) - tr.heading(k.idx));
  if (k.drift) inp.drift = Math.abs(turn) > 0.35 && k.charge < TIER_T[2] + 0.3 && Math.sign(-turn) === k.drift;
  else if (Math.abs(turn) > 0.75 && k.speed > 25 && Math.random() < 0.04) { inp.drift = true; inp.driftPressed = true; inp.steer = -Math.sign(turn); }
  if (Math.abs(diff) > 1.4 && k.speed > 15) inp.gas = false;
  if (k.item && k.rolling <= 0) {
    k.itemDelay -= dt;
    if (k.itemDelay <= 0) { inp.itemPressed = true; k.itemDelay = 0.6 + Math.random() * 2.5; }
  }
  return inp;
}

function rankFrac(k) {
  const n = G.race.karts.filter(x => !x.gone).length;
  return n > 1 ? (k.rank - 1) / (n - 1) : 0;
}

function itemLogic(k, inp, dt) {
  const R = G.race;
  if (k.rolling > 0) {
    k.rolling -= dt;
    if (k.rolling <= 0) {
      k.item = rollItem(rankFrac(k));
      k.uses = k.item === 'fizz3' ? 3 : 1;
      k.itemDelay = 0.8 + Math.random() * 2.5;
      if (k.local) sfx.item();
    }
  }
  if (inp.itemPressed && k.item && k.rolling <= 0 && R.phase === 'race' && k.spin <= 0) useItem(k, inp);
  for (const b of R.boxes) {
    if (!b.active) continue;
    const dx = b.x - k.pos.x, dz = b.z - k.pos.z;
    if (dx * dx + dz * dz < 2.8 * 2.8) {
      takeBox(R.boxes.indexOf(b), true);
      if (!k.item && k.rolling <= 0) { k.rolling = 1.1; if (k.local) sfx.pick(); }
    }
  }
}

function kartAhead(k) {
  return G.race.karts.find(x => !x.gone && x.rank === k.rank - 1) || null;
}

function useItem(k, inp) {
  const R = G.race, type = k.item;
  const fx = Math.sin(k.h), fz = Math.cos(k.h);
  if (type === 'fizz' || type === 'fizz3') {
    k.boost = Math.max(k.boost, 1.2);
    k.speed = Math.max(k.speed, k.stats.max * 1.2);
    if (k.local) sfx.boost();
  } else if (type === 'bubble') {
    k.shield = 6;
    if (k.local) sfx.shield();
  } else {
    const backward = type === 'jelly' || (type === 'gumball' && inp.brake);
    const dir = backward ? -1 : 1;
    const off = backward ? -3.4 : 3.4;
    const target = type === 'bee' ? (kartAhead(k)?.id || null) : null;
    const sp = type === 'jelly' ? 0 : type === 'bee' ? 62 : Math.max(75, Math.abs(k.speed) + 35);
    spawnItem({
      id: G.myId + ':' + (++R.seq), type, owner: k.id,
      x: k.pos.x + fx * off, y: k.pos.y, z: k.pos.z + fz * off, dx: fx * dir, dz: fz * dir, sp, target,
    }, true);
    if (k.local) sfx.throw();
  }
  k.uses--;
  if (k.uses <= 0) k.item = null;
}

function spawnItem(d, send) {
  const R = G.race;
  if (!R || R.items.has(d.id)) return;
  const mesh = buildItemMesh(d.type);
  R.group.add(mesh);
  const it = { ...d, mesh, age: 0, bounces: 0, idx: -1, life: d.type === 'jelly' ? 90 : d.type === 'bee' ? 10 : 7 };
  const loc = R.track.locate(it.x, it.z);
  it.idx = loc.i;
  it.y = loc.y + (d.type === 'jelly' ? 0.05 : d.type === 'bee' ? 1.5 : 0.6);
  mesh.position.set(it.x, it.y, it.z);
  R.items.set(d.id, it);
  if (send && G.net) G.net.send({ t: 'spawn', i: d });
}

function removeItem(id) {
  const R = G.race, it = R.items.get(id);
  if (!it) return;
  R.group.remove(it.mesh);
  R.items.delete(id);
}

function applyHit(iid, victimId, send) {
  const R = G.race;
  if (!R) return;
  const it = R.items.get(iid);
  const v = R.byId.get(victimId);
  if (it) {
    R.particles.burst(it.x, it.y + 0.5, it.z, it.type === 'jelly' ? [0x55e07a, 0xffffff] : [0xffd23f, 0xffffff, 0x2f8bff], 24, 9);
    removeItem(iid);
  }
  if (v && v.sim) {
    if (v.shield > 0) { v.shield = 0; if (v.local) sfx.shield(); }
    else spinOut(v);
  }
  if (send && G.net) G.net.send({ t: 'hit', iid, victim: victimId });
}

function takeBox(b, send) {
  const R = G.race, box = R && R.boxes[b];
  if (!box || !box.active) return;
  box.active = false; box.timer = 3; box.mesh.visible = false;
  R.particles.burst(box.x, box.y, box.z, [0xff8fb1, 0x9be7ff, 0xfff27a, 0xb9a6ff], 16, 7);
  if (send && G.net) G.net.send({ t: 'box', b });
}

function updateItems(dt) {
  const R = G.race, tr = R.track;
  for (const it of [...R.items.values()]) {
    it.age += dt;
    if (it.age > it.life) { removeItem(it.id); continue; }
    if (it.type === 'jelly') { it.mesh.scale.set(1 + Math.sin(it.age * 6) * 0.06, 1, 1 + Math.cos(it.age * 6) * 0.06); continue; }
    if (it.type === 'bee' && it.target && it.age > 0.25) {
      const tk = R.byId.get(it.target);
      if (tk && !tk.gone) {
        const want = Math.atan2(tk.pos.x - it.x, tk.pos.z - it.z);
        let cur = Math.atan2(it.dx, it.dz);
        cur += clamp(wrapA(want - cur), -3.5 * dt, 3.5 * dt);
        it.dx = Math.sin(cur); it.dz = Math.cos(cur);
      }
    }
    it.x += it.dx * it.sp * dt;
    it.z += it.dz * it.sp * dt;
    const loc = tr.locate(it.x, it.z, it.idx);
    it.idx = loc.i;
    if (it.type === 'gumball') {
      if (Math.abs(loc.lat) > tr.wall - 0.6) {
        const L = tr.L[loc.i], vl = it.dx * L.x + it.dz * L.z;
        if (vl * Math.sign(loc.lat) > 0) { it.dx -= 2 * vl * L.x; it.dz -= 2 * vl * L.z; it.bounces++; }
        if (it.bounces > 6) { removeItem(it.id); continue; }
      }
      it.y = loc.y + 0.6;
      it.mesh.rotation.x += it.sp * dt / 0.6;
    } else {
      it.y = loc.y + 1.5 + Math.sin(it.age * 10) * 0.2;
      if (Math.abs(loc.lat) > tr.wall + 25) { removeItem(it.id); continue; }
      it.mesh.rotation.y = Math.atan2(it.dx, it.dz);
      it.mesh.children.forEach(c => { if (c.userData.wing) c.rotation.z = c.userData.wing * (0.3 + Math.sin(it.age * 50) * 0.5); });
    }
    it.mesh.position.set(it.x, it.y, it.z);
  }
}

function hitChecks() {
  const R = G.race;
  for (const k of R.karts) {
    if (!k.sim || k.gone || k.spin > 0) continue;
    for (const it of R.items.values()) {
      if (it.owner === k.id && it.age < (it.type === 'jelly' ? 1.2 : 0.5)) continue;
      const dx = it.x - k.pos.x, dz = it.z - k.pos.z, r = it.type === 'jelly' ? 2.0 : 2.3;
      if (dx * dx + dz * dz < r * r && Math.abs(it.y - k.pos.y) < 3.5) { applyHit(it.id, k.id, true); break; }
    }
  }
}

function kartCollisions() {
  const R = G.race;
  for (const a of R.karts) {
    if (!a.sim || a.gone) continue;
    for (const b of R.karts) {
      if (a === b || b.gone) continue;
      const dx = a.pos.x - b.pos.x, dz = a.pos.z - b.pos.z, d2 = dx * dx + dz * dz;
      if (d2 < 2.4 * 2.4 && d2 > 0.0001) {
        const d = Math.sqrt(d2), nx = dx / d, nz = dz / d;
        const share = b.stats.weight / (a.stats.weight + b.stats.weight);
        const push = (2.4 - d) * share;
        a.pos.x += nx * push; a.pos.z += nz * push;
        a.vel.x += nx * 6 * share; a.vel.z += nz * 6 * share;
      }
    }
  }
}

// ---------------------------------------------------------------- visuals
function visualKart(k, dt) {
  const R = G.race, m = k.m, P = R.particles;
  if (!k.sim && k.net) {
    const n = k.net, a = 1 - Math.exp(-12 * dt);
    if (!k.netSnapped) { k.pos.set(n.x, n.y, n.z); k.h = n.h; k.netSnapped = true; }
    k.pos.x += (n.x - k.pos.x) * a; k.pos.y += (n.y - k.pos.y) * a; k.pos.z += (n.z - k.pos.z) * a;
    k.h = lerpA(k.h, n.h, a);
    k.speed = n.s; k.drift = n.d; k.offroad = !!n.o;
  }
  m.root.visible = !k.gone;
  if (k.gone) return;
  m.root.position.copy(k.pos);
  m.root.rotation.y = k.h;
  const spinning = k.sim ? k.spin > 0 : (k.net && k.net.sp);
  k.spinAng = spinning ? k.spinAng + dt * 13 : 0;
  k.bodyYaw += (k.drift * 0.4 - k.bodyYaw) * (1 - Math.exp(-10 * dt));
  m.body.rotation.y = k.bodyYaw + k.spinAng;
  for (const w of m.wheels) w.rotation.x += k.speed * dt / 0.45;
  const shield = k.sim ? k.shield > 0 : (k.net && k.net.sh);
  m.shield.visible = !!shield;
  if (shield) m.shield.rotation.y += dt * 2;

  const fx = Math.sin(k.h), fz = Math.cos(k.h), rx = -fz, rz = fx;
  const bx = k.pos.x - fx * 1.7, bz = k.pos.z - fz * 1.7, by = k.pos.y + 0.35;
  if (k.drift) {
    const tier = k.sim ? k.tier : (k.net ? k.net.c : 0);
    for (const s of [-1, 1]) {
      if (Math.random() < 0.75) P.emit(bx + rx * s * 1.15, by, bz + rz * s * 1.15, TIER_COL[tier], { vy: 2 + Math.random() * 2, life: 0.3, size: tier ? 1.1 : 0.8, g: 8, spread: 3 });
    }
  }
  const boosting = k.sim ? k.boost > 0 : (k.net && k.net.b);
  if (boosting) {
    for (let i = 0; i < 2; i++) P.emit(bx, by + 0.4, bz, Math.random() < 0.5 ? 0xffb030 : 0xff5a1f, { vx: -fx * 8, vz: -fz * 8, life: 0.25, size: 1.5, spread: 2 });
  }
  if (k.offroad && Math.abs(k.speed) > 8 && Math.random() < 0.5) P.emit(bx, by, bz, R.track.def.dust, { vy: 2, life: 0.5, size: 1.3, spread: 3, g: 2 });
  if (spinning && Math.random() < 0.5) P.emit(k.pos.x, k.pos.y + 2.4, k.pos.z, 0xffe14a, { vy: 1, life: 0.4, size: 0.8, spread: 4 });
}

function updateCamera(dt) {
  const R = G.race, me = R.me;
  R.camH = lerpA(R.camH, me.h, 1 - Math.exp(-5 * dt));
  const fx = Math.sin(R.camH), fz = Math.cos(R.camH);
  const want = new THREE.Vector3(me.pos.x - fx * 8.5, me.pos.y + 3.6, me.pos.z - fz * 8.5);
  if (R.camPos.lengthSq() === 0) R.camPos.copy(want);
  R.camPos.lerp(want, 1 - Math.exp(-8 * dt));
  camera.position.copy(R.camPos);
  camera.lookAt(me.pos.x + fx * 5, me.pos.y + 1.4, me.pos.z + fz * 5);
  const targetFov = 70 + (me.boost > 0 ? 9 : 0);
  R.fov += (targetFov - R.fov) * (1 - Math.exp(-6 * dt));
  if (Math.abs(camera.fov - R.fov) > 0.05) { camera.fov = R.fov; camera.updateProjectionMatrix(); }
}

function updateHud() {
  const R = G.race, me = R.me;
  $('pos-num').textContent = me.rank;
  $('pos-suf').textContent = ord(me.rank);
  $('lap-num').textContent = clamp(me.lap, 1, R.laps);
  $('hud-time').textContent = fmtTime(me.finished ? me.finishTime : R.t);
  $('speed-num').textContent = Math.round(Math.abs(me.speed) * 3.2);
  let icon = '', name = '';
  if (me.rolling > 0) { const keysI = Object.keys(ITEM_INFO); icon = ITEM_INFO[keysI[Math.floor(R.t * 14) % keysI.length]].icon; }
  else if (me.item) { icon = ITEM_INFO[me.item].icon; name = ITEM_INFO[me.item].name + (me.uses > 1 ? ' ×' + me.uses : ''); }
  $('item-icon').textContent = icon;
  $('item-name').textContent = name;
  const fill = $('drift-fill');
  fill.style.width = me.drift ? Math.min(100, me.charge / TIER_T[3] * 100) + '%' : '0%';
  fill.style.background = hex(TIER_COL[me.tier]);

  let cd = '';
  if (R.t < -3) cd = 'READY';
  else if (R.t < 0) cd = String(Math.ceil(-R.t));
  else if (R.t < 1) cd = 'GO!';
  $('countdown').textContent = cd;
  const n = R.t < -3 ? 4 : R.t < 0 ? Math.ceil(-R.t) : 0;
  if (n !== R.lastCount && R.t < 1) { if (n < 4) sfx.count(n); R.lastCount = n; }

  const c = $('minimap').getContext('2d');
  c.clearRect(0, 0, 200, 200);
  c.drawImage(R.mini.bg, 0, 0);
  for (const k of [...R.karts].reverse()) {
    if (k.gone) continue;
    const [x, y] = R.mini.map(k.pos.x, k.pos.z);
    c.beginPath(); c.arc(x, y, k === me ? 7 : 5, 0, Math.PI * 2);
    c.fillStyle = hex(k.ch.color); c.fill();
    c.lineWidth = 2; c.strokeStyle = k === me ? '#fff' : 'rgba(0,0,0,.6)'; c.stroke();
  }
}

// ---------------------------------------------------------------- main race step
function onGo() {
  const R = G.race;
  for (const k of R.karts) {
    if (!k.sim) continue;
    if (k.bot || G.autopilot) { if (Math.random() < 0.45) k.boost = 1.0; continue; }
    if (k.gasSince !== null) {
      const held = 0 - k.gasSince;
      if (held <= 0.7) { k.boost = 1.0; k.speed = k.stats.max; if (k.local) { toast('ROCKET START!'); sfx.boost(); } }
      else if (held > 2.5) { k.spin = 0.8; if (k.local) toast('Too early!'); }
    }
  }
}

function step(dt) {
  const R = G.race;
  if (!R) return;
  R.t += dt;
  if (R.phase === 'count' && R.t >= 0) { R.phase = 'race'; onGo(); }

  const playerInp = readPlayerInput(dt);

  // rubber band for bots, based on the best human
  let bestHuman = -Infinity;
  for (const k of R.karts) if (!k.bot && !k.gone) bestHuman = Math.max(bestHuman, k.prog);

  for (const k of R.karts) {
    if (k.gone) continue;
    if (k.sim) {
      const auto = k.bot || (k.local && (G.autopilot || k.finished));
      if (k.bot) k.rubber = k.botSkill * (1 + clamp((bestHuman - k.prog) / 120 * 0.12, -0.1, 0.12));
      const inp = auto ? botInput(k, dt) : playerInp;
      if (R.phase === 'count') {
        if (inp.gas) { if (k.gasSince === null) k.gasSince = R.t; } else k.gasSince = null;
      } else {
        simKart(k, inp, dt);
        itemLogic(k, inp, dt);
      }
    }
    visualKart(k, dt);
  }
  kartCollisions();
  updateItems(dt);
  hitChecks();

  for (const b of R.boxes) {
    b.phase += dt;
    if (!b.active) { b.timer -= dt; if (b.timer <= 0) { b.active = true; b.mesh.visible = true; } }
    b.mesh.rotation.y = b.phase * 1.5;
    b.mesh.rotation.x = b.phase * 0.7;
    b.mesh.position.y = b.y + Math.sin(b.phase * 2) * 0.25;
    b.mesh.userData.outer.material.emissive.setHSL((b.phase * 0.15) % 1, 0.8, 0.35);
  }
  R.particles.update(dt);

  const order = R.karts.filter(k => !k.gone).sort((a, b) => {
    if (a.finished && b.finished) return a.finishTime - b.finishTime;
    if (a.finished) return -1;
    if (b.finished) return 1;
    return b.prog - a.prog;
  });
  order.forEach((k, i) => { k.rank = i + 1; });

  if (G.net) {
    R.sendT += dt;
    if (R.sendT >= 1 / 15) {
      R.sendT = 0;
      if (G.net.isHost) G.net.send({ t: 'sts', s: R.karts.filter(k => !k.gone && (k.sim || k.net)).map(packState) });
      else G.net.send({ t: 'st', s: packState(R.me) });
    }
  }

  const me = R.me;
  sfx.engine(Math.abs(me.speed) / 50, R.phase === 'race' && !R.resultsShown);
  if (me.finished && !R.resultsShown) {
    const allDone = order.every(k => k.finished);
    if (allDone || R.t - R.myFinishAt > 10) showResults();
  }
  updateCamera(dt);
  updateHud();
}

// ---------------------------------------------------------------- networking
function packState(k) {
  const r = v => Math.round(v * 100) / 100;
  return {
    id: k.id, x: r(k.pos.x), y: r(k.pos.y), z: r(k.pos.z), h: r(k.h), s: r(k.speed), d: k.drift,
    c: k.tier, sp: k.spin > 0 ? 1 : 0, b: k.boost > 0 ? 1 : 0, sh: k.shield > 0 ? 1 : 0, o: k.offroad ? 1 : 0,
    l: k.lap, p: r(k.prog), f: k.finished ? 1 : 0, ft: r(k.finishTime),
  };
}

function applyState(s) {
  const R = G.race;
  if (!R || !s) return;
  const k = R.byId.get(s.id);
  if (!k || k.sim) return;
  k.net = s; k.lap = s.l; k.prog = s.p; k.tier = s.c;
  if (s.f && !k.finished) { k.finished = true; k.finishTime = s.ft; }
}

function broadcastLobby() {
  if (G.net && G.net.isHost) G.net.send({ t: 'lobby', players: G.lobby, track: G.trackId });
}

function onNet(d) {
  const R = G.race;
  switch (d.t) {
    case 'join': {
      if (!G.net.isHost) return;
      if (R) { G.net.sendTo(d.from, { t: 'busy' }); return; }
      if (G.lobby.length >= MAX_RACERS && !G.lobby.find(p => p.id === d.from)) { G.net.sendTo(d.from, { t: 'full' }); return; }
      G.lobby = G.lobby.filter(p => p.id !== d.from);
      G.lobby.push({ id: d.from, name: cleanName(d.name), char: charById(d.char).id });
      broadcastLobby(); renderLobby(); sfx.pick();
      break;
    }
    case 'lobby':
      G.lobby = d.players; G.trackId = d.track;
      if (R) clearRace();
      ensureMenuScene();
      show('s-lobby'); renderLobby();
      break;
    case 'start': G.trackId = d.trackId; startRace(d); break;
    case 'st': applyState(d.s); break;
    case 'sts': for (const s of d.s) if (s.id !== G.myId) applyState(s); break;
    case 'spawn': spawnItem(d.i, false); break;
    case 'hit': applyHit(d.iid, d.victim, false); break;
    case 'box': takeBox(d.b, false); break;
    case 'fin': {
      const k = R && R.byId.get(d.id);
      if (k && !k.sim && !k.finished) { k.finished = true; k.finishTime = d.time; }
      break;
    }
    case 'gone': { const k = R && R.byId.get(d.id); if (k) k.gone = true; break; }
    case 'busy': leaveOnline('That race already started. Try again when it ends.'); break;
    case 'full': leaveOnline('That room is full.'); break;
  }
}

function setupNetHandlers() {
  G.net.on('message', onNet);
  G.net.on('left', id => {
    G.lobby = G.lobby.filter(p => p.id !== id);
    broadcastLobby(); renderLobby();
    const R = G.race;
    if (R && R.byId.get(id)) { R.byId.get(id).gone = true; G.net.send({ t: 'gone', id }); }
  });
  G.net.on('hostLeft', () => leaveOnline('The host left the game.'));
  G.net.on('error', e => console.warn('net error', e));
}

function leaveOnline(message) {
  if (G.net) G.net.close();
  G.net = null;
  clearRace();
  G.lobby = [];
  ensureMenuScene();
  show('s-title');
  $('title-msg').textContent = message || '';
}

async function hostRoom() {
  show('s-lobby');
  $('lobby-msg').textContent = 'Creating room...';
  $('lobby-code').textContent = '-----';
  $('lobby-start').disabled = true;
  G.net = new Net();
  try {
    G.roomCode = await G.net.host();
  } catch (e) {
    leaveOnline('Could not create a room: ' + (e.message || e.type || e));
    return;
  }
  G.myId = G.net.id;
  setupNetHandlers();
  G.lobby = [{ id: G.myId, name: G.name, char: G.charId }];
  $('lobby-msg').textContent = 'Send the code or link to your friends. Empty spots are filled with bots.';
  renderLobby();
}

async function joinRoom() {
  show('s-lobby');
  $('lobby-code').textContent = G.joinCode;
  $('lobby-msg').textContent = 'Connecting...';
  $('lobby-start').disabled = true;
  G.net = new Net();
  try {
    await G.net.join(G.joinCode);
  } catch (e) {
    leaveOnline(e.message || 'Could not join that room.');
    return;
  }
  G.myId = G.net.id;
  G.roomCode = G.joinCode;
  setupNetHandlers();
  G.net.send({ t: 'join', name: G.name, char: G.charId });
  $('lobby-msg').textContent = 'Connected. Waiting for the host to start...';
}

function renderLobby() {
  const isHost = G.net && G.net.isHost;
  const code = G.roomCode || G.joinCode || '-----';
  $('lobby-code').textContent = code;
  $('lobby-link').value = `${location.origin}${location.pathname}?room=${code}`;
  $('lobby-track').textContent = 'Track: ' + trackById(G.trackId).name + ` · ${LAPS} laps`;
  $('lobby-list').innerHTML = G.lobby.map((p, i) => {
    const ch = charById(p.char);
    return `<li><span class="dot" style="background:${hex(ch.color)}"></span><b>${cleanName(p.name)}</b> <span>${ch.name}</span><span class="who">${i === 0 ? 'HOST' : ''}${p.id === G.myId ? ' (you)' : ''}</span></li>`;
  }).join('') + `<li style="opacity:.6">+ ${Math.max(0, MAX_RACERS - G.lobby.length)} bots</li>`;
  $('lobby-start').classList.toggle('hidden', !isHost);
  $('lobby-start').disabled = !isHost || !G.roomCode;
}

$('lobby-copy').onclick = () => {
  const v = $('lobby-link').value;
  (navigator.clipboard ? navigator.clipboard.writeText(v) : Promise.reject()).then(
    () => { $('lobby-msg').textContent = 'Invite link copied.'; },
    () => { $('lobby-link').select(); document.execCommand('copy'); $('lobby-msg').textContent = 'Invite link copied.'; });
};
$('lobby-leave').onclick = () => leaveOnline('');
$('lobby-start').onclick = () => {
  if (!G.net || !G.net.isHost) return;
  const def = { t: 'start', trackId: G.trackId, laps: LAPS, grid: buildGrid(G.lobby.map(p => ({ id: p.id, name: p.name, char: p.char }))) };
  G.net.send(def);
  startRace(def);
};

// ---------------------------------------------------------------- results
function showResults() {
  const R = G.race;
  R.resultsShown = true;
  const order = R.karts.filter(k => !k.gone).sort((a, b) => a.rank - b.rank);
  $('res-list').innerHTML = order.map(k => `<tr class="${k === R.me ? 'me' : ''}"><td class="p">${k.rank}${ord(k.rank)}</td>
    <td><span class="dot" style="background:${hex(k.ch.color)}"></span>${k.bot ? 'CPU' : cleanName(k.name)}${k === R.me ? ' (you)' : ''}</td>
    <td>${k.ch.name}</td><td>${k.finished ? fmtTime(k.finishTime) : '—'}</td></tr>`).join('');
  const box = $('res-buttons');
  box.innerHTML = '';
  const btn = (label, fn, cls = '') => { const b = document.createElement('button'); b.textContent = label; b.className = cls; b.onclick = fn; box.appendChild(b); };
  $('res-msg').textContent = '';
  if (G.mode === 'quick') {
    btn('Main Menu', () => { clearRace(); ensureMenuScene(); show('s-title'); });
    btn('Change Racer', () => { clearRace(); ensureMenuScene(); openChar(); });
    btn('Race Again', () => startQuick(), 'big');
  } else if (G.net && G.net.isHost) {
    btn('Leave', () => leaveOnline(''));
    btn('Back to Lobby', () => { clearRace(); ensureMenuScene(); show('s-lobby'); renderLobby(); broadcastLobby(); }, 'big');
  } else {
    $('res-msg').textContent = 'Waiting for the host to go back to the lobby...';
    btn('Leave', () => leaveOnline(''));
  }
  show('s-results');
}

// ---------------------------------------------------------------- menus
$('name').value = localStorage.getItem('ggp-name') || ('Racer' + Math.floor(100 + Math.random() * 900));
function saveName() { G.name = cleanName($('name').value.trim()); localStorage.setItem('ggp-name', G.name); }
if (params.get('room')) {
  $('join-code').value = params.get('room').toUpperCase().slice(0, 5);
  $('title-msg').textContent = 'You were invited to a race. Type your name and press Join Online Race.';
}
$('btn-quick').onclick = () => { sfx.init(); saveName(); G.mode = 'quick'; G.myId = 'me'; openChar(); };
$('btn-host').onclick = () => { sfx.init(); saveName(); G.mode = 'host'; openChar(); };
$('btn-join').onclick = () => {
  sfx.init(); saveName();
  const code = $('join-code').value.trim().toUpperCase();
  if (code.length !== 5) { $('title-msg').textContent = 'Type the 5-letter room code first.'; return; }
  G.joinCode = code; G.mode = 'join'; openChar();
};

// character select with a 3D preview
const pv = { r: null, scene: null, cam: null, model: null };
function initPreview() {
  if (pv.r) return;
  pv.r = new THREE.WebGLRenderer({ canvas: $('preview'), antialias: true, alpha: true });
  pv.r.setPixelRatio(Math.min(devicePixelRatio, 2));
  pv.r.setSize(420, 300, false);
  pv.scene = new THREE.Scene();
  pv.scene.add(new THREE.HemisphereLight(0xffffff, 0x554477, 1.3));
  const l = new THREE.DirectionalLight(0xffffff, 1.2); l.position.set(3, 6, 5); pv.scene.add(l);
  pv.cam = new THREE.PerspectiveCamera(38, 420 / 300, 0.1, 100);
  pv.cam.position.set(0, 3.3, 8);
  pv.cam.lookAt(0, 1.0, 0);
}
function setPreview(id) {
  initPreview();
  if (pv.model) pv.scene.remove(pv.model);
  pv.model = buildKart(charById(id)).root;
  pv.model.rotation.y = 0.6;
  pv.scene.add(pv.model);
}
function selectChar(id) {
  G.charId = id;
  const ch = charById(id);
  document.querySelectorAll('#char-grid .card').forEach(c => c.classList.toggle('sel', c.dataset.id === id));
  const bar = (n, v) => `<div class="stat"><span>${n}</span><div class="bar"><i style="width:${v * 20}%"></i></div></div>`;
  $('char-info').innerHTML = `<h3 style="color:${hex(ch.color)}">${ch.name}</h3><p>${ch.desc}</p>` +
    bar('Speed', ch.stats.speed) + bar('Accel', ch.stats.accel) + bar('Handling', ch.stats.handling) + bar('Weight', ch.stats.weight);
  setPreview(id);
}
function openChar() {
  const grid = $('char-grid');
  if (!grid.children.length) {
    grid.innerHTML = CHARACTERS.map(c => `<div class="card" data-id="${c.id}"><div class="dot" style="background:${hex(c.color)}">${c.name[0]}</div><div class="nm">${c.name}</div></div>`).join('');
    grid.querySelectorAll('.card').forEach(c => { c.onclick = () => selectChar(c.dataset.id); });
  }
  G.charId = localStorage.getItem('ggp-char') || G.charId;
  selectChar(G.charId);
  show('s-char');
}
$('char-back').onclick = () => show('s-title');
$('char-ok').onclick = () => {
  localStorage.setItem('ggp-char', G.charId);
  if (G.mode === 'join') joinRoom(); else openTrack();
};

function openTrack() {
  const grid = $('track-grid');
  if (!grid.children.length) {
    grid.innerHTML = TRACKS.map(t => `<div class="card" data-id="${t.id}"><div class="sw" style="background:linear-gradient(135deg, ${hex(t.sky)}, ${hex(t.ground)})"></div><div class="nm">${t.name}</div><div class="ds">${t.desc}</div></div>`).join('');
    grid.querySelectorAll('.card').forEach(c => { c.onclick = () => selectTrack(c.dataset.id); });
  }
  selectTrack(G.trackId);
  show('s-track');
}
function selectTrack(id) {
  G.trackId = id;
  document.querySelectorAll('#track-grid .card').forEach(c => c.classList.toggle('sel', c.dataset.id === id));
}
$('track-back').onclick = () => openChar();
$('track-ok').onclick = () => { if (G.mode === 'quick') startQuick(); else hostRoom(); };

function startQuick() {
  G.mode = 'quick'; G.myId = 'me';
  startRace({ trackId: G.trackId, laps: LAPS, grid: buildGrid([{ id: 'me', name: G.name, char: G.charId }]) });
}

// ---------------------------------------------------------------- menu background
let menu = null;
function ensureMenuScene() {
  if (menu || G.race) return;
  const t = new Track(TRACKS[0]);
  scene.add(t.group);
  scene.background = new THREE.Color(TRACKS[0].sky);
  scene.fog = new THREE.Fog(TRACKS[0].sky, 200, 800);
  menu = { t, a: 0 };
}
function removeMenuScene() { if (menu) { scene.remove(menu.t.group); menu = null; } }
function menuFrame(dt) {
  if (!menu) return;
  menu.a += dt * 0.08;
  camera.position.set(Math.cos(menu.a) * 260, 110, 80 + Math.sin(menu.a) * 260);
  camera.lookAt(0, 0, 80);
  if (camera.fov !== 60) { camera.fov = 60; camera.updateProjectionMatrix(); }
}

// ---------------------------------------------------------------- loop
let last = performance.now();
function advance(dt) {
  while (dt > 0) { const s = Math.min(dt, 1 / 30); step(s); dt -= s; }
}
function frame(now) {
  requestAnimationFrame(frame);
  const dt = Math.min(0.1, (now - last) / 1000);
  last = now;
  if (G.race) advance(dt); else menuFrame(dt);
  renderer.render(scene, camera);
  if (G.screen === 's-char' && pv.r && pv.model) {
    pv.model.rotation.y += dt * 0.8;
    pv.r.render(pv.scene, pv.cam);
  }
}
// keep the simulation (and the host's bots) running when the tab is in the background
setInterval(() => {
  if (!document.hidden || !G.race) return;
  const now = performance.now();
  const dt = Math.min(1, (now - last) / 1000);
  last = now;
  advance(dt);
}, 100);

ensureMenuScene();
show('s-title');
requestAnimationFrame(frame);

// test hooks
G.api = { startQuick, step, show };
