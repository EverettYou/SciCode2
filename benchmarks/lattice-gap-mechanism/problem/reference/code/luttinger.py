"""Green's function at omega=0 (from the chemical potential at the gap midpoint) for the nu=1/2 spectrum:
Re G(k,0) = -int A(k,w)/w dw  (Kramers-Kronig).  Zero surface and the fraction of the zone on the (0,0) side.
Writes figures/luttinger.png, data/luttinger.json"""
import json, os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, '.'); from band import eps, kgrid
import calib
cal = json.load(open('../data/ed_calibration.json'))
d3 = json.load(open('../data/ed_3x3_path.json')) if os.path.exists('../data/ed_3x3_path.json') else {}
b = cal.get('bands_3x3') or cal['bands_4x2']; mu = b['mu']
KX, KY = kgrid(800); E = eps(KX, KY)
out = {}
def frac_inside(G):
    """fraction of the zone on the (0,0) side of the zero contour = sign of G at (0,0)"""
    s0 = np.sign(G[G.shape[0]//2, G.shape[1]//2]); return float(np.mean(np.sign(G) == s0))
# (1) first-order strong coupling: equal residues, bands +-3J/4 + eps/2, midpoint shifted to 0
Ep1 = 6+E/2; Eh1 = -6+E/2; m1 = 0.5*(Ep1.min()+Eh1.max()); G1 = -0.5/(Ep1-m1) - 0.5/(Eh1-m1)
out['first_order'] = dict(fraction_00_side=frac_inside(G1), contour='eps(k) = %.3f' % (-4*0.2))
# (2) Hubbard-I: poles eps/2 +- sqrt(eps^2/4+36), residues (1 +- eps/2E)/2
R = np.sqrt(E**2/4+36); EpH = E/2+R; EhH = E/2-R; ZpH = 0.5*(1+E/(2*R)); ZhH = 1-ZpH; mH = 0.5*(EpH.min()+EhH.max())
GH = -ZpH/(EpH-mH) - ZhH/(EhH-mH)
out['hubbard_I'] = dict(fraction_00_side=frac_inside(GH), sign_changes=bool((GH > 0).any() and (GH < 0).any()), midpoint_shift=float(mH))
# (3) ED-calibrated two-pole + satellites
f = b['fits']
Ep = calib.ev(f['Ep'], KX, KY)-mu; Eh = calib.ev(f['Eh'], KX, KY)-mu
wp = np.clip(calib.ev(f['wp'], KX, KY), 0.02, 1); wh = np.clip(calib.ev(f['wh'], KX, KY), 0.02, 1); nk = np.clip(calib.ev(f['nk'], KX, KY), 0.05, 0.95)
wpr = np.clip(1-nk-wp, 0, None); whr = np.clip(nk-wh, 0, None)
G3 = -wp/Ep - wh/Eh - wpr/(Ep+b['sat_p_offset']) - whr/(Eh+b['sat_h_offset'])
G3main = -wp/Ep - wh/Eh
out['ed_calibrated'] = dict(fraction_00_side=frac_inside(G3), fraction_00_side_main_poles_only=frac_inside(G3main), G_at_00=float(G3[400, 400]), G_at_pipi=float(G3[0, 0]), G_at_pi0=float(G3[0, 400]))
# (4) exact cluster values at the 3x3 grid points (full pole sums)
pts = []
for bcn in ('pp', 'ap', 'aa'):
    for kk, v in d3.get(f'N18_{bcn}', {}).get('A', {}).items():
        if 'add' in v and 'rem' in v:
            qx, qy = map(float, kk.split(','))
            g = -sum(w_/(p_-mu) for p_, w_ in zip(*v['add'])) - sum(w_/(p_-mu) for p_, w_ in zip(*v['rem']))
            pts.append(dict(kx=qx, ky=qy, eps=float(eps(qx, qy)), ReG0=float(g)))
out['ed_3x3_points'] = pts
# (5) the exact zero band omega_z(k): Re G(k,omega_z)=0 inside the gap, at each cluster momentum
from scipy.optimize import brentq
for p in pts:
    v = None
    for bcn in ('pp', 'ap', 'aa'):
        v = d3.get(f'N18_{bcn}', {}).get('A', {}).get(f"{p['kx']:.6f},{p['ky']:.6f}") or v
    pa, wa = v['add']; pr, wr = v['rem']
    Gw = lambda w: sum(x/(w-q) for q, x in zip(pa, wa)) + sum(x/(w-q) for q, x in zip(pr, wr))
    p['omega_zero'] = float(brentq(Gw, max(pr)+1e-6, min(pa)-1e-6)); p['omega_zero_rel'] = p['omega_zero']-mu
e_ = np.array([p['eps'] for p in pts]); z_ = np.array([p['omega_zero_rel'] for p in pts])
cz = np.polyfit(e_, z_, 1); out['zero_band'] = dict(slope=float(cz[0]), offset=float(cz[1]), crossing_eps=float(-cz[1]/cz[0]),
    fraction_from_crossing=float(np.mean(E < -cz[1]/cz[0])), dispersion=float(z_.max()-z_.min()))
# (6) sensitivity: fraction on the (0,0) side when the reference energy is shifted inside the gap
sens = {}
for dmu in (-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3):
    G3s = -wp/(Ep-dmu) - wh/(Eh-dmu) - wpr/(Ep+b['sat_p_offset']-dmu) - whr/(Eh+b['sat_h_offset']-dmu)
    sens[f'{dmu:+.1f}'] = frac_inside(G3s)
out['fraction_vs_reference_shift'] = sens
# free-electron reference: fraction enclosed by the half-filling Fermi surface is 1/2 by construction
out['mu_abs'] = mu
json.dump(out, open('../data/luttinger.json', 'w'), indent=1)
for k, v in out.items():
    if k != 'ed_3x3_points': print(k, v)
for p in pts: print(f"  ED 3x3 k=({p['kx']/np.pi:.2f},{p['ky']/np.pi:.2f})pi eps={p['eps']:+.2f}: Re G(k,0) = {p['ReG0']:+.4f}  zero band {p['omega_zero_rel']:+.3f}")

fig, axall = plt.subplots(1, 5, figsize=(19.5, 4.2), gridspec_kw=dict(width_ratios=[1, 1, 1, 0.04, 1.15], wspace=0.3))
ax = [axall[0], axall[1], axall[2], axall[4]]; cax = axall[3]
a = ax[3]
a.plot(e_, z_, 'ko', label='exact 3x3 cluster')
ee = np.linspace(-4.9, 3.3, 50); a.plot(ee, ee/2-m1, 'b--', label='first order: $\\varepsilon/2$')
a.plot(ee, 0*ee-mH, 'g:', label='Hubbard-I: flat')
a.plot(ee, np.polyval(cz, ee), 'r-', lw=0.8, label=f'fit: {cz[1]:+.2f} {cz[0]:+.2f}$\\varepsilon$')
a.axhline(0, color='k', lw=0.5); a.set_xlabel('$\\varepsilon(k)$'); a.set_ylabel('$\\omega_{zero}(k)-\\omega_{mid}$'); a.yaxis.tick_right(); a.yaxis.set_label_position('right')
a.set_title('band of Green\'s-function zeros inside the gap', fontsize=8); a.legend(fontsize=7)
for a, G, t in zip(ax[:3], (G1, GH, G3), ('first order (equal residues)', 'Hubbard-I residues', 'ED-calibrated (3x3) two-pole + satellites')):
    vm = np.percentile(abs(G), 98)
    im = a.imshow(G.T, origin='lower', extent=[-1, 1, -1, 1], cmap='RdBu_r', vmin=-vm, vmax=vm)
    a.contour(KX/np.pi, KY/np.pi, G.T, levels=[0], colors='k', linewidths=1.2)
    a.set_title(f'{t}\nfraction on (0,0) side = {frac_inside(G):.3f}', fontsize=8); a.set_xlabel('$k_x/\\pi$'); a.set_ylabel('$k_y/\\pi$')
    if pts and a is ax[2]:
        for p in pts:
            for sx in (1, -1):
                for sy in (1, -1):
                    for (qx, qy) in ((p['kx'], p['ky']), (p['ky'], p['kx'])):
                        a.plot(sx*qx/np.pi, sy*qy/np.pi, 'o', mfc='r' if p['ReG0'] > 0 else 'b', mec='k', ms=5)
fig.colorbar(im, cax=cax, label='Re G(k,0)')
fig.savefig('../figures/luttinger.png', dpi=140, bbox_inches='tight')
