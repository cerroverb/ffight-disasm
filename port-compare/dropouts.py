import wave, sys, numpy as np
def load(p,sr=None):
    w=wave.open(p); s=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float).reshape(-1,w.getnchannels()).mean(1); return s, sr or w.getframerate()
h,hsr=load(sys.argv[1],60e6/2/1248)
st=0.005
def env(a,sr):
    k=int(sr*st); n=len(a)//k; return np.abs(a[:n*k]).reshape(n,k).mean(1)
eH=env(h,hsr)
for f in sys.argv[2:]:
    s,sr=load(f); eS=env(s,sr)
    z=(s==0); gaps=[]; i=0; n=len(s)
    while i<n:
        if z[i]:
            j=i
            while j<n and z[j]: j+=1
            if j-i>=int(0.003*sr) and i>3*sr and j<n-3*sr: gaps.append((i/sr,(j-i)/sr*1000))
            i=j
        else: i+=1
    drops=[]
    for t,d in gaps:
        i=int(t/st); a=eS[i-400:i+400]; c=[]
        for o in range(-300,300):
            b=eH[i-400+o:i+400+o]
            if i-400+o>=0 and len(b)==len(a) and a.std()>0 and b.std()>0: c.append((np.corrcoef(a,b)[0,1],o))
        if not c: continue
        g=i+max(c)[1]; lvl=eH[g:g+max(1,int(d/1000/st))].mean()
        if lvl>=20: drops.append((round(t,2),round(d,1)))
    print(f.split('/')[-1], 'dropouts (3 ms or more, where the game has sound):', len(drops), drops[:12])
