using Godot;

namespace MedievalKit;

/// <summary>Where a generated map opens into the next one (KitPortal): it sits on the middle of the opening on the
/// map's edge, its forward (-Z) pointing out of the map. A chain lines the next piece up by putting its own marker for
/// the facing side on this one's position; the streamer watches the walker against them. Unity: KitPortalMarker.</summary>
[GlobalClass]
public partial class KitPortalMarker : Marker3D
{
    [Export] public string PortalId = "";
    /// <summary>N, S, E or W: the map edge the opening is on</summary>
    [Export] public string Side = "";
    /// <summary>the opening's first cell along the edge and its width in cells</summary>
    [Export] public int At, Width = 2;
    [Export] public string Target = "";
    /// <summary>a connector's end (the neighbour builds the seam's rock)</summary>
    [Export] public bool Seam;
}
