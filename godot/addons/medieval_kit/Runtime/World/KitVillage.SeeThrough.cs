using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit;

public partial class KitVillage
{
    List<KitSeeThrough.Building> seeThroughBuildings;

    /// <summary>
    /// What the see-through needs on a village once it stands (<see cref="KitLevel"/> calls it after
    /// <see cref="KitSeeThrough.Bound"/>; nothing saved): the nature and the props are loose (the nature by its round
    /// shape), each building opens as one, and so does each run of walls placed as props (a town wall, a palisade); every
    /// piece is cut <see cref="KitSeeThroughCaps.Height"/> over its base -- a house's floor, a tree's or a prop's foot --
    /// with a real cap where it spans the cut, and a house gets a floor where the hole opens it. The cap bake calls it with
    /// <see cref="KitSeeThroughCaps.Collecting"/> set, to learn which caps the level needs. Unity: KitVillage.SetUpSeeThrough.
    /// </summary>
    public List<KitSeeThrough.Building> SetUpSeeThrough()
    {
        seeThroughBuildings = new List<KitSeeThrough.Building>();
        var loose = new List<Node3D>();
        foreach (var g in KitNodes.Children(this).OfType<Node3D>())
        {
            string n = g.Name;
            if (n == "Nature" || n == "Props")
            {
                KitSeeThrough.Loose(g, round: n == "Nature");
                foreach (var piece in KitNodes.Children(g).OfType<Node3D>()) if (!KitSeeThrough.IsStanding(piece.Name)) loose.Add(piece);
            }
            if (n == "Props") seeThroughBuildings.AddRange(KitSeeThrough.Runs(g));
            else if (n == "Buildings")
                foreach (var b in KitNodes.Children(g).OfType<Node3D>())
                    if (KitSeeThrough.Geometry(b).Any()) seeThroughBuildings.Add(new KitSeeThrough.Building(b));
        }
        foreach (var b in seeThroughBuildings)
        {
            foreach (var r in b.Pieces)
                if (IsInstanceValid(r)) KitSeeThroughCaps.Cut(r, b.PerPiece ? PieceRoot(r, b.Root).GlobalPosition.Y : b.Floor, b);
            // a house's floor where the hole opens it (not an L-shaped generated house: its walls' box is not its floor)
            var hg = b.PerPiece ? null : b.Root as KitHouseGenerator;
            if (!b.PerPiece && (hg == null || hg.shape != KitHouseGenerator.Shape.L)) KitSeeThroughCaps.Floor(b);
        }
        foreach (var piece in loose)
            foreach (var g in KitSeeThrough.Geometry(piece)) KitSeeThroughCaps.Cut(g, piece.GlobalPosition.Y);
        if (KitSeeThroughCaps.Collecting == null) KitSeeThroughCaps.Settle();
        return seeThroughBuildings;
    }

    /// <summary>the piece a mesh belongs to: its ancestor standing directly in `group` (a gatehouse's 44 meshes sit at
    /// their own heights: each was cut over its own origin, so its timber gallery 6 m up was cut at 7.4 m)</summary>
    static Node3D PieceRoot(Node3D t, Node3D group)
    {
        while (t.GetParent() is Node3D p && p != group) t = p;
        return t;
    }
}
