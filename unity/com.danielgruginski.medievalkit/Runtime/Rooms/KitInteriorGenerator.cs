using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// A random ground floor for <see cref="KitRoom"/> (the kit's houses in outline): a footprint by kind, a hall with the
    /// front door in the south wall and the hearth (Timber fireplace / Stone hearth) on its north wall, side rooms split off
    /// by partitions with doors, windows round the walls, the side walls raked at the camera end; each room a type
    /// (bedroom, kitchen, pantry, store, bar, workroom) with its zone styles and furniture codes, placed so every room stays
    /// walkable from its door.
    /// </summary>
    public static class KitInteriorGenerator
    {
        [Serializable]
        public class Options
        {
            [Tooltip("Cottage, Townhouse, Tavern or Workshop.")]
            public string kind = "Cottage";
            public int seed = 3;
            [Tooltip("0: by kind.")] public int nc, nr;
        }

        const float IG = 1.5f;

        class Part { public string type; public int c0, r0, c1, r1; public bool Has((int, int) p) => p.Item1 >= c0 && p.Item1 <= c1 && p.Item2 >= r0 && p.Item2 <= r1; }

        static readonly Dictionary<string, (string code, int min, int max, string place)[]> Furniture = new Dictionary<string, (string, int, int, string)[]>
        {
            ["hall"] = new[] { ("TB", 1, 1, "mid"), ("PN", 0, 1, "wall"), ("SH", 0, 1, "wall"), ("WP", 1, 1, "wall"), ("ba", 0, 1, "wall"), ("CH", 0, 1, "wall") },
            ["taproom"] = new[] { ("TB", 2, 3, "mid"), ("tb", 1, 2, "mid"), ("ba", 1, 2, "wall"), ("WP", 1, 1, "wall") },
            ["bar"] = new[] { ("CT", 1, 2, "wall"), ("CK", 1, 1, "wall"), ("BS", 0, 1, "wall"), ("ba", 1, 2, "wall") },
            ["bedroom"] = new[] { ("BX", 1, 1, "wall"), ("CH", 1, 1, "wall"), ("DR", 0, 1, "wall"), ("rg", 0, 1, "mid") },
            ["kitchen"] = new[] { ("KW", 1, 1, "wall"), ("OV", 0, 1, "wall"), ("PN", 0, 1, "wall"), ("ja", 1, 1, "wall"), ("ba", 1, 1, "wall") },
            ["pantry"] = new[] { ("PN", 1, 1, "wall"), ("ba", 1, 2, "wall"), ("ja", 1, 1, "wall"), ("bx", 0, 1, "wall") },
            ["store"] = new[] { ("bx", 2, 3, "wall"), ("ba", 1, 2, "wall"), ("GR", 0, 1, "wall") },
            ["workroom"] = new[] { ("WB", 1, 2, "wall"), ("GR", 1, 1, "wall"), ("bx", 1, 2, "wall"), ("ir", 0, 1, "wall") },
        };
        static readonly Dictionary<string, string> FloorOf = new Dictionary<string, string>
        {
            ["hall"] = "FlagRustic", ["taproom"] = "Boards_EW", ["bar"] = "Flag", ["bedroom"] = "Boards_NS", ["kitchen"] = "FlagRustic",
            ["pantry"] = "Earth", ["store"] = "Earth", ["workroom"] = "FlagRustic",
        };
        static readonly string[] Plasters = { "PlasterCream", "PlasterWhite", "PlasterOchre", "PlasterCream" };

        public static (string plan, JObject record) Generate(Options o, Func<string, (int, int)> fp = null)
        {
            var rnd = new System.Random(o.seed);
            fp ??= _ => (1, 1);
            string kind = o.kind;
            (int a, int b) ncR = kind == "Tavern" ? (8, 10) : kind == "Townhouse" ? (6, 8) : kind == "Workshop" ? (6, 8) : (6, 7);   // halls >= 4 wide: hearth + table
            (int a, int b) nrR = kind == "Tavern" ? (5, 6) : kind == "Townhouse" ? (5, 6) : (4, 5);
            int nc = o.nc > 0 ? o.nc : rnd.Next(ncR.a, ncR.b + 1), nr = o.nr > 0 ? o.nr : rnd.Next(nrR.a, nrR.b + 1);
            bool stone = kind == "Tavern" || (kind == "Townhouse" && rnd.Next(2) == 0);
            string perimeter = stone ? "Stone" : "Timber", partition = stone ? "Stone" : "Board";
            string special = stone ? "Hearth_300" : "Fireplace_300";
            string plaster = Plasters[rnd.Next(Plasters.Length)];

            // ---- parts: the hall (with the front door) and a side strip, split once more when deep enough
            string hallType = kind == "Tavern" ? "taproom" : kind == "Workshop" ? "workroom" : "hall";
            var sideTypes = kind == "Tavern" ? new[] { "bar", "kitchen", "store" } : kind == "Workshop" ? new[] { "store", "pantry" }
                          : kind == "Townhouse" ? new[] { "kitchen", "bedroom", "pantry" } : new[] { "bedroom", "pantry" };
            int sideW = Mathf.Clamp(nc / 3, 2, 3);
            bool east = rnd.Next(2) == 0;
            var parts = new List<Part>();
            var hall = east ? new Part { type = hallType, c0 = 0, c1 = nc - sideW - 1, r0 = 0, r1 = nr - 1 } : new Part { type = hallType, c0 = sideW, c1 = nc - 1, r0 = 0, r1 = nr - 1 };
            int sc0 = east ? nc - sideW : 0, sc1 = east ? nc - 1 : sideW - 1;
            parts.Add(hall);
            if (nr >= 5 && sideTypes.Length > 1)
            {
                int split = rnd.Next(2, nr - 1);
                parts.Add(new Part { type = sideTypes[0], c0 = sc0, c1 = sc1, r0 = split, r1 = nr - 1 });
                parts.Add(new Part { type = sideTypes[1 + rnd.Next(sideTypes.Length - 1)], c0 = sc0, c1 = sc1, r0 = 0, r1 = split - 1 });
            }
            else parts.Add(new Part { type = sideTypes[0], c0 = sc0, c1 = sc1, r0 = 0, r1 = nr - 1 });
            Part PartOf((int, int) p) => parts.FirstOrDefault(q => q.Has(p));

            // ---- walls: perimeter (windows, the front door, the hearth), partitions (a door from the hall into each room)
            var ew = new Dictionary<(int, int), string>();
            var ns = new Dictionary<(int, int), string>();
            var doorCells = new HashSet<(int, int)>();
            int line = east ? nc - sideW : sideW;                   // the N-S partition line
            int exitC = Mathf.Clamp((hall.c0 + hall.c1 + 1) / 2, hall.c0 + 1, hall.c1 - 1);       // the front door, mid-hall
            for (int i = 0; i < nc; i++)
            {
                ew[(i, nr)] = rnd.NextDouble() < 0.3 && i != line && i != line - 1 && i > 0 && i < nc - 1 ? "WW" : "##";
                ew[(i, 0)] = i == exitC ? "ee" : (rnd.NextDouble() < 0.35 && Math.Abs(i - exitC) > 1 ? "ww" : "==");
            }
            doorCells.Add((exitC, 0));
            // the hearth: two cells of the hall's north wall, clear of the corners and the partition
            var hearthAt = Enumerable.Range(hall.c0 + 1, Math.Max(0, hall.c1 - hall.c0 - 2)).ToList();      // i, i + 1 inside the hall's ends
            int? hearth = hearthAt.Count > 0 ? hearthAt[rnd.Next(hearthAt.Count)] : (int?)null;
            if (hearth is int h0) { ew[(h0, nr)] = "FF"; ew[(h0 + 1, nr)] = "FF"; }
            for (int r = 0; r < nr; r++)
            {
                ns[(0, r)] = r == 0 ? "t" : (rnd.NextDouble() < 0.3 && r < nr - 1 ? "W" : "#");
                ns[(nc, r)] = r == 0 ? "t" : (rnd.NextDouble() < 0.3 && r < nr - 1 ? "W" : "#");
            }
            // partitions: the N-S line between the hall and the side rooms, each side room a door ("d") from the hall
            foreach (var side in parts.Skip(1))
            {
                var rows = Enumerable.Range(side.r0, side.r1 - side.r0 + 1).ToList();
                int dr = rows[rnd.Next(rows.Count)];
                foreach (var r in rows) ns[(line, r)] = r == dr ? "d" : ":";
                doorCells.Add((east ? line : line - 1, dr));
                doorCells.Add((east ? line - 1 : line, dr));
            }
            if (parts.Count > 2)                                    // the E-W partition between the two side rooms
                for (int i = sc0; i <= sc1; i++) ew[(i, parts[1].r0)] = "==";

            // ---- furniture codes per room; the hearth's cells kept clear (the fireplace stands into the room)
            var codes = new Dictionary<(int, int), string>();
            var reserved = new HashSet<(int, int)>(doorCells);
            foreach (var d in doorCells) foreach (var q in new[] { (d.Item1 + 1, d.Item2), (d.Item1 - 1, d.Item2), (d.Item1, d.Item2 + 1), (d.Item1, d.Item2 - 1) }) reserved.Add(q);
            if (hearth is int hh) { reserved.Add((hh, nr - 1)); reserved.Add((hh + 1, nr - 1)); }
            foreach (var p in parts)
                KitFurnisher.Place(rnd, p.c0, p.r0, p.c1, p.r1, Furniture[p.type], codes, reserved, doorCells, new HashSet<(int, int)>(), fp);

            // ---- zones and the record
            var zones = new JObject();
            for (int k = 0; k < parts.Count; k++)
            {
                var p = parts[k];
                var box = new JArray(); box.Add(new JArray(p.c0, p.c1, p.r0, p.r1));      // new JArray(JArray) would copy, not nest
                zones[$"{p.type}{k}"] = new JObject
                {
                    ["cells"] = box, ["floor"] = FloorOf[p.type],
                    ["wall"] = p.type == "store" || p.type == "pantry" ? (stone ? "StoneIn" : "PlasterDaub") : plaster,
                };
            }
            var links = new JArray(); links.Add(new JArray("front", "exit", "@return"));
            var R = new JObject
            {
                ["building"] = kind, ["floor"] = 0, ["preset"] = "Day",
                ["family"] = new JObject { ["perimeter"] = perimeter, ["partition"] = partition },
                ["partition_wall"] = "zone", ["zones"] = zones, ["links"] = links,
                ["generated"] = new JObject { ["generator"] = "interior", ["kind"] = kind, ["seed"] = o.seed, ["nc"] = nc, ["nr"] = nr },
            };
            if (hearth != null) R["special"] = special;
            return (Plan(nc, nr, codes, ew, ns), R);
        }

        static string Plan(int nc, int nr, Dictionary<(int, int), string> codes, Dictionary<(int, int), string> ew, Dictionary<(int, int), string> ns)
        {
            var sb = new StringBuilder("\n      " + string.Join(" ", Enumerable.Range(0, nc).Select(i => i.ToString().PadLeft(2))) + "\n");
            for (int j = nr; j >= 0; j--)
            {
                sb.Append("     +");
                for (int i = 0; i < nc; i++)
                {
                    string tok = ew.TryGetValue((i, j), out var t) ? t : "  ";
                    sb.Append(tok).Append(j == 0 || j == nr || i == nc - 1 || tok.Trim().Length > 0 ? "+" : " ");
                }
                sb.Append('\n');
                if (j == 0) break;
                int r = j - 1;
                sb.Append("  ").Append(r.ToString().PadLeft(2)).Append(' ');
                for (int i = 0; i <= nc; i++)
                {
                    sb.Append(ns.TryGetValue((i, r), out var t) ? t : " ");
                    if (i < nc) sb.Append(codes.TryGetValue((i, r), out var c) ? c : "..");
                }
                sb.Append('\n');
            }
            return sb.ToString();
        }
    }
}
