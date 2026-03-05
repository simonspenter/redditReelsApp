import os
import random
from PIL import Image, ImageDraw, ImageFont

def generate_thumbnail_from_template(template_path, caption, output_dir):
    """
    Generates a Reddit-style thumbnail image and saves it to output_dir.
    Returns: path to thumbnail file.
    """
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    W, H = img.size

    # Fonts
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 56)
        small_font = ImageFont.truetype("arial.ttf", 46)
        text_font = ImageFont.truetype("arialbd.ttf", 70)
        number_font = ImageFont.truetype("arial.ttf", 68)
    except IOError:
        title_font = text_font = small_font = number_font = ImageFont.load_default()

    # Random subreddit + username
    subreddit = random.choice(["r/relationships", "r/AmItheAsshole", "r/TrueOffMyChest"])
    username = f"u/throwaway{random.randint(1000,9999)} · 3d"

    # Teaser (no hashtags)
    teaser = caption.split("\n")[0].replace("Part 1.", "").strip()

    # Subreddit + username
    draw.text((420, 130), subreddit, font=title_font, fill="black")
    draw.text((420, 210), username, font=small_font, fill="gray")

    # Wrap teaser if needed
    def wrap_text(text, font, max_width):
        words = text.split()
        lines, line = [], ""
        for w in words:
            test_line = f"{line} {w}".strip()
            if draw.textlength(test_line, font=font) <= max_width:
                line = test_line
            else:
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
    thumb_path = os.path.join(output_dir, "thumbnail.jpg")
    img.convert("RGB").save(thumb_path, "JPEG")
    print(f"🖼️ Thumbnail saved: {thumb_path}")

    return thumb_path
