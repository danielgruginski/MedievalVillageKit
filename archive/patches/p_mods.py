import os
os.chdir(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code")
def patch(p,rep):
    s=open(p,encoding='utf8').read()
    for a,b in rep:
        assert s.count(a)==1, (p,a[:80],s.count(a)); s=s.replace(a,b)
    open(p,'w',encoding='utf8').write(s); print(p,"ok")

patch('vk_mod_defence.py',[
('''def def_townwall_straight(k):
    def_tw_module(k,seed=4); def_tw_wobble(k)
''','''def def_townwall_straight(k):
    def_tw_module(k,seed=4); def_tw_wobble(k)

def def_townwall_postern(k):
    """3 m town-wall module with a 2.0 x 2.7 m postern passage: flat ASHLAR lintel under a relieving arch on both faces,
    quoined jambs that follow the batter, flagged floor, two plank leaves standing open against the jambs"""
    b=set(k.bm.verts)
    stone_panel(k,-1.5,-1.0,-1.5,6.05,-1.0,1.0); stone_panel(k,1.0,1.5,-1.5,6.05,-1.0,1.0)
    stone_panel(k,-1.0,1.0,2.7,6.05,-1.0,1.0); stone_panel(k,-1.0,1.0,-1.5,-0.03,-1.0,1.0)
    def_tw_batter(def_new_verts(k,b))
    for y in (-1.0,1.0):
        s_=1 if y>0 else -1
        k.box((0,y+s_*0.04,2.86),(2.55,0.14,0.34),ASHLAR,bevel=0.03)
        for i in range(7):
            a=math.pi*(i+0.5)/7
            k.box((math.cos(a)*1.2,y+s_*0.03,3.05+math.sin(a)*0.85),(0.26,0.12,0.36 if i!=3 else 0.44),STONE_BLOCK,rot=(0,-(a-math.pi/2),0),bevel=0.03)
        for j in range(5):
            zz=0.3+0.5*j; w=0.36 if j%2 else 0.26
            bt=0.35*max(0.0,min(1.0,(1.8-zz)/1.8)) if y<0 else 0.0
            for sx in (-1,1): k.box((sx*(1.0+w/2-0.05),y+s_*(0.04+bt),zz),(w,0.12,0.46),STONE_BLOCK,bevel=0.03)
    rnd=random.Random(41)
    for i in range(3):
        for j in range(4):
            k.box((-0.64+0.64*i+rnd.uniform(-0.03,0.03),-1.05+0.6*j+rnd.uniform(-0.03,0.03),0.02),(0.58,0.54,0.09),ASHLAR,bevel=0.025)
    for sx in (-1,1):
        k.box((sx*0.93,0.25,1.32),(0.07,0.92,2.6),PLANKS,bevel=0.015)
        for zz in (0.45,2.2): k.box((sx*0.89,0.25,zz),(0.03,0.86,0.1),IRON,bevel=0.01)
    def_tw_top(k,-1.5,1.5,(-0.75,0.75),seed=7)
    def_tw_plinth(k,-1.5,-1.05,seed=51); def_tw_plinth(k,1.05,1.5,seed=53)
    def_tw_wobble(k)
'''),
('''    ("SM_VK_TownWall_Straight",def_townwall_straight,dict(wobble=False,grime=True)),
''','''    ("SM_VK_TownWall_Straight",def_townwall_straight,dict(wobble=False,grime=True)),
    ("SM_VK_TownWall_Postern",def_townwall_postern,dict(wobble=False,grime=True)),
'''),
])
patch('vk_mod_construction.py',[
('''            place_v(coll, f"SM_VK_Pile_{kind}_{lvl}", x, y, 0, r.choice((0, 90, 180, 270)), origin, {})''',
 '''            o = place_v(coll, f"SM_VK_Pile_{kind}_{lvl}", x, y, 0, r.choice((0, 180)), origin, {})
            if o is not None: o.scale = (0.88, 0.88, 1.0)      # keep the pile inside the border kerb'''),
])
