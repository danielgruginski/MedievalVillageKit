// The see-through round a game's walker (the fade of Diablo-like games): what stands between the camera and the
// walker -- in a cone from the camera to a disc round the walker's chest, above the walker's knees, and in front of
// the walker along the camera's level heading -- dithers away with a soft rim. "In front" is measured level, not along
// the line of sight: the camera looks down, so a wall the walker stands before reaches nearer the camera along the
// line of sight above the walker's head, yet it is behind the walker and stays whole. Shadows stay (the shadow pass does not clip); the depth passes clip too, so
// SSAO and depth priming see the same hole. Off until a game sets the globals (Shader.SetGlobalVector):
//   _KitSeeThrough      xyz: the walker's chest (world), w: the hole's radius at the walker (m); w <= 0: off
//   _KitSeeThroughArgs  x: the walker's feet (world y), y: kept up to feet + y (the ground, low and cut walls),
//                       z: kept within z (m) in front of the walker along the camera's level heading (what it
//                          stands among: an eave over it, a post beside it)
#ifndef KIT_SEE_THROUGH_INCLUDED
#define KIT_SEE_THROUGH_INCLUDED

float4 _KitSeeThrough;
float4 _KitSeeThroughArgs;

static const float kKitBayer4[16] = { 0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5 };

// a stable screen-space dither (no frame-to-frame noise)
float KitBayer4(float2 pixel)
{
    uint2 q = (uint2)pixel % 4;
    return (kKitBayer4[q.y * 4 + q.x] + 0.5) / 16.0;
}

void KitSeeThroughClip(float3 positionWS, float2 pixel)
{
    float r = _KitSeeThrough.w;
    if (r <= 0) return;
    float3 cam = _WorldSpaceCameraPos;
    float3 d = _KitSeeThrough.xyz - cam;
    float L = length(d);
    d /= max(L, 1e-4);
    float3 v = positionWS - cam;
    float t = dot(v, d);                                       // along the line of sight
    if (t <= 0) return;
    float2 h = d.xz;                                           // the camera's level heading
    float hl = length(h);
    if (hl > 0.05)
    {
        h /= hl;
        if (dot(v.xz, h) > dot(_KitSeeThrough.xz - cam.xz, h) - _KitSeeThroughArgs.z) return;   // level with or behind it
    }
    else if (t > L - _KitSeeThroughArgs.z) return;             // (looking straight down: along the line of sight)
    if (positionWS.y < _KitSeeThroughArgs.x + _KitSeeThroughArgs.y) return;
    float rr = r * t / L;                                      // a cone: a disc of radius r at the walker, a circle on screen
    float off = length(v - d * t);
    float k = saturate((rr - off) / max(rr * 0.45, 1e-3));    // 1 in the middle, a soft dithered rim
    clip(KitBayer4(pixel) - k);
}

// in passes that know only the clip-space position (the depth passes): the world position from the pixel and its depth
void KitSeeThroughClipCS(float4 positionCS)
{
    if (_KitSeeThrough.w <= 0) return;
    float2 uv = GetNormalizedScreenSpaceUV(positionCS);
    float3 ws = ComputeWorldSpacePosition(uv, positionCS.z, UNITY_MATRIX_I_VP);
    KitSeeThroughClip(ws, positionCS.xy);
}

#endif
