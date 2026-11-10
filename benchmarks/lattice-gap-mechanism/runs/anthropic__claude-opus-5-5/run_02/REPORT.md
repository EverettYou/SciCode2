# Low-temperature state at half filling of the layered oxide: analysis, effective theory, predictions

Energies and temperatures are in units of D (k_B = 1). Momenta are in units of 2π/a, where a is the in-plane metal–metal distance. All numbers come from `measurements.json` through the scripts in `code/`; see §7 for how to reproduce them.

---

## 0. Short answers

| Question | Answer |
|---|---|
| **Low-T state at ν = ½** | An insulating, spin-gapped liquid of **preformed local (on-site) singlet pairs** with **no long-range order**: no charge-density wave (CDW), no magnetism, no superconductivity in the measured range. Superconducting and charge-ordered correlations are nearly degenerate; that near-degeneracy is the approximate SO(4) symmetry of the attractive Hubbard model. The theory predicts that t′, which breaks this symmetry, eventually selects **s-wave superconductivity below T ≈ 0.08 D**, far below the measured range. |
| **Q1 Theory** | Single-band attractive (negative-U) Hubbard model on the square lattice, one site per unit cell: H = −t Σ_NN c†c − t′ Σ_NNN c†c + U Σ n↑n↓ − μN. **t = 1.00 ± 0.01**, **t′ = +0.197 ± 0.004** (van Hove energy 8t′ above the band centre), **U = −12.0 ± 0.5** at ν = ½. In the doped, metallic crystals the attraction is screened: U_eff ≈ −8 ± 1.5 at ν≈0.3 and −6.0 ± 0.2 at ν≈0.2. The model has translations, C4v, SU(2) spin, U(1) charge and time reversal. It lacks particle–hole symmetry and the η-pairing pseudospin SU(2) (the SO(4) of the nearest-neighbour model). |
| **Q2 Phases** (low T → high T) | **ν = ½**: s-wave superconductor (T < 0.08, predicted) → insulating pair liquid → normal metal above T* ≈ 5.5. **ν ≈ 0.3**: s-wave superconductor (T < 0.36) → pseudogap metal of preformed pairs (up to T* ≈ 2.3) → normal metal. **ν ≈ 0.2**: BCS s-wave superconductor (T < 1.1) → Fermi-liquid metal. |
| **Q4 ARPES** | **ν = ½**: two co-dispersing replica bands (−8…−4 and +4…+8), each with half the bare bandwidth; the direct gap is 12.0 at every k. **ν ≈ 0.3**: Bogoliubov bands; gap about 5 at Γ, X and M and about 3.5 at k_F, where the quasiparticles are strongly broadened. **ν ≈ 0.2**: sharp BCS back-bending at k_F ≈ 0.255 along Γ–X; isotropic Δ = 1.96. |
| **Q5 Zeros** | The zeros of Re G(k, 0) form a **small closed loop around Γ** enclosing **0.035 of the Brillouin zone** (68% interval 0.00–0.07). In the equal-weight limit the loop becomes the band-centre contour, enclosing 0.314. In every case this is **≠ ν = 0.5**: Luttinger's theorem in its "zeros" form fails. The failure is controlled by the particle–hole asymmetry (t′) together with μ being pinned at mid-gap. |

---

## 1. What the measurements say (model-independent analysis)

Fits of all four STS panels are in **`fig1_sts_fits.png`**; NMR and resistivity analyses are in **`fig2_nmr_resistivity.png`**. Full numbers are in `code/params.json`.

**Bare band (Fig. 1d, ν≈0.3, high T).** The tight-binding density of states ε_k = −2t(cos k_x + cos k_y) − 4t′ cos k_x cos k_y fits the panel with t = 1.014 ± 0.006 and t′ = 0.201 ± 0.003. The filling at the fitted chemical potential is **0.303**, which confirms ν ≈ 0.3. The occupied fraction of the in-window spectral weight is 0.30 (0.29–0.30 depending on background), so no spectral weight is missing at high T.

**Half filling (Fig. 1a).** The conductance vanishes between −3.99 and +4.01, a hard gap of 8.0.
- The two bands on either side are **exact copies of the bare band with half its bandwidth**: E±(k) = (ε_k − ε_centre)/2 ± Δ_r with Δ_r = 5.999 ± 0.003, so the copies are centred 12.00 apart. The fitted copy shape gives t = 0.999 ± 0.003 and t′ = 0.195 ± 0.002, independently of panel (d). The van Hove peaks sit at 70% of each copy (−5.2 and +6.8), as in the bare band.
- The two copies are **translated, not mirrored**. The lower band peaks near its inner edge, the upper band near its outer edge. This rules out Bogoliubov (superconducting) or CDW-folded spectra.
- The weights depend on k like a smooth momentum distribution: Z± = ½[1 ± ε_k/√(ε_k² + U_w²)] with U_w = 14.2 ± 0.6. The lower copy is stronger near Γ, the upper copy near M.
- Rejected forms: equal weights give χ² 2.7× worse; the full Hubbard-I dispersion gives χ² 6× worse.

**ν ≈ 0.2 (Fig. 1c).** BCS with a **k-independent** gap Δ = 1.959 ± 0.003 fits essentially within noise, with t = 1.003 and t′ = 0.201. The normal-state filling is 0.201. An extended-s gap Δ(cos k_x + cos k_y) is rejected (χ² 12× worse): the pairing is **on-site s-wave**. NMR shows a **Hebel–Slichter peak**: a BCS calculation using Δ from STS reproduces 1/(T₁T) with T_c = 1.18 ± 0.01 and Dynes broadening 0.045 (χ² = 11.9 for 41 points). The resistance vanishes between T = 1.075 and 1.15, so 2Δ/T_c ≈ 3.5, the BCS value. The normal state is metallic, ρ = 0.18(1 + T).

**ν ≈ 0.3 (Fig. 1b).** The spectrum is mirror-symmetric (Bogoliubov-like) with soft inner edges at ±2.6, peaks at ±5.1 and sharp outer edges at ±6.55. Plain BCS, anisotropic-gap BCS and two-pole forms all fail. The best description (χ² = 1.0×10⁻³) is a gap of 3.49 ± 0.04 on the underlying Fermi surface, rising to 5.06 ± 0.01 away from it, with Fermi-surface quasiparticles broadened by about 0.65. The other observations at this filling are:
- 1/(T₁T) drops below **T* = 2.3 ± 0.2** with Δ(0) = 2.42 ± 0.04, and shows no Hebel–Slichter peak.
- The resistivity turns up, ρ ∝ exp(0.90/T), then **vanishes at T_c = 0.36 ± 0.04**.
- 2Δ/T_c ≈ 13–19: strong coupling.

**ν = ½ transport and NMR.** The resistivity is Arrhenius from T = 4 down to 0.45 with **E_a = 3.72 ± 0.05**, about half the 8.0 optical gap. 1/(T₁T) is activated over four decades with **Δ_s = 5.54 ± 0.13** and is still rising at T = 4.4. The spin excitations are gapped on the scale of the charge gap, so **there are no free local moments**.

**Symmetry.**
- The in-plane period equals the metal–metal distance and all transition-metal sites are equivalent at every temperature: no CDW, no bond order, no dimerization.
- No peak splitting: C4 is preserved.
- A single NMR line: no static moments and no inequivalent sites.
- Spatially uniform STS: no stripes or inhomogeneity.
- One electron per primitive cell at ν = ½.

---

## 2. Q1 — Effective theory

### 2.1 Degrees of freedom, lattice, unit cell
- **Degrees of freedom:** spin-½ electrons in one Wannier orbital per transition-metal site (the antibonding transition-metal–O band). Each site has four states, |0⟩, |↑⟩, |↓⟩ and |↑↓⟩. Layers are treated as decoupled 2D planes.
- **Lattice:** square, lattice constant a (metal–metal distance), **one site per primitive unit cell**. The Brillouin zone is [−½, ½]².

### 2.2 Hamiltonian (every term)
```
H = − t  Σ_{<ij>,σ}  ( c†_{iσ} c_{jσ} + h.c. )        nearest-neighbour hopping
    − t′ Σ_{<<ij>>,σ}( c†_{iσ} c_{jσ} + h.c. )        next-nearest-neighbour (diagonal) hopping
    + U  Σ_i  n_{i↑} n_{i↓}                            on-site interaction, U < 0 (attractive)
    − μ  Σ_{iσ} n_{iσ}                                 chemical potential (fixed by ν; not a free coefficient)
```
The band is ε_k = −2t(cos k_x + cos k_y) − 4t′ cos k_x cos k_y, with bottom at Γ, van Hove points at X and top at M.

| Coefficient | Value | Determination |
|---|---|---|
| t | **1.00 ± 0.01** | Bare bandwidth 8t (Fig. 1d: 1.014 ± 0.006); half-width replicas at ν=½ (0.999 ± 0.003); BCS fit at ν≈0.2 (1.003 ± 0.003) |
| t′ | **+0.197 ± 0.004** | Van Hove position within the band (fits: 0.201, 0.195, 0.201); ε_X − ε_centre = 8t′ = 1.58 |
| U (ν = ½) | **−12.0 ± 0.5** | Replica splitting = \|U\| for a liquid of local pairs: 12.00 ± 0.01 (statistical) ± 0.2 (model); NMR activation \|U\|/2 − 2t′ = 5.54 ± 0.13 → \|U\| = 11.9 ± 0.3; 8/10-site ED of the half-filling gap → \|U\| ≈ 11.2 ± 0.4 (T = 0, finite size) |
| U_eff (doped crystals) | **−8 ± 1.5 (ν≈0.3); −6.0 ± 0.2 (ν≈0.2)** | BCS gap equation with Δ = 1.959 gives \|U_eff\| = 5.98; 8–10-site ED with \|U\| = 6 gives gap 1.7–1.9 (ν≈0.2), and \|U\| ≈ 8–9 gives about 2.7 (ν≈0.3). Phenomenologically \|U_eff\| ≈ 12 − 22\|ν − ½\| (screening of the local attraction by the doped carriers) |

Strong-coupling scales at ν = ½: pair hopping 2t²/|U| = 0.17, pseudospin exchange J = 4t²/|U| = 0.33, and J′ = 4t′²/|U| = 0.013.

### 2.3 Symmetries
- **Has:** lattice translations (one site per cell); point group C4v (D4h with the layering); inversion; time reversal; **SU(2) spin rotation** (no spin–orbit term); **U(1) charge**.
- **Lacks:**
  1. **Particle–hole symmetry.** Because t′ ≠ 0, ν and 1 − ν are related only after t′ → −t′.
  2. Consequently the **η-pairing pseudospin SU(2)**, i.e. the SO(4) = SU(2)×SU(2)/Z₂ of the nearest-neighbour model at half filling. That symmetry would make CDW and s-wave superconducting order exactly degenerate. With t′ the degeneracy is lifted weakly (relative anisotropy J′/J = (t′/t)² ≈ 0.04), in favour of superconductivity.
  3. Interlayer coupling (strictly 2D, so Mermin–Wagner applies) and any explicit symmetry-breaking field.

### 2.4 Why this theory (and not the alternatives)

| Candidate | Fatal conflict with the data |
|---|---|
| Repulsive Hubbard / Mott–Heisenberg insulator (U ≈ +12) | Local moments would give a large, nearly T-independent 1/T₁, not activation over four decades. Doping would give d-wave (nodal) pairing, not the hard, k-independent gap of Fig. 1c. Avoiding Néel order would need a spin liquid with a spin gap of 4–5 D ≫ J ≈ 0.3. A doped Mott insulator would put weight n/2 in an upper Hubbard band, giving an in-window occupied fraction 0.43 at ν≈0.3; 0.30 is measured. |
| CDW / bond-disproportionated insulator (BaBiO₃-like) | Excluded by diffraction (no superlattice), the single NMR line and uniform STS. |
| Band insulator | Impossible with one electron per primitive cell and no broken symmetry (Lieb–Schultz–Mattis / Oshikawa–Hastings). |
| **Attractive Hubbard (adopted)** | Explains the spin gap at ν=½ (spins bound in singlet pairs; pair-breaking energy per spin \|U\|/2 − 2t′ = 5.6 vs 5.54 measured). Explains the absence of CDW and magnetism and the replica spectrum (translated, half bandwidth, split by \|U\|). Gives on-site s-wave pairing with a constant gap and a Hebel–Slichter peak. Gives T_c → small at ν = ½ (near-SO(4)) rising with doping, a preformed-pair pseudogap at ν≈0.3, and BCS behaviour at ν≈0.2. The high-T occupied fraction is exactly ν when pair satellites (at ω ≈ −\|U\|) lie outside the window: (n/2)(1−n/2)/[(n/2)(1−n/2)+(1−n/2)²] = n/2. |

**Quantitative limitations, stated plainly:**
1. With a single U = −12, 8- and 10-site ED gives pair-breaking gaps 3.6–4.2 at all fillings (`fig3_ed_gaps.png`); the measured values are 1.96, 2.65 and 3.97. Reproducing the doped gaps needs the screened U_eff above, an ingredient beyond the minimal Hamiltonian.
2. In the clean model, pairs at ν = ½ would conduct (pair hopping 0.17). The measured Arrhenius law down to 0.45 requires pair transport to be incoherent or localized, for example by residual disorder pinning the nearly ordered pair correlations. This is a testable requirement (§8).
3. The high-T band in Fig. 1d is sharper than a static U = −12 would allow; the model predicts weak satellites near ω ≈ −12, outside the measured window.
4. The measured T_c's, especially 1.1 at ν≈0.2, exceed 2D phase-stiffness bounds for this band. Interlayer coupling (3D coherence) must be significant.

---

## 3. Q2 — Phase diagram (`fig4_phase_diagram.png`)

**Approximation (semi-quantitative).**
- **T*(ν), pair formation:** the BCS mean-field pairing temperature for U_eff(ν) on a 220×220 k-mesh, crossing over smoothly to the local-pair dissociation scale |U|/(2 ln 3) = 5.5 as |U_eff| → 1.5W.
- **T_c(ν) = min(T*, T_θ):** T_θ is the strong-coupling phase-coherence scale c·J_eff·4n_b(1−n_b)·[1 + (W/U_eff)⁶]·S(|ν−½|), with J_eff = 4t²/|U_eff| and n_b = ν pairs per site.
- **S(|ν − ½|):** the SO(4) suppression near half filling, set so that T_c(½) equals the strong-coupling KT temperature of the easy-plane pseudospin-½ XXZ antiferromagnet with anisotropy (t′/t)² ≈ 0.04, i.e. T_KT ≈ 0.24 J = 0.08.
- **Calibration:** two constants (c = 0.45, S(0) = 0.49) are set by T_c(0.3) and T_KT(½).
- **ν > ½:** obtained by the same equations with the true band (equivalent to the particle–hole map ν → 1−ν, t′ → −t′). The right-hand dome is slightly higher because the density of states is larger in the upper half of the t′ > 0 band.
- **Ends:** band insulators at ν = 0 and 1.

**Phases from low to high temperature:**
- **ν = ½:** s-wave superconductor (T < T_KT ≈ 0.08, predicted). Then an **insulating liquid of preformed local pairs** (0.08 < T < T* ≈ 5.5): spin gap ≈ 5.5, charge gap 8, no CDW, no magnetism, short-range superconducting and CDW correlations nearly degenerate; this is the measured low-T state. Above T* ≈ 5.5 the pairs dissociate into a normal metal (a crossover, not a phase transition).
- **ν ≈ 0.3:** s-wave superconductor (T < 0.36). Then a pseudogap metal of preformed pairs (0.36 < T < T* ≈ 2.3; spin gap, resistivity upturn). Then a normal metal.
- **ν ≈ 0.2:** BCS s-wave superconductor (T < 1.1; T* ≈ T_c). Then a normal Fermi-liquid metal.

Why there is no CDW at ν = ½ although the attraction is local: in the pair (pseudospin) language the model at ν = ½ is a nearly isotropic Heisenberg antiferromagnet. CDW and superconductivity are its two degenerate orientations; t′ adds a weak easy-plane term, J′(−ηˣηˣ − ηʸηʸ + ηᶻηᶻ) on diagonal bonds, that frustrates the checkerboard CDW and favours superconductivity. In 2D, thermal fluctuations of the near-SO(3) order parameter destroy long-range order down to T_KT. The Lieb–Schultz–Mattis constraint for charge-2e pairs at half filling (one pair per two sites) forbids a featureless T = 0 ground state; the theory satisfies it through the predicted superconductivity at T → 0.

---

## 4. Q3 — Which feature of the theory produces each data set

| Data | Feature of the theory |
|---|---|
| Diffraction: in-plane period = metal–metal distance, equivalent sites, no new peaks or splitting at any T | Local pairs do not crystallize. The CDW is frustrated by t′ and its near-degeneracy with superconductivity (approximate SO(4)) keeps the 2D pair liquid disordered. Pairs are spin singlets, so there is no magnetic order. Superconductivity breaks only U(1) gauge symmetry, invisible to diffraction. The s-wave state preserves C4. |
| STS (a), ν = ½ | Removing an electron from a pair or adding one to an empty site costs on average \|U\|/2 ∓ 2t′ (5.6 for removal, 6.4 for addition) relative to the mid-gap μ. An unpaired electron hops through the disordered pair/empty background with amplitude t/2, giving two **half-bandwidth replicas** of the bare band split by \|U\| = 12. The gap is \|U\| − W/2 = 8. Weights follow the smooth momentum distribution n_k (no Fermi surface). The spectrum is uniform because there is no charge order. |
| STS (b), ν ≈ 0.3 | Condensed preformed pairs in the strong-coupling crossover regime: a large pairing gap (≈ 5 away from k_F); Fermi-surface quasiparticles smeared by pair (phase) fluctuations give the soft edge at ≈ 2.6; Bogoliubov mirror symmetry. |
| STS (c), ν ≈ 0.2 | Weak-coupling BCS of the screened on-site attraction (U_eff = −6): k-independent gap 1.96, coherence peaks, weak v_k² shadow band. |
| STS (d), ν ≈ 0.3, T > T* | Pairs dissociated: the bare t–t′ band; occupied in-window fraction = ν, with pair satellites near −\|U\| outside the window. |
| Single NMR line | All sites equivalent (no CDW) and no static moments (singlet pairs). |
| 1/(T₁T), ν = ½ | Only thermally broken pairs carry spin. The measured activation (5.54 ± 0.13) is close to the local pair-breaking energy per unpaired electron, \|U\|/2 − 2t′ = 5.6 (atomic estimate, centre of weight of the lower replica), and larger than the band-edge value 4.0. At T comparable to the replica width, the thermally broken pairs sit mostly in the dense centre of the replica bands. |
| 1/(T₁T), ν ≈ 0.3 | Spin gap opens at pair formation, T* ≈ 2.3 ≫ T_c, so it carries straight through T_c with no Hebel–Slichter peak (the gap pre-exists and quasiparticles are incoherent); activation ≈ 2.4 ≈ pairing gap. |
| 1/(T₁T), ν ≈ 0.2 | BCS coherence factors (s-wave): Korringa above T_c, Hebel–Slichter peak just below, then activation by Δ. The BCS calculation with STS Δ fits quantitatively. |
| ρ, ν = ½ | Charge carried by thermally broken pairs: Arrhenius with E_a = 3.72 ± 0.05 ≈ half-gap (3.97; the difference is within the uncertainty of the T-dependent prefactor); pairs incoherent. |
| ρ, ν ≈ 0.3 | Pseudogap removes quasiparticles (upturn, E_a ≈ 0.9) before phase coherence sets in at T_c = 0.36 ≪ T*. |
| ρ, ν ≈ 0.2 | Metallic normal state, then BCS superconductivity at T_c ≈ 1.1 = Δ/1.76. |

---

## 5. Q4 — Predicted low-T ARPES (`fig5_arpes.png`)

A(k, ω) (the intensity after division by the Fermi function, with constant matrix element) is plotted along (0,0)→(½,0)→(½,½)→(0,0). Energy window: **−9.5 ≤ ω − μ ≤ +9.5**, the same for all three panels so the full spectra can be compared; 0.1 energy resolution; intensity on a γ = 0.6 scale. Spectral functions are the theory forms calibrated on the STS (`code/arpes.py`).

**ν = ½ (pair insulator)**
- *Two replica bands that disperse the same way*, lower from −8.0 at Γ to −4.0 at M, upper from +4.0 at Γ to +8.0 at M, each **half** the bare bandwidth. Implication: no Bogoliubov particle–hole mixing (no superconducting coherence) and no folded shadow bands at k + (½,½) (no CDW). Single electrons move incoherently through a disordered background of pairs and empty sites.
- *Momentum-independent direct gap* E₊(k) − E₋(k) = 12.00 everywhere, with the indirect gap 8.0 between the top of the lower band at M and the bottom of the upper band at Γ. Implication: the gap is the **local pair-binding energy |U|**, not a Fermi-surface instability; there is no Fermi surface and no k_F.
- *Weight transfer*: the lower band is strongest at Γ (Z₋ = 0.66) and weakest at M (0.39); the upper band is the reverse. Implication: a smooth momentum distribution with no jump, which leads to the Green's-function structure of Q5.
- *Van Hove (X-point) features* at −5.2 and +6.8, at 70% of each band. Implication: the bare t′ asymmetry survives, so the state lacks particle–hole symmetry.

**ν ≈ 0.3 (strong-coupling superconductor)**
- *Back-bending at the underlying k_F* (0.31 along Γ–X; Fermi velocity 2.7), but with a **broad, weak** quasiparticle (width ≈ 0.7) and a soft gap edge near 2.6. Implication: a condensate exists, but Fermi-surface quasiparticles are incoherent (strong pair/phase fluctuations, small stiffness, T_c ≪ T*).
- *Gap ≈ 5 at Γ, X and M* (Γ: strong occupied band at −6.3), so pairing extends over the whole zone. Implication: local pairs; ξ ≈ v_F/(πΔ) ≈ 0.25a, BEC side of the crossover.
- *Strongly asymmetric Bogoliubov weights* (upper branch stronger, especially near M). Implication: low filling and a chemical potential shifted down (μ ≈ −1.04 vs −0.89 in the normal state).

**ν ≈ 0.2 (BCS superconductor)**
- *Sharp Bogoliubov back-bending* at k_F ≈ 0.255 along Γ–X and (0.178, 0.178) along Γ–M, with isotropic gap 1.96 and coherence peaks. Implication: nodeless on-site s-wave pairing with coherent quasiparticles.
- *Weak shadow branch* (v_k²) dispersing to −5.5 at M. Implication: particle–hole mixing of a coherent condensate.
- *Van Hove feature* at +3.4, the bare one at ξ = 2.8 pushed out by the gap.

**Comparison.**
- From ν≈0.2 to ½ the gap grows (1.96 → about 3.5 at k_F → 4.0 half-gap).
- Its minimum moves from the Fermi surface (BCS) to "everywhere", ending in a k-independent direct gap.
- Quasiparticle coherence near k_F is lost (ν≈0.3).
- The mirror-symmetric Bogoliubov pair of bands (condensate and underlying Fermi surface) is replaced at ν = ½ by two translated replicas: pairs without phase coherence and no Fermi surface.

---

## 6. Q5 — Green's-function zeros at ν = ½ (`fig6_zeros.png`)

**Method.** Re G(k, 0) = P∫ dω′ A(k, ω′)/(0 − ω′) was computed from the predicted (broadened) A(k, ω) on a 361×361 k-mesh, with ω measured from the T→0 chemical potential, which sits at mid-gap (the data's V = 0; the replica centre offset is c = 0.009 ± 0.006). The numerical Kramers–Kronig result agrees with the pole formula to 3×10⁻⁵.

**Result.**
- Re G(k, 0) is positive over almost the whole zone (+0.021 at M) and changes sign only near Γ (−0.0024 at Γ).
- The zeros form a **small closed loop around Γ**. **The fraction of the zone on the Γ side is 0.035.** Propagating the full fit covariance gives a median of 0.038, 68% interval 0.00–0.07; the curve exists in 84% of bootstrap samples.
- **Compared with ν = 0.5:** the Γ-side area is about 14 times smaller than ν. Equivalently, the region with Re G > 0, which counts as "occupied" in Luttinger's sense, covers 0.965 of the zone instead of 0.5. **Luttinger's theorem generalized to zeros fails.**

**Why, and how robust.**
- The two replicas are equidistant from μ only on the **band-centre contour** ε_k = −4t′, which encloses 0.314 of the zone because of t′; the non-interacting ν = ½ Fermi surface encloses 0.500.
- With equal replica weights the zero curve would be that contour, giving **0.314**. The measured momentum-dependent weights almost cancel the asymmetry, which is what the exact first-moment sum rule requires. They push the zero surface up to a weakly dispersing "zero band" ω_z(k) ≈ 0.40 + 0.08ε_k, located at the atomic midpoint rather than at μ.
- The curve at ω = 0 therefore shrinks to the loop around Γ. With exactly Hubbard-I weights (U_w ≤ 13.6) it disappears altogether.
- The fraction is thus bounded between 0 and 0.31 (right panel of Fig. 6), and **in no case equals ν**.
- With particle–hole symmetry (t′ = 0) the same construction places the zeros on the diagonal-square contour cos k_x + cos k_y = 0 (fraction exactly ½).
- The violation is therefore produced by the missing particle–hole symmetry together with μ pinned at mid-gap. This is the mechanism of Rosch (2007) and Dave, Phillips & Kane (2013).

---

## 7. Calculations: approximations and system sizes

| Step | Method | Size |
|---|---|---|
| STS fits (Fig. 1) | Gaussian-broadened spectral functions summed over k; least squares with Jacobian covariance | Irreducible-wedge grid with 80–90 points per π (≈ 3,300–4,100 k-points, equivalent to 160²–180² full zone) |
| NMR / ρ (Fig. 2) | Activated and BCS-pseudogap forms; Hebel–Slichter integral with BCS Δ(T) and Dynes broadening | 24,001-point energy grid |
| Exact diagonalization (Fig. 3) | Lanczos ground states of the t–t′–U model, pair-breaking and spin gaps | 8- and 10-site periodic clusters (≤ 63,504 states per sector) |
| Phase diagram (Fig. 4) | BCS mean field + local-pair crossover for T*; strong-coupling KT scale with SO(4) suppression for T_c; two constants calibrated | 220×220 k-mesh |
| ARPES (Fig. 5) | Calibrated theory spectral functions along Γ–X–M–Γ | 820 k-points × 1,201 energies |
| Zeros (Fig. 6) | Kramers–Kronig of A(k, ω); bootstrap over the fit covariance (600 draws) | 361×361 k-mesh, 5,601 frequencies |

Reproduce: `cd /app/code && python3 fit_all.py && python3 fig_fits.py && python3 ed_study.py && python3 phase_diagram.py && python3 arpes.py && python3 zeros.py`. This takes a few minutes on a workstation. Raw exploratory scripts are kept in `/app/analysis/`.

---

## 8. Predictions and open issues
1. **Superconductivity at ν = ½** below T_KT ≈ 0.08 in clean samples, with a 3D boost if layers couple; no CDW at any T.
2. **Below T ≈ 0.4 the ν = ½ resistivity should depart from Arrhenius** as incoherent pair conduction takes over. If it does not, pair localization (disorder) is required.
3. **Pair satellites near ω ≈ −12** (weight ≈ ν at high T) should appear in a wider-window STS or ARPES.
4. The direct gap at ν = ½ should be **k-independent (12.0)** in ARPES; this is the cleanest discriminator from a Mott–Hubbard or CDW insulator.
5. The main weakness of the minimal model is the strong filling dependence of the effective attraction (|U_eff| from 12 at ν = ½ to 6 at ν ≈ 0.2). It is attributed here to screening by doped carriers but not derived.
