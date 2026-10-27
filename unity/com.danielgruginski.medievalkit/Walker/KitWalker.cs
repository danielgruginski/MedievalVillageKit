using UnityEngine;
using UnityEngine.AI;

namespace MedievalKit
{
    /// <summary>
    /// The kit's walker: a stand-in body on the level's navmesh with the kit's click-to-move for legs
    /// (<see cref="KitClickToMove"/>) and the kit's camera following it (<see cref="KitCamera"/>: the 50-degree view, the
    /// wheel's zoom, the see-through). What Tools > Medieval Kit > Play From Start Level and Walk This Level use where the
    /// level has a navmesh (KitNavMesh); the WASD stand-in (<see cref="KitTestWalker"/>) elsewhere. A game brings its own
    /// player (MedievalSetting: ClickToMove and GameCamera, the same two with its rules on top). Shows the level's name
    /// and, at the cursor, the way out under it. FULL_PORT_PLAN phase 3b.
    /// </summary>
    public class KitWalker : MonoBehaviour
    {
        KitClickToMove legs;

        /// <summary>a walker at a point (snapped onto the navmesh within 3 m) with its camera; null when there is no
        /// navmesh there</summary>
        public static KitWalker Spawn(Vector3 at, Quaternion facing)
        {
            if (!NavMesh.SamplePosition(at, out var hit, 3f, NavMesh.AllAreas)) return null;
            var go = new GameObject("KitWalker");
            go.SetActive(false);                                    // (the agent placed before it wakes)
            go.transform.SetPositionAndRotation(hit.position, facing);
            var body = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            Destroy(body.GetComponent<Collider>());                 // (the cursor's ray goes past it to the floor)
            body.name = "Body";
            body.transform.SetParent(go.transform, false);
            body.transform.localPosition = new Vector3(0f, 0.9f, 0f);
            body.transform.localScale = new Vector3(0.6f, 0.9f, 0.6f);
            var agent = go.AddComponent<NavMeshAgent>();
            agent.radius = 0.3f; agent.height = 1.8f;
            agent.speed = 4.5f; agent.angularSpeed = 720f; agent.acceleration = 30f;
            agent.stoppingDistance = 0.05f; agent.autoBraking = true;
            var w = go.AddComponent<KitWalker>();
            w.legs = go.AddComponent<KitClickToMove>();
            go.SetActive(true);
            var cam = new GameObject("KitCamera").AddComponent<KitCamera>();
            cam.target = go.transform;
            return w;
        }

        void OnGUI()
        {
            GUI.Label(new Rect(12, 10, 700, 22), $"{KitTravel.CurrentLevel}   (click or hold the left button to walk; click a door to go through; the wheel zooms)");
            var l = legs != null ? legs.Hover : null;
            if (l == null) return;
            var m = Event.current.mousePosition;
            GUI.Label(new Rect(m.x + 18, m.y + 4, 400, 22), $"{(string.IsNullOrEmpty(l.prompt) ? "Go" : l.prompt)}  -> {l.target}");
        }
    }
}
