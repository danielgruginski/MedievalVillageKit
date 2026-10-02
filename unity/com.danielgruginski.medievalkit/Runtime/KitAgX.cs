using System;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.RenderGraphModule;
using UnityEngine.Rendering.RenderGraphModule.Util;
using UnityEngine.Rendering.Universal;

namespace MedievalKit
{
    /// <summary>
    /// Blender's AgX view transform (with its contrast looks) as a volume override. The kit's colours were tuned
    /// under AgX, so levels built from the kit enable it; set URP's own Tonemapping to None alongside it.
    /// Exposure is applied here, before the curve, as Blender does.
    /// </summary>
    [Serializable, VolumeComponentMenu("Medieval Kit/AgX Tonemapping")]
    public sealed class KitAgX : VolumeComponent, IPostProcessComponent
    {
        public BoolParameter enabled = new BoolParameter(false);
        [Tooltip("Blender's Exposure (stops), applied before the curve.")]
        public FloatParameter exposure = new FloatParameter(0f);
        [Tooltip("AgX look contrast in log space: Base 1.0, Medium High 1.2, High 1.4, Very High 1.57.")]
        public ClampedFloatParameter contrast = new ClampedFloatParameter(1.2f, 0.5f, 2f);

        public bool IsActive() => enabled.value;
    }
}
