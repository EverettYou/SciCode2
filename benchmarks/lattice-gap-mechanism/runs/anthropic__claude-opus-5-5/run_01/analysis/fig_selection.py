"""Supplementary figure: model selection.  (a) single-particle half-gap vs filling: data vs ED of candidate
models; (b) gaps of the half-filled crystal: spin gap vs charge (single-particle) gap."""
import numpy as np, re, json
import vizstyle as vs
vs.apply()
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

def parse(fn):
    out = {}
    for line in open(fn):
        m = re.search(r'nu=([\d.]+): gap_sp=([\d.]+) spin_gap=([\d.]+)', line)
        if m: out[float(m.group(1))] = (float(m.group(2)), float(m.group(3)))
    return out
att = parse('fss_U12.log'); att.update(parse('gaps_U12_16site.log') if False else {})
att16 = {0.0625: 2.6252, 0.125: 3.1612, 0.1875: 3.4391, 0.3125: 3.6912}
att10 = {0.1: 3.0226, 0.2: 3.6223, 0.3: 3.9825, 0.5: 4.2373}
att20 = {0.05: 2.5044, 0.2: 3.3680}
bil = parse('scan_U1.8_J6.5_doped.log'); bil.update(parse('scan_U1.8_J6.5_half.log'))
a = np.load('tmf_curve.npy'); m = a[:, 0] == 6.5
fig, axs = plt.subplots(1, 2, figsize=(13, 5.0), gridspec_kw={'width_ratios': [1.5, 1]})
ax = axs[0]
ax.plot(list(att10), list(att10.values()), 'v-', color=vs.MUTED, ms=7, lw=1.2, label='attractive one-layer Hubbard, U=−12: ED 10 sites')
ax.plot(list(att16), list(att16.values()), 'v--', color=vs.MUTED, ms=7, lw=1.0, mfc='none', label='  "  ED 16 sites')
ax.plot(list(att20), list(att20.values()), 'v', color=vs.INK2, ms=8, mfc='none', label='  "  ED 20 sites')
ax.axhline(2.06, color=vs.MUTED, lw=0.8)
ax.text(0.33, 2.1, r'dilute two-body limit $E_b/2=2.06$ ($U=-12$)', fontsize=8, color=vs.INK2)
xs = sorted(bil); ys = [bil[x][0] for x in xs]
ax.plot(xs, ys, 'o-', color=vs.C_HALF, ms=8, lw=1.8, label=r'bilayer model ($U=1.8$, $J_\perp=6.5$): ED 16 sites')
ax.plot(a[m, 1][a[m, 1] < 0.42], a[m, 3][a[m, 1] < 0.42], color=vs.C_HALF, lw=1.0, ls=(0, (4, 2)),
        label=r'bilayer model: $J_\perp$ mean-field gap')
# data
ax.errorbar([0.2], [1.96], yerr=0.05, fmt='*', color=vs.C_02, ms=15, mec=vs.INK, zorder=6)
ax.errorbar([0.3], [2.73], yerr=0.13, fmt='*', color=vs.C_03, ms=15, mec=vs.INK, zorder=6)
ax.errorbar([0.5], [3.95], yerr=0.05, fmt='*', color=vs.C_HALF, ms=15, mec=vs.INK, zorder=6)
ax.plot([], [], '*', color=vs.INK2, ms=12, label='measured (STS; ν≈0.3: 2.6 hard edge – 2.85 at $k_F$)')
ax.set_xlabel(r'filling $\nu$'); ax.set_ylabel(r'single-particle gap (half of the STS gap, $D$)')
ax.set_xlim(0, 0.55); ax.set_ylim(0, 4.8)
ax.set_title('(a) gap versus filling: data vs candidate models', loc='left')
ax.legend(fontsize=7.8, loc='lower right')
ax = axs[1]
labels = ['measured', 'attractive\none-layer\n(U=−12, ED)', 'bilayer model\n(ED, 16 sites)']
spin = [(5.5, 0.5), (4.24, 0.0), (bil.get(0.5, (np.nan, np.nan))[1], 0.0)]
charge = [(3.95, 0.05), (4.24, 0.0), (bil.get(0.5, (np.nan, np.nan))[0], 0.0)]
x = np.arange(3)
ax.errorbar(x - 0.08, [c[0] for c in charge], yerr=[c[1] for c in charge], fmt='s', color=vs.INK2, ms=9, capsize=3,
            label='charge: half single-particle gap $E_g/2$')
ax.errorbar(x + 0.08, [s_[0] for s_ in spin], yerr=[s_[1] for s_ in spin], fmt='o', color=vs.C_HALF, ms=9, capsize=3,
            label='spin: NMR activation / spin gap')
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
ax.set_ylim(2.5, 6.5); ax.set_ylabel(r'energy ($D$)')
ax.set_title(r'(b) $\nu=1/2$: spin vs charge gap', loc='left')
ax.text(1, 3.0, 'unpaired quasiparticles carry\nboth spin and charge:\nthe two gaps coincide', ha='center', fontsize=7.8, color=vs.INK2)
ax.text(2, 2.75, 'triplon (rung singlet→triplet)\nabove the thermal charge\ngap, as measured', ha='center', fontsize=7.8, color=vs.INK2)
ax.legend(fontsize=8, loc='upper right')
plt.tight_layout(); plt.savefig('/app/figures/fig6_model_selection.png', dpi=130)
print(json.dumps({str(k): v for k, v in bil.items()}))
