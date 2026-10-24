using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>Where a fight happens: a room of a generated dungeon (or one placed by hand), the creature tag the game
/// should spawn there ("goblin", "rat", "undead", "bandit", "cultist", "boss"...), a difficulty budget (1 + the room's
/// depth from the entrance; the lair more), and spawn points (its Node3D children). The kit only marks them: the game
/// decides what a tag and a budget turn into, and when the encounter wakes (on entering Size, on sight...).
/// Unity: KitEncounter.</summary>
[GlobalClass]
public partial class KitEncounter : Node3D
{
    [Export] public string EncounterId = "";
    [Export] public string RoomType = "";
    [Export] public string Creature = "";
    [Export] public int Budget = 1;
    [Export] public int Depth;
    [Export] public bool Boss;
    /// <summary>the room's area (local, centred on this node, standing on it), e.g. for a wake-up trigger</summary>
    [Export] public Vector3 Size = new(4.5f, 3f, 4.5f);

    public IEnumerable<Node3D> Points => GetChildren().OfType<Node3D>();
}
