import os
os.chdir(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code")
p='vk_mat.py'; s=open(p,encoding='utf8').read()
rep=[
('def pbr_material(mat,prefix,tint=None,nstr=1.0,metallic=0.0,rough_mul=1.0,emission=0.0,flat=None,paint=None,spec=0.3,metal_map=False):',
 'def pbr_material(mat,prefix,tint=None,nstr=1.0,metallic=0.0,rough_mul=1.0,emission=0.0,flat=None,paint=None,spec=0.3,metal_map=False,hsv=None,jitter=0.0):'),
('''        col_out=mt.outputs[2]
    mv=nt.nodes.new("ShaderNodeMix")''','''        col_out=mt.outputs[2]
    if hsv is not None:
        # tone the painted albedo down (hue shift, saturation, value)
        hs=nt.nodes.new("ShaderNodeHueSaturation"); hs.location=(-20,460)
        hs.inputs["Hue"].default_value=hsv[0]; hs.inputs["Saturation"].default_value=hsv[1]; hs.inputs["Value"].default_value=hsv[2]
        L.new(col_out,hs.inputs["Color"]); col_out=hs.outputs[0]
    if jitter>0:
        # per-instance brightness jitter so neighbouring roofs of one colour differ slightly
        oi=nt.nodes.new("ShaderNodeObjectInfo"); oi.location=(-300,760)
        mr=nt.nodes.new("ShaderNodeMapRange"); mr.location=(-120,760)
        mr.inputs["To Min"].default_value=1.0-jitter; mr.inputs["To Max"].default_value=1.0+jitter
        L.new(oi.outputs["Random"],mr.inputs["Value"])
        mj=nt.nodes.new("ShaderNodeMix"); mj.data_type="RGBA"; mj.blend_type="MULTIPLY"; mj.inputs[0].default_value=1.0; mj.location=(60,460)
        L.new(col_out,mj.inputs[6]); L.new(mr.outputs[0],mj.inputs[7]); col_out=mj.outputs[2]
    mv=nt.nodes.new("ShaderNodeMix")'''),
(''' "M_VK_Roof_Slate":dict(prefix="T_VK_RoofSlate",nstr=1.0,rough_mul=1.15,spec=0.2),
 "M_VK_Roof_Shingle":dict(prefix="T_VK_RoofShingle",nstr=1.0,rough_mul=1.2,spec=0.15),''',''' "M_VK_Roof_Slate":dict(prefix="T_VK_RoofSlate",nstr=1.0,rough_mul=1.15,spec=0.2,jitter=0.06),
 "M_VK_Roof_Shingle":dict(prefix="T_VK_RoofShingle",nstr=1.0,rough_mul=1.2,spec=0.15,jitter=0.06),'''),
(''' "M_VK_RoofRed":dict(prefix="T_VK_RoofRed",nstr=1.0,rough_mul=1.25,spec=0.18),
 "M_VK_RoofBlue":dict(prefix="T_VK_RoofBlue",nstr=1.0,rough_mul=1.25,spec=0.18),
 "M_VK_Roof_Blue":dict(prefix="T_VK_RoofBlue",nstr=1.0,rough_mul=1.25,spec=0.18),
 "M_VK_Roof_Green":dict(prefix="T_VK_RoofGreen",nstr=1.0,rough_mul=1.2,spec=0.18),
 "M_VK_Roof_Thatch":dict(prefix="T_VK_Thatch",nstr=0.9,spec=0.1),''',''' "M_VK_RoofRed":dict(prefix="T_VK_RoofRed",nstr=1.0,rough_mul=1.25,spec=0.18,hsv=(0.5,0.78,0.93),jitter=0.06),
 "M_VK_RoofBlue":dict(prefix="T_VK_RoofBlue",nstr=1.0,rough_mul=1.25,spec=0.18,hsv=(0.5,0.62,0.95),jitter=0.06),
 "M_VK_Roof_Blue":dict(prefix="T_VK_RoofBlue",nstr=1.0,rough_mul=1.25,spec=0.18,hsv=(0.5,0.62,0.95),jitter=0.06),
 "M_VK_Roof_Green":dict(prefix="T_VK_RoofGreen",nstr=1.0,rough_mul=1.2,spec=0.18,hsv=(0.5,0.75,0.95),jitter=0.06),
 "M_VK_Roof_Thatch":dict(prefix="T_VK_Thatch",nstr=0.9,spec=0.1,jitter=0.06),'''),
]
for a,b in rep:
    assert a in s, a[:80]; s=s.replace(a,b)
open(p,'w',encoding='utf8').write(s); print("vk_mat ok")
