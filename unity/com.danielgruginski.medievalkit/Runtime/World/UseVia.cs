using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// A collider that stands for a usable thing kept elsewhere: a find's prop (a dead goblin, a chest), whose
    /// <see cref="Lootable"/> sits on the kit's marker (<see cref="LevelDirector"/>). The cursor on the prop is on the find.
    /// </summary>
    [AddComponentMenu("")]
    public class UseVia : MonoBehaviour
    {
        public Interactable thing;

        /// <summary>the usable thing a hit collider is or stands for (null: none)</summary>
        public static Interactable Of(Collider c)
        {
            var i = c.GetComponentInParent<Interactable>();
            if (i != null) return i;
            return c.TryGetComponent<UseVia>(out var via) && via.thing != null ? via.thing : null;
        }
    }
}
