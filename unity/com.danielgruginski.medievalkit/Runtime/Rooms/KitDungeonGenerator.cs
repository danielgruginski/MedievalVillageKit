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
    /// store, shrine, warren, lair) that is written into the plan as furniture codes, with its set-pieces as record props
    /// (<see cref="KitSetPieces"/>: a shrine's altar between guardian statues and braziers, the lair's hoard between
    /// braziers, chains on the cells' walls, the guards' table laid; pillars down the larger rooms); torches on the walls;
    /// debris on the floor; an encounter in every room but the first, harder the deeper it lies (record "encounters",
    /// built as <see cref="KitEncounter"/> markers for the game to spawn its monsters on).
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
            [Range(0, 1)] public float debris = 0.25f;       // loose debris (the kit's scatter by zone theme): share of the open cells
            [Tooltip("Openings on the map's edges into the next map of a chain (KitPortal; the first is the way in). None: a stair up where one arrives, a stair down in the lair.")]
            public List<KitPortal> portals = new List<KitPortal>();
            [Tooltip("With portals: a stair up out of the chain to this scene (e.g. a camp above), in a room far from the way in; empty: none.")]
            public string exit = "";
            [Tooltip("The exit stair's link id (its spawn's id too: where one arrives coming down from the scene above).")]
            public string exitId = "exit";
            [Tooltip("The spawn the exit stair leads to in that scene (empty: KitTravel's rules).")]
            public string exitArrive = "";
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
            ["guard"] = new[] { ("TB", 1, 1, "mid"), ("WR", 0, 1, "wall"), ("ba", 1, 2, "wall"), ("bx", 1, 2, "wall"), ("BR", 1, 1, "wall"), ("CH", 0, 1, "wall"), ("br", 0, 2, "wall") },
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

        /// <summary>-> the plan and the room record. `fp` gives a code's footprint in cells (w, d) when known.</summary>
        public static (string plan, JObject record) Generate(Options o, Func<string, (int, int)> fp = null)
        {
            var rnd = new System.Random(o.seed);
            int nc = Mathf.Max(12, o.nc), nr = Mathf.Max(10, o.nr);
            fp ??= _ => (1, 1);
            var fpIn = fp;
            fp = code => code == "TB" ? (2, 2) : fpIn(code);       // a trestle table and its forms: a 2 x 2 block

            // ---- rooms: random rectangles, two rock cells apart, a rock ring round the map
            var rooms = new List<Room>();
            for (int tries = 0; tries < 400 && rooms.Count < o.rooms; tries++)
            {
                // the first a great hall, the next two can take a stair, the rest anything from a closet to a hall
            int w = rooms.Count == 0 ? rnd.Next(7, 10) : rnd.Next(3, 8);
            int h = rooms.Count == 0 ? rnd.Next(5, 8) : rooms.Count < 3 ? rnd.Next(4, 6) : rnd.Next(3, 6);
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
            // ---- portals (openings on the map's edges into the next map of a chain): a straight way in from the edge in
            // bare rock (no dressed walls where two maps meet), then a corridor on to the nearest floor
            var portals = (o.portals ?? new List<KitPortal>()).Select(pt => KitPortal.FromJson(pt.ToJson())).ToList();
            var approach = new HashSet<(int, int)>();
            foreach (var pt in portals)
            {
                foreach (var q in pt.Carve(nc, nr, x => open.Contains(x), rnd)) if (open.Add(q)) corridor.Add(q);
                for (int d = 0; d < KitPortal.Approach; d++) foreach (var q in pt.Row(d, nc, nr)) approach.Add(q);
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
            // no one-cell necks: every open cell inside some open 2 x 2 block (the rock tiles' lobes close a one-cell gap);
            // a cell short of one opens the rock of its most open block
            for (int pass = 0; pass < 3; pass++)
                foreach (var (c, r) in open.ToList())
                {
                    var blocks = new[] { (c - 1, r - 1), (c, r - 1), (c - 1, r), (c, r) }
                        .Where(b => b.Item1 >= 1 && b.Item2 >= 1 && b.Item1 + 1 <= nc - 2 && b.Item2 + 1 <= nr - 2)
                        .Select(b => new[] { b, (b.Item1 + 1, b.Item2), (b.Item1, b.Item2 + 1), (b.Item1 + 1, b.Item2 + 1) }).ToList();
                    if (blocks.Count == 0 || blocks.Any(bl => bl.All(open.Contains))) continue;
                    foreach (var q in blocks.OrderByDescending(bl => bl.Count(open.Contains)).First())
                        if (open.Add(q)) corridor.Add(q);
                }
            Room RoomOf((int, int) p) => rooms.FirstOrDefault(rm => rm.Has(p));

            // ---- room graph depth from the start (the room of the first edge's root: the largest room in the west half)
            var start = rooms.Where(rm => rm.H >= 4).OrderBy(rm => rm.Centre.Item1 + rm.Centre.Item2 * 0.5f).FirstOrDefault() ?? rooms[0];
            if (portals.Count > 0)                                      // a chained map: one comes in by the first portal
            {
                var way = portals[0].Cell(portals[0].at, 0, nc, nr);
                start = rooms.OrderBy(rm => Mathf.Abs(rm.Centre.Item1 / IG - way.Item1) + Mathf.Abs(rm.Centre.Item2 / IG - way.Item2)).First();
            }
            var adj = rooms.ToDictionary(rm => rm.id, _ => new List<int>());
            foreach (var (a, b) in edges) { adj[a].Add(b); adj[b].Add(a); }
            void Depths(Room s0)
            {
                foreach (var rm in rooms) rm.depth = -1;
                s0.depth = 0;
                var queue = new Queue<int>(); queue.Enqueue(s0.id);
                while (queue.Count > 0) { int a = queue.Dequeue(); foreach (var b in adj[a]) if (rooms[b].depth < 0) { rooms[b].depth = rooms[a].depth + 1; queue.Enqueue(b); } }
            }
            Depths(start);
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
            bool Natural((int, int) p) => approach.Contains(p) || (RoomOf(p)?.pocket ?? (o.theme == "Warren"));     // pockets, a warren's tunnels, portals: bare rock
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
            // a cave pocket has no walls: its ways in are where the tunnels and rooms round it meet its edge, the middle two
            // cells of each such run along a side (kept clear of furniture like doorways, and where the furnisher's
            // reachability check starts)
            foreach (var rm in rooms.Where(q => q.pocket))
                foreach (var (dc, dr) in new[] { (1, 0), (-1, 0), (0, 1), (0, -1) })
                {
                    // the side's cells in order along it, each flagged if the cell beyond is open
                    var side = dc != 0 ? Enumerable.Range(rm.r0, rm.H).Select(r => (dc > 0 ? rm.c1 : rm.c0, r)).ToList()
                                       : Enumerable.Range(rm.c0, rm.W).Select(c => (c, dr > 0 ? rm.r1 : rm.r0)).ToList();
                    var run = new List<(int, int)>();
                    foreach (var q in side.Append((-99, -99)))
                    {
                        if (q.Item1 != -99 && open.Contains((q.Item1 + dc, q.Item2 + dr))) { run.Add(q); continue; }
                        if (run.Count > 0)
                        {
                            doorCells.Add(run[(run.Count - 1) / 2]);
                            if (run.Count >= 2) doorCells.Add(run[run.Count / 2 == (run.Count - 1) / 2 ? run.Count / 2 + 1 : run.Count / 2]);
                        }
                        run.Clear();
                    }
                }
            var reserved = new HashSet<(int, int)>(doorCells);
            foreach (var d in doorCells) foreach (var q in new[] { (d.Item1 + 1, d.Item2), (d.Item1 - 1, d.Item2), (d.Item1, d.Item2 + 1), (d.Item1, d.Item2 - 1) }) reserved.Add(q);
            var stairs = new JArray();
            var stairCells = new HashSet<(int, int)>();
            // a stair: three cells in a line from its foot to its top, along a wall. Up: its top against the wall it runs
            // into, arrival ("Ss") in front of its foot; the corners first (north, up the west or east wall or along the north
            // wall), then anywhere along the north, east or west wall, then the south. Down: a hole along a wall, arrival
            // beside its top on the stair's local +x side (the piece's spawn), so that side faces into the room. The frame
            // (x, y) is the footprint's corner at the foot, on the local -x side (local +y runs foot to top: rot 0 north,
            // -90 east, 90 west, 180 south). Tried in the given room first, then in any other room
            JArray Place(Room rm, string kind, string lid)
            {
                var opts = new List<(List<(int, int)> cells, (int, int) front, float x, float y, float rot, string variant)>();
                void Line((int, int) top, (int, int) d)
                {
                    var foot = (top.Item1 - 2 * d.Item1, top.Item2 - 2 * d.Item2);
                    var side = (d.Item2, -d.Item1);                                  // local +x
                    var front = kind == "Up" ? (foot.Item1 - d.Item1, foot.Item2 - d.Item2) : (top.Item1 + side.Item1, top.Item2 + side.Item2);
                    var cells = new List<(int, int)> { foot, (foot.Item1 + d.Item1, foot.Item2 + d.Item2), top };
                    var (fc, fr) = foot;
                    var (x, y, rot) = d == (0, 1) ? (IG * fc, IG * fr, 0f) : d == (1, 0) ? (IG * fc, IG * (fr + 1), -90f)
                                    : d == (-1, 0) ? (IG * (fc + 1), IG * fr, 90f) : (IG * (fc + 1), IG * (fr + 1), 180f);
                    // the stone flight's wall side is its local -x and its rail side +x: an up flight with the room's edge
                    // (a wall, the rock) on its +x side and floor on its -x side is the left-hand twin, else its rail and
                    // lip stand in the wall or the rock. Down flights keep their wall on -x by the lines below.
                    bool Edge((int, int) s) => cells.Any(q => !rm.Has((q.Item1 + s.Item1, q.Item2 + s.Item2)));
                    bool left = kind == "Up" && Edge(side) && !Edge((-side.Item1, -side.Item2));
                    opts.Add((cells, front, x, y, rot, left ? "StoneL" : "Stone"));
                }
                var N = (0, 1); var E = (1, 0); var W = (-1, 0); var S = (0, -1);
                if (kind == "Up")
                {
                    Line((rm.c0, rm.r1), N); Line((rm.c1, rm.r1), N); Line((rm.c1, rm.r1), E); Line((rm.c0, rm.r1), W);
                    for (int c = rm.c0 + 1; c < rm.c1; c++) Line((c, rm.r1), N);
                    for (int r = rm.r1 - 1; r >= rm.r0; r--) { Line((rm.c1, r), E); Line((rm.c0, r), W); }
                    for (int c = rm.c0; c <= rm.c1; c++) Line((c, rm.r0), S);
                }
                else
                {
                    // north up the west wall, east along the north wall, south down the east wall, west along the south wall
                    Line((rm.c0, rm.r1), N);
                    for (int c = rm.c0 + 2; c <= rm.c1; c++) Line((c, rm.r1), E);
                    for (int r = rm.r1 - 1; r >= rm.r0 + 2; r--) Line((rm.c0, r), N);
                    for (int r = rm.r0; r + 2 <= rm.r1; r++) Line((rm.c1, r), S);
                    for (int c = rm.c0; c + 2 <= rm.c1; c++) Line((c, rm.r0), W);
                }
                foreach (var (cells, front, x, y, rot, variant) in opts)
                {
                    if (!cells.All(rm.Has) || !rm.Has(front) || cells.Concat(new[] { front }).Any(reserved.Contains)) continue;
                    foreach (var q in cells) { reserved.Add(q); stairCells.Add(q); codes[q] = kind == "Up" ? "^^" : "vv"; }
                    reserved.Add(front); codes[front] = "Ss";
                    return new JArray(kind, x, y, rot, lid, variant);
                }
                return null;
            }
            JArray Stair(ref Room rm, string kind, string lid, IEnumerable<Room> others)
            {
                var st = Place(rm, kind, lid);
                if (st != null) return st;
                foreach (var alt in others)
                {
                    st = Place(alt, kind, lid);
                    if (st != null) { rm = alt; return st; }
                }
                return null;
            }
            JArray up = null, down = null;
            if (portals.Count == 0)                                      // a level on its own: stairs are its ways in and out
            {
                var oldStart = start;
                up = Stair(ref start, "Up", "up", rooms.Where(rm => rm != exitRoom).OrderBy(rm => rm.Centre.Item1 + rm.Centre.Item2 * 0.5f));
                if (start != oldStart)                                   // the way in moved: depths and the lair follow it
                {
                    start.type = oldStart.type; oldStart.type = pool[rnd.Next(pool.Length)];
                    Depths(start);
                }
                var oldExit = exitRoom;
                down = Stair(ref exitRoom, "Down", "down", rooms.Where(rm => rm != start).OrderByDescending(rm => rm.depth));
                if (exitRoom != oldExit) { exitRoom.type = "lair"; oldExit.type = pool[rnd.Next(pool.Length)]; }
            }
            JArray exitStair = null;
            if (portals.Count > 0 && !string.IsNullOrEmpty(o.exit))     // a chained map's way out: a stair up, far from the way in
            {
                var at = exitRoom;
                exitStair = Stair(ref at, "Up", o.exitId, rooms.Where(rm => rm != start && rm != exitRoom).OrderByDescending(rm => rm.depth));
            }
            if (up != null) stairs.Add(up);
            if (down != null) stairs.Add(down);
            if (exitStair != null) stairs.Add(exitStair);
            // the stair codes are a view only (the record's stairs are the source): clear them for the furniture
            foreach (var q in codes.Where(kv => kv.Value == "^^" || kv.Value == "vv").Select(kv => kv.Key).ToList()) codes[q] = "..";

            // ---- furniture codes, torches, debris, encounters
            var props = new JArray();
            var encounters = new JArray();
            var NH = new JObject { ["hug"] = false };
            // what stands on a cell's side: 2 a full wall, 1 a cut one, 0 a door, a gap or nothing (pockets: bare rock)
            int WallAt((int, int) q, char sd)
            {
                var (c, r) = q;
                string tok = sd == 'N' ? (ew.TryGetValue((c, r + 1), out var tn) ? tn : null) : sd == 'S' ? (ew.TryGetValue((c, r), out var ts) ? ts : null)
                           : sd == 'W' ? (ns.TryGetValue((c, r), out var tw) ? tw : null) : (ns.TryGetValue((c + 1, r), out var te) ? te : null);
                return tok == "##" || tok == "#" ? 2 : tok == "==" || tok == ":" ? 1 : 0;
            }
            foreach (var rm in rooms)
            {
                var cells = Enumerable.Range(rm.c0, rm.W).SelectMany(c => Enumerable.Range(rm.r0, rm.H).Select(r => (c, r))).ToList();
                bool Edge((int, int) p) => p.Item1 == rm.c0 || p.Item1 == rm.c1 || p.Item2 == rm.r0 || p.Item2 == rm.r1;
                bool Free((int, int) p) => rm.Has(p) && !reserved.Contains(p) && (!codes.TryGetValue(p, out var cc) || cc == "..");
                var area = new KitSetPieces.Area { c0 = rm.c0, r0 = rm.r0, c1 = rm.c1, r1 = rm.r1, codes = codes, reserved = reserved, ways = doorCells, noWalk = stairCells, wall = WallAt };
                var table = Furniture[rm.type].ToList();
                // set-pieces first, the codes' furniture round them, the dressing last
                if (rm.type == "shrine" && !rm.pocket &&
                    KitSetPieces.Shrine(rnd, area, props, rnd.Next(2) == 0 ? "Altar_Idol" : "Altar_300", 2, "Statue_Guardian", "Brazier_Stone"))
                    table.RemoveAll(t => t.code == "AI" || t.code == "BZ" || t.code == "SG");
                if (rm.type == "lair" && !rm.pocket && KitSetPieces.Shrine(rnd, area, props, "Chest_Treasure", 1, "Brazier_Stone", null))
                    table.RemoveAll(t => t.code == "TR" || t.code == "BZ");
                KitFurnisher.Place(rnd, rm.c0, rm.r0, rm.c1, rm.r1, table, codes, reserved, doorCells, stairCells, fp);
                if (rm.type == "guard") KitSetPieces.TableTops(rnd, area, props, new[] { "TableDress_Guard" }, new[] { "TableDress_Guard" }, 1f);
                if (rm.type == "cells" && !rm.pocket) KitSetPieces.WallHung(rnd, area, props, "Chains_Wall", 1 + rnd.Next(3), 2);
                // torches: on the north wall of walled rooms, every third cell (pockets glow with mushrooms instead)
                if (!rm.pocket)
                    for (int c = rm.c0 + 1; c <= rm.c1 - 1; c += 3)
                        if (ew.TryGetValue((c, rm.r1 + 1), out var t) && t == "##")
                            props.Add(new JArray("Torch_Wall", IG * (c + 0.5f), IG * (rm.r1 + 0.5f), 0, null, "wall_hung"));
                if (rm.pocket)
                    foreach (var q in cells.Where(q => Edge(q) && Free(q)).OrderBy(_ => rnd.Next()).Take(Mathf.Max(1, cells.Count / 10)))
                        codes[q] = "MG";
                // pillars down the larger rooms (dressed stone; rock in a pocket), more often in the grander ones
                if (rnd.NextDouble() < (rm.type == "crypt" || rm.type == "shrine" || rm.type == "lair" ? 0.8 : 0.4))
                    KitSetPieces.Pillars(area, props, rm.pocket ? "RockPillar_Cut" : "Pillar_Cut");
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
                        ["id"] = $"room{rm.id}", ["room"] = rm.type, ["creature"] = o.theme == "Warren" && rm.type != "lair" ? "goblin" : Creature[rm.type], ["budget"] = budget, ["boss"] = rm == exitRoom,
                        ["depth"] = rm.depth,
                        ["box"] = new JArray(IG * rm.c0, IG * rm.r0, IG * (rm.c1 + 1), IG * (rm.r1 + 1)),
                        ["points"] = new JArray(pts.Select(q => new JArray(IG * (q.Item1 + 0.5f), IG * (q.Item2 + 0.5f)))),
                    });
                }
            }
            // corridors: torches on Full walls every fifth cell
            foreach (var q in corridor.Where(q => RoomOf(q) == null).OrderBy(q => q.Item1).ThenBy(q => q.Item2))
                if ((q.Item1 + 2 * q.Item2) % 5 == 0 && ew.TryGetValue((q.Item1, q.Item2 + 1), out var t) && t == "##")
                    props.Add(new JArray("Torch_Wall", IG * (q.Item1 + 0.5f), IG * (q.Item2 + 0.5f), 0, null, "wall_hung"));

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
            if (approach.Count > 0)                                     // the ways in from the portals: bare rock, cave floor
                zones["portal"] = new JObject { ["cells"] = new JArray(approach.Select(q => new JArray(q.Item1, q.Item1, q.Item2, q.Item2))), ["floor"] = "CaveFloor" };
            zones["corridor"] = new JObject
            {
                ["cells"] = new JArray(corridor.Where(q => RoomOf(q) == null).Select(q => new JArray(q.Item1, q.Item1, q.Item2, q.Item2))),
                ["floor"] = o.theme == "Warren" ? "CaveFloor" : "DungeonFlag", ["wall"] = "DungeonIn"
            };
            zones["rock"] = new JObject { ["cells"] = "rest", ["floor"] = "CaveFloor" };
            var links = new JArray();
            if (up != null) links.Add(new JArray("up", "stair_up", "@return"));
            if (down != null) links.Add(new JArray("down", "stair_down", "@deep"));
            if (exitStair != null) links.Add(new JArray(o.exitId, "stair_up", o.exit, o.exitArrive));
            var R = new JObject
            {
                ["building"] = "Dungeon", ["floor"] = -1, ["preset"] = "Dungeon",
                ["family"] = new JObject { ["perimeter"] = "Cave", ["partition"] = "Dungeon" },
                ["cave"] = true, ["pools"] = false, ["rush_mats"] = false, ["partition_wall"] = "zone",
                ["zones"] = zones, ["links"] = links, ["stairs"] = stairs, ["props"] = props, ["props_from_codes"] = true,
                ["portals"] = new JArray(portals.Select(pt => pt.ToJson())),
                ["encounters"] = encounters,
                ["debris"] = new JObject { ["density"] = o.debris, ["seed"] = o.seed },   // the kit's scatter by zone theme
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
