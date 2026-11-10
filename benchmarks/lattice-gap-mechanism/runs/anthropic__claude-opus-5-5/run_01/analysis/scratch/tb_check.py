import numpy as np
N=600
k = 2*np.pi*(np.arange(N)+0.5)/N
kx, ky = np.meshgrid(k, k, indexing='ij')
cx, cy = np.cos(kx), np.cos(ky)
for t, tp in [(1.0,0.2),(1.025,0.206),(1.0,0.25),(1.0,0.15)]:
    e = -2*t*(cx+cy) - 4*tp*cx*cy
    ef = np.sort(e.ravel())
    emin, emax = ef[0], ef[-1]
    print(f"t={t} t'={tp}: band [{emin:.3f},{emax:.3f}] W={emax-emin:.3f} vHs at {4*tp:.3f} (= {4*tp-emin:.3f} above bottom)")
    for nu in [0.2, 0.25, 0.3, 0.35, 0.4, 0.5]:
        mu = ef[int(nu*len(ef))]
        print(f"   nu={nu}: mu={mu:.3f}, mu-bottom={mu-emin:.3f}, top-mu={emax-mu:.3f}, vHs-mu={4*tp-mu:.3f}")
