using System;
using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>
/// The parts every fire is made of (<see cref="Fire"/>): upright tongues of flame (an 8 x 8 flipbook, alpha blended, so
/// flames piled on each other never wash out to white) with a smaller additive core, a faint glow, embers, a smoke column
/// (a 4 x 4 sheet of puffs) and a flickering light (<see cref="FireFlicker"/>). Flames start at spots
/// (<see cref="SetSpots"/>: emission points), not in a volume. A fire that never moves is kept <see cref="Still"/>; the
/// kit's glowing flame meshes under a fire are turned to <see cref="Coals"/>. Textures in the addon's FX/ (the Unity
/// package's Resources/FX); the materials are made here. Unity: FireFx.
/// <para>Godot: each part is a GPUParticles3D with a ParticleProcessMaterial. Its emission rate is its amount over its
/// lifetime, so a rate is set as <c>amount_ratio</c> of <see cref="Max"/> (<see cref="Rate"/>); a burst is
/// <c>emit_particle</c>; the start size and lifetime ranges are scale_min/max and lifetime_randomness; Unity's noise is
/// turbulence; the stretched embers are plain small billboards; the breeze is a constant push (Unity: a velocity curve);
/// "run ahead" is preprocess (<see cref="Warm"/>). A level held out of the tree keeps its particles where they were.</para>
/// </summary>
public static class FireFx
{
    const string Dir = KitPaths.Addon + "FX/";
    static StandardMaterial3D body, gold, core, glow, glowHot, ember, smoke, hidden;
    static QuadMesh quad;
    static readonly Dictionary<Material, Material> coals = new();
    static readonly StringName MaxMeta = "fx_max";

    /// <summary>the flames' body (alpha blended, the soft-edged sheet)</summary>
    public static StandardMaterial3D BodyMaterial => body ??= Mat("M_FX_FlameBody", "FX_FlameSheet_soft.png", false, new Color(1.4f, 1.4f, 1.4f), 8, 0.4f, 2);
    /// <summary>holy fire's body (the same sheet burning gold)</summary>
    public static StandardMaterial3D GoldMaterial => gold ??= Mat("M_FX_FlameGold", "FX_FlameSheet_gold.png", false, new Color(1.4f, 1.4f, 1.4f), 8, 0.4f, 2);
    /// <summary>the flames' hot heart (additive, the hard-edged sheet)</summary>
    public static StandardMaterial3D CoreMaterial => core ??= Mat("M_FX_FlameCore", "FX_FlameSheet.png", true, new Color(0.6f, 0.6f, 0.6f), 8, 0.4f, 3);
    public static StandardMaterial3D GlowMaterial => glow ??= Mat("M_FX_Glow", "FX_Glow.png", true, Colors.White, 1, 0.8f, 1);
    /// <summary>a brighter glow (a fire circle's flash on the ground)</summary>
    public static StandardMaterial3D HotGlowMaterial => glowHot ??= Mat("M_FX_GlowHot", "FX_Glow.png", true, new Color(1.6f, 1.6f, 1.6f), 1, 0.8f, 1);
    public static StandardMaterial3D EmberMaterial => ember ??= Mat("M_FX_Ember", "FX_Spark.png", true, new Color(1.2f, 1.2f, 1.2f), 1, 0f, 4);
    public static StandardMaterial3D SmokeMaterial => smoke ??= Mat("M_FX_Smoke", "FX_SmokeSheet.png", false, Colors.White, 4, 1.2f, 0);

    /// <summary>an unshaded particle billboard material: the texture an n x n flipbook, tinted, additive or alpha
    /// blended, no depth write, soft against what it meets (proximity fade over `soft` m); priority: drawn over lower
    /// ones (the smoke 0, glow 1, body 2, core 3, embers 4: Unity's sorting fudges)</summary>
    static StandardMaterial3D Mat(string name, string tex, bool additive, Color tint, int frames, float soft, int priority)
    {
        var t = ResourceLoader.Exists(Dir + tex) ? GD.Load<Texture2D>(Dir + tex) : null;
        if (t == null) GD.PushWarning($"[FireFx] no {Dir + tex}: a plain blob");
        return new StandardMaterial3D
        {
            ResourceName = name,
            ShadingMode = BaseMaterial3D.ShadingModeEnum.Unshaded,
            Transparency = BaseMaterial3D.TransparencyEnum.Alpha,
            BlendMode = additive ? BaseMaterial3D.BlendModeEnum.Add : BaseMaterial3D.BlendModeEnum.Mix,
            BillboardMode = BaseMaterial3D.BillboardModeEnum.Particles,
            BillboardKeepScale = true,
            VertexColorUseAsAlbedo = true,
            AlbedoTexture = t,
            AlbedoColor = tint,
            ParticlesAnimHFrames = t != null ? frames : 1,
            ParticlesAnimVFrames = t != null ? frames : 1,
            ParticlesAnimLoop = true,
            CullMode = BaseMaterial3D.CullModeEnum.Disabled,
            DepthDrawMode = BaseMaterial3D.DepthDrawModeEnum.Disabled,
            DisableReceiveShadows = true,
            DisableFog = additive,
            ProximityFadeEnabled = soft > 0f,
            ProximityFadeDistance = soft,
            RenderPriority = priority,
        };
    }

    /// <summary>where a part's particles start: spots (each jittered up to <c>jitter</c> m), or a box (x, height, z)
    /// round <c>at</c>; in the parent's space, both send them upward</summary>
    public struct Source
    {
        public IList<Vector3> spots;
        public int count;
        public float jitter;
        public Vector3 at, box;

        public static Source Spots(IList<Vector3> spots, int count, float jitter) => new() { spots = spots, count = count, jitter = jitter };
        public static Source Box(Vector3 at, Vector3 box) => new() { at = at, box = box };
    }

    // ------------------------------------------------------------------ the parts

    /// <summary>flames licking up from the source: upright tongues, born small, full a quarter of the way up, fading as
    /// they rise; <paramref name="scale"/> 1 a siege engine's, about 0.4 a campfire's; the core is the smaller additive
    /// heart drawn over the body</summary>
    public static GpuParticles3D Flames(Node3D parent, Source src, float scale, float rate, int max, bool core = false, Vector2 life = default)
    {
        var mat = core ? CoreMaterial : BodyMaterial;
        if (life == default) life = core ? new Vector2(0.5f, 0.8f) : new Vector2(0.75f, 1.15f);
        return Particles(core ? "FlameCore" : "Flames", parent, src, mat, max, (ps, pm) =>
        {
            Life(ps, pm, life.X, life.Y);
            FlameSize(ps, scale, core);
            pm.AngleMin = -7f; pm.AngleMax = 7f;                                // upright
            Rise(pm, 0.5f * scale + 0.2f, 1.1f * scale + 0.3f + 0.15f * scale);
            Turbulence(pm, 0.35f * scale, 0.6f, 0.7f);
            FlameLook(ps, pm, core);
            Rate(ps, rate);
        });
    }

    /// <summary>flames from now on at <paramref name="scale"/>'s size (as <see cref="Flames"/> makes them; a fire dying down)</summary>
    public static void FlameSize(GpuParticles3D ps, float scale, bool core = false)
    {
        if (ps?.ProcessMaterial is not ParticleProcessMaterial pm) return;
        float s = scale * (core ? 0.6f : 1f);
        pm.ScaleMin = 1.4f * s; pm.ScaleMax = 2.2f * s;
    }

    /// <summary>how a flame changes over its life (dimming and reddening, swelling then shrinking, the flipbook played
    /// once from a random frame) and its order (the youngest in front)</summary>
    public static void FlameLook(GpuParticles3D ps, ParticleProcessMaterial pm, bool core)
    {
        pm.ColorRamp = Ramp(Grad(new[] { Colors.White, new Color(1f, 0.92f, 0.85f), new Color(0.8f, 0.45f, 0.35f) }, new[] { 0f, 0.45f, 1f },
                                 new[] { 0f, 1f, 0.95f, 0f }, new[] { 0f, 0.1f, 0.6f, 1f }));
        pm.ScaleCurve = CurveTex(0f, 0.5f, 0.25f, 1f, 1f, 0.7f);
        pm.AnimSpeedMin = 1f; pm.AnimSpeedMax = 1f;
        pm.AnimOffsetMin = 0f; pm.AnimOffsetMax = 1f;
        ps.DrawOrder = GpuParticles3D.DrawOrderEnum.Lifetime;
    }

    /// <summary>a soft warm glow round the flames: a few big faint additive puffs</summary>
    public static GpuParticles3D Glow(Node3D parent, Source src, float size, float rate, float alpha, int max = 12)
    {
        return Particles("Glow", parent, src, GlowMaterial, max, (ps, pm) =>
        {
            Life(ps, pm, 1f, 1.6f);
            pm.ScaleMin = size * 0.8f; pm.ScaleMax = size * 1.2f;
            pm.Color = new Color(1f, 0.55f, 0.2f);                               // firelight's orange
            pm.ColorRamp = Ramp(Grad(new[] { Colors.White, Colors.White }, new[] { 0f, 1f }, new[] { 0f, alpha, alpha, 0f }, new[] { 0f, 0.3f, 0.7f, 1f }));
            Rate(ps, rate);
        });
    }

    /// <summary>sparks flying up, yellow fading to red; now and then a burst of up to <paramref name="burst"/> (every 1.3 s,
    /// 70% of the time)</summary>
    public static GpuParticles3D Embers(Node3D parent, Source src, float rate, float speed, int burst, int max = 60)
    {
        var ps = Particles("Embers", parent, src, EmberMaterial, max, (ps, pm) =>
        {
            Life(ps, pm, 1f, 2.2f);
            pm.Direction = Vector3.Up; pm.Spread = 35f;
            pm.InitialVelocityMin = 1.5f * speed; pm.InitialVelocityMax = 3.5f * speed;
            pm.ScaleMin = 0.04f; pm.ScaleMax = 0.08f;
            pm.Gravity = new Vector3(0f, 0.08f * 9.81f, 0f);
            Turbulence(pm, 1.2f, 0.7f, 0.8f);
            EmberLook(ps, pm);
            Rate(ps, rate);
        });
        if (ps != null && burst > 0) ps.AddChild(new FireBursts { Name = "Bursts", Max = burst });
        return ps;
    }

    /// <summary>an ember's colour and size over its life (orange from the start: a paler spark comes out lime through
    /// the tonemapper)</summary>
    public static void EmberLook(GpuParticles3D ps, ParticleProcessMaterial pm)
    {
        pm.ColorRamp = Ramp(Grad(new[] { new Color(1f, 0.72f, 0.3f), new Color(1f, 0.42f, 0.1f), new Color(0.75f, 0.12f, 0.02f) }, new[] { 0f, 0.35f, 1f },
                                 new[] { 1f, 1f, 0f }, new[] { 0f, 0.6f, 1f }));
        pm.ScaleCurve = CurveTex(0f, 1f, 1f, 0.4f);
        ps.DrawOrder = GpuParticles3D.DrawOrderEnum.Index;
    }

    /// <summary>a column of smoke: puffs rising and spreading, bent by a breeze (east and a little north); from a burning
    /// thing dark low down, paling as it spreads, pale from a campfire or ash. <paramref name="life"/> and
    /// <paramref name="rise"/> are middles (the puffs vary round them)</summary>
    public static GpuParticles3D Smoke(Node3D parent, Source src, float rate, float size0, float size1, float alpha, float life, float rise,
                                       bool pale, int max = 120)
    {
        return Particles("Smoke", parent, src, SmokeMaterial, max, (ps, pm) =>
        {
            Life(ps, pm, life * 0.75f, life * 1.1f);
            pm.Direction = Vector3.Up; pm.Spread = 8f;
            pm.InitialVelocityMin = rise * 0.7f; pm.InitialVelocityMax = rise * 1.2f;
            pm.ScaleMin = size0; pm.ScaleMax = size1;
            pm.Gravity = new Vector3(0.28f, 0f, -0.1f);                         // the breeze (Unity: west on its axes)
            pm.DampingMin = 0.02f * rise; pm.DampingMax = 0.06f * rise;
            Turbulence(pm, 0.4f, 0.25f, 0.2f);
            SmokeLook(ps, pm, alpha, pale);
            Rate(ps, rate);
            Aabb(ps, 12f);
        });
    }

    /// <summary>a smoke puff's colour, growth and slow turn over its life (one random puff of the sheet), drawn behind the
    /// flames</summary>
    public static void SmokeLook(GpuParticles3D ps, ParticleProcessMaterial pm, float alpha, bool pale)
    {
        pm.AngleMin = 0f; pm.AngleMax = 360f;
        pm.AngularVelocityMin = -17f; pm.AngularVelocityMax = 17f;
        var c = pale ? new[] { new Color(0.62f, 0.58f, 0.54f), new Color(0.66f, 0.64f, 0.62f), new Color(0.7f, 0.7f, 0.7f) }
                     : new[] { new Color(0.36f, 0.26f, 0.19f), new Color(0.2f, 0.19f, 0.18f), new Color(0.6f, 0.59f, 0.58f) };
        float mid = pale ? 0.55f : 0.9f;                                    // dark smoke stays thick
        pm.ColorRamp = Ramp(Grad(c, new[] { 0f, 0.25f, 1f }, new[] { 0f, alpha, alpha * mid, 0f }, new[] { 0f, 0.12f, 0.55f, 1f }));
        pm.ScaleCurve = CurveTex(0f, 0.5f, 1f, 1.6f);
        pm.AnimSpeedMin = 0f; pm.AnimSpeedMax = 0f;
        pm.AnimOffsetMin = 0f; pm.AnimOffsetMax = 1f;
        ps.DrawOrder = GpuParticles3D.DrawOrderEnum.ViewDepth;
    }

    /// <summary>a warm omni light (no shadows), flickering</summary>
    public static FireFlicker Lamp(Node3D parent, Vector3 at, float intensity, float range)
    {
        var l = new OmniLight3D
        {
            Name = "Light", Position = at, LightColor = new Color(1f, 0.55f, 0.22f),
            LightEnergy = intensity * LightScale, OmniRange = range, ShadowEnabled = false,
        };
        parent.AddChild(l);
        var f = new FireFlicker { Name = "Flicker" };
        l.AddChild(f);
        return f;
    }

    /// <summary>Unity's light intensity to Godot's energy (the kit's lights: a candle 0.38, a hearth 10)</summary>
    public const float LightScale = 0.5f;

    /// <summary>a stump still smouldering on burnt land: a thin pale thread of smoke on the breeze, a spark now and then,
    /// a faint warm glow at its foot; no light. Already going when first seen</summary>
    public static Node3D Smoulder(Node3D parent, Vector3 position, float scale = 1f)
    {
        var go = new Node3D { Name = "Smoulder" };
        parent.AddChild(go);
        go.GlobalPosition = position;
        Smoke(go, Source.Box(new Vector3(0f, 0.55f, 0f) * scale, new Vector3(0.35f, 0.15f, 0.35f) * scale), 2.2f, 0.7f * scale, 1.4f * scale,
              0.32f, 7f, 0.55f, true, 40);
        Embers(go, Source.Box(new Vector3(0f, 0.4f, 0f) * scale, new Vector3(0.5f, 0.1f, 0.5f) * scale), 1.2f, 0.35f, 3, 10);
        Glow(go, Source.Box(new Vector3(0f, 0.3f, 0f) * scale, new Vector3(0.3f, 0.05f, 0.3f) * scale), 0.9f * scale, 2f, 0.22f, 6);
        Warm(go, 8f);
        return go;
    }

    // ------------------------------------------------------------------ settings

    /// <summary>every part under it run ahead this long when it starts (a fire already burning when first seen)</summary>
    public static void Warm(Node root, float seconds)
    {
        foreach (var ps in Parts(root))
        {
            ps.Preprocess = seconds;
            ps.Restart();
        }
    }

    /// <summary>Unity's: run ahead again each time a held level comes back. Godot keeps a held level's particles, so
    /// this only sets how far a restarted part runs ahead</summary>
    public static void KeepWarm(Node root, float seconds)
    {
        foreach (var ps in Parts(root)) ps.Preprocess = seconds;
    }

    /// <summary>a part's emission rate (per second): a share of its <see cref="Max"/> over its lifetime</summary>
    public static void Rate(GpuParticles3D ps, float rate)
    {
        if (ps == null) return;
        int max = ps.HasMeta(MaxMeta) ? (int)ps.GetMeta(MaxMeta) : ps.Amount;
        ps.AmountRatio = Mathf.Clamp(rate * (float)ps.Lifetime / Mathf.Max(1, max), 0f, 1f);
        ps.Emitting = rate > 0f || ps.OneShot;
    }

    /// <summary>a fire that never moves (a torch, a hearth): kept in its parent's space, with no turbulence</summary>
    public static GpuParticles3D Still(GpuParticles3D ps)
    {
        if (ps == null) return null;
        ps.LocalCoords = true;
        if (ps.ProcessMaterial is ParticleProcessMaterial pm) pm.TurbulenceEnabled = false;
        return ps;
    }

    /// <summary>a part that goes off once: <paramref name="count"/> particles at <paramref name="at"/> s</summary>
    public static void OneShot(GpuParticles3D ps, int count, float at)
    {
        ps.OneShot = true;
        ps.Explosiveness = 1f;
        ps.Amount = Mathf.Max(1, count);
        ps.SetMeta(MaxMeta, ps.Amount);
        ps.AmountRatio = 1f;
        ps.Emitting = at <= 0f;
        if (at > 0f) After(ps, at, () => ps.Emitting = true);
    }

    /// <summary>a bolt landed (it goes next): its parts in the world's space left where they are to fade out, then gone</summary>
    public static void LeaveBehind(Node3D bolt)
    {
        var tree = bolt.GetTree();
        foreach (var ps in Parts(bolt).ToList())
        {
            if (ps.LocalCoords) continue;
            var t = ps.GlobalTransform;
            ps.GetParent().RemoveChild(ps);
            (tree.CurrentScene ?? tree.Root).AddChild(ps);
            ps.GlobalTransform = t;
            ps.Emitting = false;
            FreeAfter(ps, (float)ps.Lifetime + 0.1f);
        }
    }

    /// <summary>the kit's glowing flame meshes in a piece (its M_VKI_GlowIn: a pale cone) turned to coals, deep orange to
    /// red, so the flames stand over embers; <paramref name="hide"/>: not drawn at all (a bonfire's cones stand far above
    /// the flames)</summary>
    public static void Coals(Node piece, bool hide = false)
    {
        if (piece == null) return;
        hidden ??= new StandardMaterial3D
        {
            ResourceName = "M_FX_Hidden", ShadingMode = BaseMaterial3D.ShadingModeEnum.Unshaded, Transparency = BaseMaterial3D.TransparencyEnum.Alpha,
            AlbedoColor = new Color(0, 0, 0, 0), DepthDrawMode = BaseMaterial3D.DepthDrawModeEnum.Disabled,
        };
        foreach (var n in KitNodes.Below(piece, "MeshInstance3D"))
        {
            var mi = (MeshInstance3D)n;
            if (mi.Mesh == null) continue;
            for (int s = 0; s < mi.Mesh.GetSurfaceCount(); s++)
            {
                if (mi.GetActiveMaterial(s) is not ShaderMaterial m || !m.ResourcePath.GetFile().StartsWith("M_VKI_GlowIn")) continue;
                if (!coals.TryGetValue(m, out var c))
                {
                    var cm = (ShaderMaterial)m.Duplicate();
                    cm.SetShaderParameter("rim_color_a", new Color(1f, 0.42f, 0.1f));
                    cm.SetShaderParameter("rim_color_b", new Color(0.5f, 0.06f, 0.02f));
                    cm.SetShaderParameter("rim_k", new Vector2(-1.2f, 1.3f));
                    coals[m] = c = cm;
                }
                mi.SetSurfaceOverrideMaterial(s, hide ? hidden : c);
            }
        }
    }

    // ------------------------------------------------------------------ building a part

    /// <summary>a part under parent: world-space billboards from the source (spots: emission points; a box), no shadows,
    /// at most `max` alive, emitting once set up</summary>
    public static GpuParticles3D Particles(string name, Node3D parent, Source src, Material mat, int max, Action<GpuParticles3D, ParticleProcessMaterial> setup)
    {
        if (mat == null || parent == null) return null;
        quad ??= new QuadMesh { Size = Vector2.One };
        var pm = new ParticleProcessMaterial
        {
            Direction = Vector3.Up, Spread = 0f, Gravity = Vector3.Zero, InitialVelocityMin = 0f, InitialVelocityMax = 0f,
        };
        var ps = new GpuParticles3D
        {
            Name = name, Amount = Mathf.Max(1, max), ProcessMaterial = pm, DrawPass1 = quad, MaterialOverride = mat,
            CastShadow = GeometryInstance3D.ShadowCastingSetting.Off, LocalCoords = false, Emitting = false,
        };
        ps.SetMeta(MaxMeta, ps.Amount);
        Aabb(ps, 4f);
        parent.AddChild(ps);
        if (src.spots != null) SetSpots(ps, src.spots, src.count, src.jitter);
        else
        {
            ps.Position = src.at;
            pm.EmissionShape = ParticleProcessMaterial.EmissionShapeEnum.Box;
            pm.EmissionBoxExtents = new Vector3(Mathf.Max(0.001f, src.box.X), Mathf.Max(0.001f, src.box.Y), Mathf.Max(0.001f, src.box.Z)) * 0.5f;
        }
        setup(ps, pm);
        if (!ps.OneShot && !ps.Emitting && ps.AmountRatio > 0f) ps.Emitting = true;
        return ps;
    }

    /// <summary>emitted from the first `count` spots (in its parent's space; at least one), each jittered round up to
    /// `jitter` m: eight points per spot (Godot's emission points take no jitter of their own)</summary>
    public static void SetSpots(GpuParticles3D ps, IList<Vector3> spots, int count, float jitter)
    {
        if (ps?.ProcessMaterial is not ParticleProcessMaterial pm) return;
        count = Mathf.Clamp(count, 1, Mathf.Max(1, spots.Count));
        const int per = 8;
        var img = Image.CreateEmpty(count * per, 1, false, Image.Format.Rgbf);
        var rng = new Random(count * 7919 + spots.Count);
        for (int i = 0; i < count; i++)
        {
            var p = spots.Count > 0 ? spots[i] : Vector3.Zero;
            for (int k = 0; k < per; k++)
            {
                var j = k == 0 ? Vector3.Zero : new Vector3((float)rng.NextDouble() * 2f - 1f, 0f, (float)rng.NextDouble() * 2f - 1f) * jitter;
                var q = p + j;
                img.SetPixel(i * per + k, 0, new Color(q.X, q.Y, q.Z));
            }
        }
        ps.Position = Vector3.Zero;
        pm.EmissionShape = ParticleProcessMaterial.EmissionShapeEnum.Points;
        pm.EmissionPointTexture = ImageTexture.CreateFromImage(img);
        pm.EmissionPointCount = count * per;
    }

    /// <summary>lifetime: up to b, down to a (Godot shortens at random)</summary>
    public static void Life(GpuParticles3D ps, ParticleProcessMaterial pm, float a, float b)
    {
        ps.Lifetime = Mathf.Max(0.05f, b);
        pm.LifetimeRandomness = Mathf.Clamp(1f - a / Mathf.Max(0.05f, b), 0f, 1f);
    }

    /// <summary>rising at this speed (m/s), up</summary>
    public static void Rise(ParticleProcessMaterial pm, float v0, float v1)
    {
        pm.Direction = Vector3.Up; pm.Spread = 4f;
        pm.InitialVelocityMin = v0; pm.InitialVelocityMax = v1;
    }

    static void Turbulence(ParticleProcessMaterial pm, float strength, float frequency, float speed)
    {
        pm.TurbulenceEnabled = true;
        pm.TurbulenceNoiseStrength = 1f;
        pm.TurbulenceNoiseScale = Mathf.Clamp(1f / Mathf.Max(0.05f, frequency), 0.5f, 8f);
        pm.TurbulenceNoiseSpeed = new Vector3(0f, speed, 0f);
        pm.TurbulenceInfluenceMin = Mathf.Clamp(0.06f * strength, 0f, 1f);
        pm.TurbulenceInfluenceMax = Mathf.Clamp(0.12f * strength, 0f, 1f);
    }

    /// <summary>the box it is culled by (it is drawn while the box is in view): `reach` metres round, more upward</summary>
    static void Aabb(GpuParticles3D ps, float reach) => ps.VisibilityAabb = new Aabb(new Vector3(-reach, -1f, -reach), new Vector3(2f * reach, 2f * reach + 1f, 2f * reach));

    public static IEnumerable<GpuParticles3D> Parts(Node root) =>
        root == null ? Enumerable.Empty<GpuParticles3D>() :
        (root is GpuParticles3D self ? new[] { self } : Enumerable.Empty<GpuParticles3D>())
            .Concat(KitNodes.Below(root, "GPUParticles3D").OfType<GpuParticles3D>());

    /// <summary>a gradient through colour keys and alpha keys (Unity's: the two sets at their own times)</summary>
    public static Gradient Grad(Color[] c, float[] ct, float[] a, float[] at)
    {
        var times = ct.Concat(at).Distinct().OrderBy(x => x).ToArray();
        var g = new Gradient();
        g.Offsets = times;
        g.Colors = times.Select(t =>
        {
            var col = Sample(c.Select(x => new Vector3(x.R, x.G, x.B)).ToArray(), ct, t);
            float al = Sample(a.Select(x => new Vector3(x, 0, 0)).ToArray(), at, t).X;
            return new Color(col.X, col.Y, col.Z, al);
        }).ToArray();
        return g;
    }

    static Vector3 Sample(Vector3[] v, float[] t, float x)
    {
        if (x <= t[0]) return v[0];
        for (int i = 1; i < t.Length; i++)
            if (x <= t[i]) return v[i - 1].Lerp(v[i], (x - t[i - 1]) / Mathf.Max(1e-5f, t[i] - t[i - 1]));
        return v[^1];
    }

    static GradientTexture1D Ramp(Gradient g) => new() { Gradient = g, Width = 64 };

    /// <summary>a smooth curve through (time, value) pairs, as a texture</summary>
    public static CurveTexture CurveTex(params float[] tv)
    {
        var c = new Curve();
        float top = 1f;
        for (int i = 1; i < tv.Length; i += 2) top = Mathf.Max(top, tv[i]);
        c.MaxValue = top;
        for (int i = 0; i + 1 < tv.Length; i += 2) c.AddPoint(new Vector2(tv[i], tv[i + 1]));
        for (int i = 0; i < c.PointCount; i++) { c.SetPointLeftMode(i, Curve.TangentMode.Free); c.SetPointRightMode(i, Curve.TangentMode.Free); }
        return new CurveTexture { Curve = c, Width = 64 };
    }

    /// <summary>run something after a while (while the node lives)</summary>
    public static void After(Node n, float seconds, Action then)
    {
        var tree = n.IsInsideTree() ? n.GetTree() : (SceneTree)Engine.GetMainLoop();
        tree.CreateTimer(seconds).Timeout += () => { if (GodotObject.IsInstanceValid(n)) then(); };
    }

    /// <summary>free it after a while</summary>
    public static void FreeAfter(Node n, float seconds) => After(n, seconds, n.QueueFree);
}

/// <summary>an ember part's bursts (<see cref="FireFx.Embers"/>): every 1.3 s, 70% of the time, half to all of
/// <see cref="Max"/> more at once (Unity's burst)</summary>
public partial class FireBursts : Node
{
    public int Max = 6;
    double next = 0.3;
    readonly Random rng = new();

    public override void _Process(double delta)
    {
        if ((next -= delta) > 0 || GetParent() is not GpuParticles3D ps || !ps.Emitting) return;
        next = 1.3;
        if (rng.NextDouble() > 0.7) return;
        int n = rng.Next(Mathf.Max(1, Max / 2), Max + 1);
        for (int i = 0; i < n; i++) ps.EmitParticle(Transform3D.Identity, Vector3.Zero, Colors.White, Colors.White, 0);
    }
}
