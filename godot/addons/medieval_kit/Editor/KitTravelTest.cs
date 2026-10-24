#if TOOLS
using System.Linq;
using System.Threading.Tasks;
using Godot;

namespace MedievalKit.Editor;

/// <summary>Takes every link of every built world level through KitTravel (kit_cli.gd -- travel; headless is fine):
/// loads the level, asks Godot's navigation for a path from the arrival to every spawn and link, takes each link and
/// checks that it lands in the link's target, on a spawn (or the link back) -- a "@return" door after coming in by a
/// link that leads to its level. Then the instant cuts: KitTravel.Preload on at the
/// world's start, its neighbours held, a link there and the way back each taken without a load. Prints a TRAVEL line
/// per problem and a TRAVEL DONE line; quits. Unity: the links' check of the world graph (docs/world_graph.json).</summary>
public partial class KitTravelTest : Node
{
    static readonly Vector3 Nowhere = new(9999f, 9999f, 9999f);

    Node3D walker;
    bool arrived;
    string arrivedLevel;
    KitSpawn arrivedSpawn;
    int ok, bad, deep;

    public override void _Ready()
    {
        walker = new Node3D { Name = "KitTravelTestWalker" };
        AddChild(walker);           // outside the levels, as a game's player
        KitTravel.SetWalker(walker);
        KitTravel.FadeSeconds = 0f;
        KitTravel.Arrived += (l, s) => { arrived = true; arrivedLevel = l; arrivedSpawn = s; };
        Run();
    }

    /// <summary>waits for the arrival, then for the fade back (KitTravel takes one journey at a time)</summary>
    async Task<bool> Arrival(int frames = 1200)
    {
        for (int i = 0; i < frames && !arrived; i++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        for (int i = 0; i < frames && KitTravel.Travelling; i++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        return arrived;
    }

    void Fail(string what) { bad++; GD.Print("TRAVEL " + what); }

    async Task<bool> Load(string level, string spawn)
    {
        arrived = false;
        if (!KitTravel.Reload(level, spawn)) { Fail($"{level}: does not load"); return false; }
        if (!await Arrival()) { Fail($"{level}: no arrival after loading"); return false; }
        return true;
    }

    async void Run()
    {
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        var world = GD.Load<KitWorld>(KitPaths.World);
        foreach (var lv in world.Levels)
        {
            if (!ResourceLoader.Exists(KitTravel.ScenePath(lv.Name))) { Fail($"{lv.Name}: not built"); continue; }
            string entry = lv.Links.FirstOrDefault()?.Id;
            if (!await Load(lv.Name, entry)) continue;
            await Paths(lv.Name);
            var ids = GetTree().CurrentScene.FindChildren("*", "", true, false).OfType<KitLink>().Select(l => l.LinkId).ToList();
            foreach (var id in ids)
            {
                if (!await Load(lv.Name, entry)) break;
                var link = GetTree().CurrentScene.FindChildren("*", "", true, false).OfType<KitLink>().First(l => l.LinkId == id);
                string want = link.Target;
                if (want == "@deep" || string.IsNullOrEmpty(want)) { deep++; continue; }
                if (want == "@return")
                {
                    // came in by a link of another level leading here: back through it; a building no world level
                    // links to (the kit's interiors, entered from a game's own doors): as if from the start level
                    var from = world.Levels.SelectMany(o => o.Links.Select(k => (level: o.Name, link: k.Id, target: k.Target)))
                                    .FirstOrDefault(x => x.level != lv.Name && x.target == lv.Name);
                    if (from.level == null) from = (world.Start, world.Find(world.Start)?.Links.FirstOrDefault()?.Id, lv.Name);
                    KitTravel.PushReturn(from.level, from.link);
                    want = from.level;
                }
                walker.GlobalPosition = Nowhere;
                arrived = false;
                if (!KitTravel.Go(link)) { Fail($"{lv.Name}/{id} -> {link.Target}: Go refused"); continue; }
                if (!await Arrival()) { Fail($"{lv.Name}/{id} -> {want}: never arrived"); continue; }
                if (arrivedLevel != want) Fail($"{lv.Name}/{id}: arrived in {arrivedLevel}, want {want}");
                else if (walker.GlobalPosition == Nowhere) Fail($"{lv.Name}/{id} -> {want}: no spawn or link to arrive on");
                else
                {
                    ok++;
                    if (arrivedSpawn == null) GD.Print($"TRAVEL note {lv.Name}/{id} -> {want}: placed at its link (no spawn)");
                }
            }
        }
        await InstantCuts(world);
        GD.Print($"TRAVEL DONE {ok} links taken, {bad} problems, {deep} leading nowhere yet (@deep)");
        GetTree().Quit(bad > 0 ? 1 : 0);
    }

    /// <summary>Godot's own pathfinding on the level's navmesh (KitNavMesh), as an agent would ask: from the arrival
    /// spawn to every spawn, link and encounter point the walk test checks (KitWalkTest.Points)</summary>
    async Task Paths(string level)
    {
        if (GetTree().CurrentScene is not Node3D scene || scene.FindChildren("*", "KitNavMesh", true, false).Count == 0) return;
        var map = scene.GetWorld3D().NavigationMap;
        // the level's region joins the map, then the map syncs on a later physics frame (until then it may still be
        // empty or hold the level left: an agent asking on arrival has to wait the same; NavigationAgent3D does)
        var region = (NavigationRegion3D)scene.FindChildren("*", "KitNavMesh", true, false)[0];
        for (int i = 0; i < 120 && !NavigationServer3D.MapGetRegions(map).Contains(region.GetRid()); i++)
            await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
        var pts = KitWalkTest.Points(scene);
        var from = arrivedSpawn != null ? arrivedSpawn.GlobalPosition : pts.FirstOrDefault()?.At ?? Vector3.Zero;
        // regions sync on their own (asynchronous) iterations: wait until the map answers from this level's surface
        for (int i = 0; i < 300 && NavigationServer3D.MapGetClosestPoint(map, from).DistanceTo(from) > KitWalkTest.Reach; i++)
            await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
        var start = NavigationServer3D.MapGetClosestPoint(map, from);
        int reached = 0;
        var missed = new System.Collections.Generic.List<string>();
        foreach (var p in pts)
        {
            var to = NavigationServer3D.MapGetClosestPoint(map, p.At);
            var path = NavigationServer3D.MapGetPath(map, start, to, true);
            if (path.Length > 0 && path[^1].DistanceTo(to) < 0.3f) reached++;
            else missed.Add($"{p.Name} (path {path.Length} pts, ends {(path.Length > 0 ? path[^1].DistanceTo(to) : -1f):F2} m off; " +
                            $"start {start.DistanceTo(from):F2} m, end {to.DistanceTo(p.At):F2} m from their points)");
        }
        if (missed.Count > 0) Fail($"{level}: paths {reached}/{pts.Count}; none to {string.Join(", ", missed)}");
        else GD.Print($"TRAVEL paths {level}: {reached}/{pts.Count}");
    }

    /// <summary>Preload on at the start level: once its neighbours are held, a link and the way back are instant</summary>
    async Task InstantCuts(KitWorld world)
    {
        KitTravel.Preload = true;
        if (!await Load(world.Start, world.Find(world.Start)?.Links.FirstOrDefault()?.Id)) return;
        var links = GetTree().CurrentScene.FindChildren("*", "", true, false).OfType<KitLink>()
            .Where(l => ResourceLoader.Exists(KitTravel.ScenePath(l.Target))).ToList();
        int frames = 0;
        while (frames++ < 3000 && links.Any(l => !KitTravel.Held.Contains(l.Target)))
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        var notHeld = links.Where(l => !KitTravel.Held.Contains(l.Target)).Select(l => l.Target).Distinct().ToList();
        if (notHeld.Count > 0) { Fail($"preload: {string.Join(", ", notHeld)} not held after {frames} frames"); return; }
        GD.Print($"TRAVEL preload: {KitTravel.Held.Count()} levels held at {world.Start} after {frames} frames");
        var go = links.First();
        arrived = false;
        KitTravel.Go(go);
        if (!arrived || arrivedLevel != go.Target) { Fail($"preload: {world.Start}/{go.LinkId} -> {go.Target} was not an instant cut"); return; }
        var back = GetTree().CurrentScene.FindChildren("*", "", true, false).OfType<KitLink>()
            .FirstOrDefault(l => l.Target == world.Start || l.Target == "@return");
        if (back == null) { Fail($"preload: no way back from {go.Target}"); return; }
        int f = 0;
        while (f++ < 3000 && !KitTravel.Held.Contains(world.Start)) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        arrived = false;
        KitTravel.Go(back);
        if (!arrived || arrivedLevel != world.Start) Fail($"preload: {go.Target}/{back.LinkId} back to {world.Start} was not an instant cut");
        else { ok += 2; GD.Print($"TRAVEL preload: {world.Start} -> {go.Target} -> {world.Start}, both instant"); }
        // let the preloads round the start finish before they are dropped (a load cut off at quit reports parse errors)
        for (int i = 0; i < 3000 && KitTravel.preloading.Count > 0; i++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        GD.Print($"TRAVEL preload: {KitTravel.preloading.Count} loads still running, {KitTravel.Held.Count()} held at the end");
        KitTravel.Preload = false;
    }
}
#endif
