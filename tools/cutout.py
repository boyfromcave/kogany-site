"""Cut the gold flower out of a JPEG whose 'transparency' is a baked-in grey/white checkerboard.

Gold pixels are saturated; the checkerboard is neutral. Mask = saturation above a threshold,
holes inside the object filled (flood fill from the border marks what is background), then
feathered. Writes RGBA PNGs at several sizes, cropped to the object."""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops

src, outdir = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
h, s, v = im.convert("HSV").split()
# saturated = object; neutral checkerboard (grey/white) has very low saturation
mask = s.point(lambda x: 255 if x > 38 else 0)
mask = mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
# keep only what is not reachable from the border through background: fill holes
bg = mask.copy()
ImageDraw.floodfill(bg, (0, 0), 128)
filled = bg.point(lambda x: 0 if x == 128 else 255)
# remove small specks (the faint artifacts at the right): erode then dilate
filled = filled.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))
# keep the largest connected blob: flood from the centre
blob = Image.new("L", filled.size, 0)
cx, cy = filled.size[0] // 2, filled.size[1] // 2
tmp = filled.copy()
ImageDraw.floodfill(tmp, (cx, cy), 77)
blob = tmp.point(lambda x: 255 if x == 77 else 0)
alpha = blob.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0))
rgba = im.copy()
rgba.putalpha(alpha)
box = blob.getbbox()
pad = 6
box = (max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, im.width), min(box[3] + pad, im.height))
rgba = rgba.crop(box)
side = max(rgba.size)
sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
sq.paste(rgba, ((side - rgba.width) // 2, (side - rgba.height) // 2))
for size in (640, 160):
    sq.resize((size, size), Image.LANCZOS).save(f"{outdir}/kogany-flower-{size}.webp", quality=88, method=6)
# favicon and touch icon: on the dark ground so the gold reads at tiny sizes
for size, name in [(180, "apple-touch-icon.png"), (48, "favicon-48.png")]:
    ground = Image.new("RGBA", (size, size), (20, 19, 23, 255))
    f = sq.resize((int(size * .9), int(size * .9)), Image.LANCZOS)
    ground.alpha_composite(f, ((size - f.width) // 2, (size - f.height) // 2))
    ground.save(f"{outdir}/{name}", optimize=True)
print("bbox", box, "side", side)
