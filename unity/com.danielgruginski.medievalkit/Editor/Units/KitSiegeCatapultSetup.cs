using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace MedievalKit.Editor
{
    /// <summary>
    /// The siege catapult unit (2026-10-23; HANDOFF 140): the orcs' onager rigged and animated in Blender
    /// (src/units/vku_siege_catapult.py), exported to Art/Units/SiegeCatapult:
    ///   VKU_SiegeCatapult.fbx            Generic rig, avatar from this model, Motion = root-motion node (a sibling of
    ///                                    Root: nothing skinned hangs from it), Socket_Projectile; the kit's own
    ///                                    materials (Generated/Materials: M_VK_Wood, _Iron, _Burlap, _Void,
    ///                                    M_VKI_StoneBlockIn), so Build Materials must have run
    ///   Anims/VKU_SiegeCatapult@*.fbx    Idle, IdleLoaded, Move, Load, Throw, Hit, Destroyed (avatar copied from the
    ///                                    model); loop flags, root motion and events (OnUnitEvent: Release, Slam,
    ///                                    Hooked, Loaded, Break, Snap) from Anims/siegecatapult_clips.json
    ///   SM_VKU_CatapultStone.fbx         the projectile (written the kit's way: no root rotation)
    /// Builds into Generated/Units/SiegeCatapult: AC_VKU_SiegeCatapult (states by clip, parameters Moving, Load,
    /// Throw, Hit, Destroyed), VKU_SiegeCatapult.prefab (Animator, root motion off until a game drives it,
    /// KitUnitEvents), VKU_SiegeCatapult_Charred.prefab (the wood swapped for M_VKU_WoodCharred, the burnt look for the
    /// wreck), VKU_CatapultStone.prefab (mesh, sphere collider, rigidbody). No scene is opened or changed: the lineup
    /// renders use a preview scene. Report and renders: Logs/MedievalKit/SiegeCatapult.
    /// </summary>
    public static class KitSiegeCatapultSetup
    {
        public const string Unit = "VKU_SiegeCatapult";
        public const string Art = KitPaths.Package + "/Art/Units/SiegeCatapult";
        public const string Anims = Art + "/Anims";
        public const string OutDir = KitPaths.Generated + "/Units/SiegeCatapult";
        public const string PrefabPath = OutDir + "/" + Unit + ".prefab";
        public const string CharredPrefabPath = OutDir + "/" + Unit + "_Charred.prefab";
        public const string StonePrefabPath = OutDir + "/VKU_CatapultStone.prefab";
        public const string ControllerPath = OutDir + "/AC_" + Unit + ".controller";
        public const string CharredMaterialPath = OutDir + "/M_VKU_WoodCharred.mat";
        public const string EventFunction = "OnUnitEvent";
        const string ModelPath = Art + "/" + Unit + ".fbx";
        const string StoneModelPath = Art + "/SM_VKU_CatapultStone.fbx";
        const string ClipsJson = Anims + "/siegecatapult_clips.json";
        static readonly string[] KitMaterials = { "M_VK_Wood", "M_VK_Iron", "M_VK_Burlap", "M_VK_Void", "M_VKI_StoneBlockIn" };

        static string LogDir => Path.GetFullPath(Path.Combine("Logs", "MedievalKit", "SiegeCatapult"));

        [Serializable] class ClipEvent { public string name; public float time; }
        [Serializable] class ClipInfo { public string name; public int frames; public int fps; public bool loop; public bool rootMotion; public ClipEvent[] events; }
        [Serializable] class ClipList { public ClipInfo[] clips; }

        [MenuItem("Tools/Medieval Kit/Units/Build Siege Catapult")]
        public static void Build() => Run(true);

        /// <summary>renders: also the lineup renders (a preview scene; the open scenes are never touched).</summary>
        public static void Run(bool renders)
        {
            Directory.CreateDirectory(LogDir);
            var log = new StringBuilder();
            Application.LogCallback onLog = (c, s, t) => { if (t != LogType.Log) log.AppendLine($"[{t}] {c}"); };
            Application.logMessageReceived += onLog;
            try
            {
                AssetDatabase.Refresh();
                if (AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath) == null)
                {
                    log.AppendLine($"ERROR no {ModelPath}: export it first (tools/unit_catapult_run.py ... export)");
                    return;
                }
                EnsureFolder(OutDir);
                var mats = new Dictionary<string, Material>();
                foreach (var n in KitMaterials)
                {
                    var m = AssetDatabase.LoadAssetAtPath<Material>($"{KitPaths.Materials}/{n}.mat");
                    if (m == null) log.AppendLine($"ERROR missing kit material {n} (run Tools > Medieval Kit > Build Materials)");
                    else mats[n] = m;
                }
                var charred = CharredWood(log);

                var (avatar, motionPath, model) = ConfigureModel(mats, log);
                var clips = ConfigureClips(avatar, motionPath, log);
                var ctrl = BuildController(clips, log);

                var go = (GameObject)PrefabUtility.InstantiatePrefab(model);
                go.name = Unit;
                var anim = go.GetComponent<Animator>() ?? go.AddComponent<Animator>();
                anim.avatar = avatar;
                anim.runtimeAnimatorController = ctrl;
                anim.applyRootMotion = false;
                anim.cullingMode = AnimatorCullingMode.CullUpdateTransforms;
                if (go.GetComponent<KitUnitEvents>() == null) go.AddComponent<KitUnitEvents>();
                var smr = go.GetComponentInChildren<SkinnedMeshRenderer>();
                var root = FindChild(go.transform, "Root");
                if (smr != null && root != null)
                {
                    // the arm swings 2.5 m up and the wreck spreads ~3 m to the front: bounds for every clip, in Root's
                    // space (Unity axes: +Z the front), so culling never pops a pose away
                    smr.rootBone = root;
                    smr.localBounds = new Bounds(new Vector3(0f, 1.3f, 0.45f), new Vector3(4.2f, 2.9f, 6.6f));
                }
                var prefab = PrefabUtility.SaveAsPrefabAsset(go, PrefabPath);
                if (smr != null && charred != null)
                {
                    smr.sharedMaterials = smr.sharedMaterials.Select(m => m != null && m.name == "M_VK_Wood" ? charred : m).ToArray();
                    go.name = Unit + "_Charred";
                    PrefabUtility.SaveAsPrefabAsset(go, CharredPrefabPath);
                }
                Object.DestroyImmediate(go);
                log.AppendLine("prefabs: " + PrefabPath + ", " + CharredPrefabPath);
                var stone = BuildStone(mats, log);

                CheckSocket(prefab, clips, log);
                if (renders) RenderLineup(prefab, AssetDatabase.LoadAssetAtPath<GameObject>(CharredPrefabPath), stone, clips, log);
                AssetDatabase.SaveAssets();
                log.AppendLine("OK");
            }
            catch (Exception e)
            {
                log.AppendLine("EXCEPTION " + e);
            }
            finally
            {
                Application.logMessageReceived -= onLog;
                File.WriteAllText(Path.Combine(LogDir, "setup_report.txt"), log.ToString());
                Debug.Log("Siege catapult setup finished: " + Path.Combine(LogDir, "setup_report.txt"));
            }
        }

        // ------------------------------------------------------------------------------------------------ assets
        static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            var parent = Path.GetDirectoryName(path).Replace('\\', '/');
            EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }

        static Transform FindChild(Transform t, string name) =>
            t.GetComponentsInChildren<Transform>(true).FirstOrDefault(c => c.name == name);

        /// <summary>The wreck's charred wood: the kit's dark wood at 0.46 (the burnt static piece darkens its vertex
        /// colours to 0.4; the unit keeps the fresh ones, so the material carries the difference).</summary>
        static Material CharredWood(StringBuilder log)
        {
            var dark = AssetDatabase.LoadAssetAtPath<Material>($"{KitPaths.Materials}/M_VKI_WoodDark.mat");
            if (dark == null)
            {
                log.AppendLine("WARN no M_VKI_WoodDark: no charred material, no _Charred prefab");
                return null;
            }
            var m = AssetDatabase.LoadAssetAtPath<Material>(CharredMaterialPath);
            if (m == null)
            {
                m = new Material(dark) { name = "M_VKU_WoodCharred" };
                AssetDatabase.CreateAsset(m, CharredMaterialPath);
            }
            else
            {
                m.shader = dark.shader;
                m.CopyPropertiesFromMaterial(dark);
            }
            if (m.HasProperty("_BaseColor"))
            {
                var c = dark.GetColor("_BaseColor");
                m.SetColor("_BaseColor", new Color(c.r * 0.46f, c.g * 0.46f, c.b * 0.46f, c.a));
            }
            EditorUtility.SetDirty(m);
            return m;
        }

        static (Avatar, string, GameObject) ConfigureModel(Dictionary<string, Material> mats, StringBuilder log)
        {
            var imp = (ModelImporter)AssetImporter.GetAtPath(ModelPath);
            imp.globalScale = 1f;
            imp.useFileScale = true;
            imp.importNormals = ModelImporterNormals.Import;
            imp.importTangents = ModelImporterTangents.Import;
            imp.meshCompression = ModelImporterMeshCompression.Off;
            imp.isReadable = false;
            imp.importBlendShapes = false;
            imp.importVisibility = false;
            imp.importCameras = false;
            imp.importLights = false;
            imp.importAnimation = false;
            imp.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;
            foreach (var kv in mats)
                imp.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material), kv.Key), kv.Value);
            imp.animationType = ModelImporterAnimationType.Generic;
            imp.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
            imp.optimizeGameObjects = false;
            imp.SaveAndReimport();
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            var motion = FindChild(model.transform, "Motion");
            string motionPath = motion != null ? AnimationUtility.CalculateTransformPath(motion, model.transform) : "";
            if (imp.motionNodeName != motionPath)
            {
                imp.motionNodeName = motionPath;
                imp.SaveAndReimport();
                model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            }
            var avatar = AssetDatabase.LoadAllAssetsAtPath(ModelPath).OfType<Avatar>().FirstOrDefault();
            var smr = model.GetComponentInChildren<SkinnedMeshRenderer>();
            motion = FindChild(model.transform, "Motion");
            log.AppendLine($"{Path.GetFileName(ModelPath)}: avatar valid={avatar?.isValid} human={avatar?.isHuman} motion node='{motionPath}' " +
                           $"motion rotation={(motion != null ? motion.rotation.eulerAngles.ToString("F1") : "-")} " +
                           $"bones={smr?.bones.Length} tris={smr?.sharedMesh.triangles.Length / 3} " +
                           $"materials={string.Join("+", smr?.sharedMaterials.Select(m => m != null ? m.name : "null") ?? new string[0])}");
            log.AppendLine("  transforms: " + string.Join(", ", model.GetComponentsInChildren<Transform>(true).Select(t => t.name)));
            return (avatar, motionPath, model);
        }

        static Dictionary<string, AnimationClip> ConfigureClips(Avatar avatar, string motionPath, StringBuilder log)
        {
            var result = new Dictionary<string, AnimationClip>();
            var info = File.Exists(ClipsJson) ? JsonUtility.FromJson<ClipList>(File.ReadAllText(ClipsJson)) : new ClipList();
            var byName = (info.clips ?? Array.Empty<ClipInfo>()).ToDictionary(c => c.name);
            if (byName.Count == 0) log.AppendLine("WARN no clip list " + ClipsJson);
            var lines = new List<string>();
            foreach (var ci in byName.Values)
            {
                string path = $"{Anims}/{Unit}@{ci.name}.fbx";
                var imp = AssetImporter.GetAtPath(path) as ModelImporter;
                if (imp == null)
                {
                    lines.Add(ci.name + ": NO FILE");
                    continue;
                }
                imp.importCameras = false;
                imp.importLights = false;
                imp.materialImportMode = ModelImporterMaterialImportMode.None;
                imp.preserveHierarchy = true;
                imp.animationType = ModelImporterAnimationType.Generic;
                imp.avatarSetup = ModelImporterAvatarSetup.CopyFromOther;
                imp.sourceAvatar = avatar;
                imp.motionNodeName = motionPath;
                imp.importAnimation = true;
                imp.animationCompression = ModelImporterAnimationCompression.KeyframeReduction;
                imp.animationRotationError = 0.1f;
                imp.animationPositionError = 0.1f;
                imp.animationScaleError = 0.1f;
                imp.SaveAndReimport();
                var take = imp.importedTakeInfos.FirstOrDefault();
                if (string.IsNullOrEmpty(take.name))
                {
                    lines.Add(ci.name + ": NO TAKE");
                    continue;
                }
                float length = ci.frames / (float)ci.fps;
                imp.clipAnimations = new[]
                {
                    new ModelImporterClipAnimation
                    {
                        name = ci.name,
                        takeName = take.name,
                        firstFrame = Mathf.Round(take.startTime * take.sampleRate),
                        lastFrame = Mathf.Round(take.stopTime * take.sampleRate),
                        loopTime = ci.loop,
                        lockRootRotation = true, keepOriginalOrientation = true,
                        lockRootHeightY = true, keepOriginalPositionY = true,
                        lockRootPositionXZ = !ci.rootMotion, keepOriginalPositionXZ = true,
                        events = (ci.events ?? Array.Empty<ClipEvent>()).Select(e => new AnimationEvent
                        {
                            time = Mathf.Clamp01(e.time / Mathf.Max(length, 1e-3f)),      // importer events are normalised
                            functionName = EventFunction,
                            stringParameter = e.name,
                        }).ToArray(),
                    },
                };
                imp.SaveAndReimport();
                var clip = AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().FirstOrDefault(c => c.name == ci.name);
                if (clip == null)
                {
                    lines.Add(ci.name + ": MISSING");
                    continue;
                }
                result[ci.name] = clip;
                var ev = AnimationUtility.GetAnimationEvents(clip);
                lines.Add($"{ci.name} {clip.length:0.000}s{(clip.isLooping ? " loop" : "")}" +
                          (ci.rootMotion ? $" rootspeed={clip.averageSpeed.magnitude:0.000}m/s dir={clip.averageSpeed.normalized:F2}" : "") +
                          (ev.Length > 0 ? " events=" + string.Join("/", ev.Select(e => $"{e.stringParameter}@{e.time:0.000}s")) : ""));
            }
            log.AppendLine("clips: " + string.Join("; ", lines));
            return result;
        }

        /// <summary>One state per clip. Idle <-> Move on the bool Moving; Idle -Load-> Load -> IdleLoaded -Throw-> Throw ->
        /// Idle; Idle / Move -Hit-> Hit -> Idle; any state -Destroyed-> Destroyed (held). Load, Throw, Hit and Destroyed
        /// are triggers. Rebuilt in place (the asset and its GUID are kept).</summary>
        static AnimatorController BuildController(Dictionary<string, AnimationClip> clips, StringBuilder log)
        {
            var ctrl = AssetDatabase.LoadAssetAtPath<AnimatorController>(ControllerPath)
                       ?? AnimatorController.CreateAnimatorControllerAtPath(ControllerPath);
            foreach (var p in ctrl.parameters.ToArray()) ctrl.RemoveParameter(p);
            var sm = ctrl.layers[0].stateMachine;
            foreach (var t in sm.anyStateTransitions.ToArray()) sm.RemoveAnyStateTransition(t);
            foreach (var s in sm.states.ToArray()) sm.RemoveState(s.state);
            ctrl.AddParameter("Moving", AnimatorControllerParameterType.Bool);
            foreach (var t in new[] { "Load", "Throw", "Hit", "Destroyed" }) ctrl.AddParameter(t, AnimatorControllerParameterType.Trigger);
            var st = new Dictionary<string, AnimatorState>();
            var pos = new Dictionary<string, Vector3>
            {
                { "Idle", new Vector3(300, 0) }, { "Move", new Vector3(300, -120) }, { "Load", new Vector3(560, 0) },
                { "IdleLoaded", new Vector3(820, 0) }, { "Throw", new Vector3(560, 120) }, { "Hit", new Vector3(300, 120) },
                { "Destroyed", new Vector3(60, 240) },
            };
            foreach (var n in new[] { "Idle", "IdleLoaded", "Move", "Load", "Throw", "Hit", "Destroyed" })
            {
                var s = sm.AddState(n, pos[n]);
                if (clips.TryGetValue(n, out var c)) s.motion = c;
                else log.AppendLine("WARN controller: no clip " + n);
                st[n] = s;
            }
            sm.defaultState = st["Idle"];
            AnimatorStateTransition T(string a, string b, float dur, bool exit)
            {
                var t = st[a].AddTransition(st[b]);
                t.duration = dur;
                t.hasExitTime = exit;
                t.exitTime = exit ? 1f : 0f;
                t.hasFixedDuration = true;
                return t;
            }
            T("Idle", "Move", 0.15f, false).AddCondition(AnimatorConditionMode.If, 0, "Moving");
            T("Move", "Idle", 0.15f, false).AddCondition(AnimatorConditionMode.IfNot, 0, "Moving");
            T("Idle", "Load", 0.1f, false).AddCondition(AnimatorConditionMode.If, 0, "Load");
            T("Load", "IdleLoaded", 0f, true);
            T("IdleLoaded", "Throw", 0f, false).AddCondition(AnimatorConditionMode.If, 0, "Throw");
            T("Throw", "Idle", 0f, true);
            T("Idle", "Hit", 0.05f, false).AddCondition(AnimatorConditionMode.If, 0, "Hit");
            T("Move", "Hit", 0.05f, false).AddCondition(AnimatorConditionMode.If, 0, "Hit");
            T("Hit", "Idle", 0f, true);
            var d = sm.AddAnyStateTransition(st["Destroyed"]);
            d.duration = 0.05f;
            d.hasFixedDuration = true;
            d.canTransitionToSelf = false;
            d.AddCondition(AnimatorConditionMode.If, 0, "Destroyed");
            EditorUtility.SetDirty(ctrl);
            log.AppendLine($"controller: {ControllerPath} states={string.Join(",", sm.states.Select(s => s.state.name))} " +
                           $"parameters={string.Join(",", ctrl.parameters.Select(p => p.name))}");
            return ctrl;
        }

        static GameObject BuildStone(Dictionary<string, Material> mats, StringBuilder log)
        {
            var imp = AssetImporter.GetAtPath(StoneModelPath) as ModelImporter;
            if (imp == null)
            {
                log.AppendLine("WARN no " + StoneModelPath);
                return null;
            }
            imp.globalScale = 1f;
            imp.useFileScale = true;
            imp.bakeAxisConversion = false;              // written the kit's way: Unity vertex = (-x, z, -y), no root turn
            imp.importNormals = ModelImporterNormals.Import;
            imp.importTangents = ModelImporterTangents.Import;
            imp.isReadable = false;
            imp.importCameras = false;
            imp.importLights = false;
            imp.animationType = ModelImporterAnimationType.None;
            imp.importAnimation = false;
            imp.materialImportMode = ModelImporterMaterialImportMode.None;
            imp.SaveAndReimport();
            var mesh = AssetDatabase.LoadAllAssetsAtPath(StoneModelPath).OfType<Mesh>().FirstOrDefault();
            if (mesh == null)
            {
                log.AppendLine("WARN no mesh in " + StoneModelPath);
                return null;
            }
            var go = new GameObject("VKU_CatapultStone");
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = go.AddComponent<MeshRenderer>();
            mats.TryGetValue("M_VKI_StoneBlockIn", out var sm);
            mr.sharedMaterial = sm;
            var col = go.AddComponent<SphereCollider>();
            col.center = mesh.bounds.center;
            col.radius = mesh.bounds.extents.magnitude / Mathf.Sqrt(3f);
            var rb = go.AddComponent<Rigidbody>();
            rb.mass = 45f;                                // a 0.32 m field stone
            rb.interpolation = RigidbodyInterpolation.Interpolate;
            rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
            float radius = col.radius;                   // read before the scene object goes
            var prefab = PrefabUtility.SaveAsPrefabAsset(go, StonePrefabPath);
            Object.DestroyImmediate(go);
            log.AppendLine($"stone: {StonePrefabPath} tris={mesh.triangles.Length / 3} radius={radius:0.000} bounds={mesh.bounds.size:F3}");
            return prefab;
        }

        /// <summary>Throw sampled around its Release event: the socket's position and forward (the launch direction),
        /// the Stone bone's scale (1 = in the cup, ~0 = gone) just before and at the event.</summary>
        static void CheckSocket(GameObject prefab, Dictionary<string, AnimationClip> clips, StringBuilder log)
        {
            if (!clips.TryGetValue("Throw", out var throwClip)) return;
            var ev = AnimationUtility.GetAnimationEvents(throwClip).FirstOrDefault(e => e.stringParameter == "Release");
            if (ev == null)
            {
                log.AppendLine("WARN Throw has no Release event");
                return;
            }
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
            try
            {
                var sock = FindChild(go.transform, "Socket_Projectile");
                var stone = FindChild(go.transform, "Stone");
                foreach (var t in new[] { ev.time - 1f / 30f, ev.time })
                {
                    throwClip.SampleAnimation(go, t);
                    log.AppendLine($"  Throw @{t:0.000}s: socket pos={sock.position:F3} forward={sock.forward:F3} " +
                                   $"elevation={Mathf.Asin(Mathf.Clamp(sock.forward.y, -1f, 1f)) * Mathf.Rad2Deg:0.0}deg stone scale={stone.lossyScale.x:0.000}");
                }
                if (clips.TryGetValue("Move", out var move))
                {
                    var m = FindChild(go.transform, "Motion");
                    move.SampleAnimation(go, 0f);
                    var p0 = m.localPosition;
                    move.SampleAnimation(go, move.length);
                    log.AppendLine($"  Move: Motion travels {(m.localPosition - p0).magnitude:0.000} m a loop ({(m.localPosition - p0).normalized:F2} local)");
                }
            }
            finally
            {
                Object.DestroyImmediate(go);
            }
        }

        // ------------------------------------------------------------------------------------------------ renders
        static void RenderLineup(GameObject prefab, GameObject charred, GameObject stone, Dictionary<string, AnimationClip> clips, StringBuilder log)
        {
            var scene = EditorSceneManager.NewPreviewScene();
            bool async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            try
            {
                void Add(GameObject g) => SceneManager.MoveGameObjectToScene(g, scene);
                var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
                Add(ground);
                ground.transform.localScale = new Vector3(6f, 1f, 4f);
                var gm = new Material(GraphicsSettings.currentRenderPipeline != null
                    ? GraphicsSettings.currentRenderPipeline.defaultShader : Shader.Find("Standard"));
                gm.color = new Color(0.40f, 0.38f, 0.26f);
                if (gm.HasProperty("_BaseColor")) gm.SetColor("_BaseColor", gm.color);
                ground.GetComponent<Renderer>().sharedMaterial = gm;
                var sun = new GameObject("Sun").AddComponent<Light>();
                Add(sun.gameObject);
                sun.type = LightType.Directional;
                sun.intensity = 1.6f;
                sun.shadows = LightShadows.Soft;
                sun.transform.rotation = Quaternion.Euler(55, 200, 0);
                ThrowTimes(clips, out float release, out float slam);
                var poses = new (string clip, float t, bool charred)[]
                {
                    ("Idle", 0f, false), ("IdleLoaded", 0f, false), ("Load", 2.0f, false), ("Throw", release, false),
                    ("Throw", slam + 0.1f, false), ("Move", 0.5f, false), ("Destroyed", 99f, false), ("Destroyed", 99f, true),
                };
                const float spacing = 4.2f;
                float x0 = -(poses.Length - 1) * 0.5f * spacing;
                for (int i = 0; i < poses.Length; i++)
                {
                    var src = poses[i].charred && charred != null ? charred : prefab;
                    var go = (GameObject)PrefabUtility.InstantiatePrefab(src, scene);
                    go.transform.SetPositionAndRotation(new Vector3(x0 + i * spacing, 0, 0), Quaternion.Euler(0, 200f, 0));
                    if (clips.TryGetValue(poses[i].clip, out var c)) c.SampleAnimation(go, Mathf.Min(poses[i].t, c.length));
                    foreach (var smr in go.GetComponentsInChildren<SkinnedMeshRenderer>()) smr.forceMatrixRecalculationPerRender = true;
                }
                if (stone != null)
                {
                    var s = (GameObject)PrefabUtility.InstantiatePrefab(stone, scene);
                    s.transform.position = new Vector3(x0 - 2.4f, 0.17f, -1.5f);
                }
                float w = poses.Length * spacing;
                void Shoot(string name, Vector3 at, Vector3 from, float fov, string file, int pw, int ph)
                {
                    var cam = new GameObject(name).AddComponent<Camera>();
                    Add(cam.gameObject);
                    cam.scene = scene;
                    cam.transform.position = from;
                    cam.transform.LookAt(at);
                    cam.fieldOfView = fov;
                    cam.nearClipPlane = 0.05f;
                    cam.farClipPlane = 400f;
                    cam.clearFlags = CameraClearFlags.SolidColor;
                    cam.backgroundColor = new Color(0.47f, 0.52f, 0.58f);
                    Render(cam, file, pw, ph);                   // the first render of fresh skinned meshes can come out
                    Render(cam, file, pw, ph);                   // empty (shadows only): render it twice
                }
                Shoot("CAM_Lineup", new Vector3(0, 1.0f, 0), new Vector3(0, 6f, -w * 0.62f), 40, "lineup.png", 2000, 800);
                Shoot("CAM_Close", new Vector3(x0 + spacing * 3, 1.2f, 0), new Vector3(x0 + spacing * 3 + 4.5f, 3.2f, -6.5f), 40, "throw_close.png", 1200, 900);
                // the RPG camera: 50 deg down, 22 m off (the kit's VKI_CAM; vertical fov 30 ~ lens 38 on 16:9)
                float p = 50f * Mathf.Deg2Rad;
                Shoot("CAM_Game", new Vector3(0, 0.5f, 0), new Vector3(0, 22f * Mathf.Sin(p), -22f * Mathf.Cos(p)), 30, "lineup_game_22m.png", 1920, 1080);
                log.AppendLine($"renders: {LogDir} (lineup: {string.Join(", ", poses.Select(q => q.clip + "@" + q.t.ToString("0.00") + (q.charred ? " charred" : "")))})");
            }
            finally
            {
                ShaderUtil.allowAsyncCompilation = async;
                EditorSceneManager.ClosePreviewScene(scene);
            }
        }

        static void ThrowTimes(Dictionary<string, AnimationClip> clips, out float release, out float slam)
        {
            release = 0.233f;
            slam = 0.333f;
            if (!clips.TryGetValue("Throw", out var c)) return;
            foreach (var e in AnimationUtility.GetAnimationEvents(c))
            {
                if (e.stringParameter == "Release") release = e.time;
                if (e.stringParameter == "Slam") slam = e.time;
            }
        }

        static void Render(Camera cam, string file, int w, int h)
        {
            var rt = new RenderTexture(w, h, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            var req = new RenderPipeline.StandardRequest { destination = rt };
            if (GraphicsSettings.currentRenderPipeline != null && RenderPipeline.SupportsRenderRequest(cam, req))
                RenderPipeline.SubmitRenderRequest(cam, req);
            else
            {
                cam.targetTexture = rt;
                cam.Render();
                cam.targetTexture = null;
            }
            var prev = RenderTexture.active;
            RenderTexture.active = rt;
            var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, w, h), 0, 0);
            tex.Apply();
            RenderTexture.active = prev;
            File.WriteAllBytes(Path.Combine(LogDir, file), tex.EncodeToPNG());
            Object.DestroyImmediate(tex);
            rt.Release();
        }
    }
}
