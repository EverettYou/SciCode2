import numpy as np, sys, json
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from cpt_analyze import *
fn = sys.argv[1]; Lx = int(sys.argv[2]); Ly = int(sys.argv[3]); half = int(sys.argv[4])
tp = float(sys.argv[5]) if len(sys.argv) > 5 else 0.2
cpt, out = analyze(fn, Lx, Ly, tp=tp, eta=0.06, w=np.linspace(-12, 12, 961), nk_dos=28, npath=50)
res = {}
w0 = 0.5*(cpt.ep.min() + cpt.em.max())
lo, up = band_edges_from_path(cpt, Lx, Ly, w0, tp=tp)
mid = 0.5*(lo+up)
res.update(dict(lower_top=lo, upper_bottom=up, gap=up-lo, midgap=mid))
if half:
    kg, Gm = zero_map(cpt, Lx, Ly, mid)
    sg0 = np.sign(Gm[len(kg)//2, len(kg)//2])
    frac = float(np.mean(np.sign(Gm[:-1, :-1]) == sg0))
    res.update(dict(frac_gamma_side=frac, sign_gamma=float(sg0), sign_M=float(np.sign(Gm[0,0]))))
    np.save(fn.replace('.npz', '_Gmap.npy'), Gm)
np.savez(fn.replace('.npz', '_analysis.npz'), **out, midgap=mid)
print(json.dumps(res, indent=1))
fig, axs = plt.subplots(1, 3 if half else 2, figsize=(16, 5))
axs[0].plot(out['w']-mid, out['dos']); axs[0].set_xlim(-10, 10); axs[0].set_title('DOS (w-midgap)')
axs[1].imshow(out['A'].T, origin='lower', aspect='auto', extent=[0, out['dist'][-1], out['w'][0]-mid, out['w'][-1]-mid],
              cmap='magma', vmax=np.percentile(out['A'], 99.5)); axs[1].set_ylim(-10, 10)
axs[1].set_xticks(out['ticks']); axs[1].set_xticklabels(['G','X','M','G'])
if half:
    axs[2].contourf(kg/(2*np.pi), kg/(2*np.pi), Gm.T, levels=40, cmap='RdBu_r'); axs[2].contour(kg/(2*np.pi), kg/(2*np.pi), Gm.T, levels=[0], colors='k')
    axs[2].set_aspect('equal'); axs[2].set_title(f"Re G(k,mid): frac={res['frac_gamma_side']:.3f}")
plt.tight_layout(); plt.savefig(fn.replace('.npz', '_report.png'), dpi=70)
