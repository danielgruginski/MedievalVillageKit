using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.AI;

namespace MedievalKit
{
    /// <summary>
    /// Small helpers for putting things down on a level's floor: the floor under a point (the nearest hit straight down,
    /// skipping what <c>ignore</c> says is not floor: a body, a creature) and spots for n things round a point on the
    /// navmesh (a loose ring, apart from each other: dropped loot). From the Guild RPG's GroundLoot (FULL_PORT_PLAN 3a).
    /// </summary>
    public static class KitGround
    {
        /// <summary>the floor under a point: the nearest surface from 1.2 m above down to 1.8 m below, skipping colliders
        /// <paramref name="ignore"/> rejects (none: the point itself)</summary>
        public static Vector3 Floor(Vector3 p, Func<Collider, bool> ignore = null)
        {
            var hits = Physics.RaycastAll(p + Vector3.up * 1.2f, Vector3.down, 3f, ~0, QueryTriggerInteraction.Ignore);
            float bestD = float.MaxValue;
            Vector3 best = p;
            foreach (var h in hits)
            {
                if (ignore != null && ignore(h.collider)) continue;
                if (h.distance < bestD) { bestD = h.distance; best = h.point; }
            }
            return best;
        }

        /// <summary>spots for n things round a point (a seed for the same spots again): a loose ring on the navmesh,
        /// 0.42 m apart where it can, each on the floor (<see cref="Floor"/>) with a yaw</summary>
        public static List<(Vector3 pos, float yaw)> Scatter(Vector3 at, float spread, int n, int seed, Func<Collider, bool> ignore = null)
        {
            var rng = new System.Random(seed);
            var made = new List<(Vector3, float)>();
            const float apart = 0.42f;
            for (int i = 0; i < n; i++)
            {
                Vector3 best = at;
                for (int tries = 0; tries < 8; tries++)
                {
                    float a = (float)(i * 2.39996 + rng.NextDouble() * 0.8);
                    float r = n == 1 && spread < 0.5f ? spread : spread * (0.55f + 0.6f * (float)rng.NextDouble()) + 0.12f * (i / 4);
                    var p = at + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * r;
                    if (NavMesh.SamplePosition(p, out var hit, 1.2f, NavMesh.AllAreas)) p = hit.position;
                    best = p;
                    if (made.All(m => (m.Item1 - p).sqrMagnitude > apart * apart)) break;
                }
                made.Add((Floor(best, ignore), (float)(rng.NextDouble() * 360.0)));
            }
            return made;
        }
    }
}
