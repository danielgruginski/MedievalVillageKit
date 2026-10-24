using Godot;

namespace MedievalKit;

/// <summary>A way out of a level: a door, a stair, a passage, a lift. Its trigger (a box from vki_trigger, Blender
/// piece space) is where a walker can take it, facing it within FacingMin degrees. KitBuilder puts one on every link
/// piece; put one on any piece by hand to link a building you made yourself: set Target to a level name (or
/// "@return") and give the target level a KitSpawn whose SpawnId is where walkers arrive.</summary>
[GlobalClass]
public partial class KitLink : Area3D
{
    [Export] public string LinkId = "";
    [Export] public string Kind = "exit";           // exit, passage, stair_up, stair_down, lift
    [Export] public string Target = "";             // a level name, "@return" or "@deep"
    /// <summary>The spawn id in the target level; empty = the target's only link back to this level.</summary>
    [Export] public string Arrive = "";
    [Export] public string Prompt = "Enter";
    /// <summary>The walker must face the link within this angle (degrees). 0 = any direction.</summary>
    [Export] public float FacingMin = 60f;
    /// <summary>Taken by walking into its trigger (a road's end at the map's edge), not by using it (doors, stairs).</summary>
    [Export] public bool WalkInto;

    public bool CanUse(Node3D walker)
    {
        if (FacingMin <= 0f) return true;
        Vector3 to = GlobalPosition - walker.GlobalPosition;
        to.Y = 0f;
        if (to.LengthSquared() < 1e-4f) return true;
        Vector3 fwd = -walker.GlobalBasis.Z;
        fwd.Y = 0f;
        return Mathf.RadToDeg(fwd.AngleTo(to)) <= FacingMin;
    }

    public void Use() => KitTravel.Go(this);
}
