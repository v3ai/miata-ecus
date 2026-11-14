#!/usr/bin/env python3
"""The README renders and the shop's product photos: the 3D viewer with black solder mask and gold pads.

  images/daughterboard.jpg, images/assembly_1989-95.jpg, images/assembly_lifted.jpg      (README)
  website/theme/assets/render-*.jpg, website/product-images/*.jpg, website/mono-theme.zip  (shop)

usage: scripts/render_photos.py --three <dir> --assets <dir> [--build] [--no-readme] [--no-shop]
  <dir> for --three is the unpacked three.js 0.160.0 npm package (as for scripts/annotate.py).
  --assets is a scratch folder for the black-mask copy of the viewer's assets; --build fills it first by running
  viewer/pcb3d.py on every board with MASK=black FINISH=enig (one board at a time: two at once need too much memory).
Needs what viewer/pcb3d.py and scripts/annotate.py need (KiCad, trimesh, cascadio, gltfpack, Playwright, Pillow).
The pictures are the viewer's own default views, cropped; the crop boxes below are fixed so a re-render lines up
with the picture it replaces.
"""
import argparse, functools, http.server, os, shutil, socket, subprocess, sys, threading, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIEWER = os.path.join(ROOT, 'viewer')
BOARDS = [   # (board file, asset prefix, pcb3d kind)
    ('daughterboard/miata_ecu_daughter.kicad_pcb', '', 'daughter'),
    ('motherboards/1989-95/miata_mb_8995.kicad_pcb', 'mb8995_', 'mb:mb_na6'),
    ('motherboards/1996-97/miata_mb_9697.kicad_pcb', 'mb9697_', 'mb:mb_na96'),
    ('motherboards/1999-2000/miata_mb_9900.kicad_pcb', 'mb9900_', 'mb:mb_nb1'),
    ('motherboards/2001-05/miata_mb_0105.kicad_pcb', 'mb0105_', 'mb:mb_nb2'),
]
# README pictures: canvas screenshots at a 2000 x 1150 window, cropped to (x, y, w, h)
README = {'daughterboard': (104, 246, 1354, 794), 'assembly_1989-95': (227, 237, 1221, 878), 'assembly_lifted': (227, 173, 1221, 943)}
# shop products (one per range of years) and the viewer board each one shows
SHOP = {'8993': '8995', '9495': '8995', '9697': '9697', '9900': '9900', '0105': '0105'}
HIDE = '.views,.status,.scale,.tip{display:none!important}'


def build(assets):
    os.makedirs(assets, exist_ok=True)
    env = dict(os.environ, MASK='black', FINISH='enig', OUTDIR=assets)
    for board, pre, kind in BOARDS:
        print('assets:', board, flush=True)
        subprocess.run([sys.executable, os.path.join(VIEWER, 'pcb3d.py'), os.path.join(ROOT, board), pre, kind],
                       env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def serve(directory):
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Quiet, directory=directory))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--three', required=True); ap.add_argument('--assets', required=True)
    ap.add_argument('--build', action='store_true'); ap.add_argument('--no-readme', action='store_true')
    ap.add_argument('--no-shop', action='store_true')
    ap.add_argument('--settle', type=float, default=8.0, help='seconds to let the renderer finish each view')
    a = ap.parse_args()
    from PIL import Image
    from playwright.sync_api import sync_playwright
    if a.build:
        build(a.assets)
    shutil.copyfile(os.path.join(VIEWER, 'index.html'), os.path.join(a.assets, 'index.html'))
    raw = os.path.join(a.assets, 'shots'); os.makedirs(raw, exist_ok=True)
    three = os.path.abspath(a.three)
    srv, port = serve(a.assets)

    def cdn(route):
        f = os.path.join(three, route.request.url.split('three@0.160.0/')[1])
        route.fulfill(path=f, content_type='application/javascript') if os.path.exists(f) else route.abort()

    def loaded(pg, settle):
        pg.wait_for_function("document.getElementById('loading').hidden", timeout=900000); time.sleep(settle)

    def click(pg, sel):
        pg.eval_on_selector(sel, 'b => b.click()')

    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        if not a.no_readme:
            pg = b.new_page(viewport={'width': 2000, 'height': 1150}, device_scale_factor=1)
            pg.route('https://cdn.jsdelivr.net/**', cdn)
            pg.goto(f'http://127.0.0.1:{port}/index.html'); loaded(pg, 2)
            pg.add_style_tag(content=HIDE); time.sleep(a.settle)
            pg.locator('#c').screenshot(path=f'{raw}/readme_daughterboard.png', timeout=300000)
            click(pg, '#m-a'); loaded(pg, a.settle)
            pg.locator('#c').screenshot(path=f'{raw}/readme_assembly_1989-95.png', timeout=300000)
            click(pg, '#t-lift'); time.sleep(a.settle)
            pg.locator('#c').screenshot(path=f'{raw}/readme_assembly_lifted.png', timeout=300000)
            pg.close()
            for name, (x, y, w, h) in README.items():
                im = Image.open(f'{raw}/readme_{name}.png').convert('RGB').crop((x, y, x + w, y + h))
                im.save(os.path.join(ROOT, 'images', name + '.jpg'), quality=88, optimize=True, progressive=True)
                print('wrote images/' + name + '.jpg')
        if not a.no_shop:
            pg = b.new_page(viewport={'width': 2200, 'height': 1400}, device_scale_factor=1)
            pg.route('https://cdn.jsdelivr.net/**', cdn)
            pg.goto(f'http://127.0.0.1:{port}/index.html'); loaded(pg, 2)
            pg.add_style_tag(content=HIDE + '.stage{background:#fff!important;border-radius:0!important}'); time.sleep(a.settle)

            def shot(name):
                pg.screenshot(path=f'{raw}/{name}.png', clip=pg.locator('#c').bounding_box(), timeout=300000)
            shot('daughterboard')
            click(pg, '#m-a'); loaded(pg, a.settle)
            first = True
            for key in dict.fromkeys(SHOP.values()):
                if not first:
                    click(pg, f'#years [data-y="{key}"]'); loaded(pg, a.settle)
                shot('assembly_' + key)
                if first:
                    click(pg, '#t-lift'); time.sleep(a.settle); shot('assembly_lifted')
                    click(pg, '#t-lift'); time.sleep(a.settle)
                first = False
            pg.close()
        b.close()
    srv.shutdown()
    if not a.no_shop:
        web = os.path.join(ROOT, 'website')
        pairs = [f'render-assembly-{prod}=assembly_{key}.png' for prod, key in SHOP.items()]
        pairs += ['render-assembly-lifted=assembly_lifted.png', 'render-daughterboard=daughterboard.png']
        subprocess.run([sys.executable, os.path.join(web, 'preview', 'prep_images.py'), raw, os.path.join(web, 'theme', 'assets')] + pairs, check=True)
        for prod in SHOP:
            shutil.copyfile(f'{web}/theme/assets/render-assembly-{prod}-2000.jpg', f'{web}/product-images/ecu-{prod}.jpg')
        shutil.copyfile(f'{web}/theme/assets/render-assembly-lifted-2000.jpg', f'{web}/product-images/exploded.jpg')
        shutil.copyfile(f'{web}/theme/assets/render-daughterboard-2000.jpg', f'{web}/product-images/daughterboard.jpg')
        z = os.path.join(web, 'mono-theme.zip')
        if os.path.exists(z):
            os.remove(z)
        subprocess.run(['zip', '-qr', z, '.'], cwd=os.path.join(web, 'theme'), check=True)
        print('wrote the shop photos and website/mono-theme.zip')


if __name__ == '__main__':
    main()
