// Gumdrop Grand Prix — game data (all characters, tracks and items are original).

export const LAPS = 3;
export const MAX_RACERS = 8;

// stats are 1..5
export const CHARACTERS = [
  { id: 'pip', name: 'Pip', desc: 'Brave kid in a lucky orange beanie and racing goggles.', build: 'kid',
    color: 0xff7a2f, accent: 0x2f6bff, stats: { speed: 3, accel: 3, handling: 3, weight: 3 } },
  { id: 'noodle', name: 'Noodle', desc: 'An extra-long ferret who never stops wiggling.', build: 'ferret',
    color: 0xf2c14e, accent: 0x2e9c8f, stats: { speed: 2, accel: 5, handling: 4, weight: 1 } },
  { id: 'marzipan', name: 'Duchess Marzipan', desc: 'Ruler of the Sugar Hills. Her crown is a real cake.', build: 'royal',
    color: 0xff9bd2, accent: 0xffd36b, stats: { speed: 3, accel: 3, handling: 4, weight: 2 } },
  { id: 'sleet', name: 'Old Sleet', desc: 'A grumpy yeti who wears a teapot for a hat.', build: 'yeti',
    color: 0x6fb7ff, accent: 0xd97b4a, stats: { speed: 5, accel: 1, handling: 2, weight: 5 } },
  { id: 'bolt', name: 'Bolt', desc: 'A tiny robot built from tin cans and spare springs.', build: 'robot',
    color: 0x9aa6b2, accent: 0xffd200, stats: { speed: 4, accel: 2, handling: 3, weight: 3 } },
  { id: 'mossy', name: 'Mossy', desc: 'A shy frog who lives under a mushroom cap.', build: 'frog',
    color: 0x3fbf6f, accent: 0xe8413a, stats: { speed: 2, accel: 4, handling: 5, weight: 2 } },
  { id: 'zara', name: 'Zara Comet', desc: 'Space courier. Never takes off her bubble helmet.', build: 'astro',
    color: 0x8f5bff, accent: 0x22e0ff, stats: { speed: 4, accel: 3, handling: 3, weight: 2 } },
  { id: 'grumble', name: 'Grumble', desc: 'A big rock troll with a flower he never lets wilt.', build: 'troll',
    color: 0x7a6a5a, accent: 0xff6fb5, stats: { speed: 5, accel: 2, handling: 1, weight: 5 } },
];

export const TRACKS = [
  {
    id: 'gumdrop', name: 'Gumdrop Loop', desc: 'Rolling candy meadows. A friendly first race.',
    width: 26, sky: 0x9fd8ff, ground: 0x7bd36b, road: 0x7d8496, shoulder: 0xf6d27a, skirt: 0xd9a74a,
    curbA: 0xff4f7a, curbB: 0xffffff, fence: 0xff8fb1, dust: 0xe8c27a, decor: 'candy', fog: [140, 560],
    points: [[0,0,0],[80,0,-10],[150,2,20],[180,4,90],[150,4,160],[90,2,170],[60,0,120],[10,0,140],
             [-60,0,180],[-130,3,150],[-160,5,80],[-140,3,10],[-80,0,-20]],
    pads: [0.2, 0.56, 0.84], boxes: [0.12, 0.45, 0.72],
  },
  {
    id: 'fjord', name: 'Frosty Fjord', desc: 'Snowy hills and long icy sweepers.',
    width: 24, sky: 0xcfe8ff, ground: 0xf4f8ff, road: 0x6f7c93, shoulder: 0xdfe9f5, skirt: 0xb9cde3,
    curbA: 0x3aa0ff, curbB: 0xffffff, fence: 0x7fc4ff, dust: 0xffffff, decor: 'ice', fog: [120, 520],
    points: [[0,0,0],[100,0,0],[180,6,-40],[240,10,20],[230,12,110],[160,8,150],[120,4,100],[60,2,140],
             [0,6,220],[-90,10,200],[-120,6,120],[-60,2,80],[-110,0,20],[-60,0,-10]],
    pads: [0.15, 0.5, 0.78], boxes: [0.08, 0.38, 0.66],
  },
  {
    id: 'lava', name: 'Licorice Lava', desc: 'A licorice road over a sea of glowing lava.',
    width: 24, sky: 0x3a1e2e, ground: 0xff5a1f, road: 0x2f2a33, shoulder: 0x5a2b2b, skirt: 0x3a1a1a,
    curbA: 0xff6a00, curbB: 0x1a1a1a, fence: 0xff3b1f, dust: 0x553333, decor: 'volcano', fog: [100, 460],
    points: [[0,0,0],[90,0,10],[160,4,-20],[220,8,40],[200,10,120],[130,12,130],[100,8,70],[40,4,90],
             [0,6,170],[-80,10,160],[-100,6,80],[-170,4,60],[-180,2,-30],[-90,0,-40]],
    pads: [0.25, 0.6, 0.88], boxes: [0.1, 0.42, 0.7],
  },
];

export const ITEM_INFO = {
  gumball: { icon: '🔵', name: 'Gumball' },
  bee:     { icon: '🐝', name: 'Homing Bee' },
  jelly:   { icon: '🍮', name: 'Jelly Puddle' },
  fizz:    { icon: '🥤', name: 'Fizz Boost' },
  fizz3:   { icon: '🥤', name: 'Triple Fizz' },
  bubble:  { icon: '🛡️', name: 'Bubble Shield' },
};

// Better items for racers further back.
const TABLE = [
  [0.25, { gumball: 40, jelly: 40, bubble: 15, fizz: 5 }],
  [0.6,  { gumball: 30, jelly: 15, bee: 20, fizz: 25, bubble: 10 }],
  [1.01, { bee: 30, fizz: 25, fizz3: 30, gumball: 10, bubble: 5 }],
];

export function rollItem(frac) {
  const row = TABLE.find(r => frac < r[0])[1];
  let tot = 0;
  for (const k in row) tot += row[k];
  let r = Math.random() * tot;
  for (const k in row) { r -= row[k]; if (r <= 0) return k; }
  return 'gumball';
}

export const charById = id => CHARACTERS.find(c => c.id === id) || CHARACTERS[0];
export const trackById = id => TRACKS.find(t => t.id === id) || TRACKS[0];

export function mulberry32(a) {
  return function () {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

export const hex = n => '#' + n.toString(16).padStart(6, '0');
