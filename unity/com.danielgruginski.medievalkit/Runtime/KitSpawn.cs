using UnityEngine;

namespace MedievalKit
{
    /// <summary>Where a walker arrives through the link of the same id (Blender's SPN_&lt;id&gt; empties).</summary>
    public class KitSpawn : MonoBehaviour
    {
        public string spawnId;
        [Tooltip("Blender bearing: 0 = Blender +Y, 90 = Blender +X (the builder turns it into this transform's rotation).")]
        public float facingDeg;

        /// <summary>Blender bearing -> Unity rotation (Blender +Y is Unity -Z, +X is Unity -X).</summary>
        public static Quaternion FromBearing(float deg)
        {
            float r = deg * Mathf.Deg2Rad;
            return Quaternion.LookRotation(new Vector3(-Mathf.Sin(r), 0f, -Mathf.Cos(r)), Vector3.up);
        }

        void OnDrawGizmos()
        {
            Gizmos.color = Color.cyan;
            Gizmos.DrawWireSphere(transform.position + Vector3.up * 0.9f, 0.35f);
            Gizmos.DrawRay(transform.position + Vector3.up * 0.9f, transform.forward * 0.8f);
        }
    }
}
