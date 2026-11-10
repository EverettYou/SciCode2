# General sparse decoding compilation with a conditional annealing certificate

## Result and completion scope

This trial developed an executable, general sparse-matrix compiler, an explicit
polynomial construction of a valid ideal-Zephyr embedding in a declared size
regime, exact and certified floating coefficient allocation, and an efficient
finite-time quantum-dynamics certificate. The certificate gives an actual
ordering for one decoding pause protocol and proves that the ordering reverses
when the initial correction changes. These results meet the three stated
acceptance criteria within the explicitly allowed conditional theoretical
regime. They do **not** establish a universal ranking, complete forward-anneal
speedup, or performance on a noisy QPU.

The chosen contribution is the connection between a reusable general interface,
a deterministic construction with checkable witnesses, and an inexpensive
certificate of when an embedding prevents useful logical transitions. Local XOR
reductions and the published Zephyr clique construction are established tools;
no priority claim is made for those components. The finite-time proof and its
explicit constants are derived in full in [THEORY_CERTIFICATE.md](THEORY_CERTIFICATE.md).

The default explicit template was faster to query than the automatic reference
on all five matrix examples, but used more physical qubits. The usual chain
strengths gave **inconclusive** dynamical certificates for all 25 broad-example
mappings. The positive dynamical comparison is deliberately restricted to its
proved regime; these inconclusive outcomes are retained as part of the result.

## Assignment, resources, and scientific process

- Original shared trial start: **2026-10-07 19:55:30.405 UTC**, or 12:55:30.405 PDT.
- Total authorized budget: **7,200 elapsed seconds**; deadline
  **2026-10-07 21:55:30.405 UTC**. Preflight and reading count toward this budget.
- This scientific solver launched at **20:11:04.521 UTC**, leaving
  **104 minutes 25.884 seconds**. It did not restart or extend the deadline.
- Final measured finish and elapsed times are recorded in
  [results/scientific_completion.json](results/scientific_completion.json).
- Solver session: `01a117fd-a459-7621-b36c-1c49df7bcbbf`.
- The two scientific assistants worked on independent scopes: the pause proof
  and its validation (`01a117fe-0bfd-7be3-bceb-77efccafaa8b`), and the embedding,
  programming, and automatic-reference implementation
  (`01a117fe-343f-7a11-96fa-c440be5b285c`). The coordinator verified all three
  scientific sessions as Astra/ultra and owns the separate run/transcript records.

Only the frozen prompt, public references/software, and this run's newly created
materials were used scientifically. No sibling lab, author solution, or previous
trial was consulted. The coordinator prepared procedural provenance and later
ran read-only checks; it supplied no scientific hints during this solve.

Python 3.13.2 and the pinned packages in [requirements.txt](requirements.txt)
were already installed. No QPU credentials or QPU were used. The final experiment
summary records measured wall times and macOS process maximum RSS. These are
local observations, not calibrated cross-machine benchmarks. No unmeasured QPU
time, energy usage, or logical error rate is inferred.

## 1. Matrix-to-QUBO construction and proof

The input is a row-support representation of any binary matrix, the column
count `n`, a promised valid syndrome, and finite additive weights. Duplicate
sparse coordinates cancel over GF(2). Dependent and empty rows, isolated
columns, negative/zero weights, and columns incident on arbitrarily many checks
are supported. No graphlike or code-family assumption is made. The compiler
does not solve the decoding optimization as preprocessing.

Write `k=nnz(H)`, row degrees `d_r`, and choose

\[
 W=\sum_i|w_i|,\qquad \Lambda>W.
\]

For a row of degree at least three, sequentially compute prefix parity using
binary parity and carry variables, with local factors

\[
 \Lambda(a+b-p-2t)^2.
\]

This factor is zero exactly when `p=a XOR b` and `t=floor((a+b)/2)`;
otherwise it is at least `Lambda`. Terminate each row with the exact quadratic
two-input parity-violation indicator

\[
 \Lambda\{s+(1-2s)(a+b-2ab)\}.
\]

A degree-one row uses `Lambda(e_i-s)^2`. An empty row requires syndrome zero.
The full QUBO is the additive cost plus all these nonnegative integer-valued
penalties. Its projection is simply the first `n` error variables. For

\[
 a=2\sum_r(d_r-2)_+,\quad L=n+a,
\]

there are exactly `a` auxiliary variables and at most

\[
 E\leq\sum_{r:d_r\ge2}\{6(d_r-2)+1\}
\]

structural quadratic edges. Aggregation may remove interactions through exact
cancellation. The compiler records both this stable structural envelope and the
actual nonzero graph; embeddings of the envelope are also valid for the actual
graph. Syndrome changes can change interaction signs and cancellation, so reuse
is based on the envelope, not an unjustified fixed actual graph assumption.

**Fidelity.** Every feasible error pattern has a unique zero-penalty extension,
with QUBO energy equal to its cost. If any factor is violated, QUBO energy is at
least `C_min + Lambda`, where `C_min=sum_i min(0,w_i)`. Every feasible cost is at
most `C_max=sum_i max(0,w_i)`, and `C_max-C_min=W`. Thus every violating state
has energy greater than every feasible optimum. Exactly all minimum-cost
feasible error patterns occur as projected exact QUBO ground states. Negative
weights and ties do not change this argument. No hidden true error or observable
outcome is supplied to the decoder; the generated feasible patterns only
construct valid test syndromes. We do not report logical failure because no
observable map was evaluated.

The main implementation is [scripts/compiler.py](scripts/compiler.py). The
exact-only implementation [scripts/exact_pipeline.py](scripts/exact_pipeline.py)
uses rational arithmetic throughout and also handles cases where an otherwise
valid penalty or intermediate coefficient exceeds binary64 range. It accepts
all finite binary64 weights, including subnormal and very large values. The
mathematical construction holds for finite real weights under exact arithmetic;
the executable exact backend represents rational inputs.

**Numerical fidelity is checked, not assumed.** Binary64 input weights have
exact rational values. Let `delta_w` be the positive gcd lattice spacing of
those rational weights, or infinity if all weights vanish. Then

\[
 \delta_Q=\min(\Lambda-W,\delta_w)>0
\]

lower-bounds the energy difference between an exact ground state and every
nonoptimal QUBO assignment. If the sum of absolute nonconstant coefficient
rounding errors is `rho`, the sufficient condition `2 rho < delta_Q` ensures
every rounded QUBO ground state is an exact optimum. Exactly tied optima may be
split, which is allowed by the prompt. Exact coefficients and this certificate
are saved. The binary64 compiler rejects uncertified expansions; the exact
backend preserves the mathematical model. For example, naively adding a
weight `1e-300` to a penalty of one can erase the strict optimum. Our tests
confirm this unsafe floating expansion is rejected and its exact counterpart
remains faithful.

## 2. Embedding and programming

The target is ideal `Z_(g,4)`, generated by installed
`dwave_networkx.zephyr_graph` 0.8.18. The current `dwave.graphs` module was absent;
the legacy generator's exact nodes/edges, version, and parameters are saved in
[results/target_zephyr_g6.json](results/target_zephyr_g6.json). This is explicitly
an ideal architecture, not an actual working graph. No nonhardware edge is used.

For `g>=2`, the default constructs the published track minor of `K_(16g+1)`;
the complete template has `32g^2` qubits and maximum branch size `2g`.
The `g=1` special case explicitly contracts an interior `K_(8,8)` matching to
obtain `K_8`. These are sufficient capacities, not maximal-minor claims.
Construction and verification are `O(g^2)` on the bounded-degree ideal graph.
The exact coordinate construction and its validity proof are in
[TARGET_NOTES.md](TARGET_NOTES.md), based on Section 5.1 of the public
[Zephyr topology report](https://www.dwavequantum.com/media/2uznec4s/14-1056a-a_zephyr_topology_of_d-wave_quantum_processors.pdf).

Preprocessing stores a connected tree for every template branch and one target
contact edge for every pair. Any model with `L<=16g+1` is embedded by selecting
its branches. For each needed structural edge, mark its two contact endpoints;
prune unmarked leaves from each selected branch tree. Isolated variables retain
one physical qubit. The remaining branch is connected, nonempty, disjoint, and
contains every necessary contact. It cannot use more qubits than its unpruned
template branch. This is a deterministic guarantee of validity and resource
nonincrease relative to the fixed template, not a dynamics comparison.

The CLI can instead use a supplied target graph and the automatic minorminer
reference. An explicit-template capacity failure or failed heuristic search is
reported as unresolved, not as impossibility. Actual logical vertex or edge
counts exceeding corresponding target counts are certified necessary
obstructions. A damaged target must be revalidated; no ideal-template guarantee
is silently transferred to it.

For `e_i=(1+z_i)/2`, a QUBO with linear coefficients `a_i`, quadratic
coefficients `b_ij`, and constant `c_Q` becomes

\[
 J_{ij}=b_{ij}/4,\quad h_i=a_i/2+\sum_j b_{ij}/4,
 \quad c=c_Q+\sum_i a_i/2+\sum_{ij}b_{ij}/4.
\]

Allocate a field uniformly over each branch, put each logical coupling on one
available contact, and use ferromagnetic tree couplings `-K_i`. With

\[
 L_i=|h_i|+\sum_j|J_{ij}|,\qquad K_i=fL_i+\mu,
 \quad f\ge1,\ \mu>0,
\]

the physical offset `c + sum_(chain edges) K_i` makes every consistent raw
physical energy exactly equal to its logical QUBO energy. In a broken branch,
flipping a monochromatic tree component eliminates at least one wall, saving
at least `2K_i`, and changes nonchain energy by at most `2L_i`. Thus every
broken state admits a strict improvement. All physical ground states are
consistent and project onto minimum-cost corrections. A sufficient physical
nonoptimal gap before rescaling is

\[
 \delta_{\rm phys,raw}=\min\left(\delta_Q,
       2\min_{i:\,|C_i|>1}(K_i-L_i)\right),
\]

omitting the second minimum when all branches are singletons.

One positive scale `alpha` applies to every field, reduction coefficient, chain
coupling, and offset. It is the minimum of the applicable positive bounds from
individual h/J intervals and signed coupling-group sums, capped at one in the
reported comparisons. Our common illustrative
constraints are `h in [-4,4]`, `J in [-1,1]`, and group sums in `[-13,10]`;
these are parameters, not a device export. The Zephyr groups are produced by
`dwave.system.coupling_groups` and saved. Their relevance and signed-sum meaning
follow the [official solver-properties documentation](https://docs.dwavequantum.com/en/latest/quantum_research/solver_properties_all.html).

The exact-only allocator emits rational programmed coefficients and scales.
The practical allocator constructs an exact rational companion, compares every
actual binary64 coefficient against it, checks all ranges and group sums using
exact arithmetic, and certifies `2 rho_phys < alpha delta_phys,raw`. A downward
`nextafter` scale adjustment fixes representational boundary overshoot when
needed. Uncertified cases remain exact-only rather than receiving a false
floating-ground-state claim. Actual device precision/noise would require an
additional perturbation bound and is not assumed here.

## 3. Efficient annealing evaluation and a proved comparison

The physical model is the prompt's transverse-field Hamiltonian at a fixed
anneal coordinate, held constant for time `t`, with no bath or control noise and
`hbar=1`. All coefficients already include hardware scaling. Write

\[
 H=C+D-\Gamma\sum_qX_q,\quad
 C=\sum_{qr\in E_c}c_{qr}(1-Z_qZ_r),\quad
 \Gamma=A/2,\ c_{qr}=B|J^{\rm chain}_{qr}|/2.
\]

`D` contains the scaled diagonal problem terms, including reduction penalties.
Let `P` be the entire consistent-branch subspace, including every logical
assignment, not only ground states. Let `R` bound `||D||` by the sum of absolute
coefficients, `Delta` be twice the smallest weighted chain cut, `N_p` the
physical-qubit count, `n_1,n_2` the numbers of branches of sizes one and two,
and `M_p=N_p-n_1`. Define

\[
 g=\Delta-2R-\Gamma(N_p+n_1),\qquad
 b=\Gamma\sqrt{M_p+2n_2}.
\]

If `g>0`, the proved uniform finite-time bound is

\[
 \left\|(e^{-itH}-e^{-itPHP})P\right\|
 \leq \varepsilon(t)
 =\frac{2b}{g}+t\frac{b^2}{g}e^{2b/g}.
\]

The exact off-block norm is `b`, because two single-qubit flips return a chain
to its code space only by undoing one flip or flipping both sites of a size-two
branch. A Sylvester equation separates the two ordered spectral blocks; an
explicit anti-Hermitian conjugation cancels the first-order block coupling.
The bounded remainder and Duhamel's formula give the displayed constants. The
complete derivation is in the companion proof note and handles all degeneracy.

Within `P`, the first-order Hamiltonian is precisely
`D_logical - Gamma sum_(singleton i) X_i`. Diagonal events depending only on
nonsingleton logical variables therefore remain constant under that projected
evolution. Starting inside `P` with zero probability of such an event, its actual
probability after the hold is at most `min(1,epsilon^2)`. The event may include
all tied decoding optima and may extend to broken states through any fixed
recovery rule that agrees on consistent branches. This is a certificate of
logical-transition suppression, useful either to reject a repair mapping or to
certify retention. An initial leakage extension is stated in the proof note.

For tree branches, evaluation is linear in the programmed model size and uses
no spectral simulation. The implementation computes its algebraic gap with
exact rational arithmetic, bounds the square root and exponential upward, and
rounds reported upper bounds outward. For cyclic branches it uses a conservative
minimum-edge cut lower bound. If its conditions fail it returns **inconclusive**;
if the bound exceeds one it marks the probability guarantee as vacuous. Dense
matrix computations are used only in small validation examples.

**A strict decoding comparison.** Use `H=[1 1]`, `s=1`, and `w=(0,0)`.
The compiler can use `Lambda=0.0002`, producing Ising `J=0.0001` with both `01`
and `10` optimal. The common ideal Zephyr target contains path `[0,1,2,3]`.
The native mapping uses singletons `{1},{2}`; the encoded mapping uses
`{0,1},{2,3}` with chain strength one. Both use the same problem coefficient,
target, field/coupling/group constraints, `A=0.04`, `B=2`, and a constant hold

\[
 t=\frac{\pi}{2\sqrt{J^2+4\Gamma^2}}\simeq39.26978545,
 \qquad \Gamma=0.02.
\]

The problem-energy scale is intentionally common to both mappings. It is not
maximized separately for each candidate; doing so would define a different
comparison that is not covered by this ordering.

Starting in encoded error pattern `00`, the native exact success probability is

\[
 p_{\rm native}(t)=\frac{2\Gamma^2}{J^2+4\Gamma^2}
       \sin^2(t\sqrt{J^2+4\Gamma^2})
       \simeq0.4999968750.
\]

For the encoded mapping, the certificate gives `g=1.9198`, `b=0.02 sqrt(8)`,
and success **at most 0.016476688757570787**. Hence the native mapping is
strictly better for this repair protocol, without needing to simulate the
encoded evolution. A rational-only separation proof is also supplied, so this
strict comparison does not rest on unverified floating transcendental output.

Changing only the initial logical state to the optimal `01` reverses the
preference: encoded retention is **at least 0.9835233112424292**, while native
retention is approximately **0.5000031250**. This explicitly rules out an
initial-state-independent preference based only on physical size or chain
length in this model. Actual representative-readout simulation on the saved
Zephyr-path programs gives encoded repair about `0.0012909781` and retention
about `0.9987092787`; the theorem includes those recovered outcomes. The
separate abstract-path validation also reports strict consistent-state success,
which is a different measurement event.

The protocol starts at the specified classical encoded state **at the beginning
of the pause**. It excludes ramp/preparation times and makes no assertion that a
forward anneal prepares that state. Interpreting the hold as part of reverse
annealing requires separate ramp analysis. No larger-gap-implies-success
argument, thermal model, or classical simulated annealing surrogate is used.

## 4. Complexity, reuse, and finite target limits

Let `k=nnz(H)` after parity canonicalization, `k_in` be the number of supplied
coordinates before duplicate cancellation, `L=n+2 sum(d_r-2)_+`, `E=O(k)`, target size `V_T,E_T`, and
selected unpruned physical size `Q<=2gL`. Arithmetic-operation costs are:

| Stage | Time | Stored/output size |
|---|---:|---:|
| Sparse canonicalization and symbolic QUBO | `O(n+m+k_in log(1+k_in))` in this sorted Python implementation | `O(n+m+k_in)` |
| Explicit ideal-Zephyr target/template preprocessing | `O(g^2)=O(V_T+E_T)` | `O(g^2)` |
| Pruned template query | `O(L log L + Q + E)` | `O(Q+E)` |
| Independent embedding check | `O(V_T+E_T+L+E)` | linear in input/witness |
| Physical allocation, group scaling, exact rounding certificate | `O(E_T+Q+E)` arithmetic/traversal before canonical output sorting | `O(E_T+Q+E)` |
| Tree pause certificate | `O(Q+E)` arithmetic operations | linear input memory |
| Syndrome/weight numerical QUBO update | `O(n+m+k)` using cached canonical edge order | `O(n+m+k)` |

The symbolic-only allocator currently sorts target edges, adding
`O(E_T log E_T)`; canonical coefficient/witness sorting adds
`O((Q+E) log(Q+E))` in both output paths. These costs are included when timing
the actual implementation and do not change the polynomial guarantee.
For arbitrary labels, sorting costs are explicitly included. Rational bit costs
also depend on input bit lengths; they are not unit-cost real arithmetic. For
finite binary64 inputs, numerator/denominator sizes start bounded, and the
compiler's coefficient sizes grow logarithmically with accumulated term counts.
The exact-only backend also accepts rational weights, for which common-denominator
bit size must be charged. The exact transcendental enclosure uses a fixed
128-bit square-root enclosure and degree-24 exponential bound in its nonvacuous
regime. The dense scientific validation is exponential, up to `O(8^N_p)` time
and `O(4^N_p)` memory; it is not part of embedding selection.

For a fixed ideal target with `g>=2`, `L<=16g+1` is the deterministic sufficient
regime; the implemented `g=1` sufficient capacity is eight.
Choosing a larger `g=O(L)` gives `O(L^2)` worst-case hardware/preprocessing/output
overhead. This is a stated cost, not free extra connectivity or a claim that
sparsity always yields compact hardware. We never increase the target between
competing mappings in a comparison.

**Reuse.** Keep a fixed penalty envelope greater than every allowed weight L1
norm. Syndrome changes touch only the final factors, and weight changes touch
the original-variable linear terms. `update_instance` changes those numbers,
copies the sparse output, and updates its exact certificate. The structural
graph, branches, and target template remain reusable. The practical allocation
currently rescans the target/groups and recomputes fields, chain strengths, and
scale; this cost is measured and charged. Any successful automatic embedding
can also be cached across identical structural graphs. The template's advantage
is a guaranteed quick new query when the graph changes within capacity, not an
exclusive ability to cache an unchanged graph.

**Matrix/window changes.** The current implementation recompiles changed `H`
and obtains fresh pruned branches from the existing target template. It does not
claim stable auxiliary IDs under arbitrary column insertions or a fully local
dynamic-minor algorithm. A growing-window example adds two mechanisms and a
check, then verifies the new embedding. The matrix and complete supplied syndrome
are the available boundary information. If removed past mechanisms have known
contribution `b`, the new constraint must use `s_window XOR b`; if that
contribution is unknown it must remain represented or be modeled explicitly.
No causal decoder or use of unavailable future detector outcomes is asserted.

## 5. Reproducible evidence and unsuccessful approaches

[results/experiment_summary.json](results/experiment_summary.json) records five
matrix generators (seed 20261007), complete inputs, compilation/update timings,
25 mappings, physical sizes/scales, and certificate outcomes. All alternatives
use ideal `g=6,t=4`: **1,248 target qubits and 11,400 edges**. The explicit
template has capacity **97**. Automatic reference runs use minorminer 0.2.21,
seeds `11,29,47`, five-second limits and four tries.
This is the general minor-search reference described by
[Cai, Macready, and Roy](https://arxiv.org/abs/1406.2741).

| Sparse matrix | `n,m,k` | QUBO variables / structural edges | Full / pruned template qubits | Automatic qubits, three seeds |
|---|---:|---:|---:|---:|
| Banded three-body checks | 16,14,42 | 44 / 98 | 516 / 126 | 50,52,52 |
| Irregular hyperchecks | 18,10,44 | 66 / 154 | 780 / 287 | 88,86,90 |
| High-degree column, redundant row, isolated column | 18,12,44 | 62 / 140 | 732 / 264 | 82,82,82 |
| Graphlike incidence | 24,12,48 | 74 / 160 | 876 / 364 | 92,94,95 |
| Single degree-30 hypercheck | 30,1,30 | 86 / 169 | 1020 / 475 | 93,99,101 |

Recorded query times and times including independent validation are both in the
summary. Do not compare a template-only query time against an automatic search
that includes validation without that distinction. Coefficient allocation and
exact certification can dominate these small template-query times, and larger
template outputs cost more to program. Thus these measurements establish a
mapping-time/resource tradeoff, not universal end-to-end latency superiority.
Physical scales range from about `0.000363` to `0.002494` under the common
penalty envelope and programming limits; every chain/reduction term is counted.
In the final saved run, explicit-template preprocessing took 25.53 ms; pruned
queries including validation took 2.50–3.92 ms, versus automatic per-case median
times of 72.26–299.23 ms. Physical allocation plus exact certification for pruned
models took 74.66–92.45 ms, demonstrating why query speed alone is insufficient
to infer end-to-end latency. The five-case experiment took 9.15 seconds and its
process maximum RSS was 208,158,720 bytes on this macOS host.

Other saved evidence includes:

- [compiler_validation.json](results/compiler_validation.json): 38 primary
  exhaustive small cases, 32 syndrome updates, 100 chained exact-update checks,
  a cancelled-edge rounding regression, and 14,052 primary assignments;
  tests include negative/zero weights, tied optima, empty/dependent rows,
  isolated variables, and repeated sparse coordinates.
- [independent_witness_validation.json](results/independent_witness_validation.json):
  a standalone reader verifies all 25 saved embeddings, exact consistent-energy
  relations, independently recomputed ground-gap/rounding bounds, and signed
  physical ranges. It imports neither the compiler nor the embedding routine.
- [embed_checks.json](results/embed_checks.json): all 1,024 graphs on five
  vertices survive pruning; invalid-embedding cases are rejected; small
  physical ground states and exact numerical certificates are checked.
- [embed_explicit_tracks_checks.json](results/embed_explicit_tracks_checks.json):
  explicit complete minors checked for `g=1,2,3,4,6,8,12`.
- [theory_validation.json](results/theory_validation.json): 24 independently
  constructed 2–6-qubit Hamiltonians, four durations each, exact off-block norm,
  Sylvester/BCH residual, leakage, and uniform evolution-bound checks; plus
  cancellation, subnormal, and overflow boundary tests of the rigorous evaluator.
- [exact_and_pause_validation.json](results/exact_and_pause_validation.json):
  exact exhaustive cases with tiny, subnormal, and overflow-inducing weights,
  and the actual Zephyr-path repair/retention comparison.
- [cli_overflow_fallback.json](results/cli_overflow_fallback.json): an extreme
  finite-weight command-line instance overflows intermediate floating allocation
  and successfully falls back to a valid exact rational physical program.
- `input_*.json`, `model_*.json`, `witness_*.json`, `pause_*_witness.json`, and
  `exact_extreme_*.json`: complete independently inspectable input/model/program
  witnesses, with exact offsets, scale factors, and projections.

The native-clique pilot is retained in `results/native_template_pilot/` and in
the embedding subtask's separate nine-graph reference records. It is not silently
mixed with the final explicit-track results. Two initial native `g=1` calls
stalled and exited with code 137; the cause was not diagnosed, and no such job
remains active. An explicit construction replaces that dependency. Independent
review also caught unsafe coefficient cancellation/rounding and a floating
gap-sign error; both motivated the exact certificates now in the deliverable.
No failure was converted into a positive physics claim.

## 6. Reproduction and acceptance audit

Use Python 3.13 with [requirements.txt](requirements.txt). From this lab directory:

```sh
python3 scripts/verify_compiler.py
python3 scripts/embedding_checks.py --output results
python3 scripts/theory_checks.py --output results/theory_validation.json
python3 scripts/run_experiments.py
python3 scripts/verify_witnesses.py
python3 scripts/verify_exact_and_pause.py
python3 scripts/decode_compile.py --input results/input_irregular_hyperchecks.json --g 6 --output results/cli_example.json
```

The CLI accepts any row-support matrix and instance satisfying the documented
input promise. `--target` accepts a saved target and its coupling groups;
`--method automatic` selects the reference, and `--arithmetic exact` requests
rational programmed coefficients. An unrepresentable or uncertifiable floating
export falls back to an exact mathematical program with an explicit limitation.
The modules also expose the construction, update, verification, and evaluation
functions independently. No network request occurs during reproduction.

| Prompt acceptance criterion | Result |
|---|---|
| General matrix-to-model-to-embedding algorithm, fidelity, complexity, reuse/updates | Met: sparse XOR compiler; exact proof and rational witnesses; explicit Zephyr sufficient regime; faithful physical allocation/ranges; charged update and routing costs. Arbitrary-target fallback is heuristic and says so. |
| Efficient evaluation with substantive theoretical comparison or certified limitation | Met in the stated conditional hold regime: a polynomial certificate, full finite-time proof, a strict repair comparison, and an initial-state reversal. Ordinary-strength broad cases are honestly inconclusive. |
| Reproducible code/report, independent witnesses, diverse examples, automatic reference | Met: reusable CLI/modules, exact model/program/target witnesses, multiple structural families, independent checks, and seeded minorminer comparisons on the same target/ranges. |

**Scientific completion status: completed in the declared conditional scope.**
The remaining open work is sharper certificates that apply when the global
bandwidth condition fails, optimized contact/field allocation, compact mappings
with stronger efficiency guarantees, noisy/full-schedule analysis, real-device
precision and defects, and causal window integration. These are limitations and
extensions of the result, not claims already established by this trial.
