using UnityEditor;

namespace MedievalKit.Editor
{
    /// <summary>
    /// Makes the see-through's queued caps in play mode (<see cref="KitSeeThroughCaps.Flush"/>), between frames: the kit's
    /// meshes are not Read/Write, and in play mode only editor code may read them. Prototype (2026-10-13); a player build
    /// would need the caps baked.
    /// </summary>
    [InitializeOnLoad]
    static class KitSeeThroughCapsHook
    {
        static KitSeeThroughCapsHook()
        {
            EditorApplication.update += () =>
            {
                if (EditorApplication.isPlaying && KitSeeThroughCaps.Pending > 0) KitSeeThroughCaps.Flush();
            };
        }
    }
}
