#if TOOLS
using System;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Godot;

namespace MedievalKit.Editor;

/// <summary>kit_cli's chain commands (KitChainTools), run once the node stands in the tree, then quit:
/// chains sample &lt;chain.tres&gt; [seed] | chains bake &lt;chain.tres&gt; | chains validate [count] [first seed] |
/// chains stream &lt;play.tscn&gt; (the play scene run: the streamer loads the first map and places the walker; the walker
/// is put in each piece in turn and the pieces the streamer holds are checked: the one it stands in and its
/// neighbours, nothing two joins away)</summary>
public partial class KitChainsCli : Node
{
    string[] args = Array.Empty<string>();
    int fails;
    readonly StringBuilder log = new();

    public void Setup(string[] a) => args = a;

    public override void _Ready() => Callable.From(() => { _ = Run(); }).CallDeferred();

    string Arg(int i, string fallback) => i < args.Length && args[i] != "" ? args[i] : fallback;
    void Say(string s) { log.AppendLine(s); GD.Print("[chains] " + s); }
    void Check(bool ok, string what) { Say($"{(ok ? "ok  " : "FAIL")} {what}"); if (!ok) fails++; }
    async Task Frames(int n) { for (int i = 0; i < n; i++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame); }

    async Task Run()
    {
        try
        {
            switch (Arg(0, ""))
            {
                case "sample": Say(KitChainTools.CreateSample(this, Arg(1, "res://kit_chains/SampleChain.tres"), int.Parse(Arg(2, "1")))); break;
                case "bake": Say(KitChainTools.Bake(this, Arg(1, ""))); break;
                case "validate": Say(KitChainTools.ValidateChains(this, int.Parse(Arg(1, "5")), int.Parse(Arg(2, "1")))); break;
                case "stream": await Stream(Arg(1, "res://kit_chains/SampleChain/SampleChain_Play.tscn")); break;
                default: GD.PushError("kit_cli chains: sample <chain.tres> [seed] | bake <chain.tres> | validate [count] [first] | stream <play.tscn>"); fails++; break;
            }
        }
        catch (Exception e) { Say("FAIL " + e); fails++; }
        GetTree().Quit(fails == 0 ? 0 : 1);
    }

    async Task<bool> Until(Func<bool> done, int frames)
    {
        for (int i = 0; i < frames; i++) { if (done()) return true; await Frames(1); }
        return done();
    }

    async Task Stream(string playPath)
    {
        var play = GD.Load<PackedScene>(playPath).Instantiate<Node3D>();
        GetTree().Root.AddChild(play);
        var st = KitNodes.Below(play, "").OfType<KitChainStreamer>().First();
        var w = st.walker;
        var chain = st.chain;
        Check(await Until(() => st.Loaded.Contains(chain.pieces[0].id), 600), $"first map {chain.pieces[0].id} loaded");
        await Frames(2);
        Check(chain.At(w.GlobalPosition)?.id == chain.pieces[0].id, $"walker on its spawn in {chain.pieces[0].id} ({w.GlobalPosition})");
        foreach (var p in chain.pieces)
        {
            // stand on one of the piece's spawns (on the floor, inside its footprint)
            var spawn = st.Loaded.Contains(p.id) ? KitNodes.Below(st, "").OfType<KitSpawn>().FirstOrDefault(s => p.spawns.Contains(s.SpawnId) && p.footprint.HasPoint(new Vector2(s.GlobalPosition.X, s.GlobalPosition.Z))) : null;
            var at = spawn?.GlobalPosition ?? new Vector3(p.footprint.GetCenter().X, 0f, p.footprint.GetCenter().Y);
            if (w is CharacterBody3D cb) cb.Velocity = Vector3.Zero;
            w.GlobalPosition = at;
            var want = chain.Around(p.id, st.reach);
            bool held = await Until(() => want.All(id => st.Loaded.Contains(id)), 900);
            var far = st.Loaded.Where(id => !chain.Around(p.id, st.reach + 1).Contains(id)).ToList();
            await Frames(3);
            far = st.Loaded.Where(id => !chain.Around(p.id, st.reach + 1).Contains(id)).ToList();
            Check(held && far.Count == 0 && st.Current == p.id,
                  $"in {p.id}: current {st.Current}, held [{string.Join(", ", st.Loaded)}]" + (far.Count > 0 ? $", not freed: {string.Join(", ", far)}" : ""));
        }
        Say(fails == 0 ? "STREAM ALL PASS" : $"STREAM {fails} FAILED");
    }
}
#endif
