using System;
using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>
/// Small helpers for putting things down on a level's floor: the floor under a point (the nearest hit straight down,
/// skipping what <c>ignore</c> says is not floor: a body, a creature) and spots for n things round a point on the
/// navmesh (a loose ring, apart from each other: dropped loot). In the main viewport's world. Unity: KitGround.
/// </summary>
public static class KitGround
{
    static World3D World => ((SceneTree)Engine.GetMainLoop()).Root.World3D;

    /// <summary>the floor under a point: the nearest surface from 1.2 m above down to 1.8 m below, skipping colliders
    /// <paramref name="ignore"/> rejects (none: the point itself)</summary>
    public static Vector3 Floor(Vector3 p, Func<Node, bool> ignore = null)
    {
        var space = World.DirectSpaceState;
        var skip = new Godot.Collections.Array<Rid>();
        using var skipNative = (Godot.Collections.Array)skip;        // (disposed: see KitClickToMove.Cast)
        using var q = new PhysicsRayQueryParameters3D { From = p + Vector3.Up * 1.2f, To = p + Vector3.Down * 1.8f, CollideWithAreas = false };
        for (int i = 0; i < 16; i++)
        {
            q.Exclude = skip;
            using var r = space.IntersectRay(q);
            if (r.Count == 0) break;
            if (ignore == null || !ignore(r["collider"].AsGodotObject() as Node)) return (Vector3)r["position"];
            skip.Add((Rid)r["rid"]);
        }
        return p;
    }

    /// <summary>spots for n things round a point (a seed for the same spots again): a loose ring on the navmesh,
    /// 0.42 m apart where it can, each on the floor (<see cref="Floor"/>) with a yaw (degrees)</summary>
    public static List<(Vector3 pos, float yaw)> Scatter(Vector3 at, float spread, int n, int seed, Func<Node, bool> ignore = null)
    {
        var rng = new Random(seed);
        var made = new List<(Vector3, float)>();
        var map = World.NavigationMap;
        var regions = NavigationServer3D.MapGetRegions(map);
        bool nav;
        using (var native = (Godot.Collections.Array)regions) nav = regions.Count > 0;   // (disposed: see KitClickToMove.Cast)
        const float apart = 0.42f;
        for (int i = 0; i < n; i++)
        {
            Vector3 best = at;
            for (int tries = 0; tries < 8; tries++)
            {
                float a = (float)(i * 2.39996 + rng.NextDouble() * 0.8);
                float r = n == 1 && spread < 0.5f ? spread : spread * (0.55f + 0.6f * (float)rng.NextDouble()) + 0.12f * (i / 4);
                var p = at + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * r;
                if (nav)
                {
                    var c = NavigationServer3D.MapGetClosestPoint(map, p);
                    if (c.DistanceTo(p) <= 1.2f) p = c;
                }
                best = p;
                if (made.All(m => (m.Item1 - p).LengthSquared() > apart * apart)) break;
            }
            made.Add((Floor(best, ignore), (float)(rng.NextDouble() * 360.0)));
        }
        return made;
    }
}
