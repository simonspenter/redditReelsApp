from PIL import Image

# Patch for Pillow>=10 compatibility with MoviePy
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS
