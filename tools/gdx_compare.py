"""Blender vs Godot renders of a GDX layout (src/export/gdx_export.py, Godot's kit/tools/capture.gd).

  py tools/gdx_compare.py <shots dir> [layout json]

For every blender[_shadows]_<camera>.png with a godot[_shadows]_<camera>.png beside it: the mean and 95th-percentile
absolute difference (0-255, all channels) and the mean luma of each, plus a sheet <shots>/compare/<tag>_<camera>.png
(Blender | Godot | difference x4). With the layout JSON, the calibration chart's patches (helpers of kind 'chart')
are read at their centres through each camera that sees them: emitted value -> Blender vs Godot pixel.
"""
import json, os, sys
import numpy as np
from PIL import Image


def load(p):
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.float32)


def project(cam, p, size):
    """Godot-space point -> pixel (x, y) through an orthographic camera of the layout"""
    b = np.array(cam["basis"], dtype=np.float64)        # columns: x (right), y (up), z (back)
    d = np.array(p, dtype=np.float64) - np.array(cam["origin"], dtype=np.float64)
    w, h = size
    half_w = cam["ortho_scale"] / 2
    half_h = half_w * h / w
    x, y = d @ b[0], d @ b[1]
    return (x / half_w * 0.5 + 0.5) * w, (0.5 - y / half_h * 0.5) * h


def main():
    shots = sys.argv[1]
    lay = json.load(open(sys.argv[2], encoding="utf8")) if len(sys.argv) > 2 else None
    out = os.path.join(shots, "compare")
    os.makedirs(out, exist_ok=True)
    rows = []
    for fn in sorted(os.listdir(shots)):
        if not fn.startswith("blender") or not fn.endswith(".png"): continue
        gfn = "godot" + fn[len("blender"):]
        if not os.path.exists(os.path.join(shots, gfn)): continue
        a, b = load(os.path.join(shots, fn)), load(os.path.join(shots, gfn))
        if a.shape != b.shape:
            rows.append((fn, "size %s vs %s" % (a.shape, b.shape))); continue
        d = np.abs(a - b)
        luma = lambda x: float((x @ np.array([0.2126, 0.7152, 0.0722])).mean())
        rows.append((fn[len("blender_"):] if fn.startswith("blender_") else fn,
                     "mean %.1f  p95 %.1f  luma B %.1f G %.1f" % (d.mean(), np.percentile(d, 95), luma(a), luma(b))))
        sheet = np.concatenate([a, b, np.clip(d * 4, 0, 255)], axis=1).astype(np.uint8)
        Image.fromarray(sheet).save(os.path.join(out, fn[len("blender"):].lstrip("_") or fn))
    for r in rows: print("COMPARE %-48s %s" % r)
    if lay:
        chart = [h for h in lay["helpers"] if h["kind"] == "chart"]
        W, H = lay["resolution"]
        for cam in lay["cameras"]:
            if cam["type"] != "ORTHO": continue
            bf = os.path.join(shots, "blender_%s.png" % cam["name"]); gf = os.path.join(shots, "godot_%s.png" % cam["name"])
            if not (os.path.exists(bf) and os.path.exists(gf)): continue
            a, b = load(bf), load(gf)
            seen = []
            for h in chart:
                x, y = project(cam, h["center"], (W, H))
                if 4 <= x < W - 4 and 4 <= y < H - 4:
                    xi, yi = int(x), int(y)
                    pa = a[yi - 3:yi + 4, xi - 3:xi + 4].reshape(-1, 3).mean(0)
                    pb = b[yi - 3:yi + 4, xi - 3:xi + 4].reshape(-1, 3).mean(0)
                    seen.append((h["props"]["gdx_emission"], pa.round(1).tolist(), pb.round(1).tolist()))
            for e, pa, pb in seen:
                print("CHART %s  %-28s B %-22s G %s" % (cam["name"], e, pa, pb))


if __name__ == "__main__":
    main()
