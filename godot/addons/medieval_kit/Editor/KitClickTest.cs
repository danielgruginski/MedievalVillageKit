#if TOOLS
using System;
using System.Linq;
using System.Threading.Tasks;
using Godot;

namespace MedievalKit.Editor;

/// <summary>legs whose pointer a test moves (no mouse): where it is on the screen, a press, held</summary>
public partial class KitTestLegs : KitClickToMove
{
    public Vector2 Screen;
    public bool Press, Held;

    protected override bool Pointer(out Vector2 screen, out bool press, out bool held)
    {
        screen = Screen; press = Press; held = Held;
        Press = false;
        return true;
    }
}

/// <summary>
/// The click-to-move walker (<see cref="KitWalker"/>) in a built level, driven as a player drives it but by a pointer the
/// test moves (<see cref="KitTestLegs"/>): a click on the floor 6 m off (it gets there), the button held toward a point
/// 10 m off (it walks), a click on a roof or a wall (it walks up to the building), then the doors nearest the spawn:
/// the cursor on each (the way out shows under it) and a click on the first that does (it walks there and goes
/// through, then comes back by the way out inside). Logged to &lt;out&gt;/click_&lt;layout&gt;.txt with a shot per step.
/// Needs a window (not --headless); quits when done. kit_cli: clickwalk &lt;layout&gt; &lt;out dir&gt;. Unity: the itch staging
/// KitWalkerCheck (FULL_PORT_PLAN phase 6).
/// </summary>
public partial class KitClickTest : Node
{
    string layout = "VK_ValleyTown", outDir = "";
    readonly System.Text.StringBuilder log = new();
    KitWalker walker;
    KitTestLegs legs;
    int fails;
    Vector3 home;                                                   // the spawn: stands are on navmesh joined to it

    /// <summary>a navmesh point round `at` (toward the camera first, then the sides, then behind) joined to the spawn's</summary>
    Vector3? StandNear(Vector3 at, float d)
    {
        foreach (var o in new[] { new Vector3(0, 0, d), new Vector3(d, 0, d * 0.5f), new Vector3(-d, 0, d * 0.5f), new Vector3(0, 0, d * 0.5f), new Vector3(d * 0.6f, 0, 0), new Vector3(-d * 0.6f, 0, 0), new Vector3(0, 0, -d) })
        {
            var p = NavigationServer3D.MapGetClosestPoint(Map, at + o);
            var way = NavigationServer3D.MapGetPath(Map, home, p, true);
            if (way.Length >= 2 && way[^1].DistanceTo(p) < 0.2f) return p;
        }
        return null;
    }

    async Task<bool> StandAt(Vector3? p)
    {
        if (p == null) return false;
        KitTravel.Place(walker, new Transform3D(Basis.Identity, p.Value));
        walker.Camera.Snap();
        await Wait(3);
        return true;
    }

    public void Setup(string layoutName, string outDirectory) { layout = layoutName; outDir = outDirectory; }

    public override void _Ready() => Callable.From(() => { _ = Run(); }).CallDeferred();

    async Task Run()
    {
        try { await Steps(); }
        catch (Exception e) { Say($"FAIL exception {e}"); fails++; }
        Say(fails == 0 ? "ALL PASS" : $"{fails} FAILED");
        using (var f = FileAccess.Open($"{outDir}/click_{layout}.txt", FileAccess.ModeFlags.Write)) f.StoreString(log.ToString());
        GetTree().Quit(fails == 0 ? 0 : 1);
    }

    void Say(string s) { log.AppendLine(s); GD.Print("[click] " + s); }
    void Check(bool ok, string what) { Say($"{(ok ? "ok  " : "FAIL")} {what}"); if (!ok) fails++; }
    Task Frames(int n) => n <= 0 ? Task.CompletedTask : Wait(n);
    async Task Wait(int n) { for (int i = 0; i < n; i++) await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame); }

    async Task<bool> Until(Func<bool> done, float seconds)
    {
        for (int i = 0; i < seconds * 60f; i++)
        {
            if (done()) return true;
            await Wait(1);
        }
        return done();
    }

    void Shot(string name) => GetViewport().GetTexture().GetImage().SavePng($"{outDir}/click_{layout}_{name}.png");
    Vector3 Pos => walker.GlobalPosition;
    Rid Map => walker.GetWorld3D().NavigationMap;
    static float Flat(Vector3 v) => new Vector2(v.X, v.Z).Length();
    bool Standing => !legs.HasPath && legs.Velocity.Length() < 0.05f;

    async Task Click(Vector2 screen)
    {
        legs.Screen = screen; legs.Held = true; legs.Press = true;
        await Wait(2);
        legs.Held = false;
        await Wait(1);
    }

    PointerRay RayAt(Vector2 s) => new(walker.Camera.ProjectRayOrigin(s), walker.Camera.ProjectRayNormal(s));
    bool OnScreen(Vector3 p, out Vector2 s)
    {
        s = walker.Camera.UnprojectPosition(p);
        var size = GetViewport().GetVisibleRect().Size;
        return !walker.Camera.IsPositionBehind(p) && s.X > 40 && s.Y > 60 && s.X < size.X - 40 && s.Y < size.Y - 40;
    }

    async Task Steps()
    {
        DisplayServer.WindowSetSize(new Vector2I(1600, 900));
        Check(KitTravel.Reload(layout, ""), $"load {layout}");
        Check(await Until(() => KitTravel.CurrentLevel == layout && !KitTravel.Travelling, 30f), "arrived");
        var scene = GetTree().CurrentScene;
        var spawn = scene.FindChildren("*", "", true, false).OfType<KitSpawn>().FirstOrDefault();
        legs = new KitTestLegs();
        walker = KitWalker.Spawn(spawn?.GlobalTransform ?? Transform3D.Identity, legs);
        await Wait(40);
        var on = NavigationServer3D.MapGetClosestPoint(Map, Pos);
        home = on;
        Check(on.DistanceTo(Pos) < 0.2f, $"on the navmesh at {Pos} (spawn {spawn?.Name})");

        // 1: a click on the floor 6 m off
        bool clicked = false;
        for (int i = 0; i < 16 && !clicked; i++)
        {
            float a = Mathf.Tau * i / 16f;
            var want = Pos + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * 6f;
            var p = NavigationServer3D.MapGetClosestPoint(Map, want);
            if (Flat(p - want) > 0.2f || !OnScreen(p, out var s)) continue;
            var way = NavigationServer3D.MapGetPath(Map, Pos, p, true);
            if (way.Length < 2 || way[^1].DistanceTo(p) > 0.15f) continue;
            var hits = legs.Cast(RayAt(s));
            if (!legs.Ground(hits, RayAt(s), out var g, out bool exact, out _) || !exact || g.DistanceTo(p) > 0.5f) continue;
            clicked = true;
            await Click(s);
            Check(legs.HasPath, $"floor click at {p}: a way ({hits.Length} hits under the cursor)");
            bool there = await Until(() => Standing, 8f);
            Check(there && Flat(Pos - g) < 0.3f, $"floor click: stands {Flat(Pos - g):F2} m from the point clicked");
            Shot("1_floor");
        }
        Check(clicked, "found a floor point 6 m off in view");

        // 2: the button held toward a point 10 m off, 1.5 s
        var start = Pos;
        for (int i = 0; i < 16; i++)
        {
            float a = Mathf.Tau * i / 16f + 0.2f;
            var p = NavigationServer3D.MapGetClosestPoint(Map, Pos + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * 10f);
            if (Flat(p - Pos) < 7f || !OnScreen(p, out var s)) continue;
            legs.Screen = s; legs.Press = true; legs.Held = true;
            await Wait(90);
            legs.Held = false;
            await Until(() => Standing, 6f);
            Check(Flat(Pos - start) > 3f, $"held toward {p}: walked {Flat(Pos - start):F1} m");
            Shot("2_hold");
            break;
        }

        // 3: a click on a roof or a wall (the walker 8 m south of the nearest door's house): through to the floor behind
        // when the walker reaches it without a long way round, else up to the building
        var scene3 = GetTree().CurrentScene;
        var house = scene3.FindChildren("*", "", true, false).OfType<KitLink>()
                          .Where(l => KitClickToMove.Leads(l) && !l.WalkInto).OrderBy(l => l.GlobalPosition.DistanceTo(Pos)).FirstOrDefault();
        var houseStand = house != null ? StandNear(house.GlobalPosition, 8f) : null;
        await StandAt(houseStand);
        var size = GetViewport().GetVisibleRect().Size;
        (Vector2 s, bool exact)? behind = null, upTo = null;
        int high = 0;
        for (int y = 1; y <= 15; y++)
            for (int x = 2; x <= 14; x++)
            {
                var s = new Vector2(size.X * x / 16f, size.Y * y / 16f);
                var ray = RayAt(s);
                var hits = legs.Cast(ray);
                if (hits.Length == 0 || hits[0].Point.Y < Pos.Y + 1.5f) continue;
                high++;
                if (!legs.Ground(hits, ray, out var g, out bool exact, out _) || Flat(g - Pos) < 1.5f) continue;
                if (exact) behind ??= (s, true); else upTo ??= (s, false);
            }
        Say($"     {high} cursor points on something 1.5 m up; floor behind: {behind != null}, up to it: {upTo != null}");
        if (high == 0) Say("     skip: nothing with a collider stands 1.5 m up in view (exterior pieces have no vki_collider; a village's houses get a box)");
        else Check(behind != null || upTo != null, "found a roof or a wall in view");
        foreach (var c in new[] { upTo, behind })
        {
            if (c == null) continue;
            var ray = RayAt(c.Value.s);
            var hits = legs.Cast(ray);
            legs.Ground(hits, ray, out var g, out _, out var pointed);
            var from = Pos;
            await Click(c.Value.s);
            await Until(() => Standing, 10f);
            bool ok = Flat(Pos - g) < 0.5f && Flat(Pos - from) > 1f && (c.Value.exact || Flat(Pos - pointed) < 4f);
            Check(ok, $"click on {hits[0].Collider?.GetParent()?.Name} ({(c.Value.exact ? "the floor behind" : "up to it")}): stands {Flat(Pos - g):F2} m from the point, {Flat(Pos - pointed):F1} m from where the cursor met it");
            Shot(c.Value.exact ? "3_behind" : "3_up_to");
            await StandAt(houseStand);
        }

        // 4: the doors: the cursor on each, a click on the first under it; through and back
        var links = scene.FindChildren("*", "", true, false).OfType<KitLink>()
                         .Where(l => KitClickToMove.Leads(l) && !l.WalkInto && l.Target != layout && l.Target != "@return")
                         .OrderBy(l => l.GlobalPosition.DistanceTo(Pos)).Take(8).ToList();
        int shown = 0; bool went = false;
        foreach (var l in links)
        {
            var door = l.GetChildren().OfType<CollisionShape3D>().FirstOrDefault()?.GlobalPosition ?? l.GlobalPosition;
            if (!await StandAt(StandNear(door, 4f))) { Say($"     {l.LinkId}: no stand near it joined to the spawn"); continue; }
            if (!OnScreen(door, out var s)) { Say($"     {l.LinkId}: off screen"); continue; }
            legs.Screen = s;
            await Wait(2);
            bool hover = legs.Hover == l;
            if (hover) shown++;
            Say($"     {l.LinkId} -> {l.Target}: {(hover ? "shows" : $"not under the cursor ({legs.Hover?.LinkId ?? "none"})")}");
            if (!hover || went) continue;
            Shot("4_door_hover");
            await Click(s);
            went = await Until(() => KitTravel.CurrentLevel == l.Target, 12f);
            Check(went, $"clicked {l.LinkId}: in {KitTravel.CurrentLevel}" + (went ? "" : $" (stands at {Pos}, the door's trigger at {door}, {Flat(Pos - door):F2} m off, way {legs.HasPath})"));
            if (!went) continue;
            await Wait(20);
            Shot("5_inside");
            var inside = GetTree().CurrentScene.FindChildren("*", "", true, false).OfType<KitLink>()
                                  .FirstOrDefault(b => b.Target == "@return" || b.Target == layout);
            if (inside == null) { Check(false, $"{l.Target}: a way back"); continue; }
            var back = inside.GetChildren().OfType<CollisionShape3D>().FirstOrDefault()?.GlobalPosition ?? inside.GlobalPosition;
            bool seen = OnScreen(back, out var bs);
            legs.Screen = bs;
            await Wait(2);
            Check(seen && legs.Hover == inside, $"{l.Target}: the way out {inside.LinkId} shows under the cursor");
            await Click(bs);
            Check(await Until(() => KitTravel.CurrentLevel == layout, 12f), $"back in {KitTravel.CurrentLevel}");
            await Wait(20);
            Shot("6_back");
        }
        Check(shown > 0, $"doors under the cursor: {shown} of {links.Count} tried");
    }
}
#endif
