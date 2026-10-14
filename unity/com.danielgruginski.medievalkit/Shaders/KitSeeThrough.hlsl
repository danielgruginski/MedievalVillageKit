// The see-through round a game's walker (the fade of Diablo-like games): what stands between the camera and the
// walker -- in a cone from the camera to a disc round the walker's chest, in front of the walker along the camera's
// level heading, above its feet (a building's pieces: above feet + _KitSeeThroughArgs.y) -- opens, with a thin dithered
// rim. "In front" is measured level, not along the line of sight: the camera looks down, so a wall the walker stands
// before reaches nearer the camera along the line of sight above the walker's head, yet it is behind the walker and
// stays whole. And only a piece in the walker's way opens: one whose bounds (Renderer.bounds) stay out of the wedge from
// the camera to the walker's upper body (waist to head) hides none of it and stays whole, though its near stretch lies
// in the cone -- a wall beside the walker running towards the camera, the rock past that wall (a position alone cannot
// tell that wall from one across the walker's way), a fence before its legs. The pieces' rendering layers (set in play
// by KitSeeThrough.cs, from KitVillage) refine it:
//   loose (LooseLayer: KitVillage's Nature and Props) -- opens down to the walker's feet; only a building's pieces keep
//          their foot (the walls' footprint stays; a tree would be left a stump);
//   round (RoundLayer: the Nature) -- in the way when the ellipsoid inside its bounds meets the sight lines to the
//          walker's chest or head (a bush's box reaches the feet of a walker beside it, its leaves do not);
//   group (GroupLayer: a building's pieces) -- decided on the CPU, the building as one (KitSeeThrough.Decide): all its
//          pieces open (OpenLayer) when it is in the way, so the hole stays round across walls, roof and chimney. Its
//          tag (bits 8-14, KitSeeThrough.TagShift) colours it in the hidden check's view: in the way = its own surface
//          stands over the walker there (2026-10-13 night; the boxes of its pieces opened a barn behind the walker).
// Shadows stay (the shadow pass does not clip); the depth passes clip too, so SSAO and depth priming see the same hole.
// Caps (KitLit's SeeThroughCap pass, 2026-10-13): the kit's solid materials are one-sided, so a solid the hole opens
// showed hollow; inside the hole its back faces are drawn flat, in shade, a little behind in depth (a real face always
// wins): a sliced wall reads solid.
// The hidden check (KitSeeThroughProbe.cs) renders a small view of the walker with _KitSeeThroughProbe = 1: then only
// what the hole would open is drawn (the cone left out) -- of a building, all that stands in front of the walker, open
// or not -- flat magenta (KitLit; a building's tag in green), and the share of magenta over the walker's upper body says
// whether anything hides it (the game opens and closes the hole by that), its tags which buildings.
// Off until a game sets the globals (Shader.SetGlobalVector):
//   _KitSeeThrough      xyz: the walker's chest (world; all 0: no walker), w: the hole's radius at the walker (m);
//                          w <= 0: shut (the hidden check still runs)
//   _KitSeeThroughArgs  x: the walker's feet (world y), y: a building's pieces kept up to feet + y (the ground, low and
//                          cut walls),
//                       z: kept within z (m) in front of the walker along the camera's level heading (what it
//                          stands among: an eave over it, a post beside it),
//                       w: the walker's half-width (m) for "in its way": the wedge from the camera to a box w each
//                          side of the walker, from its waist to its head; w <= 0: every piece in the cone opens
// 2026-10-13 (MedievalSetting, the user's screenshots: a tree cut to a stump, bush tops and a chapel's eave speckled
// though nothing hid the player, a wall end standing whole in a roof's hole): the rim narrowed from 45% of the hole's
// radius to 15%; "in its way" from the waist up (it was from the feet); the loose, round and group layers.
#ifndef KIT_SEE_THROUGH_INCLUDED
#define KIT_SEE_THROUGH_INCLUDED

// a solid material (one-sided: KitLit defines this from its _Cull before the include; elsewhere none is)
#ifndef KIT_SEE_THROUGH_SOLID
#define KIT_SEE_THROUGH_SOLID false
#endif

float4 _KitSeeThrough;
float4 _KitSeeThroughArgs;
float _KitSeeThroughProbe;                                     // 1 while the hidden check's view renders

static const float kKitBayer4[16] = { 0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5 };
static const float kKitSeeThroughRim = 0.15;                   // the dithered rim: this share of the hole's radius
static const uint kKitSeeThroughLoose = 1u << 16;              // KitSeeThrough.LooseLayer (C#)
static const uint kKitSeeThroughRound = 1u << 17;              // KitSeeThrough.RoundLayer (C#)
static const uint kKitSeeThroughGroup = 1u << 18;              // KitSeeThrough.GroupLayer (C#): decided on the CPU
static const uint kKitSeeThroughOpen = 1u << 19;               // KitSeeThrough.OpenLayer (C#): its building is in the way
static const uint kKitSeeThroughCapMesh = 1u << 20;            // KitSeeThrough.CapLayer (C#): a real cap (KitSeeThroughCaps)
static const uint kKitSeeThroughCut = 1u << 21;                // KitSeeThrough.CutLayer (C#): its cut kept in bits 22-31
static const float kKitSeeThroughCutStep = 0.05;               // KitSeeThroughCaps.Step (C#)
static const uint kKitSeeThroughKeep = 1u << 15;               // KitSeeThrough.KeepBit (C#): never cut (what a character carries)
static const uint kKitSeeThroughTagShift = 8;                  // KitSeeThrough.TagShift (C#): a building's tag, bits 8-14
static const float kKitSeeThroughAboveFeet = 0.05;             // KitSeeThrough.AboveFeet (C#): a cut never under the walker's feet + this

// a stable screen-space dither (no frame-to-frame noise)
float KitBayer4(float2 pixel)
{
    uint2 q = (uint2)pixel % 4;
    return (kKitBayer4[q.y * 4 + q.x] + 0.5) / 16.0;
}

// keeps the s in [lo, hi] with s * a <= b
void KitSeeThroughLe(float a, float b, inout float lo, inout float hi)
{
    if (a > 1e-6) hi = min(hi, b / a);
    else if (a < -1e-6) lo = max(lo, b / a);
    else if (b < 0) hi = -1;                                   // never
}

// the piece's rendering layers (KitSeeThrough's bits)
uint KitSeeThroughLayers()
{
#if defined(UNITY_DOTS_INSTANCING_ENABLED)
    return 0;
#else
    return asuint(unity_RenderingLayer.x);
#endif
}

// does the segment from a to b meet the unit sphere?
bool KitSeeThroughHitsUnit(float3 a, float3 b)
{
    float3 d = b - a;
    float3 q = a + d * saturate(-dot(a, d) / max(dot(d, d), 1e-6));
    return dot(q, q) < 1;
}

// is the piece being drawn in the walker's way: do its bounds meet the wedge from the camera to the walker's upper body
// (a box _KitSeeThroughArgs.w each side of the walker, from 0.9 to 1.9 times its chest's height over its feet)? A point
// of the wedge is cam + s * (c - cam + u), s in [0, 1], |u| <= the box's half-size per axis: on each axis an interval of s
bool KitSeeThroughInTheWay(float3 cam)
{
    float w = _KitSeeThroughArgs.w;
    if (w <= 0) return true;
    uint layers = KitSeeThroughLayers();
    if (layers & kKitSeeThroughGroup) return (layers & kKitSeeThroughOpen) != 0;   // a building's piece: decided as one
#if defined(UNITY_INSTANCING_ENABLED) || defined(UNITY_DOTS_INSTANCING_ENABLED)
    return true;                                               // instanced: no bounds of its own (as before)
#else
    float3 bmin = unity_RendererBounds_Min.xyz, bmax = unity_RendererBounds_Max.xyz;
    if (any(bmax < bmin) || all(bmax == bmin)) return true;   // no bounds given: as before
    float feet = _KitSeeThroughArgs.x, chest = _KitSeeThrough.y - feet;
    float waist = feet + 0.9 * chest, head = feet + 1.9 * chest;
    if (layers & kKitSeeThroughRound)                          // the sight lines to its chest and head through the
    {                                                          // ellipsoid (grown by the half-width)
        float3 o = 0.5 * (bmin + bmax), inv = 1 / max(0.5 * (bmax - bmin) + w, 1e-3), a = (cam - o) * inv;
        return KitSeeThroughHitsUnit(a, (float3(_KitSeeThrough.x, 0.5 * (waist + head), _KitSeeThrough.z) - o) * inv)
            || KitSeeThroughHitsUnit(a, (float3(_KitSeeThrough.x, head, _KitSeeThrough.z) - o) * inv);
    }
    float3 c = float3(_KitSeeThrough.x, 0.5 * (waist + head), _KitSeeThrough.z);
    float3 e = float3(w, 0.5 * (head - waist), w);
    float3 dc = c - cam;
    float lo = 0, hi = 1;
    [unroll] for (int i = 0; i < 3; i++)
    {
        KitSeeThroughLe(dc[i] - e[i], bmax[i] - cam[i], lo, hi);     // the wedge's low side under the bounds' top
        KitSeeThroughLe(-(dc[i] + e[i]), cam[i] - bmin[i], lo, hi);  // its high side over their bottom
    }
    return lo <= hi;
#endif
}

// where "in front of the walker" is judged for this point: the point itself, but for the solid parts of a loose piece
// (a trunk, a rock, a cart) the piece's own origin -- the foot of a tree's trunk, a prop's base -- so the whole of it is in
// front or not; judged point by point, a trunk beside the walker was cut in half along the level line and showed its
// inside (2026-10-13; the bounds' middle was tried first, but a lopsided canopy moves it off the trunk). An origin off the
// bounds (a batched mesh) falls back to their middle. A canopy's leaves (two-sided) are still judged point by point: the
// part of it over the walker opens.
float3 KitSeeThroughLevelPoint(float3 positionWS)
{
#if !defined(UNITY_INSTANCING_ENABLED) && !defined(UNITY_DOTS_INSTANCING_ENABLED)
    if ((KitSeeThroughLayers() & kKitSeeThroughLoose) && KIT_SEE_THROUGH_SOLID)
    {
        float3 bmin = unity_RendererBounds_Min.xyz, bmax = unity_RendererBounds_Max.xyz;
        if (all(bmax >= bmin) && any(bmax != bmin))
        {
            float3 o = UNITY_MATRIX_M._m03_m13_m23;
            bool inside = all(o.xz >= bmin.xz - 0.5) && all(o.xz <= bmax.xz + 0.5);
            return inside ? float3(o.x, positionWS.y, o.z) : 0.5 * (bmin + bmax);
        }
    }
#endif
    return positionWS;
}

// the foot kept (world y): where the piece's own cut lies when it has one (KitSeeThroughCaps: 1.4 m over its base -- a
// house's floor, a tree's foot -- kept in its rendering layer as an offset over its origin, so the shader cuts exactly
// where its cap lies), but never under the walker's feet (+ kKitSeeThroughAboveFeet: a walker up an outer stair or on
// the keep's walk stood over a hole down to the ground, its floor cut away, 2026-10-14 -- there the real cap lies under
// the floor kept and is not drawn, and the back-face cap pass finishes the cut); else a building's up to feet + y and a
// loose piece's only below the feet (a little under them: the flare of a trunk's roots at the walker's own level stayed
// as a thin dark curve)
float KitSeeThroughFoot()
{
    uint layers = KitSeeThroughLayers();
    // a sheet in a building (a window pane, ivy, a cloth): opens down to the feet -- it has no section to cap, and its
    // stub stood in the cut (the chapel's stained glass, 2026-10-13)
    if ((layers & kKitSeeThroughGroup) && !KIT_SEE_THROUGH_SOLID) return _KitSeeThroughArgs.x - 0.25;
    if (layers & kKitSeeThroughCut)
    {
        int q = (int)((layers >> 22) & 0x3FF);
        if (q >= 512) q -= 1024;
        return max(UNITY_MATRIX_M._m13 + UNITY_MATRIX_M._m11 * (q * kKitSeeThroughCutStep), _KitSeeThroughArgs.x + kKitSeeThroughAboveFeet);
    }
    return _KitSeeThroughArgs.x + ((layers & kKitSeeThroughLoose) ? -0.25 : _KitSeeThroughArgs.y);
}

// is the point in front of the walker, along the camera's level heading, by more than _KitSeeThroughArgs.z? (lv: the
// point where "in front" is judged, from the camera; d: the line of sight to the walker, unit, L its length)
bool KitSeeThroughInFront(float3 lv, float3 cam, float3 d, float L)
{
    float2 h = d.xz;                                           // the camera's level heading
    float hl = length(h);
    if (hl > 0.05)
    {
        h /= hl;
        return dot(lv.xz, h) <= dot(_KitSeeThrough.xz - cam.xz, h) - _KitSeeThroughArgs.z;
    }
    return dot(lv, d) <= L - _KitSeeThroughArgs.z;            // (looking straight down: along the line of sight)
}

// would the hole open this point, the cone left out: in front of the walker, above the foot kept (askFoot), of a piece
// in its way? (v: the point from the camera, d: the line of sight to the walker, unit, L its length, t the point along it)
bool KitSeeThroughOpensAt(float3 positionWS, float3 cam, out float3 v, out float3 d, out float L, out float t, bool askFoot)
{
    d = _KitSeeThrough.xyz - cam;
    L = length(d);
    d /= max(L, 1e-4);
    v = positionWS - cam;
    t = dot(v, d);                                             // along the line of sight
    if (t <= 0) return false;
    // in front of the walker -- not asked of an open building (group): the CPU opened it because it is in the way, and
    // it is cut as a whole inside the hole; judged point by point, a building beside the walker (the hamlet's bell
    // tower) was sliced along the walker's level line and showed its hollow inside, and the far slope of a roof floated
    // over the hole (2026-10-13)
    if (!(KitSeeThroughLayers() & kKitSeeThroughGroup) && !KitSeeThroughInFront(KitSeeThroughLevelPoint(positionWS) - cam, cam, d, L))
        return false;                                          // level with or behind it
    if (askFoot && positionWS.y < KitSeeThroughFoot()) return false;   // the foot kept
    return KitSeeThroughInTheWay(cam);                         // out of the walker's way (beside it): whole
}

// in the hidden check's view, a building's piece: does this point stand over the walker -- in front of it, above the foot
// kept? Asked of every building, open or not: what the view shows of it over the walker is what opens it (its tag)
bool KitSeeThroughCovers(float3 positionWS, float3 cam)
{
    float3 d = _KitSeeThrough.xyz - cam;
    float L = length(d);
    d /= max(L, 1e-4);
    float3 v = positionWS - cam;
    return dot(v, d) > 0 && KitSeeThroughInFront(v, cam, d, L) && positionWS.y >= KitSeeThroughFoot();
}

// the hidden check's colour of a piece (green): its building's tag x 2 / 255 (0: not a building's)
half KitSeeThroughProbeTag()
{
    return (half)(((KitSeeThroughLayers() >> kKitSeeThroughTagShift) & 0x7F) * 2) / 255.0;
}

bool KitSeeThroughOpens(float3 positionWS, float3 cam, out float3 v, out float3 d, out float L, out float t)
{
    return KitSeeThroughOpensAt(positionWS, cam, v, d, L, t, true);
}

void KitSeeThroughClip(float3 positionWS, float2 pixel)
{
    float3 cam = _WorldSpaceCameraPos, v, d;
    float L, t;
    // a real cap (KitSeeThroughCaps): drawn only where the hole opened its piece -- the piece's complement, its dithered
    // rim included; never in the hidden check's view, never while the hole is shut
    if (KitSeeThroughLayers() & kKitSeeThroughCapMesh)
    {
        // (a cap under the walker's feet: its piece is kept up to them, the cap would lie inside it)
        if (_KitSeeThroughProbe > 0.5 || _KitSeeThrough.w <= 0 || positionWS.y < _KitSeeThroughArgs.x + kKitSeeThroughAboveFeet - 0.01
            || !KitSeeThroughOpensAt(positionWS, cam, v, d, L, t, false))
        {
            clip(-1);
            return;
        }
        float rc = _KitSeeThrough.w * t / L;
        float kc = saturate((rc - length(v - d * t)) / max(rc * kKitSeeThroughRim, 1e-3));
        clip(kc - KitBayer4(pixel) - 1e-3);
        return;
    }
    if (_KitSeeThroughProbe > 0.5)                             // the hidden check's view: only what the hole would open
    {                                                          // -- a building: what stands over the walker, open or not
        uint layers = KitSeeThroughLayers();
        bool draw = !(layers & kKitSeeThroughKeep)
            && ((layers & kKitSeeThroughGroup) ? KitSeeThroughCovers(positionWS, cam) : KitSeeThroughOpens(positionWS, cam, v, d, L, t));
        clip(draw ? 1 : -1);
        return;
    }
    if (KitSeeThroughLayers() & kKitSeeThroughKeep) return;   // what a character carries: never cut
    float r = _KitSeeThrough.w;
    if (r <= 0) return;
    if (!KitSeeThroughOpens(positionWS, cam, v, d, L, t)) return;
    float rr = r * t / L;                                      // a cone: a disc of radius r at the walker, a circle on screen
    float off = length(v - d * t);
    float k = saturate((rr - off) / max(rr * kKitSeeThroughRim, 1e-3));   // 1 in the middle, a thin dithered rim
    clip(KitBayer4(pixel) - k);
}

// the caps (KitLit's SeeThroughCap pass, back faces): drawn only inside the open hole on screen -- where a back face
// shows only because the hole opened what stood in front of it -- and only below the foot kept: the inside of a wall cut
// down to its footprint, which then reads as one solid cut face. Nowhere else (Greywall, 2026-10-13): a back face kept by
// the margin in front of the walker -- the far side of a wall it stands against -- was drawn flat right over it, and the
// far slope of a roof behind it (an attic's ceiling, from below) hid the street it stood in.
static const half kKitCapShade = 0.8;                          // a cap's light (sky + sun on a level face) times this
static const float kKitCapTile = 0.5;                          // a cap's texture: tiles per metre on the cut plane

// where this pixel's line of sight meets the level cut plane (the foot kept): the cap is drawn as if it lay there --
// its texture projected from above and lit as a level face -- whatever back face of the piece the pixel shows
float3 KitSeeThroughCapPoint(float3 positionWS)
{
    float3 cam = _WorldSpaceCameraPos, r = positionWS - cam;
    return cam + r * saturate((KitSeeThroughFoot() - cam.y) / min(r.y, -1e-4));
}

void KitSeeThroughCapClip(float3 positionWS)
{
    float3 cam = _WorldSpaceCameraPos, v, d;
    float L, t;
    KitSeeThroughOpens(positionWS, cam, v, d, L, t);
    clip(_KitSeeThrough.w * t / L - length(v - d * t));        // off the hole (or behind the camera): no cap
    clip(KitSeeThroughFoot() - positionWS.y);                  // above the foot kept: no cap
}

// in passes that know only the clip-space position (the depth passes): the world position from the pixel and its depth
void KitSeeThroughClipCS(float4 positionCS)
{
    if (_KitSeeThrough.w <= 0 && _KitSeeThroughProbe <= 0.5 && !(KitSeeThroughLayers() & kKitSeeThroughCapMesh)) return;
    float2 uv = GetNormalizedScreenSpaceUV(positionCS);
    float3 ws = ComputeWorldSpacePosition(uv, positionCS.z, UNITY_MATRIX_I_VP);
    KitSeeThroughClip(ws, positionCS.xy);
}

#endif
