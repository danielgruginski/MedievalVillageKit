import json, math
W,H=72,56
WALL_S,WALL_N,WALL_W,WALL_E=25,46,23,63
POSTERN_J=30
def Z(v): return [[v]*W for _ in range(H)]
L=Z(1); water=Z(False); ground=Z(0); ramp=Z(0); stair=Z(False)
for j in range(10,18):
    for i in range(60): L[j][i]=0
for j in range(12,16):
    for i in range(60): water[j][i]=True
for j in range(H):
    for i in range(W):
        if abs((i-65.5)/8.5)**4+abs((j-11.8)/7.2)**4<1.0: L[j][i]=0
        if abs((i-64.5)/6.5)**4+abs((j-12.5)/5.0)**4<1.0: water[j][i]=True
for j in range(12,16):
    for i in range(58,60): water[j][i]=True
for j in range(16,20):
    for i in range(23,30): L[j][i]=0
def setr(j0,j1,i0,i1,v,arr=None):
    a=L if arr is None else arr
    for j in range(j0,j1):
        for i in range(i0,i1): a[j][i]=v
setr(24,47,20,64,2); setr(24,34,0,20,2); setr(23,24,40,44,2)
setr(34,47,0,20,3); setr(34,47,11,19,4); setr(39,47,0,9,4)
setr(30,34,11,13,4); setr(30,34,17,19,4)
for j in range(47,H):
    for i in range(W):
        n=3+int(min(max(round(1.1*math.sin(i/4.1)+0.9*math.cos(i/2.7+j/2.1)+(j-47)*0.35),0),2))
        L[j][i]=max(L[j][i],n)
for j in range(H):
    for i in range(W):
        if L[j][i]==0 and not water[j][i]: ground[j][i]=3
        if L[j][i]>=5: ground[j][i]=4
r0,r1=41,42
for j in range(0,32):
    for i in (r0,r1):
        if not water[j][i]: ground[j][i]=1
setr(25,32,r0,r1+1,2,ground); setr(31,36,36,48,2,ground); setr(39,42,24,41,2,ground); setr(36,39,39,41,2,ground)
setr(36,39,47,52,2,ground); setr(29,30,44,62,2,ground); setr(POSTERN_J,POSTERN_J+1,WALL_W,r0,2,ground)
setr(POSTERN_J,POSTERN_J+1,11,WALL_W,1,ground); setr(9,10,11,r0,1,ground)
for i in (r0,r1):
    ramp[10][i]=3; ramp[17][i]=1; ramp[22][i]=1
for i in (9,10):
    ramp[10][i]=3; ramp[17][i]=1; ramp[23][i]=1
    for j in range(9,34):
        if not water[j][i]: ground[j][i]=1
ramp[33][9]=1; stair[33][9]=True
ramp[19][24]=1; ramp[19][25]=1; ramp[5][66]=3; ramp[5][67]=3
setr(6,9,2,10,1,ground)
def cell(x,y): return int((x-1500)//3), int(y//3)
def lvl(x,y):
    i,j=cell(x,y)
    if 0<=i<W and 0<=j<H: return L[j][i]
    return None
