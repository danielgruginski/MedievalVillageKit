using Godot;

namespace MedievalKit;

/// <summary>Settings of a random cave level (<see cref="KitCaveGenerator"/>): the layout, its size and seed, the chasm,
/// pools, dressing, finds, portals and encounters. Unity: KitCaveGenerator.Options.</summary>
[GlobalClass]
public partial class KitCaveOptions : Resource
{
    /// <summary>Maze: chambers, winding tunnels, loops and dead ends. Open: the kit's cellular automaton.</summary>
    [Export] public string layout = "Maze";
    [Export] public int nc = 28;
    [Export] public int nr = 20;
    [Export] public int seed = 7;
    [Export] public int pools = 2;
    [Export] public int props = 18;
    /// <summary>Maze: chambers per 100 cells.</summary>
    [Export] public float chambers = 2.0f;
    /// <summary>Maze: extra tunnels beyond the spanning tree, per chamber.</summary>
    [Export(PropertyHint.Range, "0,1")] public float loops = 0.35f;
    /// <summary>Maze: spurs that end in an alcove.</summary>
    [Export] public int deadEnds = 3;
    [Export] public bool chasm = true;
    /// <summary>A second chasm branching off the first.</summary>
    [Export] public bool chasmFork = true;
    /// <summary>The chasm's width in cells, narrowest .. widest along its length.</summary>
    [Export] public Vector2 chasmWidth = new Vector2(0.4f, 3.6f);
    /// <summary>Loose debris (rocks, rubble, broken stalactites, gravel, bones...): share of the open cells.</summary>
    [Export(PropertyHint.Range, "0,1")] public float debris = 0.34f;
    [Export] public string poi;              // e.g. "POI_WyrmBones": a w x h point of interest near the centre
    [Export] public int poiW = 2;
    [Export] public int poiH = 2;
    [Export] public string poiCode = "WY";
    /// <summary>Openings on the map's edges into the next map of a chain (KitPortal); none: the old tunnels west and east.</summary>
    [Export] public Godot.Collections.Array<KitPortal> portals = new();
    /// <summary>Encounters: the creatures that live here (rat, spider, goblin...), comma-separated from the way in to the deep end ("rat,spider": rats near the way in, spiders deeper); empty: none.</summary>
    [Export] public string creature = "";
    /// <summary>Encounters: how many, spread through the cave, harder the farther from the way in (the point of interest holds the boss).</summary>
    [Export] public int encounters = 4;
    /// <summary>Finds in the dead ends' alcoves, as piece:code pairs ("LootPile:lp,Goblin_Dead:gd"); a piece not in the kit is looked up in the project. Every find but an Overlay_ is marked as loot (record "markers", role loot). Empty: loot pile, fallen skeleton, treasure chest, bones.</summary>
    [Export] public string finds = "";
    /// <summary>Finds besides the alcoves': this many more along the cave's walls, spread out (bodies along the way).</summary>
    [Export] public int extraFinds = 0;
    /// <summary>Dressing round the cave, as piece:code pairs ("EggSacs:es,Cocoon:co"), placed in turn. Empty: crystals, glowing mushrooms, stalagmites, boulders, gravel.</summary>
    [Export] public string dressing = "";
}
