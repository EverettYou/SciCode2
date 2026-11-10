"""Reproduce the data analysis and the spectral non-uniqueness examples.

Run with Python 3.11 or later: python3 /app/analyze.py
Dependencies: numpy, scipy, matplotlib.  No external material data are used.

The ARPES examples are causal spectral completions, NOT solutions of a fitted
many-body Hamiltonian. This distinction is essential to the accompanying report.
All energies and temperatures in this file are in units of D.
"""

from pathlib import Path
import json
import numpy as np
from scipy.integrate import cumulative_trapezoid, trapezoid, quad
from scipy.ndimage import gaussian_filter1d, label
from scipy.optimize import least_squares, brentq
from scipy.signal import find_peaks
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)
DATA = json.loads((ROOT / "measurements.json").read_text())["measurements"]
COLORS = ["#bc3549", "#148257", "#3268bb"]
NUS = [0.5, 0.3, 0.2]
plt.rcParams.update({
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
    "savefig.dpi": 200,
    "font.family": "DejaVu Sans",
})


def native(x):
    if isinstance(x, dict):
        return {k: native(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)):
        return [native(v) for v in x]
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, np.generic):
        return x.item()
    return x


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def activation_fit(sample, experiment, tmax=np.inf, free_power=False):
    t = np.asarray(sample["temperature"])
    key = "one_over_T1" if experiment == "NMR" else "resistivity"
    y = np.asarray(sample[key])
    se = np.asarray(sample["uncertainty"])
    use = (t <= tmax) & (se > 0) & (y > 0)
    t, y, se = t[use], y[use], se[use]
    sign = -1 if experiment == "NMR" else 1

    def model(p):
        power = p[2] if free_power else (1 if experiment == "NMR" else 0)
        return np.exp(p[0] + power * np.log(t) + sign * p[1] / t)

    x0 = [0, 2, 1] if free_power else [0, 2]
    fit = least_squares(lambda p: (model(p) - y) / se, x0)
    # Absolute input errors are used. Do NOT shrink errors by sqrt(chi^2/dof).
    cov = np.linalg.inv(fit.jac.T @ fit.jac)
    return {
        "parameters": fit.x,
        "parameter_names": ["log_amplitude", "activation_energy"] +
                           (["rate_prefactor_power"] if free_power else []),
        "standard_errors": np.sqrt(np.diag(cov)),
        "covariance": cov,
        "chi2": np.sum(fit.fun**2),
        "dof": len(t) - len(fit.x),
        "n": len(t),
        "temperature_range": [t.min(), t.max()],
        "model": ("1/T1 = exp(a) * T^p * exp(-Delta/T)" if free_power else
                  "1/T1 = exp(a) * T * exp(-Delta/T)" if experiment == "NMR"
                  else "rho = exp(a) * exp(Ea/T)"),
        "uncertainty_assumption": "Diagonal supplied errors; no covariance was supplied.",
    }


RESULT = {"units": "D for energies and temperatures",
          "scope": "Empirical fits and explicit non-unique spectral completions; no fitted many-body Hamiltonian."}

nmr_fits, rho_fits = [], []
for i, sample in enumerate(DATA[1]["samples"]):
    tmax = [np.inf, 1.5, 0.7][i]
    fit = activation_fit(sample, "NMR", tmax)
    fit["filling"] = NUS[i]
    fit["free_prefactor_power_sensitivity"] = activation_fit(sample, "NMR", tmax, True)
    fit["fit_range_sensitivity"] = {
        str(cut): activation_fit(sample, "NMR", cut)
        for cut in ([1.5, 2.0, 4.5] if i == 0 else
                    [0.7, 1.0, 1.5, 4.5] if i == 1 else [0.6, 0.7, 0.9])
    }
    nmr_fits.append(fit)

for i, sample in enumerate(DATA[2]["samples"][:2]):
    fit = activation_fit(sample, "resistivity")
    fit["filling"] = NUS[i]
    rho_fits.append(fit)

RESULT["NMR_activation_fits"] = nmr_fits
RESULT["resistivity_activation_fits"] = rho_fits
tc = {}
for i in [1, 2]:
    s = DATA[2]["samples"][i]
    t, y = np.asarray(s["temperature"]), np.asarray(s["resistivity"])
    tc[str(NUS[i])] = [float(t[y == 0].max()), float(t[y > 0].min())]
RESULT["resistive_transition_brackets"] = tc

s = DATA[2]["samples"][2]
t, y, se = (np.asarray(s[k]) for k in ["temperature", "resistivity", "uncertainty"])
take = y > 0
linear = least_squares(lambda p: (p[0] + p[1] * t[take] - y[take]) / se[take], [.1, .2])
cov = np.linalg.inv(linear.jac.T @ linear.jac)
RESULT["normal_resistivity_nu_0.2_linear_fit"] = {
    "intercept_slope": linear.x, "standard_errors": np.sqrt(np.diag(cov)),
    "chi2": sum(linear.fun**2), "dof": sum(take)-2,
    "interpretation": "Empirical increasing rho(T), not a microscopic scattering mechanism."
}

# Plot the actual transformation of the supplied rates and the fitted functions.
fig, ax = plt.subplots(1, 2, figsize=(11, 4.3), layout="constrained")
for i, s in enumerate(DATA[1]["samples"]):
    t, y, se = (np.asarray(s[k]) for k in ["temperature", "one_over_T1", "uncertainty"])
    ax[0].errorbar(1/t, y/t, se/t, color=COLORS[i], fmt="o", ms=3, lw=.7,
                   capsize=2, label=fr"$\nu={NUS[i]:g}$")
    fit = nmr_fits[i]
    tt = np.linspace(*fit["temperature_range"], 500)
    a, d = fit["parameters"]
    ax[0].plot(1/tt, np.exp(a-d/tt), color=COLORS[i], lw=1.6)
ax[0].set(xlabel=r"$D/T$", ylabel=r"Normalized $1/(T_1 T)$", yscale="log",
          ylim=(5e-6, 4), xlim=(0, 5.1), title="NMR: divide the JSON rates by T")
ax[0].legend(frameon=False)
for i, s in enumerate(DATA[2]["samples"]):
    t, y, se = (np.asarray(s[k]) for k in ["temperature", "resistivity", "uncertainty"])
    take = y > 0
    ax[1].errorbar(1/t[take], y[take], se[take], color=COLORS[i], fmt="o", ms=3,
                  lw=.7, capsize=2, label=fr"$\nu={NUS[i]:g}$")
    if i < 2:
        xx = np.linspace((1/t[take]).min(), (1/t[take]).max(), 400)
        a, d = rho_fits[i]["parameters"]
        ax[1].plot(xx, np.exp(a+d*xx), color=COLORS[i], lw=1.6)
ax[1].set(xlabel=r"$D/T$", ylabel=r"$\rho(T)/\rho(4D)$", yscale="log",
          title="Resistivity: nonzero values only", ylim=(.2, 4000))
ax[1].legend(frameon=False)
save(fig, "activation_fits")

# Peak locations and gap-edge sensitivity are empirical descriptors, not U or Delta.
features = []
fig, ax = plt.subplots(2, 2, figsize=(11, 7), layout="constrained")
for i, s in enumerate(DATA[0]["spectra"]):
    x, y = np.asarray(s["bias"]), np.asarray(s["dI_dV"])
    smooth = gaussian_filter1d(y, 1.5)
    peaks = find_peaks(smooth, prominence=.09, distance=15)[0]
    peaks = peaks[np.abs(x[peaks]) < 8]
    feature = {"panel": s["panel"], "peaks": x[peaks],
               "smoothing_sigma_D": .0375, "sample_spacing_D": .025}
    if i < 3:
        edge_list = []
        smooth2 = gaussian_filter1d(y, 2)
        # Require a sustained crossing to avoid calling a noise spike an edge.
        for threshold in [.03, .05, .075, .10]:
            ee = []
            for side in [-1, 1]:
                ids = np.flatnonzero(side*x > 0)
                ids = ids[np.argsort(np.abs(x[ids]))]
                hits = np.flatnonzero(np.convolve((smooth2[ids] > threshold).astype(int),
                                                  np.ones(5, dtype=int), "valid") == 5)
                ee.append(float(x[ids[hits[0]]]) if len(hits) else None)
            edge_list.append({"threshold": threshold, "negative_positive_edge": ee})
        feature["threshold_edge_sensitivity_not_confidence_intervals"] = edge_list
    features.append(feature)
    a = ax.ravel()[i]
    color = COLORS[min(i, 2)] if i != 3 else COLORS[1]
    a.plot(x, y, color=color, alpha=.45, lw=.6)
    a.plot(x, smooth, color=color, lw=1.2)
    a.axvline(0, color=".6", lw=.7)
    for p in peaks:
        a.annotate(f"{x[p]:g}", (x[p], smooth[p]), (0, 8), textcoords="offset points",
                   ha="center", fontsize=8)
    a.set(xlim=(-10, 10), ylim=(-.025, 1.18), xlabel=r"Recorded bias / $D$",
          ylabel="Normalized conductance", title=f"({s['panel']}) {s['filling']}, {s['temperature']} T")
save(fig, "sts_features")
RESULT["STS_empirical_features"] = features


# Optional and explicitly conditional one-band DOS fit to panel (d).
# Integrate over ky analytically, then kx numerically. No many-body self-energy
# is fitted: eta is a constant Lorentzian broadening, an additional assumption.
COS = np.cos(2*np.pi*(np.arange(512)+.5)/512)


def square_dos(energy, hopping, ratio, eta):
    tp = hopping*ratio
    z = energy[:, None] + 1j*eta
    aa = -2*hopping*COS[None, :]
    bb = -2*hopping-4*tp*COS[None, :]
    root = np.sqrt((z-aa)**2-bb**2)
    root = np.where(root.imag < 0, -root, root)
    return -(1/root).mean(axis=1).imag/np.pi


def dos_model(x, p):
    t, r, mu, eta, scale, b0, b1, b2 = p
    return scale*square_dos(x+mu, t, r, eta) + b0+b1*x+b2*x*x


high = DATA[0]["spectra"][3]
xx, yy = np.asarray(high["bias"]), np.asarray(high["dI_dV"])
fit = least_squares(lambda p: dos_model(xx, p)-yy,
                    [1, .15, -1, .08, 3, .025, 0, .001],
                    bounds=([.3, -.45, -5, .02, .1, -.2, -.04, -.005],
                            [2, .45, 5, 1, 20, .4, .04, .01]),
                    max_nfev=180)
resid = fit.fun
variance = np.sum(resid**2)/(len(xx)-len(fit.x))
dcov = np.linalg.inv(fit.jac.T @ fit.jac)*variance
tt, rr = fit.x[:2]
tp_error = np.sqrt(rr**2*dcov[0, 0]+tt**2*dcov[1, 1]+2*rr*tt*dcov[0, 1])
RESULT["conditional_high_T_DOS_fit"] = {
    "model": "rho_square(t,tprime,mu,constant_eta) * scale + b0+b1*V+b2*V^2",
    "parameter_names": ["t", "tprime/t", "mu", "eta", "scale", "b0", "b1", "b2"],
    "parameters": fit.x, "formal_standard_errors": np.sqrt(np.diag(dcov)),
    "tprime": tt*rr, "tprime_formal_standard_error": tp_error,
    "rms_residual": np.sqrt(np.mean(resid**2)), "kx_quadrature_points": 512,
    "caution": "A conditional effective band fit. Errors use an iid residual model, since STS errors are absent. Not bare Hamiltonian coefficients or total uncertainties."
}
fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
ax.plot(xx, yy, color=COLORS[1], alpha=.5, lw=.7, label="Panel (d), as supplied")
ax.plot(xx, dos_model(xx, fit.x), color="black", lw=1.3, label="Conditional square-band DOS fit")
ax.set(xlabel=r"Bias / $D$", ylabel="Normalized conductance", xlim=(-10, 10),
       title="One possible effective dispersion; no interacting self-energy included")
ax.legend(frameon=False, fontsize=9)
save(fig, "conditional_dos_fit")

# The observational diagram deliberately does not invent phase boundaries at
# unmeasured fillings. Normal-state transport labels are not thermodynamic phases.
fig, ax = plt.subplots(figsize=(10, 5.5), layout="constrained")
ax.set_facecolor("#f0f1f3")
ax.set(xlim=(0, 1), ylim=(0, 4.5), xlabel=r"Filling $\nu$ (two electrons/site at $\nu=1$)",
       ylabel=r"Temperature $T/D$", title="Phase constraints from the supplied measurements")
ax.text(.77, 2.8, "Unmeasured fillings\nNo determined phase boundaries", ha="center", color=".4")
for nu, color in zip(NUS, COLORS):
    ax.axvline(nu, color=color, ls="--", lw=1)
    ax.text(nu, 4.32, fr"$\nu={nu:g}$", ha="center", color=color)
width = .014
for nu, color in [(.2, COLORS[2]), (.3, COLORS[1])]:
    lo, hi = tc[str(nu)]
    ax.fill_betweenx([0, lo], nu-width, nu+width, color=color, alpha=.7)
    ax.fill_betweenx([lo, hi], nu-width*1.6, nu+width*1.6, color=color, alpha=.25)
    ax.plot([nu, nu], [hi, 4], color=color, lw=5, alpha=.6)
    ax.annotate(f"Tc ∈ [{lo:g}, {hi:g}]", (nu, (lo+hi)/2),
                (nu+.055, (lo+hi)/2+.32), arrowprops={"arrowstyle": "-", "lw": .7},
                fontsize=8, color=color)
ax.plot([.5, .5], [.45, 4], color=COLORS[0], lw=6, alpha=.7)
ax.plot([.5, .5], [0, .45], color=COLORS[0], lw=3, ls=":")
ax.text(.17, .52, "Gapped SC", rotation=90, ha="center", va="center", color=COLORS[2], fontsize=9)
ax.text(.272, .10, "SC", color=COLORS[1], fontsize=9)
ax.text(.174, 2.85, "Metallic normal transport", rotation=90, ha="center", va="center", color=COLORS[2])
ax.text(.323, 2.8, "Activated normal transport", rotation=90, ha="center", va="center", color=COLORS[1])
ax.text(.53, 2.4, "Insulating; spin relaxation activated", rotation=90,
        ha="center", va="center", color=COLORS[0])
ax.text(.03, 4.1, "Lines mark samples, not phase boundaries", color=".35", fontsize=9)
ax.text(.67, .45, "No justified reflection about ν = 1/2.\nThe high-T STS temperature is unspecified.",
        color=".35", fontsize=9)
save(fig, "phase_constraints")


# -------------------------------------------------------------------------
# Causal spectral completions demonstrating momentum non-identifiability.
# -------------------------------------------------------------------------
# Separate normalized negative/positive energy densities retain the observed
# line shapes. Their weights are set to nu and 1-nu, granting more information
# (a calibrated local spectral DOS and known filling) than STS alone supplies.
# This rescaling is explicit; it is NOT an assertion of a constant tunneling
# matrix element for the actual measurements. Gap masks and smoothing are
# illustrative preprocessing, not extracted microscopic gaps.
GAP_MASK = [3.5, 2.1, 1.4]
MARGINALS = []
for i, s in enumerate(DATA[0]["spectra"][:3]):
    x = np.asarray(s["bias"])
    shape = gaussian_filter1d(np.asarray(s["dI_dV"]), 2)
    shape[np.abs(x) < GAP_MASK[i]] = 0
    marg = []
    integrals = []
    for select in [x < 0, x > 0]:
        energy, raw = x[select], shape[select]
        cumulative = cumulative_trapezoid(raw, energy, initial=0)
        integrals.append(float(cumulative[-1]))
        density = raw/cumulative[-1]
        cumulative /= cumulative[-1]
        # Remove duplicate CDF values in zero-density intervals for interpolation.
        unique_cdf, ids = np.unique(cumulative, return_index=True)
        # Use the last zero-CDF point, avoiding interpolation through the gap
        # at an arbitrarily small positive quantile.
        ids[0] = np.flatnonzero(cumulative == unique_cdf[0])[-1]
        marg.append({"energy": energy, "density": density,
                     "cdf_energy": energy[ids], "cdf": cumulative[ids]})
    MARGINALS.append(marg)
    RESULT.setdefault("illustrative_preprocessing", []).append({
        "nu": NUS[i], "gap_mask": GAP_MASK[i], "smoothing_sigma": .05,
        "negative_positive_integrals_before_branch_normalization": integrals,
        "assumption": "Normalize each branch separately; assign total weights nu and 1-nu."
    })


def quantile(nu_index, branch, u):
    marg = MARGINALS[nu_index][branch]
    return np.interp(u, marg["cdf"], marg["cdf_energy"])


def ranked_dispersion(n, b):
    k = (np.arange(n)+.5)/n - .5
    c = np.cos(2*np.pi*k)
    e = -c[:, None]-c[None, :]-b*c[:, None]*c[None, :]
    ordered = np.sort(e.ravel())
    # The midpoint convention handles symmetry-related degeneracies without
    # assigning different ranks to equal-energy momenta.
    u = (np.searchsorted(ordered, e, side="left") +
         np.searchsorted(ordered, e, side="right"))/(2*len(ordered))
    return k, e, ordered, u


def ranks_on_path(kx, ky, b, ordered):
    cx, cy = np.cos(2*np.pi*kx), np.cos(2*np.pi*ky)
    e = -cx-cy-b*cx*cy
    return (np.searchsorted(ordered, e, side="left") +
            np.searchsorted(ordered, e, side="right"))/(2*len(ordered))


# A uses the same rank ordering for the two branches; B uses different
# C4-symmetric orderings. Both have exactly the same local DOS in the continuum.
CASES = {"A": (.4, .4), "B": (-.8, .8)}
cache = {b: ranked_dispersion(1024, b) for b in [.4, -.8, .8]}

vertices = np.array([[0, 0], [.5, 0], [.5, .5], [0, 0]])
path_parts = [np.linspace(vertices[i], vertices[i+1], count, endpoint=False)
              for i, count in enumerate([200, 200, 283])]
path = np.vstack(path_parts + [vertices[-1][None, :]])
path_distance = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
ticks = [0, .5, 1, 1+np.sqrt(.5)]
labels = [r"$\Gamma$", r"$X$", r"$M$", r"$\Gamma$"]
omega = np.linspace(-10.5, 10.5, 1201)
display_sigma = .065
plot_poles = {}

fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True, sharey=True, layout="constrained")
for row, (name, (bm, bp)) in enumerate(CASES.items()):
    um = ranks_on_path(path[:, 0], path[:, 1], bm, cache[bm][2])
    up = ranks_on_path(path[:, 0], path[:, 1], bp, cache[bp][2])
    for col, nu in enumerate(NUS):
        em, ep = quantile(col, 0, um), quantile(col, 1, up)
        intensity = (nu*np.exp(-.5*((omega[:, None]-em)/display_sigma)**2) +
                     (1-nu)*np.exp(-.5*((omega[:, None]-ep)/display_sigma)**2))
        intensity /= np.sqrt(2*np.pi)*display_sigma
        plot_poles[(name, col)] = (em, ep)
        a = axes[row, col]
        im = a.pcolormesh(path_distance, omega, intensity, cmap="magma", shading="auto", rasterized=True,
                          norm=PowerNorm(gamma=.5, vmin=0, vmax=5))
        a.axhline(0, color="white", lw=.55, ls="--", alpha=.75)
        for point in ticks[1:-1]:
            a.axvline(point, color="white", lw=.35, alpha=.45)
        a.set(xticks=ticks, xticklabels=labels, ylim=(-10.2, 10.2),
              title=fr"Completion {name}, $\nu={nu:g}$")
        if col == 0:
            a.set_ylabel(r"Energy / $D$ (assumed midgap zero)")
        if row == 1:
            a.set_xlabel("Momentum path")
fig.colorbar(im, ax=axes.ravel().tolist(), shrink=.85, label=r"Illustrative $A(\mathbf{k},\omega)$ / $D^{-1}$")
fig.suptitle("Non-unique ARPES examples with identical local DOS in each column\n"
             "Causal spectral constructions; not predictions of a fitted Hamiltonian", fontsize=12)
save(fig, "arpes_nonuniqueness")

# Verify the Kramers--Kronig integral explicitly for the displayed half-filled
# path. Gaussian broadening is only for plotting/integration. Zero contours
# below use the exact delta-pole (zero-broadening) limit.
wint = np.linspace(-12, 12, 9601)
sigma_kk = .025
kk_results = {}
for name in CASES:
    em, ep = plot_poles[(name, 0)]
    sel = np.arange(0, len(em), 10)
    spectral = (.5*np.exp(-.5*((wint[:, None]-em[sel])/sigma_kk)**2) +
                .5*np.exp(-.5*((wint[:, None]-ep[sel])/sigma_kk)**2))
    spectral /= np.sqrt(2*np.pi)*sigma_kk
    inverse = np.divide(-1., wint, out=np.zeros_like(wint), where=np.abs(wint)>1e-12)
    g_numeric = trapezoid(spectral*inverse[:, None], wint, axis=0)
    g_poles = -.5/em[sel]-.5/ep[sel]
    kk_results[name] = {
        "max_absolute_KK_vs_delta_poles_difference": np.max(np.abs(g_numeric-g_poles)),
        "max_spectral_sum_rule_error": np.max(np.abs(trapezoid(spectral, wint, axis=0)-1)),
        "max_filling_sum_rule_error": np.max(np.abs(trapezoid(spectral[wint<0], wint[wint<0], axis=0)-.5)),
        "integration_points": len(wint), "integration_window": [-12, 12],
        "Gaussian_sigma_for_KK_check": sigma_kk,
    }
RESULT["KK_numerical_verification"] = kk_results

# Verify the central counterexample claim directly: the BZ-integrated spectra
# agree despite the different momentum assignments. Histogram broadening below
# is a numerical comparison, not a fit to the original tunneling matrix element.
edges = np.linspace(-10.5, 10.5, 1681)
centers = .5*(edges[:-1]+edges[1:])
bin_width = edges[1]-edges[0]
local_dos_checks = []
fig, axes = plt.subplots(1, 3, figsize=(12, 3.4), layout="constrained")
for col, nu in enumerate(NUS):
    curves = {}
    for name, (bm, bp) in CASES.items():
        em = quantile(col, 0, cache[bm][3])
        ep = quantile(col, 1, cache[bp][3])
        hm = np.histogram(em, bins=edges)[0]/em.size/bin_width
        hp = np.histogram(ep, bins=edges)[0]/ep.size/bin_width
        curves[name] = gaussian_filter1d(nu*hm+(1-nu)*hp, display_sigma/bin_width)
    axes[col].plot(centers, curves["A"], lw=1.7, color=COLORS[col], label="Completion A")
    axes[col].plot(centers, curves["B"], lw=1, ls="--", color="black", label="Completion B")
    axes[col].set(xlabel=r"Energy / $D$", ylabel=r"Local DOS / $D^{-1}$", title=fr"$\nu={nu:g}$")
    if col == 0:
        axes[col].legend(frameon=False, fontsize=8)
    local_dos_checks.append({
        "nu": nu,
        "integrated_absolute_difference": float(trapezoid(np.abs(curves["A"]-curves["B"]), centers)),
        "maximum_absolute_difference": float(np.max(np.abs(curves["A"]-curves["B"]))),
        "interpretation": "Only finite BZ-grid/histogram error; the continuum equality follows analytically."
    })
fig.suptitle("Different momentum spectra, the same local spectral density", fontsize=12)
save(fig, "local_dos_verification")
RESULT["local_DOS_nonuniqueness_verification"] = local_dos_checks

areas = {}
fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), layout="constrained")
for a, (name, (bm, bp)) in zip(axes[:2], CASES.items()):
    k = cache[bm][0]
    em = quantile(0, 0, cache[bm][3])
    ep = quantile(0, 1, cache[bp][3])
    g0 = -.5/em-.5/ep
    inside_gamma = g0 < 0
    fraction = float(inside_gamma.mean())
    # The chosen examples should have one connected Gamma-side region.
    components = label(inside_gamma)[1]
    a.contourf(k, k, g0.T, levels=[-1, 0, 1], colors=["#87aed6", "#f0ddaa"], alpha=.85)
    a.contour(k, k, g0.T, levels=[0], colors=["#182c43"], linewidths=1.5)
    a.scatter([0], [0], c="black", s=14)
    a.text(.015, .015, r"$\Gamma$")
    a.set(xlabel=r"$k_x/(2\pi/a)$", ylabel=r"$k_y/(2\pi/a)$", aspect="equal",
          title=f"Completion {name}: Γ-side area = {fraction:.4f}",
          xlim=(-.5, .5), ylim=(-.5, .5), xticks=[-.5, 0, .5], yticks=[-.5, 0, .5])
    areas[name] = {"fraction_Gamma_side": fraction, "Gamma_side_sign_ReG0": "negative",
                   "grid": [1024, 1024], "Gamma_region_connected_components": components,
                   "rank_parameters_negative_positive_branches": [bm, bp]}

# A third completion shows that equality to nu is not excluded either. It has
# the same pminus/pplus but momentum-dependent residues and broad spectra.
minus, plus = MARGINALS[0]
cm = trapezoid(minus["density"]/(-minus["energy"]), minus["energy"])
cp = trapezoid(plus["density"]/plus["energy"], plus["energy"])
weight_zero = cp/(cm+cp)
threshold = (weight_zero-.5)/.15


def residue_area(b):
    boundary = np.arccos(np.clip((threshold-1)/(1+b), -1, 1))
    def integrand(x):
        return np.arccos(np.clip((threshold-np.cos(x))/(1+b*np.cos(x)), -1, 1))
    return quad(integrand, 0, np.pi, points=[boundary], epsabs=1e-11)[0]/np.pi**2


bc = brentq(lambda b: residue_area(b)-.5, .2, .8, xtol=1e-12)
k = cache[.4][0]
cc = np.cos(2*np.pi*k)
weight = .5+.15*(cc[:, None]+cc[None, :]+bc*cc[:, None]*cc[None, :])
gc = weight*cm-(1-weight)*cp
a = axes[2]
a.contourf(k, k, gc.T, levels=[-1, 0, 1], colors=["#f0ddaa", "#87aed6"], alpha=.85)
a.contour(k, k, gc.T, levels=[0], colors=["#182c43"], linewidths=1.5)
a.scatter([0], [0], c="black", s=14)
a.text(.015, .015, r"$\Gamma$")
a.set(xlabel=r"$k_x/(2\pi/a)$", ylabel=r"$k_y/(2\pi/a)$", aspect="equal",
      title="Completion C: Γ-side area = 0.5000", xlim=(-.5, .5), ylim=(-.5, .5),
      xticks=[-.5, 0, .5], yticks=[-.5, 0, .5])
areas["C"] = {
    "fraction_Gamma_side_continuum": residue_area(bc),
    "fraction_Gamma_side_grid": float(np.mean(gc > 0)),
    "Gamma_side_sign_ReG0": "positive", "grid": [1024, 1024],
    "Gamma_region_connected_components": int(label(gc > 0)[1]),
    "freely_chosen_residue_coefficient_a": .15,
    "residue_b_chosen_to_make_area_one_half": bc,
    "inverse_energy_moments_minus_plus": [cm, cp],
    "zero_residue_weight": weight_zero,
    "spectral_formula": "A_C(k,w)=weight(k)*pminus(w)+(1-weight(k))*pplus(w)",
    "residue_formula": "weight(k)=0.5+0.15*(cos(2*pi*kx)+cos(2*pi*ky)+b*cos(2*pi*kx)*cos(2*pi*ky))",
    "interpretation": "A further causal example; area equality is chosen, not measured."
}
fig.suptitle("Different zero curves at the same filling ν = 1/2 and the same local DOS\n"
             "Illustrations only: none of these areas is determined by the measurements", fontsize=12)
save(fig, "zero_contour_nonuniqueness")

# Quantile ordering in A gives its zero area directly: solve Q_-(u)+Q_+(u)=0.
u0 = brentq(lambda u: quantile(0, 0, u)+quantile(0, 1, u), 1e-8, 1-1e-8)
areas["A"]["continuum_rank_fraction"] = u0

# One independent finer integration checks the area discretization error.
for name, (bm, bp) in CASES.items():
    refined = {}
    for b in set([bm, bp]):
        refined[b] = ranked_dispersion(1536, b)[3]
    em, ep = quantile(0, 0, refined[bm]), quantile(0, 1, refined[bp])
    areas[name]["fraction_on_1536_by_1536_grid"] = float(np.mean(-.5/em-.5/ep < 0))
    del refined, em, ep
RESULT["illustrative_zero_areas_NOT_inferences"] = areas
RESULT["spectral_construction"] = {
    "formula": "A_nu(k,w) = nu delta(w-Qminus(F_bminus(e_bminus(k)))) + (1-nu) delta(w-Qplus(F_bplus(e_bplus(k))))",
    "dispersion_rank_function": "e_b(k) = -cos(2 pi kx)-cos(2 pi ky)-b cos(2 pi kx) cos(2 pi ky)",
    "status": "A mathematical counterexample to uniqueness; no inferred hopping coefficients or pairing Hamiltonian.",
    "ARPES_matrix_element": "Set to 1 for both illustrative completions.",
    "energy_reference": "Midgap; assumed chemical potential for doped examples, stipulated by problem for half filling.",
    "display_Gaussian_sigma": display_sigma,
    "momentum_path_points": len(path),
    "local_DOS": "nu*pminus(w)+(1-nu)*pplus(w), identical in A and B in the continuum",
    "per_momentum_spectral_sum_rule": 1,
    "per_spin_filling": "nu, exactly, because all negative poles are occupied at zero temperature",
}

(ROOT / "results.json").write_text(json.dumps(native(RESULT), indent=2, ensure_ascii=False)+"\n")
print(json.dumps(native({
    "NMR_gaps": [(f["filling"], f["parameters"][1], f["standard_errors"][1]) for f in nmr_fits],
    "rho_gaps": [(f["filling"], f["parameters"][1], f["standard_errors"][1]) for f in rho_fits],
    "Tc_brackets": tc,
    "conditional_band_fit": RESULT["conditional_high_T_DOS_fit"],
    "illustrative_zero_areas": areas,
    "KK_checks": kk_results,
}), indent=2))
