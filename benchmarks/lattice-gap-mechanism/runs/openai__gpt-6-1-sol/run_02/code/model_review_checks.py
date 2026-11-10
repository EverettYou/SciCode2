"""Small exact checks of conditional model hypotheses; not a microscopic fit.

Units: D=1, lattice constant=1, hbar=kB=1.
Only the input empirical spin and transport activation values are data-derived.
Illustrative U=12, t=1, tprime=.3 are explicitly not independently inferred here.
"""
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def dimer_analytic(U, t):
    s = np.sqrt(U*U + 16*t*t)
    return {"U": float(U), "t": float(t),
            "spin_gap": float((s-U)/2),
            "single_particle_half_gap": float((s-2*abs(t))/2),
            "E_N1": float(-abs(t)), "E_N2": float((U-s)/2),
            "E_N3": float(U-abs(t))}


def hop(state, src, dst):
    if not (state >> src) & 1 or (state >> dst) & 1:
        return None
    a = state ^ (1 << src)
    sign = (-1)**((state & ((1 << src)-1)).bit_count())
    sign *= (-1)**((a & ((1 << dst)-1)).bit_count())
    return a | (1 << dst), sign


def dimer_ed(U, t):
    # Orbitals: site0 up/down, site1 up/down. Exact full Fock space has 16 states.
    H = np.zeros((16,16))
    for s in range(16):
        H[s,s] = U*sum(((s >> (2*i))&1)*((s >> (2*i+1))&1) for i in range(2))
        for a,b in ((0,2),(2,0),(1,3),(3,1)):
            z = hop(s,a,b)
            if z:
                H[z[0],s] += -t*z[1]
    sectors = {}
    for n in (1,2,3):
        inds = [s for s in range(16) if s.bit_count()==n]
        sectors[n] = np.linalg.eigvalsh(H[np.ix_(inds,inds)])
    return {"spin_gap": float(sectors[2][1]-sectors[2][0]),
            "single_particle_half_gap": float((sectors[1][0]+sectors[3][0]-2*sectors[2][0])/2)}


def bkt_upper_bound(nu, t, tprime):
    # epsilon=-2t(cos kx+cos ky)-4tprime cos kx cos ky.
    # Ds <= (1/4N) sum n_ks epsilon_xx <= n(2|t|+4|tprime|)/4.
    # Tc <= pi Ds / 2 and n=2nu. Interactions must have no Peierls coupling.
    return float(np.pi*nu*(abs(t)+2*abs(tprime))/2)


def spectral_counterexample(grid_size=1200):
    """Causal normalized spectra with identical local DOS but different zeros.

    This is a logical counterexample, not a fit to the supplied STS data.
    A=.1 delta(w+4)+(.4+lam*f) delta(w+6)
      +.1 delta(w-4)+(.4-lam*f) delta(w-8).
    f=(cos kx+cos ky)/2. Gap midpoint and chemical potential are zero.
    """
    k = -np.pi + 2*np.pi*(np.arange(grid_size)+.5)/grid_size
    f = (np.cos(k)[:,None]+np.cos(k)[None,:])/2
    rows = []
    for lam in (.1,.2,.3):
        greal = 1/60 + 7*lam*f/24
        threshold = -2/(35*lam)
        rows.append({"lambda": lam, "f_on_zero_curve": threshold,
                     "gamma_side_BZ_fraction": float(np.mean(greal>0)),
                     "occupied_weight_per_spin": float(np.mean(.5+lam*f)),
                     "minimum_pole_weight": float(min(.1, np.min(.4-lam*np.abs(f))))})
    return {"status": "analytic counterexample; not fitted to data",
            "grid": [grid_size,grid_size], "poles_D": [-4,-6,4,8],
            "same_local_pole_weights_for_all_lambda": [.1,.4,.1,.4],
            "gap_edges_D": [-4,4], "chemical_potential_D": 0,
            "spectral_sum_each_k": 1, "rows": rows,
            "G_real_at_zero": "1/60+(7lambda/24)*(cos(kx)+cos(ky))/2",
            "scope": "Causal spectral nonuniqueness; a microscopic one-orbital realization and identical transport/spin vertices are not asserted."}


def main():
    J = 5.54
    illustrative = dimer_analytic(12,1)
    exact = dimer_ed(12,1)
    assert np.allclose([illustrative[k] for k in exact],list(exact.values()),atol=1e-12)
    tp = np.sqrt(J*(J+12))/2
    # Formal fit of isolated-dimer gap to the two empirical activation numbers.
    # Not a valid material inference: transport activation need not equal this gap.
    c = 3.72
    roots = np.roots([16,-8*J,-4*J*(2*c-J)])
    t_formal = float(max(roots))
    U_formal = 2*t_formal + 2*c - 2*J
    out = {
        "status": "conditional model checks, not fitted microscopic parameters",
        "dimer_hamiltonian": "-t sum_sigma(c0dag c1+h.c.) + U sum_i n_iup n_idown",
        "illustrative_dimer_U12_t1": illustrative,
        "exact_16_state_ED_check": exact,
        "required_rung_hopping_if_U12_and_spin_gap_5p54": dimer_analytic(12,tp),
        "formal_two_gap_dimer_solution_NOT_material_fit": dimer_analytic(U_formal,t_formal),
        "strict_2D_t1_tprime0p3_BKT_bound": {
            "nu0p2": bkt_upper_bound(.2,1,.3),
            "nu0p3": bkt_upper_bound(.3,1,.3),
            "observed_nu0p2_Tc_lower_bound": 1.075,
            "required_t_plus_2abs_tprime_nu0p2": float(2*1.075/(np.pi*.2)),
            "assumptions": ["one band, strict 2D, n=2nu", "hopping coefficients are bare and temperature-independent",
                            "interactions do not couple to vector potential (density interactions satisfy this)",
                            "zero resistance identifies a superconducting transition"],
            "caveats": ["high-temperature STS only fits an effective DOS, not necessarily bare hopping",
                        "additional bands, coupled layers, 3D coupling, or pair/correlated hopping can change the bound"],
            "source": "https://doi.org/10.1103/PhysRevX.9.031049"
        },
        "spectral_nonidentifiability_counterexample": spectral_counterexample()
    }
    (ROOT/'data'/'model_review_checks.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2))


if __name__ == '__main__':
    main()
