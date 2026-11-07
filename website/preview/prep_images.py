"""Fit the viewer's white-background renders into the theme's 2000 x 1300 frames (content centred, 6 % margin) and
write <name>-2000.jpg and -1200.jpg into the theme's assets.
usage: prep_images.py <shots dir> <theme assets dir> [name=file.png ...]"""
import sys
from PIL import Image, ImageChops
shots, out = sys.argv[1], sys.argv[2]
pairs = [a.split('=') for a in sys.argv[3:]]
W, H, M = 2000, 1300, 0.06
for name, f in pairs:
    im = Image.open(f'{shots}/{f}').convert('RGB')
    diff = ImageChops.difference(im, Image.new('RGB', im.size, 'white')).convert('L').point(lambda v: 255 if v > 10 else 0)
    box = diff.getbbox()
    im = im.crop(box)
    s = min(W * (1 - 2 * M) / im.width, H * (1 - 2 * M) / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    c = Image.new('RGB', (W, H), 'white'); c.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    c.save(f'{out}/{name}-2000.jpg', quality=84, optimize=True, progressive=True)
    c.resize((1200, 780), Image.LANCZOS).save(f'{out}/{name}-1200.jpg', quality=84, optimize=True, progressive=True)
    print(name, box)
