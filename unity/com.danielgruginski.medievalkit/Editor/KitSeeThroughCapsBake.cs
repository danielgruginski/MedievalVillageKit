using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace MedievalKit.Editor
{
    /// <summary>
    /// Bakes the see-through's caps (2026-10-14, spike round 3; <see cref="KitSeeThroughCapBank"/>): opens each level of the
    /// build that has a <see cref="KitVillage"/> (additively, closed again unsaved), asks it which caps its pieces need
    /// (<see cref="KitVillage.SetUpSeeThrough"/> with <see cref="KitSeeThroughCaps.Collecting"/> set; every renderer's
    /// rendering layers are put back), makes each cap mesh once (<see cref="KitSeeThroughCaps.MakeCap"/>: only editor code
    /// may read the kit's meshes) and keeps them in the bank asset (Resources "KitSeeThroughCaps"; a new one goes to
    /// Assets/Resources). Tools > Medieval Kit > Bake See-through Caps (always bakes anew: after a change to the cap code),
    /// and before every player build (a build without them would show the cuts uncapped) -- there a bank that already
    /// holds exactly the caps needed, none stale, is left as it is (a bake rewrites the asset: the build would leave it
    /// changed in version control every time).
    /// </summary>
    public sealed class KitSeeThroughCapsBake : IPreprocessBuildWithReport
    {
        public const string DefaultPath = "Assets/Resources/" + KitSeeThroughCapBank.ResourceName + ".asset";

        public int callbackOrder => 0;

        public void OnPreprocessBuild(BuildReport report)
        {
            try { Debug.Log("[KitSeeThroughCapsBake] before the build: " + Bake(force: false)); }
            catch (System.Exception e) { Debug.LogWarning("[KitSeeThroughCapsBake] the caps were not baked: " + e); }
        }

        [MenuItem("Tools/Medieval Kit/Bake See-through Caps")]
        static void Menu()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode) { Debug.LogWarning("[KitSeeThroughCapsBake] not while playing"); return; }
            Debug.Log("[KitSeeThroughCapsBake] " + Bake(force: true));
        }

        /// <summary>bake the caps of these scenes' levels (default: the build's enabled scenes) into the bank (the one in the
        /// project, else a new one at `bankPath` or <see cref="DefaultPath"/>); not `force`d, a bank already holding exactly
        /// those caps (<see cref="Current"/>) is left untouched; returns a report</summary>
        public static string Bake(IEnumerable<string> scenes = null, string bankPath = null, bool force = true)
        {
            float t0 = Time.realtimeSinceStartup;
            scenes ??= EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToList();
            string guid = VillageScriptGuid();
            var keys = new HashSet<(Mesh, int, uint, uint)>();
            int levels = 0, villages = 0;
            foreach (var path in scenes)
            {
                if (string.IsNullOrEmpty(path) || !File.Exists(path)) continue;
                if (guid != null && !File.ReadAllText(path).Contains(guid)) continue;      // no KitVillage in it
                var scene = SceneManager.GetSceneByPath(path);
                bool wasOpen = scene.IsValid() && scene.isLoaded;
                if (!wasOpen) scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Additive);
                try
                {
                    var roots = scene.GetRootGameObjects();
                    var vs = roots.SelectMany(g => g.GetComponentsInChildren<KitVillage>(true)).ToList();
                    if (vs.Count == 0) continue;
                    levels++;
                    var masks = roots.SelectMany(g => g.GetComponentsInChildren<Renderer>(true)).Select(r => (r, r.renderingLayerMask)).ToList();
                    KitSeeThroughCaps.Collecting = keys;
                    try { foreach (var v in vs) { v.SetUpSeeThrough(); villages++; } }
                    finally
                    {
                        KitSeeThroughCaps.Collecting = null;
                        foreach (var (r, m) in masks) if (r != null) r.renderingLayerMask = m;
                    }
                }
                finally { if (!wasOpen) EditorSceneManager.CloseScene(scene, true); }
            }

            var bank = FindBank();
            if (!force && bank != null && Current(bank, keys))
                return $"{levels} levels ({villages} KitVillage), {keys.Count} caps needed: the bank has them all, none stale " +
                       $"(left as it is), {(Time.realtimeSinceStartup - t0):F1} s -> {AssetDatabase.GetAssetPath(bank)}";
            bank ??= CreateBank(bankPath ?? DefaultPath);
            var path_ = AssetDatabase.GetAssetPath(bank);
            foreach (var o in AssetDatabase.LoadAllAssetsAtPath(path_))
                if (o is Mesh) { AssetDatabase.RemoveObjectFromAsset(o); Object.DestroyImmediate(o, true); }
            bank.entries.Clear();
            int made = 0, empty = 0, failed0 = KitSeeThroughCaps.Failed, tris = 0;
            foreach (var (mesh, q, solid, bark) in keys.OrderBy(k => k.Item1.name).ThenBy(k => k.Item2))
            {
                var cap = KitSeeThroughCaps.MakeCap(mesh, q, solid, bark);
                var e = new KitSeeThroughCapBank.Entry
                {
                    source = mesh, q = q, solid = solid, bark = bark, vertexCount = mesh.vertexCount, bounds = mesh.bounds,
                    mats = cap.mats ?? new int[0], grain = cap.grain ?? new bool[0], area = cap.area,
                };
                if (cap.mesh != null)
                {
                    cap.mesh.name = $"{mesh.name}_q{q}_{solid:x}_Cap";
                    AssetDatabase.AddObjectToAsset(cap.mesh, bank);
                    e.cap = cap.mesh;
                    for (int s = 0; s < cap.mesh.subMeshCount; s++) tris += (int)cap.mesh.GetIndexCount(s) / 3;
                    made++;
                }
                else empty++;
                bank.entries.Add(e);
            }
            bank.materials = new List<Material>();
            foreach (var n in new[] { "M_VK_EndGrain", "M_VK_Planks", "M_VK_Wood" })
            {
                var m = KitSeeThroughCaps.FindMaterial?.Invoke(n);
                if (m != null) bank.materials.Add(m);
            }
            string report = $"{levels} levels ({villages} KitVillage), {keys.Count} caps needed: {made} cap meshes ({tris} triangles), " +
                            $"{empty} sections empty, {KitSeeThroughCaps.Failed - failed0} polygons not filled, " +
                            $"{(Time.realtimeSinceStartup - t0):F1} s -> {path_}";
            bank.report = $"{System.DateTime.Now:yyyy-MM-dd HH:mm} {report}";
            EditorUtility.SetDirty(bank);
            AssetDatabase.SaveAssets();
            KitSeeThroughCaps.ResetBank();
            return report;
        }

        /// <summary>the bank holds exactly these keys, each from its source mesh as it is now (vertex count, bounds:
        /// <see cref="KitSeeThroughCaps"/>' own staleness test)</summary>
        static bool Current(KitSeeThroughCapBank bank, HashSet<(Mesh, int, uint, uint)> keys)
        {
            if (bank.entries.Count != keys.Count) return false;
            foreach (var e in bank.entries)
            {
                if (e.source == null || !keys.Contains((e.source, e.q, e.solid, e.bark))) return false;
                if (e.source.vertexCount != e.vertexCount || (e.source.bounds.center - e.bounds.center).sqrMagnitude >= 1e-8f ||
                    (e.source.bounds.size - e.bounds.size).sqrMagnitude >= 1e-8f) return false;
            }
            return true;
        }

        static string VillageScriptGuid()
        {
            foreach (var g in AssetDatabase.FindAssets("KitVillage t:MonoScript"))
                if (Path.GetFileName(AssetDatabase.GUIDToAssetPath(g)) == "KitVillage.cs") return g;
            return null;
        }

        static KitSeeThroughCapBank FindBank()
        {
            foreach (var g in AssetDatabase.FindAssets("t:KitSeeThroughCapBank"))
            {
                var b = AssetDatabase.LoadAssetAtPath<KitSeeThroughCapBank>(AssetDatabase.GUIDToAssetPath(g));
                if (b != null && b.name == KitSeeThroughCapBank.ResourceName) return b;
            }
            return null;
        }

        static KitSeeThroughCapBank CreateBank(string path)
        {
            var dir = Path.GetDirectoryName(path)?.Replace('\\', '/');
            if (!string.IsNullOrEmpty(dir) && !AssetDatabase.IsValidFolder(dir))
            {
                var parts = dir.Split('/');
                string cur = parts[0];
                for (int i = 1; i < parts.Length; i++)
                {
                    if (!AssetDatabase.IsValidFolder(cur + "/" + parts[i])) AssetDatabase.CreateFolder(cur, parts[i]);
                    cur += "/" + parts[i];
                }
            }
            var bank = ScriptableObject.CreateInstance<KitSeeThroughCapBank>();
            AssetDatabase.CreateAsset(bank, path);
            return bank;
        }
    }
}
