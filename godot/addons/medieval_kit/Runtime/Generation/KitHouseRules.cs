using System.Collections.Generic;
using System.Linq;
using System.Text.Json.Nodes;
using Godot;

namespace MedievalKit;

/// <summary>
/// What KitHouseGenerator builds with: the grid, the pieces that fill each role and the style table, read from
/// res://kit/data/house_rules.json (vkx_export_house_rules: vk_helpers.build_house_v's rules). Point
/// <see cref="RulesPath"/> at a copy to add your own pieces to a role (another upper-wall frame, a different porch...)
/// or new style options. Pieces are the kit's by name (<see cref="KitInteriorRules.Info"/>), materials the kit's
/// library. Unity: KitHouseRules (an asset Build All makes from the same file).
/// </summary>
[GlobalClass, Tool]
public partial class KitHouseRules : Resource
{
    [Export(PropertyHint.File, "*.json")] public string RulesPath = KitPaths.Data + "house_rules.json";

    static KitHouseRules shared;
    /// <summary>the kit's own rules, loaded once</summary>
    public static KitHouseRules Default => shared ??= new KitHouseRules();

    public class GroundSet
    {
        public string name;     // "Stone", "Plaster"
        public PackedScene wallDoor, wallWindow, wallPlain, corner;
        /// <summary>concave corner of an L-house</summary>
        public PackedScene innerCorner;
    }

    public class RoofSet
    {
        public PackedScene gable, mid, hip;
        /// <summary>the L-house's corner roof (tile roofs only)</summary>
        public PackedScene lcorner;
    }

    public class StyleOption
    {
        public string name;
        /// <summary>replaces the kind's slot; null = the piece's own material</summary>
        public Material material;
    }

    public class StyleKind
    {
        public string kind;         // plaster, shutter, roof, cloth, stone
        public int blenderSlot;     // the material slot this kind swaps
        public List<StyleOption> options = new();
        public StyleOption Find(string name) => options.Find(o => o.name == name);
    }

    // grid (metres)
    public float cell = 3f;     // one wall bay
    public float h1 = 3f;       // ground storey
    public float h2 = 2.8f;     // each upper storey
    public float depth = 6f;    // houses are two cells deep

    // pieces by role
    public List<GroundSet> ground = new();
    public List<PackedScene> upperWallWindow = new(), upperWallPlain = new(), upperCorner = new(), upperInnerCorner = new();
    public RoofSet tileRoof = new(), thatchRoof = new();
    public List<PackedScene> chimney = new(), dormer = new(), porch = new(), flowerBox = new(), weeds = new(), ivy = new(), planter = new(), lantern = new();

    // styles
    public List<StyleKind> styles = new();

    // random style (vk_helpers.random_style)
    public float stoneGroundChance = 0.6f;
    public List<string> plasterChoices = new() { "Cream", "White", "Ochre", "Rose", "Cream" };
    public List<string> shutterChoices = new() { "Teal", "Red", "Green", "Blue", "Natural" };
    public float shutterWornChance = 0.2f;
    public List<string> roofChoices = new() { "Red", "Blue", "Green", "Red" };
    public int thatchWeightStone = 1, thatchWeightPlaster = 2;

    /// <summary>pieces the rules name that the kit lacks (the last load)</summary>
    public List<string> missing = new();

    string loaded;

    public StyleKind Kind(string kind) { Load(); return styles.Find(s => s.kind == kind); }
    public GroundSet Ground(string name) { Load(); return ground.Find(g => g.name == name) ?? (ground.Count > 0 ? ground[0] : null); }

    /// <summary>reads RulesPath (once per path)</summary>
    public void Load()
    {
        if (loaded == RulesPath) return;
        loaded = RulesPath;
        missing.Clear();
        if (!FileAccess.FileExists(RulesPath)) { missing.Add(RulesPath); return; }
        var j = KitJson.ParseObject(FileAccess.GetFileAsString(RulesPath));
        PackedScene P(JsonNode n)
        {
            string name = n.S();
            if (name == null) return null;
            var s = KitInteriorRules.Default.Prefab(name);
            if (s == null) missing.Add(name);
            return s;
        }
        List<PackedScene> Ps(JsonNode t) => t is JsonArray a ? a.Select(P).Where(x => x != null).ToList() : new List<PackedScene>();
        cell = j["cell"].F(); h1 = j["h1"].F(); h2 = j["h2"].F(); depth = j["depth"].F();
        var roles = (JsonObject)j["roles"];
        ground.Clear();
        foreach (var g in (JsonObject)roles["ground_wall"])
            ground.Add(new GroundSet
            {
                name = g.Key, wallDoor = P(g.Value["D"]), wallWindow = P(g.Value["W"]), wallPlain = P(g.Value["."]),
                corner = P(roles["ground_corner"][g.Key]),
                innerCorner = roles["ground_inner_corner"]?[g.Key] != null ? P(roles["ground_inner_corner"][g.Key]) : null,
            });
        upperWallWindow = Ps(roles["upper_wall_window"]);
        upperWallPlain = Ps(roles["upper_wall_plain"]);
        upperCorner = Ps(roles["upper_corner"]);
        upperInnerCorner = Ps(roles["upper_inner_corner"]);
        RoofSet Roof(JsonNode t) => new() { gable = P(t["gable"]), mid = P(t["mid"]), hip = P(t["hip"]), lcorner = t["lcorner"] != null ? P(t["lcorner"]) : null };
        tileRoof = Roof(roles["roof"]["tile"]); thatchRoof = Roof(roles["roof"]["thatch"]);
        chimney = Ps(roles["chimney"]); dormer = Ps(roles["dormer"]); porch = Ps(roles["porch"]);
        flowerBox = Ps(roles["flower_box"]); weeds = Ps(roles["weeds"]); ivy = Ps(roles["ivy"]);
        planter = Ps(roles["planter"]); lantern = Ps(roles["lantern"]);
        styles.Clear();
        foreach (var kv in (JsonObject)j["variants"])
        {
            var k = new StyleKind { kind = kv.Key, blenderSlot = j["slots"][kv.Key].I() };
            foreach (var o in (JsonObject)kv.Value)
                k.options.Add(new StyleOption { name = o.Key, material = o.Value.IsStr() ? KitInteriorRules.Default.Mat(o.Value.S()) : null });
            styles.Add(k);
        }
        var rsj = j["random_style"];
        stoneGroundChance = rsj["ground"]["Stone"].F();
        plasterChoices = rsj["plaster"].AsArray().Select(x => x.S()).ToList();
        shutterChoices = rsj["shutter"].AsArray().Select(x => x.S()).ToList();
        shutterWornChance = rsj["shutter_worn"].F();
        roofChoices = rsj["roof"].AsArray().Select(x => x.S()).ToList();
        thatchWeightPlaster = rsj["roof_thatch_plaster"].I(); thatchWeightStone = rsj["roof_thatch_stone"].I();
    }
}
