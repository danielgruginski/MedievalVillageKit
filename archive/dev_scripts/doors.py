from an import *
MOUNT=("Prop_Sign","Prop_Lantern","Prop_Festoon","Prop_Banner","Prop_Bunting","Prop_Wreath","Prop_Shelf","FlowerBox","Window","Hanging","Awning","Chimney","Doormat","Step","Mat","Porch","Deco_Ivy","Banner_Wall","Emblem","LipGrass","Sign_")
doors=[o for o in d if '_Door' in o[0] and not base(o[0]).startswith('Prop')]
def corridor(dr, half=0.65, depth=2.0):
    r=math.radians(dr[5]); c,s=math.cos(r),math.sin(r)
    # local frame: u along wall (x), v outward is -Y local
    return c,s
res=[]
for dr in doors:
    r=math.radians(dr[5]); c,s=math.cos(r),math.sin(r)
    for o in d:
        if o is dr: continue
        if abs(o[2]-dr[2])>5 or abs(o[3]-dr[3])>5: continue
        b=base(o[0])
        if any(m in o[0] for m in MOUNT): continue
        if b.startswith(('Wall_','Corner_','Roof','Chapel_','InnerCorner','Foundation','Ceiling','Gallery','Turret','Parapet','Def_','Scaffold','Gatehouse','TownWall','BuildSite','Quay','Pier','Bridge')): continue
        if o[12] < dr[4]+0.15 or o[11] > dr[4]+1.9: continue
        # object's AABB corners into door frame
        P=[((x-dr[2])*c+(y-dr[3])*s, -(x-dr[2])*s+(y-dr[3])*c) for x in (o[7],o[8]) for y in (o[9],o[10])]
        u0=min(p[0] for p in P);u1=max(p[0] for p in P);v0=min(p[1] for p in P);v1=max(p[1] for p in P)
        if u1>-0.55 and u0<0.55 and v0<-0.3 and v1>-2.0:
            res.append((dr,o,u0,u1,v0,v1))
for dr,o,u0,u1,v0,v1 in res:
    print(f'{fmt(dr):48s} <- {fmt(o):50s} u[{u0:.2f},{u1:.2f}] v[{v0:.2f},{v1:.2f}]')
