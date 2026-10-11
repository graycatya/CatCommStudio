"""Build the QCatUiKit logo proposal from the existing CatGray composition.

Run from the repository root: python assets/brand/qcat-uikit/generate.py
Requires Python 3.10+, Pillow and ImageMagick with SVG support on PATH.
"""

import hashlib
import io
import json
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / "final" / "catcommstudio.svg"
SIZES = (16, 24, 32, 48, 64, 128, 256, 512, 1024, 2048)
NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
COLORS = {
    "primary": "#1677FF",
    "background_top": "#64B5FF",
    "background_bottom": "#1545BA",
    "badge_top": "#FFFFFF",
    "badge_bottom": "#DBEAFF",
    "badge_rim": "#EDF5FF",
    "ink": "#18304D",
    "muted": "#64748B",
}
ET.register_namespace("", NS)
ET.register_namespace("xlink", XLINK_NS)


def svg_element(name, **attributes):
    return ET.Element(f"{{{NS}}}{name}", attributes)


def gradient(name, top, bottom):
    element = svg_element("linearGradient", id=name, x1="0", y1="0", x2="1", y2="1")
    element.append(svg_element("stop", **{"stop-color": top}))
    element.append(svg_element("stop", offset="1", **{"stop-color": bottom}))
    return element


def grid():
    element = svg_element("g", id="component-grid", fill=COLORS["primary"])
    for x, y in ((0, 0), (0, 36), (36, 36)):
        element.append(svg_element("rect", x=str(x), y=str(y), width="27", height="27", rx="5"))
    element.append(svg_element("rect", x="38", y="2", width="23", height="23", rx="4",
                               fill="none", stroke=COLORS["primary"], **{"stroke-width": "4"}))
    return element


def build_sources():
    source = ET.parse(BASE).getroot()
    # Older librsvg and Qt SVG renderers require the SVG 1.1 xlink form.
    for image in source.findall(f"{{{NS}}}image"):
        image.set(f"{{{XLINK_NS}}}href", image.attrib.pop("href"))
    title = svg_element("title", id="logo-title")
    title.text = "QCatUiKit"
    description = svg_element("desc", id="logo-description")
    description.text = "CatGray voxel cat on a blue rounded tile with a UI component grid badge."
    source.insert(0, title)
    source.insert(1, description)
    source.set("role", "img")
    source.set("aria-labelledby", "logo-title logo-description")
    definitions = source.find(f"{{{NS}}}defs")
    for child in list(definitions):
        definitions.remove(child)
    definitions.append(gradient("base-tone", COLORS["background_top"], COLORS["background_bottom"]))
    definitions.append(gradient("badge-tone", COLORS["badge_top"], COLORS["badge_bottom"]))
    badge = svg_element("g", id="ui-badge")
    badge.append(svg_element("rect", x="358", y="358", width="140", height="140", rx="36", fill=COLORS["badge_rim"]))
    badge.append(svg_element("rect", x="364", y="364", width="128", height="128", rx="30", fill="url(#badge-tone)"))
    symbol = grid()
    symbol.set("transform", "translate(389 389) scale(1.24)")
    badge.append(symbol)
    source.append(badge)
    ET.indent(source, space="  ")
    (ROOT / "qcat-uikit.svg").write_text(ET.tostring(source, encoding="unicode") + "\n", encoding="utf-8")

    return source


def raster(svg_path, size):
    executable = shutil.which("magick")
    if not executable:
        raise RuntimeError("ImageMagick 'magick' is required on PATH.")
    # Explicit dimensions give SVG rasterization the intended output resolution.
    with tempfile.TemporaryDirectory(prefix="qcat-logo-") as directory:
        tree = ET.parse(svg_path)
        tree.getroot().set("width", str(size))
        tree.getroot().set("height", str(size))
        temporary_svg = Path(directory) / "render.svg"
        tree.write(temporary_svg, encoding="utf-8", xml_declaration=True)
        result = subprocess.run([executable, "-background", "none", str(temporary_svg),
                                 "-depth", "8", "PNG32:-"], check=True, capture_output=True)
        return Image.open(io.BytesIO(result.stdout)).convert("RGBA")


def font(size, bold=False):
    candidates = [
        Path("C:/Windows/Fonts") / ("msyhbd.ttc" if bold else "msyh.ttc"),
        Path("C:/Windows/Fonts") / ("segoeuib.ttf" if bold else "segoeui.ttf"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    raise RuntimeError("Install Microsoft YaHei, Segoe UI or Noto Sans CJK for the overview.")


def label(draw, x, y, text, size=24, fill=None, bold=False):
    draw.text((x, y), text, font=font(size, bold), fill=fill or COLORS["ink"])


def previews(full):
    board = Image.new("RGBA", (1600, 1110), "#F4F7FC")
    draw = ImageDraw.Draw(board)
    label(draw, 64, 40, "QCatUiKit", 54, bold=True)
    label(draw, 66, 116, "Qt / QML 组件库 · Logo 设计提案", 23, COLORS["muted"])
    draw.rounded_rectangle((64, 180, 804, 812), radius=32, fill="#FFFFFF")
    draw.rounded_rectangle((836, 180, 1536, 478), radius=32, fill="#FFFFFF")
    draw.rounded_rectangle((836, 510, 1536, 812), radius=32, fill="#15243B")
    board.alpha_composite(full.resize((432, 432), Image.Resampling.LANCZOS), (218, 216))
    label(draw, 270, 690, "灰猫 × 组件网格", 32, bold=True)
    label(draw, 231, 748, "品牌辨识 + 界面构建", 22, COLORS["muted"])

    for y, ink, secondary in ((262, COLORS["ink"], COLORS["muted"]), (592, "#F7FAFF", "#A8BCD8")):
        board.alpha_composite(full.resize((142, 142), Image.Resampling.LANCZOS), (880, y))
        label(draw, 1050, y + 22, "QCatUiKit", 43, ink, True)
        label(draw, 1052, y + 91, "让界面，自然好用。", 22, secondary)

    label(draw, 64, 862, "默认主题蓝", 21, COLORS["muted"])
    draw.rounded_rectangle((64, 903, 108, 947), radius=10, fill=COLORS["primary"])
    label(draw, 124, 910, "#1677FF", 24, bold=True)
    label(draw, 360, 862, "统一图标 · 16–2048 px", 21, COLORS["muted"])
    board.alpha_composite(full.resize((92, 92), Image.Resampling.LANCZOS), (360, 896))
    label(draw, 478, 914, "所有尺寸使用完整灰猫与组件角标", 23)
    label(draw, 64, 1030, "保留 CatGray 原模型与表情；蓝色区分组件库，网格角标表达可组合的 UI 控件。", 23, COLORS["muted"])
    board.convert("RGB").save(ROOT / "overview.png")

    review = Image.new("RGBA", (1320, 610), "#F4F7FC")
    draw = ImageDraw.Draw(review)
    label(draw, 44, 26, "实际尺寸 / 浅色与深色背景", 30, bold=True)
    label(draw, 46, 79, "所有尺寸统一使用体素灰猫、蓝色底座与组件网格角标。", 20, COLORS["muted"])
    draw.rounded_rectangle((32, 330, 1288, 574), radius=24, fill="#15243B")
    for top, ink in ((150, COLORS["ink"]), (375, "#DDEAFF")):
        for x, size in ((70, 128), (284, 64), (476, 48), (672, 32), (856, 24), (1040, 16)):
            icon = Image.open(ROOT / "png" / f"qcat-uikit-{size}.png").convert("RGBA")
            review.alpha_composite(icon, (x, top + (128 - size) // 2))
            label(draw, x, top + 140, f"{size} px", 20, ink)
    review.convert("RGB").save(ROOT / "size-review.png")


def verify(source, original_hash):
    original = ET.parse(BASE).getroot()
    for image_id in ("head-shadow", "catgray-head"):
        original_image = original.find(f".//*[@id='{image_id}']")
        new_image = source.find(f".//*[@id='{image_id}']")
        normalized = dict(new_image.attrib)
        normalized["href"] = normalized.pop(f"{{{XLINK_NS}}}href")
        if normalized != original_image.attrib:
            raise RuntimeError(f"Existing {image_id} data or layout changed.")
    # Confirm that the embedded cat actually rendered, including in SVG 1.1 engines.
    with Image.open(ROOT / "png" / "qcat-uikit-512.png") as master:
        center = master.crop((180, 210, 330, 340)).convert("RGB")
        pixels = center.tobytes()
        gray_pixels = sum(max(pixels[i:i + 3]) - min(pixels[i:i + 3]) < 16
                          and 50 < pixels[i] < 230 for i in range(0, len(pixels), 3))
        if gray_pixels < center.width * center.height // 2:
            raise RuntimeError("The embedded gray cat did not render correctly.")
    for size in SIZES:
        with Image.open(ROOT / "png" / f"qcat-uikit-{size}.png") as icon:
            if icon.size != (size, size) or icon.mode != "RGBA":
                raise RuntimeError(f"Unexpected PNG dimensions/mode at {size}.")
            for corner in ((0, 0), (0, size - 1), (size - 1, 0), (size - 1, size - 1)):
                if icon.getpixel(corner)[3] != 0:
                    raise RuntimeError(f"Opaque PNG corner at {size}.")
    with Image.open(ROOT / "qcat-uikit.ico") as ico:
        expected = {(size, size) for size in SIZES if size <= 256}
        if ico.ico.sizes() != expected:
            raise RuntimeError("ICO size inventory differs from the PNG inventory.")
        for size in SIZES:
            if size <= 256:
                image = ico.ico.getimage((size, size)).convert("RGBA")
                png = Image.open(ROOT / "png" / f"qcat-uikit-{size}.png").convert("RGBA")
                if image.tobytes() != png.tobytes():
                    raise RuntimeError(f"ICO frame differs from PNG at {size}.")
    if hashlib.sha256(BASE.read_bytes()).hexdigest() != original_hash:
        raise RuntimeError("The approved base SVG changed.")


def main():
    original_hash = hashlib.sha256(BASE.read_bytes()).hexdigest()
    (ROOT / "png").mkdir(parents=True, exist_ok=True)
    source = build_sources()
    full = raster(ROOT / "qcat-uikit.svg", 2048)
    icons = []
    for size in SIZES:
        icon = full.resize((size, size), Image.Resampling.LANCZOS)
        # Remove faint resampling rings outside the rounded tile at every size.
        icon.putalpha(icon.getchannel("A").point(lambda alpha: 0 if alpha < 3 else alpha))
        for corner in ((0, 0), (0, size - 1), (size - 1, 0), (size - 1, size - 1)):
            icon.putpixel(corner, (0, 0, 0, 0))
        icon.save(ROOT / "png" / f"qcat-uikit-{size}.png")
        icons.append(icon)
    full.save(ROOT / "qcat-uikit.ico", sizes=[(s, s) for s in SIZES if s <= 256], append_images=icons)
    previews(full)
    manifest = {
        "name": "QCatUiKit",
        "status": "design-proposal",
        "created_on": "2026-10-11",
        "intended_project": "QCatUiKit",
        "palette": COLORS,
        "layout": {"viewBox": [0, 0, 512, 512], "badge": [358, 358, 140, 140], "badge_radius": 36},
        "source_base": "../final/catcommstudio.svg",
        "source_base_sha256": original_hash,
        "cat_model": "existing CatGray voxel render; geometry, expression, colors and placement preserved",
        "full_svg": "qcat-uikit.svg",
        "ico": "qcat-uikit.ico",
        "png": "png/qcat-uikit-{size}.png",
        "full_sizes": list(SIZES),
        "format": "SVG: embedded PNG cat/shadow + vector tile/badge; all sizes use the full composition",
    }
    (ROOT / "palette.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    verify(source, original_hash)
    print(f"Exported and verified {len(SIZES)} RGBA PNGs, 1 SVG, 7-frame ICO and 2 previews in {ROOT}")


if __name__ == "__main__":
    main()
