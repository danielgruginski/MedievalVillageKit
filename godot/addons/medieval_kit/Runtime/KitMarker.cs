using Godot;

namespace MedievalKit;

/// <summary>An empty from the Blender scene: spawn points (SPN_, as KitSpawn), light and effect anchors (LGT_, FXA_),
/// the level root (VKI_Root).</summary>
[GlobalClass]
public partial class KitMarker : Marker3D
{
    public enum MarkerKind { Other, Spawn, LightAnchor, FxAnchor, Root }

    [Export] public MarkerKind Kind;
    [Export] public Godot.Collections.Dictionary<string, string> Props = new();

    public static MarkerKind KindOf(string name) =>
        name.StartsWith("SPN_") ? MarkerKind.Spawn : name.StartsWith("LGT_") ? MarkerKind.LightAnchor
        : name.StartsWith("FXA_") ? MarkerKind.FxAnchor : name.StartsWith("VKI_Root") ? MarkerKind.Root : MarkerKind.Other;
}
