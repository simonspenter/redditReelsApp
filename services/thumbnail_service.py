# services/thumbnail_service.py

import os
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def _repo_root() -> Path:
    # services/thumbnail_service.py -> services -> repo root
    return Path(__file__).resolve().parents[1]


def _load_font(font_path: Path, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(str(font_path), size)
    except Exception as e:
        print(f"⚠️ Could not load font '{font_path}'. Falling back to default. ({e})")
        return ImageFont.load_default()


def generate_thumbnail_from_template(template_path: str, caption: str, output_dir: str) -> str:
    """
    Generates a Reddit-style thumbnail image and saves it to output_dir.
    Uses bundled fonts from assets/fonts to ensure it works on GitHub Actions (Linux).
    Returns: path to thumbnail file (JPEG).
    """
    root = _repo_root()

    # Expecting fonts here:
    # assets/fonts/DejaVuSans.ttf
    # assets/fonts/DejaVuSans-Bold.ttf
    font_dir = root / "assets" / "fonts"
    font_regular = font_dir / "DejaVuSans.ttf"
    font_bold = font_dir / "DejaVuSans-Bold.ttf"

    # Load template (path is relative to repo root in your app.py: "assets/reddit-thumbnail-template.png")
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    W, H = img.size

    # Fonts (tuned to your previous sizes)
    title_font = _load_font(font_bold, 56)
    small_font = _load_font(font_regular, 46)
    text_font = _load_font(font_bold, 70)
    number_font = _load_font(font_regular, 68)

    # Random subreddit + username
    subreddit = random.choice(["r/relationships", "r/AmItheAsshole", "r/TrueOffMyChest"])
    username = f"u/throwaway{random.randint(1000, 9999)} · 3d"

    # Teaser (first line, no hashtags)
    teaser = (caption or "").split("\n")[0].replace("Part 1.", "").strip()
    if not teaser:
        teaser = "A Reddit story you won’t believe…"

    # Draw subreddit + username (positions assumed to match your template)
    draw.text((420, 130), subreddit, font=title_font, fill="black")
    draw.text((420, 210), username, font=small_font, fill="gray")

    # Helper: wrap text to max width
    def wrap_text(text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
        words = text.split()
        lines: list[str] = []
        line = ""
        for w in words:
            test_line = f"{line} {w}".strip()
            # textlength exists on newer Pillow; fallback handled below
            try:
                fits = draw.textlength(test_line, font=font) <= max_width
            except Exception:
                # fallback using textbbox
                bbox = draw.textbbox((0, 0), test_line, font=font)
                fits = (bbox[2] - bbox[0]) <= max_width

            if fits:
                line = test_line
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
        return lines

    teaser_lines = wrap_text(teaser, text_font, W - 400)

    # Teaser placement
    y_offset = 380
    for line in teaser_lines:
        draw.text((180, y_offset), line, font=text_font, fill="black")
        y_offset += 100

    # Fake upvotes + comments
    upvotes = str(random.randint(2000, 15000))
    comments = str(random.randint(2000, 12000))
    draw.text((240, H - 190), upvotes, font=number_font, fill="black")
    draw.text((800, H - 190), comments, font=number_font, fill="black")

    # Save thumbnail
    os.makedirs(output_dir, exist_ok=True)
    thumb_path = os.path.join(output_dir, "thumbnail.jpg")
    img.convert("RGB").save(thumb_path, "JPEG", quality=95)
    print(f"🖼️ Thumbnail saved: {thumb_path}")

    return thumb_path