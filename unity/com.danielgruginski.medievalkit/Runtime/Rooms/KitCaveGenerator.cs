using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// A random cave level for <see cref="KitRoom"/>.
    /// Layout "Maze": chambers of different sizes with noisy outlines, joined by winding tunnels two to three cells wide
    /// (a spanning tree plus loops), dead-end spurs ending in alcoves (loot, a skeleton), roughened and smoothed into rock.
    /// Layout "Open": the kit's cellular automaton (vki_cave_generate): random rock round a carved passage and chambers.
    /// The chasm is a curve that drifts across the cave from one side to the other, its width breathing along its length
    /// (pinching to nothing leaves a natural rock bridge), optionally forking. Where it cuts the cave in two, the generator
    /// crosses it: a rope bridge over a two-cell narrows (turned to the crossing), a one-cell gap filled as a land bridge,
    /// or a wider stretch pinched to two cells round a bridge. Then pools, dressing, west and east tunnels, an optional
    /// point of interest. With a creature set, encounters (<see cref="KitEncounter"/> markers for the game's monsters) spread
    /// through the cave, harder the farther from the way in; the point of interest is the boss's lair. The result is a
    /// plan and a room record.
    /// </summary>
    public static class KitCaveGenerator
    {
        [Serializable]
        public class Options
        {
            [Tooltip("Maze: chambers, winding tunnels, loops and dead ends. Open: the kit's cellular automaton.")]
            public string layout = "Maze";
            public int nc = 28, nr = 20, seed = 7, pools = 2, props = 18;
            [Tooltip("Maze: chambers per 100 cells.")] public float chambers = 2.0f;
            [Tooltip("Maze: extra tunnels beyond the spanning tree, per chamber.")] [Range(0, 1)] public float loops = 0.35f;
            [Tooltip("Maze: spurs that end in an alcove.")] public int deadEnds = 3;
            public bool chasm = true;
            [Tooltip("A second chasm branching off the first.")] public bool chasmFork = true;
            [Tooltip("The chasm's width in cells, narrowest .. widest along its length.")] public Vector2 chasmWidth = new Vector2(0.4f, 3.6f);
            [Tooltip("Loose debris (rocks, rubble, broken stalactites, gravel, bones...): share of the open cells.")]
            [Range(0, 1)] public float debris = 0.34f;
            public string poi;              // e.g. "POI_WyrmBones": a w x h point of interest near the centre
            public int poiW = 2, poiH = 2;
            public string poiCode = "WY";
            [Tooltip("Openings on the map's edges into the next map of a chain (KitPortal); none: the old tunnels west and east.")]
            public List<KitPortal> portals = new List<KitPortal>();
            [Tooltip("Encounters: the creatures that live here (rat, spider, goblin...), comma-separated from the way in to the deep end (\"rat,spider\": rats near the way in, spiders deeper); empty: none.")]
            public string creature = "";
            [Tooltip("Encounters: how many, spread through the cave, harder the farther from the way in (the point of interest holds the boss).")]
            public int encounters = 4;
            [Tooltip("Finds in the dead ends' alcoves, as piece:code pairs (\"LootPile:lp,Goblin_Dead:gd\"); a piece not in the kit is looked up in the project. Every find but an Overlay_ is marked as loot (record \"markers\", role loot). Empty: loot pile, fallen skeleton, treasure chest, bones.")]
            public string finds = "";
            [Tooltip("Finds besides the alcoves': this many more along the cave's walls, spread out (bodies along the way).")]
            public int extraFinds = 0;
            [Tooltip("Dressing round the cave, as piece:code pairs (\"EggSacs:es,Cocoon:co\"), placed in turn. Empty: crystals, glowing mushrooms, stalagmites, boulders, gravel.")]
            public string dressing = "";
        }

        /// <summary>"piece:code, piece:code" -> pairs (a missing code: the piece's first two letters)</summary>
        static (string, string)[] Pairs(string list, (string, string)[] fallback)
        {
            if (string.IsNullOrWhiteSpace(list)) return fallback;
            var o = list.Split(',').Select(e => e.Trim()).Where(e => e.Length > 0).Select(e =>
            {
                int i = e.IndexOf(':');
                string piece = i < 0 ? e : e.Substring(0, i).Trim(), code = i < 0 ? "" : e.Substring(i + 1).Trim();
                if (code.Length != 2) code = (piece + "__").Substring(0, 2).ToLowerInvariant();
                return (piece, code);
            }).ToArray();
            return o.Length > 0 ? o : fallback;
        }

        const float IG = 1.5f;
        static readonly (int, int)[] N4 = { (1, 0), (-1, 0), (0, 1), (0, -1) };

        static float VNoise(float u, float w, int seed)
        {
            int i0 = Mathf.FloorToInt(u), j0 = Mathf.FloorToInt(w);
            float fu = u - i0, fw = w - j0, su = fu * fu * (3 - 2 * fu), sw = fw * fw * (3 - 2 * fw);
            float a = (float)KitRoomLayout.Hash01(i0, j0, seed), b = (float)KitRoomLayout.Hash01(i0 + 1, j0, seed);
            float c = (float)KitRoomLayout.Hash01(i0, j0 + 1, seed), d = (float)KitRoomLayout.Hash01(i0 + 1, j0 + 1, seed);
            return Mathf.Lerp(Mathf.Lerp(a, b, su), Mathf.Lerp(c, d, su), sw);
        }

        /// <summary>vki_rooms_mkplan: an ASCII plan from cell codes (frame walls "##" / "==" / "#" / "t")</summary>
        public static string MakePlan(int nc, int nr, Dictionary<(int, int), string> codes)
        {
            var sb = new StringBuilder("\n      " + string.Join(" ", Enumerable.Range(0, nc).Select(i => i.ToString().PadLeft(2))) + "\n");
            for (int j = nr; j >= 0; j--)
            {
                sb.Append("     +");
                for (int i = 0; i < nc; i++)
                {
                    string tok = j == nr ? "##" : j == 0 ? "==" : "  ";
                    sb.Append(tok).Append(j == 0 || j == nr || i == nc - 1 ? "+" : " ");
                }
                sb.Append('\n');
                if (j == 0) break;
                int r = j - 1;
                sb.Append("  ").Append(r.ToString().PadLeft(2)).Append(' ');
                for (int i = 0; i <= nc; i++)
                {
                    sb.Append(i == 0 || i == nc ? (r == 0 ? "t" : "#") : " ");
                    if (i < nc) sb.Append(codes.TryGetValue((i, r), out var c) ? c : "..");
                }
                sb.Append('\n');
            }
            return sb.ToString();
        }

        public static (string plan, JObject record) Generate(Options o)
        {
            var rnd = new System.Random(o.seed);
            int nc = Mathf.Max(12, o.nc), nr = Mathf.Max(10, o.nr);
            var cells = new List<(int, int)>();
            for (int c = 0; c < nc; c++) for (int r = 0; r < nr; r++) cells.Add((c, r));
            var alcoves = new List<(int, int)>();
            var open = o.layout == "Open" ? OpenCave(nc, nr, rnd, cells) : MazeCave(o, nc, nr, rnd, cells, alcoves);

            // ---- the chasm and its crossings
            var xs = new HashSet<(int, int)>();
            var bridges = new List<(int c, int r, bool across)>();      // across: the bridge runs E-W (rot 90)
            if (o.chasm)
            {
                // the chasm carves its own gorge across the map (through rock too), with ledges along stretches of it
                var banks = new HashSet<(int, int)>();
                xs = Chasm(o, nc, nr, rnd, open, banks);
                open.UnionWith(banks);
                open.UnionWith(xs);
                // floor stays two cells wide (a one-cell ledge closes under the rock tiles' lobes)
                var floor = TwoWide(new HashSet<(int, int)>(open.Where(p => !xs.Contains(p))), cells, nc, nr);
                open = new HashSet<(int, int)>(floor.Concat(xs));
                Cross(open, xs, bridges, rnd);
            }
            // the cave: the largest region one can walk (floor and bridge decks); the chasm where it borders that region
            var deckAx = Decks(bridges);
            var decks = new HashSet<(int, int)>(deckAx.Keys);
            var walk = Largest(open.Where(p => !xs.Contains(p) || decks.Contains(p)), deckAx);
            var keepX = new HashSet<(int, int)>(decks);
            var todoX = new Stack<(int, int)>(xs.Where(p => !decks.Contains(p) && N4.Any(d => walk.Contains((p.Item1 + d.Item1, p.Item2 + d.Item2)))));
            foreach (var p in todoX) keepX.Add(p);
            while (todoX.Count > 0)
            {
                var (c, r) = todoX.Pop();
                foreach (var (dc, dr) in N4) { var q = (c + dc, r + dr); if (xs.Contains(q) && keepX.Add(q)) todoX.Push(q); }
            }
            open = new HashSet<(int, int)>(walk.Concat(keepX));
            xs = new HashSet<(int, int)>(keepX);
            // ---- portals (openings on the map's edges into the next map of a chain): a straight way in from the edge,
            // then on to the cave's floor (across the chasm on a causeway if it must); the chasm kept off the approach
            var portals = (o.portals ?? new List<KitPortal>()).Select(pt => KitPortal.FromJson(pt.ToJson())).ToList();
            var portalCells = new HashSet<(int, int)>();
            foreach (var pt in portals)
            {
                var way = pt.Carve(nc, nr, q => walk.Contains(q) && !xs.Contains(q), rnd);
                var approach = Enumerable.Range(0, KitPortal.Approach).SelectMany(d => pt.Row(d, nc, nr)).ToList();
                foreach (var q in xs.Where(x => approach.Any(a => Math.Max(Math.Abs(a.Item1 - x.Item1), Math.Abs(a.Item2 - x.Item2)) <= 1)).ToList())
                {
                    xs.Remove(q); open.Remove(q);
                }
                foreach (var q in way) { open.Add(q); xs.Remove(q); portalCells.Add(q); }
            }
            alcoves = alcoves.Where(a => open.Contains(a) && !xs.Contains(a)).ToList();
            var codes = cells.Where(p => !open.Contains(p)).ToDictionary(p => p, p => "##");
            foreach (var p in xs) codes[p] = "vv";
            var clear = new HashSet<(int, int)>();
            foreach (var (c, r, across) in bridges)
            {
                var deck = across ? new[] { (c, r), (c + 1, r) } : new[] { (c, r), (c, r + 1) };
                foreach (var q in deck) codes[q] = "==";
                for (int a = -1; a <= 1; a++)
                    foreach (var d in new[] { -2, -1, 2, 3 })
                        clear.Add(across ? (c + d, r + a) : (c + a, r + d));
            }
            foreach (var q in portalCells) clear.Add(q);
            bool NearX(int c, int r) { for (int a = -1; a <= 1; a++) for (int b = -1; b <= 1; b++) if (xs.Contains((c + a, r + b))) return true; return false; }
            bool Free(int c, int r) => open.Contains((c, r)) && !xs.Contains((c, r)) && !clear.Contains((c, r)) && !codes.ContainsKey((c, r));

            // ---- tunnels out, west and east: a short drive from the cave to the map's edge if needed
            var tunnels = new JObject();
            var links = new JArray();
            foreach (var (side, i, c0, dir) in new[] { ("west", 0, 0, 1), ("east", nc, nc - 1, -1) })
            {
                if (portals.Count > 0) break;                                    // a chained map: its portals are the ways out
                // the row pair nearest the middle whose rock run from the edge to the cave is shortest and ends on free floor
                int best = -1, bestDist = int.MaxValue, bestK = 0;
                for (int j = 2; j <= nr - 3; j++)
                {
                    int k = 0;
                    while (k < nc / 2 && !open.Contains((c0 + dir * k, j - 1)) && !open.Contains((c0 + dir * k, j))) k++;
                    if (k >= nc / 2 || !Free(c0 + dir * k, j - 1) || !Free(c0 + dir * k, j)) continue;
                    int dist = k * 4 + Math.Abs(j - nr / 2);
                    if (dist < bestDist) { bestDist = dist; best = j; bestK = k; }
                }
                if (best < 0) continue;
                for (int k = 0; k < bestK; k++)                                 // drive the tunnel through the rock
                    foreach (var q in new[] { (c0 + dir * k, best - 1), (c0 + dir * k, best) }) { open.Add(q); codes.Remove(q); }
                tunnels[$"{i}|{best}"] = side;
                var lk = new JArray(side, "passage", "@return");
                links.Add(lk);
                for (int d = -2; d <= 1; d++) { clear.Add((c0, best + d)); clear.Add((c0 + dir, best + d)); }
                codes[(c0, best - 1)] = codes[(c0, best)] = "Sx";
            }

            // ---- props: bridges, the point of interest, alcove finds, pools, dressing
            var plist = new JArray();
            var NH = new JObject { ["hug"] = false };
            foreach (var (c, r, across) in bridges)
                plist.Add(across ? new JArray("RopeBridge_420", IG * (c + 1), IG * r + 0.75f, 90, null, null, NH.DeepClone())
                                 : new JArray("RopeBridge_420", IG * c + 0.75f, IG * (r + 1), 0, null, null, NH.DeepClone()));
            (int, int)? poiAt = null;
            if (!string.IsNullOrEmpty(o.poi))
            {
                var blocks = cells.Where(p => Enumerable.Range(-1, o.poiW + 2).All(a => Enumerable.Range(-1, o.poiH + 2).All(b => Free(p.Item1 + a, p.Item2 + b))) &&
                                              !Enumerable.Range(0, o.poiW).Any(a => Enumerable.Range(0, o.poiH).Any(b => NearX(p.Item1 + a, p.Item2 + b)))).ToList();
                if (blocks.Count > 0)
                {
                    var (c, r) = blocks.OrderBy(q => Math.Pow(q.Item1 + o.poiW / 2.0 - nc / 2.0, 2) + Math.Pow(q.Item2 + o.poiH / 2.0 - nr / 2.0, 2)).First();
                    plist.Add(new JArray(o.poi, IG * (c + o.poiW / 2f), IG * (r + o.poiH / 2f), 0, null, null, NH.DeepClone()));
                    for (int a = 0; a < o.poiW; a++) for (int b = 0; b < o.poiH; b++) codes[(c + a, r + b)] = o.poiCode;
                    poiAt = (c + o.poiW / 2, r + o.poiH / 2);
                }
            }
            // a find or a dressing prop may not cut the cave: the floor round it stays as many regions as before (bridge decks
            // joining along their span only), and no free cell beside it is left in a one-cell squeeze (the rock tiles'
            // lobes close those)
            var deckAt = Decks(bridges);
            HashSet<(int, int)> WalkCells((int, int)? but) => new HashSet<(int, int)>(open.Where(q =>
                (!xs.Contains(q) || deckAt.ContainsKey(q)) && q != but && !(codes.TryGetValue(q, out var cc) && cc != "Sx" && cc != "==")));
            bool Cuts((int, int) p)
            {
                var w = WalkCells(p);
                if (Regions(w, deckAt).Count > Regions(WalkCells(null), deckAt).Count) return true;
                foreach (var (dc, dr) in N4)
                {
                    var n = (p.Item1 + dc, p.Item2 + dr);
                    if (!w.Contains(n) || deckAt.ContainsKey(n)) continue;
                    if (!new[] { (0, 0), (-1, 0), (0, -1), (-1, -1) }.Any(b => new[] { (0, 0), (1, 0), (0, 1), (1, 1) }
                            .All(d => w.Contains((n.Item1 + b.Item1 + d.Item1, n.Item2 + b.Item2 + d.Item2))))) return true;
                }
                return false;
            }
            var finds = Pairs(o.finds, new[] { ("LootPile", "lp"), ("Skeleton_Fallen", "sf"), ("Chest_Treasure", "TR"), ("Overlay_Bones", "bo") });
            var markers = new JArray();
            int fi = rnd.Next(finds.Length);
            foreach (var al in alcoves)
            {
                // the alcove's cell, or a free one beside it, the deepest in the rock first, that cuts nothing
                int Rock((int, int) q) => N4.Count(d => !open.Contains((q.Item1 + d.Item1, q.Item2 + d.Item2)));
                var spot = new[] { (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1) }.Select(d => (al.Item1 + d.Item1, al.Item2 + d.Item2))
                    .Where(q => Free(q.Item1, q.Item2)).OrderByDescending(Rock).Where(q => !Cuts(q)).Select(q => ((int, int)?)q).FirstOrDefault();
                if (spot == null) continue;
                var (c, r) = spot.Value;
                var (piece, code) = finds[fi++ % finds.Length];
                plist.Add(new JArray(piece, IG * (c + 0.5f), IG * (r + 0.5f), rnd.Next(4) * 90, null, null, NH.DeepClone()));
                codes[(c, r)] = code;
                if (!piece.StartsWith("Overlay_"))          // something to search: the game makes it a container
                    markers.Add(new JObject
                    {
                        ["id"] = $"loot{markers.Count}", ["role"] = "loot", ["at"] = new JArray(IG * (c + 0.5f), IG * (r + 0.5f)), ["note"] = piece,
                    });
            }
            // more finds along the walls, spread through the cave (the alcoves alone may hold few)
            if (o.extraFinds > 0)
            {
                int RockN((int, int) q) => N4.Count(d => !open.Contains((q.Item1 + d.Item1, q.Item2 + d.Item2)));
                var taken = codes.Where(kv => finds.Any(f => f.Item2 == kv.Value)).Select(kv => kv.Key).ToList();
                int added = 0;
                foreach (var q in cells.Where(q => Free(q.Item1, q.Item2) && !NearX(q.Item1, q.Item2) && RockN(q) >= 1).OrderBy(_ => rnd.Next()).ToList())
                {
                    if (added >= o.extraFinds) break;
                    if (taken.Any(t => Math.Abs(t.Item1 - q.Item1) + Math.Abs(t.Item2 - q.Item2) < 7) || Cuts(q)) continue;
                    var (piece, code) = finds[fi++ % finds.Length];
                    var (c, r) = q;
                    plist.Add(new JArray(piece, IG * (c + 0.5f), IG * (r + 0.5f), rnd.Next(4) * 90, null, null, NH.DeepClone()));
                    codes[q] = code;
                    taken.Add(q);
                    added++;
                    if (!piece.StartsWith("Overlay_"))
                        markers.Add(new JObject
                        {
                            ["id"] = $"loot{markers.Count}", ["role"] = "loot", ["at"] = new JArray(IG * (c + 0.5f), IG * (r + 0.5f)), ["note"] = piece,
                        });
                }
            }
            var pits = new JArray();
            var used = new List<(int, int)>();
            var cand = cells.Where(p => Enumerable.Range(-1, 4).All(a => Enumerable.Range(-1, 4).All(b => Free(p.Item1 + a, p.Item2 + b))) &&
                                        !new[] { (0, 0), (1, 0), (0, 1), (1, 1) }.Any(d => NearX(p.Item1 + d.Item1, p.Item2 + d.Item2)))
                            .OrderBy(_ => rnd.Next()).ToList();
            foreach (var (c, r) in cand)
            {
                if (pits.Count >= o.pools) break;
                var blk = new[] { (c, r), (c + 1, r), (c, r + 1), (c + 1, r + 1) };
                if (blk.Any(q => used.Any(u => Math.Abs(q.Item1 - u.Item1) < 4 && Math.Abs(q.Item2 - u.Item2) < 4))) continue;
                pits.Add(new JArray("Pit_Pool_300x300", IG * c, IG * r));
                foreach (var q in blk) { codes[q] = "~~"; used.Add(q); }
            }
            var kinds = Pairs(o.dressing, new[] { ("Crystals", "CR"), ("Mushrooms_Glow", "MG"), ("Stalagmites", "SM"), ("Boulders", "BD"), ("Overlay_Gravel", "gv"),
                                                ("Crystals", "CR"), ("Stalagmites", "SM"), ("Mushrooms_Glow", "MG") });
            // any free cell off the chasm's lip: against a tunnel wall too, as Cuts keeps the way past it two cells wide
            var spots = cells.Where(p => Free(p.Item1, p.Item2) && !NearX(p.Item1, p.Item2)).OrderBy(_ => rnd.Next()).ToList();
            var placedAt = new List<(int, int)>();
            foreach (var (c, r) in spots)
            {
                if (placedAt.Count >= o.props) break;
                if (placedAt.Any(u => Math.Abs(c - u.Item1) + Math.Abs(r - u.Item2) < 4) || Cuts((c, r))) continue;
                var (piece, code) = kinds[placedAt.Count % kinds.Length];
                plist.Add(new JArray(piece, IG * (c + 0.5f), IG * (r + 0.5f), 0, null, null, NH.DeepClone()));
                codes[(c, r)] = code;
                placedAt.Add((c, r));
            }
            var encounters = Encounters(o, nc, nr, rnd, open, xs, deckAt, codes, portals, poiAt);
            var R = new JObject
            {
                ["building"] = "Dungeon", ["floor"] = -9, ["preset"] = "Cavern",
                ["family"] = new JObject { ["perimeter"] = "Cave", ["partition"] = "Cave" },
                ["cave"] = true, ["pools"] = false,
                ["zones"] = new JObject { ["cavern"] = new JObject { ["cells"] = "rest", ["floor"] = "CaveFloor" } },
                ["tunnels"] = tunnels, ["links"] = links, ["pits"] = pits, ["props"] = plist,
                ["portals"] = new JArray(portals.Select(pt => pt.ToJson())),
                ["debris"] = new JObject { ["density"] = o.debris, ["seed"] = o.seed },
                ["generated"] = new JObject { ["generator"] = "cave", ["layout"] = o.layout, ["seed"] = o.seed, ["nc"] = nc, ["nr"] = nr },
            };
            if (encounters.Count > 0) R["encounters"] = encounters;
            if (markers.Count > 0) R["markers"] = markers;
            return (MakePlan(nc, nr, codes), R);
        }

        /// <summary>encounters (record "encounters", built as KitEncounter markers): centres spread over the free floor at
        /// least six steps from the way in (the first portal, the tunnels, else the middle), the point of interest's the
        /// boss's; each with up to six spawn points round it, its budget growing with the walk from the way in</summary>
        static JArray Encounters(Options o, int nc, int nr, System.Random rnd, HashSet<(int, int)> open, HashSet<(int, int)> xs,
                                 Dictionary<(int, int), bool> decks, Dictionary<(int, int), string> codes, List<KitPortal> portals, (int, int)? poiAt)
        {
            var list = new JArray();
            if (string.IsNullOrEmpty(o.creature) || o.encounters <= 0) return list;
            var stand = new HashSet<(int, int)>(open.Where(q => !xs.Contains(q) || decks.ContainsKey(q)));
            var from = portals.Count > 0 ? portals[0].Row(0, nc, nr).ToList() : codes.Where(kv => kv.Value == "Sx").Select(kv => kv.Key).ToList();
            from = from.Where(stand.Contains).ToList();
            if (from.Count == 0 && stand.Count > 0) from.Add(stand.OrderBy(q => Math.Abs(q.Item1 - nc / 2) + Math.Abs(q.Item2 - nr / 2)).First());
            var dist = new Dictionary<(int, int), int>();
            var queue = new Queue<(int, int)>();
            foreach (var q in from) { dist[q] = 0; queue.Enqueue(q); }
            while (queue.Count > 0)
            {
                var (c, r) = queue.Dequeue();
                foreach (var (dc, dr) in N4)
                {
                    var q = (c + dc, r + dr);
                    if (stand.Contains(q) && !dist.ContainsKey(q)) { dist[q] = dist[(c, r)] + 1; queue.Enqueue(q); }
                }
            }
            if (dist.Count == 0) return list;
            int far = Mathf.Max(1, dist.Values.Max());
            // the creatures from the way in to the deep end: each encounter takes the one for its share of the walk
            var kinds = o.creature.Split(',').Select(c => c.Trim()).Where(c => c.Length > 0).ToArray();
            string CreatureAt(int d) => kinds[Mathf.Min(kinds.Length - 1, kinds.Length * d / (far + 1))];
            bool Floor((int, int) q) => dist.ContainsKey(q) && !codes.ContainsKey(q);
            int Gap((int, int) a, (int, int) b) => Math.Abs(a.Item1 - b.Item1) + Math.Abs(a.Item2 - b.Item2);
            var centres = new List<((int, int) at, bool boss)>();
            if (poiAt != null) centres.Add((poiAt.Value, true));
            var cand = dist.Keys.Where(q => Floor(q) && dist[q] >= 6).ToList();
            while (centres.Count < o.encounters + (poiAt != null ? 1 : 0) && cand.Count > 0)
            {
                var best = cand.OrderByDescending(q => centres.Count == 0 ? dist[q] : centres.Min(c => Gap(c.at, q))).ThenBy(_ => rnd.Next()).First();
                if (centres.Count > 0 && centres.Min(c => Gap(c.at, best)) < 5) break;          // the cave is full
                centres.Add((best, false));
            }
            int k = 0;
            foreach (var (at, boss) in centres)
            {
                int d = dist.TryGetValue(at, out var dd) ? dd : far;
                int budget = 1 + Mathf.RoundToInt(4f * d / far) + (boss ? 3 : 0);
                var near = dist.Keys.Where(q => Floor(q) && Math.Max(Math.Abs(q.Item1 - at.Item1), Math.Abs(q.Item2 - at.Item2)) <= 3).ToList();
                if (near.Count == 0) continue;
                var pts = new List<(int, int)> { near.OrderBy(q => Gap(q, at)).First() };
                while (pts.Count < Mathf.Min(near.Count, Mathf.Min(6, 1 + budget)))
                    pts.Add(near.OrderByDescending(q => pts.Min(p => Gap(p, q))).First());
                int c0 = Mathf.Max(0, pts.Min(p => p.Item1) - 1), c1 = Mathf.Min(nc - 1, pts.Max(p => p.Item1) + 1);
                int r0 = Mathf.Max(0, pts.Min(p => p.Item2) - 1), r1 = Mathf.Min(nr - 1, pts.Max(p => p.Item2) + 1);
                list.Add(new JObject
                {
                    ["id"] = $"cave{k++}", ["room"] = boss ? "lair" : "cave", ["creature"] = boss ? "boss" : CreatureAt(d), ["budget"] = budget,
                    ["boss"] = boss, ["depth"] = d, ["box"] = new JArray(IG * c0, IG * r0, IG * (c1 + 1), IG * (r1 + 1)),
                    ["points"] = new JArray(pts.Select(q => new JArray(IG * (q.Item1 + 0.5f), IG * (q.Item2 + 0.5f)))),
                });
            }
            return list;
        }

        // ------------------------------------------------------------------ layouts
        /// <summary>a maze: nodes on a jittered lattice (chambers or junctions) joined by winding tunnels along a randomised
        /// depth-first spanning tree of the lattice (corridors, turns, dead-end leaves) plus some loops, spurs into the rock;
        /// the walls roughened and smoothed shut (never opened, so the rock between tunnels stands)</summary>
        static HashSet<(int, int)> MazeCave(Options o, int nc, int nr, System.Random rnd, List<(int, int)> cells, List<(int, int)> alcoves)
        {
            var open = new HashSet<(int, int)>();
            var carved = new HashSet<(int, int)>();
            bool In(int c, int r) => c >= 1 && c < nc - 1 && r >= 1 && r < nr - 1;          // a rock frame round the map
            void Carve((int, int) p) { if (In(p.Item1, p.Item2)) { open.Add(p); carved.Add(p); } }
            void Disc(float x, float y, float rad)
            {
                for (int c = Mathf.FloorToInt(x - rad - 1); c <= Mathf.CeilToInt(x + rad + 1); c++)
                    for (int r = Mathf.FloorToInt(y - rad - 1); r <= Mathf.CeilToInt(y + rad + 1); r++)
                        if ((c + 0.5f - x) * (c + 0.5f - x) + (r + 0.5f - y) * (r + 0.5f - y) <= rad * rad) Carve((c, r));
            }
            // the lattice: about one node per 6 x 6 cells (o.chambers scales it), each jittered
            float spacing = Mathf.Clamp(6f * Mathf.Sqrt(2f / Mathf.Max(0.3f, o.chambers)), 4f, 10f);
            int gx = Mathf.Max(2, Mathf.RoundToInt((nc - 2) / spacing)), gy = Mathf.Max(2, Mathf.RoundToInt((nr - 2) / spacing));
            float sx = (nc - 2f) / gx, sy = (nr - 2f) / gy;
            var node = new Vector2[gx, gy];
            var room = new bool[gx, gy];
            for (int i = 0; i < gx; i++)
                for (int j = 0; j < gy; j++)
                {
                    node[i, j] = new Vector2(1 + sx * (i + 0.5f + ((float)rnd.NextDouble() - 0.5f) * 0.45f),
                                             1 + sy * (j + 0.5f + ((float)rnd.NextDouble() - 0.5f) * 0.45f));
                    room[i, j] = rnd.NextDouble() < 0.55;
                }
            // a randomised depth-first spanning tree of the lattice: the maze
            var treeEdges = new HashSet<((int, int), (int, int))>();
            var seen = new HashSet<(int, int)> { (0, 0) };
            var stack = new Stack<(int, int)>();
            stack.Push((0, 0));
            while (stack.Count > 0)
            {
                var (i, j) = stack.Peek();
                var next = N4.Select(d => (i + d.Item1, j + d.Item2)).Where(q => q.Item1 >= 0 && q.Item1 < gx && q.Item2 >= 0 && q.Item2 < gy && !seen.Contains(q))
                             .OrderBy(_ => rnd.Next()).ToList();
                if (next.Count == 0) { stack.Pop(); continue; }
                var q2 = next[0];
                seen.Add(q2);
                treeEdges.Add(((i, j), q2));
                stack.Push(q2);
            }
            var edges = treeEdges.ToList();
            for (int i = 0; i < gx; i++)                                    // loops: some of the lattice links the tree left out
                for (int j = 0; j < gy; j++)
                    foreach (var q in new[] { (i + 1, j), (i, j + 1) })
                    {
                        if (q.Item1 >= gx || q.Item2 >= gy) continue;
                        if (treeEdges.Contains(((i, j), q)) || treeEdges.Contains((q, (i, j)))) continue;
                        if (rnd.NextDouble() < o.loops * 0.6) edges.Add(((i, j), q));
                    }
            var degree = new Dictionary<(int, int), int>();
            foreach (var (a, b) in edges) { degree[a] = degree.TryGetValue(a, out var x) ? x + 1 : 1; degree[b] = degree.TryGetValue(b, out var y) ? y + 1 : 1; }
            // the nodes: chambers with a noisy outline, junctions a small widening
            for (int i = 0; i < gx; i++)
                for (int j = 0; j < gy; j++)
                {
                    var n = node[i, j];
                    if (!room[i, j]) { Disc(n.x, n.y, 1.2f); continue; }
                    float rx = 1.5f + (float)rnd.NextDouble() * Mathf.Min(1.1f, sx * 0.5f - 2.2f), ry = 1.4f + (float)rnd.NextDouble() * Mathf.Min(0.9f, sy * 0.5f - 2.2f);
                    foreach (var (c, r) in cells)
                    {
                        float dx = (c + 0.5f - n.x) / rx, dy = (r + 0.5f - n.y) / ry;
                        if (dx * dx + dy * dy < 1f + 0.6f * (VNoise(c * 0.6f, r * 0.6f, o.seed + 17) - 0.5f)) Carve((c, r));
                    }
                }
            int walkId = 0;
            void Walk(Vector2 from, Vector2 to, bool spur)
            {
                walkId++;
                var p = from;
                float wobble = 1.8f + (float)rnd.NextDouble() * 1.0f;
                for (int step = 0; step < 400 && (to - p).magnitude > 0.8f; step++)
                {
                    float goal = Mathf.Atan2(to.y - p.y, to.x - p.x);
                    float ang = goal + (VNoise(step * 0.2f, walkId * 3.7f, o.seed + 5) - 0.5f) * wobble;
                    p += new Vector2(Mathf.Cos(ang), Mathf.Sin(ang)) * 0.5f;
                    float w = VNoise(step * 0.09f, walkId * 1.9f, o.seed + 9) > 0.7f ? 1.45f : 1.05f;   // two cells, here and there three
                    Disc(p.x, p.y, w);
                }
                if (spur) { Disc(to.x, to.y, 1.3f); alcoves.Add((Mathf.FloorToInt(to.x), Mathf.FloorToInt(to.y))); }
            }
            foreach (var (a, b) in edges) Walk(node[a.Item1, a.Item2], node[b.Item1, b.Item2], false);
            // the maze's leaves are its dead ends: a junction there becomes an alcove
            for (int i = 0; i < gx; i++)
                for (int j = 0; j < gy; j++)
                    if (degree.TryGetValue((i, j), out var dg) && dg == 1 && !room[i, j])
                        alcoves.Add((Mathf.FloorToInt(node[i, j].x), Mathf.FloorToInt(node[i, j].y)));
            for (int k = 0; k < o.deadEnds; k++)                           // spurs: a short drive into the rock to an alcove
            {
                int i = rnd.Next(gx), j = rnd.Next(gy);
                var n = node[i, j];
                for (int t = 0; t < 20; t++)
                {
                    float ang = (float)(rnd.NextDouble() * Math.PI * 2), len = 3.5f + (float)rnd.NextDouble() * 2.5f;
                    var to = n + new Vector2(Mathf.Cos(ang), Mathf.Sin(ang)) * len;
                    if (to.x < 2.5f || to.y < 2.5f || to.x > nc - 2.5f || to.y > nr - 2.5f) continue;
                    if (Enumerable.Range(-1, 3).Any(a => Enumerable.Range(-1, 3).Any(b => open.Contains((Mathf.FloorToInt(to.x) + a, Mathf.FloorToInt(to.y) + b))))) continue;
                    Walk(n, to, true);
                    break;
                }
            }
            // roughen the walls, then smooth: a cell closes when rock surrounds it (carved cells stay); nothing opens
            foreach (var p in cells.Where(p => !open.Contains(p) && In(p.Item1, p.Item2) && N4.Any(d => open.Contains((p.Item1 + d.Item1, p.Item2 + d.Item2)))).ToList())
                if (rnd.NextDouble() < 0.18) open.Add(p);
            bool Rock(int c, int r) => !In(c, r) || !open.Contains((c, r));
            for (int pass = 0; pass < 2; pass++)
            {
                var next = new HashSet<(int, int)>();
                foreach (var (c, r) in open)
                {
                    int n = 0;
                    for (int dc = -1; dc <= 1; dc++) for (int dr = -1; dr <= 1; dr++) if ((dc != 0 || dr != 0) && Rock(c + dc, r + dr)) n++;
                    if (carved.Contains((c, r)) || n < 5) next.Add((c, r));
                }
                open = next;
            }
            open = TwoWide(open, cells, nc, nr);
            return Largest(open);
        }

        /// <summary>the kit's cellular automaton: random rock (44 %), a passage carved west to east, round chambers</summary>
        static HashSet<(int, int)> OpenCave(int nc, int nr, System.Random rnd, List<(int, int)> cells)
        {
            var rock = cells.ToDictionary(p => p, p => rnd.NextDouble() < 0.44);
            var carved = new HashSet<(int, int)>();
            int y = rnd.Next(nr / 3, 2 * nr / 3 + 1);
            int[] steps = { -1, 0, 0, 1 };
            for (int c = 0; c < nc; c++)
            {
                y = Mathf.Clamp(y + steps[rnd.Next(4)], 2, nr - 3);
                for (int d = -1; d <= 1; d++) carved.Add((c, y + d));
            }
            for (int k = 0; k < Mathf.Max(2, nc * nr / 90); k++)
            {
                double cx = 2 + rnd.NextDouble() * (nc - 5), cy = 2 + rnd.NextDouble() * (nr - 5), rad = 1.6 + rnd.NextDouble() * 1.6;
                foreach (var p in cells) if ((p.Item1 - cx) * (p.Item1 - cx) + ((p.Item2 - cy) * 1.2) * ((p.Item2 - cy) * 1.2) < rad * rad) carved.Add(p);
            }
            foreach (var p in carved) rock[p] = false;
            bool IsRock(int c, int r) => !(c >= 0 && c < nc && r >= 0 && r < nr) || rock[(c, r)];
            for (int pass = 0; pass < 5; pass++)
            {
                var nw = new Dictionary<(int, int), bool>();
                foreach (var (c, r) in cells)
                {
                    int n = 0;
                    for (int dc = -1; dc <= 1; dc++) for (int dr = -1; dr <= 1; dr++) if ((dc != 0 || dr != 0) && IsRock(c + dc, r + dr)) n++;
                    nw[(c, r)] = !carved.Contains((c, r)) && (n >= 5 || (n > 3 && rock[(c, r)]));
                }
                rock = nw;
            }
            return Largest(TwoWide(new HashSet<(int, int)>(cells.Where(p => !rock[p])), cells, nc, nr));
        }

        /// <summary>passages at least two cells wide: an open cell is kept only inside some open 2 x 2 block</summary>
        static HashSet<(int, int)> TwoWide(HashSet<(int, int)> open, List<(int, int)> cells, int nc, int nr)
        {
            for (int pass = 0; pass < 4; pass++)
            {
                var keep = new HashSet<(int, int)>();
                foreach (var (c, r) in open)
                    for (int dc = -1; dc <= 0; dc++)
                        for (int dr = -1; dr <= 0; dr++)
                        {
                            var blk = new[] { (c + dc, r + dr), (c + dc + 1, r + dr), (c + dc, r + dr + 1), (c + dc + 1, r + dr + 1) };
                            if (blk.All(open.Contains)) foreach (var q in blk) keep.Add(q);
                        }
                open = keep;
            }
            return open;
        }

        // ------------------------------------------------------------------ the chasm
        /// <summary>a curve drifting across the map from one side to the other (and a fork off it), its width breathing
        /// between chasmWidth.x and .y; the open cells within half the width of it</summary>
        static HashSet<(int, int)> Chasm(Options o, int nc, int nr, System.Random rnd, HashSet<(int, int)> open, HashSet<(int, int)> banks)
        {
            var pts = new List<(Vector2 p, float w)>();
            var ledge = new List<float>();                                   // per point: the ledge beside it (0, or >= 2 cells)
            int stepNo = 0;
            float ang = 0f;
            Vector2 Run(Vector2 start, Vector2 target, float wScale, int salt, bool untilOut, float maxLen)
            {
                var p = start;
                float baseAng = Mathf.Atan2(target.y - p.y, target.x - p.x), len = 0f;
                if (stepNo == 0 || salt != 0) ang = baseAng;
                while (len < maxLen)
                {
                    float t = (stepNo++) * 0.35f;
                    float goal = Mathf.Atan2(target.y - p.y, target.x - p.x);
                    float turn = (VNoise(t * 0.11f, 0.5f + salt, o.seed + 31) - 0.5f) * 0.5f;
                    ang += turn + Mathf.DeltaAngle(ang * Mathf.Rad2Deg, goal * Mathf.Rad2Deg) * Mathf.Deg2Rad * 0.06f;
                    ang = baseAng + Mathf.Clamp(Mathf.DeltaAngle(baseAng * Mathf.Rad2Deg, ang * Mathf.Rad2Deg) * Mathf.Deg2Rad, -1.1f, 1.1f);
                    p += new Vector2(Mathf.Cos(ang), Mathf.Sin(ang)) * 0.35f;
                    len += 0.35f;
                    // the width breathes: smooth noise, sharpened so it lingers wide or narrow and changes in between
                    float n = Mathf.SmoothStep(0f, 1f, Mathf.SmoothStep(0f, 1f, VNoise(t * 0.07f, 2.5f + salt, o.seed + 41)));
                    pts.Add((p, wScale * Mathf.Lerp(o.chasmWidth.x, o.chasmWidth.y, n)));
                    ledge.Add(VNoise(t * 0.08f, 4.5f + salt, o.seed + 51) > 0.5f ? 2.2f : 0f);
                    if (!untilOut && (target - p).magnitude < 1f) break;
                    if (p.x < -1.5f || p.y < -1.5f || p.x > nc + 1.5f || p.y > nr + 1.5f) break;
                }
                return p;
            }
            bool across = rnd.NextDouble() < nc / (float)(nc + nr);            // the long way: west to east (or south to north)
            float f() => 0.3f + 0.4f * (float)rnd.NextDouble();
            var s = across ? new Vector2(-1f, nr * f()) : new Vector2(nc * f(), -1f);
            var e = across ? new Vector2(nc + 1f, nr * f()) : new Vector2(nc * f(), nr + 1f);
            if (rnd.Next(2) == 0) (s, e) = (e, s);
            // through the cave: a waypoint on open floor in the middle of the map
            var mids = open.Where(q => Mathf.Abs(q.Item1 + 0.5f - nc / 2f) < nc * 0.2f && Mathf.Abs(q.Item2 + 0.5f - nr / 2f) < nr * 0.25f).ToList();
            var mid = mids.Count > 0 ? mids[rnd.Next(mids.Count)] : (nc / 2, nr / 2);
            var m = Run(s, new Vector2(mid.Item1 + 0.5f, mid.Item2 + 0.5f), 1f, 0, false, 400f);
            Run(m, e, 1f, 0, true, 400f);
            if (o.chasmFork && pts.Count > 20)
            {
                var (bp, _) = pts[pts.Count / 3 + rnd.Next(pts.Count / 3)];
                var to = across ? new Vector2(bp.x + (float)(rnd.NextDouble() - 0.5) * nc * 0.4f, rnd.Next(2) == 0 ? -1f : nr + 1f)
                                : new Vector2(rnd.Next(2) == 0 ? -1f : nc + 1f, bp.y + (float)(rnd.NextDouble() - 0.5) * nr * 0.4f);
                Run(bp, to, 0.7f, 7, true, (nc + nr) * 0.5f);
            }
            var xs = new HashSet<(int, int)>();
            for (int cx = 1; cx < nc - 1; cx++)                             // every cell inside the rock frame, rock or floor
                for (int cy = 1; cy < nr - 1; cy++)
                {
                    var c = new Vector2(cx + 0.5f, cy + 0.5f);
                    bool bank = false;
                    for (int k = 0; k < pts.Count; k++)
                    {
                        var (p, w) = pts[k];
                        float d2 = (c - p).sqrMagnitude, hw = w * 0.5f;
                        if (d2 < hw * hw) { xs.Add((cx, cy)); bank = false; break; }
                        if (ledge[k] > 0f && d2 < (hw + ledge[k]) * (hw + ledge[k])) bank = true;
                    }
                    if (bank && !xs.Contains((cx, cy))) banks.Add((cx, cy));
                }
            return xs;
        }

        /// <summary>wherever the chasm cuts the cave in two: a rope bridge over a two-cell narrows, a land bridge over a
        /// one-cell gap, or a wider stretch pinched to two cells round a bridge; floor islands too small to matter become
        /// rock pillars in the chasm</summary>
        static void Cross(HashSet<(int, int)> open, HashSet<(int, int)> xs, List<(int c, int r, bool across)> bridges, System.Random rnd)
        {
            for (int iter = 0; iter < 12; iter++)
            {
                var deckAx = Decks(bridges);
                var deck = new HashSet<(int, int)>(deckAx.Keys);
                var floor = new HashSet<(int, int)>(open.Where(p => !xs.Contains(p) || deck.Contains(p)));
                var regs = Regions(floor, deckAx).OrderByDescending(g => g.Count).ToList();
                foreach (var small in regs.Skip(1).Where(g => g.Count < 6 && !g.Any(deck.Contains)))     // rock pillars in the chasm
                    foreach (var p in small) open.Remove(p);
                regs = regs.Where(g => g.Count >= 6 || g.Any(deck.Contains)).ToList();
                if (regs.Count <= 1) return;
                var main = regs[0];
                var other = new HashSet<(int, int)>(regs.Skip(1).SelectMany(g => g));
                // straight runs of chasm (up to 6 cells) from the main region to another one, along a row or a column
                var cands = new List<(int c, int r, int dc, int dr, int len, bool landings)>();
                foreach (var (c, r) in main)
                    foreach (var (dc, dr) in N4)
                    {
                        int len = 0;
                        var q = (c + dc, r + dr);
                        while (xs.Contains(q) && !deck.Contains(q) && len < 7) { len++; q = (q.Item1 + dc, q.Item2 + dr); }
                        if (len == 0 || len > 6 || !other.Contains(q)) continue;
                        bool landings = main.Contains((c - dc, r - dr)) && other.Contains((q.Item1 + dc, q.Item2 + dr));   // two cells deep
                        // the would-be deck (the run's last two cells) keeps two cells clear of every other bridge's deck, has
                        // chasm on both sides (not floor, which its rails would cut off, nor rock), and its landings no rock
                        // beside them (a rock tile's lobe narrows the way off the deck below an agent's width)
                        if (len >= 2)
                        {
                            var d1 = (c + dc * (len - 1), r + dr * (len - 1)); var d2 = (c + dc * len, r + dr * len);
                            var near = (c + dc * (len - 2), r + dr * (len - 2));
                            bool Side((int, int) p, Func<(int, int), bool> ok) => ok((p.Item1 + dr, p.Item2 + dc)) && ok((p.Item1 - dr, p.Item2 - dc));
                            if (!Side(d1, x => xs.Contains(x) && !deck.Contains(x)) || !Side(d2, x => xs.Contains(x) && !deck.Contains(x)) ||
                                !Side(near, open.Contains) || !Side(q, open.Contains)) continue;
                            if (deck.Any(e => Mathf.Max(Mathf.Abs(e.Item1 - d1.Item1), Mathf.Abs(e.Item2 - d1.Item2)) <= 2 ||
                                              Mathf.Max(Mathf.Abs(e.Item1 - d2.Item1), Mathf.Abs(e.Item2 - d2.Item2)) <= 2)) continue;
                        }
                        cands.Add((c, r, dc, dr, len, landings));
                    }
                if (cands.Count == 0) return;
                // a two-cell narrows with landings first, then a one-cell gap (a land bridge), then the narrowest wide stretch
                var pick = cands.OrderBy(k => k.len == 2 ? 0 : k.len == 1 ? 1 : 1 + k.len).ThenBy(k => k.landings ? 0 : 1).ThenBy(_ => rnd.Next()).First();
                var run = Enumerable.Range(1, pick.len).Select(k => (pick.c + pick.dc * k, pick.r + pick.dr * k)).ToList();
                if (pick.len == 1) { xs.Remove(run[0]); continue; }                  // the chasm pinches shut
                foreach (var p in run.Take(pick.len - 2)) xs.Remove(p);              // a wide stretch narrows to two cells
                var a = run[pick.len - 2]; var b = run[pick.len - 1];
                bridges.Add((Math.Min(a.Item1, b.Item1), Math.Min(a.Item2, b.Item2), pick.dc != 0));
            }
        }

        /// <summary>4-connected regions; a bridge deck cell (`decks`: true if its bridge runs E-W) joins only the cells
        /// along its span, as its rails close the sides</summary>
        static List<HashSet<(int, int)>> Regions(IEnumerable<(int, int)> open, Dictionary<(int, int), bool> decks = null)
        {
            var set = new HashSet<(int, int)>(open);
            var seen = new HashSet<(int, int)>();
            var out_ = new List<HashSet<(int, int)>>();
            foreach (var p in set)
            {
                if (seen.Contains(p)) continue;
                var reg = new HashSet<(int, int)>();
                var todo = new Stack<(int, int)>();
                todo.Push(p); seen.Add(p);
                while (todo.Count > 0)
                {
                    var (c, r) = todo.Pop();
                    reg.Add((c, r));
                    foreach (var q in new[] { (c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1) })
                    {
                        bool ew = q.Item2 == r;
                        if (decks != null && ((decks.TryGetValue((c, r), out var a) && a != ew) || (decks.TryGetValue(q, out var b) && b != ew))) continue;
                        if (set.Contains(q) && seen.Add(q)) todo.Push(q);
                    }
                }
                out_.Add(reg);
            }
            return out_;
        }

        static HashSet<(int, int)> Largest(IEnumerable<(int, int)> open, Dictionary<(int, int), bool> decks = null) =>
            Regions(open, decks).OrderByDescending(g => g.Count).FirstOrDefault() ?? new HashSet<(int, int)>();

        static Dictionary<(int, int), bool> Decks(List<(int c, int r, bool across)> bridges)
        {
            var d = new Dictionary<(int, int), bool>();
            foreach (var (c, r, across) in bridges) { d[(c, r)] = across; d[across ? (c + 1, r) : (c, r + 1)] = across; }
            return d;
        }
    }
}
