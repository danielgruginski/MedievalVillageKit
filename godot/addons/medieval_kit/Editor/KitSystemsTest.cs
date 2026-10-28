#if TOOLS
using System;
using System.Linq;
using System.Threading.Tasks;
using Godot;

namespace MedievalKit.Editor;

/// <summary>a usable thing for the test: a post that counts its uses</summary>
public partial class KitTestThing : Interactable
{
    public int Uses;
    public override string Label => "Test post - use";
    public override void Use() => Uses++;

    public override void _Ready()
    {
        AddChild(new MeshInstance3D { Mesh = new CylinderMesh { TopRadius = 0.15f, BottomRadius = 0.15f, Height = 1.2f }, Position = new Vector3(0, 0.6f, 0) });
    }
}

/// <summary>
/// The phase 3a systems in built levels, driven as a game drives them (FULL_PORT_PLAN phase 6): VKI_Dungeon_B1's kit fires
/// lit as it stands (torches, a brazier); in VK_ValleyTown a blaze lit from one corner spreading, collapsing and
/// smouldering, a fire circle, a bolt's splash, a missile's flight, ground spots scattered; in VKI_Tavern_F0 a creature
/// behind the south wall shown as a silhouette (the pixel's colour with and without), a usable thing hovered and clicked
/// (the walker walks to it and uses it), a walkway deck given its navmesh. Logged to &lt;out&gt;/systems.txt with shots.
/// Needs a window. kit_cli: systems &lt;out dir&gt;.
/// </summary>
public partial class KitSystemsTest : Node
{
    string outDir = "";
    readonly System.Text.StringBuilder log = new();
    KitWalker walker;
    KitTestLegs legs;
    int fails;

    public void Setup(string outDirectory) => outDir = outDirectory;

    public override void _Ready() => Callable.From(() => { _ = Run(); }).CallDeferred();

    async Task Run()
    {
        try { await Steps(); }
        catch (Exception e) { Say($"FAIL exception {e}"); fails++; }
        Say(fails == 0 ? "ALL PASS" : $"{fails} FAILED");
        using (var f = FileAccess.Open($"{outDir}/systems.txt", FileAccess.ModeFlags.Write)) f.StoreString(log.ToString());
        GetTree().Quit(fails == 0 ? 0 : 1);
    }

    void Say(string s) { log.AppendLine(s); GD.Print("[systems] " + s); }
    void Check(bool ok, string what) { Say($"{(ok ? "ok  " : "FAIL")} {what}"); if (!ok) fails++; }
    async Task Wait(int n) { for (int i = 0; i < n; i++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame); }
    async Task Seconds(float s) { await ToSignal(GetTree().CreateTimer(s), SceneTreeTimer.SignalName.Timeout); }
    void Shot(string name) => GetViewport().GetTexture().GetImage().SavePng($"{outDir}/sys_{name}.png");
    Vector3 Pos => walker.GlobalPosition;
    Rid Map => walker.GetWorld3D().NavigationMap;

    async Task<bool> Until(Func<bool> done, float seconds)
    {
        for (int i = 0; i < seconds * 60f; i++) { if (done()) return true; await Wait(1); }
        return done();
    }

    /// <summary>to a level (fresh), the walker at its first spawn</summary>
    async Task Go(string level)
    {
        KitTravel.Reload(level, "");
        await Until(() => KitTravel.CurrentLevel == level && !KitTravel.Travelling, 30f);
        var spawn = KitNodes.Below(GetTree().CurrentScene, "").OfType<KitSpawn>().FirstOrDefault();
        var t = spawn?.GlobalTransform ?? Transform3D.Identity;
        if (walker == null) { legs = new KitTestLegs(); walker = KitWalker.Spawn(t, legs); }
        else KitTravel.Place(walker, t);
        await Wait(40);
        walker.Camera.Snap();
        await Wait(3);
    }

    async Task Stand(Vector3 p)
    {
        KitTravel.Place(walker, new Transform3D(Basis.Identity, NavigationServer3D.MapGetClosestPoint(Map, p)));
        walker.Camera.Snap();
        await Wait(3);
    }

    async Task Steps()
    {
        DisplayServer.WindowSetSize(new Vector2I(1600, 900));

        // the kit's fires (the brazier first unlit: what the fire changes)
        KitLevel.LightFires = false;
        await Go("VKI_Dungeon_B1");
        var unlit = KitNodes.Below(GetTree().CurrentScene, "").OfType<KitPiece>().FirstOrDefault(p => p.Name.ToString().Contains("Brazier"));
        if (unlit != null) { await Stand(unlit.GlobalPosition + new Vector3(0, 0, 2.5f)); await Seconds(0.5f); Shot("0_brazier_unlit"); }
        KitLevel.LightFires = true;
        await Go("VKI_Dungeon_B1");
        var level = GetTree().CurrentScene;
        var lit = KitNodes.Below(level, "").OfType<KitPiece>().Where(p => p.HasNode("Fire")).ToList();
        int flick = KitNodes.Below(level, "").OfType<FireFlicker>().Count();
        Check(lit.Count >= 6, $"dungeon B1: {lit.Count} kit fires lit ({string.Join(", ", lit.Select(p => p.Name))}), {flick} lights flickering");
        int parts = FireFx.Parts(level).Count(p => p.Emitting);
        Check(parts >= lit.Count * 2, $"{parts} fire parts emitting");
        var brazier = lit.FirstOrDefault(p => p.Name.ToString().Contains("Brazier")) ?? lit.FirstOrDefault();
        if (brazier != null) { await Stand(brazier.GlobalPosition + new Vector3(0, 0, 2.5f)); await Seconds(1.5f); Shot("1_brazier"); }
        var torch = lit.FirstOrDefault(p => p.Name.ToString().Contains("Torch"));
        if (torch != null) { await Stand(torch.GlobalPosition + new Vector3(0, 0, 2.5f)); await Seconds(1f); Shot("2_torch"); }

        // a blaze, a burst, a splash, a missile, ground spots
        await Go("VK_ValleyTown");
        var thing = new Node3D { Name = "Engine" };
        GetTree().CurrentScene.AddChild(thing);
        thing.GlobalPosition = NavigationServer3D.MapGetClosestPoint(Map, Pos + new Vector3(6f, 0f, 5f));   // (open grass, in view)
        thing.AddChild(new MeshInstance3D { Mesh = new BoxMesh { Size = new Vector3(2.4f, 3f, 2.4f) }, Position = new Vector3(0, 1.5f, 0) });
        var box = new Aabb(new Vector3(-1.2f, 0f, -1.2f), new Vector3(2.4f, 3f, 2.4f));
        var fire = Fire.Blaze(thing, box, null, 0.8f, thing.GlobalPosition + new Vector3(-1.2f, 0.2f, 1.2f));
        await Seconds(1f);
        Shot("3_blaze_catching");
        await Seconds(6f);
        Shot("4_blaze_full");
        Fire.Collapse(fire, 4f);
        await Seconds(1f);
        Shot("5_collapse");
        await Seconds(3.5f);
        Check(!GodotObject.IsInstanceValid(fire), "the blaze is gone after its collapse");
        thing.GetChild(0).QueueFree();
        var smoulder = Fire.Smoulder(thing, box);
        await Seconds(2f);
        Shot("6_smoulder");
        Fire.Burst(NavigationServer3D.MapGetClosestPoint(Map, Pos + new Vector3(-5f, 0f, 4f)), 2f);
        Fire.Splash(Pos + new Vector3(3f, 1f, 3f), 1f);
        await Seconds(0.35f);
        Shot("7_burst_splash");
        smoulder.QueueFree();

        bool arrived = false;
        var arrow = new Node3D();
        arrow.AddChild(new MeshInstance3D { Mesh = new BoxMesh { Size = new Vector3(0.05f, 0.8f, 0.05f) } });
        var target = Pos + new Vector3(10f, 0f, 0f);
        var m = Missile.Fly(arrow, Pos + Vector3.Up * 1.4f, target + Vector3.Up, 15f, 0f, Vector3.Zero, Vector3.One, () => arrived = true);
        float secs = m.Seconds;
        await Seconds(secs * 0.5f);
        Shot("8_missile");
        Check(await Until(() => arrived, 3f), $"missile arrived ({secs:F2} s flight)");

        var spots = KitGround.Scatter(Pos, 1f, 6, 7);
        float floorOff = spots.Max(s => Mathf.Abs(NavigationServer3D.MapGetClosestPoint(Map, s.pos).Y - s.pos.Y));
        float apart = spots.SelectMany((a, i) => spots.Skip(i + 1).Select(b => (a.pos - b.pos).Length())).Min();
        Check(spots.Count == 6 && floorOff < 0.3f, $"scatter: 6 spots on the floor (within {floorOff:F2} m of the navmesh), {apart:F2} m apart at least");

        // a silhouette, a usable thing, a walkway deck
        await Go("VKI_Tavern_F0");
        level = GetTree().CurrentScene;
        var cam = walker.Camera;
        await Stand(new Vector3(5f, 0.1f, -4f));
        // a creature right behind the south wall (the navmesh's south edge below the walker): the wall hides its feet
        Vector3 hid = Vector3.Zero;
        foreach (float dx in new[] { -3f, -4f, -2.5f, 3f, 4f, -5f })                             // off the door, past the tables
        {
            hid = NavigationServer3D.MapGetClosestPoint(Map, Pos + new Vector3(dx, 0f, 0f));
            for (int i = 0; i < 80; i++)                                                           // south till the floor ends
            {
                var q = hid + new Vector3(0f, 0f, 0.2f);
                var c = NavigationServer3D.MapGetClosestPoint(Map, q);
                if (new Vector2(c.X - q.X, c.Z - q.Z).Length() > 0.3f) break;
                hid = c;
            }
            if (hid.Z > Pos.Z + 2f) break;
        }
        bool found = hid.Z > Pos.Z + 2f;
        Check(found, $"a floor spot behind something: {hid}");
        if (found)
        {
            var creature = new Node3D { Name = "Creature" };
            level.AddChild(creature);
            creature.GlobalPosition = hid;
            creature.AddChild(new MeshInstance3D { Mesh = new CapsuleMesh { Radius = 0.25f, Height = 0.6f }, Position = new Vector3(0, 0.3f, 0) });
            await Wait(4);
            var px = (Vector2I)cam.UnprojectPosition(hid + Vector3.Up * 0.3f);
            var flickers = KitNodes.Below(level, "").OfType<FireFlicker>().ToList();
            foreach (var f in flickers) f.SetProcess(false);              // (the two frames differ by the silhouette only)
            foreach (var ps in FireFx.Parts(level)) ps.SpeedScale = 0;
            await Wait(2);
            var before = GetViewport().GetTexture().GetImage();
            CreatureSilhouettes.Tag(creature, true);
            CreatureSilhouettes.Tag(walker, false);
            await Wait(4);
            var after = GetViewport().GetTexture().GetImage();
            Shot("9_silhouette");
            foreach (var f in flickers) f.SetProcess(true);
            foreach (var ps in FireFx.Parts(level)) ps.SpeedScale = 1;
            int red = 0, away = 0;                                       // pixels turned red round the creature, and away from it
            for (int y = 0; y < after.GetHeight(); y += 2)
                for (int x = 0; x < after.GetWidth(); x += 2)
                {
                    Color b0 = before.GetPixel(x, y), a0 = after.GetPixel(x, y);
                    if (a0.R - b0.R < 0.04f || b0.G - a0.G < 0.04f || a0.R < a0.G + 0.08f) continue;   // (redder and less green: not a flicker)
                    if (Mathf.Abs(x - px.X) < 80 && Mathf.Abs(y - px.Y) < 80) red++; else away++;
                }
            Check(red >= 8 && away * 4 <= red, $"silhouette: {red * 4} pixels turned red where the creature is hidden, {away * 4} elsewhere");
            creature.QueueFree();
        }

        var post = new KitTestThing { Name = "Post" };
        level.AddChild(post);
        post.GlobalPosition = NavigationServer3D.MapGetClosestPoint(Map, Pos + new Vector3(-3f, 0f, -2f));
        await Wait(3);
        legs.Screen = cam.UnprojectPosition(post.GlobalPosition + Vector3.Up * 0.6f);
        await Wait(3);
        Check(legs.HoverThing == post, $"the usable thing under the cursor ({legs.HoverThing?.Name ?? "none"}; way out {legs.Hover?.LinkId ?? "none"})");
        legs.Press = true; legs.Held = true;
        await Wait(2);
        legs.Held = false;
        Check(await Until(() => post.Uses > 0, 6f), $"clicked: walked {new Vector2(Pos.X - post.GlobalPosition.X, Pos.Z - post.GlobalPosition.Z).Length():F2} m to it and used it ({post.Uses} use)");

        var deckAt = NavigationServer3D.MapGetClosestPoint(Map, Pos + new Vector3(2f, 0f, 1f));
        var deck = new MeshInstance3D { Name = "TestDeck", Mesh = new BoxMesh { Size = new Vector3(3f, 1f, 1.5f) } };
        level.AddChild(deck);
        deck.GlobalPosition = deckAt + Vector3.Up * 0.5f;
        KitWalkways.Names = () => new[] { "TestDeck" };
        level.RemoveMeta("kit_walkways");
        KitWalkways.Ensure(level);
        await Wait(4);
        var top = deckAt + Vector3.Up * 1f;
        var near = NavigationServer3D.MapGetClosestPoint(Map, top + Vector3.Up * 0.2f);
        Check(near.DistanceTo(top) < 0.25f, $"walkway deck: navmesh on its top ({near.DistanceTo(top):F2} m off), a body to click: {deck.HasNode("Deck")}");
        KitWalkways.Names = null;
    }
}
#endif
