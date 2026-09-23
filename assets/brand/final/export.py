"""Export only the approved SVG to PNG/ICO. No alternative designs are generated.

/usr/bin/python3 assets/brand/final/export.py [--output /path/to/output]
"""
import argparse
from pathlib import Path

import gi
gi.require_version('Rsvg', '2.0')
from gi.repository import Rsvg
from PIL import Image

ROOT = Path(__file__).resolve().parent
SIZES = (16, 24, 32, 48, 64, 128, 256, 512, 1024, 2048)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT)
    args = parser.parse_args()
    source = (ROOT / 'catcommstudio.svg').read_bytes()
    pixbuf = Rsvg.Handle.new_from_data(source).get_pixbuf()
    mode = 'RGBA' if pixbuf.get_has_alpha() else 'RGB'
    master = Image.frombytes(mode, (pixbuf.get_width(), pixbuf.get_height()),
                             pixbuf.get_pixels(), 'raw', mode, pixbuf.get_rowstride()).convert('RGBA')
    assert master.size == (2048, 2048)
    output = args.output.resolve()
    (output / 'png').mkdir(parents=True, exist_ok=True)
    images = []
    for size in SIZES:
        icon = master.resize((size, size), Image.Resampling.LANCZOS)
        if size == 16:
            # Keep the approved correction for faint alpha ringing at tiny corners.
            icon.putalpha(icon.getchannel('A').point(lambda a: 0 if a < 3 else a))
        icon.save(output / 'png' / f'catcommstudio-{size}.png')
        images.append(icon)
    master.save(output / 'catcommstudio.ico', sizes=[(s, s) for s in SIZES if s <= 256],
                append_images=images)
    print(f'Exported {len(SIZES)} approved PNG sizes and one ICO to {output}')


if __name__ == '__main__':
    main()
