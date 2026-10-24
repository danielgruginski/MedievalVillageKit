// Stand-ins for Blender's procedural nodes used by the terrain recipes (vk_terrain.py), ported line for line from the
// Unity package's KitNoise.hlsl. Not bit-exact with Blender: its Perlin uses its own hash, so patterns differ in detail
// but match in scale, octaves and value distribution.

vec3 kit_hash33(vec3 p) {
	p = fract(p * vec3(0.1031, 0.1030, 0.0973));
	p += dot(p, p.yxz + 33.33);
	return fract((p.xxy + p.yxx) * p.zyx) * 2.0 - 1.0;
}

float kit_hash11(float x) {
	x = fract(x * 0.1031);
	x *= x + 33.33;
	x *= x + x;
	return fract(x);
}

// gradient (Perlin) noise, about [-1, 1]
float kit_perlin3(vec3 p) {
	vec3 i = floor(p);
	vec3 f = p - i;
	vec3 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
	float n000 = dot(kit_hash33(i + vec3(0.0, 0.0, 0.0)), f - vec3(0.0, 0.0, 0.0));
	float n100 = dot(kit_hash33(i + vec3(1.0, 0.0, 0.0)), f - vec3(1.0, 0.0, 0.0));
	float n010 = dot(kit_hash33(i + vec3(0.0, 1.0, 0.0)), f - vec3(0.0, 1.0, 0.0));
	float n110 = dot(kit_hash33(i + vec3(1.0, 1.0, 0.0)), f - vec3(1.0, 1.0, 0.0));
	float n001 = dot(kit_hash33(i + vec3(0.0, 0.0, 1.0)), f - vec3(0.0, 0.0, 1.0));
	float n101 = dot(kit_hash33(i + vec3(1.0, 0.0, 1.0)), f - vec3(1.0, 0.0, 1.0));
	float n011 = dot(kit_hash33(i + vec3(0.0, 1.0, 1.0)), f - vec3(0.0, 1.0, 1.0));
	float n111 = dot(kit_hash33(i + vec3(1.0, 1.0, 1.0)), f - vec3(1.0, 1.0, 1.0));
	float nx00 = mix(n000, n100, u.x), nx10 = mix(n010, n110, u.x);
	float nx01 = mix(n001, n101, u.x), nx11 = mix(n011, n111, u.x);
	return 1.6 * mix(mix(nx00, nx10, u.y), mix(nx01, nx11, u.y), u.z);
}

// Blender Noise Texture "Fac" (fBM, roughness 0.5, lacunarity 2, normalized): 0.5 +- 0.5
float kit_noise(vec3 p, float scale, float detail) {
	p *= scale;
	float amp = 1.0, max_amp = 0.0, sum = 0.0, fs = 1.0;
	int n = int(floor(detail));
	for (int i = 0; i <= n; i++) {
		sum += kit_perlin3(p * fs) * amp;
		max_amp += amp;
		amp *= 0.5;
		fs *= 2.0;
	}
	float rmd = detail - float(n);
	float v = sum / max_amp;
	if (rmd > 0.001) {
		float s2 = sum + kit_perlin3(p * fs) * amp;
		v = mix(v, s2 / (max_amp + amp), rmd);
	}
	return clamp(0.5 + 0.5 * v, 0.0, 1.0);
}

// Blender Noise Texture "Color": three decorrelated noises
vec3 kit_noise3(vec3 p, float scale, float detail) {
	return vec3(kit_noise(p, scale, detail),
			kit_noise(p + vec3(31.7, 7.3, 19.1) / scale, scale, detail),
			kit_noise(p + vec3(-13.9, 43.1, 5.7) / scale, scale, detail));
}

// Blender Voronoi 1D, feature Distance to Edge
float kit_voronoi_edge_1d(float w, float scale, float randomness) {
	w *= scale;
	float cell = floor(w);
	float local = w - cell;
	float mid = kit_hash11(cell) * randomness;
	float left = -1.0 + kit_hash11(cell - 1.0) * randomness;
	float right = 1.0 + kit_hash11(cell + 1.0) * randomness;
	return min(abs((mid + left) * 0.5 - local), abs((mid + right) * 0.5 - local));
}

// Blender Hue/Saturation/Value node
vec3 kit_hsv(vec3 c, float hue, float sat, float val) {
	vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
	vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
	vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
	float d = q.x - min(q.w, q.y);
	vec3 hsv = vec3(abs(q.z + (q.w - q.y) / (6.0 * d + 1e-10)), d / (q.x + 1e-10), q.x);
	hsv.x = fract(hsv.x + hue - 0.5);
	hsv.y = clamp(hsv.y * sat, 0.0, 1.0);
	hsv.z *= val;
	vec3 rgb = clamp(abs(fract(hsv.x + vec3(1.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0) - 1.0, 0.0, 1.0);
	return hsv.z * mix(vec3(1.0), rgb, hsv.y);
}

// Blender Bump node (screen-space derivatives): perturb N by height h at world position P
vec3 kit_bump(vec3 P, vec3 N, float h, float strength, float dist) {
	vec3 dpdx = dFdx(P), dpdy = dFdy(P);
	vec3 rx = cross(dpdy, N), ry = cross(N, dpdx);
	float det = dot(dpdx, rx);
	vec3 surfgrad = dFdx(h) * rx + dFdy(h) * ry;
	vec3 nn = normalize(abs(det) * N - dist * sign(det) * surfgrad);
	return normalize(mix(N, nn, clamp(strength, 0.0, 1.0)));
}
