# Grading report: eleven agent runs on `problem/prompt.pdf`

Prepared 2026-10-31 from the run folders in this directory. All runs received the prompt version with
Tc(0.2) = 1.11D, the Hebel-Slichter NMR curve at nu = 0.2 and the activated half-filled resistivity, i.e. the
data before the 2026-10-30/31 revisions (pseudogap NMR at nu = 0.2, Boltzmann curve at nu = 1/2,
Halperin-Nelson tails, the 0.05D sentence). Scores are 20 points per item, 100 total. "LSM" = the
Lieb-Schultz-Mattis chain from one orbital per site + one in-plane site per cell + featureless gap at
nu = 1/2 to two equivalent transition metals per cell (a bilayer block).

## Scoreboard

| Run | Model written | 1 | 2 | 3 | 4 | 5 | Total | Note |
|---|---|---|---|---|---|---|---|---|
| anthropic/claude-opus-5-5 run_01 | bilayer t-t'-J-U (J = 6.6, U = 1.4) via LSM | 19 | 17 | 18 | 18 | 19 | **91** | 16-site ED + CPT; stiffness from twisted BC; quantitative rejection table for attractive U; item 5: 0.855 on the Gamma side with Re G > 0, zero band swept in omega_r |
| anthropic/claude-opus-5-5 run_03 | bilayer t-t'-J (J = 8.0, U ~ 0) via LSM, named SMG | 18 | 16 | 17 | 16 | 16 | **83** | leading-order strong coupling + 2-4-rung ED; item 5: 0.315 (equal residues), notes the (pi,pi) ambiguity |
| anthropic/claude-fable-5-1 run_01 | single-layer attractive U with U_eff(nu) = 12/8.5/6 | 7 | 10 | 11 | 13 | 16 | 57 | CPT zero curve 0.46; evades LSM by placing pair order below the measured window |
| anthropic/claude-opus-5-5 run_02 | single-layer attractive U with U_eff(nu) | 7 | 10 | 11 | 13 | 16 | 57 | states LSM for pairs and predicts SC below 0.08D; item 5: 0.035 |
| anthropic/claude-fable-5-1 run_02 | single-layer repulsive U = 12 + separate pairing V | 5 | 9 | 9 | 13 | 15 | 51 | "paramagnetic Mott insulator"; spin gap explained by a (pi,pi) form factor; item 5: 0.14 |
| anthropic/claude-fable-5-1 run_03 | single-layer repulsive U = 12 + pairing g | 5 | 9 | 9 | 12 | 14 | 49 | item 5: no zero curve at omega = 0 (flat zero band), alternatives 0.31-0.42 |
| openai/gpt-6-1-sol (Sol) run_02 | conditional two-pole spectral Hamiltonian, no interaction | 9 | 4 | 9 | 8 | 16 | 47 | precise fits; item 5: 0.081 (matches the generating spectrum); finds the t-sign and 2D-stiffness issues; declines the model |
| openai/gpt-6-astra run_01 | conditional bilayer trial, coefficients "not identified" | 9 | 4 | 9 | 8 | 16 | 46 | item 5: 0.075 with the (pi,pi) counterexample; no phase diagram |
| openai/gpt-6-astra run_02 | single-layer Hubbard "starting model" | 4 | 3 | 8 | 5 | 12 | 32 | non-uniqueness constructions only |
| openai/gpt-6-astra run_03 | same | 4 | 3 | 8 | 5 | 12 | 32 | same |
| openai/gpt-6-1-sol (Sol) run_01 | single-orbital Hubbard U = 11.5, 8-10-site ED; solution withdrawn | 4 | 3 | 7 | 5 | 11 | 30 | "joint solution not obtained"; careful audits, no answer |

Means: Opus 5.5 77, Fable 5.1 52, GPT-6 Astra 37, GPT-6.1 Sol 38.

## What every run got right

The kinetic part is not discriminating: all eleven extract t1 = 1.00 +- 0.01, t2 = 0.20 +- 0.01 and
mu(0.3) = -0.91 from panel (d), check that the occupied fraction is 0.30, and read the energy scales
(spin gap 5.5, transport activation 3.7, Tc brackets, the Hebel-Slichter peak at nu = 0.2 and its absence at
nu = 0.3). All recognize that the two bands of panel (a) are translated, not mirrored, copies of the bare band
with reduced width. Nobody imported literature parameters.

## Where the runs separate

1. The bilayer. Only the two Opus runs wrote the LSM chain. Three runs chose a single-layer attractive U
   and escaped LSM through the finite measurement window (pair order predicted below 0.2D) plus a
   doping-dependent U_eff; two chose a single-layer repulsive U and ignored the 5.5D spin gap; the five
   OpenAI runs declined to choose. This step is where the problem discriminates, and its success rate for
   the strongest model is roughly one in three per run.
2. Item 5 values spread from "no curve" through 0.035, 0.08, 0.14, 0.31, 0.46 to 0.855, as the
   residue-sensitivity analysis predicted. The range-based rubric is necessary.
3. Two runs (Sol run_02, Opus run_03) flagged the t-sign / (pi,pi) ambiguity; four runs flagged
   that Tc(0.2) = 1.11D exceeds the 2D stiffness bound. Both are fixed in the current prompt and data.
4. Reported problem inconsistencies that are now fixed: BCS fit of panel (c) returning nu = 0.256 with the
   normal-state mu (the 10-28 regeneration solved the number equation); the nu = 1/2 window; the Hebel-Slichter
   curve at nu = 0.2 against T_MF = 1.00D.

## Audit: published curves versus the best calculations of the same Hamiltonian

The public curves were generated at leading order in t/J (panel (a)), in mean field (panel (c)), and by an
interpolation (panel (b)). The reference answer's own exact diagonalization (3x3 and 4x2 bilayer tori at
J = 8, U = 0; `problem/reference/data/ed_calibration.json`, `luttinger.json`) and the two Opus runs give
the following picture.

| Quantity | Published | Reference ED (J = 8) | Opus run_01 (16-site, U = 1.4, J = 6.6) | Opus run_03 (LO / 2nd order) |
|---|---|---|---|---|
| charge gap, nu = 1/2 | 8.0 | 8.6 (3x3 mixed BC), 8.55 (4x2), 8.9 (3x3 pp) | 8.2 at its own parameters | 8.0 / 8.4 |
| spin gap, nu = 1/2 | 5.5 (two-rung band, edge 5.43) | 5.43 (4x2), 5.66 (3x3 extrapolated), 6.3 (3x3 lowest at (1/3,1/3)) | 4.7 at J = 6.5 | 5.43 |
| coherent width of each side band | 4.0 (eps/2) | hole 3.0, particle 2.7 (slopes 0.39 / 0.33 in eps) | "CPT reproduces edges" | 4.0 / 3.0 |
| incoherent weight | 10 % placed 3.5D beyond each pole | 4-6 % on average (up to 25 % of the removal weight at Gamma), 3.4-4.0D beyond the coherent pole, spread 1.4-1.5D (duplicate-pole-corrected, see note) | satellites present | satellites 3-4D out |
| residues at Gamma / M (hole band) | Eq. (19): hole weight larger at Gamma | 0.46 / 0.20 (coherent) | 0.725 / 0.34 (n_k) | - |
| Re G(k,0) around Gamma | negative (small pocket) | positive; zero band 0.59 at Gamma to -0.23 at M, slope -0.14 vs eps | positive | - |
| fraction with Re G > 0 at omega_r = 0 | 0.94 | 0.82 (exact cluster contour) - 0.87 (calibrated interpolation) | 0.855 | 0.685 or 0.315 by t sign |
| Delta, nu = 0.2 | 1.73 (mean field) | 1.8-2.2 (ED) | 2.45 (ED), 1.6 (CPT) | 1.96 (fit) |
| Delta, nu = 0.3 | 2.49 (interpolation) | 2.4-2.55 (ED) | 2.7 (ED), 2.1 (CPT) | 2.5-2.9 (fit) |
| Tc, nu = 0.3 | 0.20 | hard-core bosons 0.22 | stiffness-fit 0.36 | 0.20-0.38 |
| Tc, nu = 0.2 | 0.40 | 2D BKT estimate 0.38; bound 0.57 | T_KT <~ 0.3 | 0.40 |

Note on the reference calibration: `reference/data/ed_calibration.json` lists at the interior cluster momenta
a "main" pole with about half the residue and a "rest" of equal weight 0.3-0.9D away. The raw pole lists in
`ed_3x3_path.json` show that those interior momenta have every pole listed twice (symmetry images summed
with half weight), so the reference's 20-40 % "satellite at 1.4D" is a bookkeeping artifact; merging the
duplicates (`problem/code/ed_dos_calibration.py`) gives coherent residues of 0.28-0.55 and a genuine
incoherent weight of a few percent about 4D out, close to the old generator's picture. The reference's
"0.74 for the calibrated spectrum" inherits the same artifact; the exact cluster Re G(k,0) and zero band
are unaffected (0.82).

Reading: the NMR, transport and doped panels are consistent with the exact solution to about 20 %, which is
inside the rubric tolerance. Panel (a) is not: at J = 8 the model's gap is 8.6 +- 0.3, not 8.0; the coherent
bands are 2.7-3.0 wide, not 4.0; and the momentum structure of the residues is the opposite of the
Eq. (19) form, which flips the sign of Re G(k,0) around Gamma and moves the item-5 fraction from 0.94 to
0.82-0.87. A solver who diagonalizes the model (both Opus runs, the reference) therefore finds panel (a)
"cleaner and wider" than the model allows and retunes J downward (7.4-7.6 from the charge gap against
8.0-8.2 from the spin gap). The k-integrated curve is not contradicted by the data in a way a grader would
catch, but the answer key for item 5 is built on residues the Hamiltonian does not have.

## Recommendation for the figures (item 1 carried out 2026-10-31, see below)

1. Regenerate panel (a) from the 3x3 ED-calibrated spectrum of the reference answer (coherent poles
   E_h(eps), E_p(eps) with their fitted residues, plus the "rest" weight at its fitted offsets, broadened as
   now), keeping J = 8, U = 0. Expected landmarks: gap edges near +-4.3, coherent widths 3.0 / 2.7, peaks
   shifted inward relative to -5.2 / +6.8, visible shoulders about 1.4D outside each coherent band. Then
   recompute the item-5 key from the same spectrum (0.74-0.81 with Re G > 0 around Gamma; zero band
   dispersing opposite to the bands by about 1.2D; fraction sweeping 0.91 to 0.46 for +-0.3D of reference
   shift) and update the landmark numbers in TASK.md. The reference code (`analyze_ed.py`, `arpes.py`,
   `luttinger.py`) already produces this spectrum; only the k-integration and the noise step are new.
2. Optionally switch the nu = 1/2 NMR to the 3x3 triplon band (edge 5.66 instead of 5.43); the public
   slope moves from 5.5 to about 5.7. Low priority.
3. Keep panels (b), (c), (d), the doped NMR and all resistivities as they are now; they agree with the
   exact results within the tolerance and their forms (mean field with sharp coherence peaks at nu = 0.2,
   spread gap at nu = 0.3) are the intended fingerprints.
4. After (1), re-derive the reference report's item-4 and item-5 figures from the same spectrum so that
   data, key and reference agree.

## Status after the 2026-10-31 regeneration

Item 1 is done. `problem/code/ed_dos_calibration.py` refits the 3x3 cluster poles with duplicates merged and
writes `problem/author/ed_dos_calibration.json`; `public_spectra.py` now builds panel (a) as the momentum
sum of that calibrated spectrum (coherent bands with the fitted residues, ETA = 0.08; incoherent weight
1 - n(k) - w_p and n(k) - w_h as Gaussians 3.96D / -3.37D beyond the coherent poles with spreads 1.52 /
1.39). New landmarks of the clean curve: gap 8.6 with inner edges at +-4.3, removal band -7.3 to -4.3
(peak -4.8), addition band +4.3 to +7.0 (peak +6.1), weak outer shoulders near -10.7 and +10.
Item-5 key from the same spectrum: Re G(k,0) > 0 on 0.87 of the zone around (0,0) (exact cluster contour
eps = 1.93 gives 0.82); zero band +0.82 at (0,0), +0.27 at (1/2,0), -0.41 at (1/2,1/2), dispersing by 1.2
opposite to the bands; the fraction sweeps from 1 at omega_r = -0.5 to 0 at omega_r = +1.0. The
Halperin-Nelson parameter was reduced from b = 0.15 to 0.08 at the same time. Items 2-4 are still open;
the reference report predates all of the 2026-10-30/31 changes.
