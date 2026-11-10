import json, numpy as np
d = json.load(open('/app/measurements.json'))
nmr = d['measurements'][1]['samples']; rho = d['measurements'][2]['samples']
for s in nmr:
    T = np.array(s['temperature']); r = np.array(s['one_over_T1']); e = np.array(s['uncertainty'])
    print('NMR nu=', s['filling'])
    for Ti, ri, ei in zip(T, r, e):
        print(f'  T={Ti:7.4f}  D/T={1/Ti:6.3f}  1/T1={ri:.4e} +- {ei:.2e}   1/T1T={ri/Ti:.4e}  SNR={ri/ei:6.2f}')
for s in rho:
    T = np.array(s['temperature']); r = np.array(s['resistivity']); e = np.array(s['uncertainty'])
    print('RHO nu=', s['filling'])
    for Ti, ri, ei in zip(T, r, e):
        print(f'  T={Ti:7.4f}  rho={ri:.4e} +- {ei:.2e}  rel={ei/ri if ri else 0:.3f}')
