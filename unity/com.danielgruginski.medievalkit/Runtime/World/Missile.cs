using System;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>a thing a missile carries that acts when it lands (a spell's orb bursting): Missile calls Landed on
    /// each one before the missile goes</summary>
    public interface IMissileLanding { void Landed(); }

    /// <summary>
    /// Something the player sends flying (an arrow, a thrown knife or axe): a copy of its prop on a shallow arc from the
    /// hand to where the target stood, an arrow along its flight, a thrown blade spinning end over end; it calls back
    /// when it arrives (the hit is the thrower's to settle) and lies there a moment. Only a look: nothing it passes
    /// through stops it.
    /// </summary>
    public class Missile : MonoBehaviour
    {
        Vector3 from, to, bend;
        float t, time, arc, spin, stay = 2.5f;

        /// <summary>where it left, where it is going, and how long it takes (s)</summary>
        public Vector3 From => from;
        public Vector3 To => to;
        public float Seconds => time;
        bool arrived;
        Action onArrive;

        /// <summary>fly a copy of model from a to b at speed (m/s); spin: turns a second end over end (0: it points along
        /// its flight, its +Y forward), the prop turned by rot first</summary>
        public static Missile Fly(GameObject model, Vector3 a, Vector3 b, float speed, float spin, Vector3 rot, Vector3 scale, Action arrive)
        {
            var go = new GameObject("Missile");
            go.transform.position = a;                                      // first: a trail by the metre starts here
            var m = go.AddComponent<Missile>();
            if (model != null)
            {
                var look = Instantiate(model, go.transform, false);
                look.transform.localRotation = Quaternion.Euler(rot);
                look.transform.localScale = scale;
                foreach (var c in look.GetComponentsInChildren<Collider>(true)) Destroy(c);
                CreatureSilhouettes.Tag(look, false);
            }
            float d = Vector3.Distance(a, b);
            m.from = a; m.to = b; m.time = Mathf.Max(0.08f, d / Mathf.Max(1f, speed));
            m.arc = Mathf.Min(1.2f, d * 0.06f); m.spin = spin; m.onArrive = arrive;
            return m;
        }

        /// <summary>a spell's orb: the same flight, but gone the moment it lands (an arrow lies there a moment; a ball of
        /// light hanging in the air where the creature was is not a hit); a bolt of fire bursts (<see cref="FireBolt"/>),
        /// another spell its own way (<see cref="SpellBolt"/>)</summary>
        public static Missile FlyOrb(GameObject model, Vector3 a, Vector3 b, float speed, float spin, Vector3 rot, Vector3 scale, Action arrive)
        {
            var m = Fly(model, a, b, speed, spin, rot, scale, arrive);
            m.stay = 0f;
            return m;
        }

        /// <summary>it bows this far off the straight way at the middle of its flight (a dart weaving; it still lands
        /// where and when it was going to)</summary>
        public Missile Bend(Vector3 side) { bend = side; return this; }

        Vector3 At(float u) => Vector3.Lerp(from, to, u) + (Vector3.up * arc + bend) * (4f * u * (1f - u));

        void Update()
        {
            if (arrived)
            {
                if ((stay -= Time.deltaTime) <= 0f) Destroy(gameObject);
                return;
            }
            t += Time.deltaTime;
            float u = Mathf.Clamp01(t / time);
            var p = At(u);
            var ahead = At(Mathf.Min(1f, u + 0.02f)) - p;
            if (ahead.sqrMagnitude < 1e-6f) ahead = to - from;
            var along = Quaternion.LookRotation(ahead.normalized, Vector3.up) * Quaternion.Euler(90f, 0f, 0f);   // +Y along the flight
            transform.SetPositionAndRotation(p, spin != 0f ? Quaternion.LookRotation(ahead.normalized, Vector3.up) *
                                                              Quaternion.Euler(t * spin * 360f, 0f, 0f) : along);
            if (u < 1f) return;
            arrived = true;
            try { onArrive?.Invoke(); }
            catch (Exception e) { Debug.LogException(e); }
            if (stay > 0f) return;
            foreach (var l in GetComponentsInChildren<IMissileLanding>())                  // a spell's orb: gone as it lands (fire bursts,
                l.Landed();                                                                         // its trail left to fade; a spell its own way)
            Destroy(gameObject);
        }
    }
}
