"""Generate the CatCommStudio process/protocol logo family from the approved base.

Run: /usr/bin/python3 assets/brand/extensions/generate.py
The base logo remains untouched. Glyphs are editable SVG paths.
"""
import hashlib
import json
import re
from pathlib import Path

import cairo
import gi
gi.require_version('Rsvg', '2.0')
from gi.repository import Rsvg
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'final'
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
SIZES = (16, 24, 32, 48, 64, 128, 256, 512, 1024, 2048)
PALETTE = json.loads((BASE / 'palette.json').read_text())
COLORS = PALETTE['future_badges']['colors']
INK = COLORS['glyph']
CATALOG = [
    ('launcher', 'Launcher', '主进程 · 进程管理', '叠放窗口与运行控制'),
    ('ble', 'BLE', '子程序 · 低功耗蓝牙', '蓝牙符号'),
    ('usb', 'USB', '子程序 · USB 通信', 'USB 分支符号'),
    ('hid', 'HID', '子程序 · 人机接口设备', '键盘轮廓'),
    ('tcp', 'TCP', '子程序 · TCP 通信', 'TCP 协议缩写'),
    ('udp', 'UDP', '子程序 · UDP 通信', 'UDP 协议缩写'),
    ('websocket', 'WebSocket', '子程序 · WebSocket 通信', 'WS 协议缩写'),
    ('serial-port', 'Serial Port', '子程序 · 串口通信', '串口接口轮廓'),
    ('mqtt', 'MQTT', '子程序 · 发布与订阅', '消息节点与分发连接'),
    ('can', 'CAN', '子程序 · CAN 通信', 'CAN 协议缩写'),
]


def text_path(word):
    """Outline short labels so the exported SVG needs no installed fonts."""
    context = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1))
    context.select_font_face('DejaVu Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    context.set_font_size(80)
    xb, yb, width, height, _, _ = context.text_extents(word)
    scale = min(96 / width, 62 / height)
    context.translate(50 - (xb + width / 2) * scale, 50 - (yb + height / 2) * scale)
    context.scale(scale, scale)
    context.move_to(0, 0)
    context.text_path(word)
    # Cairo copy_path yields coordinates in the current user space.
    # The saved transform places the font's path inside a 100-square glyph.
    commands = []
    for kind, points in context.copy_path():
        commands.append(('M', 'L', 'C', 'Z')[kind] + ' '.join(f'{p:.4f}' for p in points))
    tx = 50 - (xb + width / 2) * scale
    ty = 50 - (yb + height / 2) * scale
    return f'<path transform="translate({tx:.4f} {ty:.4f}) scale({scale:.6f})" d="{" ".join(commands)}" fill="currentColor"/>'


def glyphs():
    stroke = 'fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"'
    return {
        'launcher': f'''<path d="M72 17V10H10V67H17" {stroke}/>
<rect x="25" y="29" width="64" height="58" rx="7" {stroke}/>
<path d="M28 46H86" fill="none" stroke="currentColor" stroke-width="7"/>
<path d="M46 55L66 65L46 77Z" fill="currentColor"/>''',
        'ble': f'<path d="M27 27L74 72L49 91V9L74 28L27 73" {stroke}/>',
        'usb': f'''<path d="M50 80V20M50 65L26 51V37M50 56L75 42V27" {stroke}/>
<path d="M50 4L38 23H62Z" fill="currentColor"/>
<circle cx="50" cy="86" r="10" fill="currentColor"/>
<circle cx="26" cy="32" r="9" fill="currentColor"/>
<rect x="67" y="11" width="17" height="17" rx="1" fill="currentColor"/>''',
        'hid': f'''<rect x="7" y="23" width="86" height="58" rx="9" {stroke}/>
<path d="M23 39H27M42 39H46M61 39H65M79 39H80M23 55H27M42 55H46M61 55H65M79 55H80M32 69H69" fill="none" stroke="currentColor" stroke-width="7" stroke-linecap="round"/>''',
        'tcp': text_path('TCP'),
        'udp': text_path('UDP'),
        'websocket': text_path('WS'),
        'can': text_path('CAN'),
        'serial-port': f'''<path d="M17 23H83Q94 23 91 35L82 74Q80 81 72 81H28Q20 81 18 74L9 35Q6 23 17 23Z" {stroke}/>
<g fill="currentColor"><circle cx="29" cy="43" r="5"/><circle cx="50" cy="43" r="5"/><circle cx="71" cy="43" r="5"/><circle cx="39" cy="64" r="5"/><circle cx="61" cy="64" r="5"/></g>''',
        'mqtt': f'''<path d="M50 50L23 21M50 50L80 26M50 50V83" {stroke}/>
<circle cx="50" cy="50" r="13" fill="currentColor"/>
<circle cx="19" cy="17" r="10" fill="currentColor"/>
<circle cx="84" cy="23" r="10" fill="currentColor"/>
<circle cx="50" cy="87" r="10" fill="currentColor"/>''',
    }


def raster(source, size):
    source = re.sub(r'width="[0-9.]+" height="[0-9.]+"', f'width="{size}" height="{size}"', source, count=1)
    pixbuf = Rsvg.Handle.new_from_data(source.encode()).get_pixbuf()
    mode = 'RGBA' if pixbuf.get_has_alpha() else 'RGB'
    return Image.frombytes(mode, (pixbuf.get_width(), pixbuf.get_height()),
                           pixbuf.get_pixels(), 'raw', mode, pixbuf.get_rowstride()).convert('RGBA')


def badge(glyph):
    return f'''<g id="replaceable-badge" color="{INK}">
<circle id="badge-rim" cx="425" cy="425" r="67" fill="{COLORS['rim']}"/>
<circle id="badge-face" cx="425" cy="425" r="61" fill="url(#badge-gold)"/>
<g id="badge-glyph" transform="translate(381 381) scale(.88)">{glyph}</g></g>'''


def compact(glyph):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="2048" viewBox="0 0 160 160">
<defs><linearGradient id="badge-gold" x1="0" y1="0" x2=".7" y2="1"><stop stop-color="{COLORS['top']}"/><stop offset="1" stop-color="{COLORS['bottom']}"/></linearGradient></defs>
<circle cx="80" cy="80" r="76" fill="{COLORS['rim']}"/>
<circle cx="80" cy="80" r="69" fill="url(#badge-gold)"/>
<g id="badge-glyph" transform="translate(30 30)" color="{INK}">{glyph}</g></svg>'''


def label(draw, point, word, size=24, fill='#26384B'):
    draw.text(point, word, font=ImageFont.truetype(FONT, size), fill=fill)


def centered(draw, y, word, center, size=24, fill='#26384B'):
    font = ImageFont.truetype(FONT, size)
    bounds = draw.textbbox((0, 0), word, font=font)
    draw.text((center - (bounds[2] - bounds[0]) / 2, y), word, font=font, fill=fill)


def main():
    base_source = (BASE / 'catcommstudio.svg').read_text()
    base_hash = hashlib.sha256((BASE / 'catcommstudio.svg').read_bytes()).hexdigest()
    symbols = glyphs()
    (ROOT / 'glyphs').mkdir(exist_ok=True)
    entries = []
    for key, title, role, meaning in CATALOG:
        destination = ROOT / key
        (destination / 'png').mkdir(parents=True, exist_ok=True)
        glyph = symbols[key]
        (ROOT / 'glyphs' / f'{key}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100" color="{INK}">{glyph}</svg>')
        source = base_source.replace('</svg>', badge(glyph) + '</svg>')
        small_source = compact(glyph)
        (destination / f'catcommstudio-{key}.svg').write_text(source)
        (destination / f'catcommstudio-{key}-compact.svg').write_text(small_source)
        master = raster(source, 2048)
        small = raster(small_source, 2048)
        exported = []
        for size in SIZES:
            icon = (small if size <= 32 else master).resize((size, size), Image.Resampling.LANCZOS)
            if size == 16:
                icon.putalpha(icon.getchannel('A').point(lambda a: 0 if a < 3 else a))
            icon.save(destination / 'png' / f'catcommstudio-{key}-{size}.png')
            exported.append(icon)
        master.save(destination / f'catcommstudio-{key}.ico',
                    sizes=[(s, s) for s in SIZES if s <= 256], append_images=exported)
        entries.append({'id':key,'name':title,'role':role,'glyph_meaning':meaning,
                        'svg':f'{key}/catcommstudio-{key}.svg',
                        'ico':f'{key}/catcommstudio-{key}.ico',
                        'compact_svg':f'{key}/catcommstudio-{key}-compact.svg',
                        'png':f'{key}/png/catcommstudio-{key}-{{size}}.png'})

    overview_columns = 5
    overview_rows = (len(CATALOG) + overview_columns - 1) // overview_columns
    overview = Image.new('RGBA', (1740, 136 + overview_rows * 392 + 24), '#F5F4F0')
    draw = ImageDraw.Draw(overview)
    label(draw, (48, 26), 'CatCommStudio · 进程与通信图标', 34)
    label(draw, (48, 84), f'暖沙底座与统一猫头 · Launcher + {len(CATALOG)-1} 个通信子程序 · 暖金功能角标', 20, '#717B85')
    for i, (key, title, role, meaning) in enumerate(CATALOG):
        x, y = 30 + i % overview_columns * 338, 136 + i // overview_columns * 392
        draw.rounded_rectangle((x, y, x + 318, y + 372), radius=24,
                               fill='#EFE7D5' if key == 'launcher' else '#FFFFFF')
        icon = Image.open(ROOT / key / 'png' / f'catcommstudio-{key}-512.png').convert('RGBA')
        overview.alpha_composite(icon.resize((246, 246), Image.Resampling.LANCZOS), (x + 36, y + 14))
        centered(draw, y + 270, title, x + 159, 26)
        centered(draw, y + 318, role, x + 159, 17, '#717B85')
    overview.convert('RGB').save(ROOT / 'overview.png')

    badges = Image.new('RGBA', (1400, 120 + overview_rows * 320 + 24), '#F5F4F0')
    draw = ImageDraw.Draw(badges)
    label(draw, (40, 24), '独立功能符号', 30)
    label(draw, (40, 72), '16–32 px 使用此简化形式，优先保证各程序可区分', 18, '#717B85')
    for i, (key, title, _, _) in enumerate(CATALOG):
        x, y = i % overview_columns * 280, 120 + i // overview_columns * 320
        source = (ROOT / key / f'catcommstudio-{key}-compact.svg').read_text()
        badges.alpha_composite(raster(source, 200), (x + 40, y + 10))
        centered(draw, y + 232, title, x + 140, 26)
    badges.convert('RGB').save(ROOT / 'badge-sheet.png')

    review = Image.new('RGBA', (1120, 112 + len(CATALOG) * 134 + 40), '#202731')
    draw = ImageDraw.Draw(review)
    label(draw, (36, 20), '实际尺寸检查 · 16–32 px 为简化图标', 27, '#F5F4F0')
    columns = ((262, 128), (455, 64), (595, 48), (725, 32), (846, 24), (957, 16))
    for x, size in columns:
        label(draw, (x, 74), f'{size}px', 18, '#C2CAD3')
    for i, (key, title, _, _) in enumerate(CATALOG):
        y = 112 + i * 134
        label(draw, (36, y + 40), title, 22, '#F5F4F0')
        for x, size in columns:
            image = Image.open(ROOT / key / 'png' / f'catcommstudio-{key}-{size}.png').convert('RGBA')
            review.alpha_composite(image, (x, y + (110 - size) // 2))
    review.convert('RGB').save(ROOT / 'size-review.png')

    manifest = {'status':'approved','approved_on':'2026-09-23','approved_base_sha256':base_hash,
                'approved_base':'../final/catcommstudio.svg','small_sizes':[16,24,32],
                'full_sizes':[48,64,128,256,512,1024,2048],
                'theme':PALETTE['theme'],
                'mqtt_name_confirmed':True,'modules':entries}
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    assert hashlib.sha256((BASE / 'catcommstudio.svg').read_bytes()).hexdigest() == base_hash
    for entry in entries:
        key = entry['id']
        for size in SIZES:
            with Image.open(ROOT / key / 'png' / f'catcommstudio-{key}-{size}.png') as icon:
                assert icon.size == (size, size) and icon.mode == 'RGBA'
                assert icon.getpixel((0,0))[3] == 0
        with Image.open(ROOT / key / f'catcommstudio-{key}.ico') as ico:
            assert ico.ico.sizes() == {(s,s) for s in SIZES if s <= 256}
            for size in (16,24,32,48,64,128,256):
                png = Image.open(ROOT / key / 'png' / f'catcommstudio-{key}-{size}.png').convert('RGBA')
                diff = ImageChops.difference(png, ico.ico.getimage((size,size)).convert('RGBA'))
                assert all(lo == hi == 0 for lo,hi in diff.getextrema()), (key, size)
    print(f'Generated {len(entries)} module logos, {len(entries)*len(SIZES)} PNGs, {len(entries)} ICOs, full/compact SVGs and review sheets; size and ICO checks passed.')


if __name__ == '__main__':
    main()
