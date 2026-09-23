# scratch helper for the defence agent (exec'd inside execute_blender_code). Uses only ws_common API.
import bpy, time, traceback
exec(bpy.data.texts["ws_common"].as_string())
DEF_SRC=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_defence.py"
def D_push():
    src=open(DEF_SRC,encoding="utf8").read()
    t=bpy.data.texts.get("ws_defence") or bpy.data.texts.new("ws_defence"); t.clear(); t.write(src)
D_JOBS={"pal":("build_palisade_demo",(-40,36,0),{}),"tw":("build_townwall_demo",(8,26,0),{}),
        "th":("build_tower_house",(4,42,0),{}),"ty":("build_training_yard",(-19,31,0),{}),
        "fg":("build_festival_green",(17,42,0),{}),"th2":("build_tower_house",(36,38,0),{"kind":"domestic","seed":3})}
def D_all(pieces=None,asm_jobs=("pal","tw","th","ty","fg","th2"),push=True):
    if push: D_push()
    g=ws_ns("defence"); sc,coll,asm=ws_scene("defence")
    if pieces is not False:
        objs=ws_build("defence",names=pieces,g=g)
    allp=[bpy.data.objects[s[0]] for s in g["WS_SPECS"]]
    D_layout()
    if asm_jobs:
        ws_clear_assembly("defence")
        for key in asm_jobs:
            fn,org,kw=D_JOBS[key]
            try: g[fn](asm,org,**kw)
            except Exception: print(fn,"ERR",traceback.format_exc()[-900:])
    return g
D_ROWS=[(-19.0,["TownWall_Tower_Round","Gatehouse_Block","Palisade_Tower","Prop_Beacon","Prop_Maypole"]),
        (-31.0,["Palisade_Post","Palisade_Straight","Palisade_Gate","Palisade_Diag","Palisade_Walk","Palisade_Ladder",
                "TownWall_Corner_Out","TownWall_Straight","TownWall_Step","TownWall_Stair","TownWall_Ruin","TownWall_Corner_In"]),
        (-40.5,["Palisade_GateLeaf","Gatehouse_GateLeaf","Gatehouse_Portcullis","Roof_Cone_R2","Roof_Pyramid_6","Parapet_Corner","Parapet_Crenel",
                "Def_Bartizan","Def_CornerUp","Def_StoneUp","Def_StoneUp_Slit","Def_StoneUp_Window","Def_StoneUp_Door"]),
        (-49.5,["Prop_TrainingDummy","Prop_ArcheryButt","Prop_ArmorStand","Prop_Stocks","Prop_Pillory","Prop_MarketCross","Prop_Stage","LowWall_GateArch","Deco_Hedge","Def_Standin_Ramp","Def_Standin_Plateau"])]
def D_layout(gap=1.3,cx=0.0):
    from mathutils import Vector
    for y,names in D_ROWS:
        objs=[bpy.data.objects["SM_VK_"+n] for n in names]
        spans=[]
        for o in objs:
            xs=[Vector(c).x for c in o.bound_box]; spans.append((min(xs),max(xs)))
        W=sum(b-a for a,b in spans)+gap*(len(objs)-1); x=cx-W/2
        for o,(a,b) in zip(objs,spans):
            o.location=(x-a,y,1.5 if "Standin" in o.name else 0); o.rotation_euler=(0,0,0); x+=b-a+gap
