using System;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// Receives a kit unit's animation events (function OnUnitEvent, the event's name as its string) and passes them
    /// on; nothing else happens here. The siege catapult's events: Throw "Release" (the stone leaves the cup: spawn the
    /// projectile at Socket_Projectile, its forward is the launch direction) and "Slam" (the arm hits the stop), Load
    /// "Hooked" and "Loaded", Destroyed "Break" (a wheel comes off) and "Snap" (the arm breaks). Without a receiver on
    /// the Animator's object Unity logs "AnimationEvent has no receiver" for every event.
    /// </summary>
    [DisallowMultipleComponent]
    public class KitUnitEvents : MonoBehaviour
    {
        /// <summary>Raised with the event's name.</summary>
        public event Action<string> Fired;

        public string Last { get; private set; }
        public float LastTime { get; private set; }

        public void OnUnitEvent(string name)
        {
            Last = name;
            LastTime = Time.time;
            Fired?.Invoke(name);
        }
    }
}
