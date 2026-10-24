using Godot;

namespace MedievalKit;

/// <summary>One link of a world-graph level (KitWorldLevel).</summary>
[GlobalClass]
public partial class KitWorldLink : Resource
{
    [Export] public string Id = "";
    [Export] public string Kind = "";       // exit, passage, stair_up, stair_down, lift
    [Export] public string Target = "";     // a level name, "@return" or "@deep"
    [Export] public string Arrive = "";     // the link id it lands at in the target (empty: the target's link back here)
}
