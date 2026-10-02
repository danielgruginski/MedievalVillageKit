using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// What <see cref="KitRoom"/> builds rooms from: Data/interior_rules.json (vkx_export_interior_rules: the grid,
    /// families, plan tokens, style slots and materials, and every Blender room record and plan as presets), the
    /// interior piece prefabs by name and the style materials by name. Tools > Medieval Kit > Build Interior Rules
    /// regenerates it; copy it to customise.
    /// </summary>
    [CreateAssetMenu(menuName = "Medieval Kit/Interior Rules", fileName = "KitInteriorRules")]
    public class KitInteriorRules : ScriptableObject
    {
        [Serializable] public struct PieceRef { public string name; public GameObject prefab; }
        [Serializable] public struct MatRef { public string name; public Material material; }

        public TextAsset rulesJson;
        public List<PieceRef> pieces = new List<PieceRef>();
        public List<MatRef> materials = new List<MatRef>();

        [NonSerialized] JObject json;
        [NonSerialized] Dictionary<string, GameObject> pieceMap;
        [NonSerialized] Dictionary<string, Material> matMap;

        void OnEnable() { json = null; pieceMap = null; matMap = null; }
        void OnValidate() { json = null; pieceMap = null; matMap = null; }

        public JObject Json => json ??= JObject.Parse(rulesJson != null ? rulesJson.text : "{}");

        public IEnumerable<string> RoomNames => (Json["rooms"] as JObject)?.Properties().Select(p => p.Name) ?? Enumerable.Empty<string>();
        /// <summary>a kit room's record (a copy), its zones back in their listed order (the first listed wins where
        /// zones overlap; the export sorts keys and keeps the order in "zone_order")</summary>
        public JObject Room(string name)
        {
            if (!(Json["rooms"]?[name] is JObject src)) return null;
            var r = (JObject)src.DeepClone();
            if (r["zone_order"] is JArray order && r["zones"] is JObject zones)
            {
                var z = new JObject();
                foreach (var n in order) if (zones[(string)n] != null) z[(string)n] = zones[(string)n];
                foreach (var p in zones.Properties()) if (z[p.Name] == null) z[p.Name] = p.Value;
                r["zones"] = z;
            }
            r.Remove("zone_order");
            return r;
        }
        public string Plan(string name) => (string)Json["plans"]?[name];

        public GameObject Prefab(string name)
        {
            if (pieceMap == null)
            {
                pieceMap = new Dictionary<string, GameObject>();
                foreach (var p in pieces) if (p.prefab != null) pieceMap[p.name] = p.prefab;
            }
            return name != null && pieceMap.TryGetValue(name, out var g) ? g : null;
        }

        public Material Mat(string name)
        {
            if (matMap == null)
            {
                matMap = new Dictionary<string, Material>();
                foreach (var m in materials) if (m.material != null) matMap[m.name] = m.material;
            }
            return name != null && matMap.TryGetValue(name, out var mt) ? mt : null;
        }

        /// <summary>vki_style_mat: a style key + value (e.g. wall_a = PlasterCream) -> its material name;
        /// values may also be material names ("M_...").</summary>
        public string StyleMatName(string key, string value)
        {
            if (value == null) return null;
            if (value.StartsWith("M_")) return value;
            return (string)Json["styles"]?[key]?[value];
        }

        /// <summary>vki_rooms_put's piece names: "Torch_Wall" -> "SM_VKI_Torch_Wall", full names unchanged.</summary>
        public static string Full(string piece) => piece.StartsWith("SM_") ? piece : "SM_VKI_" + piece;
    }
}
