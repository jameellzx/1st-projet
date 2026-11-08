# Gumdrop Grand Prix

An original 3D kart racer that runs in the browser, with online multiplayer.

**Play:** https://jameellzx.github.io/1st-projet/gumdrop-gp/

- 8 original racers, each with their own speed, acceleration, handling and weight
- 3 tracks: Gumdrop Loop, Frosty Fjord, Licorice Lava
- Drifting with 3 boost levels (blue, orange, purple sparks), boost pads and rocket starts
- 6 items: Gumball, Homing Bee, Jelly Puddle, Fizz Boost, Triple Fizz, Bubble Shield
- Online: host a room, send the link, race up to 8 players. Empty spots are filled with bots.

## Controls

| Key | Action |
|---|---|
| ↑ / W | Gas |
| ↓ / S | Brake / reverse |
| ← → / A D | Steer |
| Space (hold while turning) | Drift |
| Shift / E | Use item |

## Tech

Plain HTML + JavaScript modules, [three.js](https://threejs.org) for 3D and [PeerJS](https://peerjs.com) (WebRTC) for online play. No build step. Hosted on GitHub Pages.

Run locally: `python -m http.server 8765` in the repo root, then open http://localhost:8765/gumdrop-gp/
