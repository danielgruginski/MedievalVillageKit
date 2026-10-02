using System;
using System.Collections.Generic;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>A Blender custom property, kept as text (JSON values stay JSON strings).</summary>
    [Serializable]
    public struct KitProp
    {
        public string key;
        public string value;
    }

    /// <summary>Base for anything carrying the kit's custom properties (vki_* and friends).</summary>
    public abstract class KitPropsBehaviour : MonoBehaviour
    {
        public List<KitProp> props = new List<KitProp>();

        public string Get(string key, string fallback = null)
        {
            foreach (var p in props) if (p.key == key) return p.value;
            return fallback;
        }

        public bool Has(string key) => Get(key) != null;

        public void Set(string key, string value)
        {
            int i = props.FindIndex(p => p.key == key);
            if (i >= 0) props[i] = new KitProp { key = key, value = value };
            else props.Add(new KitProp { key = key, value = value });
        }

        public float GetFloat(string key, float fallback = 0f) =>
            float.TryParse(Get(key), System.Globalization.NumberStyles.Float,
                System.Globalization.CultureInfo.InvariantCulture, out var v) ? v : fallback;
    }
}
