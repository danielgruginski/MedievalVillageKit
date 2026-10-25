using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// A fire's light wavering (on any light: a burning engine's, a campfire's, a kit light by a fire): three layers of
    /// noise move its brightness, its colour (deep orange when low, yellower when high) and a little of its range, and
    /// the light itself drifts a few centimetres. <see cref="level"/> scales it (a fire still catching),
    /// <see cref="FadeOut"/> dims it to nothing. Switched off, it gives the light back as it found it.
    /// </summary>
    public class FireFlicker : MonoBehaviour
    {
        static readonly Color Low = new Color(1f, 0.48f, 0.16f), High = new Color(1f, 0.64f, 0.32f);

        [Tooltip("Scales its brightness (a fire half alight: about half).")]
        public float level = 1f;
        [Tooltip("Colours it with the flicker, deep orange to yellow (off: the light keeps its own colour).")]
        public bool tint = true;
        [Tooltip("How much it wavers (1: a fire's own light; a room's big light by its hearth: less).")]
        [Range(0f, 1f)] public float depth = 1f;

        Light l;
        float baseI, baseRange, seed, fadeFrom = -1f, fadeFor = 1f;
        Color baseColour;
        Vector3 home;

        /// <summary>where it drifts round (its own place, unless a fire moves it)</summary>
        public Vector3 Home { get => home; set => home = value; }

        void Awake()
        {
            l = GetComponent<Light>();
            seed = Random.value * 100f;
            home = transform.localPosition;
            if (l != null) { baseI = l.intensity; baseRange = l.range; baseColour = l.color; }
        }

        /// <summary>dim to nothing over this long</summary>
        public void FadeOut(float seconds) { fadeFrom = Time.time; fadeFor = Mathf.Max(0.1f, seconds); }

        void Update()
        {
            if (l == null) return;
            float t = Time.time;
            float n = 0.55f * Mathf.PerlinNoise(t * 5.3f, seed) + 0.3f * Mathf.PerlinNoise(t * 11.7f, seed + 3.1f) +
                      0.15f * Mathf.PerlinNoise(t * 23f, seed + 6.7f);
            float k = fadeFrom < 0f ? 1f : Mathf.Clamp01(1f - (t - fadeFrom) / fadeFor);
            l.intensity = baseI * level * k * (1f + depth * (0.45f * n - 0.25f));
            if (tint) l.color = Color.Lerp(Low, High, n);
            l.range = baseRange * (1f + depth * (0.1f * n - 0.05f));
            float s = t * 0.9f;                                         // a slow drift, about 12 cm each way
            transform.localPosition = home + 0.24f * new Vector3(Mathf.PerlinNoise(s, seed + 11f) - 0.5f,
                                                                 Mathf.PerlinNoise(s, seed + 23f) - 0.5f,
                                                                 Mathf.PerlinNoise(s, seed + 37f) - 0.5f);
        }

        void OnDisable()
        {
            if (l == null) return;
            l.intensity = baseI; l.range = baseRange; l.color = baseColour;
            transform.localPosition = home;
        }
    }
}
