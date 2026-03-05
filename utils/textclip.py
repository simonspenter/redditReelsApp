# utils/textclip.py

import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip


# Repo root: utils/textclip.py -> utils -> repo root
ROOT = Path(__file__).resolve().parents[1]
FONT_REG = ROOT / "assets" / "fonts" / "DejaVuSans.ttf"
FONT_BOLD = ROOT / "assets" / "fonts" / "DejaVuSans-Bold.ttf"


def _load_font(font_path: Path, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(str(font_path), size)
    except Exception as e:
        print(f"⚠️ Subtitle font load failed for {font_path}: {e} (falling back to default)")
        return ImageFont.load_default()


def make_textclip_pillow(
    txt: str,
    fontsize: int = 60,
    bold: bool = True,
    color: str = "white",
    stroke_color: str = "black",
    stroke_width: int = 6,
    shadow_color: str = "black",
    shadow_offset: tuple[int, int] | None = (5, 5),
    size: tuple[int, int] = (1080, 1920),
):
    """
    Create styled text clip with shadow + stroke for subtitles.
    Uses bundled fonts from assets/fonts to be consistent on Windows + GitHub Actions.
    """
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_path = FONT_BOLD if bold else FONT_REG
    font = _load_font(font_path, fontsize)

    # Measure
    bbox = draw.textbbox((0, 0), txt, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size[0] - w) // 2
    y = int(size[1] * 0.25)  # 1/4 from top (your original choice)

    # Shadow
    if shadow_offset:
        sx, sy = shadow_offset
        draw.text((x + sx, y + sy), txt, font=font, fill=shadow_color)

    # Stroke (outline)
    if stroke_width > 0:
        # simple square stroke
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx == 0 and dy == 0:
                    continue
                draw.text((x + dx, y + dy), txt, font=font, fill=stroke_color)

    # Main text
    draw.text((x, y), txt, font=font, fill=color)

    return ImageClip(np.array(img)).set_duration(0.1)