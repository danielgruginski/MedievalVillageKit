#ifndef MEDIEVALKIT_NOISE_INCLUDED
#define MEDIEVALKIT_NOISE_INCLUDED

// Stand-ins for Blender's procedural nodes used by the terrain recipes (vk_terrain.py). Not bit-exact: Blender's
// Perlin uses its own hash, so patterns differ in detail but match in scale, octaves and value distribution.

float3 KitHash33(float3 p)
{
    p = frac(p * float3(0.1031, 0.1030, 0.0973));
    p += dot(p, p.yxz + 33.33);
    return frac((p.xxy + p.yxx) * p.zyx) * 2.0 - 1.0;
}

float KitHash11(float x)
{
    x = frac(x * 0.1031);
    x *= x + 33.33;
    x *= x + x;
    return frac(x);
}

// gradient (Perlin) noise, about [-1, 1]
float KitPerlin3(float3 p)
{
    float3 i = floor(p);
    float3 f = p - i;
    float3 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
    float n000 = dot(KitHash33(i + float3(0, 0, 0)), f - float3(0, 0, 0));
    float n100 = dot(KitHash33(i + float3(1, 0, 0)), f - float3(1, 0, 0));
    float n010 = dot(KitHash33(i + float3(0, 1, 0)), f - float3(0, 1, 0));
    float n110 = dot(KitHash33(i + float3(1, 1, 0)), f - float3(1, 1, 0));
    float n001 = dot(KitHash33(i + float3(0, 0, 1)), f - float3(0, 0, 1));
    float n101 = dot(KitHash33(i + float3(1, 0, 1)), f - float3(1, 0, 1));
    float n011 = dot(KitHash33(i + float3(0, 1, 1)), f - float3(0, 1, 1));
    float n111 = dot(KitHash33(i + float3(1, 1, 1)), f - float3(1, 1, 1));
    float nx00 = lerp(n000, n100, u.x), nx10 = lerp(n010, n110, u.x);
    float nx01 = lerp(n001, n101, u.x), nx11 = lerp(n011, n111, u.x);
    return 1.6 * lerp(lerp(nx00, nx10, u.y), lerp(nx01, nx11, u.y), u.z);
}

// Blender Noise Texture "Fac" (fBM, roughness 0.5, lacunarity 2, normalized): 0.5 +- 0.5
float KitNoise(float3 p, float scale, float detail)
{
    p *= scale;
    float amp = 1, maxAmp = 0, sum = 0, fs = 1;
    int n = (int)floor(detail);
    for (int i = 0; i <= n; i++)
    {
        sum += KitPerlin3(p * fs) * amp;
        maxAmp += amp;
        amp *= 0.5;
        fs *= 2.0;
    }
    float rmd = detail - n;
    float v = sum / maxAmp;
    if (rmd > 0.001)
    {
        float s2 = sum + KitPerlin3(p * fs) * amp;
        v = lerp(v, s2 / (maxAmp + amp), rmd);
    }
    return saturate(0.5 + 0.5 * v);
}

// Blender Noise Texture "Color": three decorrelated noises
float3 KitNoise3(float3 p, float scale, float detail)
{
    return float3(KitNoise(p, scale, detail),
                  KitNoise(p + float3(31.7, 7.3, 19.1) / scale, scale, detail),
                  KitNoise(p + float3(-13.9, 43.1, 5.7) / scale, scale, detail));
}

// Blender Voronoi 1D, feature Distance to Edge
float KitVoronoiEdge1D(float w, float scale, float randomness)
{
    w *= scale;
    float cell = floor(w);
    float local = w - cell;
    float mid = KitHash11(cell) * randomness;
    float left = -1.0 + KitHash11(cell - 1.0) * randomness;
    float right = 1.0 + KitHash11(cell + 1.0) * randomness;
    return min(abs((mid + left) * 0.5 - local), abs((mid + right) * 0.5 - local));
}

// Blender Hue/Saturation/Value node
float3 KitHSV(float3 c, float hue, float sat, float val)
{
    float4 K = float4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    float4 p = lerp(float4(c.bg, K.wz), float4(c.gb, K.xy), step(c.b, c.g));
    float4 q = lerp(float4(p.xyw, c.r), float4(c.r, p.yzx), step(p.x, c.r));
    float d = q.x - min(q.w, q.y);
    float3 hsv = float3(abs(q.z + (q.w - q.y) / (6.0 * d + 1e-10)), d / (q.x + 1e-10), q.x);
    hsv.x = frac(hsv.x + hue - 0.5);
    hsv.y = saturate(hsv.y * sat);
    hsv.z *= val;
    float3 rgb = saturate(abs(frac(hsv.x + float3(1, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0) - 1.0);
    return hsv.z * lerp(1, rgb, hsv.y);
}

// Blender Bump node (screen-space derivatives): perturb N by height h at world position P
float3 KitBump(float3 P, float3 N, float h, float strength, float dist)
{
    float3 dPdx = ddx(P), dPdy = ddy(P);
    float3 Rx = cross(dPdy, N), Ry = cross(N, dPdx);
    float det = dot(dPdx, Rx);
    float3 surfgrad = ddx(h) * Rx + ddy(h) * Ry;
    float3 NN = normalize(abs(det) * N - dist * sign(det) * surfgrad);
    return normalize(lerp(N, NN, saturate(strength)));
}

#endif
