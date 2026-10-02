using System;
using System.Collections.Generic;
using UnityEngine;

namespace MedievalKit
{
    /// <summary>
    /// What KitHouseGenerator builds with: the grid, the pieces that fill each role and the style table.
    /// Generated from Data/house_rules.json (Tools > Medieval Kit > Build All); edit freely to add your own pieces to
    /// a role (another upper-wall frame, a different porch...) or new style options.
    /// </summary>
    [CreateAssetMenu(menuName = "Medieval Kit/House Rules", fileName = "KitHouseRules")]
    public class KitHouseRules : ScriptableObject
    {
        [Header("Grid (metres)")]
        public float cell = 3f;     // one wall bay
        public float h1 = 3f;       // ground storey
        public float h2 = 2.8f;     // each upper storey
        public float depth = 6f;    // houses are two cells deep

        [Serializable]
        public class GroundSet
        {
            public string name;     // "Stone", "Plaster"
            public GameObject wallDoor, wallWindow, wallPlain, corner;
            [Tooltip("Concave corner of an L-house.")] public GameObject innerCorner;
        }

        [Serializable]
        public class RoofSet
        {
            public GameObject gable, mid, hip;
            [Tooltip("The L-house's corner roof (tile roofs only).")] public GameObject lcorner;
        }

        [Header("Pieces by role")]
        public List<GroundSet> ground = new List<GroundSet>();
        public List<GameObject> upperWallWindow = new List<GameObject>();
        public List<GameObject> upperWallPlain = new List<GameObject>();
        public List<GameObject> upperCorner = new List<GameObject>();
        public List<GameObject> upperInnerCorner = new List<GameObject>();
        public RoofSet tileRoof = new RoofSet();
        public RoofSet thatchRoof = new RoofSet();
        public List<GameObject> chimney = new List<GameObject>();
        public List<GameObject> dormer = new List<GameObject>();
        public List<GameObject> porch = new List<GameObject>();
        public List<GameObject> flowerBox = new List<GameObject>();
        public List<GameObject> weeds = new List<GameObject>();
        public List<GameObject> ivy = new List<GameObject>();
        public List<GameObject> planter = new List<GameObject>();
        public List<GameObject> lantern = new List<GameObject>();

        [Serializable]
        public class StyleOption
        {
            public string name;
            [Tooltip("Replaces the kind's slot; empty = the piece's own material.")]
            public Material material;
        }

        [Serializable]
        public class StyleKind
        {
            public string kind;         // plaster, shutter, roof, cloth, stone
            public int blenderSlot;     // the material slot this kind swaps
            public List<StyleOption> options = new List<StyleOption>();
            public StyleOption Find(string name) => options.Find(o => o.name == name);
        }

        [Header("Styles")]
        public List<StyleKind> styles = new List<StyleKind>();

        [Header("Random style (vk_helpers.random_style)")]
        [Range(0, 1)] public float stoneGroundChance = 0.6f;
        public List<string> plasterChoices = new List<string> { "Cream", "White", "Ochre", "Rose", "Cream" };
        public List<string> shutterChoices = new List<string> { "Teal", "Red", "Green", "Blue", "Natural" };
        [Range(0, 1)] public float shutterWornChance = 0.2f;
        public List<string> roofChoices = new List<string> { "Red", "Blue", "Green", "Red" };
        public int thatchWeightStone = 1, thatchWeightPlaster = 2;

        public StyleKind Kind(string kind) => styles.Find(s => s.kind == kind);
        public GroundSet Ground(string name) => ground.Find(g => g.name == name) ?? (ground.Count > 0 ? ground[0] : null);
    }
}
