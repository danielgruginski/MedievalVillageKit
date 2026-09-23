def ind_sub_origin(origin,x,y,rot_deg=0.0):
    ox,oy,orz=origin; c,s=math.cos(orz),math.sin(orz)
    return (ox+x*c-y*s,oy+x*s+y*c,orz+math.radians(rot_deg))
def ind_opt(P,name,*a,**kw):
    """place a piece only if it exists (other agents' pieces)"""
    if bpy.data.objects.get(name): return P(name,*a,**kw)
    return None

def build_charcoal_burner(coll,origin,seed=0):
    """two 2x2 lots side by side (12 x 6 m): charcoal clamp + wood stack (x<0), bloomery + bellows + ore/coal (x>0)"""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    P("SM_VK_Prop_CharcoalMound",-3.2,0.5,0,rnd.uniform(0,40))
    P("SM_VK_Prop_Woodpile",-3.4,-2.75,0,0)
    P("SM_VK_Pile_Coal_1",-0.9,2.3,0,-20)
    ind_opt(P,"SM_VK_Pile_Logs_3",-5.2,-1.2,0,90)
    P("SM_VK_Prop_Bloomery",2.9,0.9,0,0)
    P("SM_VK_Prop_Bellows",5.65,0.9,0,0)
    P("SM_VK_Prop_Anvil",1.2,-1.9,0,25)
    P("SM_VK_Prop_Trough",4.9,-1.1,0,90)
    P("SM_VK_Pile_Ore_2",4.4,-3.2,0,15)
    P("SM_VK_Pile_Coal_2",1.3,3.3,0,180)
    P("SM_VK_Prop_Grindstone",0.2,-3.3,0,-30)

def build_tannery(coll,origin,seed=0):
    """4x3 lot (12 x 9): 2-cell daub workshop with lean-to shed on its +X end, 4 tanning pits in front, hide frames, hide piles"""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    st={"ground":"Plaster","plaster":"Daub","shutter":"Natural","roof":"Thatch","seed":seed+71}
    ho=ind_sub_origin(origin,-3.0,1.5,0)
    build_house_v(coll,ho,2,1,st,front="DW",back="..",chimney=False)
    Ph=ind_P(coll,ho)
    for yy in(-1.5,1.5): Ph("SM_VK_LeanTo",3.0,-yy,0,90,{"roof":"Thatch"})
    ind_opt(Ph,"SM_VK_Roof_Vent",-1.5,0,H1+RIDGE,0,st)
    for i,(x,y) in enumerate(((-4.4,-3.4),(-2.2,-3.4),(0.0,-3.4),(2.2,-3.4))): P("SM_VK_Prop_TanningPit",x,y,0,rnd.choice((0,90,180,270)))
    for i,x in enumerate((4.0,5.6)): P("SM_VK_Prop_HideFrame",x,-3.0+0.4*i,0,-8+16*i)
    P("SM_VK_Prop_HideFrame",4.8,-0.3,0,90)
    P("SM_VK_Pile_Hides_3",1.8,1.6,0,90)
    P("SM_VK_Pile_Hides_1",4.9,3.4,0,10)
    P("SM_VK_Prop_BarrelStack",2.0,4.0,0,0)
    P("SM_VK_Prop_Trough",4.3,1.4,0,90)
    P("SM_VK_Prop_Cauldron",-5.4,-1.2,0,0)

def build_dyers_yard(coll,origin,seed=0):
    """3x2 lot (9 x 6): four dye vats in different cloth colours, two drying racks, laundry line, wool, spinning wheel"""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    cols=["Red","Blue","Yellow","Purple","Green"]; rnd.shuffle(cols)
    for i,x in enumerate((-3.3,-1.6,0.1,1.8)):
        P("SM_VK_Prop_DyeVat",x,-2.1+0.25*(i%2),0,rnd.uniform(-25,25),{"cloth":cols[i]})
    P("SM_VK_Prop_ClothRack",-1.8,1.3,0,0,{"cloth":cols[0]})
    P("SM_VK_Prop_ClothRack",2.2,1.9,0,-12,{"cloth":cols[1]})
    P("SM_VK_Prop_Laundry",-1.0,-0.4,0,0)
    P("SM_VK_Prop_Cauldron",3.6,-1.7,0,0)
    P("SM_VK_Pile_Wool_2",-3.9,2.4,0,90)
    P("SM_VK_Prop_SpinningWheel",4.0,0.2,0,-120)
    P("SM_VK_Prop_Stool",3.45,0.55,0,0)

def build_brewery(coll,origin,seed=0):
    """5x3 lot (15 x 9): 3x2 stone brew-house range + round oast with a white cowl at its +X end, mash tun, barrels, hop field"""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    st={"ground":"Stone","plaster":"White","shutter":"Green","roof":"Red","seed":seed+13}
    ho=ind_sub_origin(origin,-3.0,1.0,0)
    build_house_v(coll,ho,3,2,st,front="WDW",back="W..",chimney=True)
    P("SM_VK_Kiln_Oast",4.0,1.2,0,0,{"plaster":"White","roof":"Red"})
    P("SM_VK_Prop_MashTun",4.9,-3.1,0,0)
    P("SM_VK_Prop_BarrelStack",-5.8,-3.0,0,0); P("SM_VK_Prop_BarrelStack",-2.6,-3.4,0,15)
    P("SM_VK_Prop_Sacks",2.4,-1.9,0,0); P("SM_VK_Prop_Cart",0.6,-3.6,0,-10)
    hop=ind_pick("SM_VK_Crop_Hops","SM_VK_Crop_Wheat")
    for x in(7.8,10.9): P(hop,x,1.2,0,0)
    ind_opt(P,"SM_VK_Emblem_Ridge_Tankard",-3.0,1.0,H1+H2+RIDGE,0)

def build_apiary(coll,origin,seed=0):
    """2x2 lot (6 x 6): two bee benches in front of lavender rows, loose skeps on stands"""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    for x in(-1.5,1.5): P("SM_VK_Crop_Lavender",x,1.5,0,0)
    for x in(-1.5,1.5): P("SM_VK_Prop_BeeBench",x,-1.1,0,rnd.uniform(-6,6))
    for i,x in enumerate((-2.3,0.0,2.3)):
        P("SM_VK_Prop_Stool",x,-2.6,0,0); P("SM_VK_Prop_Skep",x,-2.6,0.54,rnd.uniform(0,360))
    P("SM_VK_Prop_Bench",0.0,-3.8,0,180)

def build_pottery(coll,origin,seed=0):
    """3x3 lot (9 x 9): bottle kiln, clay pit, potter's wheel at a work table, brick and coal piles"""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    P("SM_VK_Prop_BottleKiln",-2.0,1.6,0,rnd.uniform(-20,20))
    P("SM_VK_Prop_ClayPit",3.0,3.0,0,0)
    P("SM_VK_Prop_PottersWheel",2.4,-1.0,0,180)
    P("SM_VK_Prop_Table",3.4,-2.9,0,0)
    P("SM_VK_Pile_Bricks_3",-2.4,-3.4,0,0)
    P("SM_VK_Pile_Bricks_1",0.4,-3.6,0,20)
    P("SM_VK_Pile_Coal_2",-4.6,-1.6,0,70)
    P("SM_VK_Prop_Woodpile",-5.0,3.4,0,90)
    ind_opt(P,"SM_VK_Prop_ShopGoods_Pots",4.6,-0.6,0,-90)
