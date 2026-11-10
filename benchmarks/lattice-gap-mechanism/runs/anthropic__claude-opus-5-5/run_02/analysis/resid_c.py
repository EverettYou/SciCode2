from smoothfit import *
exec(open('fit_c.py').read().split("p0=")[0])
p=np.load('/app/analysis/fit_c.npy')
V,G=sts('c')
m=model_bcs(p,V=V)
r=G-m
k=8
for i in range(0,len(V),k*2):
    seg=slice(i,i+k*2)
    print(f'{V[i]:6.2f} data={np.mean(G[seg]):.3f} model={np.mean(m[seg]):.3f} resid={np.mean(r[seg]):+.3f} ' + ('+'*int(max(0,np.mean(r[seg]))*200) if np.mean(r[seg])>0 else '-'*int(-np.mean(r[seg])*200)))
