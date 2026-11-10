# Actual original-error finite-forward event bounds

This isolated extension derives and implements a relative decoding-event
remainder that retains the rare event's uniform mass. A schedule-aware refinement
certifies actual rounded-program original-optimum probability orders on 45/48
ordinary sparse-H pairs, at a median duration 256 times the previous global-norm
certificate. The durations remain very early and the guaranteed relative gains
are tiny. This is a partial finite-forward theorem, not practical QA closure.

## Scientific question and controls

The target event is minimum-cost feasible ORIGINAL-error root readout, including
all ties and arbitrary compiler/chain excitations. The full physical Hamiltonian
is K(u)=−(1−u)ΣX+uE(Z), initialized in standard |+>, with total dimensionless
forward duration T. No terminal Gibbs assumption, mean-cost substitution or
encoded initial state is used.

The extension reuses all 48 parent fixed-coupling amplification pairs: four
structurally distinct sparse-H generators, n=16/32/64, historical seeds
1101/2203/3307 and parent fresh seed8809. Each size has 16 inputs. The programs
have 54–742 physical spins. The parent independently audited static fidelity and
hardware ranges. This extension does not alter embeddings or solve decoding.
All programs/cost moments are input-hashed, and all outcomes are retained.
Because the extension was devised after earlier studies, it is subsequent
reference research, not a new held-out model test or calibration.

PROTOCOL.md freezes the relative-support theorem and dyadic menu before outcomes.
The first result motivated WORD_MAJORANT_PROTOCOL.md, frozen before its results.
The latter fixes low-order majorants through order12. Three controls share the
same descending dyadic duration menu 2^(-k), k=0,...,80:

1. Parent global-norm event certificate.
2. Recomputed actual-program global-norm certificate, charging actual field
   rounding directly to the exact second-order coefficient.
3. Relative original-root support bound, then the separately declared
   driver/diagonal word refinement.

The actual-curvature global control selects exactly the same durations as the
parent on all 45 positive cases. Duration gains therefore arise from improved
remainder control, rather than a change in rounding accounting or input cohort.

## New theorem and algorithm

THEORY.md gives the full proof. Represent operators as Σ_v f_v(Z)X^v, and use
Σ_v E_uniform|f_v| as a norm. A diagonal root-event projector starts with norm
P0, its uniform root-pattern mass. Translations preserve this norm; each local
Pauli commutator costs at most twice its coefficient. Termwise support growth
gives a relative kth coefficient bound

    |a_k(F)|≤binom(n+k−1,k)(1+gE)^k,
    gE=max_q(|h_q|+Σ_r|J_qr|).

Odd expectation coefficients vanish. This yields an exact relative even
negative-binomial tail with original readout support n, avoiding the total
physical-system norm and avoiding division by exponentially small P0.

The refinement distinguishes driver and diagonal-energy commutators. After d
D and m E insertions, flip displacement has at most d sites and functional
support at most n+m. E only acts incident on the flip displacement; a final
outer D commutator has zero |+> expectation. An exact polynomial-integral
recurrence bounds these mixed words. C2=ngE/6 and

    C4=n³gE/56+n(35n+17)gE²/1260+ngE³/168.

Even C4,...,C12 bound low-order terms; the proved generic tail bounds all higher
even orders. The recurrence is cached by n. No unknown-event patterns or
physical state vector are enumerated during ordinary evaluations.

For objective amplification, actual rounded root-field deviations have L1 rho.
The optimum-event T² difference is lower-bounded by

    Aactual=Δη D_lower/12−rho/6,

where D_lower comes from the parent's exact affine feasible cost moments and
upper-bounds the unknown optimum cost appropriately. All higher terms use
ACTUAL rounded program strengths. Aactual*T² minus the two relative remainders
is an exact rational lower bound on [Pnew(opt)−Pbase(opt)]/P0.

## All ordinary-instance outcomes

Both relative methods certify 45/48 inputs. The same three cases have nonpositive
cheap curvature bounds in the parent's method and remain inconclusive:
irregular_hubs_n16_s1101, irregular_hubs_n32_s2203 and
mixed_hypergraph_n64_s2203. They are not discarded or labeled negative orders.

The simple original-support bound has median certified duration 7.63e-6, range
9.54e-7–6.10e-5, and median fourfold gain over the global controls. It remains
in results/summary.json as a preserved weaker branch.

The schedule-aware word result is:

| Original n | Certified / total | Median certified T | Range T | Median gain over global |
|---:|---:|---:|---:|---:|
|16|15/16|.001953125|.001953125–.00390625|128×|
|32|15/16|.0009765625|.00048828125–.0009765625|256×|
|64|15/16|.000244140625|.0001220703125–.00048828125|512×|

Overall median T=.0009765625, range .0001220703125–.00390625. Median duration gain
is 256× over the global certificate and 64× over the simple support bound;
individual gains over global range 128×–2048×. Family coverage is 10/12 irregular
hubs, 11/12 mixed hypergraphs, 12/12 random checks and 12/12 rewired bands.

These are the largest CERTIFIED MENU durations, not the largest true ordering
intervals or physical annealing times. The median guaranteed relative advantage
lower bound at those durations is only 7.55e-10 (range 2.12e-12–1.30e-7).
Absolute improvement multiplies this by unknown P0, which can itself be tiny.
The result does not assert a useful final success rate or moderate-time ranking.

Final saved word evaluations cost 2.82s for all 48 cases, median 34.9ms per case,
including exact inequality evaluation and serialization; scalar recurrences
are shared across cases of the same n. Host contention affects timings. The
first implementation attempt hit Python's integer-to-decimal serialization
limit; the record is preserved and exact fractions now use hexadecimal
numerator/denominator strings. No scientific criterion changed.

## Independent validation and provenance

An independent displacement-matrix Heisenberg Dyson implementation integrates
exact operator polynomials through order8 on 16 arbitrary frustrated 2–4-spin
models and arbitrary nonempty root events. All 64 even coefficients obey their
majorants, all 64 odd coefficients vanish, and every T² coefficient matches the
separate neighbor-energy formula. These examples validate the implementation;
ordinary-instance coverage comes from the full 48-input suite.

The parent separately enumerated every admissible D/E word and integrated its
scalar schedule polynomial through order12 for three (n,gE) pairs. All 18 exact
coefficients agree with the recurrence. The parent independently reviewed the
norm, termwise support counts, time orientation and outer-driver cancellation.
Cross-check evidence is in results/exact_word_checks.json and
results/independent_word_crosscheck.json; the latter references the independent
parent results/independent_word_majorants.json.

The proof requires tracking individual local-term branches. Applying its support
bound to the summed operator would be incorrect. The norm is used only with
proved Pauli translation/multiplication inequalities, not as a generic unitary
operator norm. The tail beyond computed order12 is retained exactly; it is not
replaced by an unproved all-orders mixed-word convergence assumption.

## Remaining gap and useful corollary

The theorem improves ACTUAL original-error finite-forward probability control
without an optimum oracle, across ordinary general H, with modest evaluation
cost. It does not settle useful moderate-time decoding performance. The bounds
still depend on original n, and their successful comparison is a matched
objective-amplification mechanism rather than arbitrary embedding superiority.

THEORY.md gives a corollary for different physical mappings: after averaging
nonroots, the second-order root polynomial can be split into a chosen objective
amplification and an affine-character residual whose pointwise lower bound is
cheap. Separate relative-event tails then permit a sufficient original-optimum
comparison across different roots/N. This is a theoretical route toward a
certified compact-mapping loop, not an evaluated compactness result here.

The parent is independently investigating exact T4 feasible-polynomial lower
bounds to replace the C4 triangle bound. That subsequent branch is not included
in this frozen extension's outcome numbers. No inference from mean cost,
conditional equilibrium, small-check success or positive curvature alone is
substituted for the original decoding event.
