import os
os.chdir(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code")
p='vk_mat.py'; s=open(p,encoding='utf8').read()
a='def pbr_material(mat,prefix,tint=None,nstr=1.0,metallic=0.0,rough_mul=1.0,emission=0.0,flat=None,paint=None,spec=0.3,metal_map=False,hsv=None,jitter=0.0):'
assert s.count(a)==1
s=s.replace(a,'def pbr_material(mat,prefix,tint=None,nstr=1.0,metallic=0.0,rough_mul=1.0,emission=0.0,flat=None,paint=None,spec=0.3,metal_map=False,hsv=None,jitter=0.0,wear=0.15):')
a='''        mm=nt.nodes.new("ShaderNodeMix"); mm.data_type="RGBA"; mm.blend_type="MIX"; mm.location=(-120,300)
        L.new(mk.outputs[0],mm.inputs[0]); L.new(bc.outputs[0],mm.inputs[6]); L.new(mp.outputs[2],mm.inputs[7])'''
assert s.count(a)==1
s=s.replace(a,'''        mm=nt.nodes.new("ShaderNodeMix"); mm.data_type="RGBA"; mm.blend_type="MIX"; mm.location=(-120,300)
        # wear: 1 = the painted mask as authored (chipped, lots of bare wood); small = fresh paint with only a
        # few scuffs at the very edges
        mr=nt.nodes.new("ShaderNodeMapRange"); mr.clamp=True; mr.location=(-300,600)
        mr.inputs["From Min"].default_value=0.0; mr.inputs["From Max"].default_value=max(0.02,wear)
        L.new(mk.outputs[0],mr.inputs["Value"])
        L.new(mr.outputs[0],mm.inputs[0]); L.new(bc.outputs[0],mm.inputs[6]); L.new(mp.outputs[2],mm.inputs[7])''')
a=''' "M_VK_Shutter_Natural":dict(prefix="T_VK_Wood",nstr=1.2,spec=0.15),'''
assert s.count(a)==1
s=s.replace(a,a+'''
 "M_VK_Shutter_TealWorn":dict(prefix="T_VK_PaintedWood",paint=(0.24,0.52,0.52),spec=0.2,wear=1.0),
 "M_VK_Shutter_RedWorn":dict(prefix="T_VK_PaintedWood",paint=(0.66,0.16,0.11),spec=0.2,wear=1.0),
 "M_VK_Shutter_GreenWorn":dict(prefix="T_VK_PaintedWood",paint=(0.27,0.48,0.18),spec=0.2,wear=1.0),
 "M_VK_Shutter_BlueWorn":dict(prefix="T_VK_PaintedWood",paint=(0.20,0.32,0.62),spec=0.2,wear=1.0),''')
open(p,'w',encoding='utf8').write(s)

p='vk_helpers.py'; s=open(p,encoding='utf8').read()
a=''' "shutter":{"Teal":None,"Red":("T_VK_Wood",(1.6,0.55,0.45)),"Green":("T_VK_Wood",(0.75,1.3,0.6)),"Blue":("T_VK_Wood",(0.6,0.8,1.6)),"Natural":("T_VK_Wood",(1,1,1))},'''
assert s.count(a)==1
s=s.replace(a,''' "shutter":{"Teal":None,"Red":("T_VK_Wood",(1.6,0.55,0.45)),"Green":("T_VK_Wood",(0.75,1.3,0.6)),"Blue":("T_VK_Wood",(0.6,0.8,1.6)),"Natural":("T_VK_Wood",(1,1,1)),
            "TealWorn":("T_VK_Wood",(0.6,1.2,1.2)),"RedWorn":("T_VK_Wood",(1.6,0.55,0.45)),"GreenWorn":("T_VK_Wood",(0.75,1.3,0.6)),"BlueWorn":("T_VK_Wood",(0.6,0.8,1.6))},''')
a='''    img,tint=spec
    nm=f"M_VK_{kind.capitalize()}_{name}"
    if kind=="cloth": return tex_mat(nm,None,0.9,flat=tint)
    return tex_mat(nm,img,0.8,tint=tint)'''
assert s.count(a)==1
s=s.replace(a,'''    img,tint=spec
    nm=f"M_VK_{kind.capitalize()}_{name}"
    if kind=="cloth": return tex_mat(nm,None,0.9,flat=tint)
    new=bpy.data.materials.get(nm) is None
    m=tex_mat(nm,img,0.8,tint=tint)
    mm=globals().get("MAT_MAP",{})
    if new and nm in mm and "pbr_material" in globals(): pbr_material(m,**mm[nm])     # e.g. painted/worn shutters
    return m''')
a='''            "shutter":r.choice(["Teal","Red","Green","Blue","Natural"]),
            "roof":r.choice(roofs),"seed":seed}'''
assert s.count(a)==1
s=s.replace(a,'''            "shutter":_maybe_worn(r,r.choice(["Teal","Red","Green","Blue","Natural"])),
            "roof":r.choice(roofs),"seed":seed}
def _maybe_worn(r,sh,p=0.2):
    """most houses keep fresh paint on their shutters; about one in five gets the chipped, weathered look"""
    return sh+"Worn" if sh!="Natural" and r.random()<p else sh''')
open(p,'w',encoding='utf8').write(s)
import ast
for f in ('vk_mat.py','vk_helpers.py'): ast.parse(open(f,encoding='utf8').read())
print("ok")
