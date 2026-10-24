using System;
using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>Moves the walker between levels: loads the link's target level and puts the walker on the arrival spawn.
/// "@return" goes back through the link the walker came in by (building doors). The walker is whatever was registered
/// with SetWalker (or the first node in the "player" group); it must live outside the level scenes (a child of the
/// tree's root, not of a level), which are freed when left. Games can listen to Arrived instead of relying on the
/// default placement. The arrival spawn: the link's Arrive, else the kit world's rule (its one link back), else the
/// spawn named like the link (both ends of a stair share its id).
/// Preloading (Preload, off by default): the levels the current one's links lead to are loaded in the background
/// (ResourceLoader's threaded loads) and held instantiated outside the tree, so taking a link is an instant cut: the
/// level left is taken out of the tree and held while it is one link away (else freed), the target put in and made
/// the current scene, the walker placed. A level not held yet loads the plain way behind a short fade; a journey that
/// waits on one (Pending, PendingLevel: a game can say "Loading...") cuts when it is in. Unity: KitTravel (its chain
/// streaming comes with the KitChainStreamer port).</summary>
public static class KitTravel
{
    public static event Action<string, KitSpawn> Arrived;       // level, spawn (null if none was found)
    public static event Action<KitLink> Leaving;

    /// <summary>a level name -> its scene: the kit's built levels by default; a game maps its own</summary>
    public static Func<string, string> ScenePath = name => KitPaths.LayoutScenes + name + ".tscn";
    /// <summary>hold the current level's link targets loaded, for instant cuts (off: the held levels are freed)</summary>
    public static bool Preload
    {
        get => preload;
        set
        {
            preload = value;
            if (value) { Host.Refresh(); return; }
            foreach (var h in held.Values) h.QueueFree();
            held.Clear();
        }
    }
    /// <summary>the fade of a plain load (seconds each way)</summary>
    public static float FadeSeconds = 0.18f;
    /// <summary>the levels held, ready for an instant cut</summary>
    public static IEnumerable<string> Held => held.Keys;
    public static bool Travelling => host != null && host.Fading;
    /// <summary>a journey was asked for and waits on its level's preload (the cut happens when it is ready)</summary>
    public static bool Pending => waiting.HasValue;
    /// <summary>the level a waiting journey waits on (null: none)</summary>
    public static string PendingLevel => waiting?.target;

    static bool preload;
    static Node3D walker;
    static (string level, string link)? pendingReturn;              // the way back, kept if one arrives on a "@return" door
    static readonly Stack<(string level, string link)> returns = new();
    internal static readonly Dictionary<string, Node> held = new();
    internal static readonly HashSet<string> preloading = new();
    internal static (string target, string arrive)? waiting;        // a link taken while its level was still loading
    static KitTravelHost host;

    public static void SetWalker(Node3D w) => walker = w;
    public static Node3D Walker => IsInstanceValid(walker) ? walker : Tree.GetFirstNodeInGroup("player") as Node3D;
    /// <summary>a walker was registered (a game's player): stand-ins (KitTestWalker) step aside</summary>
    public static bool HasWalker => IsInstanceValid(walker);
    public static string CurrentLevel => LevelOf(Tree.CurrentScene);
    public static int ReturnDepth => returns.Count;
    /// <summary>the door the current building was entered by (level, link id; null: none): one interior shared by many
    /// houses is told apart by it</summary>
    public static (string level, string link)? Entered => returns.Count > 0 ? returns.Peek() : null;
    /// <summary>the doors to return through, innermost first (a game's save keeps them)</summary>
    public static (string level, string link)[] ReturnStack => returns.ToArray();
    /// <summary>a door to return through, outermost first (a game's load puts the saved ones back after its GoTo)</summary>
    public static void PushReturn(string level, string link) { if (!string.IsNullOrEmpty(level)) returns.Push((level, link)); }
    /// <summary>forget a journey still waiting on its level's preload (the walker died, a menu opened...)</summary>
    public static void CancelPending() => waiting = null;

    internal static SceneTree Tree => (SceneTree)Engine.GetMainLoop();
    static bool IsInstanceValid(GodotObject o) => o != null && GodotObject.IsInstanceValid(o);
    internal static string LevelOf(Node scene) =>
        scene is KitLevel l && !string.IsNullOrEmpty(l.LevelName) ? l.LevelName : scene?.Name.ToString();
    internal static bool Exists(string level) => !string.IsNullOrEmpty(level) && ResourceLoader.Exists(ScenePath(level));

    static KitTravelHost Host
    {
        get
        {
            if (!IsInstanceValid(host))
            {
                host = new KitTravelHost { Name = "KitTravel" };
                Tree.Root.CallDeferred(Node.MethodName.AddChild, host);
            }
            return host;
        }
    }

    public static bool Go(KitLink link)
    {
        string from = CurrentLevel, target = link.Target, arrive = link.Arrive;
        if (target == "@deep" || string.IsNullOrEmpty(target))
        {
            GD.Print($"[KitTravel] {link.LinkId}: no level beyond ({target})");
            return false;
        }
        if (target == "@return")
        {
            if (returns.Count == 0) { GD.PushWarning($"[KitTravel] {from}: nowhere to return to"); return false; }
            (target, arrive) = returns.Pop();
            pendingReturn = null;
        }
        else
        {
            if (string.IsNullOrEmpty(arrive))
                arrive = (Tree.CurrentScene as KitLevel)?.World?.ArrivalFor(from, link.LinkId, target);
            if (string.IsNullOrEmpty(arrive)) arrive = link.LinkId;
            // arriving on a building's "@return" door, the way back is remembered (Arrive; not when coming down its own
            // stairs: those land on the stair, not the door)
            pendingReturn = (from, link.LinkId);
        }
        if (!Exists(target))
        {
            GD.PushError($"[KitTravel] level '{target}' has no scene ({ScenePath(target)})");
            return false;
        }
        if (Travelling) return false;                               // one journey at a time
        Leaving?.Invoke(link);
        return Start(target, arrive);
    }

    /// <summary>to a level's spawn without a link (a respawn, a teleport): the way back is forgotten; an instant cut when
    /// the level is held, else a load behind the fade; in the current level the walker is just placed</summary>
    public static bool GoTo(string target, string spawn)
    {
        if (!Exists(target)) { GD.PushError($"[KitTravel] level '{target}' has no scene"); return false; }
        if (Travelling) return false;
        returns.Clear(); pendingReturn = null; waiting = null;
        if (target == CurrentLevel) { Arrive(Tree.CurrentScene, spawn); return true; }
        return Start(target, spawn);
    }

    /// <summary>to a level's spawn on a fresh load, whatever is held or current: every level as built, not as the last
    /// visit left it (a game's New Game or Load, which put back what they keep themselves); the way back is forgotten.
    /// Always the fade and a plain load (which drops every held level).</summary>
    public static bool Reload(string target, string spawn)
    {
        if (!Exists(target)) { GD.PushError($"[KitTravel] level '{target}' has no scene"); return false; }
        if (Travelling) return false;
        returns.Clear(); pendingReturn = null; waiting = null;
        Host.FadeLoad(target, spawn);
        return true;
    }

    static bool Start(string target, string arrive)
    {
        if (preload && held.ContainsKey(target)) { Switch(target, arrive); return true; }
        if (preload && preloading.Contains(target)) { waiting = (target, arrive); return true; }
        if (preload) Host.FadeLoad(target, arrive);
        else Host.LoadNow(target, arrive);
        return true;
    }

    /// <summary>the instant cut: the level here taken out of the tree and held, the held target put in, made current,
    /// the walker placed</summary>
    internal static void Switch(string target, string arrive)
    {
        var from = Tree.CurrentScene;
        var to = held[target];
        held.Remove(target);
        if (from != null)
        {
            from.GetParent()?.RemoveChild(from);
            held[LevelOf(from)] = from;
        }
        Tree.Root.AddChild(to);
        Tree.CurrentScene = to;
        Arrive(to, arrive);
        Host.Refresh();
    }

    /// <summary>a freshly loaded level replaces the current one (every held level is dropped: a plain load)</summary>
    internal static void Replace(Node scene, string arrive)
    {
        var from = Tree.CurrentScene;
        if (from != null) { from.GetParent()?.RemoveChild(from); from.QueueFree(); }
        foreach (var h in held.Values) h.QueueFree();
        held.Clear();
        Tree.Root.AddChild(scene);
        Tree.CurrentScene = scene;
        Arrive(scene, arrive);
        if (preload) Host.Refresh();
    }

    static IEnumerable<Node> Below(Node n)
    {
        foreach (Node c in n.GetChildren())
        {
            yield return c;
            foreach (var d in Below(c)) yield return d;
        }
    }

    static void Arrive(Node scene, string id)
    {
        var spawn = Below(scene).OfType<KitSpawn>().FirstOrDefault(s => s.SpawnId == id);
        var back = Below(scene).OfType<KitLink>().FirstOrDefault(l => l.LinkId == id);
        Node3D at = spawn ?? (Node3D)back;     // no spawn: stand at the link itself (a hand-made door without a KitSpawn)
        if (pendingReturn != null && back != null && back.Target == "@return") returns.Push(pendingReturn.Value);
        pendingReturn = null;
        string level = LevelOf(scene);
        if (at == null) GD.PushWarning($"[KitTravel] {level}: no spawn or link '{id}'");
        else if (spawn == null) GD.Print($"[KitTravel] {level}: no spawn '{id}', placed at its link");
        var w = Walker;
        if (at != null && w != null) Place(w, at.GlobalTransform);
        Arrived?.Invoke(level, spawn);
    }

    /// <summary>put a walker somewhere: a body stops moving, a NavigationAgent3D below it forgets its path</summary>
    public static void Place(Node3D w, Transform3D t)
    {
        w.GlobalTransform = new Transform3D(t.Basis.Orthonormalized(), t.Origin);
        if (w is CharacterBody3D cb) cb.Velocity = Vector3.Zero;
        foreach (var agent in w.FindChildren("*", "NavigationAgent3D", true, false).OfType<NavigationAgent3D>())
            agent.TargetPosition = t.Origin;
    }

    /// <summary>the levels the current one's links lead to (its "@return" door: the level it returns to)</summary>
    internal static HashSet<string> Neighbours(Node scene)
    {
        var set = new HashSet<string>();
        if (scene == null) return set;
        string self = LevelOf(scene);
        foreach (var l in Below(scene).OfType<KitLink>())
        {
            string t = l.Target == "@return" ? (returns.Count > 0 ? returns.Peek().level : null) : l.Target;
            if (!string.IsNullOrEmpty(t) && t != "@deep" && t != self && Exists(t)) set.Add(t);
        }
        return set;
    }
}
