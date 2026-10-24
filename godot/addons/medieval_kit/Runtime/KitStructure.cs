using Godot;

namespace MedievalKit;

/// <summary>Root of a premade structure (res://kit/structures/&lt;name&gt;.tscn, built by KitBuilder.BuildStructures from
/// gdx_export_structures): which Blender builder made it. Unity: KitStructure.</summary>
[GlobalClass]
public partial class KitStructure : Node3D
{
    [Export] public string StructureName = "";
    [Export] public string Builder = "";        // e.g. build_smithy (vk_helpers)
    [Export] public string ExportVersion = "";
}
