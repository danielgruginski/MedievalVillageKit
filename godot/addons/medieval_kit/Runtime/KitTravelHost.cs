using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>KitTravel's helper (made on demand, a child of the tree's root, so it outlives the levels): the fade over a
/// plain load and the background preloading of the current level's link targets. Unity: KitTravelHost.</summary>
public partial class KitTravelHost : Node
{
    public bool Fading { get; private set; }

    ColorRect black;
    float alpha;
    double fadeT = -1;
    string fadeTarget, fadeArrive;
    bool refresh;

    public override void _Ready()
    {
        var layer = new CanvasLayer { Layer = 128 };
        black = new ColorRect { Color = new Color(0, 0, 0, 0), MouseFilter = Control.MouseFilterEnum.Ignore };
        black.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        layer.AddChild(black);
        AddChild(layer);
    }

    /// <summary>a plain load without a fade (preloading off): the target replaces the current level next frame</summary>
    public void LoadNow(string target, string arrive) =>
        Callable.From(() => KitTravel.Replace(GD.Load<PackedScene>(KitTravel.ScenePath(target)).Instantiate(), arrive)).CallDeferred();

    /// <summary>fade to black, load the target, fade back</summary>
    public void FadeLoad(string target, string arrive)
    {
        Fading = true;
        fadeTarget = target;
        fadeArrive = arrive;
        fadeT = 0;
    }

    /// <summary>held and loading round the current level, checked next frame: what it no longer links to freed, what it
    /// does requested (threaded loads)</summary>
    public void Refresh() => refresh = true;

    public override void _Process(double delta)
    {
        if (fadeT >= 0) StepFade(delta);
        if (refresh && !Fading)
        {
            refresh = false;
            var want = KitTravel.Neighbours(KitTravel.Tree.CurrentScene);
            foreach (var name in KitTravel.held.Keys.ToList())
                if (!want.Contains(name)) { KitTravel.held[name].QueueFree(); KitTravel.held.Remove(name); }
            foreach (var name in want)
            {
                if (KitTravel.held.ContainsKey(name) || KitTravel.preloading.Contains(name)) continue;
                if (ResourceLoader.LoadThreadedRequest(KitTravel.ScenePath(name)) == Error.Ok) KitTravel.preloading.Add(name);
            }
        }
        foreach (var name in KitTravel.preloading.ToList())
        {
            string path = KitTravel.ScenePath(name);
            var status = ResourceLoader.LoadThreadedGetStatus(path);
            if (status == ResourceLoader.ThreadLoadStatus.InProgress) continue;
            KitTravel.preloading.Remove(name);
            if (status != ResourceLoader.ThreadLoadStatus.Loaded) { GD.PushWarning($"[KitTravel] preload of {name} failed"); continue; }
            KitTravel.held[name] = ((PackedScene)ResourceLoader.LoadThreadedGet(path)).Instantiate();
            if (KitTravel.waiting is { } w && w.target == name)
            {
                KitTravel.waiting = null;
                KitTravel.Switch(w.target, w.arrive);
            }
        }
    }

    void StepFade(double delta)
    {
        double t = KitTravel.FadeSeconds;
        fadeT += delta;
        if (fadeTarget != null)
        {
            alpha = (float)Mathf.Min(fadeT / t, 1.0);
            if (fadeT >= t + delta)                     // the black frame has shown: load (the stall happens under it)
            {
                var scene = GD.Load<PackedScene>(KitTravel.ScenePath(fadeTarget)).Instantiate();
                KitTravel.Replace(scene, fadeArrive);
                fadeTarget = null;
                fadeT = 0;
            }
        }
        else
        {
            alpha = (float)Mathf.Max(1.0 - fadeT / t, 0.0);
            if (fadeT >= t) { fadeT = -1; alpha = 0; Fading = false; }
        }
        black.Color = new Color(0, 0, 0, alpha);
    }
}
