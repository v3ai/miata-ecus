#!/usr/bin/env python3
"""Annotated pictures for INSTALL.md, made from the design files so they can't drift from the boards.

  images/annotated_<years>.jpg               the assembled ECU from above, every user-facing part labelled
  images/annotated_motherboard_<years>.jpg   the motherboard alone: sockets, fuses, jumpers and option links
  images/header_pinouts.png                  where pin 1 is on J5 and J2 (pad positions from the PCB file)

The board pictures are the 3D viewer (viewer/index.html) looking straight down; the label positions are the viewer's
own part boxes projected through its camera, so a label always points at the real part.

usage: scripts/annotate.py --three <dir> [--out images] [--only 8995 ...] [--no-boards] [--no-pinouts]
  <dir> is the unpacked three.js 0.160.0 npm package (npm pack three@0.160.0 && tar xf three-0.160.0.tgz), served in
  place of the CDN the viewer loads it from. Needs Playwright with Chromium, Pillow and KiCad's pcbnew module.
"""
import argparse, base64, functools, http.server, io, json, os, socket, sys, threading, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIEWER = os.path.join(ROOT, 'viewer')

YEARS = {   # viewer key: (file suffix, title, motherboard folder, pcb file, harness header)
    '8995': ('1989-95', '1989–95 (NA)', '1989-95', 'miata_mb_8995.kicad_pcb', 'TE 174917-6, 48 pins, two plugs'),
    '9697': ('1996-97', '1996–97 (NA, 1.8, OBD-II)', '1996-97', 'miata_mb_9697.kicad_pcb', 'TE 178780-1, 76 positions'),
    '9900': ('1999-2000', '1999–2000 (NB)', '1999-2000', 'miata_mb_9900.kicad_pcb', 'TE 178780-1, 76 positions'),
    '0105': ('2001-05', '2001–05 (NB, VVT)', '2001-05', 'miata_mb_0105.kicad_pcb', 'TE 353830-5, 72 positions'),
}
DAUGHTER_REV = '0.10'

# ---- what gets a label -------------------------------------------------------------------------------------------
# target: 'mb:REF' / 'd:REF' = a part on the motherboard / daughterboard; 'mbhole:N' / 'dhole:N' = a mounting hole.
PROVISIONAL = ('9697', '9900', '0105')      # outline and holes still follow the 1989-95 case


def assembled_labels(y):
    hdr = YEARS[y][4]
    holes = ('M4, in the same places as the stock board’s.' if y not in PROVISIONAL else
             'M4. Provisional on this board: placed as in the 1989–95 case until this year’s case is measured.')
    L = [
        ('mb:J1', 'Harness plug (J1)', f'The car’s own ECU plugs go here. {hdr}.'),
        ('d:U1', 'Daughterboard', 'The computer itself, the same on every year. It sits on two 40-pin sockets.'),
        ('dhole:0', 'Standoff screws (4)', 'M3. Hold the daughterboard 11 mm above the motherboard.'),
        ('d:D3', 'Status lights', 'Green: power and running. Blue: talking to the laptop. Yellow: warning. Red: fault.'),
        ('d:SW1', 'BOOT and RESET buttons', 'Hold BOOT while powering up to start the firmware loader. RESET restarts the ECU.'),
        ('d:J4', 'microSD card socket', 'For logging to a card. The metal lid slides and hinges up.'),
        ('mb:U2', 'MAP sensor', 'Push the vacuum hose from the intake manifold onto its barb.'),
        ('mb:J5', 'Add-on header (J5)', 'Ribbon-cable header: boost valve, knock sensor, coils 3 and 4, flex-fuel and nitrous inputs, '
                                        'CAN bus, 5 V and 12 V.'),
        ('mb:J4', 'USB-C (J4)', 'Tuning with TunerStudio, logging and firmware updates.'),
        ('mb:J2', 'Wideband oxygen sensor (J2)', 'Takes AEM’s X-Series sensor harness (30-3427) to a Bosch LSU 4.9. No separate controller needed.'),
        ('mb:F1', 'Sensor-heater fuse (F1)', 'Resets itself when it cools. Feeds the wideband sensor’s heater.'),
        ('mbhole:0', 'Case screw holes (6)', holes),
    ]
    if y == '8995':
        L += [('mb:JP3', 'Year jumpers, left (JP3, JP5, JP4)', 'Second fan, tachometer and the 1994–95 solenoid. Set for the car: table in INSTALL.md.'),
              ('mb:JP5', None, None), ('mb:JP4', None, None),
              ('mb:JP6', 'Year jumpers, right (JP6, JP1, JP2)', 'Airflow-meter wire and the two injector jumpers: PAIR for 1989–93, SEQ for 1994–95.'),
              ('mb:JP1', None, None), ('mb:JP2', None, None)]
    return L

MB_COMMON = [
    ('mb:J1', 'Harness plug (J1)', 'Soldered by hand: salvaged from a stock ECU, or a new one.'),
    ('mb:JD1', 'Daughterboard socket JD1', 'Two 1×40 sockets, JD1 and JD2. The daughterboard only fits one way round.'),
    ('mb:JD2', 'Daughterboard socket JD2', None),
    ('mbstand:0', 'Standoff positions (4)', 'M3 × 11 mm standoffs, screwed from below.'),
    ('mb:F1', 'Sensor-heater fuse (F1)', 'Resets itself when it cools. Feeds the wideband sensor’s heater.'),
    ('mb:F4', 'Add-on 12 V fuse (F4)', 'Resets itself. Limits add-on pin 15 to 1.1 A.'),
    ('mb:R20', 'Pull-up options (R20–R22)', 'Not fitted. Only for a speed, A/C or clutch signal that switches to ground.'),
    ('mb:U2', 'MAP sensor', 'Lies flat, held by two M3 screws.'),
    ('mb:J5', 'Add-on header (J5)', '2×10 box header for a 20-way ribbon cable.'),
    ('mb:J4', 'USB-C (J4)', None),
    ('mb:J2', 'Wideband oxygen sensor (J2)', 'JST PUD header for AEM’s sensor harness. The wire colours are printed beside it.'),
]
MB_EXTRA = {
    '8995': [('mb:JP1', 'Injector jumpers (JP1, JP2)', 'PAIR: 1989–93 stock harness, two injectors per wire. SEQ: 1994–95. Never SEQ on a 1989–93 automatic.'),
             ('mb:JP2', None, None),
             ('mb:JP6', 'Airflow-meter wire jumper (JP6)', 'AFM: stock. BOOST: the boost valve on that wire once the meter is gone.'),
             ('mb:JP3', 'Second-fan jumper (JP3)', '90-93 or 94-95: which harness pin the relay is on.'),
             ('mb:JP5', 'Tachometer jumper (JP5)', 'Open with the stock igniter. Fitted only after a coil-on-plug conversion.'),
             ('mb:JP4', '1994–95 jumper (JP4)', 'Fitted on 1994–95 (pressure-regulator solenoid). Open on 1989–93.'),
             ('mb:R28', 'Throttle-sensor links (R28–R30)', 'R29 is fitted. For a real throttle position sensor on a manual car: fit R28, move R29 to R30.'),
             ('mb:R30', None, None),
             ('mb:D3', 'Spare injector clamps (D3, D4)', 'Not fitted: a rev 0.10 daughterboard clamps each injector itself.')],
    '9900': [('mb:F2', 'Idle-valve fuse (F2)', 'Resets itself.')],
    '0105': [('mb:F2', 'Idle-valve fuse (F2)', 'Resets itself.'), ('mb:F3', 'VVT-valve fuse (F3)', 'Resets itself.')],
}

EXPORT = ('\nwindow.__v = {THREE, camera, controls, scene, renderer, ground, PCBS, assy, switchMode, placeAll, '
          'requestRender, stopAnim(){ anim = null; }, get parts(){ return parts; }};\n')
CSS = ('aside,.views,.status,.scale,.tip{display:none!important}'
       '.app{display:block!important;padding:0!important;margin:0!important}'
       '.stage{position:fixed!important;inset:0!important;border-radius:0!important;border:0!important;'
       'background:#eeede8!important}body{margin:0!important;background:#eeede8!important}')

VIEW_JS = r"""
async ({year, bare}) => {
  const v = window.__v, T = v.THREE, mb = v.PCBS['mb' + year], d = v.PCBS.d;
  await v.switchMode('a', year);
  const t0 = Date.now();
  while (!document.getElementById('loading').hidden || !mb.ready) {
    if (Date.now() - t0 > 600000) throw new Error('motherboard did not load');
    await new Promise(r => setTimeout(r, 250));
  }
  v.stopAnim();                                    // the viewer's own fly-to-view animation would move the camera back
  if (!v.flatEnv) {
    // The viewer's studio has a big softbox overhead. Seen from straight above, the glossy solder mask mirrors it and
    // the whole board washes out, so for this view the ceiling is dim and the light comes from the sides.
    const env = new T.Scene();
    const room = new T.Mesh(new T.BoxGeometry(100, 60, 100), new T.MeshBasicMaterial({color: new T.Color(0.05, 0.052, 0.055), side: T.BackSide}));
    room.position.y = 20; env.add(room);
    const panel = (w, h, k, pos) => { const m = new T.Mesh(new T.PlaneGeometry(w, h),
      new T.MeshBasicMaterial({color: new T.Color(1, 0.99, 0.97).multiplyScalar(k), side: T.DoubleSide}));
      m.position.set(...pos); m.lookAt(0, 0, 0); env.add(m); };
    panel(40, 26, 0.5, [0, 48, 6]);
    panel(10, 40, 8, [-46, 14, -10]); panel(10, 40, 7, [46, 14, 14]); panel(60, 10, 5, [0, 12, 48]); panel(60, 10, 5, [0, 12, -48]);
    const pm = new T.PMREMGenerator(v.renderer); v.flatEnv = pm.fromScene(env, 0.02).texture; pm.dispose();
  }
  v.scene.environment = v.flatEnv;
  d.group.visible = !bare; v.assy.visible = !bare;
  // straight down, long lens: almost no perspective, so tall parts don't lean and labels land on their parts
  const box = new T.Box3().setFromObject(mb.group), c = box.getCenter(new T.Vector3());
  const ext = Math.max(box.max.x - box.min.x, box.max.z - box.min.z) + 14, fov = 10;
  const dist = (ext / 2) / Math.tan(fov * Math.PI / 360);
  v.controls.enableDamping = false; v.controls.maxDistance = 1e6;
  v.camera.fov = fov; v.camera.near = dist - 150; v.camera.far = dist + 150;
  v.controls.target.set(c.x, 8, c.z); v.camera.position.set(c.x, 8 + dist, c.z + 0.05);
  v.camera.updateProjectionMatrix(); v.controls.update(); v.camera.updateMatrixWorld(true);
  v.renderer.shadowMap.needsUpdate = true; v.requestRender();
  const cv = document.getElementById('c').getBoundingClientRect();
  const px = (x, y, z) => { const p = new T.Vector3(x, y, z).project(v.camera);
    return [cv.left + (p.x + 1) / 2 * cv.width, cv.top + (1 - p.y) / 2 * cv.height]; };
  const out = {parts: [], crop: null, holes: {}};
  const offs = {};          // board mm -> world: world x = mm x - offs[0], world z = mm y - offs[1]; offs[2] = board top
  for (const p of v.parts) {
    const k = p.pcb === d ? 'd' : 'mb';
    if (!offs[k]) offs[k] = [p.x0 - p.box.min.x, p.y0 - p.box.min.z, p.pcb.group.position.y + 1.6];
  }
  for (const p of v.parts) {
    const k = p.pcb === d ? 'd' : 'mb';
    if (k === 'd' && bare) continue;
    const cc = p.box.getCenter(new T.Vector3());
    const a = px(p.box.min.x, p.box.max.y, p.box.min.z), b = px(p.box.max.x, p.box.max.y, p.box.max.z);
    out.parts.push({k, ref: p.ref, c: px(cc.x, p.box.max.y, cc.z), bb: [a[0], a[1], b[0], b[1]]});
  }
  // mounting holes are listed in board-edge mm; the viewer centres each board on its `centre` (as its own standoff code does)
  const hole = (pcb, hx, hy, y) => px(pcb.group.position.x + hx - pcb.centre[0], y, pcb.group.position.z + hy - pcb.centre[1]);
  for (const [k, pcb] of [['mb', mb], ['d', d]]) {
    if (!offs[k]) continue;
    out.holes[k] = (pcb.holes || []).map(([hx, hy]) => hole(pcb, hx, hy, offs[k][2]));
  }
  // where the daughterboard's posts stand on the motherboard (for the bare view)
  out.holes.stand = (d.holes || []).map(([hx, hy]) => hole(d, hx, hy, 1.6));
  const cs = [];
  for (const x of [box.min.x, box.max.x]) for (const z of [box.min.z, box.max.z]) for (const y of [box.min.y, box.max.y]) cs.push(px(x, y, z));
  const m = 26;
  out.crop = [Math.min(...cs.map(q => q[0])) - m, Math.min(...cs.map(q => q[1])) - m,
              Math.max(...cs.map(q => q[0])) + m, Math.max(...cs.map(q => q[1])) + m];
  return out;
}
"""

PAGE = r"""<!doctype html><meta charset="utf-8">
<style>
*{box-sizing:border-box}
body{margin:0;background:#f5f4f0;color:#16181a;font:15px/1.38 Inter,"DejaVu Sans",Arial,sans-serif}
#wrap{position:relative;width:__TW__px;padding:30px 0 22px}
h1{font:800 30px/1.1 Inter,"DejaVu Sans",Arial,sans-serif;margin:0 0 4px __PAD__px;letter-spacing:-.01em}
.sub{margin:0 0 18px __PAD__px;color:#5a5f63;font-size:15.5px}
#stage{position:relative;height:__IH__px}
#pic{position:absolute;left:__COL__px;top:0;width:__IW__px;height:__IH__px;border-radius:6px}
svg{position:absolute;left:0;top:0;width:__TW__px;height:__IH__px;overflow:visible}
.lab{position:absolute;width:__LW__px}
.lab b{display:block;font-weight:700;font-size:16.5px;line-height:1.25}
.lab span{display:block;color:#484d51;font-size:14px;margin-top:2px}
.lab.l{text-align:right}
.foot{margin:16px __PAD__px 0;color:#6b7074;font-size:13px}
</style>
<div id="wrap"><h1>__TITLE__</h1><p class="sub">__SUB__</p>
<div id="stage"><img id="pic" src="data:image/png;base64,__IMG__"><svg id="lines"></svg></div>
<p class="foot">__FOOT__</p></div>
<script>
(() => {      // a function scope: the next picture reuses this page, and top-level consts would clash
const L = __LABELS__, COL = __COL__, IW = __IW__, IH = __IH__, LW = __LW__, PAD = __PAD__, TW = __TW__;
const stage = document.getElementById('stage'), svg = document.getElementById('lines');
const els = L.map(l => { const e = document.createElement('div'); e.className = 'lab ' + l.side;
  e.innerHTML = '<b></b>' + (l.text ? '<span></span>' : ''); e.querySelector('b').textContent = l.title;
  if (l.text) e.querySelector('span').textContent = l.text; stage.appendChild(e);
  e.style.left = (l.side === 'l' ? PAD : COL + IW + (COL - PAD - LW)) + 'px'; return e; });
for (const side of ['l', 'r']) {
  const idx = L.map((l, i) => i).filter(i => L[i].side === side).sort((a, b) => L[a].t[0][1] - L[b].t[0][1]);
  const gap = 16, h = idx.map(i => els[i].offsetHeight);
  let y = idx.map((i, n) => L[i].t[0][1] - 12);
  for (let n = 0; n < idx.length; n++) y[n] = Math.max(y[n], n ? y[n-1] + h[n-1] + gap : 0);
  const over = y.length ? y[y.length-1] + h[h.length-1] - IH : 0;
  if (over > 0) { y[y.length-1] -= over; for (let n = idx.length - 2; n >= 0; n--) y[n] = Math.min(y[n], y[n+1] - h[n] - gap); }
  idx.forEach((i, n) => { els[i].style.top = y[n] + 'px'; L[i].y = y[n] + 11; });
}
let s = '';
L.forEach((l, i) => { for (const t of l.t) {
  const x0 = l.side === 'l' ? PAD + LW + 10 : COL + IW + (COL - PAD - LW) - 10, x1 = l.side === 'l' ? x0 + 18 : x0 - 18;
  const tx = COL + t[0], ty = t[1], pts = `${x0},${l.y} ${x1},${l.y} ${tx},${ty}`;
  s += `<polyline points="${pts}" fill="none" stroke="#f5f4f0" stroke-width="4.5" stroke-linejoin="round" stroke-linecap="round" opacity=".9"/>`
     + `<polyline points="${pts}" fill="none" stroke="#16181a" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"/>`
     + `<circle cx="${tx}" cy="${ty}" r="6.5" fill="#f5f4f0"/><circle cx="${tx}" cy="${ty}" r="4" fill="#d6402b"/>`; } });
svg.innerHTML = s;
})();
</script>
"""


def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p


def serve_viewer():
    port = free_port()
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=VIEWER)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port


def resolve(target, geo):
    kind, ref = target.split(':')
    if kind in ('mb', 'd'):
        hit = [p for p in geo['parts'] if p['k'] == kind and p['ref'] == ref]
        return hit[0]['c'] if hit else None
    key = {'mbhole': 'mb', 'dhole': 'd', 'mbstand': 'stand'}[kind]
    hs = geo['holes'].get(key) or []
    if not hs:
        return None
    if kind == 'mbhole':       # the hole nearest the top-right corner reads best against the label columns
        return max(hs, key=lambda q: q[0] - q[1])
    return max(hs, key=lambda q: q[0] - q[1]) if kind == 'dhole' else min(hs, key=lambda q: q[0] + q[1])


def compose(pg, png, geo, labels, title, sub, foot, out_path):
    from PIL import Image
    x0, y0, x1, y1 = geo['crop']
    iw, ih = int(round(x1 - x0)), int(round(y1 - y0))
    col, lw, pad = 392, 330, 34
    L, merged = [], {}
    for target, ttl, text in labels:
        pt = resolve(target, geo)
        if pt is None:
            continue
        pt = [pt[0] - x0, pt[1] - y0]
        if ttl is None:                       # a second pointer for the label before it
            L[-1]['t'].append(pt); continue
        L.append({'title': ttl, 'text': text or '', 't': [pt], 'side': 'l' if pt[0] < iw / 2 else 'r'})
    html = PAGE
    for k, v in {'__TW__': iw + 2 * col, '__PAD__': pad, '__IH__': ih, '__IW__': iw, '__COL__': col, '__LW__': lw,
                 '__TITLE__': title, '__SUB__': sub, '__FOOT__': foot,
                 '__IMG__': base64.b64encode(png).decode(), '__LABELS__': json.dumps(L)}.items():
        html = html.replace(k, str(v))
    pg.set_viewport_size({'width': iw + 2 * col, 'height': ih + 200})
    pg.set_content(html); pg.wait_for_function("document.getElementById('lines').children.length > 0")
    time.sleep(0.4)
    shot = pg.locator('#wrap').screenshot()
    Image.open(io.BytesIO(shot)).convert('RGB').save(out_path, quality=88, optimize=True)
    print('wrote', os.path.relpath(out_path, ROOT), f'{iw + 2 * col}x', len(L), 'labels')


def boards(args):
    from playwright.sync_api import sync_playwright
    three = os.path.abspath(args.three)
    srv, port = serve_viewer()

    def cdn(route):
        f = os.path.join(three, route.request.url.split('three@0.160.0/')[1])
        route.fulfill(path=f, content_type='application/javascript') if os.path.exists(f) else route.abort()

    def page_with_handles(route):
        body = open(os.path.join(VIEWER, 'index.html'), encoding='utf-8').read()
        i = body.rindex('</script>')
        route.fulfill(body=body[:i] + EXPORT + body[i:], content_type='text/html; charset=utf-8')

    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        pg = b.new_page(viewport={'width': 1500, 'height': 1500}, device_scale_factor=1)
        pg.route('https://cdn.jsdelivr.net/**', cdn)
        pg.route('**/index.html', page_with_handles)
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(f'http://127.0.0.1:{port}/index.html')
        pg.wait_for_function("document.getElementById('loading').hidden", timeout=600000)
        pg.add_style_tag(content=CSS); time.sleep(3)
        jobs = []          # composed afterwards, in a second browser: this one is busy software-rendering WebGL
        for y in args.only or list(YEARS):
            suffix, name, folder, _, _ = YEARS[y]
            rev = open(os.path.join(VIEWER, 'index.html'), encoding='utf-8').read().split(f"'{y}': {{")[1].split("rev:'")[1].split("'")[0]
            foot = (f'Drawn from the design files: {name} motherboard rev {rev}, daughterboard rev {DAUGHTER_REV}. The harness plug, '
                    'the wideband connector, the card socket and the MAP sensor are simplified models. scripts/annotate.py redraws this picture.')
            for bare in (False, True):
                geo = pg.evaluate(VIEW_JS, {'year': y, 'bare': bare})
                time.sleep(args.settle)
                x0, y0, x1, y1 = geo['crop']
                png = pg.screenshot(clip={'x': x0, 'y': y0, 'width': x1 - x0, 'height': y1 - y0}, timeout=300000)
                if bare:
                    jobs.append((png, geo, MB_COMMON + MB_EXTRA.get(y, []), f'Miata ECU {name}: the motherboard alone',
                                 'Seen from above with the daughterboard lifted off: the sockets, fuses, jumpers and option links.',
                                 foot, os.path.join(args.out, f'annotated_motherboard_{suffix}.jpg')))
                else:
                    jobs.append((png, geo, assembled_labels(y), f'Miata ECU {name}: what’s what',
                                 'The assembled ECU seen from above. The connectors along the bottom edge face the opening cut in the case.',
                                 foot, os.path.join(args.out, f'annotated_{suffix}.jpg')))
        if errs:
            print('page errors:', errs)
        b.close()
        b2 = p.chromium.launch()
        comp = b2.new_page(device_scale_factor=1)
        for job in jobs:
            compose(comp, *job)
        b2.close()
    srv.shutdown()


# ---- header pin maps, from the pad positions in the PCB file ---------------------------------------------------------
AUX_NAMES = {1: ('IGN3', 'Coil 3 signal, 5 V logic'), 2: ('IGN4', 'Coil 4 signal, 5 V logic'),
             3: ('BOOST', 'Boost valve: switches to ground. Freewheel diode to pin 15 on the board'),
             4: ('ALT', 'Output to ground. In use on 1994–95 (pressure solenoid) and 1999–2005 (alternator)'),
             5: ('RELAY', 'Output to ground. In use on 1999–2000 (VICS) and 2003–05 (main relay)'),
             6: ('KNOCK', 'Knock sensor in. On 1999–2005 the stock sensor is already on it'),
             7: ('VR1+', 'Magnetic (VR) sensor input 1'), 8: ('VR1−', ''), 9: ('VR2+', 'Magnetic (VR) sensor input 2'), 10: ('VR2−', ''),
             11: ('AFR', 'Spare 0–5 V analog in'), 12: ('FLEX', 'Flex-fuel sensor signal (pull-up on the board)'),
             13: ('N2O', 'Nitrous arming switch: 12 V = armed'),
             14: ('+5 V', 'Protected sensor supply'), 15: ('+12 V', 'Switched, self-resetting 1.1 A fuse'), 16: ('GND', 'Ground'),
             17: ('GND', ''), 18: ('GND', ''), 19: ('CAN H', 'CAN bus, 500 kbit/s'), 20: ('CAN L', '')}
# the nets those names stand for: checked against the PCB file, so a pin map can't outlive a board change
AUX_NETS = {1: 'OUT_IGN3', 2: 'OUT_IGN4', 3: 'OUT_BOOST', 4: 'OUT_ALT', 5: 'OUT_MAINRLY', 6: 'IN_KNOCK', 7: 'VR1_P', 8: 'VR1_N',
            9: 'VR2_P', 10: 'VR2_N', 11: 'IN_AFR', 12: 'IN_FLEX', 13: 'IN_N2O', 14: 'V5_EXT', 15: 'AUX_VBAT', 16: 'GND',
            17: 'GND', 18: 'GND', 19: 'CAN_H', 20: 'CAN_L'}
# J2 takes AEM's X-Series sensor harness: pin numbers, names and wire colours from AEM's 30-0300 instructions
LSU_NETS = {1: 'LSU_RT', 2: 'LSU_HTR_N', 3: 'LSU_VM', 4: '', 5: 'LSU_IP', 6: 'LSU_UN', 7: '', 8: 'HTR_PWR'}
LSU_NAMES = {1: ('Trim', 'green wire · LSU trim resistor (RT)'), 2: ('H−', 'white · heater −'), 3: ('COM', 'orange · reference (VM)'),
             4: ('–', 'empty'), 5: ('Pump', 'red · pump current (IP)'), 6: ('Sense', 'black · sense cell (UN)'),
             7: ('–', 'empty'), 8: ('H+', 'brown · heater +12 V, through fuse F1')}
WIRE = {1: '#2e9c4a', 2: '#f2f2f2', 3: '#f08a24', 5: '#d6402b', 6: '#111111', 8: '#7a4a21'}     # AEM harness wire colours


def pinouts(args):
    import pcbnew
    from playwright.sync_api import sync_playwright
    first = next(iter(YEARS.values()))
    b = pcbnew.LoadBoard(os.path.join(ROOT, 'motherboards', first[2], first[3]))
    # the year-independent connectors sit in the same place on every motherboard: check, then draw once
    for _, _, folder, pcb, _ in YEARS.values():
        o = pcbnew.LoadBoard(os.path.join(ROOT, 'motherboards', folder, pcb))
        for ref in ('J2', 'J5'):
            a, c = b.FindFootprintByReference(ref), o.FindFootprintByReference(ref)
            pa = sorted((p.GetNumber(), p.GetPosition().x, p.GetPosition().y, p.GetNetname().split('/')[-1]) for p in a.Pads())
            pc = sorted((p.GetNumber(), p.GetPosition().x, p.GetPosition().y, p.GetNetname().split('/')[-1]) for p in c.Pads())
            assert pa == pc, f'{ref} differs on the {folder} motherboard'

    def pads(ref):
        return {int(p.GetNumber()): (p.GetPosition().x / 1e6, p.GetPosition().y / 1e6)
                for p in b.FindFootprintByReference(ref).Pads() if p.GetNumber()}

    for ref, nets in (('J5', AUX_NETS), ('J2', LSU_NETS)):
        got = {int(p.GetNumber()): p.GetNetname().split('/')[-1] for p in b.FindFootprintByReference(ref).Pads() if p.GetNumber()}
        got = {k: ('' if v.startswith('unconnected') else v) for k, v in got.items()}
        assert got == nets, f'{ref}: the PCB says {got}'

    def diagram(ref, names, scale, r, note, ring=None):
        P = pads(ref)
        xs, ys = [q[0] for q in P.values()], [q[1] for q in P.values()]
        m = r + 12
        w, h = (max(xs) - min(xs)) * scale + 2 * m, (max(ys) - min(ys)) * scale + 2 * m
        s = f'<svg width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}"><rect x="1" y="1" width="{w-2:.0f}" height="{h-2:.0f}" rx="9" fill="#202326"/>'
        for n, (x, yv) in sorted(P.items()):
            cx, cy = (x - min(xs)) * scale + m, (yv - min(ys)) * scale + m
            first = n == 1
            if ring and n in ring:        # the harness wire's colour around the pad
                s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r + 5}" fill="{ring[n]}"/>'
            shape = (f'<rect x="{cx-r:.1f}" y="{cy-r:.1f}" width="{2*r}" height="{2*r}" rx="4" fill="#d6402b"/>' if first
                     else f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{"#6f7377" if names[n][0] == "–" else "#c9a55a"}"/>')
            s += shape + (f'<text x="{cx:.1f}" y="{cy+5:.1f}" text-anchor="middle" font-size="{14 if r > 12 else 12}" '
                          f'font-weight="700" fill="{"#fff" if first else "#1a1a1a"}">{n}</text>')
        s += '</svg>'
        rows = ''.join(f'<tr><td class="n{" one" if n == 1 else ""}">{n}</td><td class="s">{names[n][0]}</td><td>{names[n][1]}</td></tr>'
                       for n in sorted(P))
        return f'<div class="dia">{s}<p class="note">{note}</p></div><table>{rows}</table>'

    html = f"""<!doctype html><meta charset="utf-8"><style>
*{{box-sizing:border-box}} body{{margin:0;background:#f5f4f0;color:#16181a;font:15px/1.35 Inter,"DejaVu Sans",Arial,sans-serif}}
#wrap{{width:1500px;padding:30px 34px 26px}} h1{{font:800 30px/1.1 Inter,"DejaVu Sans",Arial,sans-serif;margin:0 0 4px}}
.sub{{margin:0 0 20px;color:#5a5f63;font-size:15.5px;max-width:1100px}}
.grid{{display:grid;grid-template-columns:1.3fr 1fr;gap:18px;align-items:start}}
.card{{background:#fff;border:1px solid #dcdad3;border-radius:10px;padding:18px 20px}}
.card h2{{font:700 19px/1.2 Inter,"DejaVu Sans",Arial,sans-serif;margin:0 0 3px}} .card p.what{{margin:0 0 12px;color:#5a5f63;font-size:14px}}
.row{{display:flex;gap:20px;align-items:flex-start}} .dia{{flex:none}} .note{{margin:8px 0 0;font-size:12.5px;color:#6b7074;max-width:330px}}
table{{border-collapse:collapse;font-size:14px}} td{{padding:3px 10px 3px 0;vertical-align:top}}
td.n{{font-weight:700;width:26px;text-align:right;padding-right:10px}} td.n.one{{color:#d6402b}} td.s{{font-weight:700;white-space:nowrap}}
svg text{{font-family:Inter,"DejaVu Sans",Arial,sans-serif}}
.foot{{margin:16px 0 0;color:#6b7074;font-size:13px}}
</style><div id="wrap"><h1>Miata ECU: header pin maps</h1>
<p class="sub">Looking down on the motherboard, the way the labelled pictures show it, with the connector edge toward you. Pin 1 is the red square. The same on all four motherboards.</p>
<div class="grid">
<div class="card"><h2>J5 · Add-on header (2×10 box header, 2.54 mm)</h2><p class="what">Everything the stock harness has no wire for. A 20-way ribbon cable plugs in.</p>
<div class="row">{diagram('J5', AUX_NAMES, 17, 15, 'Odd pins are the row nearer the daughterboard, even pins the row nearer the board edge. Pin 1 is on the right. Pins 12 and 13 need a rev 0.10 daughterboard.')}</div></div>
<div class="card"><h2>J2 · Wideband sensor (JST PUD, 2×4, 2 mm)</h2><p class="what">Takes AEM’s X-Series sensor harness 30-3427, which has the Bosch LSU 4.9 plug on its other end. The ring round each pad is the harness wire’s colour.</p>
<div class="row">{diagram('J2', LSU_NAMES, 44, 15, 'The pads as soldered, pin 1 on the left. Odd pins are the row away from the board edge. The same colours are printed on the board beside the connector: compare them with the harness before the first use.', WIRE)}</div></div>
</div>
<p class="foot">Pad positions are read from the motherboard PCB files, and the signal on each pin is checked against them, by scripts/annotate.py. The J2 pin functions and wire colours are from AEM’s instructions for the 30-0300 gauge.</p></div>"""
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={'width': 1500, 'height': 900}, device_scale_factor=1.5)
        pg.set_content(html); time.sleep(0.4)
        out = os.path.join(args.out, 'header_pinouts.png')
        pg.locator('#wrap').screenshot(path=out)
        br.close()
    print('wrote', os.path.relpath(out, ROOT))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--three', help='unpacked three@0.160.0 npm package directory')
    ap.add_argument('--out', default=os.path.join(ROOT, 'images'))
    ap.add_argument('--only', nargs='*', choices=list(YEARS))
    ap.add_argument('--settle', type=float, default=7.0, help='seconds to let the renderer finish each view')
    ap.add_argument('--no-boards', action='store_true'); ap.add_argument('--no-pinouts', action='store_true')
    a = ap.parse_args()
    if not a.no_pinouts:
        pinouts(a)
    if not a.no_boards:
        if not a.three:
            sys.exit('--three <unpacked three@0.160.0 package> is needed for the board pictures')
        boards(a)
