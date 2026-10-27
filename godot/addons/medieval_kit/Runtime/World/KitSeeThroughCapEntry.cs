using Godot;

namespace MedievalKit;

/// <summary>one baked cap (<see cref="KitSeeThroughCapBank"/>; its own file: Godot serializes a resource by its script's
/// file)</summary>
[GlobalClass]
public partial class KitSeeThroughCapEntry : Resource
{
    /// <summary>the source mesh: its piece and its own name (<see cref="KitSeeThroughCaps.SourceOf"/>)</summary>
    [Export] public string Source = "";
    /// <summary>the cut, in KitSeeThroughCaps.Step over the source's origin (its own units)</summary>
    [Export] public int Q;
    /// <summary>the source's solid and bark surfaces (bits)</summary>
    [Export] public long Solid, Bark;
    /// <summary>the cap (null: the section filled nothing)</summary>
    [Export] public ArrayMesh Cap;
    /// <summary>each cap surface's source surface, and which take the end grain (bits by cap surface)</summary>
    [Export] public int[] Mats = System.Array.Empty<int>();
    [Export] public long GrainBits;

    public bool[] Grain
    {
        get { var g = new bool[Mats.Length]; for (int i = 0; i < g.Length; i++) g[i] = (GrainBits & (1L << i)) != 0; return g; }
        set { GrainBits = 0; for (int i = 0; i < value.Length; i++) if (value[i]) GrainBits |= 1L << i; }
    }
    /// <summary>the cap's area (the source's units)</summary>
    [Export] public float Area;
    /// <summary>the source as baked: a re-exported mesh no longer matches</summary>
    [Export] public int VertexCount;
    [Export] public Aabb Bounds;
}
