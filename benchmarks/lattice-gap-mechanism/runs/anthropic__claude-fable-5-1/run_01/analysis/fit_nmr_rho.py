import json, numpy as np
from scipy.optimize import least_squares, curve_fit
with open('/app/measurements.json') as f:
    d = json.load(f)
nmr = {s['filling']: s for s in d['measurements'][1]['samples']}
res = {s['filling']: s for s in d['measurements'][2]['samples']}

print("=========== NMR: fits of ln(1/T1) = a + p ln T - Delta/T")
for nu in ['1/2', '≈0.3', '≈0.2']:
    s = nmr[nu]
    T = np.array(s['temperature']); r = np.array(s['one_over_T1']); u = np.array(s['uncertainty'])
    print(f"\n--- nu = {nu}")
    # choose range: significant points only (r > 2u) and T below where 1/T1T begins to saturate
    sig = r > 2.5*u
    if nu == '1/2':
        rng = sig & (T <= 2.2)
    elif nu == '≈0.3':
        rng = sig & (T <= 2.2)
    else:
        rng = sig & (T <= 0.6)   # BCS low-T tail below HS peak
    Tf, rf, uf = T[rng], r[rng], u[rng]
    print(f"  using {rng.sum()} points, T in [{Tf.min():.3f}, {Tf.max():.3f}]")
    for p in [0, 1, 2, None]:
        if p is None:
            def f(x, a, pp, D): return a + pp*np.log(x) - D/x
            popt, pcov = curve_fit(f, Tf, np.log(rf), p0=[2,1,4], sigma=uf/rf, absolute_sigma=True)
            chi2 = np.sum(((f(Tf,*popt)-np.log(rf))/(uf/rf))**2)
            print(f"  free p: a={popt[0]:.3f}, p={popt[1]:.3f}+-{np.sqrt(pcov[1,1]):.3f}, Delta={popt[2]:.3f}+-{np.sqrt(pcov[2,2]):.3f}, chi2/dof={chi2/(len(Tf)-3):.2f}")
        else:
            def f(x, a, D): return a + p*np.log(x) - D/x
            popt, pcov = curve_fit(f, Tf, np.log(rf), p0=[2,4], sigma=uf/rf, absolute_sigma=True)
            chi2 = np.sum(((f(Tf,*popt)-np.log(rf))/(uf/rf))**2)
            print(f"  p={p}: a={popt[0]:.3f}, Delta={popt[1]:.3f}+-{np.sqrt(pcov[1,1]):.3f}, chi2/dof={chi2/(len(Tf)-2):.2f}")
    # 1/T1T table
    print("  T, 1/T1T:", ", ".join(f"({Ti:.3g},{ri/Ti:.3g})" for Ti,ri in zip(T,r) if Ti>=1.0))

print("\n=========== Resistivity")
for nu in ['1/2', '≈0.3', '≈0.2']:
    s = res[nu]
    T = np.array(s['temperature']); r = np.array(s['resistivity']); u = np.array(s['uncertainty'])
    print(f"\n--- nu = {nu}")
    m = r > 0
    if (~m).any():
        Tzero = T[~m].max(); Tfirst = T[m].min()
        print(f"  rho = 0 up to T = {Tzero:.3f}; first finite at T = {Tfirst:.3f} (rho={r[m][0]:.3f}) -> Tc in ({Tzero:.3f}, {Tfirst:.3f})")
    Tf, rf, uf = T[m], r[m], u[m]
    # activated fit: ln rho = a + p ln T + Delta/T
    for p in [0, 1, None]:
        if p is None:
            def f(x, a, pp, D): return a + pp*np.log(x) + D/x
            popt, pcov = curve_fit(f, Tf, np.log(rf), p0=[0,0,2], sigma=uf/rf, absolute_sigma=True)
            chi2 = np.sum(((f(Tf,*popt)-np.log(rf))/(uf/rf))**2)
            print(f"  free p: a={popt[0]:.3f}, p={popt[1]:.3f}+-{np.sqrt(pcov[1,1]):.3f}, Delta={popt[2]:.3f}+-{np.sqrt(pcov[2,2]):.3f}, chi2/dof={chi2/(len(Tf)-3):.2f}")
        else:
            def f(x, a, D): return a + p*np.log(x) + D/x
            popt, pcov = curve_fit(f, Tf, np.log(rf), p0=[0,2], sigma=uf/rf, absolute_sigma=True)
            chi2 = np.sum(((f(Tf,*popt)-np.log(rf))/(uf/rf))**2)
            print(f"  p={p}: a={popt[0]:.3f}, Delta={popt[1]:.3f}+-{np.sqrt(pcov[1,1]):.3f}, chi2/dof={chi2/(len(Tf)-2):.2f}")
    # two-channel: rho = r_inf + A exp(D/T)
    try:
        def g(x, rinf, A, D): return rinf + A*np.exp(D/x)
        popt, pcov = curve_fit(g, Tf, rf, p0=[1, 0.2, 1.5], sigma=uf, absolute_sigma=True, maxfev=20000)
        chi2 = np.sum(((g(Tf,*popt)-rf)/uf)**2)
        print(f"  rho = rinf + A exp(D/T): rinf={popt[0]:.3f}+-{np.sqrt(pcov[0,0]):.3f}, A={popt[1]:.3f}, D={popt[2]:.3f}+-{np.sqrt(pcov[2,2]):.3f}, chi2/dof={chi2/(len(Tf)-3):.2f}")
    except Exception as e:
        print("  two-channel fit failed:", e)
    # linear fit
    def h(x, a, b): return a + b*x
    popt, pcov = curve_fit(h, Tf, rf, sigma=uf, absolute_sigma=True)
    chi2 = np.sum(((h(Tf,*popt)-rf)/uf)**2)
    print(f"  linear: rho = {popt[0]:.3f} + {popt[1]:.3f} T, chi2/dof={chi2/(len(Tf)-2):.2f}")
    # power law
    def pl(x, a, p): return a*x**(-p)
    popt, pcov = curve_fit(pl, Tf, rf, p0=[1,1], sigma=uf, absolute_sigma=True)
    chi2 = np.sum(((pl(Tf,*popt)-rf)/uf)**2)
    print(f"  power law: rho = {popt[0]:.3f} T^(-{popt[1]:.3f}), chi2/dof={chi2/(len(Tf)-2):.2f}")
