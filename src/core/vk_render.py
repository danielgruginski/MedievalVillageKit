import bpy, os
from mathutils import Vector
VK_ROOT=r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit"     # project folder (see HANDOFF.md)
OUTD=os.path.join(VK_ROOT,"renders","wip")                             # default folder for shot()
def shot(name,loc,target,lens=35,res=(1280,720),scene="VillageKit",samples=None,outdir=None):
    sc=bpy.data.scenes[scene]
    cam=bpy.data.objects.get("VK_CamTmp")
    if cam is None:
        cam=bpy.data.objects.new("VK_CamTmp",bpy.data.cameras.new("VK_CamTmp"))
    if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)
    cam.location=loc; cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=lens; cam.data.clip_end=3000
    old=(sc.camera,sc.render.resolution_x,sc.render.resolution_y,sc.render.filepath,sc.render.resolution_percentage)
    sc.camera=cam; sc.render.resolution_x,sc.render.resolution_y=res; sc.render.resolution_percentage=100
    d=outdir or OUTD; os.makedirs(d,exist_ok=True); sc.render.filepath=os.path.join(d,name+".png")
    if samples: old_s=sc.eevee.taa_render_samples; sc.eevee.taa_render_samples=samples
    bpy.ops.render.render(write_still=True,scene=sc.name)
    if samples: sc.eevee.taa_render_samples=old_s
    fp=sc.render.filepath
    sc.camera,sc.render.resolution_x,sc.render.resolution_y,sc.render.filepath,sc.render.resolution_percentage=old
    return fp
bpy.app.driver_namespace["shot"]=shot
