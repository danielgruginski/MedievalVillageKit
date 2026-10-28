using Godot;

namespace MedievalKit;

/// <summary>
/// A collider that stands for a usable thing kept elsewhere: a find's prop (a dead goblin, a chest) whose
/// <see cref="Interactable"/> sits on a marker. Put it as a child of the prop's body (a CollisionObject3D): the cursor on
/// the prop is on the find. Unity: UseVia.
/// </summary>
[GlobalClass]
public partial class UseVia : Node
{
    [Export] public Interactable Thing;

    /// <summary>the usable thing a hit collider is or stands for (null: none)</summary>
    public static Interactable Of(Node c)
    {
        for (var n = c; n != null; n = n.GetParent()) if (n is Interactable i) return i;
        if (c == null) return null;
        foreach (var ch in KitNodes.Children(c))
            if (ch is UseVia { Thing: { } t } && GodotObject.IsInstanceValid(t)) return t;
        return null;
    }
}
