# Compares cull_render_check.py's pairs: for every piece and view, the share of the piece's pixels that change when
# backface culling goes on (a back face seen from outside vanished, or a z-fight resolved). Writes <dir>/diff.csv
# (piece, worst view, changed pixels, share) and a contact sheet of the worst pieces (culling off above, on below).
# Runs in Blender's Python (numpy, image IO):
#   blender -b --factory-startup --python cull_render_diff.py -- <dir> [count for the sheet]
import os, sys, glob, csv
import numpy as np
import bpy

args = sys.argv[sys.argv.index("--") + 1:]
d = args[0]
N = int(args[1]) if len(args) > 1 else 48
BG = np.array([90, 90, 100], np.float32) / 255.0
S = 128


def load(p):
    im = bpy.data.images.load(p)
    a = np.array(im.pixels[:], np.float32).reshape(im.size[1], im.size[0], 4)
    bpy.data.images.remove(im)
    al = a[..., 3:4]
    return a[..., :3] * al + BG * (1 - al), a[..., 3] > 0.03


rows = []
for off in glob.glob(os.path.join(d, "off_*.png")):
    on = os.path.join(d, "on_" + os.path.basename(off)[4:])
    if not os.path.exists(on): continue
    name = os.path.basename(off)[4:-4]
    piece, view = name.rsplit("_", 1)
    a, ma = load(off); b, mb = load(on)
    changed = (np.abs(a - b).max(axis=2) > 40 / 255.0) & (ma | mb)
    cover = max(int(ma.sum()), 1)
    rows.append((piece, int(view), int(changed.sum()), float(changed.sum()) / cover))

best = {}
for piece, view, n, share in rows:
    if piece not in best or share > best[piece][2]:
        best[piece] = (view, n, share)
order = sorted(best.items(), key=lambda kv: -kv[1][2])
with open(os.path.join(d, "diff.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f); w.writerow(["piece", "view", "changed_px", "share"])
    for piece, (view, n, share) in order: w.writerow([piece, view, n, f"{share:.4f}"])
flag = [kv for kv in order if kv[1][2] >= 0.01]
print(f"{len(best)} pieces; {len(flag)} change on >= 1% of their pixels, {sum(1 for kv in order if kv[1][2] >= 0.05)} on >= 5%", flush=True)

# contact sheet: 8 per row, culling off above on, labels in diff.csv order (the sheet has no text)
cols, n = 8, min(N, len(flag))
rows_ = (n + cols - 1) // cols
W, H = cols * (S + 2), max(rows_, 1) * (2 * S + 6)
sheet = np.zeros((H, W, 4), np.float32); sheet[..., 3] = 1; sheet[..., :3] = 0.16
for i, (piece, (view, cnt, share)) in enumerate(flag[:n]):
    x, y = (i % cols) * (S + 2), (i // cols) * (2 * S + 6)
    for r, mode in enumerate(("off", "on")):
        im, _ = load(os.path.join(d, f"{mode}_{piece}_{view}.png"))
        yy = H - (y + (r + 1) * S + r * 2)          # Blender images run bottom-up
        sheet[yy:yy + S, x:x + S, :3] = im
img = bpy.data.images.new("sheet", W, H, alpha=True)
img.pixels[:] = sheet.ravel()
img.filepath_raw = os.path.join(d, "worst.png"); img.file_format = "PNG"; img.save()
with open(os.path.join(d, "worst.txt"), "w", encoding="utf-8") as f:
    for i, (piece, (view, cnt, share)) in enumerate(flag[:n]):
        f.write(f"{i // cols},{i % cols},{piece},{share:.3f}\n")
