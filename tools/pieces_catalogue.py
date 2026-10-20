"""Build the piece catalogue from the Unity package's Data/pieces.json (plain Python with Pillow; no Blender):

  py tools/pieces_catalogue.py

Run tools/render_thumbs.py first (a background Blender) so renders/thumbs/ has a picture per piece. Writes:
  docs/PIECES.md                    every piece by kit and category: size, triangles, materials, its contact sheet
  docs/catalogue/sheets/<kit>_<category>.jpg   contact sheets (8 across, 160 px cells, the name under each)
  docs/catalogue/index.html         the browsable page: docs/catalogue/page.html with the pieces' data put in
The map-specific meshes (U_VKV_*, U_VARI_*: one valley map's terrain chunks, paving and water) are counted, not listed.
"""
import json, os, datetime
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "unity", "com.danielgruginski.medievalkit")
THUMBS = os.path.join(ROOT, "renders", "thumbs")
CAT = os.path.join(ROOT, "docs", "catalogue")
SHEETS = os.path.join(CAT, "sheets")
CELL, LABEL, COLS = 160, 18, 8
BG = (58, 62, 60)

KITS = [("building", "Building kit", "SM_VK_*", "Houses, walls, roofs, defences, market, harbour, props (`src/core`, `src/modules`)."),
        ("nature", "Nature", "SM_VK_* in VK_NaturePieces", "Trees, bushes, plants and herbs, rocks, ores (`src/nature/vk_nature.py`, `NATURE_SPECS`)."),
        ("terrain", "Terrain tiles", "SM_VKT_*", "Cliff, ramp, stair, shore and quay tiles the map generators place (`src/terrain`)."),
        ("interior", "Interior kit", "SM_VKI_*", "Walls, posts, floors, furniture and the dungeon and cave pieces (`src/interior`; see INTERIOR_KIT.md).")]

def kit_of(p):
    seg = p["fbx"].split("/")[2]
    if seg == "VKT": return "terrain"
    if seg == "VKI": return "interior"
    return "nature" if p.get("collection") == "VK_NaturePieces" else "building"

def main():
    data = json.load(open(os.path.join(PKG, "Data", "pieces.json"), encoding="utf8"))
    unique = sorted(n for n in data if n.startswith("U_"))
    groups = defaultdict(list)
    for n, p in data.items():
        if n.startswith("U_"): continue
        groups[(kit_of(p), p["fbx"].split("/")[3])].append(p)
    os.makedirs(SHEETS, exist_ok=True)
    for f in os.listdir(SHEETS):
        if f.endswith(".jpg"): os.remove(os.path.join(SHEETS, f))
    font = ImageFont.load_default(size=11)
    rows, md, nothumb = [], [], []
    total = sum(len(v) for v in groups.values())
    today = datetime.date.today().isoformat()
    md += ["# Kit pieces", "",
           f"Generated on {today} by `tools/pieces_catalogue.py` from the Unity package's `Data/pieces.json` (what was last",
           "exported), with a thumbnail per piece from `tools/render_thumbs.py`. Do not edit by hand: re-export, then run both.",
           "Browse it with pictures in [catalogue/index.html](catalogue/index.html) (open the file in a browser).", "",
           "Size is the piece's bounding box in metres in Blender's axes (x across, y deep, z up; fronts face -y). Tris is",
           "the exported triangle count. Mats is the number of materials on the piece. Prefabs are at",
           "`Packages/com.danielgruginski.medievalkit/Generated/Prefabs/<kit>/<category>/<name>.prefab`.", "",
           f"**{total} pieces**: " + ", ".join(f"{t} {sum(len(v) for (k, _), v in groups.items() if k == key)}" for key, t, _, _ in KITS) +
           f". Not listed: {len(unique)} meshes unique to one map (`U_VKV_*` valley chunks, paving and water; `U_VARI_*`).", ""]
    for key, title, pat, blurb in KITS:
        cats = sorted(c for k, c in groups if k == key)
        n_kit = sum(len(groups[(key, c)]) for c in cats)
        md += [f"## {title} (`{pat}`): {n_kit}", "", blurb, "",
               " · ".join(f"[{c}](#{key}-{c.lower()}) {len(groups[(key, c)])}" for c in cats), ""]
        for c in cats:
            ps = sorted(groups[(key, c)], key=lambda p: p["name"])
            sheet = f"{key}_{c}.jpg"
            nrow = (len(ps) + COLS - 1) // COLS
            img = Image.new("RGB", (COLS * CELL, nrow * (CELL + LABEL)), BG); dr = ImageDraw.Draw(img)
            for i, p in enumerate(ps):
                x, y = (i % COLS) * CELL, (i // COLS) * (CELL + LABEL)
                tp = os.path.join(THUMBS, p["name"] + ".png")
                if os.path.exists(tp):
                    th = Image.open(tp).convert("RGBA").resize((CELL, CELL), Image.LANCZOS)
                    tile = Image.new("RGBA", (CELL, CELL), BG + (255,)); tile.alpha_composite(th); img.paste(tile.convert("RGB"), (x, y))
                else:
                    nothumb.append(p["name"]); dr.text((x + 8, y + CELL // 2), "no thumbnail", fill=(150, 150, 150), font=font)
                label = p["name"].split("_", 2)[-1]
                if dr.textlength(label, font=font) > CELL - 6:
                    while len(label) > 3 and dr.textlength(label + "…", font=font) > CELL - 6: label = label[:-1]
                    label += "…"
                dr.text((x + 3, y + CELL + 2), label, fill=(220, 222, 214), font=font)
                (lo, hi) = p["bounds_blender"]
                rows.append(dict(n=p["name"], k=key, c=c, s=[round(hi[j] - lo[j], 2) for j in range(3)], t=p.get("tris", 0),
                                 m=p.get("materials", []), f=p["fbx"], sh=sheet, i=i,
                                 vk=(p.get("props") or {}).get("vki_kind")))
            img.save(os.path.join(SHEETS, sheet), quality=82, optimize=True)
            md += [f'### <a id="{key}-{c.lower()}"></a>{c}: {len(ps)}', "", f"![{c}](catalogue/sheets/{sheet})", "",
                   "| Piece | Size (m) | Tris | Mats |", "|---|---|---|---|"]
            for p in ps:
                (lo, hi) = p["bounds_blender"]
                md.append(f"| `{p['name']}` | {' × '.join(f'{hi[j] - lo[j]:.2f}' for j in range(3))} | {p.get('tris', 0):,} | {len(p.get('materials', []))} |")
            md.append("")
    open(os.path.join(ROOT, "docs", "PIECES.md"), "w", encoding="utf8", newline="\n").write("\n".join(md))
    tpl = open(os.path.join(CAT, "page.html"), encoding="utf8").read()
    meta = dict(date=today, total=total, unique=len(unique), kits=[dict(key=k, title=t, pat=p, blurb=b) for k, t, p, b in KITS],
                cols=COLS, cell=CELL, label=LABEL)
    blob = json.dumps(dict(meta=meta, pieces=rows), separators=(",", ":")).replace("</", "<\\/")
    assert tpl.count("/*CATALOGUE_DATA*/null") == 1
    page = tpl.replace("/*CATALOGUE_DATA*/null", blob)
    head = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body>\n')
    open(os.path.join(CAT, "index.html"), "w", encoding="utf8", newline="\n").write(head + page + "\n</body></html>\n")
    # the same page without the document skeleton, for publishing as an Artifact (the host adds its own)
    open(os.path.join(ROOT, "renders", "catalogue_page.html"), "w", encoding="utf8", newline="\n").write(page)
    print(f"{total} pieces in {len(groups)} categories; {len(nothumb)} without a thumbnail{': ' + ', '.join(nothumb[:12]) if nothumb else ''}")

if __name__ == "__main__":
    main()
