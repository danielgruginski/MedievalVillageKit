# ================================================================ BUILDERS
def ind_ground_block(coll,origin,x0,x1,y0,y1,z,name="IND_Standin"):
    """stand-in terrain plateau (box with top at z, scene ground material) - demo only, not a kit piece"""
    ox,oy,orz=origin; c,s=math.cos(orz),math.sin(orz)
    bm=bmesh.new(); r=bmesh.ops.create_cube(bm,size=1.0)
    bmesh.ops.transform(bm,matrix=Matrix.Translation(((x0+x1)/2,(y0+y1)/2,(z-0.6)/2))@Matrix.Diagonal((x1-x0,y1-y0,z+0.6,1)),verts=r["verts"])
    old=bpy.data.meshes.get(name)
    if old and old.users==0: bpy.data.meshes.remove(old)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    gm=None
    for gn in ("WS_industry_Ground","VK_Ground"):
        g_=bpy.data.objects.get(gn)
        if g_ and g_.data.materials: gm=g_.data.materials[0]; break
    if gm: me.materials.append(gm)
    o=bpy.data.objects.new(name,me); coll.objects.link(o)
    o.location=(ox,oy,0); o.rotation_euler=(0,0,orz)
    return o
def ind_P(coll,origin):
    def P(n,x,y,z=0.0,r=0.0,st=None): return place_v(coll,n,x,y,z,r,origin,st or {})
    return P

def build_mine(coll,origin,seed=0):
    """mine yard, 2x2 working lot in front of the portal (the mound runs ~6 m back into the hill):
       portal at local (0,1.5) facing -Y, rails out of the tunnel curving to a buffer at +X, cart, ore/coal piles, shelter"""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    P("SM_VK_Mine_Portal",0,1.5)
    P("SM_VK_Rail_Straight",0,3.0,0,90); P("SM_VK_Rail_Straight",0,0.0,0,90)
    P("SM_VK_Rail_Curve",0,-3.0,0,-90)
    P("SM_VK_Rail_End",4.5,-4.5,0,0)
    o=P("SM_VK_Prop_Minecart",0,-0.6,IND_RAIL_TOP,90)
    o=P("SM_VK_Prop_Minecart",3.2,-4.5,IND_RAIL_TOP,rnd.uniform(-3,3))
    P("SM_VK_Pile_Ore_3",6.8,-2.2,0,20); P("SM_VK_Pile_Ore_1",2.6,-1.6,0,-40)
    P("SM_VK_Pile_Coal_2",-3.4,-2.0,0,-15)
    P("SM_VK_LeanTo",-3.6,2.2,0,-90,{"roof":"Shingle"} if bpy.data.images.get("T_VK_RoofShingle_BC") else {"roof":"Thatch"})
    P("SM_VK_Prop_Crates",-4.6,1.4,0,90); P("SM_VK_Prop_BarrelStack",-4.3,-0.3,0,90)
    P("SM_VK_Prop_LampPost",1.9,0.6,0,0)
    P("SM_VK_Prop_Woodpile",-1.6,-5.2,0,0)
    P(ind_pick("SM_VK_Pile_Logs_2","SM_VK_Prop_Woodpile"),-5.0,-4.6,0,90)

def build_quarry_yard(coll,origin,seed=0,standin=True):
    """3x3 quarry pit cut 2 LVL (3.0 m) into a plateau, open to -Y; crane on the rim hoists a block out of the pit.
       Contour pieces: back Straight + 2 InnerCorners, side Straights, front outer Corners (+ hill-front Straights at x=+-6)."""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    P("SM_VK_Quarry_Face_Straight",0,3,0,0)
    P("SM_VK_Quarry_Face_InnerCorner",3,3,0,0); P("SM_VK_Quarry_Face_InnerCorner",-3,3,0,90)
    P("SM_VK_Quarry_Face_Straight",3,0,0,-90); P("SM_VK_Quarry_Face_Straight",-3,0,0,90)
    P("SM_VK_Quarry_Face_Corner",3,-3,0,0); P("SM_VK_Quarry_Face_Corner",-3,-3,0,90)
    P("SM_VK_Quarry_Face_Straight",6,-3,0,0); P("SM_VK_Quarry_Face_Straight",-6,-3,0,0)
    P("SM_VK_Quarry_Floor",0,0,0,0); P("SM_VK_Quarry_Floor",0,-3,0,90)
    if standin:
        ind_ground_block(coll,origin,-7.5,7.5,4.5,11.0,2.99,"IND_Standin_QuarryBack")
        ind_ground_block(coll,origin,4.5,7.5,-1.5,4.5,2.99,"IND_Standin_QuarryR")
        ind_ground_block(coll,origin,-7.5,-4.5,-1.5,4.5,2.99,"IND_Standin_QuarryL")
    # crane on the back rim, jib reaching over the pit
    P("SM_VK_Prop_TreadwheelCrane",-0.6,6.9,3.0,-90)
    w=P("SM_VK_Prop_TreadwheelCrane_Wheel",-0.6,6.9+1.0,3.0+IND_CRANE_AXLE[2],-90); w["spin_axis"]="local Y"; w["rpm"]=4.0
    # mason's corner on the floor
    P("SM_VK_Prop_Banker",-0.9,-3.4,0,10)
    P(ind_pick("SM_VK_Pile_Stone_3","SM_VK_Prop_Crates"),1.6,-4.0,0,0)
    P(ind_pick("SM_VK_Prop_Wheelbarrow","SM_VK_Prop_Cart"),1.9,-1.6,0,-30)
    P("SM_VK_Prop_Grindstone",-1.9,-1.3,0,70)
    P("SM_VK_LeanTo",-6.0,-6.0,0,180,{"roof":"Thatch"})
