using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>
/// Streams a baked <see cref="KitChain"/> round the walker: the piece it stands in and the pieces joined to it stay
/// loaded (scenes loaded in the background, one at a time, put under this node already in place in the world), the
/// rest are freed. Walking into a connector loads the map beyond it while one crosses; leaving a map frees the one
/// behind. Put it in the scene that holds the walker, the camera and the sun (the pieces bring only their own lights).
/// The walker is <see cref="walker"/>, else <see cref="KitTravel.Walker"/>. Arriving by a scene link (<see
/// cref="KitTravel"/>), it starts at the piece holding the arrival spawn instead of the first map. The fields keep the
/// Unity kit's names. Unity: KitChainStreamer.
/// </summary>
[GlobalClass]
public partial class KitChainStreamer : Node3D
{
    [Export] public KitChain chain;
    [Export] public Node3D walker;
    /// <summary>pieces kept loaded round the one the walker stands in, in joins (1: its neighbours)</summary>
    [Export(PropertyHint.Range, "1,4")] public int reach = 1;
    /// <summary>at start: load the first map and put the walker on its way-in spawn</summary>
    [Export] public bool placeWalker = true;
    /// <summary>at start: the spawn to put the walker on (its piece loaded first); empty: the first map's. Set by KitTravel.</summary>
    [Export] public string arrive = "";

    public string Current { get; private set; }
    public IEnumerable<string> Loaded => loaded.Keys;
    readonly Dictionary<string, Node3D> loaded = new();
    string loading;                 // the piece whose scene is loading in the background (one at a time)
    bool started, placing;

    Node3D Walker => walker != null && IsInstanceValid(walker) ? walker : KitTravel.Walker;

    /// <summary>start at this spawn (KitTravel calls it when a scene link arrives in the play scene)</summary>
    public void Arrive(string spawnId)
    {
        arrive = spawnId;
        placeWalker = true;
        if (started) Begin();
    }

    public override void _Ready()
    {
        if (Engine.IsEditorHint()) return;
        if (chain == null || chain.pieces.Count == 0) { GD.PushWarning("[KitChainStreamer] no baked chain"); return; }
        Begin();
    }

    void Begin()
    {
        started = true;
        var first = (string.IsNullOrEmpty(arrive) ? null : chain.WithSpawn(arrive)) ?? chain.pieces[0];
        Current = first.id;
        placing = placeWalker;
    }

    public override void _Process(double delta)
    {
        if (Engine.IsEditorHint() || chain == null || !started) return;
        if (loading != null && !Finish()) return;
        if (placing)                                        // the walker's first place waits for its piece
        {
            if (loaded.TryGetValue(Current, out var here)) Place(here);
            else Request(chain.Find(Current));
            return;
        }
        var w = Walker;
        if (w == null) return;
        var at = chain.At(w.GlobalPosition);
        if (at != null) Current = at.id;
        if (Current == null) return;
        var want = chain.Around(Current, reach);
        var next = want.Select(chain.Find).FirstOrDefault(p => p != null && !loaded.ContainsKey(p.id));
        if (next != null) { Request(next); return; }       // one load per pass
        // free what is two joins beyond the wanted ring (a step back does not reload at once)
        var keep = new HashSet<string>(want.SelectMany(id => chain.Around(id, 1)));
        foreach (var id in loaded.Keys.Where(k => !keep.Contains(k)).ToList())
        {
            loaded[id].QueueFree();
            loaded.Remove(id);
        }
    }

    void Request(KitChainPiece p)
    {
        if (p == null || loaded.ContainsKey(p.id) || loading != null) return;
        if (ResourceLoader.LoadThreadedRequest(p.scene) != Error.Ok) { GD.PushError($"[KitChainStreamer] cannot load {p.scene}"); return; }
        loading = p.id;
    }

    /// <summary>the piece loading in the background, put in once it is ready; true when nothing is loading any more</summary>
    bool Finish()
    {
        var p = chain.Find(loading);
        var status = ResourceLoader.LoadThreadedGetStatus(p.scene);
        if (status == ResourceLoader.ThreadLoadStatus.InProgress) return false;
        loading = null;
        if (status != ResourceLoader.ThreadLoadStatus.Loaded) { GD.PushError($"[KitChainStreamer] {p.scene}: {status}"); return true; }
        var node = ((PackedScene)ResourceLoader.LoadThreadedGet(p.scene)).Instantiate<Node3D>();
        AddChild(node);
        loaded[p.id] = node;
        return true;
    }

    /// <summary>the walker on the arrival spawn of the first piece (or the first map's way in)</summary>
    void Place(Node3D piece)
    {
        placing = false;
        var map = chain.maps.Count > 0 ? chain.maps[0] : null;
        var spawn = KitNodes.Below(piece, "").OfType<KitSpawn>()
            .OrderBy(s => !string.IsNullOrEmpty(arrive) ? (s.SpawnId == arrive ? 0 : 1) : map != null && s.SpawnId == map.outPortal ? 1 : 0)
            .FirstOrDefault();
        var w = Walker;
        if (spawn != null && w != null) KitTravel.Place(w, spawn.GlobalTransform);
        if (!string.IsNullOrEmpty(arrive)) KitTravel.NotifyArrived(KitTravel.LevelOf(GetTree().CurrentScene), spawn);
    }
}
