import zlib, struct, sys, colorsys

def load(path):
    d = open(path, 'rb').read()
    assert d[:8] == b'\x89PNG\r\n\x1a\n'
    pos = 8; idat = b''; w = h = None
    while pos < len(d):
        ln, = struct.unpack('>I', d[pos:pos+4]); t = d[pos+4:pos+8]; c = d[pos+8:pos+8+ln]; pos += 12 + ln
        if t == b'IHDR':
            w, h, bd, ct, _, _, il = struct.unpack('>IIBBBBB', c)
            assert bd in (8, 16) and il == 0, (bd, il)
            ch = {2: 3, 6: 4, 0: 1, 4: 2}[ct]; bpp = ch * bd // 8
        elif t == b'IDAT': idat += c
        elif t == b'IEND': break
    raw = zlib.decompress(idat); stride = w * bpp
    rows = []; prev = bytearray(stride); p = 0
    for y in range(h):
        f = raw[p]; p += 1; line = bytearray(raw[p:p+stride]); p += stride
        for x in range(stride):
            a = line[x-bpp] if x >= bpp else 0; b = prev[x]; cc = prev[x-bpp] if x >= bpp else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + b) & 255
            elif f == 3: line[x] = (line[x] + ((a + b) >> 1)) & 255
            elif f == 4:
                pp = a + b - cc; pa = abs(pp-a); pb = abs(pp-b); pc = abs(pp-cc)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else cc)
                line[x] = (line[x] + pr) & 255
        rows.append(bytes(line)); prev = line
    return w, h, bd, ch, rows

def px(img, x, y):
    w, h, bd, ch, rows = img
    r = rows[y]
    if bd == 8:
        return tuple(r[x*ch + k] for k in range(min(3, ch)))
    return tuple(r[(x*ch + k)*2] for k in range(min(3, ch)))

def region(img, x0, y0, x1, y1):
    rs = gs = bs = n = 0; hs = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px(img, x, y); rs += r; gs += g; bs += b; n += 1
            hs.append(colorsys.rgb_to_hsv(r/255, g/255, b/255))
    r, g, b = rs/n, gs/n, bs/n
    H, S, V = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    hs.sort(key=lambda t: t[1]); medS = hs[len(hs)//2][1]
    hs.sort(key=lambda t: t[2]); medV = hs[len(hs)//2][2]
    return dict(rgb=(round(r), round(g), round(b)), H=round(H*360), S=round(S, 2), V=round(V, 2), medS=round(medS, 2), medV=round(medV, 2))

if __name__ == '__main__':
    img = load(sys.argv[1])
    print('size', img[0], img[1], 'bd', img[2], 'ch', img[3])
    for a in sys.argv[2:]:
        x0, y0, x1, y1 = map(int, a.split(','))
        print(a, region(img, x0, y0, x1, y1))
