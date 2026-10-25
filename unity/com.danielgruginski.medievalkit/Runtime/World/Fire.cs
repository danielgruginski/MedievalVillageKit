using System.Collections.Generic;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// Fire on a thing in the world, made of <see cref="FireFx"/>'s parts: <see cref="Blaze"/> -- flames on spots on its
    /// timbers, catching at the one nearest where it was lit and spreading one spot at a time, embers, a glow, a smoke
    /// column, a flickering light -- for a siege engine set alight; <see cref="Collapse"/> when it falls in;
    /// <see cref="Smoulder"/> for what is left once it has burned down; <see cref="Burst"/> for a fire circle going off
    /// (the war-shaman's, a Fireball's); <see cref="Steady"/> for the kit's torches, braziers and hearths; <see cref="Splash"/>
    /// for a bolt of fire landing (<see cref="FireBolt"/>). Each goes under the parent it is given, so it leaves with its level.
    /// </summary>
    public static class Fire
    {
        /// <summary>the fires' sounds, played by the game (the kit has none): a loop on a transform, a one-shot at a
        /// point (id, where, volume, pitch); unset = silent</summary>
        public static System.Action<string, Transform, float, float> SoundLoop;
        public static System.Action<string, Vector3, float, float> SoundAt;

        /// <summary>seconds between one spot catching and the next (the siege tower's 18: alight all over in about 6 s)</summary>
        public const float SpreadSeconds = 0.35f;

        /// <summary>a fire on a thing (<paramref name="local"/>: its box in the parent's space), flames on the
        /// <paramref name="spots"/> (the parent's space, on its timbers; none: round its footprint) at
        /// <paramref name="scale"/> (1: the siege tower's); lit from <paramref name="from"/> (a world point) it catches at
        /// the spot nearest it and spreads, else it is alight all over at once</summary>
        public static GameObject Blaze(Transform parent, Bounds local, IList<Vector3> spots = null, float scale = 1f, Vector3? from = null)
        {
            var go = new GameObject("Fire");
            go.transform.SetParent(parent, false);                      // at the parent's origin: the spots are in its space
            var list = new List<Vector3>(spots != null && spots.Count > 0 ? spots : Footprint(local));
            if (from.HasValue)
            {
                var f = parent.InverseTransformPoint(from.Value);
                list.Sort((a, b) => (a - f).sqrMagnitude.CompareTo((b - f).sqrMagnitude));
            }
            go.AddComponent<Blazing>().Init(list, scale > 0f ? scale : 1f, local, from.HasValue ? 1 : list.Count);
            FireFx.KeepWarm(go, 3f);
            SoundLoop?.Invoke("blaze_loop", go.transform, Mathf.Clamp(scale, 0.6f, 1.4f), 1f);
            return go;
        }

        /// <summary>a blaze falling in: a gust of sparks and big puffs of smoke, its flames going out over the first half of
        /// <paramref name="seconds"/> (the highest first: the wreck is low), then it is gone; any other fire dies down
        /// (<see cref="Douse"/>)</summary>
        public static void Collapse(GameObject fire, float seconds = 6f)
        {
            if (fire == null) return;
            if (!fire.TryGetComponent<Blazing>(out var b)) { Douse(fire, seconds); return; }
            b.Collapse(seconds * 0.5f);
            SoundAt?.Invoke("earth", fire.transform.position, 0.9f, 0.7f);
            Object.Destroy(fire, seconds);
        }

        /// <summary>a fire dying down: its particles stop coming (the last ones live out their time), its light fades,
        /// then it is gone</summary>
        public static void Douse(GameObject fire, float seconds = 5f)
        {
            if (fire == null) return;
            if (fire.TryGetComponent<Blazing>(out var b)) b.enabled = false;           // no more spots catching
            foreach (var ps in fire.GetComponentsInChildren<ParticleSystem>()) ps.Stop(true, ParticleSystemStopBehavior.StopEmitting);
            foreach (var f in fire.GetComponentsInChildren<FireFlicker>()) f.FadeOut(seconds * 0.6f);
            Object.Destroy(fire, seconds);
        }

        /// <summary>what is left of a fire: pale smoke rising from the ash, a few embers, flames dying down over the first half
        /// minute (on the three lowest of its <paramref name="spots"/>: the timbers left standing; none: in the ash) and a
        /// light dying with them; the smoke thins over two minutes to a wisp that stays.
        /// <paramref name="age"/>: seconds it has smouldered already (a level come back: 120, only the wisp)</summary>
        public static GameObject Smoulder(Transform parent, Bounds local, float age = 0f, IList<Vector3> spots = null)
        {
            var go = new GameObject("Smoulder");
            go.transform.SetParent(parent, false);
            go.AddComponent<Smouldering>().Init(local, age, spots);
            return go;
        }

        /// <summary>a ring of fire going off on the ground (a fire circle): flames shooting up round its edge and a few
        /// inside, in two waves, a flash on the ground, sparks falling back and a puff of pale smoke (dark is lost on the
        /// burnt ground); gone in a few seconds</summary>
        public static void Burst(Vector3 at, float radius)
        {
            var go = new GameObject("FireBurst");
            go.transform.position = at;
            SoundAt?.Invoke("fire_spray", at, 0.8f, 1f);
            float r = Mathf.Max(0.5f, radius);
            Shoot(go.transform, "Ring", r, 0f, Mathf.Clamp(Mathf.RoundToInt(r * 2f * Mathf.PI * 2.2f), 8, 60),
                  new Vector2(0.9f, 1.5f), new Vector2(1.5f, 3f), new Vector2(0.9f, 1.4f));
            Shoot(go.transform, "Inside", r * 0.85f, 1f, Mathf.Clamp(Mathf.RoundToInt(3f * r * r), 3, 40),
                  new Vector2(0.5f, 0.9f), new Vector2(1f, 2f), new Vector2(0.6f, 1f));
            // the flash, flat on the ground (high enough that the soft particles do not fade it out); the plain glow: the
            // hot one comes out lime on dark ground through the tonemapper
            var glow = FireFx.GlowMaterial;
            if (glow != null)
                FireFx.Particles("Flash", go.transform, new Vector3(0f, 0.35f, 0f), glow, (ps, rend) =>
                {
                    FireFx.OneShot(ps, 1, 0f);
                    var main = ps.main;
                    main.startLifetime = 0.6f; main.startSpeed = 0f; main.startSize = 2.5f * r;
                    main.startColor = new Color(1f, 0.42f, 0.1f);
                    var sh = ps.shape;
                    sh.enabled = false;
                    var col = ps.colorOverLifetime;
                    col.enabled = true;
                    col.color = FireFx.Grad(new[] { Color.white, Color.white }, new[] { 0f, 1f }, new[] { 1f, 0.7f, 0f }, new[] { 0f, 0.25f, 1f });
                    var size = ps.sizeOverLifetime;
                    size.enabled = true; size.size = new ParticleSystem.MinMaxCurve(1f, FireFx.Curve(0f, 0.7f, 1f, 1f));
                    rend.renderMode = ParticleSystemRenderMode.HorizontalBillboard;
                    rend.sortingFudge = -5f;
                });
            var ember = FireFx.EmberMaterial;
            if (ember != null)
                FireFx.Particles("Sparks", go.transform, Vector3.zero, ember, (ps, rend) =>
                {
                    FireFx.OneShot(ps, 30, 0f);
                    var main = ps.main;
                    main.startLifetime = new ParticleSystem.MinMaxCurve(0.9f, 1.5f);
                    main.startSpeed = new ParticleSystem.MinMaxCurve(2.5f, 4.5f);
                    main.startSize = new ParticleSystem.MinMaxCurve(0.04f, 0.08f);
                    main.gravityModifier = 0.5f;                            // falling back
                    var sh = ps.shape;
                    sh.enabled = true; sh.shapeType = ParticleSystemShapeType.Cone; sh.angle = 35f; sh.radius = r * 0.8f;
                    sh.rotation = new Vector3(-90f, 0f, 0f);                // the cone points up
                    FireFx.EmberLook(ps, rend);
                });
            var smoke = FireFx.SmokeMaterial;
            if (smoke != null)
                FireFx.Particles("Smoke", go.transform, Vector3.zero, smoke, (ps, rend) =>
                {
                    FireFx.OneShot(ps, 10, 0.12f);
                    var main = ps.main;
                    main.startLifetime = new ParticleSystem.MinMaxCurve(2f, 3f);
                    main.startSpeed = 0f;
                    main.startSize = new ParticleSystem.MinMaxCurve(1.4f, 2.2f);
                    var sh = ps.shape;
                    sh.enabled = true; sh.shapeType = ParticleSystemShapeType.Circle; sh.radius = r * 0.8f; sh.radiusThickness = 1f;
                    sh.rotation = new Vector3(-90f, 0f, 0f);                // flat on the ground
                    FireFx.Rise(ps, 0.6f, 1.2f);
                    FireFx.SmokeLook(ps, rend, smoke, 0.8f, true);
                });
            Object.Destroy(go, 3.5f);
        }

        /// <summary>a small fire that stays where it is (the kit's torches, braziers, hearths and fire pits, the goblins'
        /// bonfire): flames licking up off a patch <paramref name="patch"/> wide (x, z) at <paramref name="at"/> (the
        /// parent's space) at <paramref name="scale"/> (a torch's 0.18, a bonfire's 0.9), a few sparks off the bigger ones
        /// and a thin pale smoke outdoors; the flames and sparks kept <see cref="FireFx.Still"/>, so the ones off screen
        /// cost nothing; already burning when it is first seen</summary>
        public static GameObject Steady(Transform parent, Vector3 at, Vector2 patch, float scale, bool sparks, bool smoke)
        {
            var go = new GameObject("Fire");
            go.transform.SetParent(parent, false);
            float rate = (5f + 12f * scale) * Mathf.Max(1f, Mathf.Max(patch.x, patch.y) / 0.4f);   // a hearth's long bed: more
            var src = FireFx.Source.Box(at, new Vector3(Mathf.Max(0.04f, patch.x), 0.02f, Mathf.Max(0.04f, patch.y)));
            FireFx.Still(FireFx.Flames(go.transform, src, scale, rate, Mathf.CeilToInt(rate * 1.3f) + 2));
            FireFx.Still(FireFx.Flames(go.transform, src, scale, rate * 0.5f, Mathf.CeilToInt(rate * 0.7f) + 2, true));
            if (sparks)
                FireFx.Still(FireFx.Embers(go.transform, FireFx.Source.Box(at + Vector3.up * 0.1f, new Vector3(patch.x, 0.05f, patch.y)),
                                           1f + 2.5f * scale, 0.35f + 0.5f * scale, Mathf.RoundToInt(6f * scale), 16));
            if (smoke)                                                  // the breeze is the world's: not still
                FireFx.Smoke(go.transform, FireFx.Source.Box(at + Vector3.up * (0.5f + 1.4f * scale), new Vector3(0.2f, 0.1f, 0.2f) * (0.5f + scale)),
                             1f + 1.5f * scale, 0.4f + 0.7f * scale, 0.7f + 1.4f * scale, 0.22f, 3.5f, 0.8f, true, 14);
            FireFx.Warm(go, 3f);
            FireFx.KeepWarm(go, 3f);
            SoundLoop?.Invoke("fire_loop", go.transform, Mathf.Clamp(scale * 2.2f, 0.35f, 1.5f), Mathf.Lerp(1.15f, 0.8f, Mathf.Clamp01(scale)));
            return go;
        }

        /// <summary>a bolt of fire bursting where it lands: a puff of flames, a spray of sparks, a flash and a moment of
        /// light; <paramref name="size"/> 1 a Firebolt's</summary>
        public static void Splash(Vector3 at, float size = 1f)
        {
            var go = new GameObject("FireSplash");
            go.transform.position = at;
            SoundAt?.Invoke("spell_hit", at, 0.8f, 0.75f);
            var body = FireFx.BodyMaterial;
            if (body != null)
                FireFx.Particles("Flames", go.transform, Vector3.zero, body, (ps, rend) =>
                {
                    FireFx.OneShot(ps, 8, 0f);
                    var main = ps.main;
                    main.startLifetime = new ParticleSystem.MinMaxCurve(0.35f, 0.6f);
                    main.startSpeed = new ParticleSystem.MinMaxCurve(0.4f * size, 1.4f * size);
                    main.startSize = new ParticleSystem.MinMaxCurve(0.45f * size, 0.75f * size);
                    main.startRotation = new ParticleSystem.MinMaxCurve(-0.12f, 0.12f);
                    var sh = ps.shape;
                    sh.enabled = true; sh.shapeType = ParticleSystemShapeType.Sphere; sh.radius = 0.15f * size;
                    FireFx.Rise(ps, 0.6f, 1.2f);
                    FireFx.FlameLook(ps, rend, body, false);
                });
            var ember = FireFx.EmberMaterial;
            if (ember != null)
                FireFx.Particles("Sparks", go.transform, Vector3.zero, ember, (ps, rend) =>
                {
                    FireFx.OneShot(ps, 12, 0f);
                    var main = ps.main;
                    main.startLifetime = new ParticleSystem.MinMaxCurve(0.5f, 1f);
                    main.startSpeed = new ParticleSystem.MinMaxCurve(2f * size, 4f * size);
                    main.startSize = new ParticleSystem.MinMaxCurve(0.04f, 0.07f);
                    main.gravityModifier = 0.5f;
                    var sh = ps.shape;
                    sh.enabled = true; sh.shapeType = ParticleSystemShapeType.Sphere; sh.radius = 0.1f * size;
                    FireFx.EmberLook(ps, rend);
                });
            var glow = FireFx.GlowMaterial;
            if (glow != null)
                FireFx.Particles("Flash", go.transform, Vector3.zero, glow, (ps, rend) =>
                {
                    FireFx.OneShot(ps, 1, 0f);
                    var main = ps.main;
                    main.startLifetime = 0.3f; main.startSpeed = 0f; main.startSize = 1.6f * size;
                    main.startColor = new Color(1f, 0.45f, 0.12f);
                    var sh = ps.shape;
                    sh.enabled = false;
                    var col = ps.colorOverLifetime;
                    col.enabled = true;
                    col.color = FireFx.Grad(new[] { Color.white, Color.white }, new[] { 0f, 1f }, new[] { 0.8f, 0f }, new[] { 0f, 1f });
                    rend.sortingFudge = -5f;
                });
            FireFx.Lamp(go.transform, Vector3.zero, 4f * size, 5f * size).FadeOut(0.4f);
            Object.Destroy(go, 1.5f);
        }

        /// <summary>flames bursting up off a circle on the ground (thickness 0: its edge, 1: all of it)</summary>
        static void Shoot(Transform parent, string name, float radius, float thickness, int count, Vector2 size, Vector2 rise, Vector2 life)
        {
            var mat = FireFx.BodyMaterial;
            if (mat == null) return;
            FireFx.Particles(name, parent, Vector3.zero, mat, (ps, rend) =>
            {
                FireFx.OneShot(ps, count, 0f, count / 2);                   // a second, smaller wave: it keeps burning a moment
                var main = ps.main;
                main.startLifetime = new ParticleSystem.MinMaxCurve(life.x, life.y);
                main.startSpeed = 0f;
                main.startSize = new ParticleSystem.MinMaxCurve(size.x, size.y);
                main.startRotation = new ParticleSystem.MinMaxCurve(-0.12f, 0.12f);
                var sh = ps.shape;
                sh.enabled = true; sh.shapeType = ParticleSystemShapeType.Circle; sh.radius = radius; sh.radiusThickness = thickness;
                sh.rotation = new Vector3(-90f, 0f, 0f);                    // flat on the ground
                FireFx.Rise(ps, rise.x, rise.y);
                FireFx.FlameLook(ps, rend, mat, false);
            });
        }

        /// <summary>spots round a footprint (when a thing has none of its own): its corners and the middles of its sides, a
        /// little in, low, a third and two thirds of the way up, and two near the top</summary>
        static List<Vector3> Footprint(Bounds b)
        {
            var list = new List<Vector3>();
            float ex = b.extents.x * 0.85f, ez = b.extents.z * 0.85f, h = b.size.y;
            foreach (float y in new[] { 0.08f, 0.38f, 0.65f })
                for (int i = 0; i < 8; i++)
                {
                    float a = i * Mathf.PI * 0.25f;                     // round to the corners and the sides' middles
                    list.Add(new Vector3(b.center.x + Mathf.Round(Mathf.Cos(a)) * ex, b.min.y + y * h, b.center.z + Mathf.Round(Mathf.Sin(a)) * ez));
                }
            list.Add(new Vector3(b.center.x - ex * 0.4f, b.min.y + 0.9f * h, b.center.z + ez * 0.3f));
            list.Add(new Vector3(b.center.x + ex * 0.4f, b.min.y + 0.9f * h, b.center.z - ez * 0.3f));
            return list;
        }
    }

    /// <summary>a blaze catching spot by spot (<see cref="Fire.Blaze"/>, the spots nearest first): the flames, the glow
    /// and the embers come from the spots alight; the smoke, the glow, the embers and the light grow with them; falling
    /// in, they go out spot by spot, the highest first</summary>
    [AddComponentMenu("")]
    public class Blazing : MonoBehaviour
    {
        List<Vector3> spots;
        float scale, next, fadeFrom, fadeFor;
        int lit, litAtFall;
        Bounds local;
        Mesh mesh;
        ParticleSystem body, core, glow, embers, smoke;
        FireFlicker lamp;

        internal void Init(List<Vector3> spots, float scale, Bounds local, int lit)
        {
            this.spots = spots; this.scale = scale; this.local = local;
            float sx = local.size.x, sz = local.size.z, h = local.size.y;
            var c = local.center;
            int n = spots.Count;
            mesh = FireFx.SpotMesh(spots, 1);
            body = FireFx.Flames(transform, FireFx.Source.Spots(mesh, 0.4f * scale), scale, 0f, 12 * n);
            core = FireFx.Flames(transform, FireFx.Source.Spots(mesh, 0.25f * scale), scale, 0f, 6 * n, true);
            glow = FireFx.Glow(transform, FireFx.Source.Spots(mesh, 0.5f * scale), 3f * scale, 0f, 0.12f);   // faint: the light warms the ground
            embers = FireFx.Embers(transform, FireFx.Source.Spots(mesh, 0.5f * scale), 0f, 1f, 10, 100);
            smoke = FireFx.Smoke(transform, FireFx.Source.Box(new Vector3(c.x, local.min.y + 0.6f * h, c.z), new Vector3(0.56f * sx, 0.3f * h, 0.56f * sz)),
                                 0f, 2.6f * scale, 4f * scale, 0.8f, 5f, 1.4f, false);
            lamp = FireFx.Lamp(transform, new Vector3(c.x, local.min.y + 0.5f * h, c.z), 3.5f, Mathf.Clamp(1.8f * Mathf.Max(sx, sz), 6f, 12f));
            Set(lit);
            if (embers != null) embers.Emit(20);                         // the rags catching
            next = Time.time + Fire.SpreadSeconds;
        }

        void Update()
        {
            if (spots == null) return;
            if (fadeFor > 0f) { Dying(); return; }
            if (Time.time < next) return;
            if (lit >= spots.Count) { enabled = false; return; }
            next = Time.time + Fire.SpreadSeconds;
            Set(lit + 1);
        }

        /// <summary>the first n spots alight</summary>
        void Set(int n)
        {
            lit = Mathf.Clamp(n, 1, spots.Count);
            var old = mesh;
            mesh = FireFx.SpotMesh(spots, lit);
            foreach (var ps in new[] { body, core, glow, embers })
                if (ps != null) { var sh = ps.shape; sh.mesh = mesh; }
            if (old != null && old != mesh) Destroy(old);
            float g = 0.3f + 0.7f * lit / spots.Count;                  // the rest grows from a third to full
            FireFx.Rate(body, 7f * lit);
            FireFx.Rate(core, 3.5f * lit);
            FireFx.Rate(glow, 3f * g);
            FireFx.Rate(embers, 10f * g);
            FireFx.Rate(smoke, 10f * g);
            if (lamp == null) return;
            lamp.level = g;
            var mid = Vector3.zero;                                     // the light over the spots alight
            for (int i = 0; i < lit; i++) mid += spots[i];
            lamp.Home = mid / lit + Vector3.up * 0.5f;
        }

        /// <summary>falling in: a gust of sparks and a dozen big puffs of smoke from all over it (its own column stops), the
        /// flames going out over <paramref name="fade"/> s, the highest first, the light fading with them</summary>
        internal void Collapse(float fade)
        {
            spots = spots.GetRange(0, lit);
            spots.Sort((a, b) => a.y.CompareTo(b.y));                     // the lowest alight longest
            litAtFall = lit;
            fadeFrom = Time.time; fadeFor = Mathf.Max(0.1f, fade);
            enabled = true;
            if (lamp != null) lamp.FadeOut(fade);
            if (embers != null) embers.Emit(40);
            if (smoke == null) return;
            for (int i = 0; i < 12; i++)
            {
                var p = new Vector3(Random.Range(local.min.x, local.max.x) * 0.7f + local.center.x * 0.3f,
                                    local.min.y + local.size.y * Random.Range(0.15f, 0.6f),
                                    Random.Range(local.min.z, local.max.z) * 0.7f + local.center.z * 0.3f);
                smoke.Emit(new ParticleSystem.EmitParams
                {
                    position = transform.TransformPoint(p), applyShapeToPosition = false,
                    velocity = new Vector3(0f, Random.Range(0.8f, 1.5f), 0f),
                    startSize = Random.Range(3f, 4.5f) * scale, startLifetime = Random.Range(4f, 5.5f),
                }, 1);
            }
            smoke.Stop(true, ParticleSystemStopBehavior.StopEmitting);
        }

        /// <summary>the spots alight dwindling with the time left, then nothing more coming (the last flames live out)</summary>
        void Dying()
        {
            float k = 1f - (Time.time - fadeFrom) / fadeFor;
            if (k > 0f)
            {
                int n = Mathf.CeilToInt(litAtFall * k);
                if (n != lit) Set(n);
                return;
            }
            foreach (var ps in GetComponentsInChildren<ParticleSystem>()) ps.Stop(true, ParticleSystemStopBehavior.StopEmitting);
            enabled = false;
        }

        void OnDestroy()
        {
            if (mesh != null) Destroy(mesh);
        }
    }

    /// <summary>a fire burned down (<see cref="Fire.Smoulder"/>): flames dying down and their light for the first half
    /// minute, pale smoke thinning over two minutes to a wisp that stays (with a few embers)</summary>
    [AddComponentMenu("")]
    public class Smouldering : MonoBehaviour
    {
        const float FlameSeconds = 30f, TaperSeconds = 120f, SmokeRate = 3f, Flame0 = 0.55f, Flame1 = 0.35f;

        ParticleSystem smoke, flames;
        Mesh mesh;
        float start;

        internal void Init(Bounds local, float age, IList<Vector3> given)
        {
            start = Time.time - age;
            var c = local.center;
            float sx = local.size.x, sz = local.size.z, y0 = local.min.y;
            smoke = FireFx.Smoke(transform, FireFx.Source.Box(new Vector3(c.x, y0 + 0.5f, c.z), new Vector3(0.5f * sx, 0.4f, 0.5f * sz)),
                                 SmokeRate, 1.5f, 2.5f, 0.65f, 7f, 0.9f, true, 80);
            FireFx.Embers(transform, FireFx.Source.Box(new Vector3(c.x, y0 + 0.2f, c.z), new Vector3(0.6f * sx, 0.2f, 0.6f * sz)), 1.5f, 0.5f, 0, 12);
            if (age < FlameSeconds)
            {
                var spots = new List<Vector3>();
                if (given != null && given.Count >= 3)
                {
                    spots.AddRange(given);                              // the lowest three: the base's timbers
                    spots.Sort((a, b) => a.y.CompareTo(b.y));
                }
                else
                {
                    spots.Add(new Vector3(c.x - 0.2f * sx, y0 + 0.15f, c.z - 0.15f * sz));      // three in the ash bed
                    spots.Add(new Vector3(c.x + 0.22f * sx, y0 + 0.2f, c.z + 0.1f * sz));
                    spots.Add(new Vector3(c.x + 0.02f * sx, y0 + 0.12f, c.z + 0.28f * sz));
                }
                mesh = FireFx.SpotMesh(spots, 3);
                flames = FireFx.Flames(transform, FireFx.Source.Spots(mesh, 0.14f), Flame0, 6f, 16);
                var lamp = FireFx.Lamp(transform, new Vector3(c.x, y0 + 1f, c.z), 1.2f, Mathf.Clamp(1.6f * Mathf.Max(sx, sz), 5f, 9f));
                lamp.FadeOut(FlameSeconds - age);
                Destroy(lamp.gameObject, FlameSeconds - age + 0.1f);
            }
            Update();                                                   // the rates for its age, then
            if (age > 0f) FireFx.Warm(gameObject, 6f);                    // smoking already when the level comes back
            FireFx.KeepWarm(gameObject, 6f);
        }

        void Update()
        {
            float t = Time.time - start;
            if (flames != null && t >= FlameSeconds)
            {
                flames.Stop(true, ParticleSystemStopBehavior.StopEmitting);
                Destroy(flames.gameObject, 1.5f);
                Destroy(mesh, 1.5f);
                flames = null; mesh = null;
            }
            if (flames != null) FireFx.FlameSize(flames, Mathf.Lerp(Flame0, Flame1, t / FlameSeconds));
            FireFx.Rate(smoke, SmokeRate * Mathf.Lerp(1f, 0.3f, t / TaperSeconds));
            if (t >= TaperSeconds && flames == null) enabled = false;    // the wisp stays as it is
        }

        void OnDestroy()
        {
            if (mesh != null) Destroy(mesh);
        }
    }
}
