using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>a screen ray: where it starts and its direction (unit)</summary>
public readonly record struct PointerRay(Vector3 From, Vector3 Dir)
{
    public Vector3 At(float t) => From + Dir * t;
}

/// <summary>what a screen ray met: the point, how far along the ray, the collider (a body, or a link's Area3D)</summary>
public readonly record struct PointerHit(Vector3 Point, float Distance, Node Collider);

/// <summary>
/// A walker's legs, Diablo / Baldur's Gate style: hold the left button to walk toward the cursor, click the ground to walk
/// there; click a way out (a door, stair, cave mouth: a <see cref="KitLink"/>) to walk to it and take it. Road ends at a
/// map's edge (KitLink.WalkInto) are taken by walking on into them, once the walker has stepped clear of the one it
/// arrived by. Clicks the game's UI takes stay there (Godot's GUI eats them before _UnhandledInput; and
/// <see cref="KitPointer"/>). A child of the walker's body (any Node3D), which it moves; walks the levels' baked navmesh
/// (KitNavMesh); travels with KitTravel, preloading on, so the levels one link away are held ready and a door is an
/// instant cut. Unity: KitClickToMove (FULL_PORT_PLAN phase 6).
/// <para>The point walked to is the floor under the cursor the walker can reach (<see cref="Ground"/>): the ray looks
/// through what the see-through has opened (<see cref="KitSeeThrough.Opened"/>) and past crates and roofs to the floor
/// behind; while the button is held the way round an obstacle is kept (<see cref="Hold"/>), so the walker does not swing
/// between going left and right of it.</para>
/// <para>Godot: the walker follows its own way along the navmesh (Unity's NavMeshAgent; a NavigationAgent3D cannot take a
/// way worked out ahead, which the held button's flip check needs): <see cref="Speed"/>, <see cref="Acceleration"/>,
/// <see cref="TurnSpeed"/> as the agent's. Not yet here: things to use (Unity's Interactable, port phase 6's 3a systems)
/// and houses whose door the camera cannot see (Unity's HouseUnder: Godot has no village builder yet).</para>
/// <para>A game adds its own rules in a subclass: <see cref="Under"/>, <see cref="Press"/>, <see cref="Take"/>,
/// <see cref="Offers"/>, <see cref="PassesThrough"/> and the small hooks (<see cref="Halted"/>, <see cref="ReadsPointer"/>,
/// <see cref="TakesClicks"/>, <see cref="Walking"/>, <see cref="Went"/>, <see cref="Pointer"/>).</para>
/// </summary>
[GlobalClass]
public partial class KitClickToMove : Node
{
    /// <summary>how near a way out's trigger counts as at it (m)</summary>
    [Export] public float Reach = 0.9f;
    /// <summary>seconds between new destinations while the button is held</summary>
    [Export] public float Repath = 0.1f;
    /// <summary>while held: a new way only once the point under the cursor moved this far (m)</summary>
    [Export] public float RepathMove = 0.3f;
    /// <summary>while held: the way round an obstacle stays the one taken until the cursor's point is this far from where it leads (m)</summary>
    [Export] public float KeepWay = 2.5f;
    /// <summary>while held with the cursor on something unwalkable: the spot walked to changes only when another is this much nearer what the cursor points at (m)</summary>
    [Export] public float Stick = 0.75f;
    /// <summary>the walker's top speed (m/s), how fast it gets there (m/s²), how fast it turns (degrees a second)</summary>
    [Export] public float Speed = 4.5f, Acceleration = 30f, TurnSpeed = 720f;
    /// <summary>how near the way's end counts as there (m)</summary>
    [Export] public float StoppingDistance = 0.05f;
    /// <summary>the camera whose view the cursor is on (null: the viewport's)</summary>
    public Camera3D Cam;

    protected Node3D body;
    /// <summary>the way out walked to (taken on arrival)</summary>
    protected KitLink target;
    /// <summary>the button is held (hold-to-walk); a road's end may be walked into (stepped clear of the arrival one);
    /// a held way was refused as a flip (walked to when the button comes up)</summary>
    protected bool holding, armed, refused;
    /// <summary>two things the ray meets this close (m) count as at the same spot</summary>
    protected const float Tie = 0.05f;
    double nextRepath;
    Vector3 aimed;
    bool pressed;                                                   // a press came since the last frame
    Vector3[] way;                                                  // the way walked (navmesh corners; null: standing)
    int corner;                                                     // the corner walked to
    Vector3 velocity;
    int settle = -1;                                                // frames to wait for a level's navmesh before standing on it
    ulong settleFrom;

    /// <summary>the way out under the cursor (its prompt shows)</summary>
    public KitLink Hover { get; protected set; }
    /// <summary>a click sent the walker somewhere (the walkable point): a pointer's ring goes there</summary>
    public event System.Action<Vector3> Clicked;
    /// <summary>the walker moved (this node's parent)</summary>
    public Node3D Body => body;
    public bool HasPath => way != null;
    /// <summary>where the way ends (where it stands when it has none)</summary>
    public Vector3 Destination => way != null ? way[^1] : body.GlobalPosition;
    public Vector3 Velocity => velocity;
    Vector3 Steering => way != null ? way[Mathf.Min(corner, way.Length - 1)] : body.GlobalPosition;
    Rid Map => body.GetWorld3D().NavigationMap;
    static double Now => Time.GetTicksMsec() / 1000.0;

    public override void _Ready()
    {
        body = GetParent<Node3D>();
        body.AddToGroup("player");
        KitTravel.SetWalker(body);
        KitTravel.Arrived += OnArrived;
        KitTravel.Preload = true;
        Settle();
    }

    public override void _ExitTree() => KitTravel.Arrived -= OnArrived;

    protected virtual void OnArrived(string level, KitSpawn spawn)
    {
        target = null; holding = false; armed = false; refused = false;
        way = null; velocity = Vector3.Zero;
        Settle();
    }

    /// <summary>stand on the navmesh once the level's has joined the map (it joins at the map's next update)</summary>
    void Settle() { settle = 12; settleFrom = body != null && body.IsInsideTree() ? NavigationServer3D.MapGetIterationId(Map) : 0; }

    public override void _UnhandledInput(InputEvent e)
    {
        if (e is InputEventMouseButton { ButtonIndex: MouseButton.Left, Pressed: true } mb && !KitPointer.BlockedAt(mb.Position))
            pressed = true;
    }

    // ------------------------------------------------------------------ the game's hooks

    /// <summary>the walker takes no orders now (dead, mid-swing): no hover, no walking</summary>
    protected virtual bool Halted => false;
    /// <summary>this walker reads the pointer</summary>
    protected virtual bool ReadsPointer => true;
    /// <summary>this walker's clicks and holds walk it</summary>
    protected virtual bool TakesClicks => true;
    /// <summary>the walker was sent walking by the pointer</summary>
    protected virtual void Walking() { }
    /// <summary>the walker went through a way out (a door's sound)</summary>
    protected virtual void Went(KitLink l) { }
    /// <summary>clear what is under the cursor (every frame, before <see cref="Under"/>)</summary>
    protected virtual void ClearHover() { Hover = null; }

    /// <summary>the pointer this frame: where it is on the screen, pressed since the last frame, held now. False: no
    /// pointer. The mouse; a test or a gamepad cursor brings its own.</summary>
    protected virtual bool Pointer(out Vector2 screen, out bool press, out bool held)
    {
        screen = GetViewport().GetMousePosition();
        press = pressed;
        pressed = false;
        held = Input.IsMouseButtonPressed(MouseButton.Left);
        return true;
    }

    // ------------------------------------------------------------------ the navmesh (Unity's NavMesh calls)

    bool NavReady => NavigationServer3D.MapGetRegions(Map).Count > 0;

    /// <summary>the navmesh's nearest point to p within r (Unity: NavMesh.SamplePosition)</summary>
    protected bool Sample(Vector3 p, float r, out Vector3 at)
    {
        at = default;
        if (!NavReady) return false;
        at = NavigationServer3D.MapGetClosestPoint(Map, p);
        return at.DistanceTo(p) <= r;
    }

    /// <summary>the walker stands on the navmesh (Unity: agent.isOnNavMesh)</summary>
    protected bool OnNavMesh => Sample(body.GlobalPosition, 0.5f, out _);

    /// <summary>the way from the walker toward p along the navmesh (to the reachable point nearest p); null: none</summary>
    protected Vector3[] WayTo(Vector3 p)
    {
        var c = NavigationServer3D.MapGetPath(Map, body.GlobalPosition, p, true);
        return c.Length >= 2 ? c : null;
    }

    /// <summary>whether the navmesh ends along the level line from a toward b, and where (Unity: NavMesh.Raycast; Godot has
    /// none: walked in 0.2 m steps, a step off the navmesh or onto another floor ends it)</summary>
    protected bool NavRay(Vector3 a, Vector3 b, out Vector3 edge)
    {
        edge = a;
        if (!NavReady) return true;
        var d = b - a; d.Y = 0f;
        int n = Mathf.Max(1, Mathf.CeilToInt(d.Length() / 0.2f));
        float y = a.Y;
        for (int i = 1; i <= n; i++)
        {
            var p = a + d * (i / (float)n);
            p.Y = y;
            var c = NavigationServer3D.MapGetClosestPoint(Map, p);
            if (Flat(c - p) > 0.1f || Mathf.Abs(c.Y - y) > 0.5f) return true;
            edge = c; y = c.Y;
        }
        return false;
    }

    // ------------------------------------------------------------------ walking

    /// <summary>walk to a point (the nearest walkable spot to it)</summary>
    public void MoveTo(Vector3 p)
    {
        target = null; refused = false;
        aimed = p;
        SetDestination(p);
    }

    /// <summary>everything a screen ray meets, nearest first (areas: link triggers too; Unity: Physics.RaycastAll)</summary>
    public PointerHit[] Cast(PointerRay ray, bool areas = false)
    {
        var space = body.GetWorld3D().DirectSpaceState;
        var skip = new Godot.Collections.Array<Rid>();
        var q = new PhysicsRayQueryParameters3D { From = ray.From, To = ray.At(500f), CollideWithAreas = areas, CollideWithBodies = true };
        var hits = new List<PointerHit>();
        for (int i = 0; i < 32; i++)
        {
            q.Exclude = skip;
            var r = space.IntersectRay(q);
            if (r.Count == 0) break;
            var p = (Vector3)r["position"];
            hits.Add(new PointerHit(p, (p - ray.From).Dot(ray.Dir), r["collider"].AsGodotObject() as Node));
            skip.Add((Rid)r["rid"]);
        }
        return hits.ToArray();
    }

    /// <summary>a hit on walkable floor (the navmesh right at it; it may still be out of reach)</summary>
    protected bool IsFloor(PointerHit h, out Vector3 p) => Sample(h.Point, 0.5f, out p) && Mathf.Abs(p.Y - h.Point.Y) <= 0.4f;

    /// <summary>the floor the walker can walk to under a screen ray (see the hits overload)</summary>
    public bool Ground(PointerRay ray, out Vector3 p) => Ground(Cast(ray), ray, out p, out _, out _);

    /// <summary>
    /// The floor the walker can walk to under a screen ray (its hits nearest first). 1: the first floor along it the
    /// walker can reach without a long way round: the ray looks through what it meets first -- a crate or a stall, a
    /// wall or a roof, a rock -- to the floor just behind (exact). 2: else the reachable point nearest the navmesh within
    /// 3 m of the first thing hit: the tops of those things carry navmesh the walker cannot reach (the bake keeps every
    /// flat top), and the way toward one ends beside it, so the walker walks up to the house clicked and slides along
    /// the wall the cursor is beyond. 3: else (the cursor over nothing) toward the point at the walker's level.
    /// `pointed` is what the cursor points at. False when the walker is off the navmesh.
    /// </summary>
    public bool Ground(PointerHit[] hits, PointerRay ray, out Vector3 p, out bool exact, out Vector3 pointed)
    {
        p = default; exact = false;
        var pos = body.GlobalPosition;
        var level = new Plane(Vector3.Up, pos);
        pointed = hits.Length > 0 ? hits[0].Point : level.IntersectsRay(ray.From, ray.Dir) ?? ray.At(30f);
        if (!OnNavMesh) return false;
        foreach (var h in hits)
        {
            if (!IsFloor(h, out var f) || !PathEnd(f, out _, out bool whole, out float len) || !whole) continue;
            if (len > Flat(f - pos) * 1.5f + 2f) break;                      // behind a wall, a long way round
            p = f; exact = true;
            return true;
        }
        if (Sample(pointed, hits.Length > 0 ? 3f : 4f, out var s) && PathEnd(s, out p, out _, out _)) return true;
        p = NavRay(pos, pointed, out var edge) ? edge : pos;
        return true;
    }

    /// <summary>where a way from the walker toward q ends (q itself when whole; the nearest reachable point when not)
    /// and how long it is</summary>
    bool PathEnd(Vector3 q, out Vector3 end, out bool whole, out float len)
    {
        end = default; whole = false; len = 0f;
        var c = NavigationServer3D.MapGetPath(Map, body.GlobalPosition, q, true);
        if (c.Length == 0) return false;
        for (int i = 1; i < c.Length; i++) len += c[i - 1].DistanceTo(c[i]);
        end = c[^1];
        whole = end.DistanceTo(q) < 0.15f;
        return true;
    }

    /// <summary>one step of hold-to-walk toward the floor under a ray (see the hits overload)</summary>
    public void Hold(PointerRay ray) => Hold(Cast(ray), ray);

    /// <summary>
    /// One step of hold-to-walk toward the floor under a ray (the held button does this every <see cref="Repath"/>
    /// seconds). The way is worked out again only once the cursor's point moved (<see cref="RepathMove"/>); a point that
    /// is only the nearest reachable one (the cursor on a roof, a rock, a wall) changes only when it is clearly nearer
    /// what the cursor points at (by <see cref="Stick"/>): at a corner both sides are about as near, and the walker would
    /// go to and fro; and a new way that only flips round the same obstacle the other way is refused for a while
    /// (<see cref="Flip"/>). A point refused when the button comes up is walked to then.
    /// </summary>
    public void Hold(PointerHit[] hits, PointerRay ray)
    {
        if (!Ground(hits, ray, out var aim, out bool exact, out var pointed)) return;
        target = null;
        Walking();
        if (!exact)
        {
            var keep = Destination;
            if (Flat(keep - pointed) <= Flat(aim - pointed) + Stick) aim = keep;
        }
        if (HasPath && Flat(aim - aimed) < RepathMove) return;
        aimed = aim; refused = false;
        if (Flat(aim - body.GlobalPosition) < 0.3f) { way = null; return; }   // on the walker: stand
        var w = WayTo(aim);
        if (w == null) return;
        if (Flip(w, aim)) { refused = true; return; }
        Follow(w);
    }

    /// <summary>a new way round the same obstacle the other way: the walker is going round something (its way bends
    /// ahead) and the new way does too, setting off more than 80 degrees from the walker's heading, toward a point near
    /// where the old way ends (<see cref="KeepWay"/>) and in plain view of it. A straight new way (turning on open
    /// ground) or one beyond a fence or a wall from the old end (the way round by its gate) is never refused.</summary>
    bool Flip(Vector3[] w, Vector3 aim) =>
        HasPath && velocity.LengthSquared() > 0.25f && w.Length > 2 &&
        (Steering - Destination).LengthSquared() > 0.01f && !SameWay(w) &&
        Flat(aim - Destination) < KeepWay && !NavRay(Destination, aim, out _);

    /// <summary>the new way sets off roughly where the walker is heading now</summary>
    bool SameWay(Vector3[] w)
    {
        Vector3 now = Steering - body.GlobalPosition, next = w[1] - body.GlobalPosition;
        now.Y = 0f; next.Y = 0f;
        return now.LengthSquared() < 0.04f || next.LengthSquared() < 0.04f || Mathf.RadToDeg(now.AngleTo(next)) < 80f;
    }

    /// <summary>walk to a way out and take it</summary>
    public void Interact(KitLink link)
    {
        target = link; refused = false;
        SetDestination(DoorPoint(link));
    }

    protected bool SetDestination(Vector3 p)
    {
        if (!OnNavMesh || !Sample(p, 3f, out var h)) return false;
        var w = WayTo(h);
        if (w == null) { way = null; return false; }                      // (already there)
        Follow(w);
        return true;
    }

    void Follow(Vector3[] w) { way = w; corner = 1; }

    /// <summary>stop where it stands (its way dropped)</summary>
    protected void Stop() => way = null;

    public override void _PhysicsProcess(double delta)
    {
        if (body == null) return;
        if (settle >= 0 && NavReady && (NavigationServer3D.MapGetIterationId(Map) != settleFrom || settle == 0))
        {
            settle = -1;
            if (Sample(body.GlobalPosition, 3f, out var on)) body.GlobalPosition = on;
        }
        else if (settle > 0) settle--;
        ClearHover();
        if (KitTravel.Travelling || KitTravel.Pending || Halted) { holding = false; pressed = false; }
        else Think();
        Walk((float)delta);
    }

    void Think()
    {
        var c = Cam != null && IsInstanceValid(Cam) ? Cam : GetViewport().GetCamera3D();
        if (ReadsPointer && c != null && Pointer(out var screen, out bool press, out bool held))
        {
            bool clicks = TakesClicks;
            if (!KitPointer.BlockedAt(screen))
            {
                var ray = new PointerRay(c.ProjectRayOrigin(screen), c.ProjectRayNormal(screen));
                var hits = Cast(ray);                                            // one cast a frame: hover, click and hold
                Under(hits, ray, c);
                if (clicks && press && !Press(hits, ray))
                {
                    Walking();
                    holding = true;
                    nextRepath = Now + Repath;
                    if (Ground(hits, ray, out var p, out _, out _))
                    {
                        MoveTo(p);
                        if (HasPath) Clicked?.Invoke(Destination);
                    }
                }
                if (clicks && holding && Now >= nextRepath && held)
                {
                    nextRepath = Now + Repath;
                    Hold(hits, ray);
                }
            }
            if (!held)
            {
                if (holding && refused) { refused = false; SetDestination(aimed); }   // let go mid-refusal: that point still counts
                holding = false;
            }
        }
        // at a way out
        var here = LinksHere();
        if (target != null && (here.Contains(target) || Near(target))) { Take(target); return; }
        if (here.Count == 0) armed = true;
        else if (armed)
            foreach (var l in here)
                if (l.WalkInto && Offers(l)) { Take(l); return; }
    }

    /// <summary>one step along the way: toward its next corner at up to <see cref="Speed"/>, slowing to stop at its end,
    /// turning to face where it goes; the height from the navmesh under it</summary>
    void Walk(float dt)
    {
        var pos = body.GlobalPosition;
        var want = Vector3.Zero;
        float left = 0f;
        if (way != null)
        {
            while (corner < way.Length - 1 && Flat(way[corner] - pos) < 0.1f) corner++;
            left = Flat(way[corner] - pos);
            for (int i = corner + 1; i < way.Length; i++) left += Flat(way[i] - way[i - 1]);
            if (left <= StoppingDistance) { way = null; left = 0f; }
            else
            {
                var to = way[corner] - pos; to.Y = 0f;
                want = to.Normalized() * Mathf.Min(Speed, Mathf.Sqrt(2f * Acceleration * left));
            }
        }
        velocity = velocity.MoveToward(want, Acceleration * dt);
        if (velocity.LengthSquared() < 1e-6f) { velocity = Vector3.Zero; return; }
        var step = velocity * dt;
        if (way != null && corner == way.Length - 1 && step.Length() > left) step = step.Normalized() * left;   // not past the end
        var next = pos + step;
        if (way != null)                                                       // the height: along the way, then onto the navmesh
        {
            var a = way[Mathf.Max(0, corner - 1)]; var b = way[corner];
            float seg = Flat(b - a);
            next.Y = seg > 1e-3f ? Mathf.Lerp(a.Y, b.Y, Mathf.Clamp(1f - Flat(b - next) / seg, 0f, 1f)) : b.Y;
        }
        if (NavReady)
        {
            var on = NavigationServer3D.MapGetClosestPoint(Map, next);
            if (Flat(on - next) < 0.05f && Mathf.Abs(on.Y - next.Y) < 0.5f) next.Y = on.Y;
        }
        body.GlobalPosition = next;
        var flat = new Vector3(velocity.X, 0f, velocity.Z);
        if (flat.LengthSquared() > 0.01f)
        {
            var from = body.GlobalBasis.GetRotationQuaternion();
            var to = Basis.LookingAt(flat.Normalized(), Vector3.Up).GetRotationQuaternion();
            float ang = from.AngleTo(to), turn = Mathf.DegToRad(TurnSpeed) * dt;
            body.GlobalBasis = new Basis(ang <= turn ? to : from.Slerp(to, turn / ang));
        }
    }

    /// <summary>a click on what is under the cursor (<see cref="Under"/>): a way out is walked to and taken. False:
    /// nothing taken, the click walks to the floor.</summary>
    protected virtual bool Press(PointerHit[] hits, PointerRay ray)
    {
        if (Hover != null) { Walking(); Interact(Hover); holding = false; return true; }
        return false;
    }

    protected static float Flat(Vector3 v) => new Vector2(v.X, v.Z).Length();

    /// <summary>a link that goes somewhere (a map edge marked "@deep", the world graph's open end, leads nowhere yet)</summary>
    public static bool Leads(KitLink l) => !string.IsNullOrEmpty(l.Target) && l.Target != "@deep";

    /// <summary>a link the cursor and walking on take (a game adds its closed ways, which say why they do not go)</summary>
    protected virtual bool Offers(KitLink l) => Leads(l);

    /// <summary>take a way out the walker is at: travel through it (KitTravel.Go)</summary>
    protected virtual void Take(KitLink l)
    {
        target = null;
        armed = false;                          // not again every frame while standing in it
        if (!Leads(l)) return;                  // an open end that says nothing
        if (KitTravel.Go(l))
        {
            Went(l);
            holding = false;
            Stop();
        }
    }

    /// <summary>what the cursor is on: a way out (where the cursor meets something solid)</summary>
    protected virtual void Under(PointerHit[] hits, PointerRay ray, Camera3D c) => Hover = LinkUnder(ray);

    /// <summary>the cursor's ray passes through this hit to what is behind: what the see-through has opened</summary>
    protected virtual bool PassesThrough(PointerHit h, PointerRay ray) => Opened(h, ray);

    /// <summary>the see-through has opened this hit (<see cref="KitSeeThrough.Opened"/>)</summary>
    public static bool Opened(PointerHit h, PointerRay ray) => KitSeeThrough.Opened(h.Point, h.Distance, ray.From, ray.Dir, h.Collider);

    /// <summary>how far along the ray it meets something solid (<see cref="PassesThrough"/> aside)</summary>
    protected float Surface(PointerHit[] hits, PointerRay ray)
    {
        foreach (var h in hits)
            if (!PassesThrough(h, ray)) return h.Distance;
        return float.MaxValue;
    }

    /// <summary>a way out under the cursor: its trigger hit before anything solid, or the solid thing hit (the door
    /// itself) standing within a stride of a link's trigger. What the see-through has opened does not stop it.</summary>
    protected KitLink LinkUnder(PointerRay ray)
    {
        foreach (var hit in Cast(ray, true))
        {
            if (hit.Collider is Area3D a)
            {
                if (Up<KitLink>(a) is KitLink l && Offers(l)) return l;
                continue;
            }
            if (Opened(hit, ray)) continue;
            foreach (var near in Triggers(hit.Point, 0.8f))
                if (Offers(near)) return near;
            return null;
        }
        return null;
    }

    /// <summary>the links whose triggers reach within r of a point</summary>
    IEnumerable<KitLink> Triggers(Vector3 at, float r)
    {
        var q = new PhysicsShapeQueryParameters3D
        {
            Shape = new SphereShape3D { Radius = r }, Transform = new Transform3D(Basis.Identity, at),
            CollideWithAreas = true, CollideWithBodies = false,
        };
        return body.GetWorld3D().DirectSpaceState.IntersectShape(q, 16)
                   .Select(x => Up<KitLink>(x["collider"].AsGodotObject() as Node)).Where(l => l != null).Distinct();
    }

    static T Up<T>(Node n) where T : class
    {
        for (; n != null; n = n.GetParent()) if (n is T t) return t;
        return null;
    }

    /// <summary>a link's trigger box (null: none)</summary>
    static CollisionShape3D Box(KitLink l) => l.GetChildren().OfType<CollisionShape3D>().FirstOrDefault();

    /// <summary>where a way out is used from: the middle of its trigger (the link itself without one)</summary>
    protected static Vector3 DoorPoint(KitLink l) => Box(l) is CollisionShape3D s ? s.GlobalPosition : l.GlobalPosition;

    List<KitLink> LinksHere() => Triggers(body.GlobalPosition + Vector3.Up * 0.9f, 0.45f).ToList();

    bool Near(KitLink l)
    {
        var p = body.GlobalPosition + Vector3.Up * 0.9f;
        var q = l.GlobalPosition;
        if (Box(l) is CollisionShape3D s && s.Shape is BoxShape3D box)
        {
            var local = s.GlobalTransform.AffineInverse() * p;
            var h = box.Size * 0.5f;
            q = s.GlobalTransform * local.Clamp(-h, h);
        }
        q.Y = body.GlobalPosition.Y;
        return q.DistanceTo(body.GlobalPosition) <= Reach;
    }
}
