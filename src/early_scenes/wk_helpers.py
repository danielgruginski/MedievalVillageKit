
exec(bpy.data.texts["mc_helpers"].as_string())
SC = bpy.data.scenes["StoneWallKit"]
def col(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name); (parent or SC.collection).children.link(c)
    return c
CELL=4.0; H=4.0; T=1.4; PAR=0.45; MERL_H=0.8; PAR_H=0.55
def kit_mats():
    return [mat("WK_StoneA",(0.46,0.44,0.40),0.85), mat("WK_StoneB",(0.38,0.37,0.35),0.9), mat("WK_StoneC",(0.52,0.48,0.42),0.85),
            mat("WK_Mortar",(0.16,0.15,0.14),1.0), mat("WK_Walkway",(0.40,0.38,0.35),0.9), mat("WK_Moss",(0.26,0.34,0.14),0.9),
            mat("WK_Wood",(0.33,0.21,0.11),0.8), mat("WK_Iron",(0.20,0.20,0.22),0.45,metal=0.8), mat("WK_WoodDark",(0.18,0.11,0.06),0.8),
            mat("WK_Banner",(0.55,0.08,0.07),0.8), mat("WK_Roof",(0.40,0.17,0.10),0.7)]
STONE=(0,1,2); MORTAR=3; WALK=4; MOSS=5; WOOD=6; IRON=7; WOODD=8; BANNER=9; ROOF=10
def xf_verts(bm,vs,M):
    bmesh.ops.transform(bm,matrix=M,verts=vs)
def block_face(bm,M,length,z0,z1,seed,course_h=0.42,depth=0.14,moss_h=0.9,block_len=(0.55,0.95),u0=0.0):
    """Stone blocks on a vertical face. Local frame: u along +X from 0..length, face plane y=0, blocks protrude to -Y.
    u0 = global offset along the run so staggering matches across modules."""
    rnd=random.Random(seed)
    z=z0; i=0
    while z<z1-0.05:
        ch=min(course_h*rnd.uniform(0.85,1.15), z1-z)
        if z1-(z+ch)<0.15: ch=z1-z
        # stagger based on global u so neighbours line up
        crs=random.Random(int(z*1000)+7)
        u=-((u0+crs.uniform(0,0.8)) % 0.9)
        while u<length:
            bl=rnd.uniform(*block_len)
            a=max(0.0,u+0.025); b=min(length,u+bl-0.025)
            if b-a>0.08:
                dd=depth*rnd.uniform(0.75,1.15)
                mi=rnd.choice(STONE)
                if z<moss_h and rnd.random()<0.35*(1-z/moss_h): mi=MOSS
                vs=box(bm,((a+b)/2,-dd/2+0.02,z+ch/2),(b-a,dd,ch-0.05),mat_index=mi)
                # slight random tilt / bulge for hand-cut look
                for v in vs:
                    if v.co.y<-dd/2: v.co.y-=rnd.uniform(0,0.03); v.co.z+=rnd.uniform(-0.015,0.015)
                xf_verts(bm,vs,M)
                if M.to_3x3().determinant()<0:
                    bmesh.ops.reverse_faces(bm,faces=list({f for v in vs for f in v.link_faces}))
            u+=bl
        z+=ch; i+=1
def frame(origin,direction,normal):
    """Matrix mapping local (u along direction, -Y toward normal, z up) to world."""
    d=Vector(direction).normalized(); n=Vector(normal).normalized()
    # local -Y must map to n  -> local Y maps to -n
    m=Matrix(((d.x,-n.x,0,origin[0]),(d.y,-n.y,0,origin[1]),(0,0,1,origin[2] if len(origin)>2 else 0),(0,0,0,1)))
    return m
def wall_arm(bm,a,b,outer,height=H,seed=0,crenel=True,top=True,plinth=True):
    """Wall run from a to b (2D), outer side normal 'outer'. Core + stone facing + parapet + merlons."""
    a=Vector((*a,0)); b=Vector((*b,0)); d=(b-a); L=d.length; d.normalize()
    n=Vector((*outer,0)).normalized(); side=d.cross(Vector((0,0,1)))  # right side
    mid=(a+b)/2
    ang=math.atan2(d.y,d.x)
    u0=a.dot(d)  # global position along run for stagger
    # core (mortar)
    box(bm,(mid.x,mid.y,height/2),(L,T-0.2,height),rot_z=ang,mat_index=MORTAR)
    # plinth
    if plinth:
        box(bm,(mid.x,mid.y,0.2),(L,T+0.35,0.6),rot_z=ang,mat_index=1)
        box(bm,(mid.x,mid.y,-0.4),(L,T+0.35,0.6),rot_z=ang,mat_index=MORTAR)
    # stone facing both sides
    for s in(1,-1):
        nn=side*s
        o=a+nn*(T/2-0.1)
        # direction must keep local frame right-handed-ish: use d, normal nn
        M=frame((o.x,o.y,0),d,nn)
        block_face(bm,M,L,0.5 if plinth else 0.0,height,seed*13+(1 if s>0 else 2)+int(u0*10),u0=u0)
    if top:
        # walkway
        box(bm,(mid.x,mid.y,height+0.06),(L,T,0.12),rot_z=ang,mat_index=WALK)
        # inner curb
        ci=mid-n*(T/2-0.1)
        box(bm,(ci.x,ci.y,height+0.2),(L,0.2,0.28),rot_z=ang,mat_index=1)
        # outer parapet
        po=mid+n*(T/2-PAR/2)
        box(bm,(po.x,po.y,height+PAR_H/2+0.06),(L,PAR,PAR_H),rot_z=ang,mat_index=0)
        if crenel:
            rnd=random.Random(seed+99)
            k=math.floor(u0)
            # merlons centred on global half-metres (x.5) so modules tile
            c=math.floor(u0)+0.5
            while c<u0+L:
                if c-0.3>=u0-1e-6 and c+0.3<=u0+L+1e-6:
                    p=a+d*(c-u0)+n*(T/2-PAR/2)
                    box(bm,(p.x,p.y,height+0.06+PAR_H+MERL_H/2),(0.62,PAR,MERL_H),rot_z=ang,mat_index=rnd.choice(STONE))
                    box(bm,(p.x,p.y,height+0.06+PAR_H+MERL_H+0.04),(0.7,PAR+0.08,0.08),rot_z=ang,mat_index=1)
                c+=1.0
def pillar(bm,x,y,w=1.9,height=H+0.9,seed=0,cap=True):
    box(bm,(x,y,height/2),(w-0.2,w-0.2,height),mat_index=MORTAR)
    box(bm,(x,y,0.2),(w+0.35,w+0.35,0.6),mat_index=1)
    box(bm,(x,y,-0.4),(w+0.35,w+0.35,0.6),mat_index=MORTAR)
    for k,(dx,dy) in enumerate([(1,0),(0,1),(-1,0),(0,-1)]):
        n=Vector((dx,dy,0)); d=Vector((-dy,dx,0))
        o=Vector((x,y,0))+n*(w/2)-d*(w/2)
        M=frame((o.x,o.y,0),-d,n) if False else frame((o.x,o.y,0),d,n)
        block_face(bm,M,w,0.5,height,seed*7+k,block_len=(0.45,0.8),u0=k*0.37)
    if cap:
        box(bm,(x,y,height+0.1),(w+0.15,w+0.15,0.2),mat_index=1)
        rnd=random.Random(seed)
        for cx in(-1,1):
            for cy in(-1,1):
                box(bm,(x+cx*(w/2-0.3),y+cy*(w/2-0.3),height+0.2+0.45),(0.55,0.55,0.9),mat_index=rnd.choice(STONE))
                box(bm,(x+cx*(w/2-0.3),y+cy*(w/2-0.3),height+1.12),(0.65,0.65,0.08),mat_index=1)
def finish(name,bm,coll,loc=(0,0,0)):
    o=obj_from_bm(name,bm,kit_mats(),coll,loc=loc)
    o["kit"]="StoneWall"; o["cell_size_m"]=CELL
    return o
