import numpy as np
from bcs_bilayer import solve, Tmf, E_K
nus = np.concatenate([np.linspace(0.01, 0.09, 5), np.linspace(0.1, 0.9, 33), np.linspace(0.91, 0.99, 5)])
out = []
for J in [6.0, 6.5, 7.0]:
    for nu in nus:
        try:
            T = Tmf(J, nu)
        except Exception as ex:
            T = np.nan
        D, mu = solve(J, nu)
        out.append((J, nu, T, D, mu))
        print(f'J={J} nu={nu:.3f} Tmf={T:.3f} Delta0={D:.3f} mu={mu:.3f}', flush=True)
np.save('tmf_curve.npy', np.array(out))
