using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// A way out of a level: a door, a stair, a passage, a lift. Its trigger is the area where a walker can take it,
    /// facing it within facingMin degrees (vki_trigger / vki_facing_min from Blender). Put one on any piece by hand to
    /// link a building you made yourself: set target to a level name (or "@return") and give the target level a
    /// KitSpawn whose spawnId is where walkers arrive.
    /// </summary>
    public class KitLink : MonoBehaviour
    {
        public string linkId;
        public string kind = "exit";
        public string target;
        [Tooltip("The spawn id in the target level; empty = the target's only link back to this level.")]
        public string arrive;
        public string prompt = "Enter";
        [Tooltip("The walker must face the link within this angle (degrees). 0 = any direction.")]
        public float facingMin = 60f;
        [Tooltip("Taken by walking into its trigger (a road's end at the map's edge), not by using it (doors, stairs).")]
        public bool walkInto;

        public bool CanUse(Transform walker)
        {
            if (facingMin <= 0f) return true;
            Vector3 to = transform.position - walker.position;
            to.y = 0f;
            if (to.sqrMagnitude < 1e-4f) return true;
            return Vector3.Angle(walker.forward, to) <= facingMin;
        }

        public void Use() => KitTravel.Go(this);

        void OnDrawGizmosSelected()
        {
            Gizmos.color = new Color(1f, 0.8f, 0.2f, 0.5f);
            foreach (var c in GetComponents<BoxCollider>())
                if (c.isTrigger)
                {
                    Gizmos.matrix = transform.localToWorldMatrix;
                    Gizmos.DrawCube(c.center, c.size);
                }
        }
    }
}
