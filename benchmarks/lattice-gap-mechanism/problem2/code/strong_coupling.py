"""Strong-coupling (J >> t) quasiparticle theory of the rung-singlet phase,
with effective amplitudes extracted from exact diagonalization of two rungs
and validated on a four-rung ring.

Excitations of the rung-singlet product at half filling (one electron per layer per site):
  * triplon : one rung in the S=1 state, costs J, disperses at O(t^2/J)
  * holon   : one rung with a single electron (N-1), costs 3J/4, disperses at O(t)
  * trion   : one rung with three electrons (N+1), costs 3J/4, disperses at O(t)
Bond additivity: at the orders kept (first order in t for the charge quasiparticles,
second order t^2/J for the triplon and for diagonal shifts) every process lives on a
single bond, so the lattice dispersion is a sum over bond directions of two-rung
amplitudes.  E(k) = e0 + sum_delta 2 a_delta cos(k.delta) for the holon/trion, and
w(q) = w0 + sum_delta 2 b_delta cos(q.delta) for the triplon, with delta over the
NN (t1) and NNN (t2) bond vectors.
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import Lattice, hamiltonian_terms
from ed import Sector, build_operator, ground_state


class TwoRung(Lattice):
    """Two rungs connected by a single intralayer bond of hopping t (both layers)."""

    def __init__(self, t):
        self.Lx, self.Ly, self.bc = 2, 1, "oo"
        self.n_cell = 2
        self.n_orb = 4
        self.n_modes = 8
        self.nn_bonds = [(0, 1, 1.0)]
        self.nnn_bonds = []
        self.t = t


def two_rung_levels(J, t, N, Nup, Ndn, n_levels=4):
    lat = TwoRung(t)
    terms = hamiltonian_terms(lat, J, t1=t, t2=0.0)
    # all (N1,N2) splits
    out = []
    for N1 in range(0, 5):
        N2 = N - N1
        if N2 < 0 or N2 > 4:
            continue
        sec = Sector(lat, N1, N2, Nup, Ndn)
        if sec.dim == 0:
            continue
        H = build_operator(sec, sec, terms).toarray()
        w = np.linalg.eigvalsh(H)
        out.append((N1, N2, w[:n_levels]))
    return out


def two_rung_amplitudes(J, t):
    """Return the effective parameters per bond:
    e_gs2: two-rung ground energy (singlet-singlet + second-order shift)
    triplon: (onsite shift per bond, hopping per bond)
    holon:   (onsite shift per bond, hopping per bond)  [N-1 sector, N1+N2=3]
    trion:   (onsite shift per bond, hopping per bond)  [N+1 sector, N1+N2=5]
    """
    lat = TwoRung(t)
    terms = hamiltonian_terms(lat, J, t1=t, t2=0.0)

    def lowest(N1, N2, Nup, Ndn, k=2):
        sec = Sector(lat, N1, N2, Nup, Ndn)
        H = build_operator(sec, sec, terms).toarray()
        return np.sort(np.linalg.eigvalsh(H))[:k]

    e_gs2 = lowest(2, 2, 2, 2, 1)[0]
    # triplon: S=1 sector, two levels (bonding/antibonding) from the two rung positions
    w_t = lowest(2, 2, 3, 1, 2)
    trip_center = 0.5 * (w_t[0] + w_t[1]) - e_gs2
    trip_hop = 0.5 * (w_t[1] - w_t[0])  # |hopping|; sign fixed below by parity analysis
    # holon: N=3 total, Sz=1/2, sector (N1,N2)=(2,1): the hole lives in layer 2, on rung 1 or 2
    w_h = lowest(2, 1, 2, 1, 2)
    hol_center = 0.5 * (w_h[0] + w_h[1]) - e_gs2
    hol_hop = 0.5 * (w_h[1] - w_h[0])
    w_e = lowest(3, 2, 3, 2, 2)
    tri_center = 0.5 * (w_e[0] + w_e[1]) - e_gs2
    tri_hop = 0.5 * (w_e[1] - w_e[0])
    return dict(e_gs2=e_gs2, trip=(trip_center, trip_hop), hol=(hol_center, hol_hop), tri=(tri_center, tri_hop),
                e_ss=-1.5 * J)


def signed_amplitudes(J, t):
    """Determine the sign of each hopping amplitude by looking at the parity of the
    lower level under rung exchange (symmetric combination lower => negative hopping)."""
    lat = TwoRung(t)
    terms = hamiltonian_terms(lat, J, t1=t, t2=0.0)
    # exchange operator between rungs: swap site 0 <-> 1 in both layers and spins
    res = {}
    for name, (N1, N2, Nup, Ndn) in dict(trip=(2, 2, 3, 1), hol=(2, 1, 2, 1), tri=(3, 2, 3, 2)).items():
        secs = [(N1, N2)]
        # build the combined space of both (N1,N2) splits when they differ
        states, Hs = [], []
        for (a, b) in secs:
            sec = Sector(lat, a, b, Nup, Ndn)
            Hs.append(build_operator(sec, sec, terms).toarray())
            states.append(sec)
        if len(Hs) == 1:
            H = Hs[0]
            sec = states[0]
            st = sec.states
        else:
            from scipy.linalg import block_diag
            H = block_diag(*Hs)
            st = np.concatenate([s.states for s in states])
        w, v = np.linalg.eigh(H)
        # site-exchange permutation of modes: site 0 <-> 1 within each (layer,spin) block
        def swap_sites(x):
            y = np.zeros_like(x)
            for m in range(8):
                blk, s = divmod(m, 2)
                m2 = blk * 2 + (1 - s)
                y |= ((x >> np.uint64(m)) & np.uint64(1)) << np.uint64(m2)
            return y
        # fermionic sign of the permutation: compute by reordering; use the ED apply machinery
        from ed import apply_term
        # Represent the exchange as the product over blocks of the hop-exchange; easier: use the
        # one-body "exchange" via the overlap of eigenvectors with the swapped-basis vectors ignoring
        # signs is unsafe, so compute the sign exactly: swapping sites in every block is a product of
        # transpositions of modes (2b, 2b+1) for b in blocks; in the JW ordering each transposition of
        # adjacent modes with both occupied gives -1.
        signs = np.ones(len(st))
        for blk in range(4):
            both = ((st >> np.uint64(2 * blk)) & np.uint64(3)) == np.uint64(3)
            signs = np.where(both, -signs, signs)
        new = swap_sites(st)
        idx = np.searchsorted(st, new)
        P = np.zeros((len(st), len(st)))
        P[idx, np.arange(len(st))] = signs
        v0 = v[:, 0]
        par = float(v0 @ (P @ v0))
        res[name] = par
    return res


def lattice_dispersions(J, t1=1.0, t2=0.2, Lx=64, Ly=64, z1=4, z2=4):
    """Quasiparticle dispersions on the square lattice from bond additivity.
    z1, z2: number of NN / NNN bonds touching a site (4 and 4 on the square lattice)."""
    a1 = two_rung_amplitudes(J, t1)
    a2 = two_rung_amplitudes(J, t2)
    par1 = signed_amplitudes(J, t1)
    par2 = signed_amplitudes(J, t2)
    kx = 2 * np.pi * np.arange(Lx) / Lx
    ky = 2 * np.pi * np.arange(Ly) / Ly
    KX, KY = np.meshgrid(kx, ky, indexing="ij")
    out = {}
    for name in ("trip", "hol", "tri"):
        c1, h1 = a1[name]
        c2, h2 = a2[name]
        # sign: parity +1 (symmetric combination lowest) => hopping amplitude negative
        s1 = -1.0 if par1[name] > 0 else 1.0
        s2 = -1.0 if par2[name] > 0 else 1.0
        base = {"trip": J, "hol": 0.75 * J, "tri": 0.75 * J}[name]
        # on-site energy: base + per-bond shifts for every bond touching the site
        e0 = base + z1 * (c1 - base) + (z2 * (c2 - base) if t2 != 0 else 0.0)
        disp = e0 + 2 * s1 * h1 * (np.cos(KX) + np.cos(KY)) + 2 * s2 * h2 * (np.cos(KX + KY) + np.cos(KX - KY))
        out[name] = dict(e0=e0, hop1=s1 * h1, hop2=s2 * h2, disp=disp, kx=kx, ky=ky)
    out["e_gs_per_site"] = -0.75 * J + (z1 / 2) * (a1["e_gs2"] + 1.5 * J) + ((z2 / 2) * (a2["e_gs2"] + 1.5 * J) if t2 != 0 else 0.0)
    return out


def ring_check(J, t1=1.0, n_rungs=4):
    """Four-rung ring ED: compare lowest energies per momentum sector with the dispersions."""
    lat = Lattice(n_rungs, 1, "po")
    lat.nn_bonds = [(i, (i + 1) % n_rungs, 1.0) for i in range(n_rungs)]
    lat.nnn_bonds = []
    terms = hamiltonian_terms(lat, J, t1=t1, t2=0.0)
    nc = n_rungs
    res = {}
    for name, (N1, N2, Nup, Ndn) in dict(gs=(nc, nc, nc, nc), trip=(nc, nc, nc + 1, nc - 1),
                                        hol=(nc, nc - 1, nc, nc - 1), tri=(nc + 1, nc, nc + 1, nc)).items():
        sec = Sector(lat, N1, N2, Nup, Ndn)
        H = build_operator(sec, sec, terms)
        w, v = ground_state(H, k=min(6, sec.dim - 1))
        res[name] = w
    return res


if __name__ == "__main__":
    for J in (4.0, 8.0, 16.0):
        a = two_rung_amplitudes(J, 1.0)
        par = signed_amplitudes(J, 1.0)
        print(f"J={J}: per-bond (t=1): triplon center-J={a['trip'][0]-J:+.4f} hop={a['trip'][1]:.4f} par={par['trip']:+.2f} | "
              f"holon center-3J/4={a['hol'][0]-0.75*J:+.4f} hop={a['hol'][1]:.4f} par={par['hol']:+.2f} | "
              f"trion center-3J/4={a['tri'][0]-0.75*J:+.4f} hop={a['tri'][1]:.4f} par={par['tri']:+.2f} | gs shift={a['e_gs2']+1.5*J:+.4f}")
        print(f"      leading order: triplon hop ~ t^2/J = {1/J:.4f}; holon/trion hop ~ t/2 = 0.5; gs shift ~ -2t^2/(3J/2)= {-4/(3*J):.4f}")
    # ring check at J=8
    J = 8.0
    d = lattice_dispersions(J, 1.0, 0.0, Lx=4, Ly=1, z1=2, z2=0)
    r = ring_check(J)
    print("ring (4 rungs, t2=0) J=8:")
    print("  gs E/rung ED =", r["gs"][0] / 4, " theory =", d["e_gs_per_site"] + 0.0 * 0)
    for name in ("trip", "hol", "tri"):
        th = d[name]["e0"] + 2 * d[name]["hop1"] * np.cos(2 * np.pi * np.arange(4) / 4)
        if name == "trip":
            th = th  # triplon energies relative to the ground state
        else:
            th = th  # holon/trion energies relative to the ground state (E(N-+1) - E(N))
        print(f"  {name}: ED lowest levels - E_gs: {np.round(r[name][:4] - r['gs'][0], 4)}  theory band: {np.round(np.sort(th), 4)}")


# ---------------------------------------------------------------------------
# Doped carriers in the rung-singlet background: charge-2e rung pairs
# ---------------------------------------------------------------------------
def pair_boson_parameters(J, t):
    """Two-rung ED for (a) an empty rung next to a singlet rung (hole pair, N=2)
    and (b) a full rung next to a singlet rung (electron pair, N=6).
    Returns per-bond: pair hopping t_b, diagonal shift delta_se, and the effective
    nearest-neighbour pair-pair interaction V = delta_ss + delta_xx - 2 delta_se
    (delta_xx = 0 for two empty rungs; for two full rungs also 0)."""
    lat = TwoRung(t)
    terms = hamiltonian_terms(lat, J, t1=t, t2=0.0)

    def lowest(N1, N2, Nup, Ndn, k=2):
        sec = Sector(lat, N1, N2, Nup, Ndn)
        H = build_operator(sec, sec, terms).toarray()
        return np.sort(np.linalg.eigvalsh(H))[:k]

    e_ss = lowest(2, 2, 2, 2, 1)[0]
    d_ss = e_ss + 1.5 * J
    out = {}
    for name, (N1, N2, Nup, Ndn) in dict(hole=(1, 1, 1, 1), elec=(3, 3, 3, 3)).items():
        w = lowest(N1, N2, Nup, Ndn, 2)
        center = 0.5 * (w[0] + w[1])
        t_b = 0.5 * (w[1] - w[0])
        d_se = center + 0.75 * J
        V = d_ss - 2 * d_se
        out[name] = dict(t_b=t_b, d_se=d_se, V=V, levels=w)
    out["d_ss"] = d_ss
    return out


if __name__ == "__main__":
    print("\n--- rung-pair (charge 2e boson) parameters per NN bond (t=1) ---")
    for J in (3.0, 4.0, 6.0, 8.0, 12.0, 16.0):
        p = pair_boson_parameters(J, 1.0)
        h, e = p["hole"], p["elec"]
        print(f"J={J:5.1f}: hole pair: t_b={h['t_b']:.4f} d_se={h['d_se']:+.4f} V={h['V']:+.4f} V/t_b={h['V']/h['t_b']:+.3f} | "
              f"elec pair: t_b={e['t_b']:.4f} V={e['V']:+.4f} | leading t_b ~ 8t^2/(3J) = {8/(3*J):.4f}; d_ss={p['d_ss']:+.4f}")
