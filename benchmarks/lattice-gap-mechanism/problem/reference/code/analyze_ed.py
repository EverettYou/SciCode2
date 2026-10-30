"""Collect ED poles (3x3 k-grid run, 4x2 run) and calibrate the strong-coupling two-pole description of
the half-filled spectrum: band positions, residues, satellites, triplon band, gaps.
Writes data/ed_calibration.json and data/triplon_fit.json, figures/ed_poles.png"""
import json, os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, '.'); from band import eps, kgrid
import calib
def load(fn): return json.load(open(fn)) if os.path.exists(fn) else {}
d3 = load('../data/ed_3x3_path.json'); d4 = load('../data/ed_4x2.json'); d3g = load('../data/ed_3x3.json')
cal = {}

def main_pole(p, which):
    """dominant pole (largest weight) and the residual weight/centroid of the rest"""
    pos = np.array(p[0]); w = np.array(p[1])
    if len(pos) == 0: return None
    i = np.argmax(w); rest = np.delete(np.arange(len(pos)), i)
    wr = w[rest].sum(); cen = (pos[rest]*w[rest]).sum()/wr if wr > 1e-9 else np.nan
    return dict(E=float(pos[i]), w=float(w[i]), w_rest=float(wr), E_rest=float(cen), total=float(w.sum()))

def collect(d, keys):
    rows = []
    for key in keys:
        rec = d.get(key)
        if not rec or 'A' not in rec: continue
        for kk, v in rec['A'].items():
            if 'add' not in v or 'rem' not in v: continue
            kx, ky = map(float, kk.split(','))
            a = main_pole(v['add'], 'add'); r = main_pole(v['rem'], 'rem')
            if a is None or r is None: continue
            rows.append(dict(kx=kx, ky=ky, eps=float(eps(kx, ky)), add=a, rem=r, n_k=float(v.get('n_k', sum(v['rem'][1]))), bc=key))
    return rows

rows3 = collect(d3, ['N18_pp', 'N18_ap', 'N18_aa']); rows4 = collect(d4.get('half', {}), ['pp', 'ap', 'pa', 'aa'])
# add the first 3x3 run points (k=(0,0) pp, (pi,pi) aa)
for name, k in (('pp', (0.0, 0.0)), ('aa', (np.pi, np.pi))):
    if f'A_{name}_add' in d3g and f'A_{name}_rem' in d3g:
        a = main_pole(d3g[f'A_{name}_add']['poles'], 'add'); r = main_pole(d3g[f'A_{name}_rem']['poles'], 'rem')
        if not any(abs(x['kx']-k[0]) < 1e-6 and abs(x['ky']-k[1]) < 1e-6 for x in rows3):
            rows3.append(dict(kx=k[0], ky=k[1], eps=float(eps(*k)), add=a, rem=r, n_k=float(sum(d3g[f'A_{name}_rem']['poles'][1])), bc='first-run-'+name))
print(f'3x3 points: {len(rows3)}, 4x2 points: {len(rows4)}')

def fit_bands(rows, label):
    if len(rows) < 3: return None
    kx = np.array([r['kx'] for r in rows]); ky = np.array([r['ky'] for r in rows]); e = np.array([r['eps'] for r in rows])
    Ep = np.array([r['add']['E'] for r in rows]); Eh = np.array([r['rem']['E'] for r in rows])
    wp = np.array([r['add']['w'] for r in rows]); wh = np.array([r['rem']['w'] for r in rows]); nk = np.array([r['n_k'] for r in rows])
    nb = 4 if len(rows) >= 6 else 3
    fits = {}
    for name, y in (('Ep', Ep), ('Eh', Eh), ('wp', wp), ('wh', wh), ('nk', nk)):
        c, rms = calib.fit(kx, ky, y, nb); fits[name] = c; fits[name+'_rms'] = rms
    KX, KY = kgrid(400); Epg = calib.ev(fits['Ep'], KX, KY); Ehg = calib.ev(fits['Eh'], KX, KY)
    mu = 0.5*(Epg.min()+Ehg.max())
    res = dict(label=label, nbasis=nb, fits=fits, mu=float(mu), gap=float(Epg.min()-Ehg.max()),
               Ep_min=float(Epg.min()), Ep_max=float(Epg.max()), Eh_min=float(Ehg.min()), Eh_max=float(Ehg.max()),
               width_p=float(Epg.max()-Epg.min()), width_h=float(Ehg.max()-Ehg.min()),
               points=[dict(kx=r['kx'], ky=r['ky'], eps=r['eps'], Ep=r['add']['E'], wp=r['add']['w'], Ep_rest=r['add']['E_rest'], wp_rest=r['add']['w_rest'],
                            Eh=r['rem']['E'], wh=r['rem']['w'], Eh_rest=r['rem']['E_rest'], wh_rest=r['rem']['w_rest'], n_k=r['n_k'], bc=r['bc']) for r in rows])
    res['sat_p_offset'] = float(np.nanmean([r['add']['E_rest']-r['add']['E'] for r in rows if r['add']['w_rest'] > 0.01] or [4.0]))
    res['sat_h_offset'] = float(np.nanmean([r['rem']['E_rest']-r['rem']['E'] for r in rows if r['rem']['w_rest'] > 0.01] or [-3.0]))
    # first-order comparison: slope of the main poles vs eps(k)/2
    sp = np.polyfit(e, Ep, 1)[0]; sh = np.polyfit(e, Eh, 1)[0]
    res['slope_p_vs_eps'] = float(sp); res['slope_h_vs_eps'] = float(sh)
    print(f"[{label}] mu={mu:.3f} gap={res['gap']:.3f}  particle band [{Epg.min()-mu:.2f},{Epg.max()-mu:.2f}] (width {res['width_p']:.2f}); hole band [{Ehg.min()-mu:.2f},{Ehg.max()-mu:.2f}] (width {res['width_h']:.2f}); slopes vs eps: {sp:.3f}, {sh:.3f} (first order 0.5); rms Ep {fits['Ep_rms']:.3f} Eh {fits['Eh_rms']:.3f}; n(k) fit {np.round(fits['nk'],3)} rms {fits['nk_rms']:.3f}")
    return res
cal['bands_3x3'] = fit_bands(rows3, '3x3'); cal['bands_4x2'] = fit_bands(rows4, '4x2')

# triplon band from 3x3 (and 4x2 pp) poles: omega_t(k) = a + b (cos kx + cos ky) + c cos kx cos ky + d (cos 2kx + cos 2ky)
def triplon_fit(points, label):
    if len(points) < 3: return None
    k = np.array([[p[0], p[1]] for p in points]); w = np.array([p[2] for p in points])
    X = np.stack([np.ones(len(k)), np.cos(k[:, 0])+np.cos(k[:, 1]), np.cos(k[:, 0])*np.cos(k[:, 1]), np.cos(2*k[:, 0])+np.cos(2*k[:, 1])], 1)
    ncoef = 4 if len(points) >= 5 else 3
    coef, *_ = np.linalg.lstsq(X[:, :ncoef], w, rcond=None)
    coef = np.concatenate([coef, np.zeros(4-ncoef)])
    kk = np.linspace(-np.pi, np.pi, 301); KX, KY = np.meshgrid(kk, kk)
    om = coef[0] + coef[1]*(np.cos(KX)+np.cos(KY)) + coef[2]*np.cos(KX)*np.cos(KY) + coef[3]*(np.cos(2*KX)+np.cos(2*KY))
    r = dict(a=float(coef[0]), b=float(coef[1]), c=float(coef[2]), d=float(coef[3]), edge=float(om.min()), top=float(om.max()), label=label,
             points=[dict(kx=p[0], ky=p[1], omega=p[2], w=p[3]) for p in points], rms=float(np.sqrt(np.mean((X[:, :ncoef]@coef[:ncoef]-w)**2))))
    print(f'[{label}] triplon fit a={coef[0]:.3f} b={coef[1]:.3f} c={coef[2]:.3f} d={coef[3]:.3f}: edge {om.min():.3f} top {om.max():.3f} rms {r["rms"]:.3f}')
    return r
# NOTE: a spin-flip operator S^+_q carries the difference of two single-particle momenta, so under a twisted
# boundary condition its allowed q lie on the UNshifted grid.  Only the periodic (pp) runs are momentum-resolved
# triplon spectra; the ap/aa 'S' entries are the lowest S=1 state of the twisted cluster and are used only as a
# twist-dependence (finite-size) estimate of the (2pi/3,2pi/3) triplon.
tp3 = []
for key in ('N18_pp',):
    for kk, p in d3.get(key, {}).get('S', {}).items():
        kx, ky = map(float, kk.split(',')); i = int(np.argmin(p[0])); tp3.append((kx, ky, p[0][i], p[1][i]))
for name, k in (('pp', (0.0, 0.0)),):
    if f'S_{name}' in d3g and not any(abs(x[0]-k[0]) < 1e-6 and abs(x[1]-k[1]) < 1e-6 for x in tp3):
        p = d3g[f'S_{name}']['poles']; i = int(np.argmin(p[0])); tp3.append((k[0], k[1], p[0][i], p[1][i]))
tp4 = []
for key in ('pp',):
    for kk, p in d4.get('half', {}).get(key, {}).get('S', {}).items():
        kx, ky = map(float, kk.split(',')); q = p['odd']; i = int(np.argmin(q[0])); tp4.append((kx, ky, q[0][i], q[1][i]))
cal['triplon_3x3'] = triplon_fit(tp3, '3x3'); cal['triplon_4x2'] = triplon_fit(tp4, '4x2')
cal['triplon_3x3_lowest_vs_twist'] = {key: float(min(min(p[0]) for p in d3[key]['S'].values())) for key in ('N18_pp', 'N18_ap', 'N18_aa') if key in d3 and d3[key].get('S')}
print('lowest S=1 pole vs twist (3x3):', cal['triplon_3x3_lowest_vs_twist'])
best_t = cal['triplon_3x3'] or cal['triplon_4x2']
if best_t: json.dump(best_t, open('../data/triplon_fit.json', 'w'), indent=1)
best_b = cal['bands_3x3'] or cal['bands_4x2']
if best_b: json.dump(dict(fits=best_b['fits'], mu=best_b['mu']), open('../data/half_filling_bands.json', 'w'))

# gaps from total energies
g = {}
for name in ('pp', 'aa'):
    if all(k in d3g for k in (f'E18_{name}', f'E19_{name}', f'E17_{name}')):
        g[f'charge_gap_3x3_{name}'] = d3g[f'E19_{name}'] + d3g[f'E17_{name}'] - 2*d3g[f'E18_{name}']
    if all(k in d3g for k in (f'E18_{name}', f'E18_Sz1_{name}')):
        g[f'spin_gap_3x3_{name}'] = d3g[f'E18_Sz1_{name}'] - d3g[f'E18_{name}']
if all(k in d3g for k in ('E19_pp', 'E18_pp', 'E17_aa', 'E18_aa')):
    g['charge_gap_3x3_mixedBC'] = (d3g['E19_pp']-d3g['E18_pp']) + (d3g['E17_aa']-d3g['E18_aa'])
en = d4.get('energies', {})
for name in ('pp', 'aa'):
    for N in range(5, 20):
        if all(f'N{n}_{name}' in en for n in (N-1, N, N+1)):
            g[f'gap1_4x2_N{N}_{name}'] = en[f'N{N+1}_{name}'] + en[f'N{N-1}_{name}'] - 2*en[f'N{N}_{name}']
for key, v in d4.get('doped', {}).items():
    if 'spin_gap' in v: g[f'spin_gap_4x2_{key}'] = v['spin_gap']
for N in (12, 8):
    if all(f'N{N}_pp_{l}' in d3 for l in ('Np1', 'Nm1')) and f'N{N}_pp' in d3:
        E0 = d3[f'N{N}_pp']['E0']; g[f'gap1_3x3_N{N}'] = d3[f'N{N}_pp_Np1'] + d3[f'N{N}_pp_Nm1'] - 2*E0
        if all(f'N{N}_pp_{l}' in d3 for l in ('Np2', 'Nm2')): g[f'gap2_3x3_N{N}'] = d3[f'N{N}_pp_Np2'] + d3[f'N{N}_pp_Nm2'] - 2*E0
        if f'N{N}_pp_Sz1' in d3: g[f'spin_gap_3x3_N{N}'] = d3[f'N{N}_pp_Sz1'] - E0
cal['gaps'] = g
for k, v in g.items(): print(f'  {k} = {v:.4f}')
json.dump(cal, open('../data/ed_calibration.json', 'w'), indent=1)

# figure: poles vs eps(k)
fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
for rows, lab, mk in ((rows3, '3x3', 'o'), (rows4, '4x2', 's')):
    if not rows: continue
    e = np.array([r['eps'] for r in rows])
    ax[0].scatter(e, [r['add']['E'] for r in rows], marker=mk, s=[200*r['add']['w'] for r in rows], label=f'{lab} addition (area = weight)', alpha=0.7)
    ax[0].scatter(e, [r['rem']['E'] for r in rows], marker=mk, s=[200*r['rem']['w'] for r in rows], label=f'{lab} removal', alpha=0.7)
    ax[1].plot(e, [r['n_k'] for r in rows], mk, label=f'{lab} n(k)')
eg = np.linspace(-4.8, 3.2, 100)
ax[0].plot(eg, 6+eg/2, 'k--', lw=0.8, label='first order $\\pm 3J/4+\\epsilon/2$'); ax[0].plot(eg, -6+eg/2, 'k--', lw=0.8)
ax[0].plot(eg, eg/2+np.sqrt(eg**2/4+36), 'k:', lw=0.8, label='Hubbard-I'); ax[0].plot(eg, eg/2-np.sqrt(eg**2/4+36), 'k:', lw=0.8)
ax[1].plot(eg, 0.5*(1-eg/(2*np.sqrt(eg**2/4+36))), 'k:', lw=0.8, label='Hubbard-I n(k)'); ax[1].axhline(0.5, color='k', ls='--', lw=0.8, label='first order')
ax[0].set_xlabel('$\\epsilon(k)$'); ax[0].set_ylabel('pole energy $E_{N\\pm1}-E_N$'); ax[0].legend(fontsize=7)
ax[1].set_xlabel('$\\epsilon(k)$'); ax[1].set_ylabel('n(k) per spin, per layer'); ax[1].legend(fontsize=7)
fig.tight_layout(); fig.savefig('../figures/ed_poles.png', dpi=140)
