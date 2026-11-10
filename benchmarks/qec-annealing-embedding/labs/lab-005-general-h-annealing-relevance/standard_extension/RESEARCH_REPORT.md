# Standard-compiler mapping limitation and necessary-optimality extension

The original necessary-optimality relaxation improves many bounds but certifies
no standard-compiler mapping changes. Combining its strongest character
constraints with cheap feasible-cost witnesses proves three compact standard
mapping improvements on n16 inputs; all n32/64 cases remain inconclusive. The
proof concerns actual original-optimum finite-forward probability, not mean cost.
This is a limited constructive result with retained negative controls.

## Protocol and event

All24 saved standard-compiler inputs and their192 successful original automatic
candidates are retained. The compiler/globalM, programmed target/ranges, first
candidate baseline, actual programs, exact T4 polynomial and event tails are
unchanged. The primary duration is T=1/1024; all seven declared durations
1/64,...,1/4096 are reported. No new mapping, physical evolution or ordinary
optimum enumeration is performed.

The scored event is minimum-cost feasible ORIGINAL-error root readout, including
ties and arbitrary branch/auxiliary states. Standard-|+> physical initialization
and K(u)=−(1−u)ΣX+uE(Z) remain explicit. Each comparison is between candidates of
the SAME standard compiler. Baseline is FIRST automatic candidate, seed11 in
all24 pools; gains are not versus the previously compact alpha-guided mapping.

PROTOCOL.md froze cost-only, basis moves, basis+pairs and triangle-augmented
controls before outcomes. UPPER_BOUND_PROTOCOL.md separately froze the negative
curvature diagnostic after no positive certificates. WITNESS_PROTOCOL.md froze
a bounded feasible-cost search; its subsequent addenda record the parent's
zero-search particular-solution control and the required mechanism controls.
This is adaptive continuing research, not a blind/held-out test or difficulty
calibration. No frozen main/word/event/mapping snapshot is modified.

## Theory and implementation

THEORY.md proves necessary kernel-move inequalities, valid three-character
facets, and an exact dual box lower bound for unknown optimal-error characters.
HiGHS only proposes nonnegative multipliers. Exact Fraction evaluation charges
all residual coefficients and does not rely on numerical LP optimality or
primal feasibility. Every nonzero multiplier and exact bound is saved.

The affine-cost upper bound U* is first the parent's moment bound. The particular
solution and searched feasible error can tighten U* because C* cannot exceed
ANY feasible cost. Neither is called optimum. The searched witness uses16 fixed
kernel starts and basis/pair best-improving descent capped at4n moves/start.
No planted error or ordinary reference optimum enters construction.

The implementation supports finite signed binary64 weights exactly via Fraction
and an LCM denominator, rather than assuming integer-quarter weights. Ordinary
weights have small dyadic precision; timings do not guarantee similar cost at
arbitrary bit precision. The theoretical inequalities apply to arbitrary finite
signed costs and general binary H with feasible syndrome.

## All ordinary controls and outcomes

Every method retains all24 matrices, every192 candidate and every duration.
The following primary-T outcomes also hold at every declared duration:

| Feasible-cost upper bound | Character constraints | Certified changes /24 | Strict smaller | Mean qubit reduction across24 |
|---|---|---:|---:|---:|
| Parent moment bound | Cost-only |0|0|0|
| Parent moment bound | Basis moves |0|0|0|
| Parent moment bound | Basis+pairs |0|0|0|
| Parent moment bound | Basis+pairs+triangles |0|0|0|
| Particular cost | Cost-only |0|0|0|
| Particular cost | Basis or basis+pairs |0|0|0|
| Particular cost | Basis+pairs+triangles |1|1|.4032%|
| Searched witness cost | Cost-only |0|0|0|
| Searched witness cost | Basis or basis+pairs |0|0|0|
| Searched witness cost | Basis+pairs+triangles |3|3|.6563%|

The initial triangle relaxation strengthens164/192 moment-based lower bounds by
more than1e-10 (maximum improvement .5207), but none becomes positive. Thus this
negative result is not merely an unchanged calculation. The strongest relaxation
has at most86 variables/732 inequalities. Applying it to minus the difference
polynomial gives no negative upper-curvature certificate, including all94
nonbaseline candidates with N≤FIRST. Neither favorable nor adverse standard
ordering follows from the original moment-only relaxation.

The searched witness tightens U* onall24 inputs, costs median14.0ms,total1.39s,
and evaluates715,220 kernel moves. None of its384 starts hits the accepted-move
cap. The already computed particular solution also tightens U* onall24, with
median.142ms,total5.72ms additional exact-cost/syndrome checks and zero search.
Its proposal was a subsequent parent collaboration, documented before outcomes.

The three positive selected comparisons, all at original n16, are:

| Input | FIRST seed / qubits | Selected seed / qubits | Relative optimum advantage lower at T1/1024 |
|---|---:|---:|---:|
|mixed_hypergraph_n16_s8807|11 /111|173 /110|4.44e-8|
|rewired_band_n16_s8807|11 /58|211 /55|1.25e-8|
|rewired_band_n16_s9901|11 /62|47 /56|5.56e-8|

The particular-only triangle control obtains the final row. Search adds the
first two. None of the evaluated cost-only/basis/pair controls obtains them,
so stronger upper witnesses alone do not explain the combined certificates.
This does not assert that these constraints are logically necessary for every
possible proof method. All16 standard n32/64 models remain inconclusive.

Positive lower bounds refer to [P_selected(opt)−P_FIRST(opt)]/P0. P0 is unknown
uniform optimum mass and may be small. These are correct early-time conditional
regime results; they neither establish a useful success rate nor a moderate-time
ranking. The larger balanced compiler is not used as a hidden resource subsidy.

## Costs, validation and provenance

Initial24-pool three-method evaluation takes3.76s; numerical LP medians are
approximately1–2ms/candidate. The negative diagnostic takes4.08s. Particular+
strongest-LP and searched-witness+strongest-LP runs take2.52s and3.30s respectively.
Both tightened-upper cost-only controls together take1.99s. The complete nested
controls with particular/search uppers take4.20s/4.19s. These are incremental
costs: parent GF2 preprocessing, automatic embedding, physical programming and
exact q2/q4/tail computations are inherited and not included again. The parent
records those costs separately; this is not a standalone end-to-end timing.

Sixty arbitrary small binary matrices with dependent rows and signed/zero
weights supply independent validation, not ordinary selection. Exact reference
optimum enumeration checks75 tied optimal patterns,2,084 necessary inequalities,
480 exact lower/upper dual bounds, and60 feasible-search witnesses. All pass.
The ordinary selector never enumerates its optimum set. Parent independently
reviewed the kernel inequality sign, triangle facets and exact dual proof.

The root-only q2 extractor is independently checked against all192 saved exact
parent cost-Lagrange values before any bound change. Exact witnesses include
nonzero dual multipliers, source hashes, feasible original-error masks, descent
counts, cost bounds and all duration outcomes. One initial reader mismatch with
the parent's migrated Fraction-hex schema is retained; it occurred before
outcome collection and did not change the scientific criterion.

## Interpretation

This branch provides a modest correct standard-compiler finite-event compact
mapping result, and stronger evidence of the remaining limitation: most ordinary
standard inputs, including all larger tested ones, remain unresolved despite
substantially stronger inexpensive bounds. It does not prove that no useful
standard mapping exists, that true candidate order is adverse, or that the
relaxation is tight. Cheap feasible witnesses are approximate cost searches and
are charged as such. No optimum oracle or special-code assumption closes the gap.

An ANY-conditional-finite-event benchmark cannot dismiss these correct early-time
certificates merely because their regime is conservative. Practical/informative
regime and broad larger-input coverage remain distinct scientific questions.
No model difficulty or organizer acceptance conclusion is inferred here.

A final exact replay, without any LP or optimum solve, verifies1,728 saved dual
certificates,12,096 event-gap updates and all48 ordinary feasible witnesses
(particular plus searched). See results/exact_audit.json. This checks all initial
and tightened-upper nested-control witnesses, including negative outcomes.
