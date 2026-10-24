"""Side-by-side crop of a Blender and a Godot shot (tools/gdx_compare.py's shots) at 1:1 or enlarged, for inspection.
  py tools/gdx_crop.py <shots dir> <camera png name without prefix> x0 y0 x1 y1 <out png> [scale] [shadows]"""
import sys, os
from PIL import Image
sh, cam, x0, y0, x1, y1, out = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:7]), sys.argv[7]
k = float(sys.argv[8]) if len(sys.argv) > 8 else 1.0
tag = "_shadows" if len(sys.argv) > 9 and sys.argv[9] == "shadows" else ""
ims = [Image.open(os.path.join(sh, f"{p}{tag}_{cam}.png")).convert("RGB").crop((x0, y0, x1, y1)) for p in ("blender", "godot")]
w, h = ims[0].size
sheet = Image.new("RGB", (w * 2 + 8, h), (255, 0, 255))
sheet.paste(ims[0], (0, 0)); sheet.paste(ims[1], (w + 8, 0))
if k != 1.0: sheet = sheet.resize((int(sheet.width * k), int(sheet.height * k)), Image.NEAREST)
sheet.save(out)
