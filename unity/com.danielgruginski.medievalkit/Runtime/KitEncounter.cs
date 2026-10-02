using System.Collections.Generic;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// Where a fight happens: a room of a generated dungeon (or one placed by hand), the creature tag the game should
    /// spawn there ("goblin", "rat", "undead", "bandit", "cultist", "boss"...), a difficulty budget (1 + the room's depth
    /// from the entrance; the lair more), and spawn points (its children). The kit only marks them: the game decides
    /// what a tag and a budget turn into, and when the encounter wakes (on entering `size`, on sight...).
    /// </summary>
    public class KitEncounter : MonoBehaviour
    {
        public string encounterId;
        public string roomType;
        public string creature;
        public int budget = 1;
        public int depth;
        public bool boss;
        [Tooltip("The room's area (local, centred on this transform), e.g. for a wake-up trigger.")]
        public Vector3 size = new Vector3(4.5f, 3f, 4.5f);

        public IEnumerable<Transform> Points
        {
            get { foreach (Transform t in transform) yield return t; }
        }

        void OnDrawGizmos()
        {
            Gizmos.color = boss ? new Color(1f, 0.2f, 0.1f, 0.9f) : new Color(1f, 0.5f, 0.1f, 0.7f);
            Gizmos.matrix = transform.localToWorldMatrix;
            Gizmos.DrawWireCube(new Vector3(0f, size.y / 2f, 0f), size);
            Gizmos.matrix = Matrix4x4.identity;
            foreach (var p in Points) Gizmos.DrawSphere(p.position + Vector3.up * 0.5f, boss ? 0.35f : 0.25f);
        }
    }
}
