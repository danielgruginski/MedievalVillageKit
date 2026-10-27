using System.Collections.Generic;
using Godot;

namespace MedievalKit;

/// <summary>The pointer's one question to the game: is it on the game's own UI? Then the wheel does not zoom and a
/// click does not walk. Unset, never. Unity: KitPointer.</summary>
public static class KitPointer
{
    /// <summary>screen point (pixels) -> on the game's UI</summary>
    public static System.Func<Vector2, bool> Blocked;

    public static bool BlockedAt(Vector2 screen) => Blocked != null && Blocked(screen);
}

/// <summary>
/// The kit's play camera and the see-through's driver, Unity's KitCamera on Godot's axes. The kit's view (looking north,
/// Godot -Z, 50 degrees down), never turned. Follows <see cref="Target"/> smoothly, cuts with it between levels
/// (KitTravel.Arrived), the mouse wheel zooms between <see cref="ZoomNear"/> and <see cref="ZoomFar"/>. The listener
/// stands at the target. The sun's shadows are drawn only as far as the view reaches. Optionally it stops short of a
/// level's border (<see cref="KeepInBorder"/>: <see cref="KitWalkWindow"/> over the level's <see cref="KitMapFrame"/>).
/// <para>The see-through: each frame it sets the shader's globals (kit_see_through, kit_see_through_args) round the
/// target, decides the buildings (<see cref="KitSeeThrough.DecideAll"/>) and, with <see cref="SeeThroughWhenHidden"/>,
/// opens the hole only while kit pieces really hide the target (<see cref="KitSeeThroughProbe"/>), with hysteresis.
/// Without it (or another driver) the shader draws everything whole.</para>
/// <para>Hooks: <see cref="MapFrameOf"/>, <see cref="Entered"/>, <see cref="KitPointer.Blocked"/>; or subclass it.
/// Differences from Unity: a level's own cameras need no switching off (the current camera alone draws), and the
/// backdrop stays the level's environment. FULL_PORT_PLAN phase 6.</para>
/// </summary>
[GlobalClass]
public partial class KitCamera : Camera3D
{
    [Export] public Node3D Target;
    [Export] public float Pitch = 50f;
    [Export] public float Distance = 22f;
    [Export] public float ZoomNear = 13f, ZoomFar = 32f;
    [Export] public float ViewFov = 30f;
    /// <summary>follow lag (s)</summary>
    [Export] public float Smooth = 0.12f;
    [ExportGroup("See-through")]
    /// <summary>the hole's radius round the target (m); 0 turns it off</summary>
    [Export] public float SeeThroughRadius = 2.4f;
    /// <summary>kept below this height over the target's feet (the ground, low and cut walls)</summary>
    [Export] public float KeepBelow = 1.4f;
    /// <summary>only pieces in the target's way fade: those reaching into the wedge from the camera to its body, this far
    /// (m) each side of it (under the navmesh agent's radius); 0: every piece in the hole's cone</summary>
    [Export] public float SeeThroughBody = 0.2f;
    /// <summary>kept whole this far (m) in front of the target, level (an eave over it, a post beside it)</summary>
    [Export] public float SeeThroughNear = 0.25f;
    /// <summary>open the hole only while kit pieces really hide the target (the hidden check); off: always open</summary>
    [Export] public bool SeeThroughWhenHidden = true;
    /// <summary>the share of the target's upper body hidden to open the hole, and under which it shuts</summary>
    [Export] public float SeeThroughCoverOpen = 0.12f, SeeThroughCoverShut = 0.04f;
    /// <summary>how long the hole takes to open and to shut (s), and how long it stays open once the target is seen</summary>
    [Export] public float SeeThroughOpenTime = 0.2f, SeeThroughShutTime = 0.35f, SeeThroughHold = 0.3f;
    [ExportGroup("Border")]
    [Export] public bool KeepInBorder = false;
    [Export] public float BorderPad = 3f;
    /// <summary>the part of the screen the target is kept in (viewport: left, bottom, right, top)</summary>
    [Export] public Vector4 KeepIn = new Vector4(0.15f, 0.22f, 0.85f, 0.82f);
    [Export] public float BorderLag = 0.35f;

    /// <summary>a level's map frame (by KitTravel's level name; null: none). For <see cref="KeepInBorder"/>.</summary>
    public static System.Func<string, KitMapFrame> MapFrameOf;
    /// <summary>the camera took a level over (true: outdoors, a level with a node in the "kit_village" group): the game's
    /// ambience</summary>
    public static System.Action<bool> Entered;

    Vector3 vel;
    AudioListener3D ears;
    readonly KitWalkWindow border = new KitWalkWindow();
    KitSeeThroughProbe probe;
    float seeOpen;
    double seeHiddenAt = -99;
    readonly Dictionary<DirectionalLight3D, float> shadowRest = new Dictionary<DirectionalLight3D, float>();
    readonly List<DirectionalLight3D> suns = new List<DirectionalLight3D>();

    /// <summary>the hidden check's last answer: the share of the target's upper body hidden (-1: no check)</summary>
    public float SeeThroughCover => probe != null ? probe.Cover : -1f;
    /// <summary>how far the hole is open (0 shut .. 1 open)</summary>
    public float SeeThroughOpen => seeOpen;
    public KitSeeThroughProbe Probe => probe;

    static double Now => Time.GetTicksMsec() / 1000.0;

    public override void _Ready()
    {
        TopLevel = true;
        Fov = ViewFov; Near = 0.3f; Far = 400f;
        ears = new AudioListener3D { Name = "Ears", TopLevel = true };
        AddChild(ears);
        ProcessPriority = 100;                                       // after the walkers move
        KitTravel.Arrived += OnArrived;
        TakeOver();
        Snap();
    }

    public override void _ExitTree()
    {
        KitTravel.Arrived -= OnArrived;
        KitSeeThrough.Set(Vector4.Zero, KitSeeThrough.Args);                    // the editor's views stay whole
        foreach (var kv in shadowRest) if (GodotObject.IsInstanceValid(kv.Key)) kv.Key.DirectionalShadowMaxDistance = kv.Value;
        shadowRest.Clear();
    }

    void OnArrived(string level, KitSpawn spawn) { TakeOver(); Snap(); }

    /// <summary>this camera and its ears current; the game hears where it is (outdoors or not)</summary>
    protected virtual void TakeOver()
    {
        MakeCurrent();
        ears?.MakeCurrent();
        suns.Clear();
        foreach (var n in GetTree().Root.FindChildren("*", "DirectionalLight3D", true, false))
            if (n is DirectionalLight3D l && l.ShadowEnabled) suns.Add(l);
        bool outdoors = GetTree().GetFirstNodeInGroup("kit_village") != null;
        Entered?.Invoke(outdoors);
    }

    Basis Rot => Basis.FromEuler(new Vector3(-Mathf.DegToRad(Pitch), 0f, 0f));      // north is Godot -Z
    Vector3 Forward => -Rot.Z;
    /// <summary>where the camera wants to be, looking at its focus (dt: the border's easing step; 0: at once)</summary>
    Vector3 Want(float dt) => Focus(dt) + Vector3.Up - Forward * Distance;

    /// <summary>jump to the target at once (after a cut: a level change, a teleport); the hidden check asks again</summary>
    public void Snap()
    {
        if (Target == null || !IsInstanceValid(Target)) return;
        border.Reset();
        GlobalTransform = new Transform3D(Rot, Want(0f));
        vel = Vector3.Zero;
        seeOpen = 0f; seeHiddenAt = -99;
        probe?.Forget();
    }

    Vector3 Focus(float dt)
    {
        var p = Target.GlobalPosition;
        if (!KeepInBorder || MapFrameOf == null) return p;
        var d = KitTravel.Travelling ? null : MapFrameOf(KitTravel.CurrentLevel);
        if (d == null || d.FogW <= 0) return p;
        var uv = d.ToMap(p);
        if (uv.X < -0.3f || uv.X > 1.3f || uv.Y < -0.3f || uv.Y > 1.3f) return p;
        Seen(d, out var view, out var keep);
        var pad = new Vector2(BorderPad / Mathf.Max(1f, d.Right.Length()), BorderPad / Mathf.Max(1f, d.Down.Length()));
        var f = border.Fit(d, uv, view, keep, pad, dt <= 0f ? 1f : 1f - Mathf.Exp(-dt / Mathf.Max(0.01f, BorderLag)));
        var w = d.FromMap(f);
        return new Vector3(w.X, p.Y, w.Y);
    }

    /// <summary>the ground the camera sees round its focus at this zoom, on the map frame: the whole view and the part the
    /// target is kept in</summary>
    void Seen(KitMapFrame d, out Rect2 view, out Rect2 keep)
    {
        var o = Vector3.Up - Forward * Distance;
        var size = GetViewport().GetVisibleRect().Size;
        float aspect = size.Y > 0 ? size.X / size.Y : 16f / 9f;
        float ty = Mathf.Tan(Mathf.DegToRad(Fov * 0.5f)), tx = ty * aspect;
        var rot = Rot;
        Vector2 Ground(float x, float y)
        {
            var dir = rot * new Vector3((2f * x - 1f) * tx, (2f * y - 1f) * ty, -1f);
            var g = o + dir * (dir.Y < -1e-3f ? -o.Y / dir.Y : 200f);
            return d.MapDelta(new Vector2(g.X, g.Z));
        }
        view = Box(Ground(0f, 0f), Ground(1f, 0f), Ground(0f, 1f), Ground(1f, 1f), false);
        keep = Box(Ground(KeepIn.X, KeepIn.Y), Ground(KeepIn.Z, KeepIn.Y), Ground(KeepIn.X, KeepIn.W), Ground(KeepIn.Z, KeepIn.W), true);
    }

    static Rect2 Box(Vector2 a, Vector2 b, Vector2 c, Vector2 e, bool inner)
    {
        float[] us = { a.X, b.X, c.X, e.X }, vs = { a.Y, b.Y, c.Y, e.Y };
        System.Array.Sort(us); System.Array.Sort(vs);
        int lo = inner ? 1 : 0, hi = inner ? 2 : 3;
        return new Rect2(us[lo], vs[lo], us[hi] - us[lo], vs[hi] - vs[lo]);
    }

    public override void _UnhandledInput(InputEvent e)
    {
        if (e is not InputEventMouseButton { Pressed: true } mb || KitPointer.BlockedAt(mb.Position)) return;
        if (mb.ButtonIndex == MouseButton.WheelUp) Distance = Mathf.Clamp(Distance - 1.5f, ZoomNear, ZoomFar);
        else if (mb.ButtonIndex == MouseButton.WheelDown) Distance = Mathf.Clamp(Distance + 1.5f, ZoomNear, ZoomFar);
    }

    public override void _Process(double delta)
    {
        if (Target == null || !IsInstanceValid(Target)) return;
        float dt = Mathf.Min((float)delta, 0.1f);
        GlobalTransform = new Transform3D(Rot, SmoothDamp(GlobalPosition, Want(dt), ref vel, Smooth, dt));
        var p = Target.GlobalPosition;
        if (ears != null) ears.GlobalTransform = new Transform3D(Basis.Identity, p + Vector3.Up * 1.6f);
        SeeThrough(p, dt);
        FitShadows();
    }

    /// <summary>Unity's Vector3.SmoothDamp (Game Programming Gems 4)</summary>
    static Vector3 SmoothDamp(Vector3 cur, Vector3 target, ref Vector3 v, float smooth, float dt)
    {
        smooth = Mathf.Max(0.0001f, smooth);
        float omega = 2f / smooth, x = omega * dt, exp = 1f / (1f + x + 0.48f * x * x + 0.235f * x * x * x);
        var change = cur - target;
        var temp = (v + omega * change) * dt;
        v = (v - omega * temp) * exp;
        var output = target + (change + temp) * exp;
        if ((target - cur).Dot(output - target) > 0) { output = target; v = (output - target) / Mathf.Max(dt, 1e-5f); }
        return output;
    }

    /// <summary>the see-through round the target (feet p): the hole opens while kit pieces hide the target and shuts when
    /// it is seen again, growing from and shrinking to its middle</summary>
    void SeeThrough(Vector3 p, float dt)
    {
        Vector4 Hole() => new Vector4(p.X, p.Y + 1f, p.Z, SeeThroughRadius * Mathf.SmoothStep(0f, 1f, seeOpen));
        var args = new Vector4(p.Y, KeepBelow, SeeThroughNear, SeeThroughBody);
        KitSeeThrough.Set(Hole(), args);
        float want = 1f;
        if (SeeThroughWhenHidden && SeeThroughRadius > 0f)
        {
            probe ??= KitSeeThroughProbe.For(this);
            probe.Look(p, 1f);
            if (probe.Reads > 0 && probe.Cover > (seeOpen > 0f ? SeeThroughCoverShut : SeeThroughCoverOpen)) seeHiddenAt = Now;
            want = Now - seeHiddenAt < SeeThroughHold ? 1f : 0f;
        }
        seeOpen = Mathf.MoveToward(seeOpen, want, dt / Mathf.Max(0.01f, want > seeOpen ? SeeThroughOpenTime : SeeThroughShutTime));
        var hole = Hole();
        KitSeeThrough.Set(hole, args);
        KitSeeThrough.DecideAll(GlobalPosition, hole, args);
        KitSeeThroughCaps.LayPool(this);
    }

    /// <summary>the sun's shadows drawn only as far as the view reaches: the ground the screen's top corners see, plus a
    /// margin for a shadow cast in from just outside (the light's own distance the most)</summary>
    void FitShadows()
    {
        float half = Fov * 0.5f;
        float down = Mathf.DegToRad(Pitch - half);
        float reach = 400f;
        if (down > 0.05f)
        {
            var size = GetViewport().GetVisibleRect().Size;
            float aspect = size.Y > 0 ? size.X / size.Y : 16f / 9f;
            float h = Distance * Mathf.Sin(Mathf.DegToRad(Pitch)) + 1f;
            float side = Mathf.Atan(Mathf.Tan(Mathf.DegToRad(half)) * aspect);
            reach = h / Mathf.Sin(down) / Mathf.Cos(side) + 4f;
        }
        foreach (var l in suns)
        {
            if (!IsInstanceValid(l)) continue;
            if (!shadowRest.ContainsKey(l)) shadowRest[l] = l.DirectionalShadowMaxDistance;
            float want = Mathf.Clamp(reach, 25f, shadowRest[l] + 5f);
            if (Mathf.Abs(l.DirectionalShadowMaxDistance - want) > 0.5f) l.DirectionalShadowMaxDistance = want;
        }
    }
}
