using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// Where a generated map opens into the next one (<see cref="KitPortal"/>): it sits on the middle of the opening on
    /// the map's edge, its forward pointing out of the map. A chain lines the next piece up by putting its own marker
    /// for the facing side on this one's position; the streamer watches the walker against them.
    /// </summary>
    public class KitPortalMarker : MonoBehaviour
    {
        public string portalId;
        [Tooltip("N, S, E or W: the map edge the opening is on.")]
        public string side;
        [Tooltip("The opening's first cell along the edge and its width in cells.")]
        public int at, width = 2;
        public string target;
        [Tooltip("A connector's end (the neighbour builds the seam's rock).")]
        public bool seam;

        void OnDrawGizmos()
        {
            Gizmos.color = seam ? new Color(0.3f, 0.8f, 1f, 0.8f) : new Color(1f, 0.6f, 0.1f, 0.8f);
            var w = width * 1.5f;
            Gizmos.matrix = transform.localToWorldMatrix;
            Gizmos.DrawWireCube(new Vector3(0f, 1.2f, 0f), new Vector3(w, 2.4f, 0.1f));
            Gizmos.DrawLine(new Vector3(0f, 0.1f, 0f), new Vector3(0f, 0.1f, 1.2f));
        }
    }
}
