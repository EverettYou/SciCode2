"""Neural-quantum-state VMC engine for the bilayer t1-t2-J model (NetKet backend).

Ansatz (real, "neural Jastrow x geminal"):
    psi(n) = det[ Phi(x_a, y_b) | U(x_a, k) ]  *  exp( J2(n) + RBM(n) )
  * x_a: occupied up modes, y_b: occupied down modes (orbital index = layer*Nc+site)
  * Phi(o,o') pairing function, translation invariant with the twisted-boundary
    sign structure: Phi = F[l,l',dx mod Lx, dy mod Ly] * s(dx,dy)
  * U: unpaired orbitals when N_up != N_down (or odd N)
  * J2: two-body (density-density) Jastrow, translation invariant
  * RBM: translation-symmetric RBM (hidden units replicated over translations)
Sampler: Metropolis with (i) intralayer same-spin hops, (ii) interlayer
spin exchange (S+_1 S-_2 type), conserving N1, N2, N_up, N_down.
Optimizer: stochastic reconfiguration (NetKet VMC_SR).
"""
from __future__ import annotations

import os
import numpy as np

import jax
import jax.numpy as jnp
import flax.linen as nn
import netket as nk
from netket.utils import struct
from netket.sampler.rules.base import MetropolisRule

from model import (Lattice, hamiltonian_terms, dispersion, hopping_matrix_single_layer,
                   spin_corr_terms, interlayer_pair_terms, hop_terms, density_corr_terms)

jax.config.update("jax_enable_x64", True)


# ---------------------------------------------------------------------------
# Hilbert space and Hamiltonian
# ---------------------------------------------------------------------------
def make_hilbert(lat: Lattice, Nup: int, Ndn: int):
    return nk.hilbert.SpinOrbitalFermions(lat.n_orb, s=1 / 2, n_fermions_per_spin=(Ndn, Nup))


def terms_to_operator(hi, terms, jax_op=True):
    ops = [list(t[1]) for t in terms]
    ws = [float(t[0]) for t in terms]
    op = nk.operator.FermionOperator2nd(hi, ops, ws)
    if jax_op:
        op = nk.experimental.operator.ParticleNumberAndSpinConservingFermioperator2nd.from_fermionoperator2nd(op)
    return op


def make_hamiltonian(hi, lat: Lattice, J: float, t1=1.0, t2=0.2):
    return terms_to_operator(hi, hamiltonian_terms(lat, J, t1, t2))


# ---------------------------------------------------------------------------
# Translation tables
# ---------------------------------------------------------------------------
def translation_tables(lat: Lattice):
    """Returns
    pair_idx[o,o']  : index into F[(l,l'), dx, dy] flattened
    pair_sgn[o,o']  : +-1 twisted-boundary sign
    jas_idx[m,m']   : index into W[(flavor, flavor'), dx, dy]
    perm[r, m]      : mode m translated by lattice vector r (for the symmetric RBM)
    """
    Lx, Ly, nc, no = lat.Lx, lat.Ly, lat.n_cell, lat.n_orb
    nm = lat.n_modes
    sym = all(c != "o" for c in lat.bc)
    pos = lat.positions().astype(int)
    pair_idx = np.zeros((no, no), dtype=np.int64)
    pair_sgn = np.ones((no, no), dtype=np.float64)
    jas_idx = np.zeros((nm, nm), dtype=np.int64)
    for o in range(no):
        l, r = divmod(o, nc)
        for o2 in range(no):
            l2, r2 = divmod(o2, nc)
            dx = pos[r, 0] - pos[r2, 0]
            dy = pos[r, 1] - pos[r2, 1]
            s = 1.0
            if lat.bc[0] == "a" and dx < 0:
                s = -s
            if lat.bc[1] == "a" and dy < 0:
                s = -s
            if sym:
                pair_idx[o, o2] = ((l * 2 + l2) * Lx + dx % Lx) * Ly + dy % Ly
            else:
                pair_idx[o, o2] = o * no + o2
                s = 1.0
            pair_sgn[o, o2] = s
    for m in range(nm):
        s1, o = divmod(m, no)
        l, r = divmod(o, nc)
        f1 = s1 * 2 + l
        for m2 in range(nm):
            s2, o2 = divmod(m2, no)
            l2, r2 = divmod(o2, nc)
            f2 = s2 * 2 + l2
            dx = pos[r, 0] - pos[r2, 0]
            dy = pos[r, 1] - pos[r2, 1]
            if sym:
                jas_idx[m, m2] = ((f1 * 4 + f2) * Lx + dx % Lx) * Ly + dy % Ly
            else:
                jas_idx[m, m2] = m * nm + m2
    if sym:
        perm = np.zeros((nc, nm), dtype=np.int64)
        for rr in range(nc):
            tx, ty = pos[rr]
            for m in range(nm):
                s1, o = divmod(m, no)
                l, r = divmod(o, nc)
                x, y = pos[r]
                r2 = lat.site(x + tx, y + ty)
                perm[rr, m] = s1 * no + l * nc + r2
    else:
        perm = np.arange(nm)[None, :]
    n_pair = 4 * Lx * Ly if sym else no * no
    n_jas = 16 * Lx * Ly if sym else nm * nm
    return dict(pair_idx=pair_idx, pair_sgn=pair_sgn, jas_idx=jas_idx, perm=perm,
                n_pair=n_pair, n_jas=n_jas, sym=sym)


# ---------------------------------------------------------------------------
# Mean-field initial pairing functions
# ---------------------------------------------------------------------------
def fl_pairing_matrix(lat: Lattice, n_per_flavor: int, t1=1.0, t2=0.2):
    """Phi(o,o') = delta_{ll'} sum_{k occ} phi_k(r) phi_k(r')  (closed-shell projector).
    Degenerate shells: fills the lowest states of the single-layer hopping matrix."""
    h = hopping_matrix_single_layer(lat, t1, t2)
    w, v = np.linalg.eigh(h)
    P = v[:, :n_per_flavor] @ v[:, :n_per_flavor].T  # Nc x Nc
    no, nc = lat.n_orb, lat.n_cell
    Phi = np.zeros((no, no))
    for l in (0, 1):
        Phi[l * nc:(l + 1) * nc, l * nc:(l + 1) * nc] = P
    return Phi, w


def singlet_pairing_matrix(lat: Lattice):
    """Rung-singlet product: Phi((l,r),(l',r)) = delta_{rr'} (1 - delta_{ll'})."""
    no, nc = lat.n_orb, lat.n_cell
    Phi = np.zeros((no, no))
    for r in range(nc):
        Phi[r, nc + r] = 1.0
        Phi[nc + r, r] = 1.0
    return Phi


def bcs_pairing_matrix(lat: Lattice, n_per_flavor: int, Delta: float, t1=1.0, t2=0.2, mu=None):
    """Interlayer s-wave BCS: Phi_k = v_k/u_k for pairs (k,l,up)(-k,l',dn), l != l'.
    Phi(o,o') = (1-delta_ll') sum_k phi_k phi_k(r) phi_k(r')^* with phi_k = Delta/(xi_k + E_k)."""
    h = hopping_matrix_single_layer(lat, t1, t2)
    w, v = np.linalg.eigh(h)
    if mu is None:
        mu = 0.5 * (w[n_per_flavor - 1] + w[n_per_flavor]) if n_per_flavor < len(w) else w[-1] + 1
    xi = w - mu
    E = np.sqrt(xi ** 2 + Delta ** 2)
    g = Delta / (xi + E)
    P = (v * g[None, :]) @ v.T
    no, nc = lat.n_orb, lat.n_cell
    Phi = np.zeros((no, no))
    Phi[0:nc, nc:2 * nc] = P
    Phi[nc:2 * nc, 0:nc] = P
    return Phi


def pairing_matrix_to_params(lat: Lattice, Phi: np.ndarray, tabs) -> np.ndarray:
    """Project a full pairing matrix onto the translation-invariant parameter vector
    (least squares over equivalent entries; exact if Phi has the symmetry)."""
    idx, sgn = tabs["pair_idx"], tabs["pair_sgn"]
    n = tabs["n_pair"]
    num = np.zeros(n)
    cnt = np.zeros(n)
    np.add.at(num, idx.ravel(), (Phi * sgn).ravel())
    np.add.at(cnt, idx.ravel(), 1.0)
    return num / np.maximum(cnt, 1)


def unpaired_orbitals_init(lat: Lattice, n_per_flavor: int, m: int, t1=1.0, t2=0.2):
    """Lowest unoccupied single-particle orbitals (layer symmetric combos) for the
    extra up electrons: columns of size n_orb."""
    h = hopping_matrix_single_layer(lat, t1, t2)
    w, v = np.linalg.eigh(h)
    no, nc = lat.n_orb, lat.n_cell
    U = np.zeros((no, m))
    if m == 2:
        # Fermi-liquid triplet: particle in the lowest empty orbital, the partner in the top occupied one, same layer
        U[0:nc, 0] = v[:, max(n_per_flavor - 1, 0)]
        U[0:nc, 1] = v[:, min(n_per_flavor, nc - 1)]
        return U
    for k in range(m):
        orb = v[:, min(n_per_flavor + k // 2, nc - 1)]
        layer = k % 2
        U[layer * nc:(layer + 1) * nc, k] = orb
    return U


# ---------------------------------------------------------------------------
# The model
# ---------------------------------------------------------------------------
class GeminalNQS(nn.Module):
    n_modes: int
    n_orb: int
    n_cell: int
    Nup: int
    Ndn: int
    pair_idx: tuple  # stored as static numpy via tuple wrapper
    pair_sgn: tuple
    jas_idx: tuple
    perm: tuple
    n_pair: int
    n_jas: int
    n_hidden: int = 8
    use_rbm: bool = True
    use_jastrow2: bool = True
    pair_init: tuple = ()
    unpaired_init: tuple = ()
    triplet: bool = False          # Sz=1 sector: up-up pairing block (Pfaffian via block identity)
    q_mod: tuple = (0.0, 0.0)      # modulation momentum of the up-up pair (units of 1, i.e. radians)
    site_xy: tuple = ()            # positions of orbitals (n_orb, 2) for the modulation
    triplet_init: tuple = ()

    def setup(self):
        self._pair_idx = jnp.asarray(np.array(self.pair_idx))
        self._pair_sgn = jnp.asarray(np.array(self.pair_sgn))
        self._jas_idx = jnp.asarray(np.array(self.jas_idx))
        self._perm = jnp.asarray(np.array(self.perm))
        pinit = np.array(self.pair_init) if len(self.pair_init) else None
        if pinit is not None:
            self.F = self.param("F", lambda key, shape: jnp.asarray(pinit), (self.n_pair,))
        else:
            self.F = self.param("F", nn.initializers.normal(0.1), (self.n_pair,))
        m = abs(self.Nup - self.Ndn)
        if m > 0:
            uinit = np.array(self.unpaired_init) if len(self.unpaired_init) else None
            if self.triplet and m == 2:
                # Q is an arbitrary completion (not variational); the up-up pairing is
                # T = U0 ^ U1 (two variational orbitals, Fermi-liquid-like triplet) + antisym[cos(q.r) G] (triplon)
                rng = np.random.default_rng(12345)
                self.Qfix = jnp.asarray(rng.normal(size=(self.n_orb, 2)))
                if uinit is not None:
                    self.U = self.param("U", lambda key, shape: jnp.asarray(uinit), (self.n_orb, 2))
                else:
                    self.U = self.param("U", nn.initializers.normal(0.3), (self.n_orb, 2))
                ginit = np.array(self.triplet_init) if len(self.triplet_init) else None
                if ginit is not None:
                    self.G = self.param("G", lambda key, shape: jnp.asarray(ginit), (self.n_pair,))
                else:
                    self.G = self.param("G", nn.initializers.normal(0.1), (self.n_pair,))
                xy = np.array(self.site_xy, dtype=float)
                self._cosq = jnp.asarray(np.cos(self.q_mod[0] * xy[:, 0] + self.q_mod[1] * xy[:, 1]))
            elif uinit is not None:
                self.U = self.param("U", lambda key, shape: jnp.asarray(uinit), (self.n_orb, m))
            else:
                self.U = self.param("U", nn.initializers.normal(0.3), (self.n_orb, m))
        if self.use_jastrow2:
            self.W2 = self.param("W2", nn.initializers.zeros, (self.n_jas,))
        if self.use_rbm:
            self.Wr = self.param("Wr", nn.initializers.normal(0.01), (self.n_hidden, self.n_modes))
            self.br = self.param("br", nn.initializers.zeros, (self.n_hidden,))

    def __call__(self, n):
        if not jnp.issubdtype(n.dtype, jnp.integer):
            n = jnp.isclose(n, 1).astype(jnp.int32)
        Phi = self.F[self._pair_idx] * self._pair_sgn  # (n_orb, n_orb)
        no = self.n_orb
        Nup, Ndn = self.Nup, self.Ndn
        Nbig, Nsmall = max(Nup, Ndn), min(Nup, Ndn)
        m = Nbig - Nsmall
        if self.use_jastrow2:
            Wfull = self.W2[self._jas_idx]
            Wfull = 0.5 * (Wfull + Wfull.T)
        use_trip = self.triplet and m == 2
        if use_trip:
            Tm = self.G[self._pair_idx] * self._pair_sgn
            Tm = Tm * self._cosq[:, None]
            Tfull = Tm - Tm.T + (jnp.outer(self.U[:, 0], self.U[:, 1]) - jnp.outer(self.U[:, 1], self.U[:, 0]))

        def single(nv):
            nd = nv[:no]
            nu = nv[no:]
            xu = jnp.nonzero(nu, size=Nup, fill_value=0)[0]
            xd = jnp.nonzero(nd, size=Ndn, fill_value=0)[0]
            Ucomp = self.Qfix if use_trip else (self.U if m > 0 else None)
            if Nup >= Ndn:
                A = Phi[xu][:, xd]  # (Nup, Ndn)
                if m > 0:
                    A = jnp.concatenate([A, Ucomp[xu]], axis=1)
            else:
                A = Phi[xu][:, xd].T  # (Ndn, Nup)
                if m > 0:
                    A = jnp.concatenate([A, Ucomp[xd]], axis=1)
            if Nbig > 0:
                sign, logabs = jnp.linalg.slogdet(A)
                logdet = logabs + jnp.log(sign.astype(jnp.complex128))
                if use_trip:
                    xb = xu if Nup >= Ndn else xd
                    Minv = jnp.linalg.inv(A)
                    r1, r2 = Minv[-2], Minv[-1]
                    corr = r1 @ (Tfull[xb][:, xb] @ r2)
                    logdet = logdet + jnp.log(corr.astype(jnp.complex128))
            else:
                logdet = jnp.array(0.0 + 0.0j)
            nf = nv.astype(jnp.float64)
            out = logdet
            if self.use_jastrow2:
                out = out + 0.5 * nf @ (Wfull @ nf)
            if self.use_rbm:
                nT = nf[self._perm]  # (n_trans, n_modes)
                theta = nT @ self.Wr.T + self.br[None, :]
                # numerically stable log cosh (no overflow for large |theta|)
                at = jnp.abs(theta)
                out = out + jnp.sum(at + jnp.log1p(jnp.exp(-2.0 * at)) - jnp.log(2.0))
            return out

        return jax.vmap(single)(n.reshape(-1, n.shape[-1])).reshape(n.shape[:-1])


# ---------------------------------------------------------------------------
# Sampler rule
# ---------------------------------------------------------------------------
class BilayerRule(MetropolisRule):
    """Intralayer same-spin hops (any distance within the layer, cluster list)
    + interlayer spin exchange. Conserves N1, N2, N_up, N_down."""

    clusters: jax.Array = struct.field(pytree_node=False)
    n_cell: int = struct.field(pytree_node=False)
    n_orb: int = struct.field(pytree_node=False)
    N1: int = struct.field(pytree_node=False)
    N2: int = struct.field(pytree_node=False)
    Nup: int = struct.field(pytree_node=False)
    Ndn: int = struct.field(pytree_node=False)
    p_exchange: float = struct.field(pytree_node=False)

    def __init__(self, lat: Lattice, N1, N2, Nup, Ndn, p_exchange=0.3, max_dist=None):
        nc, no = lat.n_cell, lat.n_orb
        pos = lat.positions()
        cl = []
        for l in (0, 1):
            for i in range(nc):
                for j in range(i + 1, nc):
                    if max_dist is not None:
                        d = pos[i] - pos[j]
                        d = np.minimum(np.abs(d), np.array([lat.Lx, lat.Ly]) - np.abs(d))
                        if np.hypot(*d) > max_dist + 1e-9:
                            continue
                    for s in (0, 1):
                        cl.append((s * no + l * nc + i, s * no + l * nc + j))
        self.clusters = jnp.asarray(np.array(cl, dtype=np.int64))
        self.n_cell, self.n_orb = nc, no
        self.N1, self.N2, self.Nup, self.Ndn = N1, N2, Nup, Ndn
        self.p_exchange = p_exchange

    def random_state(self, sampler, machine, params, sampler_state, key):
        n_chains = sampler.n_batches
        nc, no = self.n_cell, self.n_orb
        N1, N2, Nup, Ndn = self.N1, self.N2, self.Nup, self.Ndn
        lo = max(0, N1 - nc, Nup - nc, Nup - N2)
        hi = min(nc, N1, Nup, Nup - N2 + nc)
        keys = jax.random.split(key, n_chains)

        def one(k):
            k1, k2 = jax.random.split(k)
            n1u = jax.random.randint(k1, (), lo, hi + 1)
            n1d = N1 - n1u
            n2u = Nup - n1u
            n2d = N2 - n2u
            ks = jax.random.split(k2, 4)
            sigma = jnp.zeros((no * 2,), dtype=sampler.dtype)
            # flavor blocks: (spin block, layer) -> offset
            for (kk, nfl, off) in ((ks[0], n1u, no + 0), (ks[1], n1d, 0),
                                   (ks[2], n2u, no + nc), (ks[3], n2d, nc)):
                rank = jax.random.uniform(kk, (nc,))
                order = jnp.argsort(jnp.argsort(rank))
                occ = (order < nfl).astype(sampler.dtype)
                sigma = jax.lax.dynamic_update_slice(sigma, occ, (off,))
            return sigma

        return jax.vmap(one)(keys)

    def transition(self, sampler, machine, parameters, state, key, σ):
        n_chains = σ.shape[0]
        keys = jax.random.split(key, n_chains)
        clusters = self.clusters
        nc, no = self.n_cell, self.n_orb
        p_ex = self.p_exchange

        def one(k, s):
            k0, k1, k2, k3 = jax.random.split(k, 4)
            # --- hop move ---
            mask = (s[clusters[:, 0]] != s[clusters[:, 1]]).astype(jnp.float64)
            c = jax.random.choice(k1, clusters.shape[0], p=mask / mask.sum())
            si, sj = clusters[c, 0], clusters[c, 1]
            sh = s.at[si].set(s[sj]).at[sj].set(s[si])
            mask2 = (sh[clusters[:, 0]] != sh[clusters[:, 1]]).astype(jnp.float64)
            corr_hop = jnp.log(mask.sum()) - jnp.log(mask2.sum())
            # --- interlayer spin exchange ---
            i = jax.random.randint(k2, (), 0, nc)
            j = jax.random.randint(k3, (), 0, nc)
            a, b = no + i, i              # layer 0 up, layer 0 down
            c_, d = no + nc + j, nc + j   # layer 1 up, layer 1 down
            condA = (s[a] == 1) & (s[b] == 0) & (s[d] == 1) & (s[c_] == 0)
            condB = (s[b] == 1) & (s[a] == 0) & (s[c_] == 1) & (s[d] == 0)
            sA = s.at[a].set(0).at[b].set(1).at[d].set(0).at[c_].set(1)
            sB = s.at[b].set(0).at[a].set(1).at[c_].set(0).at[d].set(1)
            se = jnp.where(condA, sA, jnp.where(condB, sB, s))
            u = jax.random.uniform(k0)
            do_ex = u < p_ex
            s_new = jnp.where(do_ex, se, sh)
            corr = jnp.where(do_ex, 0.0, corr_hop)
            return s_new, corr

        return jax.vmap(one)(keys, σ)


# ---------------------------------------------------------------------------
# Observables (translation-averaged correlators)
# ---------------------------------------------------------------------------
def shift_sign(lat: Lattice, r: int, dx: int, dy: int):
    """Site r+Delta (wrapped) and the magnetic-translation sign for c+_{r+D} c_r."""
    x, y = lat.xy(r)
    s = 1.0
    X, Y = x + dx, y + dy
    if X >= lat.Lx or X < 0:
        if lat.bc[0] == "a":
            s = -s
    if Y >= lat.Ly or Y < 0:
        if lat.bc[1] == "a":
            s = -s
    return lat.site(X, Y), s


def build_observables(hi, lat: Lattice, which=("spin", "nk", "pair", "local")):
    """Dict name -> operator; translation-averaged correlators per displacement."""
    nc = lat.n_cell
    obs = {}
    disp = [(dx, dy) for dx in range(lat.Lx) for dy in range(lat.Ly)]
    if "spin" in which or "spin_lite" in which:
        combos = ((0, 0, "s11"), (1, 1, "s22"), (0, 1, "s12")) if "spin" in which else ((0, 0, "s11"), (0, 1, "s12"))
        for (l1, l2, tag) in combos:
            for (dx, dy) in disp:
                terms = []
                for r in range(nc):
                    r2, _ = shift_sign(lat, r, dx, dy)
                    terms += [(c / nc, o) for (c, o) in spin_corr_terms(lat, l1, r, l2, r2)]
                obs[f"{tag}_{dx}_{dy}"] = terms_to_operator(hi, terms)
    if "nk" in which or "nk_lite" in which:
        combos = ((0, 1, "g1u"), (0, 0, "g1d"), (1, 1, "g2u"), (1, 0, "g2d")) if "nk" in which else ((0, 1, "g1u"),)
        for (l, s, tag) in combos:
            for (dx, dy) in disp:
                terms = []
                for r in range(nc):
                    r2, sg = shift_sign(lat, r, dx, dy)
                    terms += [(c * sg / nc, o) for (c, o) in hop_terms(lat, l, s, r2, r)]
                obs[f"{tag}_{dx}_{dy}"] = terms_to_operator(hi, terms)
    if "pair" in which:
        for (dx, dy) in disp:
            terms = []
            for r in range(nc):
                r2, _ = shift_sign(lat, r, dx, dy)
                terms += [(c / nc, o) for (c, o) in interlayer_pair_terms(lat, r2, r)]
            obs[f"pair_{dx}_{dy}"] = terms_to_operator(hi, terms)
    if "dens" in which:
        # density-density correlators, translation averaged: <n_{r,l} n_{r+D,l'}> for (11),(12)
        for (l1, l2, tag) in ((0, 0, "d11"), (0, 1, "d12")):
            for (dx, dy) in disp:
                terms = []
                for r in range(nc):
                    r2, _ = shift_sign(lat, r, dx, dy)
                    terms += [(c / nc, o) for (c, o) in density_corr_terms(lat, l1, r2, l2, r)]
                obs[f"{tag}_{dx}_{dy}"] = terms_to_operator(hi, terms)
    if "local" in which:
        # double occupancy per layer, interlayer density correlation
        for l in (0, 1):
            terms = []
            for r in range(nc):
                u, d = lat.mode(l, r, 1), lat.mode(l, r, 0)
                terms.append((1.0 / nc, ((u, 1), (u, 0), (d, 1), (d, 0))))
            obs[f"docc{l+1}"] = terms_to_operator(hi, terms)
        terms = []
        for r in range(nc):
            terms += [(c / nc, o) for (c, o) in density_corr_terms(lat, 0, r, 1, r)]
        obs["n1n2"] = terms_to_operator(hi, terms)
    return obs


def fourier_disp(lat: Lattice, vals: dict, tag: str, ks=None):
    """Sum_Delta e^{-i k.Delta} C(Delta) for all k (twisted set)."""
    if ks is None:
        ks = lat.kpoints()
    out = np.zeros(len(ks), dtype=complex)
    err = np.zeros(len(ks))
    for (dx, dy) in [(dx, dy) for dx in range(lat.Lx) for dy in range(lat.Ly)]:
        m, e = vals[f"{tag}_{dx}_{dy}"]
        phase = np.exp(-1j * (ks[:, 0] * dx + ks[:, 1] * dy))
        out += phase * m
        err += (np.abs(phase) * e) ** 2
    return out, np.sqrt(err)
