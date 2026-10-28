using System;
using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>
/// Walkable tops the kit's navmesh leaves out (a warcamp's walkway: its deck pieces have no collider, so the bake skips
/// them): a level's meshes the rules name (<see cref="Names"/>: the game sets it) each get a box over their top (to click
/// and stand on) and one navmesh over all of them, once per level (<see cref="Ensure"/>: as it stands). The region and
/// boxes go under the level, so they leave with it. Unity: KitWalkways.
/// </summary>
public static class KitWalkways
{
    /// <summary>the deck pieces' names (a mesh whose node or piece name holds one gets a deck): the game sets it, e.g. from
    /// its rules; null or empty = no decks</summary>
    public static Func<IList<string>> Names;

    static readonly StringName Done = "kit_walkways";

    /// <summary>the level's decks, made once (later calls do nothing)</summary>
    public static void Ensure(Node level)
    {
        if (level == null || level.HasMeta(Done)) return;
        level.SetMeta(Done, true);
        var names = Names?.Invoke();
        if (names == null || names.Count == 0 || level is not Node3D root) return;
        var src = new NavigationMeshSourceGeometryData3D();
        int n = 0;
        foreach (var node in KitNodes.Below(level, "MeshInstance3D"))
        {
            var mi = (MeshInstance3D)node;
            string piece = PieceName(mi);
            if (mi.Mesh == null || !names.Any(x => !string.IsNullOrEmpty(x) && (piece.Contains(x, StringComparison.Ordinal) || mi.Name.ToString().Contains(x, StringComparison.Ordinal)))) continue;
            var m = mi.Mesh.GetAabb();                                         // the deck: the piece's top, a thin box
            var top = new Vector3(m.GetCenter().X, m.End.Y - 0.05f, m.GetCenter().Z);
            var size = new Vector3(m.Size.X, 0.1f, m.Size.Z);
            var box = new BoxMesh { Size = size };
            src.AddMesh(box, mi.GlobalTransform * new Transform3D(Basis.Identity, top));
            if (KitNodes.Children(mi).OfType<CollisionObject3D>().FirstOrDefault() == null)
            {
                var body = new StaticBody3D { Name = "Deck", CollisionLayer = KitPiece.Solid };
                body.AddChild(new CollisionShape3D { Shape = new BoxShape3D { Size = size }, Position = top });
                mi.AddChild(body);
            }
            n++;
        }
        if (n == 0) return;
        // on the level's own cells (a map whose cell size differs from a region's does not join it)
        float voxel = KitNodes.Below(level, "").OfType<KitNavMesh>().FirstOrDefault()?.NavigationMesh?.CellSize ?? 0.1f;
        var nm = KitNavMesh.Settings(voxel);
        NavigationServer3D.BakeFromSourceGeometryData(nm, src);
        root.AddChild(new NavigationRegion3D { Name = "KitWalkways", NavigationMesh = nm });
    }

    static string PieceName(Node n)
    {
        for (; n != null; n = n.GetParent()) if (n is KitPiece kp) return kp.Piece ?? "";
        return "";
    }
}
