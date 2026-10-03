using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// Loose debris that gives a level its age (vki_props_debris.vki_rooms_debris, in outline): R["debris"] = {density
    /// (share of a zone's open cells that get a piece, default 0.15), seed, zones {zone: density}, themes {zone: theme}}.
    /// A zone's theme comes from its floor (cave, lair, dungeon, ruins, sewer, dwarf; forge and mine by name); each theme
    /// draws from its own weighted mix. Pieces stand on random points of open cells, turned at random, clear of walls,
    /// posts, links, props, spawns, the rock and the chasm; heavy stone gathers at the feet of walls and rock faces and
    /// scree lies along them; stone debris takes the theme's stone.
    /// </summary>
    public partial class KitRoom
    {
        static readonly Dictionary<string, string> DebrisTheme = new Dictionary<string, string>
        {
            ["CaveFloor"] = "cave", ["EarthDamp"] = "lair", ["DungeonFlag"] = "dungeon", ["DungeonFlagWarm"] = "dungeon",
            ["AncientFlag"] = "ruins", ["SewerFloor"] = "sewer", ["DwarfFloor"] = "dwarf", ["DwarfFlag"] = "dwarf",
        };
        public static readonly Dictionary<string, string> DebrisStone = new Dictionary<string, string>
        {
            ["cave"] = "M_VKI_CaveRock", ["lair"] = "M_VKI_CaveRock", ["dungeon"] = "M_VKI_DungeonBlock", ["ruins"] = "M_VKI_AncientBlock",
            ["sewer"] = "M_VKI_SewerBlock", ["dwarf"] = "M_VKI_DwarfBlock", ["forge"] = "M_VKI_DwarfBlock", ["mine"] = "M_VKI_CaveRock",
        };
        static readonly Dictionary<string, (string kind, float w)[]> DebrisKinds = new Dictionary<string, (string, float)[]>
        {
            ["cave"] = new[] { ("Rocks_A", 3f), ("Rocks_B", 2f), ("Rocks_C", 2f), ("Rubble", 1.5f), ("Stalactite", 2f), ("Pottery_C", 0.6f),
                               ("Weapons", 0.6f), ("Sack", 0.4f), ("Campfire", 0.3f), ("Overlay_Gravel", 1.2f), ("Overlay_Bones", 0.5f) },
            ["lair"] = new[] { ("Rocks_A", 2f), ("Rocks_B", 1f), ("Rubble", 0.8f), ("Pottery_C", 1.5f), ("Pottery_A", 1f), ("PotPile", 0.8f),
                               ("Planks", 1.5f), ("Rags", 1.5f), ("Sack", 1f), ("Barrel", 0.8f), ("Weapons", 1f), ("Campfire", 0.5f),
                               ("Overlay_Refuse", 1.2f), ("Overlay_Bones", 1f) },
            ["dungeon"] = new[] { ("Rocks_A", 1.5f), ("Rocks_C", 1.5f), ("Rubble", 1.2f), ("Pottery_A", 1.5f), ("Pottery_B", 1f),
                                  ("Pottery_C", 1.5f), ("PotPile", 1f), ("Planks", 1.5f), ("Crate", 1f), ("Barrel", 1f), ("Weapons", 1f),
                                  ("Rags", 1f), ("Sack", 0.8f), ("Overlay_Bones", 1f), ("Overlay_Puddle", 0.6f) },
            ["ruins"] = new[] { ("Masonry_A", 3f), ("Masonry_B", 2f), ("Rubble", 2f), ("Rocks_A", 2f), ("Rocks_B", 1f), ("Rocks_C", 1f),
                                ("Pottery_A", 1.5f), ("Pottery_B", 1f), ("Pottery_C", 1.5f), ("PotPile", 1f), ("Weapons", 0.6f), ("Overlay_Bones", 0.5f) },
            ["sewer"] = new[] { ("Rocks_A", 1f), ("Rubble", 0.8f), ("Planks", 2f), ("Barrel", 1f), ("Crate", 1f), ("Rags", 2f), ("Sack", 1f),
                                ("Pottery_C", 1f), ("Pottery_B", 0.5f), ("Overlay_Sludge", 1.5f), ("Overlay_Puddle", 1f), ("Overlay_Bones", 0.3f) },
            ["dwarf"] = new[] { ("Rocks_A", 1.5f), ("Rubble", 1f), ("Masonry_A", 1f), ("Ore", 2f), ("Pottery_C", 1f), ("Weapons", 0.8f),
                                ("Barrel", 0.7f), ("Planks", 0.7f), ("Slag", 0.5f) },
            ["forge"] = new[] { ("Slag", 3f), ("Ore", 2f), ("Rocks_A", 1f), ("Rubble", 1f), ("Planks", 1f), ("Barrel", 1f) },
            ["mine"] = new[] { ("Rocks_A", 3f), ("Rocks_B", 2f), ("Rocks_C", 2f), ("Rubble", 1.2f), ("Ore", 2.5f), ("Tools", 1.5f), ("Rail", 1f),
                               ("Planks", 1.5f), ("Sack", 0.6f), ("Crate", 0.4f), ("Barrel", 0.4f), ("Campfire", 0.2f), ("Overlay_Gravel", 1.5f) },
        };
        static readonly HashSet<string> DebrisOnce = new HashSet<string> { "Campfire" };
        static readonly HashSet<string> DebrisHug = new HashSet<string> { "Rocks_B", "Rocks_C", "Rubble", "Masonry_A", "Masonry_B", "Stalactite", "Overlay_Gravel" };
        static readonly HashSet<string> DebrisAlong = new HashSet<string> { "Rocks_C" };
        static readonly HashSet<string> NoFloor = new HashSet<string> { "##", "vv", "==", "ss", "ww", "ll", "~~" };

        struct Rect2 { public float x0, y0, x1, y1; public Rect2 Grow(float m) => new Rect2 { x0 = x0 - m, y0 = y0 - m, x1 = x1 + m, y1 = y1 + m }; }
        static bool Hit(Rect2 a, Rect2 b, float gap = 0f) => a.x0 < b.x1 + gap && b.x0 < a.x1 + gap && a.y0 < b.y1 + gap && b.y0 < a.y1 + gap;
        static float Near(float x, float y, List<Rect2> boxes, out float dxOut, out float dyOut)
        {
            float best = float.MaxValue; dxOut = dyOut = 0f;
            foreach (var b in boxes)
            {
                float dx = Mathf.Max(b.x0 - x, 0f, x - b.x1), dy = Mathf.Max(b.y0 - y, 0f, y - b.y1), d = Mathf.Sqrt(dx * dx + dy * dy);
                if (d < best) { best = d; dxOut = dx; dyOut = dy; }
            }
            return best;
        }
        static Rect2 Footprint(float[] bx, float x, float y, float rot)
        {
            var r = new Rect2 { x0 = float.MaxValue, y0 = float.MaxValue, x1 = float.MinValue, y1 = float.MinValue };
            foreach (var px in new[] { bx[0], bx[3] })
                foreach (var py in new[] { bx[1], bx[4] })
                {
                    var w = Frame(x, y, rot, px, py);
                    r.x0 = Mathf.Min(r.x0, w.x); r.y0 = Mathf.Min(r.y0, w.y); r.x1 = Mathf.Max(r.x1, w.x); r.y1 = Mathf.Max(r.y1, w.y);
                }
            return r;
        }
        static Rect2 Flat(Box b) => new Rect2 { x0 = b.a.x, y0 = b.a.y, x1 = b.b.x, y1 = b.b.y };

        /// <summary>a piece's vki_collider boxes (Blender local centre, size) as room rects</summary>
        IEnumerable<Rect2> ColliderRects(Placed p)
        {
            if (!(PropJ(p.kp, "vki_collider") is JArray boxes)) { yield return Flat(ObjBox(p)); yield break; }
            foreach (var c in boxes)
            {
                float cx = (float)c[0], cy = (float)c[1], sx = Mathf.Abs((float)c[3]) / 2f, sy = Mathf.Abs((float)c[4]) / 2f;
                if ((float)c[2] + Mathf.Abs((float)c[5]) / 2f <= 0.01f) continue;          // below the floor: no obstacle
                yield return Footprint(new[] { cx - sx, cy - sy, 0f, cx + sx, cy + sy, 0f }, p.x, p.y, p.rot);
            }
        }

        void Debris()
        {
            if (!(R["debris"] is JObject cfg)) return;
            var rnd = new System.Random((int?)cfg["seed"] ?? 0);
            var obst = new List<Rect2>();
            var structure = new List<Rect2>();                       // walls and rock faces: the feet debris gathers at
            foreach (var p in placed)
            {
                string c = Cls(p);
                if (c == "wall") { var env = Flat(WallEnv(p)).Grow(0.06f); obst.Add(env); structure.Add(env); obst.Add(Flat(ObjBox(p)).Grow(0.04f)); }
                else if (c == "post" || c == "leaf" || c == "link" || c == "pit" || c == "stair") obst.Add(Flat(ObjBox(p)).Grow(0.10f));
                else if (c == "prop" || c == "overlay") obst.Add(Flat(ObjBox(p)).Grow(0.12f));
                else if (c == "rock" || c == "ground")
                    foreach (var b in ColliderRects(p)) { var g = b.Grow(0.15f); obst.Add(g); if (c == "rock") structure.Add(g); }
            }
            foreach (var sp in logic.GetComponentsInChildren<KitSpawn>())
            {
                var lp = sp.transform.localPosition;
                obst.Add(new Rect2 { x0 = -lp.x - 0.8f, y0 = -lp.z - 0.8f, x1 = -lp.x + 0.8f, y1 = -lp.z + 0.8f });
            }
            var zones = (JObject)R["zones"];
            var byZone = new SortedDictionary<string, (string theme, List<(int, int)> cells)>();
            foreach (var kv in Layout.zmap.OrderBy(k => k.Key.Item1).ThenBy(k => k.Key.Item2))
            {
                string zn = kv.Value;
                if (zn == null || (Layout.P.codes.TryGetValue(kv.Key, out var code) && NoFloor.Contains(code))) continue;
                string th = (string)cfg["themes"]?[zn];
                if (th == null && zones[zn]?["floor"] != null) DebrisTheme.TryGetValue((string)zones[zn]["floor"], out th);
                if (th == null || !DebrisKinds.ContainsKey(th)) continue;
                if (!byZone.TryGetValue(zn, out var e)) byZone[zn] = e = (th, new List<(int, int)>());
                e.cells.Add(kv.Key);
            }
            var done = new List<Rect2>();
            var once = new HashSet<string>();
            int n = 0;
            foreach (var kv in byZone)
            {
                var (th, cells) = kv.Value;
                float density = cfg["zones"]?[kv.Key] != null ? (float)cfg["zones"][kv.Key] : (float?)cfg["density"] ?? 0.15f;
                int want = Mathf.RoundToInt(density * cells.Count), got = 0;
                var order = cells.OrderBy(_ => rnd.Next()).ToList();
                foreach (var cell in order.Concat(order).Concat(order).Concat(order))
                {
                    if (got >= want) break;
                    var ks = DebrisKinds[th].Where(k => !once.Contains(k.kind)).ToList();
                    float t = (float)rnd.NextDouble() * ks.Sum(k => k.w);
                    string kd = ks[ks.Count - 1].kind;
                    foreach (var k in ks) { t -= k.w; if (t <= 0f) { kd = k.kind; break; } }
                    string piece = kd.StartsWith("Overlay_") || kd.StartsWith("Prop_") ? "SM_VKI_" + kd : "SM_VKI_Overlay_Debris_" + kd;
                    var prefab = rules.Prefab(piece);
                    if (prefab == null) continue;
                    var bx = LocalBox(prefab);
                    bool hug = DebrisHug.Contains(kd);
                    (float d, float x, float y, float rot, Rect2 fp)? best = null;
                    for (int tr = 0; tr < 8; tr++)
                    {
                        float x = Layout.IG * (cell.Item1 + 0.15f + 0.7f * (float)rnd.NextDouble());
                        float y = Layout.IG * (cell.Item2 + 0.15f + 0.7f * (float)rnd.NextDouble());
                        float rot = Mathf.Round((float)rnd.NextDouble() * 3600f) / 10f;
                        if (DebrisAlong.Contains(kd) && structure.Count > 0)
                        {
                            Near(x, y, structure, out var dx, out var dy);
                            rot = (dx > dy ? 90f : 0f) + ((float)rnd.NextDouble() * 24f - 12f) + 180f * rnd.Next(2);
                        }
                        var fp = Footprint(bx, x, y, rot);
                        if (obst.Any(b => Hit(fp, b)) || done.Any(b => Hit(fp, b, 0.15f))) continue;
                        float dd = hug && structure.Count > 0 ? Near(x, y, structure, out _, out _) : 0f;
                        if (best == null || dd < best.Value.d) best = (dd, x, y, rot, fp);
                        if (!hug) break;
                    }
                    if (best == null) continue;
                    var b0 = best.Value;
                    var kp0 = prefab.GetComponent<KitPiece>();
                    var st = Truthy(kp0?.Get("vki_debris_stone")) && DebrisStone.TryGetValue(th, out var stone) ? new Dictionary<string, string> { ["cap"] = stone } : null;
                    var o = Put(props, piece, b0.x, b0.y, b0.rot, 0f, st, "debris");
                    if (o == null) continue;
                    o.kp?.Set("vki_debris", "1");
                    o.kp?.Set("vki_debris_theme", th);
                    done.Add(b0.fp);
                    got++; n++;
                    if (DebrisOnce.Contains(kd)) once.Add(kd);
                }
            }
        }
    }
}
