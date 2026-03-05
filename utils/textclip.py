import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip

def make_textclip_pillow(txt, fontsize=60, font="arialbd.ttf",
                         color="white", stroke_color="black", stroke_width=6,
                         shadow_color="black", shadow_offset=(5, 5),
                         size=(1080, 1920)):
    """
    Create styled text clip with shadow + stroke for subtitles.
    """
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(font, fontsize)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), txt, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size[0] - w) // 2
    y = int(size[1] * 0.25)  # 1/4 from top

    # Shadow
    if shadow_offset:
        sx, sy = shadow_offset
        draw.text((x+sx, y+sy), txt, font=font, fill=shadow_color)

    # Stroke
    if stroke_width > 0:
        for dx in range(-stroke_width, stroke_width+1):
            for dy in range(-stroke_width, stroke_width+1):
                if dx != 0 or dy != 0:
                    draw.text((x+dx, y+dy), txt, font=font, fill=stroke_color)

    # Main text
    draw.text((x, y), txt, font=font, fill=color)

    return ImageClip(np.array(img)).set_duration(0.1)
