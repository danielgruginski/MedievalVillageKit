using Godot;

namespace MedievalKit;

/// <summary>
/// Live creatures hidden by a wall, a rock or a roof show where they are hidden as a flat translucent red, so they can be
/// seen and clicked (the cursor's ray goes through what is in front). A creature's meshes carry two overlay passes
/// (<see cref="Tag"/>; the game tags a creature as it spawns and untags it on death): the mark (Shaders/
/// CreatureSilhouetteMark: stencil 1 where the creature or the player is the visible surface) and the fill
/// (CreatureSilhouetteFill: the colour where something lies in front of it by more than <see cref="Pull"/> and the pixel is
/// not marked, once per pixel); the player's meshes carry only the mark, so a rat behind the player does not show through
/// the player. On a level with grass the feet get <see cref="FeetPull"/> more (paws among the blades).
/// <para>Godot: Unity's version is a render pass over the creatures' renderers (a rendering layer); Godot has no such
/// pass, so each mesh's material_overlay carries the two (an overlay already there is replaced). The mark sorts before
/// every fill (render priority), as Unity drew the marks first.</para>
/// </summary>
public static class CreatureSilhouettes
{
    static ShaderMaterial mark, fill, markOnly;
    static Color colour = new(0.86f, 0.30f, 0.24f, 0.55f);
    static float pull = 0.35f, feetPull;

    /// <summary>the silhouette's colour; alpha: how much of it covers what hides the creature</summary>
    public static Color Colour { get => colour; set { colour = value; Fill.SetShaderParameter("colour", value); } }
    /// <summary>something less than this far (m) in front of a creature does not hide it</summary>
    public static float Pull { get => pull; set { pull = value; Fill.SetShaderParameter("pull", value); } }
    /// <summary>this much more at the feet (m), fading out 0.6 m up: a level with grass sets 0.6 (blades in front of the
    /// paws), 0 off (caves: it would cut the near half off a rat against a wall)</summary>
    public static float FeetPull { get => feetPull; set { feetPull = value; Fill.SetShaderParameter("feet_pull", value); } }

    static ShaderMaterial Fill
    {
        get
        {
            if (fill != null) return fill;
            fill = new ShaderMaterial { Shader = GD.Load<Shader>(KitPaths.Shaders + "CreatureSilhouetteFill.gdshader"), RenderPriority = 101 };
            fill.SetShaderParameter("colour", colour);
            fill.SetShaderParameter("pull", pull);
            fill.SetShaderParameter("feet_pull", feetPull);
            return fill;
        }
    }

    /// <summary>the overlay for a creature (mark, then fill) or for anyone else (mark only)</summary>
    static ShaderMaterial Overlay(bool creature)
    {
        if (creature)
        {
            if (mark == null)
            {
                mark = new ShaderMaterial { Shader = GD.Load<Shader>(KitPaths.Shaders + "CreatureSilhouetteMark.gdshader"), RenderPriority = 100 };
                mark.NextPass = Fill;
            }
            return mark;
        }
        return markOnly ??= new ShaderMaterial { Shader = GD.Load<Shader>(KitPaths.Shaders + "CreatureSilhouetteMark.gdshader"), RenderPriority = 100 };
    }

    /// <summary>a body's meshes on or off the silhouettes: a creature's are drawn where hidden, anyone else's (the
    /// player's) only hide the creatures behind them. Either way never cut by the kit's see-through
    /// (<see cref="KitSeeThrough.Keep"/>: a body's props are drawn with the kit's materials)</summary>
    public static void Tag(Node node, bool creature, bool on = true)
    {
        if (node == null) return;
        var o = Overlay(creature);
        foreach (var g in KitSeeThrough.Geometry(node))
        {
            if (on) g.MaterialOverlay = o;
            else if (g.MaterialOverlay == o) g.MaterialOverlay = null;
        }
        KitSeeThrough.Keep(node);
    }
}
