exec(open('/app/analysis/fit_b7.py').read().split('best=None')[0])
p=np.load('/app/analysis/fit_b7.npy')
m=model(p,V=V)
k=8
for i in range(0,len(V),k*2):
    seg=slice(i,i+k*2)
    rr=np.mean(G[seg]-m[seg])
    print(f'{V[i]:6.2f} data={np.mean(G[seg]):.3f} model={np.mean(m[seg]):.3f} resid={rr:+.3f} '+('+'*int(rr*200) if rr>0 else '-'*int(-rr*200)))
