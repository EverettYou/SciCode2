import numpy as np
import importlib.util, sys
spec = importlib.util.spec_from_file_location('nb', 'nmr_bcs.py')
src = open('nmr_bcs.py').read().split("Tc = 1.11; D0 = 1.98")[0]
ns = {}; exec(src, ns)
T = np.concatenate([np.linspace(0.19, 1.3, 120), np.linspace(1.32, 5.0, 40)])
r = 1.093*ns['rate'](T, 1.11, 1.98, 0.044, True)
np.save('nmr_bcs_curve.npy', np.vstack([T, r]))
print(r[:3], r[-3:])
