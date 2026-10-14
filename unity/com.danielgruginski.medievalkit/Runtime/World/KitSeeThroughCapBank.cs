using System.Collections.Generic;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// The see-through's caps, baked (2026-10-14, see-through spike round 3; <see cref="KitSeeThroughCaps"/>): a player
    /// build cannot read the kit's meshes, so each cap mesh is made in the editor -- Tools > Medieval Kit > Bake See-through
    /// Caps, and before every player build -- for every piece, cut and set of solid materials the build's levels
    /// (KitVillage) use, and kept here as sub-assets. Loaded from Resources (<see cref="ResourceName"/>). An entry whose
    /// source mesh changed since the bake (re-exported: another vertex count or bounds) is ignored until the next bake; in
    /// the editor the missing cap is made again in play.
    /// </summary>
    public sealed class KitSeeThroughCapBank : ScriptableObject
    {
        public const string ResourceName = "KitSeeThroughCaps";

        [System.Serializable]
        public class Entry
        {
            public Mesh source;
            [Tooltip("The cut, in KitSeeThroughCaps.Step over the source's origin (its own units).")]
            public int q;
            [Tooltip("The source's solid and bark submeshes (bits).")]
            public uint solid, bark;
            [Tooltip("The cap (none: the section filled nothing).")]
            public Mesh cap;
            [Tooltip("Each cap submesh's source submesh, and whether it takes the end grain.")]
            public int[] mats;
            public bool[] grain;
            [Tooltip("The cap's area (the source's units).")]
            public float area;
            [Tooltip("The source as baked: a re-exported mesh no longer matches.")]
            public int vertexCount;
            public Bounds bounds;
        }

        public List<Entry> entries = new List<Entry>();
        [Tooltip("Materials a cap or a floor may need that a level does not use (the end grain, the planks).")]
        public List<Material> materials = new List<Material>();
        [TextArea(2, 6)] public string report;
    }
}
