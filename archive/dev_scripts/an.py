import json, sys, math
sys.path.insert(0, '.')
from grid import *
d = json.load(open('objs.json'))
O = {o[0]: o for o in d}
def base(n): return n.split('_inst')[0][6:]
FORT = ('TownWall_', 'Gatehouse_')
def cat(n):
    b = base(n)
    if b.startswith(FORT): return 'FORT'
    if b.startswith('Tree_'): return 'TREE'
    if b.startswith(('Prop_', 'Pile_')): return 'PROP'
    if b.startswith(('Bush_', 'Plant_', 'Rock_', 'Mushrooms', 'LipGrass', 'Deco_Weeds', 'Stump', 'Crop_', 'Log_Fallen')): return 'VEG'
    if b.startswith(('Wall_', 'Corner_', 'Roof', 'Chapel_', 'Porch', 'InnerCorner', 'Foundation', 'Gallery', 'Chimney', 'Stair_Stone', 'LeanTo', 'BellTower', 'Turret', 'Ceiling', 'Windmill', 'Kiln', 'Passage', 'Parapet', 'Def_', 'Mine_', 'Quarry', 'Palisade', 'Scaffold', 'BuildSite', 'Tent', 'MarketStall', 'LowWall', 'Stockpile', 'Mill_', 'WaterWheel', 'Banner', 'Emblem', 'Sign_', 'Deco_', 'Quay', 'Pier', 'Bridge', 'Rail', 'Animal')): return 'BLD'
    return 'OTHER'
def ov(a, b, s=0.1, zs=0.05):
    return (a[7] + s < b[8] and b[7] < a[8] - s and a[9] + s < b[10] and b[9] < a[10] - s and a[11] + zs < b[12] and b[11] < a[12] - zs)
def depth(a, b):
    return min(a[8], b[8]) - max(a[7], b[7]), min(a[10], b[10]) - max(a[9], b[9])
# spatial hash
HS = {}
for o in d:
    for ci in range(int(o[7] // 3), int(o[8] // 3) + 1):
        for cj in range(int(o[9] // 3), int(o[10] // 3) + 1):
            HS.setdefault((ci, cj), []).append(o)
def near(o, s=0.1):
    seen = set(); out = []
    for ci in range(int(o[7] // 3), int(o[8] // 3) + 1):
        for cj in range(int(o[9] // 3), int(o[10] // 3) + 1):
            for e in HS.get((ci, cj), ()):
                if e[0] == o[0] or e[0] in seen: continue
                seen.add(e[0])
                if ov(o, e, s): out.append(e)
    return out
def fmt(o): return f"{o[0][6:]} @({o[2]:.1f},{o[3]:.1f},{o[4]:.1f}) r{o[5]:.0f}"
