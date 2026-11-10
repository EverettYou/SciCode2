"""ED (Lanczos) of the attractive Hubbard model on 8- and 10-site periodic clusters:
single-particle (pair-breaking) gap  Δ_pb(N) = [E(N+1)+E(N-1)-2E(N)]/2  and spin gap vs filling.
Also the strong-coupling pseudospin exchange constants and a BKT estimate at half filling."""
import numpy as np, json, sys
sys.path.insert(0,'/app/code')
from ed_hubbard import *
P=json.load(open('/app/code/params.json'))
t,tp=1.0,0.197
res={}
clusters={'10':((3,1),(-1,3)),'8':((2,2),(2,-2))}
for name,(a1,a2) in clusters.items():
    sites,idx,red=tilted_cluster(a1,a2); Ns=len(sites)
    T=hopping_matrix(Ns,sites,idx,red,t,tp)
    for U in [-6.0,-9.0,-12.0]:
        E={}
        for N in range(1,Ns+2):
            nup=(N+1)//2; ndn=N-nup
            E[N]=ground(Ns,T,U,nup,ndn)[0][0]
        rows=[]
        for N in range(2,Ns+1,2):
            dpb=(E[N+1]+E[N-1]-2*E[N])/2
            sg=ground(Ns,T,U,N//2+1,N//2-1)[0][0]-E[N]
            rows.append(dict(N=N,nu=N/Ns/2,gap=dpb,spin_gap=sg))
        res[f'{name}_U{int(abs(U))}']=rows
        print(name,U,[(round(r['nu'],3),round(r['gap'],3),round(r['spin_gap'],3)) for r in rows])
# strong-coupling pseudospin constants
U=12.0
J=4*t**2/U; Jp=4*tp**2/U
res['pseudospin']=dict(J=J,Jp=Jp,anisotropy=Jp/J,pair_hopping=2*t**2/U)
json.dump(res,open('/app/code/ed_results.json','w'),indent=1)
from style import *; setup()
fig,ax=plt.subplots(figsize=(6.2,4.2))
cols={'6':'#86b6ef','9':'#2a78d6','12':'#104281'}
for U in ['6','9','12']:
    for name,mk in [('10','o'),('8','s')]:
        rows=res[f'{name}_U{U}']
        ax.plot([r['nu'] for r in rows],[r['gap'] for r in rows],mk+'-',color=cols[U],ms=5,lw=1.2,mfc=cols[U] if name=='10' else 'none',
                label=f'ED |U|={U}, {name} sites')
meas=[(0.2,1.959,0.01),(0.3,2.65,0.3),(0.5,3.97,0.03)]
ax.errorbar([m[0] for m in meas],[m[1] for m in meas],yerr=[m[2] for m in meas],fmt='D',color=INK,ms=7,capsize=3,label='measured (STS gap edge)')
ax.set_xlabel('filling ν'); ax.set_ylabel('single-particle gap / D'); ax.set_xlim(0,0.55); ax.set_ylim(0,5)
ax.set_title('Pair-breaking gap of the attractive Hubbard model (t′=0.197t) vs data',fontsize=9,loc='left')
ax.legend(fontsize=7,ncol=2,loc='lower right')
fig.tight_layout(); fig.savefig('/app/fig3_ed_gaps.png'); plt.close(fig)
