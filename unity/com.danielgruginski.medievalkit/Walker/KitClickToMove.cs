using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;

namespace MedievalKit
{
    /// <summary>
    /// A walker's legs, Diablo / Baldur's Gate style: hold the left button to walk toward the cursor, click the ground to
    /// walk there; click something to use (an <see cref="Interactable"/>) to walk to it and use it; click a way out (a door,
    /// stair, cave mouth: a <see cref="KitLink"/>) to walk to it and take it -- a house whose door the camera cannot see
    /// (round the back) stands for it (<see cref="HouseUnder"/>). Road ends at a map's edge (KitLink.walkInto) are taken by
    /// walking on into them, once the walker has stepped clear of the one it arrived by. Clicks on the game's UI stay there
    /// (<see cref="KitPointer"/>). Walks the levels' baked navmesh (KitNavMesh); travels with KitTravel, preloading on, so
    /// the levels one link away are held ready and a door is an instant cut.
    /// <para>The point walked to is the floor under the cursor the walker can reach (<see cref="Ground"/>): the ray looks
    /// through what the see-through has opened (<see cref="KitSeeThrough.Opened(RaycastHit, Ray)"/>) and past crates and
    /// roofs to the floor behind; while the button is held the way round an obstacle is kept (<see cref="Hold"/>), so the
    /// walker does not swing between going left and right of it.</para>
    /// <para>A game adds its own rules in a subclass (MedievalSetting: ClickToMove -- creatures to fight, closed ways, the
    /// travel map at a road's end): <see cref="Under"/>, <see cref="Press"/>, <see cref="Take"/>, <see cref="Offers"/>,
    /// <see cref="PassesThrough"/> and the small hooks (<see cref="Halted"/>, <see cref="ReadsPointer"/>,
    /// <see cref="TakesClicks"/>, <see cref="Walking"/>, <see cref="Went"/>). From the Guild RPG's ClickToMove
    /// (FULL_PORT_PLAN phase 3b).</para>
    /// </summary>
    [RequireComponent(typeof(NavMeshAgent))]
    public class KitClickToMove : MonoBehaviour
    {
        [Tooltip("How near a way out's trigger counts as at it (m).")]
        public float reach = 0.9f;
        [Tooltip("Seconds between new destinations while the button is held.")]
        public float repath = 0.1f;
        [Tooltip("While held: a new way only once the point under the cursor moved this far (m).")]
        public float repathMove = 0.3f;
        [Tooltip("While held: the way round an obstacle stays the one taken until the cursor's point is this far from where it leads (m).")]
        public float keepWay = 2.5f;
        [Tooltip("While held with the cursor on something unwalkable: the spot walked to changes only when another is this much nearer what the cursor points at (m).")]
        public float stick = 0.75f;
        [Tooltip("A house whose door faces away from the camera, within this many degrees of its heading (round the back), stands for its door: the cursor on its walls or roof is on the door. 0: off; 180: every house with a door.")]
        public float hiddenDoor = 72f;                      // Greywall's keep_st_6 (69) in; the hamlet's cottage_4 (74), the inn (76) out
        public Camera cam;

        protected NavMeshAgent agent;
        /// <summary>the way out walked to (taken on arrival)</summary>
        protected KitLink target;
        /// <summary>the thing walked to (used on arrival)</summary>
        protected Interactable using_;
        /// <summary>the button is held (hold-to-walk); a road's end may be walked into (stepped clear of the arrival one);
        /// a held way was refused as a flip (walked to when the button comes up)</summary>
        protected bool holding, armed, refused;
        float nextRepath;
        Vector3 aimed;
        NavMeshPath probe;                                  // (made in Awake: Unity refuses one from a field initializer)
        static readonly System.Comparison<RaycastHit> Nearest = (a, b) => a.distance.CompareTo(b.distance);
        readonly List<House> houses = new List<House>();    // the active level's buildings (HouseUnder)
        int housesOf;                                       // the scene they are of (its handle; 0: find them again)
        /// <summary>two things the ray meets this close (m) count as at the same spot</summary>
        protected const float Tie = 0.05f;

        /// <summary>the way out under the cursor (its prompt shows)</summary>
        public KitLink Hover { get; protected set; }
        /// <summary>the usable thing under the cursor</summary>
        public Interactable HoverThing { get; protected set; }
        /// <summary>what the walker is walking to use</summary>
        public Interactable Using => using_;
        /// <summary>a click sent the walker somewhere (the walkable point): a pointer's ring goes there</summary>
        public event System.Action<Vector3> Clicked;
        public NavMeshAgent Agent => agent;

        protected virtual void Awake()
        {
            agent = GetComponent<NavMeshAgent>();
            probe = new NavMeshPath();
            gameObject.tag = "Player";
            DontDestroyOnLoad(gameObject);
            KitTravel.SetWalker(transform);
            KitTravel.Arrived += OnArrived;
            KitTravel.Preload = true;
        }

        protected virtual void OnDestroy() => KitTravel.Arrived -= OnArrived;

        protected virtual void OnArrived(string level, KitSpawn spawn)
        {
            target = null; using_ = null; holding = false; armed = false; refused = false;
            housesOf = 0;                                   // the level's houses are found again (HouseUnder)
        }

        // ------------------------------------------------------------------ the game's hooks

        /// <summary>the walker takes no orders now (dead, mid-swing): no hover, no walking</summary>
        protected virtual bool Halted => false;
        /// <summary>this walker reads the pointer (MedievalSetting: in a party only the member in focus)</summary>
        protected virtual bool ReadsPointer => true;
        /// <summary>this walker's clicks and holds walk it (MedievalSetting: not in a party, where the party's input orders)</summary>
        protected virtual bool TakesClicks => true;
        /// <summary>the walker was sent walking by the pointer (MedievalSetting: it leaves its fight)</summary>
        protected virtual void Walking() { }
        /// <summary>the walker went through a way out (MedievalSetting: a door's sound)</summary>
        protected virtual void Went(KitLink l) { }

        /// <summary>clear what is under the cursor (every frame, before <see cref="Under"/>)</summary>
        protected virtual void ClearHover() { Hover = null; HoverThing = null; }

        // ------------------------------------------------------------------ walking

        /// <summary>walk to a point (the nearest walkable spot to it)</summary>
        public void MoveTo(Vector3 p)
        {
            target = null; using_ = null; refused = false;
            aimed = p;
            SetDestination(p);
        }

        /// <summary>everything a screen ray meets (triggers aside), nearest first</summary>
        public static RaycastHit[] Cast(Ray ray)
        {
            var hits = Physics.RaycastAll(ray, 500f, ~0, QueryTriggerInteraction.Ignore);
            System.Array.Sort(hits, Nearest);
            return hits;
        }

        /// <summary>a hit on walkable floor (the navmesh right at it; it may still be out of reach)</summary>
        protected static bool IsFloor(RaycastHit h, out Vector3 p)
        {
            p = default;
            if (!NavMesh.SamplePosition(h.point, out var nh, 0.5f, NavMesh.AllAreas) || Mathf.Abs(nh.position.y - h.point.y) > 0.4f) return false;
            p = nh.position;
            return true;
        }

        /// <summary>the floor the walker can walk to under a screen ray (see the hits overload)</summary>
        public bool Ground(Ray ray, out Vector3 p) => Ground(Cast(ray), ray, out p, out _, out _);

        /// <summary>
        /// The floor the walker can walk to under a screen ray (its hits nearest first). 1: the first floor along it
        /// the walker can reach without a long way round: the ray looks through what it meets first -- a crate or a
        /// stall, a wall or a roof (one the see-through has faded too), a rock -- to the floor just behind (exact).
        /// 2: else the reachable point nearest the navmesh within 3 m of the first thing hit: the tops of those things
        /// carry navmesh the walker cannot reach (the bake keeps every flat top), and the way toward one ends beside it,
        /// so the walker walks up to the house clicked and slides along the wall the cursor is beyond. 3: else (the
        /// cursor over nothing) toward the point at the walker's level. `pointed` is what the cursor points at.
        /// False when the walker is off the navmesh.
        /// </summary>
        public bool Ground(RaycastHit[] hits, Ray ray, out Vector3 p, out bool exact, out Vector3 pointed)
        {
            p = default; exact = false;
            var level = new Plane(Vector3.up, transform.position);
            pointed = hits.Length > 0 ? hits[0].point : level.Raycast(ray, out float t) ? ray.GetPoint(t) : ray.GetPoint(30f);
            if (!agent.isOnNavMesh) return false;
            foreach (var h in hits)
            {
                if (!IsFloor(h, out var f) || !PathEnd(f, out _, out bool whole, out float len) || !whole) continue;
                if (len > Flat(f - transform.position) * 1.5f + 2f) break;            // behind a wall, a long way round
                p = f; exact = true;
                return true;
            }
            if (NavMesh.SamplePosition(pointed, out var s, hits.Length > 0 ? 3f : 4f, NavMesh.AllAreas) && PathEnd(s.position, out p, out _, out _))
                return true;
            p = NavMesh.Raycast(transform.position, pointed, out var edge, NavMesh.AllAreas) ? edge.position : transform.position;
            return true;
        }

        /// <summary>where a way from the walker toward q ends (q itself when whole; the nearest reachable point when not)
        /// and how long it is</summary>
        bool PathEnd(Vector3 q, out Vector3 end, out bool whole, out float len)
        {
            end = default; whole = false; len = 0f;
            if (!NavMesh.CalculatePath(transform.position, q, NavMesh.AllAreas, probe) || probe.status == NavMeshPathStatus.PathInvalid) return false;
            var c = probe.corners;
            if (c.Length == 0) return false;
            for (int i = 1; i < c.Length; i++) len += Vector3.Distance(c[i - 1], c[i]);
            end = c[c.Length - 1];
            whole = probe.status == NavMeshPathStatus.PathComplete;
            return true;
        }

        /// <summary>one step of hold-to-walk toward the floor under a ray (see the hits overload)</summary>
        public void Hold(Ray ray) => Hold(Cast(ray), ray);

        /// <summary>
        /// One step of hold-to-walk toward the floor under a ray (the held mouse does this every <see cref="repath"/>
        /// seconds). The way is worked out again only once the cursor's point moved (<see cref="repathMove"/>); a point
        /// that is only the nearest reachable one (the cursor on a roof, a rock, a wall) changes only when it is clearly
        /// nearer what the cursor points at (by <see cref="stick"/>): at a corner both sides are about as near, and the
        /// walker would go to and fro; and a new way that only flips round the same obstacle the other way is refused
        /// for a while (<see cref="Flip"/>): for a point just behind a crate the shortest way swaps between left and
        /// right with every small move of the cursor and the camera. A point refused when the button comes up is walked
        /// to then.
        /// </summary>
        public void Hold(RaycastHit[] hits, Ray ray)
        {
            if (!Ground(hits, ray, out var aim, out bool exact, out var pointed)) return;
            target = null; using_ = null;
            Walking();
            if (!exact)
            {
                var keep = agent.hasPath ? agent.destination : transform.position;
                if (Flat(keep - pointed) <= Flat(aim - pointed) + stick) aim = keep;
            }
            if (agent.hasPath && Flat(aim - aimed) < repathMove) return;
            aimed = aim; refused = false;
            if (Flat(aim - transform.position) < 0.3f) { if (agent.hasPath) agent.ResetPath(); return; }    // on the walker: stand
            var path = new NavMeshPath();
            if (!agent.CalculatePath(aim, path) || path.status == NavMeshPathStatus.PathInvalid || path.corners.Length < 2) return;
            if (Flip(path, aim)) { refused = true; return; }
            agent.SetPath(path);
        }

        /// <summary>a new way round the same obstacle the other way: the walker is going round something (its way bends
        /// ahead) and the new way does too, setting off more than 80 degrees from the walker's heading, toward a point near
        /// where the old way ends (<see cref="keepWay"/>) and in plain view of it. A straight new way (turning on open
        /// ground) or one beyond a fence or a wall from the old end (the way round by its gate) is never refused.</summary>
        bool Flip(NavMeshPath path, Vector3 aim) =>
            agent.hasPath && agent.velocity.sqrMagnitude > 0.25f && path.corners.Length > 2 &&
            (agent.steeringTarget - agent.destination).sqrMagnitude > 0.01f && !SameWay(path) &&
            Flat(aim - agent.destination) < keepWay && !NavMesh.Raycast(agent.destination, aim, out _, NavMesh.AllAreas);

        /// <summary>the new way sets off roughly where the walker is heading now</summary>
        bool SameWay(NavMeshPath path)
        {
            Vector3 now = agent.steeringTarget - transform.position, next = path.corners[1] - transform.position;
            now.y = 0f; next.y = 0f;
            return now.sqrMagnitude < 0.04f || next.sqrMagnitude < 0.04f || Vector3.Angle(now, next) < 80f;
        }

        /// <summary>walk to a way out and take it</summary>
        public void Interact(KitLink link)
        {
            target = link; using_ = null; refused = false;
            SetDestination(DoorPoint(link));
        }

        /// <summary>walk to something and use it on arrival</summary>
        public void Interact(Interactable thing)
        {
            target = null; using_ = thing; refused = false;
            if (InReach(thing)) { Use(thing); return; }
            SetDestination(thing.UsePoint);
        }

        protected bool SetDestination(Vector3 p)
        {
            if (!agent.isOnNavMesh) return false;
            if (!NavMesh.SamplePosition(p, out var h, 3f, NavMesh.AllAreas)) return false;
            return agent.SetDestination(h.position);
        }

        /// <summary>stop where it stands (its way dropped)</summary>
        protected void Stop()
        {
            if (agent.isOnNavMesh) agent.ResetPath();
        }

        protected virtual void Update()
        {
            ClearHover();
            if (KitTravel.Travelling || KitTravel.Pending || Halted) { holding = false; return; }
            var c = cam != null ? cam : Camera.main;
            var mouse = ReadsPointer ? Mouse.current : null;
            bool clicks = TakesClicks;
            if (mouse != null && c != null)
            {
                var screen = mouse.position.ReadValue();
                if (!KitPointer.BlockedAt(screen))
                {
                    var ray = c.ScreenPointToRay(screen);
                    var hits = Cast(ray);                                        // one cast a frame: hover, click and hold
                    Under(hits, ray, c);
                    if (clicks && mouse.leftButton.wasPressedThisFrame && !Press(hits, ray))
                    {
                        Walking();
                        holding = true;
                        nextRepath = Time.unscaledTime + repath;
                        if (Ground(hits, ray, out var p, out _, out _))
                        {
                            MoveTo(p);
                            if (agent.hasPath || agent.pathPending) Clicked?.Invoke(agent.destination);
                        }
                    }
                    if (clicks && holding && Time.unscaledTime >= nextRepath && mouse.leftButton.isPressed)
                    {
                        nextRepath = Time.unscaledTime + repath;
                        Hold(hits, ray);
                    }
                }
                if (!mouse.leftButton.isPressed)
                {
                    if (holding && refused) { refused = false; SetDestination(aimed); }   // let go mid-refusal: that point still counts
                    holding = false;
                }
            }
            // at the thing to use
            if (using_ != null)
            {
                if (!using_ || !using_.CanUse) using_ = null;
                else if (InReach(using_) || (!agent.pathPending && agent.hasPath == false && Flat(using_.UsePoint - transform.position) < using_.UseRadius + 1.2f))
                    Use(using_);
            }
            // at a way out
            var here = LinksHere();
            if (target != null && (here.Contains(target) || Near(target))) { Take(target); return; }
            if (here.Count == 0) armed = true;
            else if (armed)
                foreach (var l in here)
                    if (l.walkInto && Offers(l)) { Take(l); return; }
        }

        /// <summary>a click on what is under the cursor (<see cref="Under"/>): a usable thing is walked to and used, a way
        /// out walked to and taken. False: nothing taken, the click walks to the floor.</summary>
        protected virtual bool Press(RaycastHit[] hits, Ray ray)
        {
            if (HoverThing != null) { Walking(); holding = false; Interact(HoverThing); return true; }
            if (Hover != null) { Walking(); Interact(Hover); holding = false; return true; }
            return false;
        }

        protected static float Flat(Vector3 v) => new Vector2(v.x, v.z).magnitude;

        protected bool InReach(Interactable i) => Flat(i.UsePoint - transform.position) <= i.UseRadius;

        protected void Use(Interactable i)
        {
            using_ = null;
            if (agent.isOnNavMesh)
            {
                if (agent.hasPath) agent.ResetPath();
                agent.velocity = Vector3.zero;                         // stand still now (a kneel may check the speed)
            }
            var d = i.transform.position - transform.position; d.y = 0f;
            if (d.sqrMagnitude > 1e-3f) transform.rotation = Quaternion.LookRotation(d);
            i.Use();
        }

        /// <summary>a link that goes somewhere (a map edge marked "@deep", the world graph's open end, leads nowhere yet)</summary>
        public static bool Leads(KitLink l) => !string.IsNullOrEmpty(l.target) && l.target != "@deep";

        /// <summary>a link the cursor and walking on take (MedievalSetting adds the closed ways, which say why they do not go)</summary>
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

        /// <summary>what the cursor is on: a usable thing or a way out, whichever is nearest along the ray (a way out is
        /// where the cursor meets something solid: <see cref="Surface"/>); with neither, a house whose door the camera
        /// cannot see stands for the door (<see cref="HouseUnder"/>)</summary>
        protected virtual void Under(RaycastHit[] hits, Ray ray, Camera c)
        {
            var (th, td, _) = ThingUnder(hits);
            var link = LinkUnder(ray);
            float ld = link != null ? Surface(hits, ray) : float.MaxValue;
            if (th != null && td <= ld + Tie) HoverThing = th;
            else Hover = link != null ? link : HouseUnder(hits, ray, c);
        }

        /// <summary>the cursor's ray passes through this hit to what is behind: what the see-through has opened
        /// (MedievalSetting adds creatures, live or dead)</summary>
        protected virtual bool PassesThrough(RaycastHit h, Ray ray) => KitSeeThrough.Opened(h, ray);

        /// <summary>how far along the ray it meets something solid (<see cref="PassesThrough"/> aside)</summary>
        protected float Surface(RaycastHit[] hits, Ray ray)
        {
            foreach (var h in hits)
                if (!PassesThrough(h, ray)) return h.distance;
            return float.MaxValue;
        }

        /// <summary>a usable thing under the cursor, how far along the ray, how far off the cursor's point: hit anywhere
        /// along the ray (a find's prop stands for it: <see cref="UseVia"/>), or near where the ray meets something
        /// (<see cref="Interactable.Under(Collider, Vector3, out float)"/>) -- the floor behind a rock, not only the rock's top</summary>
        protected static (Interactable, float, float) ThingUnder(RaycastHit[] hits)
        {
            foreach (var h in hits)
            {
                var i = UseVia.Of(h.collider);
                if (i != null && i.CanUse) return (i, h.distance, 0f);
                var near = Interactable.Under(null, IsFloor(h, out var f) ? f : h.point, out float off);
                if (near != null) return (near, h.distance, off);
            }
            return (null, float.MaxValue, float.MaxValue);
        }

        /// <summary>a way out under the cursor: its trigger hit before anything solid, or the solid thing hit (the door
        /// itself) standing within a stride of a link's trigger. What the see-through has opened does not stop it: the
        /// walker at a door round the back of a house sees the door through the house, and the house's box over its walls
        /// is opened with it.</summary>
        protected KitLink LinkUnder(Ray ray)
        {
            foreach (var hit in Physics.RaycastAll(ray, 500f, ~0, QueryTriggerInteraction.Collide).OrderBy(h => h.distance))
            {
                if (hit.collider.isTrigger)
                {
                    var l = hit.collider.GetComponentInParent<KitLink>();
                    if (l != null && Offers(l)) return l;
                    continue;
                }
                if (KitSeeThrough.Opened(hit, ray)) continue;
                foreach (var t in Physics.OverlapSphere(hit.point, 0.8f, ~0, QueryTriggerInteraction.Collide))
                    if (t.isTrigger && t.GetComponentInParent<KitLink>() is KitLink near && Offers(near)) return near;
                return null;
            }
            return null;
        }

        /// <summary>where a way out is used from: the middle of its trigger (the link itself without one)</summary>
        protected static Vector3 DoorPoint(KitLink l) => l.TryGetComponent<Collider>(out var t) ? t.bounds.center : l.transform.position;

        // ------------------------------------------------------------------ houses whose door the camera cannot see

        /// <summary>a building of an outdoor map: its root, its body (in the root's space, <see cref="FindHouses"/>) and
        /// its doors (null: it has none, or none the camera cannot see)</summary>
        struct House { public Transform root; public Bounds body; public KitLink[] doors; }

        /// <summary>how far a house's body reaches past the box over its walls, for the eaves (m)</summary>
        const float Eaves = 0.5f;

        /// <summary>
        /// The door of the house under the cursor, where the camera cannot see it (houses with their doors on the north
        /// had their roof over the cursor: the door's trigger stands behind the house, in the shadow of its box, so no ray
        /// reaches it): the nearest house along the ray (its body), unless the see-through has opened it (the walker
        /// behind it: the floor round the walker is clicked through it) or something solid stands in front of it (a crate,
        /// a tree, a wall), and one of its doors faces away from the camera (<see cref="hiddenDoor"/>): its door nearest
        /// where the ray meets it. A click walks round to it and goes in (<see cref="Interact(KitLink)"/>). A house with no
        /// way in, or with its doors in view, keeps the click (the floor behind it, or up to its wall: <see cref="Ground"/>).
        /// </summary>
        protected KitLink HouseUnder(RaycastHit[] hits, Ray ray, Camera c)
        {
            int scene = SceneManager.GetActiveScene().handle;
            if (scene != housesOf) { housesOf = scene; FindHouses(c); }
            float best = float.MaxValue; int bi = -1;
            for (int i = 0; i < houses.Count; i++)
            {
                var h = houses[i];
                if (h.root == null) continue;
                var local = new Ray(h.root.InverseTransformPoint(ray.origin), h.root.InverseTransformVector(ray.direction));
                if (!h.body.IntersectRay(local, out float t)) continue;
                float d = Vector3.Dot(h.root.TransformPoint(local.GetPoint(Mathf.Max(0f, t))) - ray.origin, ray.direction);
                if (d <= 0f || d >= best || KitSeeThrough.Opened(ray.GetPoint(d), d, ray, h.root)) continue;
                best = d; bi = i;
            }
            if (bi < 0 || houses[bi].doors == null) return null;
            foreach (var h in hits)                                           // nearest first: something solid in front of it
            {
                if (h.distance >= best - 0.05f) break;
                if (!PassesThrough(h, ray)) return null;
            }
            var at = ray.GetPoint(best);
            KitLink door = null; float dd = float.MaxValue;
            foreach (var l in houses[bi].doors)                               // several: the one on the cursor's side
            {
                if (l == null) continue;
                float m = Flat(DoorPoint(l) - at);
                if (m < dd) { dd = m; door = l; }
            }
            return door;
        }

        /// <summary>
        /// The active level's buildings, as its <see cref="KitVillage"/> made them: each under its "Buildings" named by its
        /// id, its door's link taking the same id (LEVEL_BUILDING 5.7), or a link put by hand on one of its pieces. Its
        /// body is the village's box over its walls (4 m high: the one collider a building has, its pieces have none --
        /// the ray goes through a roof to it, or past it to the floor behind) widened by the eaves and raised to 60% of
        /// the house's height: under the eaves of a tall house, so a ray that meets its roof anywhere (one under 50
        /// degrees) comes down into the body over the walls, and one that passes over its far eave comes down beyond it.
        /// A house without a door still hides those behind it. Its doors are kept when one of them faces away from the
        /// camera (<see cref="hiddenDoor"/>: the box's side nearest the door's trigger). Rooms, caves and chains have no
        /// village: no houses.
        /// </summary>
        void FindHouses(Camera c)
        {
            houses.Clear();
            var links = FindObjectsByType<KitLink>(FindObjectsSortMode.None).Where(l => !l.walkInto && Leads(l)).ToList();
            var view = c != null ? c.transform.forward : Vector3.forward;
            view.y = 0f;
            view.Normalize();
            float away = Mathf.Cos(Mathf.Clamp(hiddenDoor, 0f, 180f) * Mathf.Deg2Rad);
            foreach (var v in FindObjectsByType<KitVillage>(FindObjectsSortMode.None))
            {
                var group = v.transform.Find("Buildings");
                if (group == null) continue;
                foreach (Transform b in group)
                {
                    var box = b.GetComponents<BoxCollider>().LastOrDefault(x => x.enabled && !x.isTrigger);   // (added after a piece's own)
                    if (box == null) continue;
                    var walls = new Bounds(box.center, box.size);
                    float wx = walls.extents.x + Eaves, wz = walls.extents.z + Eaves, top = walls.max.y;
                    foreach (var r in b.GetComponentsInChildren<MeshRenderer>())    // its height: what stands over its walls
                    {
                        if (!r.enabled) continue;
                        var rb = r.bounds;
                        var p = b.InverseTransformPoint(rb.center);
                        if (Mathf.Abs(p.x - walls.center.x) > wx || Mathf.Abs(p.z - walls.center.z) > wz) continue;
                        top = Mathf.Max(top, b.InverseTransformPoint(new Vector3(rb.center.x, rb.max.y, rb.center.z)).y);
                    }
                    float low = walls.min.y;
                    var body = new Bounds();
                    body.SetMinMax(new Vector3(walls.center.x - wx, low + 0.3f, walls.center.z - wz),       // (the floor at its foot stays floor)
                                   new Vector3(walls.center.x + wx, Mathf.Max(walls.max.y, low + 0.6f * (top - low)), walls.center.z + wz));
                    var doors = links.Where(l => l.transform.IsChildOf(b) || (l.linkId == b.name && l.transform.IsChildOf(v.transform))).ToArray();
                    bool hidden = hiddenDoor > 0f && doors.Any(l =>
                    {
                        var q = b.InverseTransformPoint(DoorPoint(l));
                        var o = q - walls.ClosestPoint(q);                            // out of the walls' side the door is on
                        if (new Vector2(o.x, o.z).sqrMagnitude < 1e-4f) o = q - walls.center;
                        o = b.TransformDirection(o);
                        o.y = 0f;
                        return o.sqrMagnitude > 1e-6f && Vector3.Dot(o.normalized, view) >= away;
                    });
                    houses.Add(new House { root = b, body = body, doors = hidden ? doors : null });
                }
            }
        }

        List<KitLink> LinksHere() =>
            Physics.OverlapSphere(transform.position + Vector3.up * 0.9f, 0.45f, ~0, QueryTriggerInteraction.Collide)
                   .Where(t => t.isTrigger).Select(t => t.GetComponentInParent<KitLink>()).Where(l => l != null).Distinct().ToList();

        bool Near(KitLink l)
        {
            var t = l.GetComponent<Collider>();
            Vector3 q = t != null ? t.ClosestPoint(transform.position + Vector3.up * 0.9f) : l.transform.position;
            q.y = transform.position.y;
            return Vector3.Distance(q, transform.position) <= reach;
        }
    }
}
