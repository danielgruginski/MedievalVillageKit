using Godot;

namespace MedievalKit;

/// <summary>Where a walker arrives through the link of the same id (Blender's SPN_&lt;id&gt; empties).</summary>
[GlobalClass]
public partial class KitSpawn : KitMarker
{
    [Export] public string SpawnId = "";
    /// <summary>Blender bearing: 0 = Blender +Y, 90 = Blender +X (the builder turns it into this node's basis).</summary>
    [Export] public float FacingDeg;

    /// <summary>Blender bearing -> a Godot basis whose forward (-Z) points that way (Blender +Y is Godot -Z, +X is +X).</summary>
    public static Basis FromBearing(float deg)
    {
        float r = Mathf.DegToRad(deg);
        return Basis.LookingAt(new Vector3(Mathf.Sin(r), 0f, -Mathf.Cos(r)), Vector3.Up);
    }
}
