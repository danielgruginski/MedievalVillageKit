using UnityEngine;
using UnityEngine.AI;

namespace MedievalKit
{
    /// <summary>
    /// A level's walkable surface for NavMeshAgents (a click-to-move player, monsters): the NavMeshData the kit's tools
    /// bake (KitNavBake: outdoor maps, rooms and chains when they are built; Tools > Medieval Kit > Navigation for scenes
    /// made before), added while this is enabled and removed when it is not, so a level held switched off by
    /// <see cref="KitTravel.Preload"/> takes its surface with it. A chain's play scene carries one surface over all its
    /// pieces: paths run on into pieces not streamed in yet.
    /// </summary>
    public class KitNavMesh : MonoBehaviour
    {
        public NavMeshData data;
        NavMeshDataInstance instance;

        /// <summary>the kit's walker on the project's default agent type (id 0, so a NavMeshAgent left on its default type
        /// walks it): radius 0.3 (the kit's 0.84 m doors), height 1.8, step 0.35, slope 40; 0.05 m voxels indoors and in
        /// caves (narrow doors and openings), 0.1 m on outdoor maps</summary>
        public static NavMeshBuildSettings Settings(float voxel = 0.05f)
        {
            var s = NavMesh.GetSettingsByID(0);
            s.agentRadius = 0.3f; s.agentHeight = 1.8f; s.agentClimb = 0.35f; s.agentSlope = 40f;
            s.overrideVoxelSize = true; s.voxelSize = voxel;
            return s;
        }

        void OnEnable()
        {
            if (data != null) instance = NavMesh.AddNavMeshData(data, transform.position, transform.rotation);
        }

        void OnDisable()
        {
            if (instance.valid) NavMesh.RemoveNavMeshData(instance);
            instance = default;
        }
    }
}
