using Godot;

namespace MedievalKit;

/// <summary>One level of the world graph (KitWorld): its name (= scene name), kind and links.</summary>
[GlobalClass]
public partial class KitWorldLevel : Resource
{
    [Export] public string Name = "";
    [Export] public string Kind = "";
    [Export] public Godot.Collections.Array<KitWorldLink> Links = new();
}
