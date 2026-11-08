import * as THREE from 'three';

const lam = (c, o = {}) => new THREE.MeshLambertMaterial({ color: c, ...o });
const phong = (c, o = {}) => new THREE.MeshPhongMaterial({ color: c, shininess: 60, ...o });

function add(parent, geo, mat, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z);
  parent.add(m);
  return m;
}
const sphere = (r, w = 14, h = 10) => new THREE.SphereGeometry(r, w, h);
const dome = r => new THREE.SphereGeometry(r, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2);
const eyes = (g, y, z, spread, r = 0.07, color = 0x111111) => {
  for (const s of [-1, 1]) add(g, sphere(r, 8, 6), lam(color), s * spread, y, z);
};

// Drivers sit at the seat and face +z.
function buildDriver(ch) {
  const g = new THREE.Group();
  const skin = lam(0xffd2a8);
  switch (ch.build) {
    case 'kid': {
      add(g, new THREE.CylinderGeometry(0.38, 0.42, 0.7, 12), lam(ch.accent), 0, 0.35, 0);
      add(g, sphere(0.42), skin, 0, 1.0, 0);
      add(g, dome(0.46), lam(ch.color), 0, 1.08, -0.02);
      add(g, sphere(0.15, 8, 6), lam(0xffffff), 0, 1.58, -0.05);
      for (const s of [-1, 1]) {
        const lens = add(g, new THREE.TorusGeometry(0.13, 0.05, 6, 12), lam(0x333333), s * 0.17, 1.1, 0.36);
        lens.rotation.y = 0;
      }
      eyes(g, 1.1, 0.4, 0.17, 0.06);
      add(g, new THREE.BoxGeometry(0.2, 0.05, 0.05), lam(0xc0504d), 0, 0.85, 0.4);
      break;
    }
    case 'ferret': {
      const body = add(g, new THREE.CapsuleGeometry(0.32, 0.9, 6, 12), lam(ch.color), 0, 0.75, 0);
      body.rotation.x = 0.15;
      add(g, sphere(0.36), lam(ch.color), 0, 1.45, 0.12);
      add(g, sphere(0.2), lam(0xfff3d6), 0, 1.36, 0.42);
      add(g, sphere(0.06, 8, 6), lam(0x222222), 0, 1.4, 0.62);
      add(g, new THREE.BoxGeometry(0.6, 0.12, 0.1), lam(0x6b4a2f), 0, 1.52, 0.34);
      eyes(g, 1.53, 0.4, 0.13, 0.06);
      for (const s of [-1, 1]) add(g, sphere(0.12, 8, 6), lam(ch.color), s * 0.26, 1.75, 0.05);
      const scarf = add(g, new THREE.TorusGeometry(0.33, 0.1, 6, 14), lam(ch.accent), 0, 1.15, 0.05);
      scarf.rotation.x = Math.PI / 2;
      const tail = add(g, new THREE.CapsuleGeometry(0.16, 1.2, 4, 8), lam(0x8a5a2b), 0, 0.5, -1.2);
      tail.rotation.x = 1.25;
      break;
    }
    case 'royal': {
      add(g, new THREE.ConeGeometry(0.62, 1.0, 14), lam(ch.color), 0, 0.35, 0);
      add(g, sphere(0.4), lam(0xf3c9a0), 0, 1.05, 0);
      add(g, sphere(0.44), lam(0x7a3b2e), 0, 1.12, -0.1);
      eyes(g, 1.08, 0.37, 0.14, 0.06);
      add(g, new THREE.CylinderGeometry(0.3, 0.3, 0.2, 14), lam(0xfff3d6), 0, 1.55, 0);
      add(g, new THREE.CylinderGeometry(0.22, 0.22, 0.16, 14), lam(0xff7fb8), 0, 1.73, 0);
      add(g, sphere(0.09, 8, 6), lam(0xd2142b), 0, 1.88, 0);
      add(g, new THREE.TorusGeometry(0.3, 0.04, 6, 16), lam(ch.accent), 0, 1.46, 0).rotation.x = Math.PI / 2;
      break;
    }
    case 'yeti': {
      add(g, new THREE.IcosahedronGeometry(0.78, 1), lam(0xf0f6ff, { flatShading: true }), 0, 0.55, 0);
      add(g, sphere(0.32), lam(0x9fb7d9), 0, 0.92, 0.55);
      eyes(g, 1.0, 0.82, 0.12, 0.06);
      add(g, new THREE.BoxGeometry(0.22, 0.05, 0.05), lam(0x333333), 0, 0.82, 0.84);
      const pot = add(g, sphere(0.36), lam(ch.accent), 0, 1.48, 0);
      pot.scale.y = 0.75;
      const spout = add(g, new THREE.CylinderGeometry(0.05, 0.09, 0.4, 8), lam(ch.accent), 0.38, 1.55, 0);
      spout.rotation.z = -0.9;
      add(g, new THREE.TorusGeometry(0.16, 0.04, 6, 12), lam(ch.accent), -0.38, 1.5, 0);
      add(g, sphere(0.08, 8, 6), lam(0xffffff), 0, 1.78, 0);
      break;
    }
    case 'robot': {
      add(g, new THREE.BoxGeometry(0.9, 0.7, 0.6), phong(0xb8c2cc), 0, 0.4, 0);
      add(g, new THREE.BoxGeometry(0.9, 0.12, 0.62), lam(ch.accent), 0, 0.55, 0);
      add(g, new THREE.BoxGeometry(0.7, 0.55, 0.55), phong(0xd5dde4), 0, 1.05, 0);
      eyes(g, 1.1, 0.28, 0.15, 0.09, 0x22e0ff);
      add(g, new THREE.CylinderGeometry(0.03, 0.03, 0.4, 6), lam(0x555555), 0, 1.5, 0);
      add(g, sphere(0.09, 8, 6), lam(0xff3344), 0, 1.72, 0);
      break;
    }
    case 'frog': {
      const b = add(g, sphere(0.62), lam(0x5fbf4a), 0, 0.5, 0);
      b.scale.y = 0.85;
      for (const s of [-1, 1]) {
        add(g, sphere(0.17, 10, 8), lam(0xffffff), s * 0.24, 0.92, 0.32);
        add(g, sphere(0.08, 8, 6), lam(0x111111), s * 0.24, 0.94, 0.46);
      }
      add(g, new THREE.TorusGeometry(0.18, 0.03, 6, 12, Math.PI), lam(0x2d6b25), 0, 0.62, 0.5).rotation.z = Math.PI;
      const cap = add(g, dome(0.62), lam(ch.accent), 0, 1.0, -0.05);
      cap.scale.y = 0.7;
      for (let k = 0; k < 6; k++) {
        const a = k * 1.05;
        add(g, sphere(0.09, 8, 6), lam(0xffffff), Math.cos(a) * 0.4, 1.22, Math.sin(a) * 0.4 - 0.05);
      }
      break;
    }
    case 'astro': {
      add(g, new THREE.CylinderGeometry(0.4, 0.44, 0.7, 12), lam(0xf4f4f8), 0, 0.35, 0);
      add(g, new THREE.TorusGeometry(0.41, 0.06, 6, 16), lam(ch.color), 0, 0.5, 0).rotation.x = Math.PI / 2;
      add(g, new THREE.BoxGeometry(0.6, 0.6, 0.3), lam(0xcfd3dc), 0, 0.5, -0.4);
      add(g, sphere(0.3), lam(0xb68cff), 0, 1.05, 0);
      eyes(g, 1.08, 0.27, 0.11, 0.05);
      add(g, sphere(0.48, 16, 12), new THREE.MeshPhongMaterial({ color: ch.accent, transparent: true, opacity: 0.3, shininess: 100 }), 0, 1.05, 0);
      break;
    }
    case 'troll': {
      add(g, new THREE.DodecahedronGeometry(0.72), lam(0x8b8f94, { flatShading: true }), 0, 0.5, 0);
      add(g, new THREE.DodecahedronGeometry(0.45), lam(0x9a9ea3, { flatShading: true }), 0, 1.2, 0.05);
      eyes(g, 1.28, 0.42, 0.15, 0.07, 0xffd23f);
      add(g, sphere(0.13, 8, 6), lam(0x7d8186), 0, 1.15, 0.5);
      add(g, new THREE.CylinderGeometry(0.03, 0.03, 0.35, 6), lam(0x3c8a3c), 0.15, 1.75, 0);
      for (let k = 0; k < 5; k++) {
        const a = k * 1.256;
        add(g, sphere(0.09, 8, 6), lam(ch.accent), 0.15 + Math.cos(a) * 0.12, 1.95, Math.sin(a) * 0.12);
      }
      add(g, sphere(0.07, 8, 6), lam(0xffe14a), 0.15, 1.95, 0);
      break;
    }
  }
  return g;
}

export function buildKart(ch) {
  const root = new THREE.Group();
  const body = new THREE.Group();
  root.add(body);
  const c = phong(ch.color), acc = phong(ch.accent), dark = lam(0x222222);
  add(body, new THREE.BoxGeometry(2.2, 0.5, 3.0), c, 0, 0.55, 0);
  add(body, new THREE.BoxGeometry(1.7, 0.4, 1.0), c, 0, 0.6, 1.8);
  add(body, new THREE.BoxGeometry(2.5, 0.3, 0.35), acc, 0, 0.45, 2.3);
  add(body, new THREE.BoxGeometry(2.3, 0.14, 0.55), acc, 0, 1.3, -1.55);
  for (const s of [-1, 1]) add(body, new THREE.BoxGeometry(0.1, 0.55, 0.1), dark, s * 0.8, 1.0, -1.55);
  add(body, new THREE.BoxGeometry(1.2, 0.8, 0.3), dark, 0, 1.05, -0.75);
  add(body, new THREE.TorusGeometry(0.28, 0.06, 6, 14), dark, 0, 1.2, 0.75).rotation.x = -0.6;
  for (const s of [-1, 1]) add(body, new THREE.CylinderGeometry(0.16, 0.2, 0.5, 8), dark, s * 0.6, 0.6, -1.7).rotation.x = Math.PI / 2;
  const wheels = [];
  const wGeo = new THREE.CylinderGeometry(0.45, 0.45, 0.5, 14);
  const wMat = lam(0x1b1b1b);
  const hubMat = lam(ch.accent);
  for (const [x, z] of [[-1.2, 1.1], [1.2, 1.1], [-1.2, -1.05], [1.2, -1.05]]) {
    const w = add(body, wGeo, wMat, x, 0.45, z);
    w.rotation.z = Math.PI / 2;
    add(w, new THREE.CylinderGeometry(0.2, 0.2, 0.52, 8), hubMat);
    wheels.push(w);
  }
  const driver = buildDriver(ch);
  driver.position.set(0, 0.8, -0.15);
  body.add(driver);
  const shield = new THREE.Mesh(sphere(2.4, 18, 14), new THREE.MeshPhongMaterial({ color: 0x7fe8ff, transparent: true, opacity: 0.28, shininess: 100, depthWrite: false }));
  shield.position.y = 1.0;
  shield.visible = false;
  root.add(shield);
  return { root, body, wheels, driver, shield };
}

export function buildItemMesh(type) {
  const g = new THREE.Group();
  if (type === 'gumball') {
    add(g, sphere(0.6, 16, 12), phong(0x2f8bff, { shininess: 120 }));
    add(g, sphere(0.18, 8, 6), new THREE.MeshBasicMaterial({ color: 0xffffff }), 0.25, 0.3, 0.3);
  } else if (type === 'bee') {
    const b = add(g, sphere(0.55, 14, 10), lam(0xffd23f));
    b.scale.z = 1.35;
    for (const z of [-0.2, 0.25]) add(g, new THREE.TorusGeometry(0.5, 0.09, 6, 16), lam(0x222222), 0, 0, z);
    for (const s of [-1, 1]) {
      const w = add(g, new THREE.PlaneGeometry(0.9, 0.5), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.7, side: THREE.DoubleSide }), s * 0.55, 0.45, 0);
      w.rotation.z = s * 0.4;
      w.userData.wing = s;
    }
    add(g, new THREE.ConeGeometry(0.12, 0.35, 8), lam(0x222222), 0, 0, -0.85).rotation.x = -Math.PI / 2;
    eyes(g, 0.15, 0.68, 0.18, 0.08);
  } else if (type === 'jelly') {
    const d = add(g, dome(1.0), new THREE.MeshPhongMaterial({ color: 0x55e07a, transparent: true, opacity: 0.85, shininess: 100 }));
    d.scale.y = 0.6;
    add(g, sphere(0.15, 8, 6), new THREE.MeshBasicMaterial({ color: 0xffffff }), 0.3, 0.45, 0.3);
  }
  return g;
}

export function buildItemBox() {
  const g = new THREE.Group();
  const outer = add(g, new THREE.OctahedronGeometry(1.1), new THREE.MeshPhongMaterial({ color: 0xffffff, emissive: 0x6633ff, transparent: true, opacity: 0.8, shininess: 100 }));
  add(g, new THREE.IcosahedronGeometry(0.42), new THREE.MeshBasicMaterial({ color: 0xffffff }));
  g.userData.outer = outer;
  return g;
}

export class Particles {
  constructor(parent, n = 320) {
    this.list = [];
    this.next = 0;
    const geo = new THREE.BoxGeometry(0.3, 0.3, 0.3);
    for (let i = 0; i < n; i++) {
      const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, depthWrite: false }));
      m.visible = false;
      parent.add(m);
      this.list.push({ m, life: 0, max: 1, vx: 0, vy: 0, vz: 0, g: 0, size: 1 });
    }
  }
  emit(x, y, z, color, o = {}) {
    const p = this.list[this.next];
    this.next = (this.next + 1) % this.list.length;
    const s = o.spread ?? 1;
    p.m.visible = true;
    p.m.position.set(x, y, z);
    p.m.material.color.setHex(color);
    p.m.material.opacity = 1;
    p.size = o.size ?? 1;
    p.m.scale.setScalar(p.size);
    p.life = p.max = o.life ?? 0.5;
    p.vx = (o.vx ?? 0) + (Math.random() - 0.5) * s;
    p.vy = (o.vy ?? 0) + (Math.random() - 0.5) * s;
    p.vz = (o.vz ?? 0) + (Math.random() - 0.5) * s;
    p.g = o.g ?? 0;
  }
  burst(x, y, z, colors, n = 20, speed = 8) {
    for (let i = 0; i < n; i++) {
      const a = Math.random() * Math.PI * 2, b = Math.random() * Math.PI;
      this.emit(x, y, z, colors[i % colors.length], {
        vx: Math.cos(a) * Math.sin(b) * speed, vy: Math.cos(b) * speed * 0.6 + 3, vz: Math.sin(a) * Math.sin(b) * speed,
        life: 0.6 + Math.random() * 0.3, size: 1.2, g: 12, spread: 1,
      });
    }
  }
  update(dt) {
    for (const p of this.list) {
      if (p.life <= 0) continue;
      p.life -= dt;
      if (p.life <= 0) { p.m.visible = false; continue; }
      p.vy -= p.g * dt;
      p.m.position.x += p.vx * dt;
      p.m.position.y += p.vy * dt;
      p.m.position.z += p.vz * dt;
      const a = p.life / p.max;
      p.m.material.opacity = a;
      p.m.scale.setScalar(p.size * (0.4 + 0.6 * a));
    }
  }
  clear() { for (const p of this.list) { p.life = 0; p.m.visible = false; } }
}
