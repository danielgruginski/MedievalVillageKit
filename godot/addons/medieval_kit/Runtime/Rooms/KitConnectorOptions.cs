using Godot;

namespace MedievalKit;

/// <summary>Settings of a connector between two generated maps of a chain (<see cref="KitConnectorGenerator"/>): the
/// edges it joins, its length, the openings' width and place, the seed and the floor style.
/// Unity: KitConnectorGenerator.Options.</summary>
[GlobalClass]
public partial class KitConnectorOptions : Resource
{
    /// <summary>The edge the map one comes from meets: N, S, E or W.</summary>
    [Export] public string from = "S";
    /// <summary>The edge the next map meets (not the same as From).</summary>
    [Export] public string to = "N";
    /// <summary>Cells from one opening to the other along the way (about 8-14).</summary>
    [Export] public int length = 10;
    /// <summary>The openings' width in cells: the maps either side use the same.</summary>
    [Export] public int width = 2;
    /// <summary>The openings' first cell along their edges; -1: the generator picks.</summary>
    [Export] public int fromAt = -1;
    /// <summary>The openings' first cell along their edges; -1: the generator picks.</summary>
    [Export] public int toAt = -1;
    [Export] public int seed = 1;
    /// <summary>Cave: cave floor. Dungeon: a dressed-stone floor (the sides stay bare rock, as at every seam).</summary>
    [Export] public string style = "Cave";
    [Export(PropertyHint.Range, "0,1")] public float debris = 0.3f;
}
