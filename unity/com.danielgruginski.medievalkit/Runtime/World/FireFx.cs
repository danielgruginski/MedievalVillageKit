using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace MedievalKit
{
    /// <summary>
    /// The parts every fire in the game is made of (<see cref="Fire"/>, <see cref="Campfire"/>): upright tongues of flame
    /// (an 8 x 8 flipbook, alpha blended, so flames piled on each other never wash out to white) with a smaller additive
    /// core, a faint glow, stretched embers, a smoke column (a 4 x 4 sheet of puffs) and a flickering light
    /// (<see cref="FireFlicker"/>). Flames start at spots (<see cref="SpotMesh"/>: a mesh of tiny triangles a particle
    /// shape emits from), not in a volume. A fire that never moves is kept <see cref="Still"/> (Unity culls it off
    /// screen); the kit's glowing flame meshes under a fire are turned to <see cref="Coals"/>. The materials are assets in Resources/FX (Game > Create FX Materials, on
    /// Tools~/fx/make_fx.py's textures), so the URP particle shader and its soft-particle variant ship in a build; a plain
    /// one made in code (a soft blob, no flipbook) stands in if they are missing.
    /// </summary>
    public static class FireFx
    {
        static Material body, gold, core, glow, glowHot, ember, smoke, hidden;
        static Texture2D blob;
        static readonly Dictionary<Material, Material> coals = new Dictionary<Material, Material>();

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        static void ResetStatics() { body = gold = core = glow = glowHot = ember = smoke = hidden = null; blob = null; coals.Clear(); }

        /// <summary>the flames' body (alpha blended, the soft-edged sheet)</summary>
        public static Material BodyMaterial => Load(ref body, "M_FX_FlameBody", false);
        /// <summary>holy fire's body (the same sheet burning gold)</summary>
        public static Material GoldMaterial => Load(ref gold, "M_FX_FlameGold", false);
        /// <summary>the flames' hot heart (additive, the hard-edged sheet)</summary>
        public static Material CoreMaterial => Load(ref core, "M_FX_FlameCore", true);
        public static Material GlowMaterial => Load(ref glow, "M_FX_Glow", true);
        /// <summary>a brighter glow (a fire circle's flash on the ground)</summary>
        public static Material HotGlowMaterial => Load(ref glowHot, "M_FX_GlowHot", true);
        public static Material EmberMaterial => Load(ref ember, "M_FX_Ember", true);
        public static Material SmokeMaterial => Load(ref smoke, "M_FX_Smoke", false);

        /// <summary>where a system's particles start: the spots of a spot mesh (each jittered up to <c>jitter</c> m), or a
        /// box (x, height, z) round <c>at</c>; in the parent's space, both send them upward</summary>
        public struct Source
        {
            public Mesh spots;
            public float jitter;
            public Vector3 at, box;

            public static Source Spots(Mesh spots, float jitter) => new Source { spots = spots, jitter = jitter };
            public static Source Box(Vector3 at, Vector3 box) => new Source { at = at, box = box };
        }

        /// <summary>a mesh of tiny (2 cm) triangles facing up, one at each of the first <paramref name="count"/> spots (at
        /// least one): flames emitted from its vertices start only there (a fresh one each time: a particle system's
        /// shape warns about a mesh cleared under it)</summary>
        public static Mesh SpotMesh(IList<Vector3> spots, int count)
        {
            var m = new Mesh { name = "FireSpots" };
            count = Mathf.Clamp(count, 1, Mathf.Max(1, spots.Count));
            var v = new Vector3[count * 3];
            var n = new Vector3[count * 3];
            var t = new int[count * 3];
            for (int i = 0; i < count; i++)
            {
                var p = spots.Count > 0 ? spots[i] : Vector3.zero;
                v[i * 3] = p + new Vector3(-0.02f, 0f, -0.02f);
                v[i * 3 + 1] = p + new Vector3(0f, 0f, 0.02f);
                v[i * 3 + 2] = p + new Vector3(0.02f, 0f, -0.02f);
                for (int k = 0; k < 3; k++) { n[i * 3 + k] = Vector3.up; t[i * 3 + k] = i * 3 + k; }
            }
            m.vertices = v; m.normals = n; m.triangles = t;
            m.RecalculateBounds();
            return m;
        }

        /// <summary>flames licking up from the source: upright tongues, born small, full a quarter of the way up, fading
        /// as they rise; <paramref name="scale"/> 1 a siege engine's, about 0.4 a campfire's; the core is the smaller
        /// additive heart drawn over the body</summary>
        public static ParticleSystem Flames(Transform parent, Source src, float scale, float rate, int max, bool core = false, Vector2 life = default)
        {
            var mat = core ? CoreMaterial : BodyMaterial;
            if (mat == null) return null;
            if (life == default) life = core ? new Vector2(0.5f, 0.8f) : new Vector2(0.75f, 1.15f);
            return Particles(core ? "FlameCore" : "Flames", parent, src.at, mat, (ps, r) =>
            {
                var main = ps.main;
                main.loop = true;
                main.startLifetime = new ParticleSystem.MinMaxCurve(life.x, life.y);
                main.startSpeed = new ParticleSystem.MinMaxCurve(0f, 0.15f * scale);
                FlameSize(ps, scale, core);
                main.startRotation = new ParticleSystem.MinMaxCurve(-0.12f, 0.12f);     // upright
                main.maxParticles = Mathf.Max(4, max);
                var em = ps.emission;
                em.rateOverTime = rate;
                Shape(ps, src);
                Rise(ps, 0.5f * scale + 0.2f, 1.1f * scale + 0.3f);
                var noise = ps.noise;
                noise.enabled = true; noise.strength = 0.35f * scale; noise.frequency = 0.6f; noise.scrollSpeed = 0.7f; noise.damping = true;
                FlameLook(ps, r, mat, core);
            });
        }

        /// <summary>flames from now on at <paramref name="scale"/>'s size (as <see cref="Flames"/> makes them; a fire dying down)</summary>
        public static void FlameSize(ParticleSystem ps, float scale, bool core = false)
        {
            if (ps == null) return;
            float s = scale * (core ? 0.6f : 1f);
            var main = ps.main;
            main.startSize = new ParticleSystem.MinMaxCurve(1.4f * s, 2.2f * s);
        }

        /// <summary>how a flame changes over its life (dimming and reddening, swelling then shrinking, the flipbook played
        /// once) and its draw order (the core over the body)</summary>
        public static void FlameLook(ParticleSystem ps, ParticleSystemRenderer r, Material mat, bool core)
        {
            var col = ps.colorOverLifetime;
            col.enabled = true;
            col.color = Grad(new[] { Color.white, new Color(1f, 0.92f, 0.85f), new Color(0.8f, 0.45f, 0.35f) }, new[] { 0f, 0.45f, 1f },
                             new[] { 0f, 1f, 0.95f, 0f }, new[] { 0f, 0.1f, 0.6f, 1f });
            var size = ps.sizeOverLifetime;
            size.enabled = true;
            size.size = new ParticleSystem.MinMaxCurve(1f, Curve(0f, 0.5f, 0.25f, 1f, 1f, 0.7f));
            Sheet(ps, mat, 8, true);
            r.sortMode = ParticleSystemSortMode.YoungestInFront;
            r.sortingFudge = core ? -11f : -10f;
        }

        /// <summary>a soft warm glow round the flames: a few big faint additive puffs</summary>
        public static ParticleSystem Glow(Transform parent, Source src, float size, float rate, float alpha, int max = 12)
        {
            var mat = GlowMaterial;
            if (mat == null) return null;
            return Particles("Glow", parent, src.at, mat, (ps, r) =>
            {
                var main = ps.main;
                main.loop = true;
                main.startLifetime = new ParticleSystem.MinMaxCurve(1f, 1.6f);
                main.startSpeed = 0f;
                main.startSize = new ParticleSystem.MinMaxCurve(size * 0.8f, size * 1.2f);
                main.startColor = new Color(1f, 0.55f, 0.2f);                  // firelight's orange (redder reads as a pink fog)
                main.maxParticles = max;
                var em = ps.emission;
                em.rateOverTime = rate;
                Shape(ps, src);
                var col = ps.colorOverLifetime;
                col.enabled = true;
                col.color = Grad(new[] { Color.white, Color.white }, new[] { 0f, 1f }, new[] { 0f, alpha, alpha, 0f }, new[] { 0f, 0.3f, 0.7f, 1f });
                r.sortingFudge = -5f;
            });
        }

        /// <summary>sparks flying up, yellow fading to red, stretched along their flight; now and then a burst of up to
        /// <paramref name="burst"/> (every 1.3 s, 70% of the time)</summary>
        public static ParticleSystem Embers(Transform parent, Source src, float rate, float speed, int burst, int max = 60)
        {
            var mat = EmberMaterial;
            if (mat == null) return null;
            return Particles("Embers", parent, src.at, mat, (ps, r) =>
            {
                var main = ps.main;
                main.loop = true;
                main.startLifetime = new ParticleSystem.MinMaxCurve(1f, 2.2f);
                main.startSpeed = new ParticleSystem.MinMaxCurve(1.5f * speed, 3.5f * speed);
                main.startSize = new ParticleSystem.MinMaxCurve(0.04f, 0.08f);
                main.gravityModifier = -0.08f;
                main.maxParticles = max;
                var em = ps.emission;
                em.rateOverTime = rate;
                if (burst > 0) em.SetBursts(new[] { new ParticleSystem.Burst(0.3f, (short)Mathf.Max(1, burst / 2), (short)burst, 4, 1.3f) { probability = 0.7f } });
                Shape(ps, src);
                var sh = ps.shape;
                sh.randomDirectionAmount = 0.35f;
                var noise = ps.noise;
                noise.enabled = true; noise.strength = 1.2f; noise.frequency = 0.7f; noise.scrollSpeed = 0.8f; noise.damping = true;
                EmberLook(ps, r);
            });
        }

        /// <summary>an ember's colour and size over its life, drawn stretched along its flight, over the flames (orange from
        /// the start: a paler spark comes out lime through the tonemapper)</summary>
        public static void EmberLook(ParticleSystem ps, ParticleSystemRenderer r)
        {
            var col = ps.colorOverLifetime;
            col.enabled = true;
            col.color = Grad(new[] { new Color(1f, 0.72f, 0.3f), new Color(1f, 0.42f, 0.1f), new Color(0.75f, 0.12f, 0.02f) }, new[] { 0f, 0.35f, 1f },
                             new[] { 1f, 1f, 0f }, new[] { 0f, 0.6f, 1f });
            var size = ps.sizeOverLifetime;
            size.enabled = true;
            size.size = new ParticleSystem.MinMaxCurve(1f, Curve(0f, 1f, 1f, 0.4f));
            r.renderMode = ParticleSystemRenderMode.Stretch;
            r.velocityScale = 0.05f; r.lengthScale = 1.5f; r.cameraVelocityScale = 0f;
            r.sortingFudge = -12f;
        }

        /// <summary>a column of smoke: puffs rising and spreading, bent by a breeze (west, to the screen's right, and a
        /// little north); from a burning thing dark low down (warm at first, lit by the fire), paling as it spreads (so
        /// some of the column stands out on dark ground or pale), pale from a campfire or ash.
        /// <paramref name="life"/> and <paramref name="rise"/> are middles (the puffs vary round them)</summary>
        public static ParticleSystem Smoke(Transform parent, Source src, float rate, float size0, float size1, float alpha, float life, float rise,
                                           bool pale, int max = 120)
        {
            var mat = SmokeMaterial;
            if (mat == null) return null;
            return Particles("Smoke", parent, src.at, mat, (ps, r) =>
            {
                var main = ps.main;
                main.loop = true;
                main.startLifetime = new ParticleSystem.MinMaxCurve(life * 0.75f, life * 1.1f);
                main.startSpeed = new ParticleSystem.MinMaxCurve(rise * 0.7f, rise * 1.2f);
                main.startSize = new ParticleSystem.MinMaxCurve(size0, size1);
                main.maxParticles = max;
                var em = ps.emission;
                em.rateOverTime = rate;
                Shape(ps, src);
                var vel = ps.velocityOverLifetime;                      // the breeze (all three as curves: one mode)
                vel.enabled = true; vel.space = ParticleSystemSimulationSpace.World;
                vel.x = new ParticleSystem.MinMaxCurve(1f, Curve(0f, -0.1f, 1f, -1.4f));
                vel.y = new ParticleSystem.MinMaxCurve(1f, Curve(0f, 0f, 1f, 0f));
                vel.z = new ParticleSystem.MinMaxCurve(1f, Curve(0f, 0f, 1f, -0.5f));
                var lim = ps.limitVelocityOverLifetime;
                lim.enabled = true; lim.limit = rise * 1.2f; lim.dampen = 0.08f;
                var noise = ps.noise;
                noise.enabled = true; noise.strength = 0.4f; noise.frequency = 0.25f; noise.scrollSpeed = 0.2f; noise.damping = true;
                SmokeLook(ps, r, mat, alpha, pale);
            });
        }

        /// <summary>a smoke puff's colour, growth and slow turn over its life (one random puff of the sheet), drawn behind
        /// the flames</summary>
        public static void SmokeLook(ParticleSystem ps, ParticleSystemRenderer r, Material mat, float alpha, bool pale)
        {
            var main = ps.main;
            main.startRotation = new ParticleSystem.MinMaxCurve(0f, Mathf.PI * 2f);
            var col = ps.colorOverLifetime;
            col.enabled = true;
            var c = pale ? new[] { new Color(0.62f, 0.58f, 0.54f), new Color(0.66f, 0.64f, 0.62f), new Color(0.7f, 0.7f, 0.7f) }
                         : new[] { new Color(0.36f, 0.26f, 0.19f), new Color(0.2f, 0.19f, 0.18f), new Color(0.6f, 0.59f, 0.58f) };
            float mid = pale ? 0.55f : 0.9f;                                // dark smoke stays thick (thin, it is lost on burnt ground)
            col.color = Grad(c, new[] { 0f, 0.25f, 1f }, new[] { 0f, alpha, alpha * mid, 0f }, new[] { 0f, 0.12f, 0.55f, 1f });
            var size = ps.sizeOverLifetime;
            size.enabled = true;
            size.size = new ParticleSystem.MinMaxCurve(1f, Curve(0f, 0.5f, 1f, 1.6f));
            var rot = ps.rotationOverLifetime;
            rot.enabled = true; rot.z = new ParticleSystem.MinMaxCurve(-0.3f, 0.3f);
            Sheet(ps, mat, 4, false);
            r.sortMode = ParticleSystemSortMode.Distance;
            r.sortingFudge = 10f;
        }

        /// <summary>a warm point light (no shadows), flickering</summary>
        public static FireFlicker Lamp(Transform parent, Vector3 at, float intensity, float range)
        {
            var go = new GameObject("Light");
            go.transform.SetParent(parent, false);
            go.transform.localPosition = at;
            var l = go.AddComponent<Light>();
            l.type = LightType.Point;
            l.color = new Color(1f, 0.55f, 0.22f);
            l.intensity = intensity; l.range = range; l.shadows = LightShadows.None;
            return go.AddComponent<FireFlicker>();
        }

        /// <summary>a stump still smouldering on burnt land (2026-10-24, the burnt maps' dressing: a layout's "smoulder"
        /// marker): a thin pale thread of smoke on the breeze, a spark now and then, a faint warm glow at its foot; no light,
        /// no harm. Already going when first seen</summary>
        public static GameObject Smoulder(Transform parent, Vector3 position, float scale = 1f)
        {
            var go = new GameObject("Smoulder");
            go.transform.SetParent(parent, false);
            go.transform.position = position;
            Smoke(go.transform, Source.Box(new Vector3(0f, 0.55f, 0f) * scale, new Vector3(0.35f, 0.15f, 0.35f) * scale), 2.2f, 0.7f * scale, 1.4f * scale,
                  0.32f, 7f, 0.55f, true, 40);
            Embers(go.transform, Source.Box(new Vector3(0f, 0.4f, 0f) * scale, new Vector3(0.5f, 0.1f, 0.5f) * scale), 1.2f, 0.35f, 3, 10);
            Glow(go.transform, Source.Box(new Vector3(0f, 0.3f, 0f) * scale, new Vector3(0.3f, 0.05f, 0.3f) * scale), 0.9f * scale, 2f, 0.22f, 6);
            Warm(go, 8f);
            KeepWarm(go, 8f);
            return go;
        }

        /// <summary>every system under it run ahead this long (a fire already burning when it is first seen), then playing</summary>
        public static void Warm(GameObject root, float seconds)
        {
            foreach (var ps in root.GetComponentsInChildren<ParticleSystem>())
            {
                ps.Simulate(seconds, false, true, true);
                ps.Play(false);
            }
        }

        /// <summary>run ahead this long again each time it is switched back on (a level held switched off comes back: Unity
        /// clears a switched-off system's particles, and it would start again from nothing)</summary>
        public static void KeepWarm(GameObject root, float seconds)
        {
            if (!root.TryGetComponent<FireWarm>(out var w)) w = root.AddComponent<FireWarm>();
            w.seconds = seconds;
        }

        /// <summary>a system's emission rate (per second)</summary>
        public static void Rate(ParticleSystem ps, float rate)
        {
            if (ps == null) return;
            var em = ps.emission;
            em.rateOverTime = rate;
        }

        /// <summary>a fire that never moves (a torch, a hearth): kept in its parent's space, with no noise, so Unity can
        /// work it out ahead: paused off screen (a dungeon has dozens), caught up the moment it is seen again</summary>
        public static ParticleSystem Still(ParticleSystem ps)
        {
            if (ps == null) return null;
            var main = ps.main;
            main.simulationSpace = ParticleSystemSimulationSpace.Local;
            main.cullingMode = ParticleSystemCullingMode.PauseAndCatchup;
            var noise = ps.noise;
            noise.enabled = false;
            var vel = ps.velocityOverLifetime;
            if (vel.enabled) vel.space = ParticleSystemSimulationSpace.Local;
            return ps;
        }

        /// <summary>a system that goes off once: <paramref name="count"/> particles at <paramref name="at"/> s (and
        /// <paramref name="again"/> more 0.2 s later)</summary>
        public static void OneShot(ParticleSystem ps, int count, float at, int again = 0)
        {
            var main = ps.main;
            main.loop = false; main.duration = Mathf.Max(0.2f, at + 0.3f);
            main.maxParticles = count + again;
            var em = ps.emission;
            em.rateOverTime = 0f;
            em.SetBursts(again > 0 ? new[] { new ParticleSystem.Burst(at, (short)count), new ParticleSystem.Burst(at + 0.2f, (short)again) }
                                   : new[] { new ParticleSystem.Burst(at, (short)count) });
        }

        /// <summary>a bolt landed (it goes next): the trails it dropped in the world (systems in world space, streaks)
        /// left where they are to fade out, then gone</summary>
        public static void LeaveBehind(Transform bolt)
        {
            foreach (var ps in bolt.GetComponentsInChildren<ParticleSystem>())
            {
                if (ps.main.simulationSpace != ParticleSystemSimulationSpace.World) continue;
                ps.transform.SetParent(null, true);
                ps.Stop(true, ParticleSystemStopBehavior.StopEmitting);
                Object.Destroy(ps.gameObject, ps.main.startLifetime.constantMax + 0.1f);
            }
            foreach (var tr in bolt.GetComponentsInChildren<TrailRenderer>())
            {
                tr.transform.SetParent(null, true);
                tr.emitting = false;
                Object.Destroy(tr.gameObject, tr.time + 0.05f);
            }
        }

        /// <summary>a system's particles emitted by the metre it moves, not by the second (a bolt's trail)</summary>
        public static void PerMetre(ParticleSystem ps, float rate)
        {
            if (ps == null) return;
            var em = ps.emission;
            em.rateOverTime = 0f;
            em.rateOverDistance = rate;
        }

        /// <summary>the kit's glowing flame meshes in a piece (its M_VKI_GlowIn: a pale cone) turned to coals, deep orange
        /// to red, so the flames stand over embers, not over a second, cold fire; <paramref name="hide"/>: not drawn at all
        /// (the goblins' bonfire: its cones stand far above the flames)</summary>
        public static void Coals(GameObject piece, bool hide = false)
        {
            if (hide && hidden == null && GlowMaterial != null)
            {
                hidden = new Material(GlowMaterial) { name = "M_FX_Hidden" };    // additive black: adds nothing
                hidden.SetColor("_BaseColor", Color.clear);
            }
            if (piece == null) return;
            foreach (var r in piece.GetComponentsInChildren<Renderer>(true))
            {
                var mats = r.sharedMaterials;
                bool hit = false;
                for (int i = 0; i < mats.Length; i++)
                {
                    var m = mats[i];
                    if (m == null || !m.name.StartsWith("M_VKI_GlowIn") || !m.HasProperty("_RimColorA")) continue;
                    if (!coals.TryGetValue(m, out var c))
                    {
                        c = new Material(m) { name = m.name + "_Coals" };
                        c.SetColor("_RimColorA", new Color(1f, 0.42f, 0.1f));
                        c.SetColor("_RimColorB", new Color(0.5f, 0.06f, 0.02f));
                        c.SetVector("_RimK", new Vector4(-1.2f, 1.3f, 0f, 0f));
                        coals[m] = c;
                    }
                    mats[i] = hide && hidden != null ? hidden : c;
                    hit = true;
                }
                if (hit) r.sharedMaterials = mats;
            }
        }

        /// <summary>a particle system built switched off (so its settings take before it plays), then started: world
        /// space, billboards, no shadows, allowed big on the screen (a close camera)</summary>
        public static ParticleSystem Particles(string name, Transform parent, Vector3 at, Material mat, System.Action<ParticleSystem, ParticleSystemRenderer> setup)
        {
            var go = new GameObject(name);
            go.SetActive(false);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = at;
            var ps = go.AddComponent<ParticleSystem>();
            var r = go.GetComponent<ParticleSystemRenderer>();
            if (r == null) r = go.AddComponent<ParticleSystemRenderer>();
            r.sharedMaterial = mat;
            r.renderMode = ParticleSystemRenderMode.Billboard;
            r.shadowCastingMode = ShadowCastingMode.Off;
            r.receiveShadows = false;
            r.maxParticleSize = 2f;
            var main = ps.main;
            main.playOnAwake = true;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.scalingMode = ParticleSystemScalingMode.Shape;            // the spots follow the piece; sizes stay metres
            main.startColor = Color.white;
            main.gravityModifier = 0f;
            setup(ps, r);
            go.SetActive(true);
            return ps;
        }

        /// <summary>rising at this speed (m/s) all their life (the other two axes still: one curve mode for the three)</summary>
        public static void Rise(ParticleSystem ps, float v0, float v1)
        {
            var vel = ps.velocityOverLifetime;
            vel.enabled = true; vel.space = ParticleSystemSimulationSpace.World;
            vel.x = new ParticleSystem.MinMaxCurve(0f, 0f);
            vel.y = new ParticleSystem.MinMaxCurve(v0, v1);
            vel.z = new ParticleSystem.MinMaxCurve(0f, 0f);
        }

        static void Shape(ParticleSystem ps, Source src)
        {
            var sh = ps.shape;
            sh.enabled = true;
            if (src.spots != null)
            {
                sh.shapeType = ParticleSystemShapeType.Mesh;
                sh.meshShapeType = ParticleSystemMeshShapeType.Vertex;
                sh.mesh = src.spots;
                sh.useMeshColors = false;
                sh.randomPositionAmount = src.jitter;
            }
            else
            {
                sh.shapeType = ParticleSystemShapeType.Box;                 // a box emits along its Z: turned to rise, its Y
                sh.rotation = new Vector3(-90f, 0f, 0f);                    // is the world's depth, its Z the height
                sh.scale = new Vector3(src.box.x, src.box.z, src.box.y);
            }
        }

        /// <summary>the material's n x n flipbook: played through once over the life from a random frame (flames), or one
        /// random frame (smoke puffs); nothing on the stand-in blob</summary>
        static void Sheet(ParticleSystem ps, Material mat, int n, bool play)
        {
            if (mat.mainTexture == null || mat.mainTexture == blob) return;
            var ts = ps.textureSheetAnimation;
            ts.enabled = true;
            ts.mode = ParticleSystemAnimationMode.Grid;
            ts.numTilesX = n; ts.numTilesY = n;
            ts.animation = ParticleSystemAnimationType.WholeSheet;
            ts.frameOverTime = play ? new ParticleSystem.MinMaxCurve(1f, AnimationCurve.Linear(0f, 0f, 1f, 1f)) : new ParticleSystem.MinMaxCurve(0f);
            ts.cycleCount = 1;
            ts.startFrame = new ParticleSystem.MinMaxCurve(0f, 1f);         // 0..1 of the sheet in code, not a frame number
        }

        public static Gradient Grad(Color[] c, float[] ct, float[] a, float[] at)
        {
            var g = new Gradient();
            var ck = new GradientColorKey[c.Length];
            for (int i = 0; i < c.Length; i++) ck[i] = new GradientColorKey(c[i], ct[i]);
            var ak = new GradientAlphaKey[a.Length];
            for (int i = 0; i < a.Length; i++) ak[i] = new GradientAlphaKey(a[i], at[i]);
            g.SetKeys(ck, ak);
            return g;
        }

        /// <summary>a smooth curve through (time, value) pairs</summary>
        public static AnimationCurve Curve(params float[] tv)
        {
            var k = new Keyframe[tv.Length / 2];
            for (int i = 0; i < k.Length; i++) k[i] = new Keyframe(tv[i * 2], tv[i * 2 + 1]);
            var c = new AnimationCurve(k);
            for (int i = 0; i < k.Length; i++) c.SmoothTangents(i, 0f);
            return c;
        }

        /// <summary>the material from Resources/FX, else a stand-in made in code (the spells' too: <see cref="SpellFx"/>)</summary>
        public static Material Load(ref Material slot, string name, bool additive)
        {
            if (slot != null) return slot;
            slot = Resources.Load<Material>("FX/" + name);
            if (slot == null) slot = Fallback(name, additive);
            return slot;
        }

        /// <summary>URP Particles/Unlit (additive or alpha blended, no depth write, two-sided) on a soft round blob;
        /// Sprites/Default when the URP shader is missing (a build that stripped it); null when neither is there</summary>
        static Material Fallback(string name, bool additive)
        {
            if (blob == null) blob = Blob(64);
            var sh = Shader.Find("Universal Render Pipeline/Particles/Unlit");
            if (sh == null)
            {
                var sprites = Shader.Find("Sprites/Default");
                return sprites != null ? new Material(sprites) { name = name + " (stand-in)", mainTexture = blob } : null;
            }
            var m = new Material(sh) { name = name + " (stand-in)" };
            m.SetFloat("_Surface", 1f);                                       // transparent
            m.SetFloat("_Blend", additive ? 2f : 0f);
            m.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            m.SetFloat("_DstBlend", additive ? (float)BlendMode.One : (float)BlendMode.OneMinusSrcAlpha);
            m.SetFloat("_SrcBlendAlpha", (float)BlendMode.One);
            m.SetFloat("_DstBlendAlpha", additive ? (float)BlendMode.One : (float)BlendMode.OneMinusSrcAlpha);
            m.SetFloat("_ZWrite", 0f);
            m.SetFloat("_Cull", 0f);
            m.SetOverrideTag("RenderType", "Transparent");
            m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            m.SetShaderPassEnabled("DepthOnly", false);
            m.renderQueue = (int)RenderQueue.Transparent;
            m.SetTexture("_BaseMap", blob);
            m.mainTexture = blob;
            bool fire = name.Contains("Flame") || name.Contains("Glow") || name.Contains("Ember");
            m.SetColor("_BaseColor", name.Contains("Smoke") ? new Color(0.3f, 0.28f, 0.26f) : fire ? new Color(1f, 0.55f, 0.2f) : Color.white);
            return m;
        }

        /// <summary>white, alpha falling off from the centre: a soft round blob</summary>
        static Texture2D Blob(int n)
        {
            var t = new Texture2D(n, n, TextureFormat.RGBA32, true) { name = "FireBlob", wrapMode = TextureWrapMode.Clamp };
            var px = new Color32[n * n];
            for (int y = 0; y < n; y++)
                for (int x = 0; x < n; x++)
                {
                    float dx = (x + 0.5f) / n * 2f - 1f, dy = (y + 0.5f) / n * 2f - 1f;
                    float a = Mathf.Pow(Mathf.Clamp01(1f - Mathf.Sqrt(dx * dx + dy * dy)), 1.8f);
                    px[y * n + x] = new Color32(255, 255, 255, (byte)(a * 255f));
                }
            t.SetPixels32(px);
            t.Apply(true);
            return t;
        }
    }

    /// <summary>a fire run ahead again each time it is switched back on (<see cref="FireFx.KeepWarm"/>)</summary>
    [AddComponentMenu("")]
    public class FireWarm : MonoBehaviour
    {
        internal float seconds = 3f;
        bool seen;

        void OnEnable()
        {
            if (seen) FireFx.Warm(gameObject, seconds);
            seen = true;
        }
    }
}
