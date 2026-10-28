#if TOOLS
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Godot;

namespace MedievalKit.Editor;

/// <summary>
/// Chains of generated maps joined by connectors (<see cref="KitPortal"/>): pieces lined up on their portals (maps are
/// never turned, so a north portal meets a south one), baking a <see cref="KitChain"/> into piece scenes and a play
/// scene, a sample chain, and a walk test across the seams (one navmesh over every piece: the floor must run on from
/// one map into the next). kit_cli: chains sample | bake | validate. Unity: KitChainTools.
/// </summary>
public static class KitChainTools
{
    public class Piece
    {
        public string name;
        public Action<KitRoom> make;       // sets the generator's options (portals included) and generates
        public string inPortal, outPortal; // its portal lined up on the piece it joins; the one a later piece joins by default
        public int attach = -1;            // the piece it joins (an earlier one; -1: the one before)
        public string attachPortal;        // that piece's portal it joins (null: that piece's outPortal)
        public int Parent(int index) => attach >= 0 ? attach : index - 1;
    }

    public static KitPortalMarker Marker(KitRoom room, string id) =>
        KitNodes.Below(room, "").OfType<KitPortalMarker>().FirstOrDefault(m => m.PortalId == id);

    /// <summary>moves `next` so its portal `nextPortal` sits on `prev`'s portal `prevPortal` (both in the tree)</summary>
    public static bool Align(KitRoom prev, string prevPortal, KitRoom next, string nextPortal)
    {
        var a = Marker(prev, prevPortal);
        var b = Marker(next, nextPortal);
        if (a == null || b == null) return false;
        next.GlobalPosition += a.GlobalPosition - b.GlobalPosition;
        return true;
    }

    /// <summary>a piece's footprint on the ground (world x / z), its map without the rock ring: Blender (x, y) is Godot
    /// (x, -y), so the map runs east from the room's x and north (-z) from its z</summary>
    public static Rect2 Footprint(KitRoom room)
    {
        var p = room.GlobalPosition;
        float w = room.Layout.W, d = room.Layout.D;
        return new Rect2(p.X, p.Z - d, w, d);
    }

    /// <summary>builds the pieces under `parent` (in the tree), each lined up on the piece it joins; notes what fails</summary>
    public static List<KitRoom> Build(IList<Piece> pieces, Node3D parent, Vector3 origin, List<string> notes)
    {
        var built = new List<KitRoom>();
        foreach (var pc in pieces)
        {
            int k = built.Count, t = pc.Parent(k);
            var room = new KitRoom { Name = pc.name.Replace(":", "").Replace("/", "_") };
            parent.AddChild(room);
            pc.make(room);
            if (k == 0) room.GlobalPosition = origin;
            else if (t < 0 || t >= k) notes.Add($"{pc.name}: joins piece {t}, not an earlier one");
            else
            {
                string tp = pc.attachPortal ?? pieces[t].outPortal;
                if (!Align(built[t], tp, room, pc.inPortal)) notes.Add($"{pc.name}: portal {pc.inPortal} or {pieces[t].name}'s {tp} missing");
            }
            // a missing portal or piece breaks the level (a stair without its piece is a way out that is gone)
            notes.AddRange(room.notes.Where(n => n.Contains("portal") || n.StartsWith("no prefab")).Select(n => $"{pc.name}: {n}"));
            built.Add(room);
        }
        for (int i = 0; i < built.Count; i++)
            for (int j = i + 1; j < built.Count; j++)
            {
                var o = Footprint(built[i]).Intersection(Footprint(built[j]));
                if (o.Size.X > 0.01f && o.Size.Y > 0.01f) notes.Add($"{built[i].Name} and {built[j].Name} overlap ({o.Size.X:0.#} x {o.Size.Y:0.#} m)");
            }
        return built;
    }

    /// <summary>a sample chain: a maze cave out north -> a connector -> a dungeon in south, out east -> a connector
    /// turning north -> an open cave in south; and a branch off the first cave's east side: a connector -> a small open
    /// cave in west</summary>
    public static List<Piece> Sample(int seed) => new()
    {
        new Piece { name = $"Chain {seed}: cave (maze)", outPortal = "north", make = r =>
            {
                r.cave.seed = seed;
                r.cave.portals = new() { new KitPortal { id = "north", side = "N" }, new KitPortal { id = "east", side = "E", at = 4 } };
                r.RandomCave();
            } },
        new Piece { name = $"Chain {seed}: connector S-N", inPortal = "from", outPortal = "to", make = r =>
            { r.connector.seed = seed; r.connector.from = "S"; r.connector.to = "N"; r.RandomConnector(); } },
        new Piece { name = $"Chain {seed}: dungeon", inPortal = "south", outPortal = "east", make = r =>
            {
                r.dungeon.seed = seed;
                r.dungeon.portals = new() { new KitPortal { id = "south", side = "S" }, new KitPortal { id = "east", side = "E", at = 14 } };
                r.RandomDungeon();
            } },
        new Piece { name = $"Chain {seed}: connector W-N", inPortal = "from", outPortal = "to", make = r =>
            { r.connector.seed = seed + 1; r.connector.from = "W"; r.connector.to = "N"; r.RandomConnector(); } },
        new Piece { name = $"Chain {seed}: cave (open)", inPortal = "south", make = r =>
            { r.cave.seed = seed + 2; r.cave.layout = "Open"; r.cave.portals = new() { new KitPortal { id = "south", side = "S" } }; r.RandomCave(); } },
        new Piece { name = $"Chain {seed}: branch connector W-E", inPortal = "from", outPortal = "to", attach = 0, attachPortal = "east", make = r =>
            { r.connector.seed = seed + 3; r.connector.from = "W"; r.connector.to = "E"; r.RandomConnector(); } },
        new Piece { name = $"Chain {seed}: side cave", inPortal = "west", make = r =>
            {
                r.cave.seed = seed + 4; r.cave.layout = "Open"; r.cave.nc = 18; r.cave.nr = 14; r.cave.chasm = false;
                r.cave.portals = new() { new KitPortal { id = "west", side = "W", at = 4 } };
                r.RandomCave();
            } },
    };

    /// <summary>one navmesh over every piece (KitNavMesh.Bake: the kit's walker, 0.05 m cells, openable leaves left out):
    /// which spawns of every piece lie on the first piece's first spawn's island. -> (reached, total, the unreached)</summary>
    public static (int ok, int total, List<string> missed, NavigationMesh nm) WalkChain(Node3D parent, IList<KitRoom> rooms)
    {
        var nm = KitNavMesh.Bake(parent, 0.05f);
        var map = KitWalkTest.Join(nm);
        var toParent = parent.GlobalTransform.AffineInverse();
        var spawns = rooms.SelectMany(r => KitNodes.Below(r, "").OfType<KitSpawn>().Select(s => (room: r, s))).ToList();
        var missed = new List<string>();
        if (spawns.Count == 0) return (0, 0, missed, nm);
        int home = map.At(toParent * spawns[0].s.GlobalPosition);
        int ok = 0;
        foreach (var (room, s) in spawns)
        {
            int at = map.At(toParent * s.GlobalPosition);
            if (home >= 0 && at == home) ok++; else missed.Add($"{room.Name}/{s.SpawnId}");
        }
        return (ok, spawns.Count, missed, nm);
    }

    // ------------------------------------------------------------------ baking a KitChain
    static KitPortal PortalOf(KitChainMap m, string id) => m.Portals().FirstOrDefault(p => p.id == id);

    /// <summary>the chain's maps as pieces: each map after the first behind a connector from the earlier map's out
    /// portal (its edge facing it) to its own in portal</summary>
    public static List<Piece> PiecesOf(KitChain chain, string chainName, List<string> notes)
    {
        var list = new List<Piece>();
        var pieceOf = new Dictionary<string, int>();                     // map id -> its piece's index
        var used = new HashSet<string>();                                // "map.portal" taken by a join
        var maps = chain.maps.ToList();
        for (int i = 0; i < maps.Count; i++)
        {
            var m = maps[i];
            if (pieceOf.ContainsKey(m.id)) { notes.Add($"two maps are called {m.id}"); continue; }
            if (i > 0)
            {
                var prev = string.IsNullOrEmpty(m.attachTo) ? maps[i - 1] : maps.Take(i).FirstOrDefault(q => q.id == m.attachTo);
                if (prev == null) { notes.Add($"{m.id}: joins {m.attachTo}, not a map listed before it"); continue; }
                string prevPortal = string.IsNullOrEmpty(m.attachPortal) ? prev.outPortal : m.attachPortal;
                var po = PortalOf(prev, prevPortal); var pi = PortalOf(m, m.inPortal);
                if (po == null || pi == null) { notes.Add($"{m.id}: portal {prev.id}.{prevPortal} or {m.id}.{m.inPortal} not in the maps' portals"); continue; }
                if (!used.Add($"{prev.id}.{po.id}")) notes.Add($"{prev.id}.{po.id} is joined twice");
                used.Add($"{m.id}.{pi.id}");
                int parentPiece = pieceOf[prev.id];
                char from = KitPortal.Opposite(po.Side), to = KitPortal.Opposite(pi.Side);
                if (from == to) notes.Add($"{prev.id} -> {m.id}: both portals face the same way; a connector cannot turn back");
                if (po.width != pi.width) notes.Add($"{prev.id}.{prev.outPortal} and {m.id}.{m.inPortal} differ in width");
                var co = m.connector ?? new KitConnectorOptions();
                list.Add(new Piece
                {
                    name = $"{chainName} {i:00}a {prev.id}-{m.id}", inPortal = "from", outPortal = "to",
                    attach = parentPiece, attachPortal = po.id,
                    make = r =>
                    {
                        r.connector = new KitConnectorOptions
                        {
                            from = from.ToString(), to = to.ToString(), length = co.length, width = po.width, seed = co.seed, style = co.style, debris = co.debris,
                        };
                        r.RandomConnector();
                    },
                });
            }
            pieceOf[m.id] = list.Count;
            list.Add(new Piece
            {
                name = $"{chainName} {i:00} {m.id}", inPortal = i > 0 ? m.inPortal : null, outPortal = m.outPortal,
                make = r =>
                {
                    if (m.kind == KitChainMap.Kind.Cave) { r.cave = m.cave; r.RandomCave(); }
                    else if (m.kind == KitChainMap.Kind.Dungeon) { r.dungeon = m.dungeon; r.RandomDungeon(); }
                    else { r.preset = ""; r.plan = m.PlanText; r.record = m.RecordText; r.Generate(); }
                },
            });
        }
        // every portal leads somewhere (an unjoined one would open the map's edge onto nothing)
        foreach (var m in maps)
            foreach (var p in m.Portals())
            {
                if (!used.Contains($"{m.id}.{p.id}")) notes.Add($"{m.id}.{p.id} leads nowhere: join a map to it or remove it");
                if (m.kind == KitChainMap.Kind.Plan && p.at < 0) notes.Add($"{m.id}.{p.id}: a hand-made map's portal needs its `at`");
            }
        return list;
    }

    static void Own(Node n, Node owner)
    {
        foreach (var c in KitNodes.Children(n))
        {
            if (c.Owner == null) c.Owner = owner;
            if (string.IsNullOrEmpty(c.SceneFilePath)) Own(c, owner);
        }
    }

    /// <summary>builds every piece of the chain at `chainPath` lined up in world space (under `host`, in the tree),
    /// stops if pieces overlap or a portal is missing, else saves each piece as a scene in a folder named after the chain
    /// (beside it), fills the chain's pieces, bakes one navmesh over all of them into the play scene
    /// (&lt;chain&gt;_Play.tscn: the sun and environment of VKI_Dungeon_B4, the streamer, the WASD walker) and saves the
    /// chain. Last, <see cref="KitChain.AfterBake"/> (a game's own additions).</summary>
    public static string Bake(Node host, string chainPath)
    {
        var chain = GD.Load<KitChain>(chainPath);
        if (chain == null) return $"no chain at {chainPath}";
        string chainName = chainPath.GetFile().GetBaseName();
        string folder = $"{chainPath.GetBaseDir()}/{chainName}";
        var notes = new List<string>();
        var pieces = PiecesOf(chain, chainName, notes);
        if (notes.Count > 0) return $"chain {chainName} not baked:\n{string.Join("\n", notes)}";
        var root = new Node3D { Name = "ChainBake" };
        host.AddChild(root);
        var sb = new StringBuilder();
        try
        {
            var rooms = Build(pieces, root, chain.origin, notes);
            if (notes.Count > 0) return $"chain {chainName} not baked:\n{string.Join("\n", notes)}";
            var (ok, total, missed, nm) = WalkChain(root, rooms);
            sb.AppendLine($"walk test: {ok}/{total} spawns reached" + (missed.Count > 0 ? $" (not {string.Join(", ", missed)})" : ""));
            DirAccess.MakeDirRecursiveAbsolute(ProjectSettings.GlobalizePath(folder));
            var baked = new Godot.Collections.Array<KitChainPiece>();
            for (int i = 0; i < rooms.Count; i++)
            {
                var room = rooms[i];
                string id = pieces[i].name.Substring(chainName.Length + 1);
                string path = $"{folder}/{room.Name}.tscn";
                Own(room, room);
                var packed = new PackedScene();
                var err = packed.Pack(room);
                if (err == Error.Ok) err = ResourceSaver.Save(packed, path);
                if (err != Error.Ok) return $"chain {chainName}: saving {path} failed ({err})";
                baked.Add(new KitChainPiece
                {
                    id = id, scene = path, position = room.GlobalPosition, footprint = Footprint(room),
                    spawns = KitNodes.Below(room, "").OfType<KitSpawn>().Select(sp => sp.SpawnId).ToArray(),
                });
            }
            for (int i = 1; i < baked.Count; i++)                     // each piece and the piece it joins
            {
                int t = pieces[i].Parent(i);
                baked[i].neighbours = baked[i].neighbours.Append(baked[t].id).ToArray();
                baked[t].neighbours = baked[t].neighbours.Append(baked[i].id).ToArray();
            }
            chain.pieces = baked;
            var err2 = ResourceSaver.Save(chain, chainPath);
            if (err2 != Error.Ok) return $"chain {chainName}: saving the chain failed ({err2})";
            string play = WritePlayScene(chainPath, folder, chainName, nm);
            sb.Insert(0, $"chain {chainName}: {baked.Count} pieces baked to {folder} (play: {play})\n");
        }
        finally
        {
            host.RemoveChild(root);
            root.Free();
        }
        if (KitChain.AfterBake != null)                                   // the game's own additions to the pieces (a quest's way in)
        {
            try { sb.AppendLine(KitChain.AfterBake(GD.Load<KitChain>(chainPath))); }
            catch (Exception e) { sb.AppendLine($"after bake: {e.Message}"); }
        }
        return sb.ToString();
    }

    /// <summary>&lt;chain&gt;_Play.tscn: the sun and environment of VKI_Dungeon_B4, a KitChainStreamer, one navmesh over every
    /// piece (KitNavMesh: paths run into pieces not streamed in yet), a KitShroud (as the play scene's was tuned, on a
    /// re-bake) and a KitTestWalker</summary>
    static string WritePlayScene(string chainPath, string folder, string chainName, NavigationMesh nm)
    {
        string path = $"{folder}/{chainName}_Play.tscn";
        var shroud = TunedShroud(path) ?? new KitShroud();      // the rock away from the passages fades to black
        shroud.Name = "KitShroud";
        var root = new Node3D { Name = chainName + "_Play" };
        try
        {
            string lit = KitPaths.LayoutScenes + "VKI_Dungeon_B4.tscn";
            if (ResourceLoader.Exists(lit))
            {
                var lv = GD.Load<PackedScene>(lit).Instantiate();
                foreach (var n in KitNodes.Below(lv, "").Where(n => n is DirectionalLight3D || n is WorldEnvironment))
                {
                    var c = n.Duplicate();
                    if (n is Node3D n3 && c is Node3D c3) c3.Transform = Placed(lv, n3);       // the level is not in the tree
                    root.AddChild(c);
                    c.Owner = root;
                }
                lv.Free();
            }
            var st = new KitChainStreamer { Name = "KitChainStreamer", chain = GD.Load<KitChain>(chainPath) };
            root.AddChild(st);
            st.Owner = root;
            var nav = new KitNavMesh { Name = "KitNavMesh", NavigationMesh = nm };
            root.AddChild(nav);
            nav.Owner = root;
            root.AddChild(shroud);
            shroud.Owner = root;
            var w = new KitTestWalker { Name = "KitTestWalker" };
            root.AddChild(w);
            w.Owner = root;
            st.walker = w;
            var packed = new PackedScene();
            var err = packed.Pack(root);
            if (err == Error.Ok) err = ResourceSaver.Save(packed, path);
            return err == Error.Ok ? path : $"(failed: {err})";
        }
        finally { root.Free(); }
    }

    /// <summary>the KitShroud of the play scene already at `path` (null: none yet), loose, so a re-bake keeps it as tuned</summary>
    static KitShroud TunedShroud(string path)
    {
        if (!ResourceLoader.Exists(path)) return null;
        var old = GD.Load<PackedScene>(path).Instantiate();
        try
        {
            var s = KitNodes.Below(old, "").OfType<KitShroud>().FirstOrDefault();
            return s == null ? null : new KitShroud { darkFrom = s.darkFrom, blackAt = s.blackAt, topLight = s.topLight, cell = s.cell, floorBand = s.floorBand };
        }
        finally { old.Free(); }
    }

    /// <summary>a KitChain like the sample chain (maze cave -> dungeon -> open cave, and a side cave branching off the
    /// first cave's east side) saved at `chainPath`, baked</summary>
    public static string CreateSample(Node host, string chainPath, int seed)
    {
        var chain = new KitChain();
        chain.maps.Add(new KitChainMap
        {
            id = "cave", kind = KitChainMap.Kind.Cave, inPortal = "", outPortal = "north",
            cave = new KitCaveOptions { seed = seed, portals = new() { new KitPortal { id = "north", side = "N" }, new KitPortal { id = "east", side = "E", at = 4 } } },
        });
        chain.maps.Add(new KitChainMap
        {
            id = "dungeon", kind = KitChainMap.Kind.Dungeon, inPortal = "south", outPortal = "east",
            dungeon = new KitDungeonOptions { seed = seed, portals = new() { new KitPortal { id = "south", side = "S" }, new KitPortal { id = "east", side = "E", at = 14 } } },
            connector = new KitConnectorOptions { seed = seed, length = 10 },
        });
        chain.maps.Add(new KitChainMap
        {
            id = "deep cave", kind = KitChainMap.Kind.Cave, inPortal = "south", outPortal = "",
            cave = new KitCaveOptions { seed = seed + 2, layout = "Open", portals = new() { new KitPortal { id = "south", side = "S" } } },
            connector = new KitConnectorOptions { seed = seed + 1, length = 10 },
        });
        chain.maps.Add(new KitChainMap
        {
            id = "side cave", kind = KitChainMap.Kind.Cave, inPortal = "west", attachTo = "cave", attachPortal = "east", outPortal = "",
            cave = new KitCaveOptions { seed = seed + 4, layout = "Open", nc = 18, nr = 14, chasm = false, portals = new() { new KitPortal { id = "west", side = "W", at = 4 } } },
            connector = new KitConnectorOptions { seed = seed + 3, length = 10 },
        });
        DirAccess.MakeDirRecursiveAbsolute(ProjectSettings.GlobalizePath(chainPath.GetBaseDir()));
        var err = ResourceSaver.Save(chain, chainPath);
        if (err != Error.Ok) return $"saving {chainPath} failed ({err})";
        return Bake(host, chainPath);
    }

    /// <summary>builds the sample chain for `count` seeds and walks each from its first map to its last</summary>
    public static string ValidateChains(Node host, int count, int firstSeed = 1)
    {
        var sb = new StringBuilder();
        int good = 0;
        for (int sd = firstSeed; sd < firstSeed + count; sd++)
        {
            var root = new Node3D { Name = $"chain_{sd}" };
            host.AddChild(root);
            try
            {
                var notes = new List<string>();
                var rooms = Build(Sample(sd), root, new Vector3(2000f, 0f, 2000f), notes);
                var (ok, total, missed, _) = WalkChain(root, rooms);
                bool pass = ok == total && total > 0 && notes.Count == 0;
                if (pass) good++;
                else sb.AppendLine($"seed {sd}: {ok}/{total} spawns reached" + (missed.Count > 0 ? $" (not {string.Join(", ", missed)})" : "") +
                                   (notes.Count > 0 ? $"; {string.Join("; ", notes)}" : ""));
            }
            catch (Exception e) { sb.AppendLine($"seed {sd}: error {e.GetBaseException().Message}"); }
            finally { host.RemoveChild(root); root.Free(); }
        }
        return $"chains: {good}/{count} walkable end to end\n{sb}";
    }

    /// <summary>a node's transform in the space of `root` above it (outside the tree, where GlobalTransform is not known)</summary>
    static Transform3D Placed(Node root, Node3D n)
    {
        var t = Transform3D.Identity;
        for (Node c = n; c != null && c != root; c = c.GetParent()) if (c is Node3D c3) t = c3.Transform * t;
        return t;
    }
}
#endif
