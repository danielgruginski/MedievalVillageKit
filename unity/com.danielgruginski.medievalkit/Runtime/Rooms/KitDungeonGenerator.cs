using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// A random dungeon level for <see cref="KitRoom"/>: rooms dug into the rock (a cave map, so the rock between them is
    /// the kit's rock tiles) and joined by corridors two cells wide (a spanning tree plus a few loops). Rooms and
    /// corridors are walled in dressed stone (the walls stand on the grid lines between floor and rock and the rock
    /// tiles behind them are the wall-backed ones); some rooms are natural cave pockets. A stair up where the player
    /// arrives, a stair down in the room farthest from it (the lair). Each room has a theme (guardroom, cells, crypt,
    /// store, shrine, warren, lair) that is written into the plan as furniture codes; torches on the walls; debris on
    /// the floor; an encounter in every room but the first, harder the deeper it lies (record "encounters", built as
    /// <see cref="KitEncounter"/> markers for the game to spawn its monsters on).
    /// </summary>
    public static class KitDungeonGenerator
    {
        [Serializable]
        public class Options
        {
            public int nc = 28, nr = 20, seed = 11, rooms = 8;
            [Tooltip("Dungeon (mixed rooms), Crypt or Warren (goblins in natural caves).")]
            public string theme = "Dungeon";
            [Range(0, 1)] public float pockets = 0.2f;       // share of rooms left as natural cave
            [Range(0, 1)] public float loops = 0.25f;        // extra corridors beyond the spanning tree, per room
            [Range(0, 1)] public float debris = 0.25f;       // debris pieces per free floor cell
        }

        const float IG = 1.5f;

        class Room
        {
            public int id, c0, r0, c1, r1;
            public string type;
            public bool pocket;
            public int depth = -1;
            public int W => c1 - c0 + 1;
            public int H => r1 - r0 + 1;
            public bool Has((int, int) p) => p.Item1 >= c0 && p.Item1 <= c1 && p.Item2 >= r0 && p.Item2 <= r1;
            public (float, float) Centre => (IG * (c0 + c1 + 1) / 2f, IG * (r0 + r1 + 1) / 2f);
        }

        // theme -> furniture codes (code, min, max, place: "wall" along the walls, "mid" in the middle), creature tag
        static readonly Dictionary<string, (string code, int min, int max, string place)[]> Furniture = new Dictionary<string, (string, int, int, string)[]>
        {
            ["guard"] = new[] { ("TB", 1, 1, "mid"), ("ba", 1, 2, "wall"), ("bx", 1, 2, "wall"), ("BR", 1, 1, "wall"), ("CH", 0, 1, "wall") },
            ["cells"] = new[] { ("bd", 1, 2, "wall"), ("bu", 1, 1, "wall"), ("st", 1, 2, "wall"), ("CG", 0, 1, "wall") },
            ["crypt"] = new[] { ("SA", 1, 2, "mid"), ("CF", 1, 2, "wall"), ("ur", 1, 2, "wall"), ("cd", 1, 2, "wall") },
            ["store"] = new[] { ("bx", 2, 3, "wall"), ("ba", 2, 3, "wall"), ("CK", 0, 1, "wall"), ("GR", 0, 1, "wall") },
            ["shrine"] = new[] { ("AI", 1, 1, "wall"), ("BZ", 2, 2, "wall"), ("SG", 0, 2, "wall"), ("cn", 1, 2, "mid") },
            ["warren"] = new[] { ("FP", 1, 1, "mid"), ("br", 2, 3, "wall"), ("lp", 0, 1, "wall"), ("TO", 0, 1, "wall"), ("rf", 1, 1, "wall") },
            ["lair"] = new[] { ("TR", 1, 1, "wall"), ("lp", 1, 2, "wall"), ("gc", 1, 1, "mid"), ("bo", 1, 2, "wall"), ("BZ", 0, 2, "wall") },
        };
        static readonly Dictionary<string, string> Creature = new Dictionary<string, string>
        {
            ["guard"] = "bandit", ["cells"] = "rat", ["crypt"] = "undead", ["store"] = "rat", ["shrine"] = "cultist",
            ["warren"] = "goblin", ["lair"] = "boss",
        };
        static readonly Dictionary<string, (string floor, string wall)> Look = new Dictionary<string, (string, string)>
        {
            ["guard"] = ("DungeonFlag", "DungeonIn"), ["cells"] = ("DungeonFlag", "DungeonInDamp"), ["crypt"] = ("AncientFlag", "AncientIn"),
            ["store"] = ("DungeonFlagWarm", "DungeonInWarm"), ["shrine"] = ("AncientFlag", "AncientIn"), ["warren"] = ("CaveFloor", null),
            ["lair"] = ("DungeonFlag", "DungeonIn"),
        };
        static readonly string[] DebrisDungeon = { "Overlay_Debris_Rocks_A", "Overlay_Debris_Rocks_B", "Overlay_Debris_Rocks_C", "Overlay_Debris_Pottery_A",
                                                  "Overlay_Debris_Pottery_B", "Overlay_Debris_Pottery_C", "Overlay_Debris_Rags", "Overlay_Debris_Sack", "Overlay_Bones", "Overlay_Puddle" };
        static readonly string[] DebrisCrypt = { "Overlay_Bones", "Overlay_Debris_Masonry_A", "Overlay_Debris_Masonry_B", "Overlay_Debris_Rubble", "Overlay_Debris_Pottery_B", "Overlay_Debris_Rocks_A" };
        static readonly string[] DebrisCave = { "Overlay_Debris_Rocks_A", "Overlay_Debris_Rocks_B", "Overlay_Debris_Rocks_C", "Overlay_Debris_Stalactite", "Overlay_Gravel", "Overlay_Bones", "Overlay_Debris_Rags" };

        /// <summary>-> the plan and the room record. `fp` gives a code's footprint in cells (w, d) when known.</summary>
        public static (string plan, JObject record) Generate(Options o, Func<string, (int, int)> fp = null)
        {
            var rnd = new System.Random(o.seed);
            int nc = Mathf.Max(12, o.nc), nr = Mathf.Max(10, o.nr);
            fp ??= _ => (1, 1);

            // ---- rooms: random rectangles, two rock cells apart, a rock ring round the map
            var rooms = new List<Room>();
            for (int tries = 0; tries < 400 && rooms.Count < o.rooms; tries++)
            {
                int w = rnd.Next(3, 7), h = rooms.Count < 2 ? rnd.Next(4, 6) : rnd.Next(3, 6);   // the first two can take a stair
                int c0 = rnd.Next(1, nc - w), r0 = rnd.Next(1, nr - h);
                if (c0 + w > nc - 1 || r0 + h > nr - 1) continue;
                var rm = new Room { id = rooms.Count, c0 = c0, r0 = r0, c1 = c0 + w - 1, r1 = r0 + h - 1 };
                if (rooms.Any(q => rm.c0 <= q.c1 + 3 && q.c0 <= rm.c1 + 3 && rm.r0 <= q.r1 + 3 && q.r0 <= rm.r1 + 3)) continue;
                rooms.Add(rm);
            }
            var open = new HashSet<(int, int)>();
            foreach (var rm in rooms) for (int c = rm.c0; c <= rm.c1; c++) for (int r = rm.r0; r <= rm.r1; r++) open.Add((c, r));

            // ---- corridors: a spanning tree (Prim, Manhattan between centres) plus loops; L-shaped, two cells wide
            var edges = new List<(int, int)>();
            var inTree = new HashSet<int> { 0 };
            float Dist(Room a, Room b) => Mathf.Abs(a.Centre.Item1 - b.Centre.Item1) + Mathf.Abs(a.Centre.Item2 - b.Centre.Item2);
            while (inTree.Count < rooms.Count)
            {
                var best = (from a in inTree from b in Enumerable.Range(0, rooms.Count) where !inTree.Contains(b)
                            orderby Dist(rooms[a], rooms[b]) select (a, b)).First();
                edges.Add(best); inTree.Add(best.b);
            }
            int extra = Mathf.RoundToInt(rooms.Count * o.loops);
            var pairs = (from a in Enumerable.Range(0, rooms.Count) from b in Enumerable.Range(0, rooms.Count)
                         where a < b && !edges.Contains((a, b)) && !edges.Contains((b, a)) orderby Dist(rooms[a], rooms[b]) select (a, b)).Take(extra * 2).ToList();
            foreach (var p in pairs.OrderBy(_ => rnd.Next()).Take(extra)) edges.Add(p);
            var corridor = new HashSet<(int, int)>();
            void Brush(int c, int r)
            {
                for (int a = 0; a < 2; a++)
                    for (int b = 0; b < 2; b++)
                    {
                        var q = (Mathf.Clamp(c + a, 1, nc - 2), Mathf.Clamp(r + b, 1, nr - 2));
                        if (open.Add(q)) corridor.Add(q);
                    }
            }
            foreach (var (a, b) in edges)
            {
                var A = rooms[a]; var B = rooms[b];
                int ax = (A.c0 + A.c1) / 2, ay = (A.r0 + A.r1) / 2, bx = (B.c0 + B.c1) / 2, by = (B.r0 + B.r1) / 2;
                bool xFirst = rnd.Next(2) == 0;
                int cx = ax, cy = ay;
                void Walk(int tx, int ty) { while (cx != tx || cy != ty) { Brush(cx, cy); if (cx != tx) cx += Math.Sign(tx - cx); else cy += Math.Sign(ty - cy); } Brush(cx, cy); }
                if (xFirst) { Walk(bx, ay); Walk(bx, by); } else { Walk(ax, by); Walk(bx, by); }
            }
            // no checkerboard pinches (open cells meeting at a corner only): open one rock cell of each
            for (bool again = true; again;)
            {
                again = false;
                for (int c = 1; c < nc - 2; c++)
                    for (int r = 1; r < nr - 2; r++)
                    {
                        bool a = open.Contains((c, r)), b = open.Contains((c + 1, r)), d = open.Contains((c, r + 1)), e = open.Contains((c + 1, r + 1));
                        if ((a && e && !b && !d) || (b && d && !a && !e)) { var q = a ? (c + 1, r) : (c, r); open.Add(q); corridor.Add(q); again = true; }
                    }
            }
            Room RoomOf((int, int) p) => rooms.FirstOrDefault(rm => rm.Has(p));

            // ---- room graph depth from the start (the room of the first edge's root: the largest room in the west half)
            var start = rooms.Where(rm => rm.H >= 4).OrderBy(rm => rm.Centre.Item1 + rm.Centre.Item2 * 0.5f).First();
            var adj = rooms.ToDictionary(rm => rm.id, _ => new List<int>());
            foreach (var (a, b) in edges) { adj[a].Add(b); adj[b].Add(a); }
            start.depth = 0;
            var queue = new Queue<int>(); queue.Enqueue(start.id);
            while (queue.Count > 0) { int a = queue.Dequeue(); foreach (var b in adj[a]) if (rooms[b].depth < 0) { rooms[b].depth = rooms[a].depth + 1; queue.Enqueue(b); } }
            var exitRoom = rooms.Where(rm => rm != start && rm.H >= 4).OrderByDescending(rm => rm.depth).ThenByDescending(rm => rm.W * rm.H).FirstOrDefault()
                           ?? rooms.Where(rm => rm != start).OrderByDescending(rm => rm.depth).First();

            // ---- themes
            string[] pool = o.theme == "Crypt" ? new[] { "crypt", "crypt", "shrine", "store", "cells" }
                          : o.theme == "Warren" ? new[] { "warren", "warren", "store", "cells", "warren" }
                          : new[] { "guard", "cells", "crypt", "store", "shrine", "warren" };
            foreach (var rm in rooms) rm.type = pool[rnd.Next(pool.Length)];
            start.type = o.theme == "Warren" ? "store" : "guard";
            exitRoom.type = "lair";
            foreach (var rm in rooms) rm.pocket = rm.type == "warren" || (rm != start && rm != exitRoom && rnd.NextDouble() < o.pockets);
            if (o.theme == "Warren") foreach (var rm in rooms) rm.pocket = true;

            // ---- walls on the grid lines: floor | rock, and room | corridor (doors and gaps)
            bool IsRock(int c, int r) => !open.Contains((c, r));
            char Height(int c, int r)          // vki_cave_cells: the rock behind a wall
            {
                bool south = r <= 0;
                return south || !IsRock(c, r + 1) || !IsRock(c, r + 2) ? 'C' : 'F';
            }
            bool Natural((int, int) p) => RoomOf(p)?.pocket ?? (o.theme == "Warren");     // pockets and a warren's tunnels: bare rock
            var ew = new Dictionary<(int, int), string>();       // (i, j): segment (i, j)..(i + 1, j), between cells (i, j - 1) and (i, j)
            var ns = new Dictionary<(int, int), string>();       // (i, r): segment (i, r)..(i, r + 1), between cells (i - 1, r) and (i, r)
            var doorCells = new HashSet<(int, int)>();
            var runs = new Dictionary<(int, string, int), List<(int, int)>>();   // room, side, line -> segments touching corridor
            for (int j = 1; j < nr; j++)
                for (int i = 0; i < nc; i++)
                {
                    var s = (i, j - 1); var n = (i, j);
                    bool so = open.Contains(s), no = open.Contains(n);
                    if (so == no)
                    {
                        if (so && RoomOf(s) != RoomOf(n) && (RoomOf(s) != null || RoomOf(n) != null))
                        {
                            var rm = RoomOf(s) ?? RoomOf(n);
                            if (!rm.pocket) Run(runs, (rm.id, RoomOf(s) == rm ? "N" : "S", j), (i, j));
                        }
                        continue;
                    }
                    var fl = so ? s : n;
                    if (Natural(fl)) continue;
                    ew[(i, j)] = no ? "==" : (Height(i, j) == 'F' ? "##" : "==");      // rock south of the floor is always Cut
                }
            for (int i = 1; i < nc; i++)
                for (int r = 0; r < nr; r++)
                {
                    var w = (i - 1, r); var e = (i, r);
                    bool wo = open.Contains(w), eo = open.Contains(e);
                    if (wo == eo)
                    {
                        if (wo && RoomOf(w) != RoomOf(e) && (RoomOf(w) != null || RoomOf(e) != null))
                        {
                            var rm = RoomOf(w) ?? RoomOf(e);
                            if (!rm.pocket) Run(runs, (rm.id, RoomOf(w) == rm ? "E" : "W", i), (i, r));
                        }
                        continue;
                    }
                    var fl = wo ? w : e; var rk = wo ? e : w;
                    if (Natural(fl)) continue;
                    ns[(i, r)] = Height(rk.Item1, rk.Item2) == 'F' ? "#" : ":";
                }
            // a room's segments facing a corridor: each run gets one door, or stays open (a gap) when short
            foreach (var kv in runs)
            {
                var (rid, side, line) = kv.Key;
                var segsAlong = kv.Value.OrderBy(q => side == "N" || side == "S" ? q.Item1 : q.Item2).ToList();
                var groups = new List<List<(int, int)>>();
                foreach (var q in segsAlong)
                {
                    var last = groups.LastOrDefault();
                    var prev = last?.Last();
                    bool next = prev != null && ((side == "N" || side == "S") ? q.Item1 == prev.Value.Item1 + 1 : q.Item2 == prev.Value.Item2 + 1);
                    if (next) last.Add(q); else groups.Add(new List<(int, int)> { q });
                }
                foreach (var g in groups)
                {
                    bool gap = g.Count <= 2 && rnd.NextDouble() < 0.35;
                    int di = g.Count / 2;
                    for (int k = 0; k < g.Count; k++)
                    {
                        var q = g[k];
                        if (gap) continue;                                       // no wall: the room opens on the corridor
                        bool door = k == di;
                        if (side == "N" || side == "S") ew[q] = door ? "dd" : "==";
                        else ns[q] = door ? "d" : "#";
                        if (door)
                        {
                            var rm = rooms[rid];
                            var cell = side == "N" ? (q.Item1, q.Item2 - 1) : side == "S" ? (q.Item1, q.Item2) : side == "E" ? (q.Item1 - 1, q.Item2) : (q.Item1, q.Item2);
                            doorCells.Add(cell);
                        }
                    }
                    if (gap)
                        foreach (var q in g)
                            doorCells.Add(side == "N" ? (q.Item1, q.Item2 - 1) : side == "S" ? (q.Item1, q.Item2) : side == "E" ? (q.Item1 - 1, q.Item2) : (q.Item1, q.Item2));
                }
            }

            // ---- stairs: up in the start room, down in the lair, against the west or east wall, top at the north wall
            var codes = new Dictionary<(int, int), string>();
            foreach (var (c, r) in Enumerable.Range(0, nc).SelectMany(c => Enumerable.Range(0, nr).Select(r => (c, r))))
                if (!open.Contains((c, r))) codes[(c, r)] = "##";
            var reserved = new HashSet<(int, int)>(doorCells);
            foreach (var d in doorCells) foreach (var q in new[] { (d.Item1 + 1, d.Item2), (d.Item1 - 1, d.Item2), (d.Item1, d.Item2 + 1), (d.Item1, d.Item2 - 1) }) reserved.Add(q);
            var stairs = new JArray();
            var stairCells = new HashSet<(int, int)>();
            JArray Stair(Room rm, string kind, string lid)
            {
                foreach (var c in kind == "Up" ? new[] { rm.c0, rm.c1 } : new[] { rm.c0 })
                {
                    var cells = Enumerable.Range(rm.r1 - 2, 3).Select(r => (c, r)).ToList();
                    var front = kind == "Up" ? (c, rm.r1 - 3) : (c + 1, rm.r1);
                    if (cells.Concat(new[] { front }).Any(reserved.Contains) || !rm.Has(front)) continue;
                    foreach (var q in cells) { reserved.Add(q); stairCells.Add(q); codes[q] = kind == "Up" ? "^^" : "vv"; }
                    reserved.Add(front); codes[front] = "Ss";
                    return new JArray(kind, IG * c, IG * (rm.r1 - 2), 0, lid, "Stone");
                }
                return null;
            }
            var up = Stair(start, "Up", "up");
            var down = Stair(exitRoom, "Down", "down");
            if (up != null) stairs.Add(up);
            if (down != null) stairs.Add(down);
            // the stair codes are a view only (the record's stairs are the source): clear them for the furniture
            foreach (var q in codes.Where(kv => kv.Value == "^^" || kv.Value == "vv").Select(kv => kv.Key).ToList()) codes[q] = "..";

            // ---- furniture codes, torches, debris, encounters
            var props = new JArray();
            var encounters = new JArray();
            var NH = new JObject { ["hug"] = false };
            foreach (var rm in rooms)
            {
                var cells = Enumerable.Range(rm.c0, rm.W).SelectMany(c => Enumerable.Range(rm.r0, rm.H).Select(r => (c, r))).ToList();
                bool Edge((int, int) p) => p.Item1 == rm.c0 || p.Item1 == rm.c1 || p.Item2 == rm.r0 || p.Item2 == rm.r1;
                bool Free((int, int) p) => rm.Has(p) && !reserved.Contains(p) && (!codes.TryGetValue(p, out var cc) || cc == "..");
                KitFurnisher.Place(rnd, rm.c0, rm.r0, rm.c1, rm.r1, Furniture[rm.type], codes, reserved, doorCells, stairCells, fp);
                // torches: on the north wall of walled rooms, every third cell (pockets glow with mushrooms instead)
                if (!rm.pocket)
                    for (int c = rm.c0 + 1; c <= rm.c1 - 1; c += 3)
                        if (ew.TryGetValue((c, rm.r1 + 1), out var t) && t == "##")
                            props.Add(new JArray("Torch_Wall", IG * (c + 0.5f), IG * (rm.r1 + 0.5f), 0, null, "wall_hung"));
                if (rm.pocket)
                    foreach (var q in cells.Where(q => Edge(q) && Free(q)).OrderBy(_ => rnd.Next()).Take(Mathf.Max(1, cells.Count / 10)))
                        codes[q] = "MG";
                // debris
                var pile = rm.type == "crypt" || rm.type == "shrine" ? DebrisCrypt : rm.pocket ? DebrisCave : DebrisDungeon;
                foreach (var q in cells.Where(q => Free(q) && !doorCells.Contains(q)))
                    if (rnd.NextDouble() < o.debris)
                        props.Add(new JArray(pile[rnd.Next(pile.Length)], IG * (q.Item1 + 0.2f + 0.6f * (float)rnd.NextDouble()),
                                             IG * (q.Item2 + 0.2f + 0.6f * (float)rnd.NextDouble()), rnd.Next(24) * 15, null, null, NH.DeepClone()));
                // the encounter: every room but the start, deeper is harder; spawn points spread over its free cells
                if (rm != start)
                {
                    int budget = 1 + Mathf.Max(0, rm.depth) + (rm == exitRoom ? 3 : 0);
                    var free = cells.Where(q => Free(q) && !doorCells.Contains(q)).ToList();
                    var pts = new List<(int, int)>();
                    if (free.Count > 0) pts.Add(free[rnd.Next(free.Count)]);
                    while (pts.Count < Mathf.Min(free.Count, Mathf.Min(6, 1 + budget)))
                        pts.Add(free.OrderByDescending(q => pts.Min(p => Mathf.Abs(p.Item1 - q.Item1) + Mathf.Abs(p.Item2 - q.Item2))).First());
                    encounters.Add(new JObject
                    {
                        ["id"] = $"room{rm.id}", ["room"] = rm.type, ["creature"] = Creature[rm.type], ["budget"] = budget, ["boss"] = rm == exitRoom,
                        ["depth"] = rm.depth,
                        ["box"] = new JArray(IG * rm.c0, IG * rm.r0, IG * (rm.c1 + 1), IG * (rm.r1 + 1)),
                        ["points"] = new JArray(pts.Select(q => new JArray(IG * (q.Item1 + 0.5f), IG * (q.Item2 + 0.5f)))),
                    });
                }
            }
            // corridors: torches on Full walls every fourth cell, a little debris
            foreach (var q in corridor.Where(q => RoomOf(q) == null).OrderBy(q => q.Item1).ThenBy(q => q.Item2))
            {
                if ((q.Item1 + 2 * q.Item2) % 5 == 0 && ew.TryGetValue((q.Item1, q.Item2 + 1), out var t) && t == "##")
                    props.Add(new JArray("Torch_Wall", IG * (q.Item1 + 0.5f), IG * (q.Item2 + 0.5f), 0, null, "wall_hung"));
                else if (rnd.NextDouble() < o.debris * 0.5)
                    props.Add(new JArray(DebrisDungeon[rnd.Next(DebrisDungeon.Length)], IG * (q.Item1 + 0.2f + 0.6f * (float)rnd.NextDouble()),
                                         IG * (q.Item2 + 0.2f + 0.6f * (float)rnd.NextDouble()), rnd.Next(24) * 15, null, null, NH.DeepClone()));
            }

            // ---- zones: each room (floor and wall styles of its type), the corridors, the rock
            var zones = new JObject();
            foreach (var rm in rooms)
            {
                var (floor, wall) = Look[rm.type];
                if (rm.pocket) { floor = "CaveFloor"; wall = null; }
                var box = new JArray(); box.Add(new JArray(rm.c0, rm.c1, rm.r0, rm.r1));      // new JArray(JArray) would copy, not nest
                var z = new JObject { ["cells"] = box, ["floor"] = floor };
                if (wall != null) z["wall"] = wall;
                zones[$"{rm.type}{rm.id}"] = z;
            }
            zones["corridor"] = new JObject
            {
                ["cells"] = new JArray(corridor.Where(q => RoomOf(q) == null).Select(q => new JArray(q.Item1, q.Item1, q.Item2, q.Item2))),
                ["floor"] = o.theme == "Warren" ? "CaveFloor" : "DungeonFlag", ["wall"] = "DungeonIn"
            };
            zones["rock"] = new JObject { ["cells"] = "rest", ["floor"] = "CaveFloor" };
            var links = new JArray();
            if (up != null) links.Add(new JArray("up", "stair_up", "@return"));
            if (down != null) links.Add(new JArray("down", "stair_down", "@deep"));
            var R = new JObject
            {
                ["building"] = "Dungeon", ["floor"] = -1, ["preset"] = "Dungeon",
                ["family"] = new JObject { ["perimeter"] = "Cave", ["partition"] = "Dungeon" },
                ["cave"] = true, ["pools"] = false, ["rush_mats"] = false, ["partition_wall"] = "zone",
                ["zones"] = zones, ["links"] = links, ["stairs"] = stairs, ["props"] = props, ["props_from_codes"] = true,
                ["encounters"] = encounters,
                ["generated"] = new JObject { ["generator"] = "dungeon", ["seed"] = o.seed, ["nc"] = nc, ["nr"] = nr, ["theme"] = o.theme },
            };
            return (Plan(nc, nr, codes, ew, ns), R);
        }

        static void Run(Dictionary<(int, string, int), List<(int, int)>> runs, (int, string, int) key, (int, int) seg)
        {
            if (!runs.TryGetValue(key, out var l)) runs[key] = l = new List<(int, int)>();
            l.Add(seg);
        }

        /// <summary>vki_rooms_mkplan with wall tokens: ew (i, j) 2 chars, ns (i, r) 1 char; the frame "##" / "==" / "#" / "t"</summary>
        static string Plan(int nc, int nr, Dictionary<(int, int), string> codes, Dictionary<(int, int), string> ew, Dictionary<(int, int), string> ns)
        {
            var sb = new StringBuilder("\n      " + string.Join(" ", Enumerable.Range(0, nc).Select(i => i.ToString().PadLeft(2))) + "\n");
            for (int j = nr; j >= 0; j--)
            {
                sb.Append("     +");
                for (int i = 0; i < nc; i++)
                {
                    string tok = j == nr ? "##" : j == 0 ? "==" : ew.TryGetValue((i, j), out var t) ? t : "  ";
                    sb.Append(tok).Append(j == 0 || j == nr || i == nc - 1 || tok.Trim().Length > 0 ? "+" : " ");
                }
                sb.Append('\n');
                if (j == 0) break;
                int r = j - 1;
                sb.Append("  ").Append(r.ToString().PadLeft(2)).Append(' ');
                for (int i = 0; i <= nc; i++)
                {
                    sb.Append(i == 0 || i == nc ? (r == 0 ? "t" : "#") : ns.TryGetValue((i, r), out var t) ? t : " ");
                    if (i < nc) sb.Append(codes.TryGetValue((i, r), out var c) ? c : "..");
                }
                sb.Append('\n');
            }
            return sb.ToString();
        }
    }
}
