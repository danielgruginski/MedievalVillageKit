#if TOOLS
using Godot;

namespace MedievalKit.Editor;

/// <summary>Runs on every kit piece's .glb (gdx_export.py names it in each .glb.import).
/// Shadows come from both faces, as Blender casts them: the one-sided materials cull what the camera sees, not what the
/// sun sees (an open-backed piece turned away from the sun would let light through otherwise). Every surface must have
/// taken its material from the shared library (res://kit/materials/, mapped by name).</summary>
[Tool]
public partial class KitImport : EditorScenePostImport
{
    public override GodotObject _PostImport(Node scene)
    {
        foreach (var n in scene.FindChildren("*", "MeshInstance3D", true, false))
        {
            var mi = (MeshInstance3D)n;
            mi.CastShadow = GeometryInstance3D.ShadowCastingSetting.DoubleSided;
            for (int s = 0; s < mi.Mesh.GetSurfaceCount(); s++)
            {
                var m = mi.Mesh.SurfaceGetMaterial(s);
                if (m == null || !m.ResourcePath.StartsWith(KitPaths.Materials))
                    GD.PushWarning($"{GetSourceFile()}: surface {s} has no library material ({m})");
            }
        }
        return scene;
    }
}
#endif
