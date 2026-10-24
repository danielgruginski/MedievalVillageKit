using Godot;

namespace MedievalKit;

/// <summary>Level root: camera settings and links from VKI_Root (Props), and the world graph the level belongs to.</summary>
[GlobalClass]
public partial class KitLevel : Node3D
{
    [Export] public string LevelName = "";
    [Export] public string BlenderScene = "";
    [Export] public string ExportVersion = "";
    [Export] public Godot.Collections.Dictionary<string, string> Props = new();
    [Export] public KitWorld World;
}
