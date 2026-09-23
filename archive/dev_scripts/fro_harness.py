import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
SRC=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_frontier.py"

def H_push():
    src=open(SRC,encoding="utf8").read()
    t=bpy.data.texts.get("ws_frontier") or bpy.data.texts.new("ws_frontier"); t.clear(); t.write(src)

def H_clear(g):
    sc,coll,asm=ws_scene("frontier")
    mine={n for n,_,_ in g["WS_SPECS"]}
    stale=set()
    for o in list(asm.objects):
        base=o.name.split("_inst")[0]
        if o.data and o.data.name.startswith("VAR_") and base in mine: stale.add(o.data.name)
        bpy.data.objects.remove(o)
    for mn in stale:
        me=bpy.data.meshes.get(mn)
        if me and me.users==0: bpy.data.meshes.remove(me)

def H_layout(g):
    objs=[bpy.data.objects[n] for n,_,_ in g["WS_SPECS"] if bpy.data.objects.get(n)]
    ws_grid(objs,cols=6,sx=8,sy=9,origin=(-50,50))
    return objs

DEMOS={
 "cabin2":   ("build_logcabin",(-36,-10,0),dict(seed=1,n=2)),
 "cabin3":   ("build_logcabin",(-18,-10,0),dict(seed=4,n=3)),
 "woodcutter":("build_woodcutter",(2,-10,0),dict(seed=0)),
 "forester": ("build_forester_hut",(20,-10,0),dict(seed=0)),
 "granary":  ("build_granary",(36,-10,0),dict(seed=0)),
 "storehouse":("build_storehouse",(-30,-34,0),dict(seed=0)),
}
def H_demos(g,which=None):
    sc,coll,asm=ws_scene("frontier")
    for k_,(fn,o,kw) in DEMOS.items():
        if which and k_ not in which: continue
        g[fn](asm,o,**kw)

def H_all(build=True,demos=True,which=None):
    t0=time.time()
    H_push(); g=ws_ns("frontier")
    objs=ws_build("frontier",g=g) if build else None
    H_clear(g); H_layout(g)
    if demos: H_demos(g,which)
    return g,objs,round(time.time()-t0,2)
