using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>A level's walkable surface for the game's agents (a click-to-move player, monsters: NavigationAgent3D),
/// baked by the level builder from the level's colliders the way the walk tests see them (doors that open and
/// breakables passable: only layer KitPiece.Solid; Area3D triggers ignored). Godot's NavigationRegion3D already adds its
/// surface while it is in the tree and removes it when not, so a level held out of the tree by KitTravel.Preload takes
/// its surface with it; this sets the navigation map's cell size to the surface's on entering (a map whose cell size
/// differs from its regions' does not join them) and its edge-merge grid finer. Unity: KitNavMesh (+ KitNavBake).</summary>
[GlobalClass]
public partial class KitNavMesh : NavigationRegion3D
{
    /// <summary>the kit's walker (radius 0.3: the kit's 0.84 m doors, height 1.8, step 0.35, slope 40), on cells of
    /// `voxel` metres (0.05 indoors and in caves: narrow doors and openings; 0.1 on outdoor maps), heights in 0.05 m;
    /// islands under 2 m² left out (Unity's minRegionArea: the tops of sacks, chests and fire pits are no floor)</summary>
    public static NavigationMesh Settings(float voxel = 0.05f) => new()
    {
        CellSize = voxel, CellHeight = 0.05f,
        RegionMinSize = Mathf.Sqrt(2f) / voxel,                    // (squared: a count of cells)
        AgentRadius = 0.3f, AgentHeight = 1.8f, AgentMaxClimb = 0.35f, AgentMaxSlope = 40f,
        GeometryParsedGeometryType = NavigationMesh.ParsedGeometryType.StaticColliders,
        GeometryCollisionMask = KitPiece.Solid,
        GeometrySourceGeometryMode = NavigationMesh.SourceGeometryMode.RootNodeChildren,
    };

    /// <summary>the surface of everything under root (which must be in the tree: the parser reads global transforms);
    /// `notWalkable`: outlines in root space (their y left out) where none is made between the heights `bottom` and
    /// `top` (an outdoor map's forest beyond its walls from floor to sky, the ground under its raised terrain, its sea;
    /// Unity's Not Walkable volumes); `mask`: the collision layers baked (the solid ones; with
    /// <see cref="KitPiece.Passable"/> too, doors and breakables count as shut)</summary>
    public static NavigationMesh Bake(Node3D root, float voxel = 0.05f, IEnumerable<(Vector3[] poly, float bottom, float top)> notWalkable = null, uint mask = KitPiece.Solid)
    {
        var nm = Settings(voxel);
        nm.GeometryCollisionMask = mask;
        var src = new NavigationMeshSourceGeometryData3D();
        NavigationServer3D.ParseSourceGeometryData(nm, src, root);
        SolidBoxes(root, nm, src);
        foreach (var (poly, bottom, top) in notWalkable ?? Enumerable.Empty<(Vector3[], float, float)>())
            src.AddProjectedObstruction(poly, bottom, top - bottom, true);
        NavigationServer3D.BakeFromSourceGeometryData(nm, src);
        return nm;
    }

    /// <summary>
    /// Unity bakes a box collider as a solid; Godot's parser sees only its faces, so the floor inside a box taller than
    /// the walker (a hearth's 2.2 m block) stays walkable, an island sealed in the box. Every such solid box goes in as
    /// a projected obstruction too (its footprint, eroded by the walker's radius like the box itself): nothing inside.
    /// </summary>
    static void SolidBoxes(Node3D root, NavigationMesh nm, NavigationMeshSourceGeometryData3D src)
    {
        var toRoot = root.GlobalTransform.AffineInverse();
        foreach (var cs in KitNodes.Below(root, "CollisionShape3D").OfType<CollisionShape3D>())
        {
            if (cs.Disabled || cs.Shape is not BoxShape3D box || cs.GetParent() is not StaticBody3D body || (body.CollisionLayer & nm.GeometryCollisionMask) == 0)
                continue;
            var t = toRoot * cs.GlobalTransform;
            var h = box.Size / 2f;
            var corners = new[] { new Vector3(-h.X, -h.Y, -h.Z), new Vector3(h.X, -h.Y, -h.Z), new Vector3(h.X, -h.Y, h.Z), new Vector3(-h.X, -h.Y, h.Z) }
                .Select(c => t * c).ToArray();
            float bottom = corners.Min(c => c.Y), height = (t.Basis * new Vector3(0, box.Size.Y, 0)).Length();
            if (height < nm.AgentHeight || Mathf.Abs(t.Basis.Y.Normalized().Y) < 0.99f) continue;     // upright and tall only
            src.AddProjectedObstruction(corners, bottom, height, false);
        }
    }

    public override void _EnterTree()
    {
        if (NavigationMesh == null) return;
        var map = GetWorld3D().NavigationMap;
        NavigationServer3D.MapSetCellSize(map, NavigationMesh.CellSize);
        NavigationServer3D.MapSetCellHeight(map, NavigationMesh.CellHeight);
        // edges are joined on a grid of cell size x this: at 1 the small cells' edges crowd it ("more than 2 edges ...
        // same map rasterization space"); Recast's vertices lie on the cell grid, so a finer one loses nothing
        NavigationServer3D.MapSetMergeRasterizerCellScale(map, 0.1f);
    }
}
