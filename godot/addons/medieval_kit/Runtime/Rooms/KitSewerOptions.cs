using Godot;

namespace MedievalKit;

/// <summary>
/// Settings of a random town sewer (<see cref="KitSewerGenerator"/>): its size, seed, how much of the street grid the
/// tunnels reach, the loops, chambers, grottoes and cross walls, the debris, the ladder up and the way on down, the
/// creatures and the lair's point of interest. Unity: KitSewerGenerator.Options.
/// </summary>
[GlobalClass]
public partial class KitSewerOptions : Resource
{
    [Export] public int nc = 30;
    [Export] public int nr = 22;
    [Export] public int seed = 7;
    /// <summary>Share of the street grid's crossings the tunnels reach (the rest stays rock: room for the grottoes).</summary>
    [Export(PropertyHint.Range, "0.3,1")] public float reach = 0.85f;
    /// <summary>Dry passages two cells wide closing loops between the tunnels, per crossing reached.</summary>
    [Export(PropertyHint.Range, "0,1")] public float loops = 0.35f;
    /// <summary>Vaulted chambers on the crossings: a cistern (a basin the channels meet in) or a hall.</summary>
    [Export] public int chambers = 2;
    /// <summary>Natural caves the tunnels have broken into (a breach in the brick); the one farthest from the ladder is the lair.</summary>
    [Export] public int grottoes = 2;
    /// <summary>Cross walls over the channels (a culvert under them, a door on the walkways).</summary>
    [Export] public int crossWalls = 2;
    /// <summary>loose debris (the kit's scatter by zone theme): share of the open cells</summary>
    [Export(PropertyHint.Range, "0,1")] public float debris = 0.35f;
    /// <summary>The ladder up to the street (the way in): its link id (its spawn's id too), the scene it leads to, the spawn there.</summary>
    [Export] public string upId = "up";
    /// <summary>The ladder up to the street (the way in): the scene it leads to.</summary>
    [Export] public string upTarget = "@return";
    /// <summary>The ladder up to the street (the way in): the spawn there.</summary>
    [Export] public string upArrive = "";
    /// <summary>A tunnel on down in the lair's rock (else a passage in a north wall): the scene it leads to; empty: none.</summary>
    [Export] public string deep = "";
    [Export] public string deepId = "down";
    [Export] public string deepArrive = "";
    /// <summary>The encounters' creature tag, and the lair's (the boss).</summary>
    [Export] public string creature = "rat";
    /// <summary>The lair's creature tag (the boss).</summary>
    [Export] public string boss = "boss";
    /// <summary>The lair's point of interest (2 x 2 cells), e.g. POI_RatKing; empty: none.</summary>
    [Export] public string poi = "POI_RatKing";
    /// <summary>How many encounters (0: by the level's size): one in every grotto and chamber, the rest along the tunnels.</summary>
    [Export] public int encounters = 0;
}
