import * as THREE from 'three';
import { mulberry32, hex } from './data.js';

const GROUND_Y = -0.6;

function canvasTex(w, h, draw) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}

export class Track {
  constructor(def) {
    this.def = def;
    this.group = new THREE.Group();
    const pts = def.points.map(p => new THREE.Vector3(p[0], p[1], p[2]));
    const curve = new THREE.CatmullRomCurve3(pts, true, 'centripetal');
    this.length = curve.getLength();
    const N = this.N = Math.max(200, Math.round(this.length / 2));
    this.seg = this.length / N;
    const sp = curve.getSpacedPoints(N);
    this.P = []; this.T = []; this.L = [];
    for (let i = 0; i < N; i++) this.P.push(sp[i].clone());
    for (let i = 0; i < N; i++) {
      const a = this.P[(i - 1 + N) % N], b = this.P[(i + 1) % N];
      const t = new THREE.Vector3(b.x - a.x, 0, b.z - a.z).normalize();
      this.T.push(t);
      this.L.push(new THREE.Vector3(t.z, 0, -t.x));
    }
    this.half = def.width / 2;
    this.curb = 1.4;
    this.wall = this.half + 10;
    this.pads = def.pads.map(f => ({ i: Math.floor(f * N), lat: 0, w: 8 }));
    let minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
    for (const p of this.P) { minX = Math.min(minX, p.x); maxX = Math.max(maxX, p.x); minZ = Math.min(minZ, p.z); maxZ = Math.max(maxZ, p.z); }
    this.bounds = { minX: minX - this.wall, maxX: maxX + this.wall, minZ: minZ - this.wall, maxZ: maxZ + this.wall };
    this.build();
  }

  heading(i) { const t = this.T[((i % this.N) + this.N) % this.N]; return Math.atan2(t.x, t.z); }

  // Nearest point on the centre line. lat = signed sideways distance.
  locate(x, z, hint = -1) {
    const N = this.N, P = this.P;
    let best = 0, bd = Infinity;
    const scan = (i) => { const dx = x - P[i].x, dz = z - P[i].z, d = dx * dx + dz * dz; if (d < bd) { bd = d; best = i; } };
    if (hint >= 0) {
      for (let k = -25; k <= 25; k++) scan((hint + k + N) % N);
      if (bd > (this.wall + 12) ** 2) { bd = Infinity; for (let i = 0; i < N; i++) scan(i); }
    } else {
      for (let i = 0; i < N; i++) scan(i);
    }
    const p = P[best], t = this.T[best], L = this.L[best];
    const dx = x - p.x, dz = z - p.z;
    const along = dx * t.x + dz * t.z;
    const lat = dx * L.x + dz * L.z;
    let j = best, f = along / this.seg;
    if (f < 0) { j = (best - 1 + N) % N; f += 1; }
    f = Math.min(1, Math.max(0, f));
    const y = P[j].y + (P[(j + 1) % N].y - P[j].y) * f;
    return { i: best, j, f, lat, y, idxF: j + f };
  }

  pointAt(i, lat = 0, yOff = 0) {
    i = ((i % this.N) + this.N) % this.N;
    const p = this.P[i], L = this.L[i];
    return new THREE.Vector3(p.x + L.x * lat, p.y + yOff, p.z + L.z * lat);
  }

  ribbon(a, b, yOff, mat, vRep) {
    const N = this.N, pos = [], uv = [], idx = [];
    for (let i = 0; i <= N; i++) {
      const p = this.P[i % N], L = this.L[i % N];
      pos.push(p.x + L.x * a, p.y + yOff, p.z + L.z * a, p.x + L.x * b, p.y + yOff, p.z + L.z * b);
      const v = i * this.seg / vRep;
      uv.push(0, v, 1, v);
    }
    for (let i = 0; i < N; i++) { const o = i * 2; idx.push(o, o + 1, o + 2, o + 1, o + 3, o + 2); }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    geo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    geo.setIndex(idx);
    geo.computeVertexNormals();
    mat.side = THREE.DoubleSide;
    const m = new THREE.Mesh(geo, mat);
    this.group.add(m);
    return m;
  }

  // Vertical strip along the track at sideways offset `lat`.
  wallStrip(lat, topRel, botRel, mat, botAbs = null) {
    const N = this.N, pos = [], idx = [];
    for (let i = 0; i <= N; i++) {
      const p = this.P[i % N], L = this.L[i % N];
      const x = p.x + L.x * lat, z = p.z + L.z * lat;
      pos.push(x, p.y + topRel, z, x, botAbs !== null ? botAbs : p.y + botRel, z);
    }
    for (let i = 0; i < N; i++) { const o = i * 2; idx.push(o, o + 1, o + 2, o + 1, o + 3, o + 2); }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    geo.setIndex(idx);
    geo.computeVertexNormals();
    mat.side = THREE.DoubleSide;
    const m = new THREE.Mesh(geo, mat);
    this.group.add(m);
    return m;
  }

  build() {
    const d = this.def, N = this.N, g = this.group;

    const roadTex = canvasTex(128, 128, (x, w, h) => {
      x.fillStyle = hex(d.road); x.fillRect(0, 0, w, h);
      for (let i = 0; i < 600; i++) {
        x.fillStyle = Math.random() < 0.5 ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.07)';
        x.fillRect(Math.random() * w, Math.random() * h, 2, 2);
      }
      x.fillStyle = 'rgba(255,255,255,0.75)';
      x.fillRect(w / 2 - 2, 0, 4, h / 2);
    });
    this.ribbon(-this.half, this.half, 0.03, new THREE.MeshLambertMaterial({ map: roadTex }), 10);

    const curbTex = canvasTex(16, 64, (x, w, h) => {
      x.fillStyle = hex(d.curbA); x.fillRect(0, 0, w, h / 2);
      x.fillStyle = hex(d.curbB); x.fillRect(0, h / 2, w, h / 2);
    });
    const cm = new THREE.MeshLambertMaterial({ map: curbTex });
    this.ribbon(this.half, this.half + this.curb, 0.05, cm, 5);
    this.ribbon(-this.half - this.curb, -this.half, 0.05, cm.clone(), 5);

    const sm = new THREE.MeshLambertMaterial({ color: d.shoulder });
    this.ribbon(this.half + this.curb, this.wall + 1.5, 0, sm, 10);
    this.ribbon(-this.wall - 1.5, -this.half - this.curb, 0, sm.clone(), 10);

    const skirt = new THREE.MeshLambertMaterial({ color: d.skirt });
    this.wallStrip(this.wall + 1.5, 0, 0, skirt, GROUND_Y - 0.2);
    this.wallStrip(-this.wall - 1.5, 0, 0, skirt.clone(), GROUND_Y - 0.2);

    const barrier = new THREE.MeshLambertMaterial({ color: d.fence, transparent: true, opacity: 0.85 });
    this.wallStrip(this.wall + 0.6, 1.1, 0, barrier);
    this.wallStrip(-this.wall - 0.6, 1.1, 0, barrier.clone());

    // fence posts
    const postGeo = new THREE.CylinderGeometry(0.35, 0.35, 1.8, 8);
    const postMat = new THREE.MeshLambertMaterial({ color: 0xffffff });
    const count = Math.floor(N / 4) * 2;
    const posts = new THREE.InstancedMesh(postGeo, postMat, count);
    const mtx = new THREE.Matrix4();
    let n = 0;
    for (let i = 0; i < N && n < count; i += 4) {
      for (const s of [-1, 1]) {
        const p = this.pointAt(i, s * (this.wall + 0.6), 0.9);
        mtx.makeTranslation(p.x, p.y, p.z);
        posts.setMatrixAt(n++, mtx);
      }
    }
    g.add(posts);

    // ground
    const groundMat = d.decor === 'volcano'
      ? new THREE.MeshBasicMaterial({ color: d.ground })
      : new THREE.MeshLambertMaterial({ color: d.ground });
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = GROUND_Y;
    g.add(ground);

    // start line + arch
    const checker = canvasTex(64, 16, (x, w, h) => {
      for (let i = 0; i < 16; i++) for (let j = 0; j < 4; j++) {
        x.fillStyle = (i + j) % 2 ? '#111' : '#fff';
        x.fillRect(i * 4, j * 4, 4, 4);
      }
    });
    checker.wrapS = checker.wrapT = THREE.ClampToEdgeWrapping;
    const line = new THREE.Mesh(new THREE.PlaneGeometry(d.width, 3), new THREE.MeshLambertMaterial({ map: checker }));
    line.rotation.order = 'YXZ';
    line.rotation.y = this.heading(0);
    line.rotation.x = -Math.PI / 2;
    line.position.copy(this.pointAt(0, 0, 0.07));
    g.add(line);

    const archMat = new THREE.MeshLambertMaterial({ color: d.curbA });
    const arch = new THREE.Group();
    for (const s of [-1, 1]) {
      const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 9, 10), archMat);
      pole.position.set(s * (this.half + 2.5), 4.5, 0);
      arch.add(pole);
    }
    const bannerTex = canvasTex(512, 64, (x, w, h) => {
      x.fillStyle = hex(d.curbA); x.fillRect(0, 0, w, h);
      x.fillStyle = '#fff'; x.font = 'bold 40px Arial'; x.textAlign = 'center'; x.textBaseline = 'middle';
      x.fillText('GUMDROP GRAND PRIX', w / 2, h / 2 + 2);
    });
    bannerTex.wrapS = bannerTex.wrapT = THREE.ClampToEdgeWrapping;
    const banner = new THREE.Mesh(new THREE.BoxGeometry(d.width + 6, 2.2, 0.5),
      [archMat, archMat, archMat, archMat, new THREE.MeshLambertMaterial({ map: bannerTex }), new THREE.MeshLambertMaterial({ map: bannerTex })]);
    banner.position.y = 9;
    arch.add(banner);
    const ap = this.pointAt(0);
    arch.position.copy(ap);
    arch.rotation.y = this.heading(0);
    g.add(arch);

    // boost pads
    const padTex = canvasTex(64, 64, (x, w, h) => {
      x.fillStyle = '#ff8a00'; x.fillRect(0, 0, w, h);
      x.fillStyle = '#ffe14a';
      for (let k = 0; k < 2; k++) {
        const y0 = k * 32;
        x.beginPath(); x.moveTo(8, y0 + 28); x.lineTo(32, y0 + 6); x.lineTo(56, y0 + 28); x.lineTo(46, y0 + 28); x.lineTo(32, y0 + 15); x.lineTo(18, y0 + 28); x.fill();
      }
    });
    padTex.repeat.set(1, 2);
    for (const p of this.pads) {
      const pad = new THREE.Mesh(new THREE.PlaneGeometry(p.w, 9), new THREE.MeshBasicMaterial({ map: padTex }));
      pad.rotation.order = 'YXZ';
      pad.rotation.y = this.heading(p.i + 2) + Math.PI;
      pad.rotation.x = -Math.PI / 2;
      pad.position.copy(this.pointAt(p.i + 2, p.lat, 0.08));
      g.add(pad);
    }

    this.decorate();
  }

  decorate() {
    const d = this.def, g = this.group, rand = mulberry32(d.id.length * 977 + d.points.length);
    const b = this.bounds, pad = 140;
    const lam = c => new THREE.MeshLambertMaterial({ color: c });
    const pastel = [0xff8fb1, 0x9be7ff, 0xfff27a, 0xb9a6ff, 0x8af0b0, 0xffb36b];
    let placed = 0;
    for (let tries = 0; tries < 900 && placed < 170; tries++) {
      const x = b.minX - pad + rand() * (b.maxX - b.minX + pad * 2);
      const z = b.minZ - pad + rand() * (b.maxZ - b.minZ + pad * 2);
      const loc = this.locate(x, z);
      if (Math.abs(loc.lat) < this.wall + 7) continue;
      placed++;
      const o = new THREE.Group();
      const s = 0.8 + rand() * 1.4;
      if (d.decor === 'candy') {
        if (rand() < 0.55) {
          const stick = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 6, 6), lam(0xffffff));
          stick.position.y = 3; o.add(stick);
          const pop = new THREE.Mesh(new THREE.SphereGeometry(2, 14, 10), lam(pastel[Math.floor(rand() * pastel.length)]));
          pop.position.y = 7; pop.scale.z = 0.45; o.add(pop);
        } else {
          const drop = new THREE.Mesh(new THREE.SphereGeometry(2.2, 14, 10, 0, Math.PI * 2, 0, Math.PI / 2), lam(pastel[Math.floor(rand() * pastel.length)]));
          drop.scale.y = 1.4; o.add(drop);
        }
      } else if (d.decor === 'ice') {
        if (rand() < 0.6) {
          const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.5, 2, 6), lam(0x6b4a2f));
          trunk.position.y = 1; o.add(trunk);
          for (let k = 0; k < 3; k++) {
            const c = new THREE.Mesh(new THREE.ConeGeometry(3 - k * 0.7, 3.2, 8), lam(k === 2 ? 0xffffff : 0x2f6b4f));
            c.position.y = 3 + k * 2; o.add(c);
          }
        } else {
          const crystal = new THREE.Mesh(new THREE.OctahedronGeometry(2.2), new THREE.MeshLambertMaterial({ color: 0xbfe6ff, transparent: true, opacity: 0.8 }));
          crystal.scale.y = 2; crystal.position.y = 3; o.add(crystal);
        }
      } else {
        if (rand() < 0.6) {
          const rock = new THREE.Mesh(new THREE.DodecahedronGeometry(2.4), new THREE.MeshLambertMaterial({ color: 0x2a2224, flatShading: true }));
          rock.position.y = 0.8; rock.rotation.set(rand() * 3, rand() * 3, 0); o.add(rock);
        } else {
          const spire = new THREE.Mesh(new THREE.ConeGeometry(1.8, 8, 6), new THREE.MeshLambertMaterial({ color: 0x1e1719, flatShading: true }));
          spire.position.y = 4; o.add(spire);
          const tip = new THREE.Mesh(new THREE.SphereGeometry(0.9, 8, 6), new THREE.MeshBasicMaterial({ color: 0xffa040 }));
          tip.position.y = 8; o.add(tip);
        }
      }
      o.scale.setScalar(s);
      o.position.set(x, GROUND_Y, z);
      o.rotation.y = rand() * Math.PI * 2;
      g.add(o);
    }
    // distant mountains
    const cx = (b.minX + b.maxX) / 2, cz = (b.minZ + b.maxZ) / 2;
    const mCol = d.decor === 'candy' ? 0xc9a0ff : d.decor === 'ice' ? 0xe8f2ff : 0x2a1a20;
    for (let k = 0; k < 14; k++) {
      const a = (k / 14) * Math.PI * 2 + rand() * 0.3;
      const r = 520 + rand() * 120;
      const hgt = 90 + rand() * 120;
      const m = new THREE.Mesh(new THREE.ConeGeometry(70 + rand() * 50, hgt, 7), new THREE.MeshLambertMaterial({ color: mCol, flatShading: true }));
      m.position.set(cx + Math.cos(a) * r, GROUND_Y + hgt / 2, cz + Math.sin(a) * r);
      g.add(m);
      if (d.decor === 'volcano' && k % 4 === 0) {
        const glow = new THREE.Mesh(new THREE.SphereGeometry(14, 10, 8), new THREE.MeshBasicMaterial({ color: 0xff6a1f }));
        glow.position.set(m.position.x, GROUND_Y + hgt, m.position.z);
        g.add(glow);
      }
    }
  }
}
