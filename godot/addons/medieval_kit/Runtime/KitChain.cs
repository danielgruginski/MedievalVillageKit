using System;
using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>
/// A chain of maps for a continuous world (generated, or hand-made plans): the maps listed in order, each joined to an
/// earlier one (the one before, or any other: branches) through a connector (<see cref="KitConnectorGenerator"/>)
/// between that map's portal and its own in portal (see <see cref="KitPortal"/>). Every portal leads somewhere: each is
/// used by exactly one join. A tree, not a loop (a branch never rejoins). KitChainTools.Bake (kit_cli chains bake)
/// builds every piece, lines them up in world space (maps are never turned), checks they do not overlap and saves each
/// piece as a scene; <see cref="KitChainStreamer"/> then loads the pieces next to the walker and frees the rest, so one
/// walks from map to map without a cut. A scene link into the chain (a stair down into a cellar) targets the play scene
/// Bake writes, with the arrival spawn's id: the streamer starts at the piece holding that spawn. The maps keep the
/// Unity kit's field names. Unity: KitChain.
/// </summary>
[GlobalClass]
public partial class KitChain : Resource
{
    [Export] public Godot.Collections.Array<KitChainMap> maps = new();
    /// <summary>where the first map's origin (its plan's south-west corner) lies in the world: when the first map grows
    /// south or west, move it the other way (z - 1.5 a row, x - 1.5 a column) so what was baked stays put</summary>
    [Export] public Vector3 origin = Vector3.Zero;
    /// <summary>filled by Bake: every piece in order (map, connector, map, ...)</summary>
    [Export] public Godot.Collections.Array<KitChainPiece> pieces = new();

    public KitChainPiece Find(string id) => pieces.FirstOrDefault(p => p.id == id);

    /// <summary>called by Bake once every piece is saved and the navmesh baked: a game puts what it adds to the generated
    /// pieces here (a quest's way in, a clue by a lair), so a re-bake keeps them; it returns lines for Bake's report</summary>
    public static Func<KitChain, string> AfterBake;

    /// <summary>the piece holding a spawn, or null</summary>
    public KitChainPiece WithSpawn(string spawnId) => pieces.FirstOrDefault(p => p.spawns.Contains(spawnId));

    /// <summary>the piece whose footprint holds a world point (x / z), or null</summary>
    public KitChainPiece At(Vector3 p) => pieces.FirstOrDefault(q => q.footprint.HasPoint(new Vector2(p.X, p.Z)));

    /// <summary>pieces within `steps` joins of a piece (it included)</summary>
    public HashSet<string> Around(string id, int steps)
    {
        var seen = new HashSet<string> { id };
        var front = new List<string> { id };
        for (int s = 0; s < steps; s++)
        {
            var next = new List<string>();
            foreach (var f in front)
                foreach (var n in Find(f)?.neighbours ?? Array.Empty<string>())
                    if (seen.Add(n)) next.Add(n);
            front = next;
        }
        return seen;
    }
}
