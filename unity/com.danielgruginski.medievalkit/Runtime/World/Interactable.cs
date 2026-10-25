using System.Collections.Generic;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// Something in the world the player clicks to use: a corpse or a find to loot, someone to talk to, a campfire, a
    /// sign. The click walks the player to <see cref="UsePoint"/> and calls <see cref="Use"/> on arrival (ClickToMove).
    /// The HUD reads the rest: the hover label, a name plate and its badge, a sign's bubble, a loot glint.
    /// </summary>
    public abstract class Interactable : MonoBehaviour
    {
        public enum CursorKind { Use, Loot, Talk, Look }

        public static readonly List<Interactable> All = new List<Interactable>();

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        static void ResetAll() => All.Clear();

        protected virtual void OnEnable() => All.Add(this);
        protected virtual void OnDisable() => All.Remove(this);

        /// <summary>the hover text ("Rat corpse - loot", "Mara the Trader - talk")</summary>
        public abstract string Label { get; }
        public virtual CursorKind Cursor => CursorKind.Use;
        /// <summary>wins over others under the same click (talk 30, loot 20, campfire 10, sign 0)</summary>
        public virtual int Priority => 0;
        /// <summary>where the player walks to use it</summary>
        public virtual Vector3 UsePoint => transform.position;
        /// <summary>used once the player is this near <see cref="UsePoint"/> (flat metres)</summary>
        public virtual float UseRadius => 1.5f;
        /// <summary>a ground click this near (flat metres) counts as on it (small things are hard to hit)</summary>
        public virtual float PickRadius => 0.8f;
        /// <summary>can be hovered and used now (an emptied corpse cannot)</summary>
        public virtual bool CanUse => isActiveAndEnabled;
        /// <summary>the player arrived: do it</summary>
        public abstract void Use();

        /// <summary>above it: where the HUD puts its name plate or bubble</summary>
        public virtual Vector3 LabelPoint => transform.position + Vector3.up * 2.1f;
        /// <summary>a name over its head (people), or null</summary>
        public virtual string Nameplate => null;
        /// <summary>" !" when it has news for the player, or null</summary>
        public virtual string Badge => null;
        /// <summary>words shown over it while the player is within <see cref="BubbleRange"/> (signs), or null</summary>
        public virtual string Bubble => null;
        public virtual float BubbleRange => 4f;
        /// <summary>a small gold glint bobbing over it (loot left)</summary>
        public virtual bool Glint => false;

        /// <summary>the best usable thing for a click: the one hit, or the nearest within its pick radius of the ground
        /// point (higher priority first)</summary>
        public static Interactable Under(Collider hit, Vector3 point) => Under(hit, point, out _);

        /// <summary>as <see cref="Under(Collider, Vector3)"/>, and how far (flat metres) it is from the point</summary>
        public static Interactable Under(Collider hit, Vector3 point, out float off)
        {
            off = 0f;
            if (hit != null)
            {
                var direct = UseVia.Of(hit);
                if (direct != null && direct.CanUse) return direct;
            }
            Interactable best = null; float bestScore = float.MaxValue;
            foreach (var i in All)
            {
                if (!i.CanUse) continue;
                var d = i.transform.position - point; d.y = 0f;
                float m = d.magnitude;
                if (m > i.PickRadius || Mathf.Abs(i.transform.position.y - point.y) > 2.5f) continue;
                float score = m - i.Priority * 0.01f;
                if (score < bestScore) { bestScore = score; best = i; off = m; }
            }
            return best;
        }
    }
}
