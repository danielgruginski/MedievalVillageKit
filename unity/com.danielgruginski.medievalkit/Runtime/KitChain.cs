using System;
using System.Collections.Generic;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// A chain of maps for a continuous world (generated, or hand-made plans): the maps listed in order, each joined to an earlier one (the one
    /// before, or any other: branches) through a connector (<see cref="KitConnectorGenerator"/>) between that map's
    /// portal and its own in portal (see <see cref="KitPortal"/>). Every portal leads somewhere: each is used by exactly
    /// one join. A tree, not a loop (a branch never rejoins). Tools > Medieval Kit > Chains > Bake builds every piece,
    /// lines them up in world space (maps are never turned), checks they do not overlap and saves each piece as a scene;
    /// <see cref="KitChainStreamer"/> then loads the pieces next to the walker and unloads the rest, so one walks from
    /// map to map without a cut. A scene link into the chain (a stair down into a cellar) targets the play scene Bake
    /// writes, with the arrival spawn's id: the streamer starts at the piece holding that spawn.
    /// </summary>
    [CreateAssetMenu(menuName = "Medieval Kit/Chain", fileName = "KitChain")]
    public class KitChain : ScriptableObject
    {
        public enum Kind { Cave, Dungeon, Plan }

        [Serializable]
        public class Map
        {
            public string id = "map";
            public Kind kind = Kind.Cave;
            [Tooltip("Its portals are in the generator's settings (Portals): one for the way in, one for the way on.")]
            public KitCaveGenerator.Options cave = new KitCaveGenerator.Options();
            public KitDungeonGenerator.Options dungeon = new KitDungeonGenerator.Options();
            [Tooltip("Plan: a hand-made map's plan file (<name>.plan.txt, typed as for KitRoom); else the text below.")]
            public TextAsset planFile;
            [Tooltip("Plan: its room record file (<name>.record.json; a cave map: \"cave\": true); its \"portals\" are the map's openings, each with its `at` set.")]
            public TextAsset recordFile;
            [TextArea(6, 30)] public string plan;
            [TextArea(6, 30)] public string record;

            public string PlanText => planFile != null ? planFile.text : plan;
            public string RecordText => recordFile != null ? recordFile.text : record;
            [Tooltip("Its portal the earlier map's connector reaches (empty for the first map).")]
            public string inPortal = "south";
            [Tooltip("The map it joins (empty: the one before it in the list).")]
            public string attachTo = "";
            [Tooltip("The portal of that map it joins through (empty: that map's Out Portal).")]
            public string attachPortal = "";
            [Tooltip("The portal a later map joins by default (empty if none does).")]
            public string outPortal = "north";
            [Tooltip("The connector from the map it joins: its length, seed and style (its edges follow the two portals).")]
            public KitConnectorGenerator.Options connector = new KitConnectorGenerator.Options();

            /// <summary>the map's portals: its generator's, or a plan's record's</summary>
            public List<KitPortal> Portals()
            {
                if (kind == Kind.Cave) return cave.portals ?? new List<KitPortal>();
                if (kind == Kind.Dungeon) return dungeon.portals ?? new List<KitPortal>();
                try { return KitPortal.Of(Newtonsoft.Json.Linq.JObject.Parse(string.IsNullOrWhiteSpace(RecordText) ? "{}" : RecordText)); }
                catch (Exception) { return new List<KitPortal>(); }
            }
        }

        /// <summary>a baked piece: a map or a connector, its scene and where it lies in the world</summary>
        [Serializable]
        public class Piece
        {
            public string id;
            public string scene;            // the scene's asset path
            public Vector3 position;
            public Rect footprint;          // world x / z
            public List<string> neighbours = new List<string>();
            public List<string> spawns = new List<string>();     // its KitSpawn ids (where scene links into the chain arrive)
        }

        public List<Map> maps = new List<Map>();
        [Tooltip("Filled by Bake: every piece in order (map, connector, map, ...).")]
        public List<Piece> pieces = new List<Piece>();

        public Piece Find(string id) => pieces.Find(p => p.id == id);

        /// <summary>the piece holding a spawn, or null</summary>
        public Piece WithSpawn(string spawnId) => pieces.Find(p => p.spawns.Contains(spawnId));

        /// <summary>the piece whose footprint holds a world point (x / z), or null</summary>
        public Piece At(Vector3 p) => pieces.Find(q => q.footprint.Contains(new Vector2(p.x, p.z)));

        /// <summary>pieces within `steps` joins of a piece (it included)</summary>
        public HashSet<string> Around(string id, int steps)
        {
            var seen = new HashSet<string> { id };
            var front = new List<string> { id };
            for (int s = 0; s < steps; s++)
            {
                var next = new List<string>();
                foreach (var f in front)
                    foreach (var n in Find(f)?.neighbours ?? new List<string>())
                        if (seen.Add(n)) next.Add(n);
                front = next;
            }
            return seen;
        }
    }
}
