using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace MedievalKit
{
    /// <summary>
    /// Grass blades made on the GPU (KitVillage writes the clump list: where each clump stands, its tint and height;
    /// 16 bytes a clump). The list goes to the GPU once; each frame, for each camera, a compute shader (KitGrassCull)
    /// keeps the clumps in its view and one indirect draw grows them: the vertex shader (KitGrass) builds each clump's
    /// 5-7 blades from its index, sways them in the wind and parts them round the walker. No blade meshes exist, so
    /// nothing is grown at load and nothing is held in memory but the list. Positions are this object's local space,
    /// which is the ground's object space (the shader reads the ground's grass colour under each blade).
    /// Needs compute shaders (any desktop or console GPU, Metal, Vulkan, D3D11+).
    /// </summary>
    [ExecuteAlways]
    public class KitGrass : MonoBehaviour
    {
        public Material material;
        [Tooltip("Clumps, 16 bytes each: x, y, z (float, local), then tint r, g, b and height (bytes).")]
        [HideInInspector] public byte[] clumps;
        [Tooltip("The clumps' bounds in local space (KitVillage sets it).")]
        public Bounds localBounds;
        public float minHeight = 0.3f, maxHeight = 0.58f;
        public int seed = 1;
        public bool castShadows = true;
        [Tooltip("Clumps farther than this from the camera are not drawn (m).")]
        public float reach = 90f;

        public const int MaxBlades = 7, VertsPerBlade = 9;          // 3 triangles a blade, unindexed
        public int Clumps => clumps == null ? 0 : clumps.Length / 16;

        ComputeShader cull;
        int kernel;
        GraphicsBuffer clumpBuf;
        MaterialPropertyBlock mpb;
        readonly Dictionary<Camera, (GraphicsBuffer visible, GraphicsBuffer args)> perCam = new Dictionary<Camera, (GraphicsBuffer, GraphicsBuffer)>();
        readonly Vector4[] planes = new Vector4[6];
        readonly Plane[] fr = new Plane[6];

        static readonly int IdClumps = Shader.PropertyToID("_Clumps"), IdVisible = Shader.PropertyToID("_Visible"),
            IdO2W = Shader.PropertyToID("_ObjectToWorld"), IdPlanes = Shader.PropertyToID("_Planes"), IdCam = Shader.PropertyToID("_Cam"),
            IdCount = Shader.PropertyToID("_Count"), IdGClumps = Shader.PropertyToID("_GrassClumps"),
            IdGVisible = Shader.PropertyToID("_GrassVisible"), IdGO2W = Shader.PropertyToID("_GrassObjectToWorld"),
            IdGParams = Shader.PropertyToID("_GrassParams");

        /// <summary>pack a clump (KitVillage)</summary>
        public static void Write(List<byte> into, Vector3 p, Color tint, float tall01)
        {
            into.AddRange(System.BitConverter.GetBytes(p.x));
            into.AddRange(System.BitConverter.GetBytes(p.y));
            into.AddRange(System.BitConverter.GetBytes(p.z));
            into.Add((byte)Mathf.Clamp(Mathf.RoundToInt(tint.r * 200f), 0, 255));
            into.Add((byte)Mathf.Clamp(Mathf.RoundToInt(tint.g * 200f), 0, 255));
            into.Add((byte)Mathf.Clamp(Mathf.RoundToInt(tint.b * 200f), 0, 255));
            into.Add((byte)Mathf.Clamp(Mathf.RoundToInt(tall01 * 255f), 0, 255));
        }

        void OnEnable()
        {
            if (!SystemInfo.supportsComputeShaders || Clumps == 0 || material == null) return;
            cull = Resources.Load<ComputeShader>("KitGrassCull");
            if (cull == null) { Debug.LogWarning("[KitGrass] no KitGrassCull compute shader"); return; }
            kernel = cull.FindKernel("Cull");
            var words = new uint[Clumps * 4];
            System.Buffer.BlockCopy(clumps, 0, words, 0, Clumps * 16);
            clumpBuf = new GraphicsBuffer(GraphicsBuffer.Target.Structured, words.Length, 4);
            clumpBuf.SetData(words);
            mpb = new MaterialPropertyBlock();
            RenderPipelineManager.beginCameraRendering += Draw;
        }

        void OnDisable()
        {
            RenderPipelineManager.beginCameraRendering -= Draw;
            clumpBuf?.Release(); clumpBuf = null;
            foreach (var b in perCam.Values) { b.visible.Release(); b.args.Release(); }
            perCam.Clear();
        }

        void Draw(ScriptableRenderContext ctx, Camera cam)
        {
            if (clumpBuf == null || cam == null || cam.cameraType == CameraType.Preview || cam.cameraType == CameraType.Reflection) return;
            if (!perCam.TryGetValue(cam, out var b))
            {
                foreach (var dead in new List<Camera>(perCam.Keys))
                    if (dead == null) { perCam[dead].visible.Release(); perCam[dead].args.Release(); perCam.Remove(dead); }
                b = (new GraphicsBuffer(GraphicsBuffer.Target.Append, Clumps, 4),
                     new GraphicsBuffer(GraphicsBuffer.Target.IndirectArguments, 1, GraphicsBuffer.IndirectDrawArgs.size));
                b.args.SetData(new[] { new GraphicsBuffer.IndirectDrawArgs { vertexCountPerInstance = MaxBlades * VertsPerBlade } });
                perCam[cam] = b;
            }
            var o2w = transform.localToWorldMatrix;
            GeometryUtility.CalculateFrustumPlanes(cam, fr);
            for (int i = 0; i < 6; i++) planes[i] = new Vector4(fr[i].normal.x, fr[i].normal.y, fr[i].normal.z, fr[i].distance);
            b.visible.SetCounterValue(0);
            cull.SetBuffer(kernel, IdClumps, clumpBuf);
            cull.SetBuffer(kernel, IdVisible, b.visible);
            cull.SetMatrix(IdO2W, o2w);
            cull.SetVectorArray(IdPlanes, planes);
            var cp = cam.transform.position;
            cull.SetVector(IdCam, new Vector4(cp.x, cp.y, cp.z, reach));
            cull.SetInt(IdCount, Clumps);
            cull.Dispatch(kernel, (Clumps + 63) / 64, 1, 1);
            GraphicsBuffer.CopyCount(b.visible, b.args, sizeof(uint));          // -> instanceCount

            mpb.SetBuffer(IdGClumps, clumpBuf);
            mpb.SetBuffer(IdGVisible, b.visible);
            mpb.SetMatrix(IdGO2W, o2w);
            mpb.SetVector(IdGParams, new Vector4(minHeight, maxHeight, seed, 0));
            var wb = GeometryUtility.CalculateBounds(new[]
            {
                localBounds.min, localBounds.max, new Vector3(localBounds.min.x, localBounds.max.y, localBounds.max.z),
                new Vector3(localBounds.max.x, localBounds.min.y, localBounds.min.z)
            }, o2w);
            wb.Expand(3f);
            var rp = new RenderParams(material)
            {
                worldBounds = wb, camera = cam, matProps = mpb, layer = gameObject.layer, receiveShadows = true,
                shadowCastingMode = castShadows ? ShadowCastingMode.On : ShadowCastingMode.Off,
            };
            Graphics.RenderPrimitivesIndirect(rp, MeshTopology.Triangles, b.args, 1);
        }
    }
}
