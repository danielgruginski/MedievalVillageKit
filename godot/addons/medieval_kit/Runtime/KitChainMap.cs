using System;
using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>One map of a <see cref="KitChain"/>: a generated cave or dungeon (its portals in its settings), or a
/// hand-made plan (a cave map whose record's "portals" each have their `at`), and how it joins an earlier map. Unity:
/// KitChain.Map.</summary>
[GlobalClass]
public partial class KitChainMap : Resource
{
    public enum Kind { Cave, Dungeon, Plan }

    [Export] public string id = "map";
    [Export] public Kind kind = Kind.Cave;
    /// <summary>its portals are in the generator's settings (portals): one for the way in, one for the way on</summary>
    [Export] public KitCaveOptions cave = new();
    [Export] public KitDungeonOptions dungeon = new();
    /// <summary>Plan: a hand-made map's plan file (&lt;name&gt;.plan.txt, typed as for KitRoom); else the text below</summary>
    [Export(PropertyHint.File, "*.txt")] public string planFile = "";
    /// <summary>Plan: its room record file (&lt;name&gt;.record.json; a cave map: "cave": true); its "portals" are the map's
    /// openings, each with its `at` set</summary>
    [Export(PropertyHint.File, "*.json")] public string recordFile = "";
    [Export(PropertyHint.MultilineText)] public string plan = "";
    [Export(PropertyHint.MultilineText)] public string record = "";
    /// <summary>its portal the earlier map's connector reaches (empty for the first map)</summary>
    [Export] public string inPortal = "south";
    /// <summary>the map it joins (empty: the one before it in the list)</summary>
    [Export] public string attachTo = "";
    /// <summary>the portal of that map it joins through (empty: that map's outPortal)</summary>
    [Export] public string attachPortal = "";
    /// <summary>the portal a later map joins by default (empty if none does)</summary>
    [Export] public string outPortal = "north";
    /// <summary>the connector from the map it joins: its length, seed and style (its edges follow the two portals)</summary>
    [Export] public KitConnectorOptions connector = new();

    static string Read(string path) => !string.IsNullOrEmpty(path) && FileAccess.FileExists(path) ? FileAccess.GetFileAsString(path) : null;

    public string PlanText => Read(planFile) ?? plan;
    public string RecordText => Read(recordFile) ?? record;

    /// <summary>the map's portals: its generator's, or a plan's record's</summary>
    public List<KitPortal> Portals()
    {
        if (kind == Kind.Cave) return cave?.portals.ToList() ?? new List<KitPortal>();
        if (kind == Kind.Dungeon) return dungeon?.portals.ToList() ?? new List<KitPortal>();
        try { return KitPortal.Of(KitJson.ParseObject(RecordText)); }
        catch (Exception) { return new List<KitPortal>(); }
    }
}
