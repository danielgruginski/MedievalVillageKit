namespace MedievalKit
{
    /// <summary>Level root: camera settings and links from VKI_Root, and the world graph the level belongs to.</summary>
    public class KitLevel : KitPropsBehaviour
    {
        public string levelName;
        public string blenderScene;
        public string exportVersion;
        public KitWorld world;
    }
}
