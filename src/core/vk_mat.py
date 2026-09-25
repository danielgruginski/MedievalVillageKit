
def pbr_material(mat,prefix,tint=None,nstr=1.0,metallic=0.0,rough_mul=1.0,emission=0.0,flat=None,paint=None,spec=0.3,metal_map=False,hsv=None,jitter=0.0,wear=0.15):
    mat.use_nodes=True; nt=mat.node_tree; nt.nodes.clear(); L=nt.links
    out=nt.nodes.new("ShaderNodeOutputMaterial"); out.location=(900,0)
    b=nt.nodes.new("ShaderNodeBsdfPrincipled"); b.location=(550,0)
    uv=nt.nodes.new("ShaderNodeUVMap"); uv.uv_map="UVMap"; uv.location=(-900,0)
    def tex(suffix,y):
        n=nt.nodes.new("ShaderNodeTexImage"); n.image=bpy.data.images[prefix+suffix]; n.location=(-650,y)
        L.new(uv.outputs[0],n.inputs[0]); return n
    bc=tex("_BC",300); nm=tex("_N",-300); rg=tex("_R",0)
    vc=nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name="Col"; vc.location=(-300,500)
    col_out=bc.outputs[0]
    if flat is not None:
        # flat colour, modulated by the texture's value so the painted shading survives
        bw=nt.nodes.new("ShaderNodeRGBToBW"); bw.location=(-350,300); L.new(bc.outputs[0],bw.inputs[0])
        mf=nt.nodes.new("ShaderNodeMix"); mf.data_type="RGBA"; mf.blend_type="MULTIPLY"; mf.inputs[0].default_value=1.0
        mf.inputs[6].default_value=(*flat,1); L.new(bw.outputs[0],mf.inputs[7]); mf.location=(-150,300)
        col_out=mf.outputs[2]
    elif paint is not None:
        mk=tex("_Mask",600)
        mp=nt.nodes.new("ShaderNodeMix"); mp.data_type="RGBA"; mp.blend_type="MULTIPLY"; mp.inputs[0].default_value=1.0
        L.new(bc.outputs[0],mp.inputs[6]); mp.inputs[7].default_value=(*paint,1); mp.location=(-300,300)
        mm=nt.nodes.new("ShaderNodeMix"); mm.data_type="RGBA"; mm.blend_type="MIX"; mm.location=(-120,300)
        # wear: 1 = the painted mask as authored (chipped, lots of bare wood); small = fresh paint with only a
        # few scuffs at the very edges
        mr=nt.nodes.new("ShaderNodeMapRange"); mr.clamp=True; mr.location=(-300,600)
        mr.inputs["From Min"].default_value=0.0; mr.inputs["From Max"].default_value=max(0.02,wear)
        L.new(mk.outputs[0],mr.inputs["Value"])
        L.new(mr.outputs[0],mm.inputs[0]); L.new(bc.outputs[0],mm.inputs[6]); L.new(mp.outputs[2],mm.inputs[7])
        col_out=mm.outputs[2]
    elif tint is not None:
        mt=nt.nodes.new("ShaderNodeMix"); mt.data_type="RGBA"; mt.blend_type="MULTIPLY"; mt.inputs[0].default_value=1.0
        L.new(bc.outputs[0],mt.inputs[6]); mt.inputs[7].default_value=(*tint,1); mt.location=(-150,300)
        col_out=mt.outputs[2]
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
    mv=nt.nodes.new("ShaderNodeMix"); mv.data_type="RGBA"; mv.blend_type="MULTIPLY"; mv.inputs[0].default_value=1.0; mv.location=(150,300)
    L.new(col_out,mv.inputs[6]); L.new(vc.outputs[0],mv.inputs[7]); L.new(mv.outputs[2],b.inputs["Base Color"])
    rm=nt.nodes.new("ShaderNodeMath"); rm.operation="MULTIPLY"; rm.inputs[1].default_value=rough_mul; rm.location=(150,0)
    L.new(rg.outputs[0],rm.inputs[0]); L.new(rm.outputs[0],b.inputs["Roughness"])
    nmap=nt.nodes.new("ShaderNodeNormalMap"); nmap.uv_map="UVMap"; nmap.inputs["Strength"].default_value=nstr; nmap.location=(150,-300)
    L.new(nm.outputs[0],nmap.inputs["Color"]); L.new(nmap.outputs[0],b.inputs["Normal"])
    if metal_map:
        mm_=tex("_M",-600); L.new(mm_.outputs[0],b.inputs["Metallic"])
    else: b.inputs["Metallic"].default_value=metallic
    b.inputs["Specular IOR Level"].default_value=spec
    if emission>0:
        L.new(col_out,b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value=emission
    L.new(b.outputs[0],out.inputs[0])
    return mat
MAT_MAP={
 "M_VK_Stone":dict(prefix="T_VK_Stone",nstr=1.0),
 "M_VK_StoneBlock":dict(prefix="T_VK_StoneBlock",nstr=0.8,spec=0.25),
 "M_VK_StoneDressed":dict(prefix="T_VK_StoneBlock",tint=(0.62,0.52,0.44),nstr=0.8,spec=0.25),
 "M_VK_FieldStone":dict(prefix="T_VK_FieldStone",nstr=1.1),
 "M_VK_Stone_Field":dict(prefix="T_VK_FieldStone",nstr=1.1),
 "M_VK_Stone_Warm":dict(prefix="T_VK_Stone",tint=(1.04,1.0,0.94),nstr=1.0),
 "M_VK_Stone_Cool":dict(prefix="T_VK_Stone",tint=(0.95,0.98,1.03),nstr=1.0),
 "M_VK_Stone_Dark":dict(prefix="T_VK_Stone",tint=(0.88,0.88,0.88),nstr=1.0),
 "M_VK_Wattle":dict(prefix="T_VK_Wattle",nstr=1.1,spec=0.15),
 "M_VK_Roof_Slate":dict(prefix="T_VK_RoofSlate",nstr=1.0,rough_mul=1.15,spec=0.2,jitter=0.06),
 "M_VK_Roof_Shingle":dict(prefix="T_VK_RoofShingle",nstr=1.0,rough_mul=1.2,spec=0.15,jitter=0.06),
 "M_VK_Ashlar":dict(prefix="T_VK_Ashlar",nstr=1.1),
 "M_VK_Plaster":dict(prefix="T_VK_Plaster"),
 "M_VK_Plaster_White":dict(prefix="T_VK_Plaster",tint=(1.06,1.08,1.12)),
 "M_VK_Plaster_Ochre":dict(prefix="T_VK_Plaster",tint=(1.03,0.84,0.56)),
 "M_VK_Plaster_Rose":dict(prefix="T_VK_Plaster",tint=(1.03,0.82,0.76)),
 "M_VK_Wood":dict(prefix="T_VK_Wood",nstr=1.2,spec=0.15),
 "M_VK_Planks":dict(prefix="T_VK_Planks",nstr=1.2,spec=0.15),
 "M_VK_RoofRed":dict(prefix="T_VK_RoofRed",nstr=1.0,rough_mul=1.25,spec=0.18,hsv=(0.5,0.78,0.93),jitter=0.06),
 "M_VK_RoofBlue":dict(prefix="T_VK_RoofBlue",nstr=1.0,rough_mul=1.25,spec=0.18,hsv=(0.5,0.62,0.95),jitter=0.06),
 "M_VK_Roof_Blue":dict(prefix="T_VK_RoofBlue",nstr=1.0,rough_mul=1.25,spec=0.18,hsv=(0.5,0.62,0.95),jitter=0.06),
 "M_VK_Roof_Green":dict(prefix="T_VK_RoofGreen",nstr=1.0,rough_mul=1.2,spec=0.18,hsv=(0.5,0.75,0.95),jitter=0.06),
 "M_VK_Roof_Thatch":dict(prefix="T_VK_Thatch",nstr=0.9,spec=0.1,jitter=0.06),
 "M_VK_Thatch":dict(prefix="T_VK_Thatch",nstr=0.9,spec=0.1),
 "M_VK_Window":dict(prefix="T_VK_Window",spec=0.5),
 "M_VK_Stained":dict(prefix="T_VK_Stained",emission=0.5,spec=0.5),
 "M_VK_Iron":dict(prefix="T_VK_Iron",metal_map=True),
 "M_VK_Bronze":dict(prefix="T_VK_Iron",flat=(3.4,2.2,0.95),metallic=1.0,rough_mul=0.75),
 "M_VK_Steel":dict(prefix="T_VK_Iron",flat=(1.6,1.65,1.75),metallic=0.9,rough_mul=0.6),
 "M_VK_Shutter_Teal":dict(prefix="T_VK_PaintedWood",paint=(0.24,0.52,0.52),spec=0.2),
 "M_VK_Shutter_Red":dict(prefix="T_VK_PaintedWood",paint=(0.66,0.16,0.11),spec=0.2),
 "M_VK_Shutter_Green":dict(prefix="T_VK_PaintedWood",paint=(0.27,0.48,0.18),spec=0.2),
 "M_VK_Shutter_Blue":dict(prefix="T_VK_PaintedWood",paint=(0.20,0.32,0.62),spec=0.2),
 "M_VK_Shutter_Natural":dict(prefix="T_VK_Wood",nstr=1.2,spec=0.15),
 "M_VK_Shutter_TealWorn":dict(prefix="T_VK_PaintedWood",paint=(0.24,0.52,0.52),spec=0.2,wear=1.0),
 "M_VK_Shutter_RedWorn":dict(prefix="T_VK_PaintedWood",paint=(0.66,0.16,0.11),spec=0.2,wear=1.0),
 "M_VK_Shutter_GreenWorn":dict(prefix="T_VK_PaintedWood",paint=(0.27,0.48,0.18),spec=0.2,wear=1.0),
 "M_VK_Shutter_BlueWorn":dict(prefix="T_VK_PaintedWood",paint=(0.20,0.32,0.62),spec=0.2,wear=1.0),
 "M_VK_Cloth_Red":dict(prefix="T_VK_Cloth",tint=(0.70,0.12,0.09),spec=0.2),
 "M_VK_Cloth_Cream":dict(prefix="T_VK_Cloth",tint=(1.0,0.93,0.74),spec=0.2),
 "M_VK_Cloth_Blue":dict(prefix="T_VK_Cloth",tint=(0.14,0.25,0.62),spec=0.2),
 "M_VK_Cloth_Green":dict(prefix="T_VK_Cloth",tint=(0.17,0.45,0.14),spec=0.2),
 "M_VK_Cloth_Yellow":dict(prefix="T_VK_Cloth",tint=(0.95,0.70,0.14),spec=0.2),
 "M_VK_Burlap":dict(prefix="T_VK_Burlap",spec=0.1),
 "M_VK_Hay":dict(prefix="T_VK_Straw",spec=0.1),
 "M_VK_Soil":dict(prefix="T_VK_Soil",spec=0.1),
 "M_VK_Paper":dict(prefix="T_VK_Paper",spec=0.1),
 "M_VK_Water":dict(prefix="T_VK_Water",nstr=0.6,spec=0.6),
 "M_VK_Rock":dict(prefix="T_VK_Rock",nstr=1.2),
 "M_VK_Clock":dict(prefix="T_VK_Clock",nstr=0.8),
 "M_VK_Clay":dict(prefix="T_VK_Plaster",tint=(0.56,0.42,0.35),nstr=0.8),
}
def tone_material(name,hsv,img_hint=None):
    """insert (or update) a Hue/Saturation node labelled TONE after a material's first image texture"""
    m=bpy.data.materials.get(name)
    if m is None or not m.use_nodes: return None
    nt=m.node_tree; hs=next((n for n in nt.nodes if n.label=="TONE"),None)
    if hs is None:
        tex=next(n for n in nt.nodes if n.type=="TEX_IMAGE" and n.image and (img_hint is None or img_hint in n.image.name))
        outs=[l.to_socket for l in nt.links if l.from_socket==tex.outputs["Color"]]
        hs=nt.nodes.new("ShaderNodeHueSaturation"); hs.label="TONE"; hs.location=(tex.location.x+280,tex.location.y+200)
        for l in [l for l in nt.links if l.from_socket==tex.outputs["Color"]]: nt.links.remove(l)
        nt.links.new(tex.outputs["Color"],hs.inputs["Color"])
        for s in outs: nt.links.new(hs.outputs[0],s)
    hs.inputs["Hue"].default_value,hs.inputs["Saturation"].default_value,hs.inputs["Value"].default_value=hsv
    return hs
TONE_MAP={"M_VK_Foliage":((0.51,0.6,1.15),"Foliage")}      # kit hedges/ivy/turf toned toward the terrain grass
def apply_pbr_all():
    for mn,kw in MAT_MAP.items():
        m=bpy.data.materials.get(mn)
        if m: pbr_material(m,**kw)
    for mn,(hsv,hint) in TONE_MAP.items(): tone_material(mn,hsv,hint)
    v=bpy.data.materials.get("M_VK_Void") or bpy.data.materials.new("M_VK_Void")
    v.use_nodes=True; nt=v.node_tree; nt.nodes.clear()
    o=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value=(0.015,0.012,0.01,1); b.inputs["Roughness"].default_value=1.0; b.inputs["Specular IOR Level"].default_value=0.0
    nt.links.new(b.outputs[0],o.inputs[0]); v.diffuse_color=(0.015,0.012,0.01,1)

def leaf_material(name="M_VK_Leaves",atlas="T_VK_Leaves"):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); L=nt.links
    o=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled")
    uv=nt.nodes.new("ShaderNodeUVMap"); uv.uv_map="UVMap"
    tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=bpy.data.images[atlas+"_BCA"]; L.new(uv.outputs[0],tx.inputs[0])
    th=nt.nodes.new("ShaderNodeTexImage"); th.image=bpy.data.images[atlas+"_H"]; th.image.colorspace_settings.name="Non-Color"; L.new(uv.outputs[0],th.inputs[0])
    vc=nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name="Col"
    mx=nt.nodes.new("ShaderNodeMix"); mx.data_type="RGBA"; mx.blend_type="MULTIPLY"; mx.inputs[0].default_value=1
    L.new(tx.outputs["Color"],mx.inputs[6]); L.new(vc.outputs[0],mx.inputs[7]); L.new(mx.outputs[2],b.inputs["Base Color"])
    geo=nt.nodes.new("ShaderNodeNewGeometry")
    mul=nt.nodes.new("ShaderNodeMath"); mul.operation="MULTIPLY_ADD"; mul.inputs[1].default_value=-2; mul.inputs[2].default_value=1
    L.new(geo.outputs["Backfacing"],mul.inputs[0])
    sc=nt.nodes.new("ShaderNodeVectorMath"); sc.operation="SCALE"
    L.new(geo.outputs["Normal"],sc.inputs[0]); L.new(mul.outputs[0],sc.inputs["Scale"])
    bump=nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=0.35; bump.inputs["Distance"].default_value=0.02
    L.new(th.outputs["Color"],bump.inputs["Height"]); L.new(sc.outputs[0],bump.inputs["Normal"])
    L.new(bump.outputs[0],b.inputs["Normal"])
    b.inputs["Roughness"].default_value=0.62; b.inputs["Specular IOR Level"].default_value=0.25
    tr=nt.nodes.new("ShaderNodeBsdfTranslucent"); L.new(mx.outputs[2],tr.inputs["Color"])
    neg=nt.nodes.new("ShaderNodeVectorMath"); neg.operation="SCALE"; neg.inputs["Scale"].default_value=-1
    L.new(bump.outputs[0],neg.inputs[0]); L.new(neg.outputs[0],tr.inputs["Normal"])
    ms=nt.nodes.new("ShaderNodeMixShader"); ms.inputs[0].default_value=0.28
    L.new(b.outputs[0],ms.inputs[1]); L.new(tr.outputs[0],ms.inputs[2])
    gt=nt.nodes.new("ShaderNodeMath"); gt.operation="GREATER_THAN"; gt.inputs[1].default_value=0.5
    L.new(tx.outputs["Alpha"],gt.inputs[0])
    tp=nt.nodes.new("ShaderNodeBsdfTransparent"); ms2=nt.nodes.new("ShaderNodeMixShader")
    L.new(gt.outputs[0],ms2.inputs[0]); L.new(tp.outputs[0],ms2.inputs[1]); L.new(ms.outputs[0],ms2.inputs[2]); L.new(ms2.outputs[0],o.inputs[0])
    m.use_backface_culling=False
    try: m.surface_render_method="DITHERED"
    except: pass
    return m
def mossy_material(name,base_prefix,moss_prefix="T_VK_Moss",base_tile=1.5,moss_tile=1.0,thresh=0.52,soft=0.14,noise_amt=0.5,nstr=1.1):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); L=nt.links
    o=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled")
    uv=nt.nodes.new("ShaderNodeUVMap"); uv.uv_map="UVMap"
    mp=nt.nodes.new("ShaderNodeMapping"); s_=base_tile/moss_tile; mp.inputs["Scale"].default_value=(s_,s_,1)
    L.new(uv.outputs[0],mp.inputs[0])
    def tex(img,src,data=False):
        n=nt.nodes.new("ShaderNodeTexImage"); n.image=bpy.data.images[img]
        if data: n.image.colorspace_settings.name="Non-Color"
        L.new(src,n.inputs[0]); return n
    bbc=tex(base_prefix+"_BC",uv.outputs[0]); bn=tex(base_prefix+"_N",uv.outputs[0],True); br=tex(base_prefix+"_R",uv.outputs[0],True)
    mbc=tex(moss_prefix+"_BC",mp.outputs[0]); mn=tex(moss_prefix+"_N",mp.outputs[0],True); mr=tex(moss_prefix+"_R",mp.outputs[0],True); mh=tex(moss_prefix+"_H",mp.outputs[0],True)
    geo=nt.nodes.new("ShaderNodeNewGeometry"); sep=nt.nodes.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"],sep.inputs[0])
    hh=nt.nodes.new("ShaderNodeMath"); hh.operation="MULTIPLY_ADD"; hh.inputs[1].default_value=noise_amt; hh.inputs[2].default_value=-0.5*noise_amt
    L.new(mh.outputs["Color"],hh.inputs[0])
    add=nt.nodes.new("ShaderNodeMath"); add.operation="ADD"; L.new(sep.outputs["Z"],add.inputs[0]); L.new(hh.outputs[0],add.inputs[1])
    mr_=nt.nodes.new("ShaderNodeMapRange"); mr_.interpolation_type="SMOOTHSTEP"
    mr_.inputs["From Min"].default_value=thresh-soft; mr_.inputs["From Max"].default_value=thresh+soft
    L.new(add.outputs[0],mr_.inputs["Value"])
    vc=nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name="Col"
    gate=nt.nodes.new("ShaderNodeMath"); gate.operation="MULTIPLY"; L.new(mr_.outputs["Result"],gate.inputs[0]); L.new(vc.outputs["Alpha"],gate.inputs[1])
    def mix(a,bb_,dtype="RGBA"):
        n=nt.nodes.new("ShaderNodeMix"); n.data_type=dtype; L.new(gate.outputs[0],n.inputs[0])
        if dtype=="RGBA": L.new(a,n.inputs[6]); L.new(bb_,n.inputs[7]); return n.outputs[2]
        L.new(a,n.inputs[2]); L.new(bb_,n.inputs[3]); return n.outputs[0]
    col=mix(bbc.outputs[0],mbc.outputs[0])
    mv=nt.nodes.new("ShaderNodeMix"); mv.data_type="RGBA"; mv.blend_type="MULTIPLY"; mv.inputs[0].default_value=1
    L.new(col,mv.inputs[6]); L.new(vc.outputs[0],mv.inputs[7]); L.new(mv.outputs[2],b.inputs["Base Color"])
    rough=mix(br.outputs[0],mr.outputs[0]); L.new(rough,b.inputs["Roughness"])
    ncol=mix(bn.outputs[0],mn.outputs[0])
    nm=nt.nodes.new("ShaderNodeNormalMap"); nm.uv_map="UVMap"; nm.inputs["Strength"].default_value=nstr
    L.new(ncol,nm.inputs["Color"]); L.new(nm.outputs[0],b.inputs["Normal"])
    b.inputs["Specular IOR Level"].default_value=0.2
    L.new(b.outputs[0],o.inputs[0])
    return m
def nature_materials():
    for mn,prefix,kw in (("M_VK_BarkOak","T_VK_BarkOak",dict(nstr=1.2,spec=0.15)),("M_VK_BarkBirch","T_VK_BarkBirch",dict(nstr=1.0,spec=0.2)),
                         ("M_VK_BarkPine","T_VK_BarkPine",dict(nstr=1.25,spec=0.15)),("M_VK_Moss","T_VK_Moss",dict(nstr=1.0,spec=0.1)),
                         ("M_VK_EndGrain","T_VK_EndGrain",dict(nstr=0.8,spec=0.15))):
        m=bpy.data.materials.get(mn) or bpy.data.materials.new(mn); pbr_material(m,prefix,**kw); MAT_MAP[mn]=dict(prefix=prefix,**kw)
    leaf_material()
    mossy_material("M_VK_RockMossy","T_VK_Rock",base_tile=1.5,thresh=0.66,soft=0.12,noise_amt=0.75)
    mossy_material("M_VK_BarkMossy","T_VK_BarkOak",base_tile=1.2,thresh=0.45)
