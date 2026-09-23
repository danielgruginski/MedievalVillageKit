import bpy, numpy as np, time
CODE=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\nature\wip2_willow_cell.png"
L={}
exec(bpy.data.texts["vk_tex"].as_string(),L); exec(open(CODE+r"\vk_leafgen.py",encoding="utf8").read(),L)
t0=time.time()
Base=L["Painter"]; TB=L["cell_bounds"]("willow")
class _Only(Base):
    def seg(s,B,*a,**k):
        if B==TB: return Base.seg(s,B,*a,**k)
    def leaf(s,B,*a,**k):
        if B==TB: return Base.leaf(s,B,*a,**k)
    def disc(s,B,*a,**k):
        if B==TB: return Base.disc(s,B,*a,**k)
    def flower(s,B,*a,**k):
        if B==TB: return Base.flower(s,B,*a,**k)
L["Painter"]=_Only
try: P=L["paint_leaf_atlas"](301)
finally: L["Painter"]=Base
x0,y0,x1,y1=TB[0]-6,TB[1]-6,TB[2]+6,TB[3]+6
rgb=P.img[y0:y1,x0:x1]; a=P.a[y0:y1,x0:x1,None]
S=2048; im=bpy.data.images["T_VK_Leaves_BCA"]; cur=np.zeros(S*S*4,np.float32); im.pixels.foreach_get(cur); cur=cur.reshape(S,S,4)[::-1]
o=cur[y0:y1,x0:x1]
bg=np.array([0.45,0.55,0.62],np.float32)
new=rgb*a+bg*(1-a); old=o[...,:3]*o[...,3:4]+bg*(1-o[...,3:4])
# small version (as seen from far): 8x box downsample, upscaled back
sm=new.reshape(64,8,64,8,3).mean((1,3)).repeat(8,0).repeat(8,1)
img=np.concatenate([old,np.ones((512,8,3),np.float32),new,np.ones((512,8,3),np.float32),sm],1)
h,w=img.shape[:2]
rgba=np.concatenate([np.clip(img,0,1),np.ones((h,w,1),np.float32)],-1)[::-1]
t=bpy.data.images.new("TMPN_prev",w,h,alpha=False)
t.pixels.foreach_set(rgba.ravel())
t.filepath_raw=OUT; t.file_format="PNG"; t.save()
bpy.data.images.remove(t)
print("coverage old",float((o[...,3]>0.5).mean()),"new",float((a[...,0]>0.5).mean()),"t",time.time()-t0)
