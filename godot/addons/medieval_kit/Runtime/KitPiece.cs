using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>One kit piece: the root of every imported piece (KitImport puts it there) and so of every placed one. Props
/// are the master's Blender properties, replaced on a placement by the instance's (vki_class, vki_collider, vki_link...).</summary>
[GlobalClass]
public partial class KitPiece : Node3D
{
    /// <summary>collision layers of a piece's StaticBody3D: solid, and passable once the game opens or breaks it (doors
    /// with vki_openable, vki_breakable): the navmesh is baked from Solid only (Unity: KitNavBake leaves them out)</summary>
    public const uint Solid = 1, Passable = 2;

    [Export] public string Piece = "";
    [Export] public Godot.Collections.Dictionary<string, string> Props = new();
    /// <summary>Godot surface i -> the Blender material slot it came from. Styles (plaster, shutter, roof...) are slot
    /// swaps in Blender (vk_helpers.SLOT), so this is how a generator restyles a piece.</summary>
    [Export] public int[] BlenderSlots = System.Array.Empty<int>();

    public MeshInstance3D MeshInstance => KitNodes.Below(this, "MeshInstance3D").OfType<MeshInstance3D>().FirstOrDefault();

    /// <summary>The surface carrying Blender material slot `slot`, or -1.</summary>
    public int SurfaceOfSlot(int slot) => System.Array.IndexOf(BlenderSlots, slot);

    public string Get(string key, string fallback = null) => Props.Get(key, fallback);
    public bool Has(string key) => Props.Has(key);
    public float GetFloat(string key, float fallback = 0f) => Props.GetFloat(key, fallback);

    /// <summary>sets a property on this piece only: the dictionary a placed piece got from its scene is copied first,
    /// so its siblings keep theirs</summary>
    public void Set(string key, string value)
    {
        if (!ownProps) { Props = Props.Duplicate(); ownProps = true; }
        Props[key] = value;
    }

    bool ownProps;

    /// <summary>a 0 / 1 property set and not off ("0", "0.0" -- glTF extras bring whole numbers in as floats -- "False")</summary>
    public bool Flag(string key) => Truthy(Props.Get(key));

    public static bool Truthy(string v) =>
        !string.IsNullOrEmpty(v) && v != "False" && v != "false" &&
        !(float.TryParse(v, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var f) && f == 0f);
}
