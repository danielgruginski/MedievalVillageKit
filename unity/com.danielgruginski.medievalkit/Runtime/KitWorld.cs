using System;
using System.Collections.Generic;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// The world graph (docs/WORLD_GRAPH.md): every level, its links and where each link arrives. A level is a scene
    /// of the same name. Generated from Data/world.json by KitBuilder; hand-made levels can be added to it.
    /// Targets "@return" (back to where the walker came in) and "@deep" (an open end) are holes, not levels.
    /// </summary>
    [CreateAssetMenu(menuName = "Medieval Kit/World Graph", fileName = "KitWorld")]
    public class KitWorld : ScriptableObject
    {
        [Serializable]
        public class Link
        {
            public string id;
            public string kind;     // exit, passage, stair_up, stair_down, lift
            public string target;   // a level name, "@return" or "@deep"
            public string arrive;   // the link id it lands at in the target (empty: the target's link back here)
        }

        [Serializable]
        public class Level
        {
            public string name;     // = scene name
            public string kind;
            public List<Link> links = new List<Link>();
        }

        public string start;
        public List<Level> levels = new List<Level>();

        public Level Find(string name) => levels.Find(l => l.name == name);

        /// <summary>The link in `target` a walker lands at when coming from `from` through link `via`.</summary>
        public string ArrivalFor(string from, string via, string target)
        {
            var src = Find(from)?.links.Find(l => l.id == via);
            if (src != null && !string.IsNullOrEmpty(src.arrive)) return src.arrive;
            var t = Find(target);
            if (t == null) return null;
            var back = t.links.FindAll(l => l.target == from);
            if (back.Count == 1) return back[0].id;                         // the arrival rule: exactly one link back
            var ret = t.links.FindAll(l => l.target == "@return");
            return back.Count == 0 && ret.Count == 1 ? ret[0].id : null;    // into a building: its door (@return)
        }
    }
}
