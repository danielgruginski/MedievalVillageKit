using System.Collections.Generic;
using Godot;

namespace MedievalKit;

/// <summary>
/// A node's children and the nodes below it as plain lists. Godot's FindChildren and GetChildren hand back a Godot array
/// each call; one left to .NET's finalizer may be freed after the engine has shut down, and the game crashes on quit
/// (0xC0000005 in godotsharp_array_destroy). These dispose theirs at once (and Children makes none).
/// </summary>
public static class KitNodes
{
    /// <summary>the nodes below root of a class (empty: any) whose names match the pattern, recursively (FindChildren,
    /// owned or not); root null: none</summary>
    public static List<Node> Below(Node root, string type = "", string pattern = "*", bool recursive = true)
    {
        var list = new List<Node>();
        if (root == null) return list;
        var found = root.FindChildren(pattern, type, recursive, false);
        using var native = (Godot.Collections.Array)found;
        foreach (var n in found) list.Add(n);
        return list;
    }

    /// <summary>a node's own children, in order (null: none)</summary>
    public static IEnumerable<Node> Children(Node n)
    {
        if (n == null) yield break;
        int count = n.GetChildCount();
        for (int i = 0; i < count && i < n.GetChildCount(); i++) yield return n.GetChild(i);
    }
}
