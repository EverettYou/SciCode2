#!/usr/bin/env python3
"""Reproduce the measurement analysis and the spectral non-identifiability example.

Only measurements.json supplies experimental numbers.  No compound data are used.
The spectral examples are deliberately NOT a many-body solution or a prediction.
Run: python3 analyze.py
"""
from pathlib import Path
import json

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm, TwoSlopeNorm
from scipy.optimize import least_squares
from scipy.signal import savgol_filter, find_peaks

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "measurements.json").read_text())["measurements"]
COLORS = ["#bd3545", "#008b68", "#315ec3"]
LABELS = [r"$\nu=1/2$", r"$\nu\simeq0.3$", r"$\nu\simeq0.2$"]
plt.rcParams.update({
    "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 11,
    "figure.dpi": 120, "savefig.dpi": 180, "axes.spines.top": False,
    "axes.spines.right": False, "mathtext.fontset": "dejavusans",
})


def savefig(fig, stem):
    fig.savefig(ROOT / (stem + ".png"), bbox_inches="tight")
    fig.savefig(ROOT / (stem + ".pdf"), bbox_inches="tight")
    plt.close(fig)


def activation_fit(t, y, err, mask, sign, free_power=False):
    """Fit in the measured linear ordinate; do not log noise-floor points.

    y = exp(log_a + sign * E * (1/t - 1/4)) * (t/4)**p.
    Quoted covariance treats the supplied marginal errors as independent 1 sigma.
    A free amplitude absorbs an overall normalization. No reduced-chi-square
    rescaling is made because the supplied uncertainties are used as given.
    """
    tt, yy, ee = t[mask], y[mask], err[mask]

    def residual(par):
        power = par[2] if free_power else 0.0
        model = np.exp(par[0] + sign * par[1] * (1 / tt - .25)
                       + power * np.log(tt / 4))
        return (model - yy) / ee

    par0 = [0., 3.] + ([0.] if free_power else [])
    fit = least_squares(residual, par0, max_nfev=2000)
    covariance = np.linalg.inv(fit.jac.T @ fit.jac)
    errors = np.sqrt(np.diag(covariance))
    return {
        "log_amplitude_at_T4": float(fit.x[0]),
        "activation_energy_D": float(fit.x[1]),
        "activation_energy_1sigma_D": float(errors[1]),
        "power": float(fit.x[2]) if free_power else 0.0,
        "power_fitted": bool(free_power),
        "power_1sigma": float(errors[2]) if free_power else None,
        "chi2": float(np.dot(fit.fun, fit.fun)),
        "dof": int(mask.sum() - len(par0)),
        "T_range_D": [float(tt.min()), float(tt.max())],
        "n_points": int(mask.sum()),
        "covariance": covariance.tolist(),
    }


def predicted_activation(t, fit, sign):
    return np.exp(fit["log_amplitude_at_T4"]
                  + sign * fit["activation_energy_D"] * (1 / t - .25)
                  + fit["power"] * np.log(t / 4))


def analyze_rates(results):
    results["NMR_activation"] = []
    results["resistivity_activation"] = []
    results["transition_brackets"] = []
    fig, ax = plt.subplots(1, 2, figsize=(11.6, 4.3))
    for j, sample in enumerate(DATA[1]["samples"]):
        t = np.array(sample["temperature"])
        # The JSON reports 1/T1, NOT 1/(T1*T).
        y = np.array(sample["one_over_T1"]) / t
        err = np.array(sample["uncertainty"]) / t
        mask = t <= 4.4318
        if j == 1:
            mask &= t >= .3085
        if j == 2:
            mask = t <= .622
        fixed = activation_fit(t, y, err, mask, -1)
        free = activation_fit(t, y, err, mask, -1, True)
        results["NMR_activation"].append({
            "filling": sample["filling"], "constant_prefactor": fixed,
            "free_power_prefactor": free,
        })
        ax[0].errorbar(1 / t, y, yerr=err, fmt="o", ms=3, capsize=2,
                       color=COLORS[j], alpha=.8, label=LABELS[j])
        tt = np.geomspace(t[mask].min(), t[mask].max(), 250)
        ax[0].plot(1 / tt, predicted_activation(tt, fixed, -1), color=COLORS[j])
    ax[0].set(xlabel=r"$D/T$", ylabel=r"Normalized $1/(T_1T)$",
              yscale="log", ylim=(1e-5, 3), xlim=(0, 5.1),
              title="NMR: correct temperature division and activated fits")
    ax[0].legend(loc="upper right", frameon=False)

    for j, sample in enumerate(DATA[2]["samples"]):
        t = np.array(sample["temperature"])
        y = np.array(sample["resistivity"])
        err = np.array(sample["uncertainty"])
        positive = y > 0
        ax[1].errorbar(1 / t[positive], y[positive], yerr=err[positive],
                       fmt="o", ms=3, capsize=2, color=COLORS[j], alpha=.8)
        if j < 2:
            fixed = activation_fit(t, y, err, positive, +1)
            free = activation_fit(t, y, err, positive, +1, True)
            results["resistivity_activation"].append({
                "filling": sample["filling"], "constant_prefactor": fixed,
                "free_power_prefactor": free,
            })
            tt = np.geomspace(t[positive].min(), t[positive].max(), 250)
            ax[1].plot(1 / tt, predicted_activation(tt, fixed, +1), color=COLORS[j])
        if j > 0:
            lo, hi = float(t[~positive].max()), float(t[positive].min())
            results["transition_brackets"].append({
                "filling": sample["filling"], "last_zero_resistance_T_D": lo,
                "first_nonzero_resistance_T_D": hi,
                "bracket_midpoint_D": (lo + hi) / 2,
                "bracket_halfwidth_D": (hi - lo) / 2,
                "meaning": "sampling bracket, not a statistical confidence interval",
            })
        else:
            results["half_filling_lowest_resistivity_temperature_D"] = float(t.min())
    ax[1].set(xlabel=r"$D/T$", ylabel=r"$\rho(T)/\rho(4D)$", yscale="log",
              ylim=(.2, 4000), xlim=(0, 2.65),
              title="Resistivity: fits use only nonzero data")
    fig.text(.5, -.015,
             "Lines fit observable activation scales; they are not microscopic coupling constants.",
             ha="center", fontsize=10)
    fig.tight_layout()
    savefig(fig, "activation_fits")


def sts_features(results):
    fig, axes = plt.subplots(2, 2, figsize=(11.4, 7.3), sharex=True)
    rows = []
    for j, (s, ax) in enumerate(zip(DATA[0]["spectra"], axes.flat)):
        x, y = np.array(s["bias"]), np.array(s["dI_dV"])
        smoothed = savgol_filter(y, 15, 3)
        peaks, _ = find_peaks(smoothed, prominence=.075)
        if j == 3:
            peaks = peaks[(x[peaks] > -1) & (x[peaks] < 3)]
        elif j == 2:
            peaks = peaks[(x[peaks] > -4) & (x[peaks] < 5)]
        else:
            peaks = peaks[np.abs(x[peaks]) < 8]
        residual = y - smoothed
        sigma_rough = float(np.median(np.abs(residual - np.median(residual))) / .67449)
        ax.plot(x, y, lw=.55, color=COLORS[min(j, 2)], alpha=.55)
        ax.plot(x, smoothed, lw=1.1, color="#202a36")
        for idx in peaks:
            ax.axvline(x[idx], ls=":", lw=.8, color="#808080")
            ax.text(x[idx], 1.12, f"{x[idx]:.2f}", ha="center", fontsize=9)
        ax.set(ylim=(-.04, 1.25), xlim=(-10, 10), ylabel="Normalized conductance",
               title=f"({s['panel']})  {s['filling']}, {s['temperature']} T")
        rows.append({"panel": s["panel"], "filling": s["filling"],
                     "smoothed_peak_bias_D": x[peaks].tolist(),
                     "rough_high_frequency_noise_scale": sigma_rough,
                     "bias_step_D": float(x[1] - x[0]),
                     "note": "Noise estimate is descriptive; no STS uncertainty array is supplied."})
    for ax in axes[1]:
        ax.set_xlabel(r"Bias energy / $D$ (origin as specified in the input)")
    results["STS_features"] = rows
    fig.tight_layout()
    savefig(fig, "sts_features")


def conditional_band_fit(results):
    """A DOS fit conditional on a very restrictive, explicitly stated band model.

    Integrate ky analytically and kx with 420 midpoint quadrature nodes.  This
    is a one-electron DOS calculation, not an interacting cluster calculation.
    """
    s = DATA[0]["spectra"][3]
    x, y = np.array(s["bias"]), np.array(s["dI_dV"])
    cosine = np.cos((np.arange(420) + .5) * np.pi / 420)

    def model(p):
        t1, t2, mu, eta, scale, b0, b2 = p
        z = x[:, None] + mu + 2 * t1 * cosine[None, :] + 1j * eta
        b = 2 * t1 + 4 * t2 * cosine[None, :]
        g = np.mean(1 / (np.sqrt(z - b) * np.sqrt(z + b)), axis=1)
        return -scale * g.imag / np.pi + b0 + b2 * x * x

    fit = least_squares(lambda p: model(p) - y,
                        [1., .2, -.8, .07, 2., .01, .001],
                        bounds=([.5, -.4, -3., .005, .1, -.2, -.01],
                                [2., .6, 1., 1., 10., .3, .01]), max_nfev=200)
    sigma = np.sqrt(np.dot(fit.fun, fit.fun) / (len(x) - len(fit.x)))
    covariance = np.linalg.inv(fit.jac.T @ fit.jac) * sigma ** 2
    names = ["t1_D", "t2_D", "mu_D", "Lorentz_width_D", "amplitude",
             "background_constant", "background_quadratic"]
    result = {
        "parameters": dict(zip(names, fit.x.tolist())),
        "conditional_1sigma": dict(zip(names, np.sqrt(np.diag(covariance)).tolist())),
        "residual_rms": float(sigma), "kx_quadrature_points": len(cosine),
        "assumptions": "High-temperature STS is the DOS of a noninteracting square lattice with only NN and both NNN hoppings, a constant tunneling matrix element, Lorentz broadening, and a quadratic background. The uncertainty omits all model error. The high STS temperature is unspecified, so no thermal number equation was imposed.",
    }
    results["conditional_band_fit"] = result
    (ROOT / "conditional_band_fit.json").write_text(json.dumps(result, indent=2) + "\n")
    fig, (ax, resid) = plt.subplots(2, 1, figsize=(9, 5.6), sharex=True,
                                  gridspec_kw={"height_ratios": [3, 1]})
    ax.plot(x, y, color="#999999", lw=.65, label="Panel (d) measurements")
    ax.plot(x, model(fit.x), color="#156b8a", lw=1.6, label="Conditional two-hopping DOS fit")
    ax.set(ylabel="Normalized conductance", ylim=(-.03, 1.2),
           title="A good local-DOS fit does not identify a microscopic Hamiltonian")
    ax.legend(frameon=False)
    resid.plot(x, fit.fun, color="#156b8a", lw=.65)
    resid.axhline(0, color="black", lw=.5)
    resid.set(xlabel=r"Bias energy / $D$ relative to the high-T chemical potential",
              ylabel="Fit − data", xlim=(-10, 10))
    fig.text(.5, -.02,
             f"Conditional values: t₁/D = {fit.x[0]:.3f}, t₂/D = {fit.x[1]:.3f}. "
             "Self-energy, matrix-element and longer-range hopping ambiguities are excluded by assumption.",
             ha="center", fontsize=9)
    fig.tight_layout()
    savefig(fig, "conditional_band_fit")


def phase_constraints(results):
    fig, ax = plt.subplots(figsize=(10.4, 6.2))
    ax.set_facecolor("#f0f1f3")
    for nu, color in zip([.5, .3, .2], COLORS):
        ax.axvline(nu, color=color, lw=1, alpha=.7)
    for j, nu in [(1, .3), (2, .2)]:
        br = results["transition_brackets"][j - 1]
        low, high = br["last_zero_resistance_T_D"], br["first_nonzero_resistance_T_D"]
        # The finite bar widths are visibility only, not an inferred filling range.
        ax.plot([nu, nu], [.1, low], color=COLORS[j], lw=13, solid_capstyle="butt")
        ax.plot([nu, nu], [low, high], color="#ffcb69", lw=13, solid_capstyle="butt")
        ax.plot([nu, nu], [high, 4], color=COLORS[j], lw=5, alpha=.6)
        ax.plot([nu, nu], [0, .1], color=COLORS[j], lw=3, ls=":")
    ax.plot([.5, .5], [.45, 4], color=COLORS[0], lw=7, alpha=.7)
    ax.plot([.5, .5], [0, .45], color=COLORS[0], lw=2, ls=":")
    ax.annotate("Superconductor candidate\nzero resistance, low-T spectral gap",
                xy=(.2, .45), xytext=(.025, 1.45), fontsize=9,
                arrowprops={"arrowstyle": "-", "color": COLORS[2]})
    ax.annotate(r"$T_c\in[1.075,1.150]D$", xy=(.2, 1.1125), xytext=(.015, 2.05),
                fontsize=10, arrowprops={"arrowstyle": "-", "color": COLORS[2]})
    ax.annotate("Metallic temperature dependence\nof normal-state resistivity",
                xy=(.2, 3.15), xytext=(.015, 3.65), fontsize=9,
                arrowprops={"arrowstyle": "-", "color": COLORS[2]})
    ax.annotate(r"$T_c\in[0.325,0.400]D$", xy=(.3, .3625), xytext=(.34, .85),
                fontsize=10, arrowprops={"arrowstyle": "-", "color": COLORS[1]})
    ax.annotate("Activated normal-state transport\nSpin response suppressed on cooling",
                xy=(.3, 2), xytext=(.34, 2.6), fontsize=9,
                arrowprops={"arrowstyle": "-", "color": COLORS[1]})
    ax.annotate("Insulating temperature dependence\nSpin activation; low-T electron gap",
                xy=(.5, 3.3), xytext=(.58, 3.55), fontsize=9,
                arrowprops={"arrowstyle": "-", "color": COLORS[0]})
    ax.annotate("Insulating extrapolation\nNo resistivity points below 0.45D",
                xy=(.5, .18), xytext=(.61, .6), fontsize=9,
                arrowprops={"arrowstyle": "-", "color": COLORS[0]})
    ax.text(.76, 2.05, "Unmeasured fillings\nPhase boundaries undetermined",
            ha="center", color="#68717b", fontsize=12)
    ax.set(xlim=(0, 1), ylim=(0, 4.4), xlabel=r"Filling fraction $\nu$",
           ylabel=r"Temperature $T/D$", title="Experimental constraints on a phase diagram")
    ax.set_xticks([0, .2, .3, .5, 1])
    fig.text(.5, -.025,
             "Colored bars mark measured crystal fillings only. Gray does not denote a physical phase.\n"
             "Dotted segments extrapolate below measured transport temperatures; no phase boundaries are inferred between fillings.",
             ha="center", fontsize=9)
    fig.tight_layout()
    savefig(fig, "phase_constraints")


def path_grid(n=180):
    vertices = np.array([[0., 0.], [.5, 0.], [.5, .5], [0., 0.]])
    lengths = np.linalg.norm(np.diff(vertices, axis=0), axis=1)
    segments, coordinates = [], []
    start = 0.
    for j in range(3):
        f = np.linspace(0, 1, n, endpoint=False)
        segments.append(vertices[j] + f[:, None] * (vertices[j + 1] - vertices[j]))
        coordinates.append(start + f * lengths[j])
        start += lengths[j]
    return np.vstack(segments + [vertices[-1:]]), np.r_[*coordinates, start], np.r_[0, np.cumsum(lengths)]


def construct_local_spectrum(s, nu, w):
    """One explicitly arbitrary completion of the finite STS energy window.

    Smooth the trace and impose a central exact gap, as asserted in the prompt.
    Half the canonical spectral weight is assigned to the measured window.
    Unobserved positive/negative satellites then enforce n_sigma = nu and the
    unit spectral sum.  Both satellites lie entirely outside [-10,10].
    The choices of window weight, gap cutoff, and satellites are NOT fitted.
    """
    x = np.array(s["bias"])
    y = np.maximum(savgol_filter(s["dI_dV"], 11, 2), 0.)
    cutoff = {0.5: 3.7, 0.3: 2.4, 0.2: 1.25}[nu]
    y[np.abs(x) < cutoff] = 0.
    finite = np.interp(w, x, y, left=0., right=0.)
    finite /= np.trapezoid(finite, w)
    window_fraction = .5
    rho = window_fraction * finite
    nwindow = np.trapezoid(rho * (w < 0), w)
    pwindow = np.trapezoid(rho * (w > 0), w)
    remaining_minus, remaining_plus = nu - nwindow, 1 - nu - pwindow
    assert remaining_minus > 0 and remaining_plus > 0
    for center, weight in [(-15., remaining_minus), (15., remaining_plus)]:
        z = (w - center) / 1.
        bump = np.where(np.abs(z) < 1, (1 - z * z) ** 2, 0.)
        bump /= np.trapezoid(bump, w)
        rho += weight * bump
    rho_minus = rho * (w < 0) / nu
    rho_plus = rho * (w > 0) / (1 - nu)
    return rho, rho_minus, rho_plus, {
        "filling": nu, "chosen_window_weight": window_fraction,
        "chosen_gap_halfwidth_D": cutoff,
        "unobserved_negative_satellite_weight": float(remaining_minus),
        "unobserved_positive_satellite_weight": float(remaining_plus),
        "satellite_support_D": [[-16., -14.], [14., 16.]],
        "normalization": float(np.trapezoid(rho, w)),
        "occupation_per_spin": float(np.trapezoid(rho * (w < 0), w)),
    }


def spectral_ambiguity(results):
    """Positive, normalized spectral functions with indistinguishable local DOS.

    A_l(k,w) = [nu + l*h(k)] p_minus(w)
             + [1-nu-l*h(k)] p_plus(w).
    Each p has unit integral and lies wholly on one side of mu=0.
    h has zero BZ mean, so local spectra and filling are independent of l.
    """
    w = np.linspace(-18, 18, 2881)
    kp, path, ticks = path_grid()
    cp = np.cos(2 * np.pi * kp)
    hp = (cp[:, 0] + cp[:, 1]) / 2
    local = [construct_local_spectrum(s, nu, w)
             for s, nu in zip(DATA[0]["spectra"][:3], [.5, .3, .2])]
    results["illustrative_spectral_completions"] = [entry[3] for entry in local]
    fig, axes = plt.subplots(2, 3, figsize=(12.3, 7.8), sharex=True, sharey=True)
    selected = np.abs(w) <= 10
    for j, (nu, entry) in enumerate(zip([.5, .3, .2], local)):
        rho, pm, pp, _ = entry
        for row, mixing in enumerate([0., .75 * min(nu, 1 - nu)]):
            wm = nu + mixing * hp
            spectrum = pm[:, None] * wm + pp[:, None] * (1 - wm)
            mesh = axes[row, j].pcolormesh(path, w[selected], spectrum[selected] / np.max(rho[selected]),
                                   shading="auto", cmap="magma",
                                   norm=PowerNorm(.7, vmin=0., vmax=1.5),
                                   rasterized=True)
            axes[row, j].axhline(0, lw=.6, ls="--", color="white", alpha=.5)
            axes[row, j].set_xticks(ticks, [r"$\Gamma$", r"$X$", r"$M$", r"$\Gamma$"])
            for tick in ticks[1:-1]:
                axes[row, j].axvline(tick, color="white", lw=.5, alpha=.4)
            if row == 0:
                axes[row, j].set_title(LABELS[j])
    axes[0, 0].set_ylabel("Completion A\nEnergy / D")
    axes[1, 0].set_ylabel("Completion B\nEnergy / D")
    fig.suptitle("Different momentum intensities with the same local spectrum and filling", y=1.01)
    fig.text(.5, -.035,
             "Illustrations of non-uniqueness, not ARPES predictions. Constant photoemission matrix element assumed.\n"
             "The doped chemical potentials are set to the gap midpoint only for these examples; this is not measured.\n"
             "Unobserved spectral weight at |energy| = 14–16D enforces the sum rules; it is excluded from this display.",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0, .94, 1))
    cbax = fig.add_axes([.945, .22, .012, .54])
    fig.colorbar(mesh, cax=cbax, label=r"$A(\mathbf{k},\omega)/\max_\omega\rho_\nu(\omega)$")
    savefig(fig, "spectral_nonuniqueness")

    # Half-filling Kramers-Kronig integral at zero frequency. The exact central
    # gap makes this an ordinary integral, not a numerically singular one.
    rho, pm, pp, _ = local[0]
    invabs = np.divide(1., np.abs(w), out=np.zeros_like(w), where=w != 0)
    cm = float(np.trapezoid(pm * invabs, w))
    cplus = float(np.trapezoid(pp * invabs, w))
    gamma = (cm - cplus) / (cm + cplus)
    nfit = 1200
    k = (np.arange(nfit) + .5) / nfit - .5
    c = np.cos(2 * np.pi * k)
    h0 = (c[:, None] + c[None, :]) / 2
    product = c[:, None] * c[None, :]
    examples = []
    for target, beta in [(0.5, 0.2), (0.6, 0.), (0.8, 0.)]:
        hh = h0 + beta * product
        threshold = float(np.quantile(hh, 1 - target))
        alpha = -gamma / threshold
        # w_minus = (1+alpha*h)/2.
        assert np.min(1 + alpha * hh) > 0
        assert np.max(1 + alpha * hh) < 2
        examples.append({"target_fraction": target, "beta": beta, "alpha": float(alpha),
                         "h_threshold": threshold,
                         "min_removal_weight": float(np.min((1 + alpha * hh) / 2)),
                         "max_removal_weight": float(np.max((1 + alpha * hh) / 2))})
    validation = []
    for size in [400, 800, 1600]:
        kk = (np.arange(size) + .5) / size - .5
        cc = np.cos(2 * np.pi * kk)
        hh = (cc[:, None] + cc[None, :]) / 2
        prod = cc[:, None] * cc[None, :]
        fractions = []
        for example in examples:
            h = hh + example["beta"] * prod
            # Re G(k,0) = 1/2 (Cminus - Cplus)
            #             + alpha/2 * h * (Cminus + Cplus).
            greal = .5 * (cm - cplus) + .5 * example["alpha"] * h * (cm + cplus)
            fractions.append(float(np.mean(greal > 0)))
        validation.append({"grid": [size, size], "fractions_on_Gamma_side": fractions})
    # Direct spectral integration at a selection of momenta verifies the KK
    # expression, canonical normalization, and occupation average.
    inverse_w = np.divide(1., w, out=np.zeros_like(w), where=w != 0)
    numerical_errors = []
    for example in examples:
        hpath = hp + example["beta"] * cp[:, 0] * cp[:, 1]
        wm = .5 * (1 + example["alpha"] * hpath)
        spectral = pm[:, None] * wm + pp[:, None] * (1 - wm)
        direct = -np.trapezoid(spectral * inverse_w[:, None], w, axis=0)
        analytic = .5 * (cm - cplus) + .5 * example["alpha"] * hpath * (cm + cplus)
        numerical_errors.append(float(np.max(np.abs(direct - analytic))))
        assert np.max(np.abs(np.trapezoid(spectral, w, axis=0) - 1)) < 1e-12
    results["KK_counterexamples"] = {
        "C_minus_inverse_D": cm, "C_plus_inverse_D": cplus, "gamma": float(gamma),
        "examples": examples, "area_grid_check": validation,
        "max_direct_KK_error_inverse_D": numerical_errors,
        "frequency_grid": {"points": len(w), "range_D": [float(w.min()), float(w.max())],
                           "step_D": float(w[1] - w[0])},
        "meaning": "Constructive ambiguity, not an inferred Luttinger volume.",
    }
    fig, axes = plt.subplots(2, 3, figsize=(12.1, 8.2))
    size = 400
    kk = (np.arange(size) + .5) / size - .5
    cc = np.cos(2 * np.pi * kk)
    hh = (cc[:, None] + cc[None, :]) / 2
    prod = cc[:, None] * cc[None, :]
    for j, example in enumerate(examples):
        h = hh + example["beta"] * prod
        greal = .5 * (cm - cplus) + .5 * example["alpha"] * h * (cm + cplus)
        bound = float(np.max(np.abs(greal)))
        axes[0, j].pcolormesh(kk, kk, greal.T, cmap="RdBu_r", shading="auto",
                              norm=TwoSlopeNorm(vmin=-bound, vcenter=0, vmax=bound), rasterized=True)
        axes[0, j].contour(kk, kk, greal.T, levels=[0], colors="black", linewidths=1.5)
        axes[0, j].plot(0, 0, "ko", ms=3)
        axes[0, j].text(.02, .02, r"$\Gamma$", color="black")
        axes[0, j].set(aspect="equal", xlabel=r"$k_x/(2\pi/a)$", ylabel=r"$k_y/(2\pi/a)$",
                       title=f"Γ-side area = {validation[-1]['fractions_on_Gamma_side'][j]:.4f} BZ")
        hpath = hp + example["beta"] * cp[:, 0] * cp[:, 1]
        wm = .5 * (1 + example["alpha"] * hpath)
        spectrum = pm[:, None] * wm + pp[:, None] * (1 - wm)
        mesh = axes[1, j].pcolormesh(path, w[selected], spectrum[selected] / np.max(rho[selected]),
                                    shading="auto", cmap="magma",
                                    norm=PowerNorm(.7, vmin=0, vmax=2), rasterized=True)
        axes[1, j].set_xticks(ticks, [r"$\Gamma$", r"$X$", r"$M$", r"$\Gamma$"])
        axes[1, j].set_ylabel(r"$\omega/D$ relative to $\mu=0$")
        axes[1, j].axhline(0, color="white", lw=.6, ls="--", alpha=.5)
    fig.suptitle("Same half-filled local spectrum; different zero contours from Kramers–Kronig", y=1.015)
    fig.text(.5, -.03,
             "Black curves: Re G(k,0) = 0; Im G(k,0) = 0 throughout the gap. Red: positive Re G.\n"
             "All examples have ν = 1/2, positive spectra, unit spectral sums, C₄ symmetry, and identical momentum averages.",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0, .94, 1))
    cbax = fig.add_axes([.946, .115, .012, .30])
    fig.colorbar(mesh, cax=cbax, label=r"$A(\mathbf{k},\omega)/\max_\omega\rho(\omega)$")
    savefig(fig, "zero_contour_nonuniqueness")


def main():
    results = {
        "source": "measurements.json",
        "energy_unit": "D",
        "important": "Statistical observable fits and deliberately arbitrary spectral counterexamples; no uniquely fitted Hamiltonian.",
        "uncertainty_convention": "Supplied errors used as independent 1-sigma marginal errors; normalization covariance not supplied.",
    }
    analyze_rates(results)
    sts_features(results)
    conditional_band_fit(results)
    phase_constraints(results)
    spectral_ambiguity(results)
    (ROOT / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    for group in ["NMR_activation", "resistivity_activation"]:
        for row in results[group]:
            a = row["constant_prefactor"]
            p = row["free_power_prefactor"]
            print(group, row["filling"],
                  f"E/D = {a['activation_energy_D']:.5f} +/- {a['activation_energy_1sigma_D']:.5f};",
                  f"free power: {p['activation_energy_D']:.5f} +/- {p['activation_energy_1sigma_D']:.5f}")
    print("Counterexample areas:", results["KK_counterexamples"]["area_grid_check"])
    print("Wrote figures and results.json in", ROOT)


if __name__ == "__main__":
    main()
