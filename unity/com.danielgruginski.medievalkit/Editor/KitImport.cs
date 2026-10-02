using UnityEditor;
using UnityEngine;

namespace MedievalKit.Editor
{
    /// <summary>Import settings for the exported kit: FBX pieces and their textures (HANDOFF issue 11).</summary>
    public class KitImport : AssetPostprocessor
    {
        static bool InKit(string path, string sub) =>
            path.StartsWith(KitPaths.Package + "/" + sub + "/");

        void OnPreprocessModel()
        {
            if (!InKit(assetPath, "Art/Models")) return;
            var mi = (ModelImporter)assetImporter;
            mi.globalScale = 1f;
            mi.useFileScale = true;
            mi.bakeAxisConversion = false;          // the exporter already baked Blender -> Unity space
            mi.importNormals = ModelImporterNormals.Import;
            mi.importTangents = ModelImporterTangents.Import;
            mi.meshCompression = ModelImporterMeshCompression.Off;
            mi.meshOptimizationFlags = MeshOptimizationFlags.Everything;
            mi.weldVertices = true;
            mi.isReadable = false;
            mi.importBlendShapes = false;
            mi.importVisibility = false;
            mi.importCameras = false;
            mi.importLights = false;
            // Unity orders submeshes its own way, so the FBX's material names are kept (as throwaway embedded
            // materials) and KitBuilder matches each submesh to its kit material by name.
            mi.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;
            mi.materialLocation = ModelImporterMaterialLocation.InPrefab;
            mi.animationType = ModelImporterAnimationType.None;
            mi.importAnimation = false;
            mi.generateSecondaryUV = false;
            mi.addCollider = false;
        }

        void OnPreprocessTexture()
        {
            if (!InKit(assetPath, "Art/Textures")) return;
            var ti = (TextureImporter)assetImporter;
            string n = System.IO.Path.GetFileNameWithoutExtension(assetPath);
            ti.mipmapEnabled = true;
            ti.anisoLevel = 4;
            ti.wrapMode = TextureWrapMode.Repeat;
            ti.textureCompression = TextureImporterCompression.CompressedHQ;
            if (n.Contains("GroundCtl"))
            {
                // per-map ground control: exact data, bilinear, clamped (Blender: Linear, EXTEND)
                ti.textureType = TextureImporterType.Default;
                ti.sRGBTexture = false;
                ti.mipmapEnabled = false;
                ti.wrapMode = TextureWrapMode.Clamp;
                ti.filterMode = FilterMode.Bilinear;
                ti.textureCompression = TextureImporterCompression.Uncompressed;
                ti.npotScale = TextureImporterNPOTScale.None;
                ti.alphaSource = TextureImporterAlphaSource.FromInput;
                ti.alphaIsTransparency = false;
                return;
            }
            if (n.Contains("TerrainMacro"))
            {
                ti.textureType = TextureImporterType.Default;
                ti.sRGBTexture = false;
                return;
            }
            if (n.EndsWith("_N"))
            {
                ti.textureType = TextureImporterType.NormalMap;
                ti.sRGBTexture = false;
            }
            else if (n.EndsWith("_R") || n.EndsWith("_Roughness") || n.EndsWith("_Mask") || n.EndsWith("_H"))
            {
                ti.textureType = TextureImporterType.Default;
                ti.sRGBTexture = false;
                ti.alphaSource = TextureImporterAlphaSource.None;
            }
            else
            {
                ti.textureType = TextureImporterType.Default;
                ti.sRGBTexture = true;
                ti.alphaSource = TextureImporterAlphaSource.FromInput;
                ti.alphaIsTransparency = n.EndsWith("_BCA") || n.Contains("Foliage") || n.Contains("Leaves") || n.Contains("Web");
                ti.mipMapsPreserveCoverage = ti.alphaIsTransparency;   // cut-outs keep their coverage in the distance
                ti.alphaTestReferenceValue = 0.5f;
            }
        }
    }

    public static class KitPaths
    {
        public const string Package = "Packages/com.danielgruginski.medievalkit";
        public const string Data = Package + "/Data";
        public const string Textures = Package + "/Art/Textures";
        public const string Generated = Package + "/Generated";
        public const string Materials = Generated + "/Materials";
        public const string Prefabs = Generated + "/Prefabs";
        public const string Levels = Generated + "/Levels";
        public const string Shader = "MedievalKit/KitLit";
        public const string TerrainShader = "MedievalKit/KitTerrain";
    }
}
