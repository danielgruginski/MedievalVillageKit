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
    /// `voxel` metres (0.05 indoors and in caves: narrow doors and openings; 0.1 on outdoor maps), heights in 0.05 m</summary>
    public static NavigationMesh Settings(float voxel = 0.05f) => new()
    {
        CellSize = voxel, CellHeight = 0.05f,
        AgentRadius = 0.3f, AgentHeight = 1.8f, AgentMaxClimb = 0.35f, AgentMaxSlope = 40f,
        GeometryParsedGeometryType = NavigationMesh.ParsedGeometryType.StaticColliders,
        GeometryCollisionMask = KitPiece.Solid,
        GeometrySourceGeometryMode = NavigationMesh.SourceGeometryMode.RootNodeChildren,
    };

    /// <summary>the surface of everything under root (which must be in the tree: the parser reads global transforms)</summary>
    public static NavigationMesh Bake(Node3D root, float voxel = 0.05f)
    {
        var nm = Settings(voxel);
        var src = new NavigationMeshSourceGeometryData3D();
        NavigationServer3D.ParseSourceGeometryData(nm, src, root);
        NavigationServer3D.BakeFromSourceGeometryData(nm, src);
        return nm;
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
