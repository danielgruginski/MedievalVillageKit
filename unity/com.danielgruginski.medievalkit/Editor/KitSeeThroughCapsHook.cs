using UnityEditor;

namespace MedievalKit.Editor
{
    /// <summary>
    /// Makes the see-through's queued caps in play mode (<see cref="KitSeeThroughCaps.Flush"/>), between frames: the kit's
    /// meshes are not Read/Write, and in play mode only editor code may read them. Since 2026-10-14 the caps come baked
    /// (<see cref="KitSeeThroughCapsBake"/>, also before every player build); this makes only what the bake lacks (a piece
    /// changed or added since).
    /// </summary>
    [InitializeOnLoad]
    static class KitSeeThroughCapsHook
    {
        static KitSeeThroughCapsHook()
        {
            // a material the level does not use (the end grain on a map without stumps): from the package
            KitSeeThroughCaps.FindMaterial = name =>
            {
                foreach (var g in AssetDatabase.FindAssets(name + " t:Material", new[] { "Packages/com.danielgruginski.medievalkit" }))
                {
                    var p = AssetDatabase.GUIDToAssetPath(g);
                    if (System.IO.Path.GetFileNameWithoutExtension(p) == name) return AssetDatabase.LoadAssetAtPath<UnityEngine.Material>(p);
                }
                return null;
            };
            EditorApplication.update += () =>
            {
                if (EditorApplication.isPlaying && KitSeeThroughCaps.Pending > 0) KitSeeThroughCaps.Flush();
            };
        }
    }
}
