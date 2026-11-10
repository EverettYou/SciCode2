import numpy as np, json, sys
from cpt_bilayer import CPT
from cpt_analyze import G_batch, vk_batch
fn, Lx, Ly, mid = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
cpt = CPT(fn=fn, Lx=Lx, Ly=Ly, t=1.0, tp=0.2)
nf = 161; kf = -np.pi + 2*np.pi*(np.arange(nf)+0.5)/nf
KX, KY = np.meshgrid(kf, kf, indexing='ij'); ks = np.stack([KX.ravel(), KY.ravel()], 1)
V = vk_batch(cpt, ks); Vr = vk_batch(cpt, ks[:, ::-1]) if Lx != Ly else None
out = []
for d in np.arange(-1.0, 1.61, 0.1):
    g = G_batch(cpt, ks, mid + d + 1e-9j, V)
    if Vr is not None: g = 0.5*(g + G_batch(cpt, ks[:, ::-1], mid + d + 1e-9j, Vr))
    Gm = g.real.reshape(nf, nf)
    fpos = float(np.mean(Gm > 0))
    out.append((round(d, 2), fpos))
    print(f'w_ref - midgap = {d:+.2f}:  fraction with G(k,w_ref)>0 = {fpos:.3f}')
json.dump(out, open(fn.replace('.npz', '_frac_vs_mu.json'), 'w'))
