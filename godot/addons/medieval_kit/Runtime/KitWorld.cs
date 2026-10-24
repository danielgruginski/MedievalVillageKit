using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>The world graph (docs/WORLD_GRAPH.md): every level, its links and where each link arrives. A level is a
/// scene of the same name (res://kit/layouts/&lt;name&gt;.tscn). Built from res://kit/data/world.json by KitBuilder;
/// hand-made levels can be added to it. Targets "@return" (back to where the walker came in) and "@deep" (an open end)
/// are holes, not levels.</summary>
[GlobalClass]
public partial class KitWorld : Resource
{
    [Export] public string Start = "";
    [Export] public Godot.Collections.Array<KitWorldLevel> Levels = new();

    public KitWorldLevel Find(string name) => Levels.FirstOrDefault(l => l.Name == name);

    /// <summary>The link in `target` a walker lands at when coming from `from` through link `via`.</summary>
    public string ArrivalFor(string from, string via, string target)
    {
        var src = Find(from)?.Links.FirstOrDefault(l => l.Id == via);
        if (src != null && !string.IsNullOrEmpty(src.Arrive)) return src.Arrive;
        var t = Find(target);
        if (t == null) return null;
        var back = t.Links.Where(l => l.Target == from).ToList();
        if (back.Count == 1) return back[0].Id;                             // the arrival rule: exactly one link back
        var ret = t.Links.Where(l => l.Target == "@return").ToList();
        return back.Count == 0 && ret.Count == 1 ? ret[0].Id : null;        // into a building: its door (@return)
    }
}
