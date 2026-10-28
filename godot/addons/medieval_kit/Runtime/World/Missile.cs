using System;
using Godot;

namespace MedievalKit;

/// <summary>a thing a missile carries that acts when it lands (a spell's orb bursting): Missile calls Landed on each
/// one before the missile goes</summary>
public interface IMissileLanding { void Landed(); }

/// <summary>
/// Something the player sends flying (an arrow, a thrown knife or axe): a copy of its prop on a shallow arc from the hand
/// to where the target stood, an arrow along its flight, a thrown blade spinning end over end; it calls back when it
/// arrives (the hit is the thrower's to settle) and lies there a moment. Only a look: nothing it passes through stops
/// it. Lives under the current scene (it goes with the level). Unity: Missile.
/// </summary>
public partial class Missile : Node3D
{
    Vector3 from, to, bend;
    float t, time, arc, spin, stay = 2.5f;
    bool arrived;
    Action onArrive;

    /// <summary>where it left, where it is going, and how long it takes (s)</summary>
    public Vector3 From => from;
    public Vector3 To => to;
    public float Seconds => time;

    /// <summary>fly a copy of model (a scene, or a node duplicated) from a to b at speed (m/s); spin: turns a second end
    /// over end (0: it points along its flight, its +Y forward), the prop turned by rot (degrees) first</summary>
    public static Missile Fly(Node3D model, Vector3 a, Vector3 b, float speed, float spin, Vector3 rot, Vector3 scale, Action arrive) =>
        Make(model != null ? (Node3D)model.Duplicate() : null, a, b, speed, spin, rot, scale, arrive);

    public static Missile Fly(PackedScene model, Vector3 a, Vector3 b, float speed, float spin, Vector3 rot, Vector3 scale, Action arrive) =>
        Make(model?.Instantiate<Node3D>(), a, b, speed, spin, rot, scale, arrive);

    static Missile Make(Node3D look, Vector3 a, Vector3 b, float speed, float spin, Vector3 rot, Vector3 scale, Action arrive)
    {
        var tree = (SceneTree)Engine.GetMainLoop();
        var m = new Missile { Name = "Missile" };
        (tree.CurrentScene ?? tree.Root).AddChild(m);
        m.GlobalPosition = a;                                                // first: a trail by the metre starts here
        if (look != null)
        {
            foreach (var c in KitNodes.Below(look, "CollisionObject3D")) c.QueueFree();
            if (look is CollisionObject3D) look.SetProcess(false);
            look.Position = Vector3.Zero;
            look.RotationDegrees = rot;
            look.Scale = scale;
            m.AddChild(look);
            CreatureSilhouettes.Tag(look, false);
        }
        float d = a.DistanceTo(b);
        m.from = a; m.to = b; m.time = Mathf.Max(0.08f, d / Mathf.Max(1f, speed));
        m.arc = Mathf.Min(1.2f, d * 0.06f); m.spin = spin; m.onArrive = arrive;
        return m;
    }

    /// <summary>a spell's orb: the same flight, but gone the moment it lands (a ball of light hanging in the air where the
    /// creature was is not a hit)</summary>
    public static Missile FlyOrb(Node3D model, Vector3 a, Vector3 b, float speed, float spin, Vector3 rot, Vector3 scale, Action arrive)
    {
        var m = Fly(model, a, b, speed, spin, rot, scale, arrive);
        m.stay = 0f;
        return m;
    }

    /// <summary>it bows this far off the straight way at the middle of its flight (a dart weaving; it still lands where
    /// and when it was going to)</summary>
    public Missile Bend(Vector3 side) { bend = side; return this; }

    Vector3 At(float u) => from.Lerp(to, u) + (Vector3.Up * arc + bend) * (4f * u * (1f - u));

    public override void _Process(double delta)
    {
        float dt = (float)delta;
        if (arrived)
        {
            if ((stay -= dt) <= 0f) QueueFree();
            return;
        }
        t += dt;
        float u = Mathf.Clamp(t / time, 0f, 1f);
        var p = At(u);
        var ahead = At(Mathf.Min(1f, u + 0.02f)) - p;
        if (ahead.LengthSquared() < 1e-6f) ahead = to - from;
        var dir = ahead.Normalized();
        var up = Mathf.Abs(dir.Y) > 0.99f ? Vector3.Forward : Vector3.Up;
        var look = Basis.LookingAt(dir, up);                                  // -Z along the flight
        var basis = spin != 0f ? look * new Basis(Vector3.Right, -t * spin * Mathf.Tau)                 // end over end
                               : look * new Basis(Vector3.Right, -Mathf.Pi * 0.5f);                    // +Y along the flight
        GlobalTransform = new Transform3D(basis, p);
        if (u < 1f) return;
        arrived = true;
        try { onArrive?.Invoke(); }
        catch (Exception e) { GD.PushError(e.ToString()); }
        if (stay > 0f) return;
        foreach (var n in KitNodes.Below(this, ""))                 // a spell's orb: gone as it lands
            if (n is IMissileLanding l) l.Landed();
        QueueFree();
    }
}
