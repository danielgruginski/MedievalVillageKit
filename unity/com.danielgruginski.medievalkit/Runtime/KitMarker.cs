namespace MedievalKit
{
    /// <summary>An empty from the Blender scene: spawn points (SPN_), light and effect anchors (LGT_, FXA_), the level root.</summary>
    public class KitMarker : KitPropsBehaviour
    {
        public enum Kind { Other, Spawn, LightAnchor, FxAnchor, Root }
        public Kind kind;
    }
}
