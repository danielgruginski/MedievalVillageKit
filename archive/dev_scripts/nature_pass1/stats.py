import bpy, numpy as np, colorsys
def img_stats(path,boxes,thr=0.06):
    """boxes: {name:(x0,y0,x1,y1)} in image pixel coords (y down). Returns mean lum/sat of pixels that differ
    from the background (estimated per column from the top rows)."""
    im=bpy.data.images.load(path,check_existing=False)
    try:
        w,h=im.size; a=np.zeros(w*h*4,np.float32); im.pixels.foreach_get(a); a=a.reshape(h,w,4)[::-1,:,:3]
    finally: bpy.data.images.remove(im)
    bg=np.median(a[:40],axis=0)             # per column background from the top rows
    out={}
    for n,(x0,y0,x1,y1) in boxes.items():
        reg=a[y0:y1,x0:x1]; d=np.abs(reg-bg[None,x0:x1]).sum(-1)
        m=d>thr
        if m.sum()<50: out[n]=None; continue
        px=reg[m]; lum=(px*np.array([0.2126,0.7152,0.0722])).sum(-1)
        mx=px.max(-1); mn=px.min(-1); sat=np.where(mx>1e-4,(mx-mn)/np.maximum(mx,1e-4),0)
        ys=np.nonzero(m)[0]; mid=(ys.min()+ys.max())/2
        top=lum[ys<mid].mean(); bot=lum[ys>=mid].mean()
        out[n]=dict(n=int(m.sum()),lum=round(float(lum.mean()),3),sat=round(float(sat.mean()),3),lum_top=round(float(top),3),lum_bot=round(float(bot),3))
    return out
