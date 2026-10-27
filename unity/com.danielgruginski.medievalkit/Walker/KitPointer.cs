using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// The pointer's one question to the game: is it on the game's own UI (a menu, the HUD)? Then the wheel does not zoom
    /// (<see cref="KitCamera"/>) and a click does not walk (<see cref="KitClickToMove"/>). The game sets
    /// <see cref="Blocked"/> (MedievalSetting: GameUI.BlocksPointer); unset, the pointer is never blocked.
    /// </summary>
    public static class KitPointer
    {
        /// <summary>screen point (pixels) -> on the game's UI</summary>
        public static System.Func<Vector2, bool> Blocked;

        public static bool BlockedAt(Vector2 screen) => Blocked != null && Blocked(screen);
    }
}
