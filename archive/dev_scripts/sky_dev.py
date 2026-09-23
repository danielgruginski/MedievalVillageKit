# dev loop helpers for the skyline agent (scratch only; exec'd inside Blender calls)
import bpy, bmesh, math, time
exec(bpy.data.texts["ws_common"].as_string())
SKY_SRC=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_skyline.py"

def dev_push():
    src=open(SKY_SRC,encoding="utf8").read()
    t=bpy.data.texts.get("ws_skyline") or bpy.data.texts.new("ws_skyline"); t.clear(); t.write(src)

def dev_sync():
    sc,coll,asm=ws_scene("skyline"); mine={o.name for o in coll.objects}; done=set()
    for o in asm.objects:
        if o.data and o.data.name.startswith("VAR_"):
            b=o.name.split("_inst")[0]
            if b in mine and o.data.name not in done:
                bm=bmesh.new(); bm.from_mesh(bpy.data.objects[b].data); bm.to_mesh(o.data); bm.free(); done.add(o.data.name)
    return len(done)

def dev_build(names=None,hide=True):
    dev_push(); g=ws_ns("skyline"); objs=ws_build("skyline",names=names,g=g)
    sc,coll,asm=ws_scene("skyline")
    if hide:
        for o in coll.objects: o.hide_render=True; o.hide_viewport=True
    dev_sync(); return g,objs

def dev_show_asm(show=True):
    sc,coll,asm=ws_scene("skyline")
    for o in asm.objects: o.hide_render=not show; o.hide_viewport=not show

def dev_catalog(rows,y0=-30.0,sx=7.0,sy=9.0,x0=0.0):
    """rows: list of (list of piece names, z lift). places masters in a grid, returns list"""
    sc,coll,asm=ws_scene("skyline")
    for o in coll.objects: o.hide_render=True; o.hide_viewport=True
    placed=[]
    for r,(names,lift) in enumerate(rows):
        for i,n in enumerate(names):
            o=bpy.data.objects[n]; o.hide_render=False; o.hide_viewport=False
            o.location=(x0+i*sx,y0-r*sy,lift); o.rotation_euler=(0,0,0); placed.append(o)
    return placed
