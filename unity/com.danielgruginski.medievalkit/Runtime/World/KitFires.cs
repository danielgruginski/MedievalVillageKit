using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// The kit's fires burning: its torches, braziers, hearths, fireplaces, fire pits and the goblins' bonfire (pieces with
    /// a glowing flame mesh, an <c>M_VKI_GlowIn</c> submesh) get small steady flames at that mesh (<see cref="Fire.Steady"/>),
    /// the mesh turned to coals (or hidden: a brazier's and the bonfire's cones stand up through the flames like
    /// crystals), and the kit's light beside it flickering (<see cref="FireFlicker"/>; none within 3 m: a light of its
    /// own). Call <see cref="Light"/> for each piece of a level as it loads (the game skips its own campfires first).
    /// From the Guild RPG's LevelDirector (FULL_PORT_PLAN phase 3a).
    /// </summary>
    public static class KitFires
    {
        /// <summary>the kit's fires, matched in a piece's name: the flames' scale (a torch's 0.18), sparks, smoke
        /// (outdoors), and whether its flame mesh stays, as coals</summary>
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

        /// <summary>the fires' lights under these roots (switched off ones too)</summary>
        public static List<Light> FireLights(IEnumerable<GameObject> roots) =>
            roots.SelectMany(g => g.GetComponentsInChildren<Light>(true))
                 .Where(l => l.name.StartsWith("LIT_", StringComparison.Ordinal) &&
                             LightWords.Any(w => l.name.IndexOf(w, StringComparison.OrdinalIgnoreCase) >= 0)).ToList();

        /// <summary>one piece: if it is a kit fire (not a burnt one, not within 1.5 m of one of <paramref name="notNear"/>:
        /// fires of the game's own on the spot), its flames lit and the nearest of <paramref name="lights"/> flickering.
        /// -> whether it was lit</summary>
        public static bool Light(KitPiece p, IList<Light> lights, IList<Vector3> notNear = null)
        {
            string piece = p.Get("vki_piece") ?? p.name;
            var kind = Kinds.FirstOrDefault(k => piece.IndexOf(k.match, StringComparison.Ordinal) >= 0);
            if (kind.match == null || piece.EndsWith("_Burnt", StringComparison.Ordinal)) return false;
            var at0 = p.transform.position;
            if (notNear != null && notNear.Any(c => new Vector2(c.x - at0.x, c.z - at0.z).sqrMagnitude < 2.25f)) return false;
            if (!FlameMesh(p, out var b)) return false;
            var at = new Vector3(b.center.x, b.min.y + Mathf.Min(0.15f * b.size.y, 0.2f), b.center.z);   // at the foot of it
            float scale = kind.scale * Mathf.Clamp(p.transform.lossyScale.y, 0.5f, 3f);
            var fire = Fire.Steady(p.transform, at, new Vector2(b.size.x, b.size.z) * 0.6f, scale, kind.sparks, kind.smoke);
            FireFx.Coals(p.gameObject, !kind.coals);
            var world = p.transform.TransformPoint(at);
            Light near = null;
            float best = 9f;                                            // within 3 m (one flickering already for a fire
            foreach (var l in lights)                                   // beside it too: two torches, one light)
            {
                if (l == null) continue;
                float d = (l.transform.position - world).sqrMagnitude;
                if (d < best) { best = d; near = l; }
            }
            if (near == null)
            {
                FireFx.Lamp(fire.transform, at + Vector3.up * (0.3f + scale), 1.5f + 3f * scale, 4f + 8f * scale);
                return true;
            }
            if (near.TryGetComponent<FireFlicker>(out _)) return true;
            var f = near.gameObject.AddComponent<FireFlicker>();
            f.tint = false;                                             // the kit's colour kept; the bigger the light (a
            f.depth = near.range > 20f ? 0.4f : 0.7f;                   // hearth's lights the room), the less it wavers
            return true;
        }

        /// <summary>a kit piece's glowing flame mesh (its M_VKI_GlowIn part), as a box in the piece's space</summary>
        public static bool FlameMesh(KitPiece p, out Bounds b)
        {
            b = default;
            bool found = false;
            foreach (var r in p.GetComponentsInChildren<MeshRenderer>(true))
            {
                var mesh = r.TryGetComponent<MeshFilter>(out var mf) ? mf.sharedMesh : null;
                if (mesh == null || r.GetComponentInParent<KitPiece>(true) != p) continue;     // not a piece inside it
                var mats = r.sharedMaterials;
                for (int i = 0; i < mats.Length && i < mesh.subMeshCount; i++)
                {
                    if (mats[i] == null || !mats[i].name.StartsWith("M_VKI_GlowIn", StringComparison.Ordinal)) continue;
                    var sb = mesh.GetSubMesh(i).bounds;                     // (known without reading the mesh)
                    for (int c = 0; c < 8; c++)
                    {
                        var corner = sb.center + Vector3.Scale(sb.extents, new Vector3((c & 1) == 0 ? -1 : 1, (c & 2) == 0 ? -1 : 1, (c & 4) == 0 ? -1 : 1));
                        var q = p.transform.InverseTransformPoint(r.transform.TransformPoint(corner));
                        if (!found) { b = new Bounds(q, Vector3.zero); found = true; }
                        else b.Encapsulate(q);
                    }
                }
            }
            return found;
        }
    }
}
