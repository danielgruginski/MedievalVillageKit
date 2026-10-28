using Godot;

namespace MedievalKit;

/// <summary>Settings of a random house floor (<see cref="KitInteriorGenerator"/>): the kind of house, the seed, its
/// size, a great hall, a stair and books. Unity: KitInteriorGenerator.Options.</summary>
[GlobalClass]
public partial class KitInteriorOptions : Resource
{
    /// <summary>Cottage, Townhouse, Tavern or Workshop.</summary>
    [Export] public string kind = "Cottage";
    [Export] public int seed = 3;
    /// <summary>0: by kind.</summary>
    [Export] public int nc;
    /// <summary>0: by kind.</summary>
    [Export] public int nr;
    /// <summary>One room: the hall over the whole floor, no side rooms (a great hall).</summary>
    [Export] public bool open;
    /// <summary>A stair up the hall's west wall at its north end: "up" (arrival in front of its foot) or "down" (an upper
    /// floor: arrival beside its top, bedrooms aside, no front door); empty: none.</summary>
    [Export] public string stair = "";
    /// <summary>Books, by how learned and rich the house is (2026-10-14): 0 none, 1 a narrow bookcase in the hall, 2 a
    /// bookcase in the hall and a study (a side room of bookcases, a scroll rack, a desk, a reading table), 3 a
    /// library (the hall lined with bookcases and scroll racks). -1: by kind -- a townhouse 1 or 2 (its upper
    /// floor none), the rest 0.</summary>
    [Export] public int books = -1;
}
