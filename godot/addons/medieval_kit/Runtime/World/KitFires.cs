using System;
using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>
/// The kit's fires burning: its torches, braziers, hearths, fireplaces, fire pits and the goblins' bonfire (pieces with a
/// glowing flame mesh, an <c>M_VKI_GlowIn</c> surface) get small steady flames at that mesh (<see cref="Fire.Steady"/>),
/// the mesh turned to coals (or hidden: a brazier's and the bonfire's cones stand up through the flames like crystals),
/// and the kit's light beside it flickering (<see cref="FireFlicker"/>; none within 3 m: a light of its own). A level
/// lights its own as it stands (KitLevel: <see cref="LightLevel"/>; a game with its own campfires turns that off and calls
/// <see cref="Light"/> per piece). Unity: KitFires.
/// </summary>
public static class KitFires
{
    /// <summary>the kit's fires, matched in a piece's name: the flames' scale (a torch's 0.18), sparks, smoke (outdoors),
    /// and whether its flame mesh stays, as coals</summary>
    public static readonly (string match, float scale, bool sparks, bool smoke, bool coals)[] Kinds =
    {
        ("Torch_Wall", 0.18f, false, false, true),
        ("Brazier", 0.3f, true, false, false),
        ("FirePit", 0.38f, true, true, true),                       // a campfire's size
        ("Bonfire", 1.1f, true, true, false),
        ("Hearth", 0.32f, true, false, true),                       // a stone hearth, an open one
        ("Fireplace", 0.3f, true, false, true),
    };

    /// <summary>the words in the kit's light names (LIT_..._torch, _brazier, _hearth...) that make it a fire's</summary>
    public static readonly string[] LightWords = { "torch", "brazier", "hearth", "fire", "pit", "bonfire" };

    /// <summary>the fires' lights under this root (hidden ones too)</summary>
    public static List<Light3D> FireLights(Node root) =>
        KitNodes.Below(root, "Light3D").OfType<Light3D>()
            .Where(l => l.Name.ToString().StartsWith("LIT_", StringComparison.Ordinal) &&
                        LightWords.Any(w => l.Name.ToString().Contains(w, StringComparison.OrdinalIgnoreCase))).ToList();

    /// <summary>every kit fire in a level lit (its pieces, its fire lights); returns how many</summary>
    public static int LightLevel(Node level)
    {
        var lights = FireLights(level);
        int n = 0;
        foreach (var p in KitNodes.Below(level, "").OfType<KitPiece>().ToList())
            if (Light(p, lights)) n++;
        return n;
    }

    /// <summary>one piece: if it is a kit fire (not a burnt one, not within 1.5 m of one of <paramref name="notNear"/>: fires
    /// of the game's own on the spot), its flames lit and the nearest of <paramref name="lights"/> flickering. -> whether
    /// it was lit</summary>
    public static bool Light(KitPiece p, IList<Light3D> lights, IList<Vector3> notNear = null)
    {
        string piece = !string.IsNullOrEmpty(p.Piece) ? p.Piece : p.Name.ToString();
        var kind = Kinds.FirstOrDefault(k => piece.Contains(k.match, StringComparison.Ordinal));
        if (kind.match == null || piece.EndsWith("_Burnt", StringComparison.Ordinal)) return false;
        var at0 = p.GlobalPosition;
        if (notNear != null && notNear.Any(c => new Vector2(c.X - at0.X, c.Z - at0.Z).LengthSquared() < 2.25f)) return false;
        if (p.HasNode("Fire")) return false;                            // (lit already)
        if (!FlameMesh(p, out var b)) return false;
        var c0 = b.GetCenter();
        var at = new Vector3(c0.X, b.Position.Y + Mathf.Min(0.15f * b.Size.Y, 0.2f), c0.Z);   // at the foot of it
        float scale = kind.scale * Mathf.Clamp(p.GlobalBasis.Y.Length(), 0.5f, 3f);
        var fire = Fire.Steady(p, at, new Vector2(b.Size.X, b.Size.Z) * 0.6f, scale, kind.sparks, kind.smoke);
        FireFx.Coals(p, !kind.coals);
        var world = p.GlobalTransform * at;
        Light3D near = null;
        float best = 9f;                                            // within 3 m (one flickering already for a fire
        foreach (var l in lights)                                   // beside it too: two torches, one light)
        {
            if (!GodotObject.IsInstanceValid(l)) continue;
            float d = (l.GlobalPosition - world).LengthSquared();
            if (d < best) { best = d; near = l; }
        }
        if (near == null)
        {
            FireFx.Lamp(fire, at + Vector3.Up * (0.3f + scale), 1.5f + 3f * scale, 4f + 8f * scale);
            return true;
        }
        if (KitNodes.Children(near).OfType<FireFlicker>().Any()) return true;
        float range = near is OmniLight3D o ? o.OmniRange : near is SpotLight3D s ? s.SpotRange : 0f;
        near.AddChild(new FireFlicker { Name = "Flicker", Tint = false, Depth = range > 20f ? 0.4f : 0.7f });   // the kit's colour kept;
        return true;                                                                                            // a room's big light wavers less
    }

    /// <summary>a kit piece's glowing flame mesh (its M_VKI_GlowIn surfaces), as a box in the piece's space</summary>
    public static bool FlameMesh(KitPiece p, out Aabb b)
    {
        b = default;
        bool found = false;
        var inv = p.GlobalTransform.AffineInverse();
        foreach (var n in KitNodes.Below(p, "MeshInstance3D"))
        {
            var mi = (MeshInstance3D)n;
            if (mi.Mesh == null || Owner(mi) != p) continue;            // not a piece inside it
            for (int s = 0; s < mi.Mesh.GetSurfaceCount(); s++)
            {
                if (mi.GetActiveMaterial(s) is not Material m || !m.ResourcePath.GetFile().StartsWith("M_VKI_GlowIn", StringComparison.Ordinal)) continue;
                Aabb sb;
                using (var surf = RenderingServer.MeshGetSurface(mi.Mesh.GetRid(), s)) sb = (Aabb)surf["aabb"];   // (known without reading the mesh)
                for (int c = 0; c < 8; c++)
                {
                    var q = inv * (mi.GlobalTransform * sb.GetEndpoint(c));
                    if (!found) { b = new Aabb(q, Vector3.Zero); found = true; }
                    else b = b.Expand(q);
                }
            }
        }
        return found;
    }

    static KitPiece Owner(Node n)
    {
        for (; n != null; n = n.GetParent()) if (n is KitPiece kp) return kp;
        return null;
    }
}
