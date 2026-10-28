using Godot;

namespace MedievalKit;

/// <summary>
/// Settings of a random dungeon level (<see cref="KitDungeonGenerator"/>): its size, seed, room count, theme, the share of
/// natural cave pockets, the loops, the debris, the portals into the next maps of a chain and the stair out of it.
/// Unity: KitDungeonGenerator.Options.
/// </summary>
[GlobalClass]
public partial class KitDungeonOptions : Resource
{
    [Export] public int nc = 28;
    [Export] public int nr = 20;
    [Export] public int seed = 11;
    [Export] public int rooms = 8;
    /// <summary>Dungeon (mixed rooms), Crypt, Warren (goblins in natural caves) or Hideout (bandits: guard posts, stores
    /// of plunder and sleeping cells walled into rock, joined by rough tunnels).</summary>
    [Export] public string theme = "Dungeon";
    /// <summary>share of rooms left as natural cave</summary>
    [Export(PropertyHint.Range, "0,1")] public float pockets = 0.2f;
    /// <summary>extra corridors beyond the spanning tree, per room</summary>
    [Export(PropertyHint.Range, "0,1")] public float loops = 0.25f;
    /// <summary>loose debris (the kit's scatter by zone theme): share of the open cells</summary>
    [Export(PropertyHint.Range, "0,1")] public float debris = 0.25f;
    /// <summary>Openings on the map's edges into the next map of a chain (KitPortal; the first is the way in). None: a stair up where one arrives, a stair down in the lair.</summary>
    [Export] public Godot.Collections.Array<KitPortal> portals = new();
    /// <summary>With portals: a stair up out of the chain to this scene (e.g. a camp above), in a room far from the way in
    /// (the lair; a Hideout's in the deepest room but the lair, with no encounter: its front door); empty: none.</summary>
    [Export] public string exit = "";
    /// <summary>The exit stair's link id (its spawn's id too: where one arrives coming down from the scene above).</summary>
    [Export] public string exitId = "exit";
    /// <summary>The spawn the exit stair leads to in that scene (empty: KitTravel's rules).</summary>
    [Export] public string exitArrive = "";
}
