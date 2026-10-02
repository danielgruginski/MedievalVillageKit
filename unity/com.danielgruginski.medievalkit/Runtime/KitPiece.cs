namespace MedievalKit
{
    /// <summary>One placed kit piece. Props are the instance's Blender properties (vki_class, vki_collider, vki_link...).</summary>
    public class KitPiece : KitPropsBehaviour
    {
        public string piece;
        /// <summary>Submesh i -> the Blender material slot it came from. Styles (plaster, shutter, roof...) are
        /// slot swaps in Blender (vk_helpers.SLOT), so this is how a generator restyles a piece.</summary>
        public int[] blenderSlots = new int[0];
    }
}
