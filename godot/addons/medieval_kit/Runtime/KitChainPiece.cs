using Godot;

namespace MedievalKit;

/// <summary>A baked piece of a <see cref="KitChain"/>: a map or a connector, its scene and where it lies in the world.
/// Unity: KitChain.Piece.</summary>
[GlobalClass]
public partial class KitChainPiece : Resource
{
    [Export] public string id = "";
    /// <summary>the scene's path (res://...tscn); its root, a KitRoom, already stands where it lies in the world</summary>
    [Export(PropertyHint.File, "*.tscn")] public string scene = "";
    [Export] public Vector3 position;
    /// <summary>its map on the ground: world x / z (the rock ring round it left out)</summary>
    [Export] public Rect2 footprint;
    [Export] public string[] neighbours = System.Array.Empty<string>();
    /// <summary>its KitSpawn ids (where scene links into the chain arrive)</summary>
    [Export] public string[] spawns = System.Array.Empty<string>();
}
