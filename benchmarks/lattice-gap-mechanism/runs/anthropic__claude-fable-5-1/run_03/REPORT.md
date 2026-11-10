# Effective theory for the layered perovskite-block oxide at and near half filling

All energies and temperatures are in units of D. Momenta are in units of 2π/a with a the in-plane metal–metal distance. ν = n/2 with n the number of electrons per transition-metal site. All numbers below are derived from `measurements.json`; the analysis code is in `code/`, intermediate fits in `work/`, figures in `figures/`.

**Summary of the result.** The data are described by a one-band Hubbard model on the square lattice with hopping t = 0.99 D, second-neighbour hopping t′ = 0.195 D (van Hove singularity above the band centre), on-site repulsion U = 12.0 D, and an s-wave pairing interaction g = 6.1 D acting in the Cooper channel. At ν = 1/2 the crystal is a paramagnetic Mott insulator whose single-particle spectrum is two Hubbard bands of half the bare width, separated by U. At ν ≈ 0.2 it is a conventional BCS superconductor on the bare band (Tc = 1.1 D, Δ = 1.97 D, 2Δ/Tc = 3.5, Hebel–Slichter peak). At ν ≈ 0.3 it is a pseudogapped, paired, Mott-reconstructed state below T* ≈ 3.5 D which superconducts only below Tc = 0.36 D. The Mott insulator has no Fermi surface and the Kramers–Kronig Green's function at ω = 0 does not change sign anywhere in the zone: Luttinger's theorem fails there.

---

## 1. Effective theory

### 1.1 Degrees of freedom, lattice, unit cell

* Degrees of freedom: spin-1/2 electrons in one Wannier orbital per transition-metal site (the orbital that dominates the band at the Fermi level; the admixture of other orbitals renormalizes the hopping and gives the smooth, featureless background of ≈0.1 in the STS traces).
* Lattice: two-dimensional square lattice of transition-metal sites, lattice constant a (the in-plane metal–metal distance). One site per unit cell. The diffraction data (no new peaks, no splitting, equivalent sites at all temperatures) show that the crystallographic unit cell is never enlarged, so every phase below is described in this one-site cell. Interlayer coupling is neglected (layered oxide; the STS gap and the in-plane resistivity are two-dimensional quantities).
* Bare dispersion:

  ε_k = −2t (cos kx + cos ky) − 4t′ cos kx cos ky,

  band bottom at (0,0): −4t − 4t′ = −4.74, top at (1/2,1/2): 4t − 4t′ = 3.18, van Hove singularity at (1/2,0): +4t′ = +0.78, i.e. 8t′ = 1.56 above the band centre. Width 8t = 7.9.

### 1.2 Hamiltonian (every term)

H = H_kin + H_μ + H_U + H_pair

* H_kin = −t Σ_{⟨ij⟩σ} (c†_{iσ}c_{jσ} + h.c.) − t′ Σ_{⟨⟨ij⟩⟩σ} (c†_{iσ}c_{jσ} + h.c.) = Σ_{kσ} ε_k c†_{kσ}c_{kσ}
* H_μ = −μ Σ_{iσ} n_{iσ} (μ fixes ν; μ(ν≈0.2) = −1.93, μ(ν≈0.3) = −0.93; at ν = 1/2 μ sits at the midpoint of the Mott gap)
* H_U = U Σ_i n_{i↑} n_{i↓}
* H_pair = −(g/N) Σ_{k,k′} c†_{k↑} c†_{−k↓} c_{−k′↓} c_{k′↑}  (reduced s-wave Cooper-channel attraction; it stands for a retarded, e.g. phonon-mediated, interaction that acts at low energy in the pairing channel only, whereas U acts at all energies in the local charge channel. The two cannot be merged into one on-site constant: U sets the 12 D Mott splitting, g sets the ≈2 D pairing gaps.)

### 1.3 Coefficients and uncertainties (from the data)

| coefficient | value (D) | uncertainty | determined from |
|---|---|---|---|
| t | 0.99 | ±0.01 | width of the bare band in Fig. 1(c),(d): 0.995±0.003 and 0.984±0.005; systematic from broadening model |
| t′ | +0.195 | ±0.005 | position of the van Hove peak in Fig. 1(a),(c),(d): 0.198±0.002, 0.192±0.003, 0.194; the sign is fixed by the peak lying above μ for ν<1/2 |
| U | 12.02 | ±0.05 | separation of lower and upper Hubbard bands in Fig. 1(a) (12.023±0.013 statistical) |
| g | 6.1 | ±0.2 | cutoff-free BCS gap equation 1 = g⟨1/2E_k⟩ with Δ(ν≈0.2) = 1.967 (gives 5.97) and the ν≈0.3 gap edge 2.45 (gives 6.25) |
| μ | −1.93 / −0.93 | ±0.01 | fraction of the zone below μ in Fig. 1(c),(d): 0.198 and 0.295, i.e. ν = 0.20 and 0.30 as labelled |

Supporting numbers at ν = 1/2 (Fig. `figures/fig_sts_fits.png`(a), `figures/supp_inverted_weights.png`): the two bands have dispersions E_±(k) = ±U/2 + a ε_k + c₀ with a = 0.515 ± 0.03 (i.e. ε_k/2), k-independent splitting E₊−E₋ = 12.02 ± 0.1 at the band bottoms, the van Hove points and the band tops, and spectral weights w_∓(k) = ½(1 ∓ α ε_k) with α = (1.02 ± 0.07)/U. These are exactly the first-order strong-coupling (t/U) results for the paramagnetic Mott insulator: both Hubbard bands are copies of the bare band compressed by one half, and spectral weight is transferred from the lower band at (0,0) (w₋ = 0.70) to the upper band at (1/2,1/2) (w₊ = 0.63).

### 1.4 Symmetries the model has and lacks

Has: lattice translations with one site per cell (never broken: diffraction), the C4v point group of the plane (never broken), spin SU(2) (never broken: single NMR line, no magnetic order in any phase; the Mott insulator is treated as a spin-disordered paramagnet), time reversal, and global U(1) charge conservation, which is spontaneously broken only in the superconducting phase (s-wave, full gap).

Lacks: particle–hole symmetry (t′ ≠ 0; the Hubbard bands are not mirror images, the phase diagram is not symmetric about ν = 1/2), SU(2) pseudospin symmetry, long-range Coulomb interaction (no charge order), spin–orbit coupling, interlayer hopping, explicit lattice (phonon) dynamics (g is instantaneous in the effective theory), and intersite spin exchange J = 4t²/U ≈ 0.33 D is dropped (it is below the lowest temperature at which spin correlations could be seen in the data, 0.2 D, only marginally; no signature of it is present).

### 1.5 How the Hamiltonian is solved (approximations and system sizes)

* ν = 1/2: strong-coupling expansion to first order in t/U (Harris–Lange / Hubbard-I expanded to O(t/U)) for the spin-disordered paramagnet: A(k,ω) = ½(1 − ε_k/U) δ(ω − E₋) + ½(1 + ε_k/U) δ(ω − E₊), E_± = ±U/2 + ε_k/2 + c₀, c₀ = −(ε_min + ε_max)/4 = 0.39 (puts μ at midgap). The full Hubbard-I resummation was tested and is excluded by the unequal edge heights of the two bands (Fig. `figures/supp_fit_nu_half_models.png`), as is the exactly solvable Hatsugai–Kohmoto model (full-width bands, equal weights).
* ν ≈ 0.2: BCS mean field on the bare band, cutoff-free gap equation at fixed μ, Δ(T) and T_MF from the same g.
* ν ≈ 0.3, T < T*: the pairing operates on Mott-reconstructed quasiparticles. The spectral function is written in the Bogoliubov form A(k,ω) = Z_k [p₊(k) δ(ω − E_k) + p₋(k) δ(ω + E_k)] with mirror bands ±E_k, E_k = c + a ε_k + b ε_k², p_± = ½(1 ± ξ̃_k/E_k), ξ̃_k = α + β ε_k, and the low-energy weight Z_k = u_k² = ½[1 + (ε_k−μ)/√((ε_k−μ)² + Δ₁²)] with Δ₁ = 2.45 the pairing gap itself; the missing weight 1 − Z_k = v_k² = n_{k,−σ} sits in the upper Hubbard band at ≈ +U, outside the measured window. Fitted to Fig. 1(b): c = 4.65, a = 0.56, b = 0.018, α = 1.03, β = 0.51 (rms 0.051 on a trace normalized to 1, comparable to the 0.036–0.042 of the other panels). This part of the theory is phenomenological: the dispersion compression a ≈ 0.56 and the weight transfer are the Mott ingredients, the mirror structure and the coherence factors are the pairing ingredients.
* Transport and NMR: local bubble 1/(T₁T) ∝ ∫dω N(ω)² (−∂f/∂ω) (plus the BCS coherence term M(ω)² in the superconductor), and ρ ∝ T/N_eff(T) with N_eff = ∫N(ω)(−∂f/∂ω)dω (T-linear scattering rate on a thermally averaged density of states); ρ = 0 below Tc.
* System sizes: k grids of 700×700 (fits) and 400×400 (final figures); Gaussian instrumental broadening 0.10–0.19 D fitted to the STS; Lorentzian η = 0.12 D for the ARPES maps; Kramers–Kronig on a 16001-point frequency grid. Everything runs on a workstation in minutes.

---

## 2. Phase diagram

Figure: `figures/fig_phase_diagram.png`. Horizontal axis ν from 0 to 1, vertical axis T. The three crystals are the vertical lines at ν = 1/2, 0.3 and 0.2.

* Thick black line at ν = 1/2: Mott insulator, gap 8.0 D, no magnetic or charge order, at every measured temperature (0.45–4.4 D); the gap closes only on the scale of U.
* Blue dashed: T_MF(ν) from the gap equation with g = 6.1: 1.12 at ν = 0.2, 1.27 at ν = 0.3, 1.33 at ν = 0.48 (it follows the density of states at μ, which grows toward the van Hove filling ν = 0.58).
* Blue solid: Tc(ν) = min(T_MF, T_coh). Far from half filling Tc = T_MF (ν ≈ 0.2: Tc = 1.1 = T_MF). Approaching half filling the phase-coherence scale collapses with the hole density; it is parametrized as T_coh ∝ |1 − 2ν|³ through Tc(0.3) = 0.36 (only this point and the inequality T_coh(0.2) ≥ 1.1 are measured, so the exponent is not determined; any form with T_coh(0.3) = 0.36, T_coh(0.2) ≥ 1.1 and T_coh → 0 at ν → 1/2 is allowed). The dome maximum is Tc ≈ 1.1–1.2 near ν ≈ 0.2.
* Red: T*(ν), the pseudogap onset. T* ≈ Tc at ν ≈ 0.2 (no pseudogap: Korringa NMR and ρ ∝ T right above Tc), T* ≈ 3.5 ± 1 at ν ≈ 0.3 (1/(T₁T) is Korringa-like at 4.4 and 10 D, suppressed below ≈3 D; ρ stops decreasing on cooling below ≈4 D), T* → ∞ at ν = 1/2. The curve drawn is schematic between these constraints.
* Shaded orange: pseudogap region (paired, Mott-reconstructed, insulating-like); shaded blue: superconductor. Elsewhere: metal with the bare band. The side ν > 1/2 is obtained from the same Hamiltonian (electron doping); because t′ ≠ 0 the van Hove filling lies at ν = 0.58, so the mean-field pairing scale is slightly higher on that side; otherwise the structure mirrors the hole-doped side. No data constrain it.

Phases from low to high temperature:

* ν = 1/2: Mott insulator (paramagnetic, gapped) at all temperatures measured.
* ν ≈ 0.3: superconductor (T < 0.36) → pseudogap state (0.36 < T < T* ≈ 3.5: full single-particle gap 2×2.45 D, no phase coherence, resistivity rising on cooling) → metal with the bare band (T > T*).
* ν ≈ 0.2: s-wave BCS superconductor (T < 1.1) → metal with the bare band (Korringa NMR, ρ ∝ T).

---

## 3. Explanation of each measurement

Figures: `figures/fig_sts_fits.png`, `figures/fig_nmr_rho.png`.

**Diffraction.** No new peaks, no splitting, equivalent sites at all T: none of the three phases breaks translation or the fourfold symmetry. The Mott insulator is produced by U alone in a one-site cell (no antiferromagnetic doubling of the cell is needed, and the single NMR line excludes a static staggered moment); the superconductor and the pseudogap are zero-momentum (Cooper-channel) instabilities, which leave the lattice periodicity intact.

**STS.**
* (a) ν = 1/2: the two bands at [−8.0, −4.0] and [+4.0, +8.1] are the lower and upper Hubbard bands; their separation is U = 12.0, the gap 8.0 = U − 4t is U minus the half-compressed bandwidth, each band has the shape of the bare density of states compressed by 1/2 (compressed van Hove peaks at −5.2 and +6.8, both 2.8 above the respective band bottom). The feature of the theory producing this is the atomic-limit splitting U and the first-order hopping of a hole or doublon in a spin-disordered background, which gives the dispersion ε_k/2. The asymmetric edge heights (0.30 vs 0.15 at the bottoms, 0.35 vs 0.54 at the tops) are the spectral-weight transfer w_∓ = ½(1 ∓ ε_k/U).
* (c) ν ≈ 0.2: BCS density of states of the bare band, Δ = 1.967 ± 0.003 (coherence peaks at ±1.97), with the bare band's bottom at ξ = −2.8 and its van Hove singularity at ξ = +2.76 appearing at −3.4 and +3.4 through E = √(ξ² + Δ²). Produced by H_pair in mean field on the bare band; the lower band carries ⟨v_k²⟩ = 0.25 per spin, consistent with the integrated weight ratio 0.29–0.31.
* (d) ν ≈ 0.3, high T: the bare band (t = 0.98, t′ = 0.19) with μ putting 29.5 % of the zone below it: the van Hove peak at +1.7, band edges at −3.8 and +4.1. Produced by H_kin alone: above T* the Mott and pairing renormalizations are gone.
* (b) ν ≈ 0.3, low T: a full gap of ±2.45 around the gap midpoint, mirror-symmetric bands extending to ±6.5 with equal weights near the gap edges and an upper/lower weight ratio ≈1.8 near the band edges, a compressed van Hove peak at 5.1. Produced by pairing (mirror bands with equal coherence factors near the gap edge are the Bogoliubov signature; the gap value 2.45 is reproduced by the same g that gives Δ = 1.97 at ν ≈ 0.2, because the density of states at μ is larger at ν = 0.3) acting on Mott-reconstructed quasiparticles (upper band = bare band compressed by 0.56, exactly as the Hubbard bands at ν = 1/2, and low-energy spectral weight removed from the interior of the Fermi sea and transferred to the upper Hubbard band beyond the window, which is why there are no BCS coherence peaks and the gap edge rises linearly). The spectrum is not BCS on the bare band: that would end at ±4.8 and show coherence peaks (tested, excluded).

**NMR 1/(T₁T).** The single line at all ν and T is the absence of static magnetism and of inhomogeneity. The temperature dependence follows the single-particle gap through the local bubble ∫N(ω)²(−∂f/∂ω)dω:
* ν ≈ 0.2: Korringa plateau above Tc (bare metal), Hebel–Slichter peak just below Tc = 1.1 (data 1.8× the normal value; the model with the coherence factor and a Dynes broadening 0.08 gives 1.6×), then exp(−Δ_eff/T) with Δ_eff = 1.73 ± 0.04 (model 1.72). This is the fingerprint of a full s-wave gap with BCS coherence factors; 2Δ/Tc = 3.5.
* ν ≈ 0.3: no Hebel–Slichter peak at Tc = 0.36, exponential suppression exp(−2.64/T) (±0.07) from T ≈ 3 down to 0.2 that passes smoothly through Tc. Produced by the pseudogap: the single-particle gap 2.45 is already open above Tc, so Tc leaves no trace in a single-particle probe. The model with the fitted spectrum gives a steeper slope (3.5) because its onset step at the gap edge is very small; the data require slightly more weight right at the edge than the fit puts there.
* ν = 1/2: activated with 5.5 ± 0.4, no Korringa regime below 4 D. Produced by the Mott gap: carriers must be thermally excited across it. The local-bubble model with the fitted bands gives 4.3 (the gap edge 4.0 steepened by the compressed van Hove peaks); the data are steeper by ≈1 D, which the purely local formula does not capture (a relaxation weighted toward the antiferromagnetic wavevector, where the two Hubbard bands connect at ≈5.5 D, would).

**Resistivity.**
* ν ≈ 0.2: ρ = 0 below Tc ∈ (1.075, 1.15) (BCS T_MF = 1.12 with g = 6.1); above, ρ ∝ T^0.7–1 (quasi-linear) from the T-linear scattering rate on the bare band.
* ν ≈ 0.3: ρ = 0 below Tc ∈ (0.325, 0.40); above Tc the resistivity rises on cooling (8.9× the T = 4 value at T = 0.4) and is flat rather than ∝ T between 2.5 and 4: the pseudogap removes carriers. The effective transport activation energy, 0.94 ± 0.09 (pure exponential) or ≈1.45 above a constant floor, is smaller than the spectroscopic gap 2.45: transport is carried by the soft, low-weight edge states (and by pair fluctuations) rather than by the full gap; the simple T/N_eff model over-estimates the upturn.
* ν = 1/2: activated insulator, ρ ∝ exp(Δ_ρ/T) with Δ_ρ = 3.7 ± 0.1 (p = 0) to 4.4 (p = 1), bracketing the gap edge 4.0; produced by thermal activation across the Mott gap. The two simple models 1/N_eff (slope 4.15) and T/N_eff (3.4) bracket the data.

---

## 4. ARPES prediction at low temperature

Figure: `figures/fig_arpes.png` (A(k,ω) along (0,0) → (1/2,0) → (1/2,1/2) → (0,0); the Fermi-function division restores the intensity above μ; energy windows ±10, ±8 and ±7 D; Lorentzian width 0.12 D).

* ν = 1/2 (left): two bands, E₋ = −6 + ε_k/2 + 0.39 ∈ [−8.0, −4.0] and E₊ = +6 + ε_k/2 + 0.39 ∈ [4.0, 8.1], dispersing in parallel (both follow ε_k/2, maxima at (1/2,1/2), saddle at (1/2,0)). No band crosses μ: no Fermi surface, a direct gap of 8.0 at every k (minimum at (1/2,1/2) for the lower band, at (0,0) for the upper). The intensity of the lower band is largest at (0,0) (0.70) and weakest at (1/2,1/2) (0.37), the upper band the reverse. Features of significance: (i) the parallel ("copy") dispersion is the hallmark of Hubbard bands as opposed to a density-wave gap (which gives mirror bands); (ii) the k-dependent weight transfer between the bands is the Mott spectral-weight transfer and encodes U; (iii) the compression by 1/2 encodes the disordered spin background (a Néel background would make the bands nearly flat on the scale t²/U).
* ν ≈ 0.2 (right): Bogoliubov bands ±√(ξ_k² + Δ²), Δ = 1.97, on the bare band. Back-bending at the Fermi momenta k_F = (0.252, 0) and (0.177, 0.177); for |k| < k_F the intensity sits in the lower branch (v_k² → 1 at (0,0)), for |k| > k_F in the upper branch; the upper branch follows ξ_k up to the band top (5.5) and the lower branch mirrors it (−5.5 at (1/2,1/2)) with weight v_k² = 0.03. Features: (i) the back-bending and the particle–hole mixing confined to a thermal/Δ window around k_F are the BCS signature; (ii) the normal-state Fermi surface (contour ξ_k = 0, a closed electron pocket around (0,0)) encloses 19.8 % of the zone = ν, i.e. Luttinger's theorem holds in this phase; (iii) the gap is the same everywhere on the Fermi surface (s-wave).
* ν ≈ 0.3 (middle): mirror bands ±E_k with E_k rising monotonically from 2.4 at (0,0) through 5.1 at (1/2,0) to 6.6 at (1/2,1/2). Unlike BCS, the lower branch does not bend back to follow ξ_k: it is the inverted image of the upper branch everywhere, and the coherence factors are equal (p₊ ≈ p₋) over the whole interior of the former Fermi sea, not only at k_F. The total low-energy intensity Z_k is suppressed inside the normal-state Fermi surface (Z = 0.08 at (0,0), 0.78 at (1/2,0), 0.93 at (1/2,1/2)); the missing weight is in the upper Hubbard band at ≈ +10 to +12 D (outside the window). Features: (i) a k-independent full gap 2×2.4 with no coherence peaks is the pseudogap; (ii) the upper branch is the bare band compressed by ≈0.56, i.e. the same Mott compression as the Hubbard bands at ν = 1/2 — the state is Mott-reconstructed; (iii) the weight transfer out of the Fermi sea is the dynamical spectral-weight transfer of a doped Mott insulator; (iv) the dotted bare band ξ_k shows where the high-T Fermi surface (k_F = (0.31, 0) and (0.215, 0.215), enclosing 29.5 % = ν) was; at low T it is gapped everywhere.

Comparison: going from ν = 0.2 to 0.3 to 0.5 the spectrum changes from "bare band + small pairing gap at k_F" to "compressed band + large full gap + weight transfer" to "two compressed copies separated by U with no low-energy states": the proximity to the Mott insulator progressively replaces the Fermi-surface physics (back-bending at k_F) by Mott physics (gap everywhere, compressed dispersions, weight transfer between bands separated by U).

---

## 5. Green's function at ν = 1/2 by Kramers–Kronig; zeros and Luttinger count

Figure: `figures/fig_luttinger.png`. From the predicted A(k,ω) (two Lorentzian-broadened bands, η = 0.05), Re G(k,ω) = P∫dω′ A(k,ω′)/(ω − ω′). At ω = 0 (the chemical potential, midgap) this gives Re G(k,0) = −w₋/E₋ − w₊/E₊; the numerical principal-value integral reproduces the exact expression to 10⁻⁴.

Result: Re G(k,0) is positive at every k, between +0.0108/D (near (1/2,0)) and +0.0121/D (at (0,0) and (1/2,1/2)), roughly ten times smaller than the band-edge scale 1/(4 D) but without a sign change. The zeros of G lie at the energy ω₀(k) = w₋E₊ + w₊E₋ = c₀ = +0.39 D above the midgap for every k: in this theory the self-energy pole (the "Mott pole") is pinned at the atomic energy U/2 above the on-site level, which lies 2t′ above the gap centre of the particle–hole-asymmetric band. Exactly at ω = 0 the zeros therefore do not form a curve; they fill the zone at ω = +0.39 D. In terms of the Luttinger count (fraction of the zone where Re G(k,0) > 0, poles and zeros both counted) the result is 1, i.e. two electrons per site, which is incompatible with ν = 1/2: Luttinger's theorem, which relies on a Fermi liquid with a pole surface, fails in the Mott insulator; the count depends on where in the gap μ sits (it jumps from 1 to 0 when μ crosses ω₀), which is the known arbitrariness of the Luttinger count in an insulator.

If the self-energy pole is allowed to disperse, ω₀(k) = c₀ + λ ε_k (as in momentum-space Mott models, where λ = 1), the zeros at ω = 0 form a closed curve around (0,0). The STS data bound λ ≤ 0.05 (the sum of the two band compressions minus U times the weight slope is 0.01 ± 0.09), for which no curve exists; for λ = 0.2, 0.5, 1 the curve encloses 20 %, 23 %, 36 % of the zone (right panel of the figure). The two natural closed contours of the ν = 1/2 spectrum are the equal-weight contour ε_k = 0 (where the two Hubbard bands carry equal spectral weight), enclosing 41.7 % of the zone around (0,0), and the band-centre contour ε_k = −4t′, enclosing 31.3 %. Both differ from ν = 50 %. The conclusion is robust against these choices: in the Mott insulator the fraction of the zone on the (0,0) side of any zero surface of G is not equal to ν (here 0.31–0.42, or formally 1, versus 0.5). With t′ = 0 all these contours would coincide with the diamond |kx|+|ky| = 1/2 and enclose exactly 1/2; the violation is driven by the particle–hole asymmetry t′, consistent with the breakdown of Luttinger's count in Mott insulators without particle–hole symmetry.

---

## 6. Limitations

* The ν ≈ 0.3 low-temperature spectral function is fitted, not derived; its ingredients (Mott compression, weight transfer, Bogoliubov mirror structure, the same g) are those of the Hamiltonian, but a controlled solution of H in this regime (cluster methods) was not attempted.
* The simple local-bubble and T/N_eff formulas reproduce the activated behaviour of NMR and resistivity qualitatively; quantitatively the NMR slope at ν = 1/2 is 20 % steeper and the transport gap at ν ≈ 0.3 a factor 2–3 smaller than the models.
* The coherence temperature T_coh(ν) that suppresses Tc near the Mott insulator is fixed by one point; its functional form is a guess.
* The electron-doped side (ν > 1/2) of the phase diagram is an extrapolation of the same Hamiltonian with no data.
