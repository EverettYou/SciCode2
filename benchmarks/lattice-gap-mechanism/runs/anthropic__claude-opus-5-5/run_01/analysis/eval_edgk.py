import json, numpy as np
from ed_hubbard import cont_frac_eval
d = json.load(open('edgk_fin.json'))
E0 = d['E0']
mu_p = -51.998116 - (-55.168194); mu_m = -55.168194 - (-50.148212)  # E(9,8)-E0 ; E0-E(8,7)
mid = 0.5 * (mu_p + mu_m)
print(f'cluster midgap = {mid:.4f}  (mu+ = {mu_p:.4f}, mu- = {mu_m:.4f})')
names = {(0,0):'Gamma', (1,0):'X', (1,1):'M', (0.5,0.5):'(pi/2,pi/2)'}
for K, p, h in zip(d['K'], d['p'], d['h']):
    z = np.array([mid + 1e-9j])
    gp = cont_frac_eval(z, p[0], np.array(p[1]), np.array(p[2]), sign=+1, E0=E0)
    gh = cont_frac_eval(z, h[0], np.array(h[1]), np.array(h[2]), sign=-1, E0=E0)
    G = (gp + gh)[0].real
    key = tuple(np.round(np.array(K)/np.pi, 2))
    print(f'K={key} ({names.get(key, "")}): weights p={p[0]:.4f} h={h[0]:.4f};  G(K, midgap) = {G:+.5f}  sign {"+" if G>0 else "-"}')
out = []
for K, p, h in zip(d['K'], d['p'], d['h']):
    z = np.array([mid + 1e-9j])
    G = (cont_frac_eval(z, p[0], np.array(p[1]), np.array(p[2]), sign=+1, E0=E0) +
         cont_frac_eval(z, h[0], np.array(h[1]), np.array(h[2]), sign=-1, E0=E0))[0].real
    out.append({'K_over_2pi': (np.array(K)/(2*np.pi)).tolist(), 'G_mid': float(G), 'hole_weight': h[0], 'particle_weight': p[0]})
json.dump({'midgap': mid, 'points': out}, open('edgk_fin_eval.json', 'w'), indent=1)
