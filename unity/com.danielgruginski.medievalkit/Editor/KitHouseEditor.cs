using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace MedievalKit.Editor
{
    /// <summary>House generator tooling: the rules asset from Data/house_rules.json, the inspector, the menus.</summary>
    [InitializeOnLoad]
    public static class KitHouseTools
    {
        public const string RulesAsset = KitPaths.Generated + "/KitHouseRules.asset";
        public const string OutFolder = "Assets/MedievalKitHouses";

        static KitHouseTools()
        {
            // keep prefab links when generating in the editor
            KitHouseGenerator.Spawn = (prefab, parent) =>
                Application.isPlaying ? Object.Instantiate(prefab, parent) : (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
        }

        static string Abs(string p) => Path.GetFullPath(p);

        /// <summary>Data/house_rules.json -> Generated/KitHouseRules.asset (regenerated: copy it to customise).</summary>
        public static KitHouseRules BuildRules(System.Text.StringBuilder log)
        {
            string jp = KitPaths.Data + "/house_rules.json";
            if (!File.Exists(Abs(jp))) { log?.AppendLine("no house_rules.json"); return null; }
            var j = JObject.Parse(File.ReadAllText(Abs(jp)));
            var pieces = JObject.Parse(File.ReadAllText(Abs(KitPaths.Data + "/pieces.json")));
            int missing = 0;
            GameObject P(string name)
            {
                var pd = pieces[name];
                if (pd == null) { missing++; log?.AppendLine($"  house rules: no piece {name}"); return null; }
                string dir = Path.GetDirectoryName((string)pd["fbx"]).Replace('\\', '/').Substring("Art/Models/".Length);
                var go = AssetDatabase.LoadAssetAtPath<GameObject>($"{KitPaths.Prefabs}/{dir}/{name}.prefab");
                if (go == null) { missing++; log?.AppendLine($"  house rules: no prefab {name}"); }
                return go;
            }
            List<GameObject> Ps(JToken t) => t.Select(x => P((string)x)).Where(x => x != null).ToList();

            var r = AssetDatabase.LoadAssetAtPath<KitHouseRules>(RulesAsset);
            bool isNew = r == null;
            if (isNew) r = ScriptableObject.CreateInstance<KitHouseRules>();
            r.cell = (float)j["cell"]; r.h1 = (float)j["h1"]; r.h2 = (float)j["h2"]; r.depth = (float)j["depth"];
            var roles = (JObject)j["roles"];
            r.ground.Clear();
            foreach (var g in (JObject)roles["ground_wall"])
                r.ground.Add(new KitHouseRules.GroundSet
                {
                    name = g.Key, wallDoor = P((string)g.Value["D"]), wallWindow = P((string)g.Value["W"]),
                    wallPlain = P((string)g.Value["."]), corner = P((string)roles["ground_corner"][g.Key]),
                    innerCorner = roles["ground_inner_corner"]?[g.Key] != null ? P((string)roles["ground_inner_corner"][g.Key]) : null
                });
            r.upperWallWindow = Ps(roles["upper_wall_window"]);
            r.upperWallPlain = Ps(roles["upper_wall_plain"]);
            r.upperCorner = Ps(roles["upper_corner"]);
            r.upperInnerCorner = roles["upper_inner_corner"] != null ? Ps(roles["upper_inner_corner"]) : new List<GameObject>();
            KitHouseRules.RoofSet Roof(JToken t) => new KitHouseRules.RoofSet
            {
                gable = P((string)t["gable"]), mid = P((string)t["mid"]), hip = P((string)t["hip"]),
                lcorner = t["lcorner"] != null ? P((string)t["lcorner"]) : null
            };
            r.tileRoof = Roof(roles["roof"]["tile"]); r.thatchRoof = Roof(roles["roof"]["thatch"]);
            r.chimney = Ps(roles["chimney"]); r.dormer = Ps(roles["dormer"]); r.porch = Ps(roles["porch"]);
            r.flowerBox = Ps(roles["flower_box"]); r.weeds = Ps(roles["weeds"]); r.ivy = Ps(roles["ivy"]);
            r.planter = Ps(roles["planter"]); r.lantern = Ps(roles["lantern"]);
            r.styles.Clear();
            foreach (var kv in (JObject)j["variants"])
            {
                var k = new KitHouseRules.StyleKind { kind = kv.Key, blenderSlot = (int)j["slots"][kv.Key] };
                foreach (var o in (JObject)kv.Value)
                    k.options.Add(new KitHouseRules.StyleOption
                    {
                        name = o.Key,
                        material = o.Value.Type == JTokenType.String ? AssetDatabase.LoadAssetAtPath<Material>($"{KitPaths.Materials}/{(string)o.Value}.mat") : null
                    });
                r.styles.Add(k);
            }
            var rsj = j["random_style"];
            r.stoneGroundChance = (float)rsj["ground"]["Stone"];
            r.plasterChoices = rsj["plaster"].Select(x => (string)x).ToList();
            r.shutterChoices = rsj["shutter"].Select(x => (string)x).ToList();
            r.shutterWornChance = (float)rsj["shutter_worn"];
            r.roofChoices = rsj["roof"].Select(x => (string)x).ToList();
            r.thatchWeightPlaster = (int)rsj["roof_thatch_plaster"]; r.thatchWeightStone = (int)rsj["roof_thatch_stone"];
            if (isNew) AssetDatabase.CreateAsset(r, RulesAsset); else EditorUtility.SetDirty(r);
            AssetDatabase.SaveAssets();
            int noMat = r.styles.Sum(s => s.options.Count(o => o.material == null)) - r.styles.Count;   // one base option per kind
            log?.AppendLine($"house rules: {r.ground.Count} ground sets, {r.styles.Count} style kinds, {missing} missing pieces" +
                            (noMat > 0 ? $", {noMat} style options without a material" : ""));
            return r;
        }

        [MenuItem("GameObject/Medieval Kit/House Generator", false, 10)]
        static void CreateGenerator(MenuCommand cmd)
        {
            var go = new GameObject("House");
            GameObjectUtility.SetParentAndAlign(go, cmd.context as GameObject);
            var g = go.AddComponent<KitHouseGenerator>();
            g.rules = AssetDatabase.LoadAssetAtPath<KitHouseRules>(RulesAsset);
            g.seed = Random.Range(1, 100000);
            Undo.RegisterCreatedObjectUndo(go, "House Generator");
            Selection.activeGameObject = go;
            if (g.rules != null) g.Generate();
        }

        /// <summary>Saves a generated house as a prefab in Assets/MedievalKitHouses (kit pieces stay nested prefabs).</summary>
        public static string SaveAsPrefab(KitHouseGenerator g, string name = null)
        {
            Directory.CreateDirectory(Abs(OutFolder));
            name = name ?? (g.shape == KitHouseGenerator.Shape.L
                ? $"House_L{2 + g.armCells}x{2 + g.wingCells}_{g.stories}st_{g.seed}"
                : $"House_{g.cells}x2_{g.stories}st_{g.seed}");
            string path = $"{OutFolder}/{name}.prefab";
            PrefabUtility.SaveAsPrefabAsset(g.gameObject, path);
            return path;
        }

        /// <summary>The kit levels' look for a scene of your own: the lights, the post volume (AgX) and the ambient of a level.</summary>
        public static void CopyLighting(UnityEngine.SceneManagement.Scene dst, string levelPath, System.Func<Light, bool> keep = null)
        {
            var src = EditorSceneManager.OpenScene(levelPath, OpenSceneMode.Additive);
            UnityEngine.SceneManagement.SceneManager.SetActiveScene(src);
            var mode = RenderSettings.ambientMode; var flat = RenderSettings.ambientLight;
            var sky = RenderSettings.ambientSkyColor; var eq = RenderSettings.ambientEquatorColor; var gr = RenderSettings.ambientGroundColor;
            // the kit's levels have no environment reflection (Custom, intensity 0): Unity's default (its procedural sky at
            // full strength) washes dark leaves and painted wood blue-white at grazing angles
            var refl = RenderSettings.defaultReflectionMode; var reflI = RenderSettings.reflectionIntensity; var reflT = RenderSettings.customReflectionTexture;
            UnityEngine.SceneManagement.SceneManager.SetActiveScene(dst);
            foreach (var l in Object.FindObjectsByType<Light>(FindObjectsSortMode.None))
                if (l.gameObject.scene == dst) Object.DestroyImmediate(l.gameObject);
            foreach (var root in src.GetRootGameObjects())
            {
                foreach (var l in root.GetComponentsInChildren<Light>())
                {
                    if (keep != null && !keep(l)) continue;
                    var c = Object.Instantiate(l.gameObject); c.name = l.name;
                    UnityEngine.SceneManagement.SceneManager.MoveGameObjectToScene(c, dst);
                    c.transform.SetPositionAndRotation(l.transform.position, l.transform.rotation);
                }
                foreach (var v in root.GetComponentsInChildren<UnityEngine.Rendering.Volume>())
                {
                    var c = Object.Instantiate(v.gameObject); c.name = v.name;
                    UnityEngine.SceneManagement.SceneManager.MoveGameObjectToScene(c, dst);
                }
            }
            EditorSceneManager.CloseScene(src, true);
            RenderSettings.ambientMode = mode; RenderSettings.ambientLight = flat;
            RenderSettings.ambientSkyColor = sky; RenderSettings.ambientEquatorColor = eq; RenderSettings.ambientGroundColor = gr;
            RenderSettings.defaultReflectionMode = refl; RenderSettings.reflectionIntensity = reflI; RenderSettings.customReflectionTexture = reflT;
        }

        [MenuItem("Tools/Medieval Kit/Generate House Set")]
        public static void GenerateHouseSetMenu() => GenerateHouseSet(12, 1000);

        /// <summary>A set of random houses as prefabs plus Assets/MedievalKitHouses/HouseShowcase.unity laying them out.</summary>
        public static List<string> GenerateHouseSet(int count, int seed0)
        {
            if (AssetDatabase.LoadAssetAtPath<KitHouseRules>(RulesAsset) == null) { Debug.LogError("[MedievalKit] no house rules: run Build All"); return null; }
            var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            var rules = AssetDatabase.LoadAssetAtPath<KitHouseRules>(RulesAsset);     // after the scene switch, which unloads unused assets
            var rnd = new System.Random(seed0);
            var paths = new List<string>();
            float x = 0, z = 0, rowDepth = 0;
            for (int i = 0; i < count; i++)
            {
                var go = new GameObject("House");
                var g = go.AddComponent<KitHouseGenerator>();
                g.rules = rules;
                if (rnd.NextDouble() < 0.33)
                {
                    g.shape = KitHouseGenerator.Shape.L;      // about a third are L-houses (build_L_v)
                    g.armCells = 1 + rnd.Next(2); g.wingCells = 1 + rnd.Next(2);
                }
                else g.cells = 2 + rnd.Next(3);              // 2-4 bays, as the valley's infill houses
                g.stories = rnd.NextDouble() < 0.25 ? 1 : 2;
                g.seed = seed0 + i * 37;
                g.Generate();
                paths.Add(SaveAsPrefab(g));
                float w = (g.shape == KitHouseGenerator.Shape.L ? (2 + g.armCells) : g.cells) * rules.cell + 4f;
                if (x + w > 48f) { x = 0; z -= rowDepth; rowDepth = 0; }
                bool isL = g.shape == KitHouseGenerator.Shape.L;
                // an L-house's pivot is its corner block: shift it so the footprint sits centred in its slot
                go.transform.position = new Vector3(-(x + w / 2) + (isL ? 0.5f * rules.cell * g.armCells : 0f), 0, z);
                x += w; rowDepth = Mathf.Max(rowDepth, (isL ? rules.cell * (2 + g.wingCells) : rules.depth) + 7f);
                go.name = Path.GetFileNameWithoutExtension(paths[paths.Count - 1]);
            }
            CopyLighting(scene, $"{KitPaths.Levels}/Slice_House.unity");
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Ground"; ground.transform.position = new Vector3(-24, -0.01f, z / 2); ground.transform.localScale = new Vector3(7, 1, 6);
            EditorSceneManager.SaveScene(scene, $"{OutFolder}/HouseShowcase.unity");
            Debug.Log($"[MedievalKit] {paths.Count} houses -> {OutFolder}");
            return paths;
        }
    }

    [CustomEditor(typeof(KitHouseGenerator))]
    public class KitHouseGeneratorEditor : UnityEditor.Editor
    {
        public override void OnInspectorGUI()
        {
            DrawDefaultInspector();
            var g = (KitHouseGenerator)target;
            if (g.rules == null && GUILayout.Button("Use the kit's house rules"))
                g.rules = AssetDatabase.LoadAssetAtPath<KitHouseRules>(KitHouseTools.RulesAsset);
            EditorGUILayout.Space();
            using (new EditorGUILayout.HorizontalScope())
            {
                if (GUILayout.Button("Generate")) Regenerate(g);
                if (GUILayout.Button("Reroll")) { Undo.RecordObject(g, "Reroll"); g.seed = Random.Range(1, 100000); Regenerate(g); }
                if (GUILayout.Button("Clear")) { Undo.RegisterFullObjectHierarchyUndo(g.gameObject, "Clear"); g.Clear(); }
            }
            if (GUILayout.Button("Save as Prefab"))
                EditorGUIUtility.PingObject(AssetDatabase.LoadAssetAtPath<GameObject>(KitHouseTools.SaveAsPrefab(g)));
            if (g.LastStyle.Count > 0)
                EditorGUILayout.HelpBox($"{g.LastPieceCount} pieces. Style: " + string.Join(", ", g.LastStyle.Select(kv => $"{kv.Key} {kv.Value}")), MessageType.None);
        }

        static void Regenerate(KitHouseGenerator g)
        {
            Undo.RegisterFullObjectHierarchyUndo(g.gameObject, "Generate House");
            g.Generate();
            EditorSceneManager.MarkSceneDirty(g.gameObject.scene);
        }
    }
}
