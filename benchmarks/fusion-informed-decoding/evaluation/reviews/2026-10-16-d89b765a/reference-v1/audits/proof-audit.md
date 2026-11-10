# R3 large-N theorems and proof details: independent aspect-by-aspect review

Date: 2026-10-16. This file reviews the existing 7 scientific submissions without changing the task, launching models, or resampling phase diagrams.
The source task is `/Users/home/Downloads/20261014-102308_d89b765a/prompt.md`.
The original R3 requirement (line 143) is an explicit integer N0 and a proof of decodability for every N≥N0 and every p∈[0,1].
A smaller valid N0 is stronger, but the task does not require the minimum N0, a particular auxiliary decoder, or a particular 2×2 matrix method.

## Conclusions and scoring approach

The scientific conclusions of all 7 large-N theorems are supported by mathematical review and existing independent arithmetic checks.
GPT 01/02 achieve the strongest N0=13, GPT 03 gives 14, the three Opus runs give 15, and Fable 03 gives 19.
Different N0 values represent sufficient conditions of different strength, not contradictions.

This review separates “proof evidence present in the original submission” from “scientific conclusions supported after additional reviewer checks.”
In particular, Opus 03 originally obtained its final full-p maximum only from a grid and floating-point optimization; an existing review subsequently supplied
rational interval coverage. This supports the theorem but cannot retroactively count as a rigorous arithmetic certificate submitted by the original agent.
Fable’s memory-22 proof with about five million states was not rebuilt in this review; its λ=1.876764 exceeds
the known honeycomb connective constant, so a published theorem independently supports the same path-count bound.

The following is a recommended local post-hoc R3 rubric, out of 20; it is not the official frozen original evaluator.

| Aspect | Points | Full-credit condition |
|---|---:|---|
| C1 Explicit N0 and quantifier scope | 3 | Integer N0; explicit coverage of every N≥N0 and every p; treatment of p=0,1. |
| C2 Legitimate decoder or equivalent Bayes argument; failure witness | 5 | An auxiliary rule using only observations, or a valid posterior/polymer proof; correct difference components, spanning paths, local feasibility, and global selection conditions. |
| C3 Correlations and single-path probability | 6 | A valid exponential upper bound handling shared orientations and off-path chords; valid alternatives include garbling, matrix norms, Bhattacharyya, bipartite Cauchy–Schwarz, and cycle expansion. |
| C4 Size limit and uniform-constant certificate | 4 | Path count/minimum length/strict growth factor<1/geometric series; an auditable analytic or certified numerical bound on the maximum over all p. |
| C5 Scope of conclusions | 2 | Sufficient N0 is not claimed minimal; exponential upper bounds are not claimed as true critical exponents or phase boundaries; risk comparisons concern average Bayes risk. |

| Run | N0 | C1 /3 | C2 /5 | C3 /6 | C4 /4 | C5 /2 | Recommended original-submission score | Correctness score including existing independent checks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Fable 03 | 19 | 3 | 5 | 6 | 3.5 | 2 | 19.5 | 20 |
| Opus 01 | 15 | 3 | 5 | 6 | 4 | 2 | 20 | 20 |
| Opus 02 | 15 | 3 | 5 | 6 | 4 | 2 | 20 | 20 |
| Opus 03 | 15 | 3 | 5 | 6 | 3 | 2 | 19 | 20 |
| GPT 01 | 13 | 3 | 5 | 6 | 4 | 2 | 20 | 20 |
| GPT 02 | 13 | 3 | 5 | 6 | 4 | 2 | 20 | 20 |
| GPT 03 | 14 | 3 | 5 | 6 | 4 | 2 | 20 | 20 |

Smaller N0 is separately reported as result strength, avoiding classifying a correct conservative proof satisfying R3 as a failure.
If an aggregate rubric evaluates only “whether the scientific conclusion holds after review,” all 7 may receive 20/20,
but diagnoses of insufficient original arithmetic evidence should remain explicit.

## Evidence locations for each proof

All line numbers are 1-based in the original downloaded files and can be used directly during review. The external root directory is abbreviated RAW.

### Fable 03

`RAW/anthropic__claude-fable-5-1/run_03/docs/theory.md`:

- 3–11: complete microscopic variables x and additional orientation ε; edge prior 1-p,p/2,p/2; conditionally independent readouts.
- 13–16: the average failure probability of any observation-based decoder is at least the optimal Bayes risk.
- 113–143: same-parity arrival ambiguities and random degradation to an orientation-blind noisy-degree channel.
- 183–202: MAP configuration on the degraded channel; differences are simple paths/cycles; feasible component flips and likelihood ratio≥1.
- 204–222: square-root likelihood/Bhattacharyya; different path patterns; separate averaging of third edges used once or chords used twice; occupancy matrix `[[β,1],[1,β]]`.
- 224–227: minimum length 2L-1, L starting points, and a geometric series.
- 237–247: memory-22 path-growth bound and final N0=19; `report.md:279–284` gives the final values consistently.
- Original lines 179–181 retain the earlier memory-20→N0=20 discussion, but final lines 244–247 explicitly use memory-22→19; this is not a conflict in the final answer.

The original h19 value is floating-point output, and the large memory-22 Collatz–Wielandt validation was not rebuilt here,
so C4 retains a half-point documentation/certification gap. Existing rational coverage in `proof-certificate-checks.json` gives
`(λρ)^2≤0.9978532029240675<1`; the path-count argument using λ>exact μ can independently replace the large matrix.

### Opus 01

`RAW/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md`:

- 3–7: binary x is separated from orientation σ; conditionally independent readouts.
- 9–16, 66–75: average-risk data processing; local degree garbling based only on visible irreps and private randomness.
- 95–109: theorem N0=15, legitimate MAP-configuration decoder, degree-0/2 differences, spanning components, and their likelihood ratio≥1.
- 111–120: Bhattacharyya summation over all occupancy patterns; chords shared by two vertices cannot be averaged vertex by vertex; an explicit occupancy transfer matrix.
- 122–130: μ+δ supplies a uniform finite prefactor rather than assuming it at exact μ; geometric series; the original rational interval cover.
- 132–135: 15 is an upper bound from this method and orientations are deliberately discarded; numerical all-p behavior at N≥3 is separate from the theorem.

Existing check: squared uniform path factor≤0.9987983641909155.

### Opus 02

`RAW/anthropic__claude-opus-5-5/run_02/report/02_exact_structure.md:3–10,35–58` and
`report/03_large_N.md:3–33`:

- exact_structure 39–47: legitimate degree garbling on visible readouts; the analytic construction for every N≥7 suffices for N0=15.
- large_N 8–17: difference components and feasibility of individual components; an injective polymer/posterior path bound directly controls Bayes risk, without separately constructing GPT1’s auxiliary decoder.
- 19–24: general-θ readout overlap; occupancy-bit weights; Cauchy–Schwarz for chords and Jensen for single endpoints; the matrix is explicit in exact_structure 55–58.
- 26–33: SAW counting, exponential decay, a 120-bit interval-arithmetic certificate, and monotonicity in N.
- 39–40: the theorem is separated from numerical behavior at smaller N.

The proof does not “calculate independent probabilities for all hidden vertices.” Through fractional moments of posterior ratios,
it jointly handles all readouts and path patterns. An existing check may use the simpler uniform θ=1/2 bound, still giving
a squared factor≤0.9987983641909155<1.

### Opus 03

`RAW/anthropic__claude-opus-5-5/run_03/docs/sec_model.md:10–26` and `docs/proofs.md:134–223`:

- model 10–12: three-state microscopic y and the endpoint receiving V; model 25–26: binary correction and logical success.
- proofs 138–161: an explicit randomized degree-garbling kernel; orientation summation genuinely disappears because the degraded local law depends only on n.
- 163–179: MAP-configuration auxiliary decoder, degree-0/2 components, and the likelihood selection condition.
- 181–197: Bhattacharyya, occupancy matrices sharing an eigenvector, summing path patterns first and then averaging grouped third-edge occurrences.
- 199–211: μ+δ, geometric series, N0=15, and the numerical maximum.
- 218–223: discarded information, proved values, and smaller-N numerical extrapolation are separated.

**Original arithmetic gap:** `scripts/r3_bound.py:31–37` uses a 200001-point grid plus bounded scalar
floating-point optimization to find the maximum. It does not certify the full-p maximum as a rigorous upper bound, so C4=3/4.
An existing review subsequently used a rational interval cover to verify `(μρ)^2≤0.9967961575574339<1`;
with this numerical certification gap closed, the R3 scientific conclusion holds.

### GPT 01

`RAW/openai__gpt-6-astra/run_01/proofs.md`:

- 7–18: degree0/2→simple components, minimum length; a general actual correction need not reproduce charge/irrep observations.
- 70–77: three-state microscopic t is separated from binary occupancy; endpoint signs of shared edges are retained.
- 104–138: coarse constraint M (originally m); only 11 vertices must hide; weighted auxiliary decoder; component flips and square-root selection inequality; whole-path occupancy-pattern summation; optimal average risk≤auxiliary risk.
- 142–168: true hiding conditions, arrow matrices, and endpoint normalization; matrix norms 1/(2N²), φ/N².
- 170–192: parity-dependent τ0,τ1; third edges used once or twice; rigorous chord-correlation treatment.
- 194–208: three-part rational full-p certificate, N≥13, endpoints, and explicit sufficiency rather than minimality.
- 210–212: the special N=4 pure-triple irrep and the statement that sufficient-bound roots are not actual phase boundaries.

The two 2×2 objects have different states: the orientation matrix has latent arrow states ±; the binary-sequence summation matrix
has occupancy states 0/1. Occupancy summation is expressed by formulas at lines 125–129 without separately drawing the matrix.
Existing checks give growth-factor bounds 0.9991283076923076, 0.9987422178461538, and 0.9678148006153846 on the three p segments.

### GPT 02

`RAW/openai__gpt-6-astra/run_02/proofs.md:130–219` and `large_N_13.md`:

- proofs 130–147: M is explicitly the smallest same-parity count compatible with the observation; min/max-cardinality auxiliary decoders; hiding only at 11; the half-path occupancy condition.
- 149–173: path reference direction for latent arrows, arrivals u_i,-u_{i+1}, F/2, endpoint summation, matrix norms, and a table for different N.
- 175–188: off-path chords, at most two uses, and Cauchy–Schwarz.
- 190–215: Chernoff parameter and p-dependent selection of min/max decoder; occupancy-matrix states and endpoint prefactors; the exact geometric-series risk bound.
- 219: sufficiency only, without treating equality as a phase boundary.
- large_N_13 26–60: positive-cycle expansion handles residual orientation/chord correlations rather than ignoring cycles.
- 62–130: Ihara–Bass, 100 exact triangular-lattice return-walk terms and an analytic tail bound; cycle factor<51/50.
- 132–173: Δ_N(p), uniform rational certificate, and full-p N0=13.
- 175–179: microscopic hexagon-enumeration validation at three cases, distinguished from the actual proof.

Existing checks: growth factor≤0.9998879761451236<1; the three normalized 31104-state cycle-expansion examples agree with direct enumeration.

### GPT 03

`RAW/openai__gpt-6-astra/run_03/proofs.md`:

- 3–6: three-state microscopic variables and additional orientations; conditionally independent readouts.
- 8–34: binary differences, degree0/2, simple paths, minimum length, and legitimate logical representatives.
- 53–55: risk ordering concerns average Bayes risk, not smaller error for every individual fine record.
- 189–225: M (originally h) is observation-derived; n∈{M,M+2}; minimum cardinality; at least half the path active; only 11 vertices must hide.
- 227–252: bipartite grouping, with disjoint microscopic edge variables within each group; second-moment Cauchy–Schwarz, explicitly including chords.
- 253–275: Bernoulli occupancy-pattern summation, Chernoff, and occupancy matrix A_z; no arrow matrix is used, without discarding its correlations.
- 278–315: rational full-p certificate, separate high-p treatment, endpoints, μ+ε, sufficiency rather than minimality, and potentially impractical proof bounds at simulation scales.

Existing check: growth factor≤0.9999497492286578<1.

## Diagnostic coverage of discussion details

E=explicit in the original; I=inferable but not separately explained; M=explanation missing; X=error; NA=this proof legitimately avoids the method.
This table assesses exposition/coverage; **it does not turn every explanatory detail into a new mandatory original-task requirement**.
Binary edge occupancy and latent arrows are correctly modeled in all runs, but not every submission gives readers local four-panel diagrams.

| Diagnostic | F03 | O01 | O02 | O03 | G01 | G02 | G03 |
|---|---|---|---|---|---|---|---|
| Binary x/c occupancy differs from additional latent orientation | E | E | E | E | E | E | E |
| Latent orientations are not given to the decoder; conditioning is only for probability calculation | I | E | E | E | E | E | E |
| Difference degree0/2→simple components→spanning path | E | E | E | E | E | E | E |
| M is the minimum same-parity arrival count allowed by the current local observation | I | I | I | I | E | E | E |
| Not every path vertex must hide; 11 differs from mixed patterns | I | E | E | E | E | E | E |
| Hiding is necessary, not sufficient, and applies to the constructed feasible decoder/channel | E | E | E | E | E | E | E |
| Global decoder selection/likelihood ratio/Chernoff cannot be omitted | E | E | E | E | E | E | E |
| Arrow-matrix ± states and endpoint 1/2 weights | NA | NA | NA | NA | E | E | NA |
| Occupancy-matrix 0/1 states and pattern summation | E | E | E | E | I | E | E |
| Correlations from shared off-path third edges/chords | E | E | E | E | E | E | E |
| optimal≤aux compares average risks, not samplewise failure-event inclusion | E | E | E | E | E | E | E |
| Scaling is an exponential upper bound, not a true critical exponent/phase boundary | E | E | E | E | E | E | E |
| Diagrams of all four arrow-matrix elements and notation without conflicts | M | M | M | M | M | M | M |

The final item is a teaching requirement arising from the current user’s follow-up; the original task did not request illustrations.
The earlier chat diagram used a,b both for matrix indices and arrival counts, creating a notation conflict in this explanation;
this cannot retroactively become a scientific error in the runs. The standard answer consistently uses n_V,n_barV and α,β∈{+,-}.

## Recommended strongest valid reference-proof outline (N0=13)

Use GPT 01’s route, which is shorter than GPT 02’s cycle expansion and more direct for explaining shared arrows.

1. Microscopic states consist of binary X and independent latent orientations; correction C remains binary. Define
   M_v=min{n:same syndrome parity and positive local-readout probability for some composition}.
   For O2,N≥13, M=0/1 corresponds respectively to an even singlet/odd fundamental (or conjugate); otherwise M=s+2. True n∈{M,M+2}.
2. Among binary configurations satisfying n_C(v)∈{M_v,M_v+2}, maximize
   W(C)=p^{|C|}(1-p)^{|E|-|C|} Π_{v:n_C=M_v+2} τ_{M_v},
   with τ0=1/(2N²), τ1=φ/N², φ=(1+√5)/2. True X is feasible, so the rule exists and uses only visible observations.
3. Auxiliary failure yields a spanning component P of X⊕C with d≥2L-1. Flipping this complete component remains feasible.
   Every true 11 vertex requires M=n_X-2; 01/10 preserve counts; 00 adds a pair but requires no true hiding.
   Maximization gives a path likelihood/score ratio≥1; retaining only hiding events is insufficient.
4. Fix off-path microscopic states and sum latent σ over each continuous run of active path edges.
   For inactive/active third edges, the operator norms of F/2 are τ0/τ1; endpoint vectors are 1/√2 with norm one.
   Do not assume readouts independent when conditioning only on X. The square-root selection inequality combines hiding factors
   and score ratios at true 11 vertices, and score ratios at true 00 vertices, into √τ_h.
5. Off-path edges may touch two path vertices. Average occurrences by physical edge: for j=1,2 uses,
   (1-p)τ0^{j/2}+pτ1^{j/2}≤[(1-p)τ0+pτ1]^{j/2}.
   Thus an effective weight for every equal adjacent occupancy pair is
   η_N(p)=sqrt((1-p)/2+pφ)/N.
6. Sum whole-path occupancy patterns with K=[[η,1],[1,η]]:
   1ᵀK^{d-1}1=2(1+η)^{d-1}, giving fixed-path witness probability≤
   2[p(1-p)]^{d/2}(1+η)^{d-1}.
7. SAW count≤L C_ε(μ+ε)^d, with μ=sqrt(2+√2). At N=13, a three-part rational certificate gives
   μ sqrt(p(1-p))(1+η)<1 with a strict margin across the entire p interval; the factor decreases for larger N.
   Therefore auxiliary average failure≤constant·L r^{2L-1}/(1-r)→0, and optimal average Bayes risk is smaller.
   At p=0,1 use the known binary error directly; risk is zero.

Alternative reference proofs that should also be accepted:

- N0=15: randomly degrade O2 to an n-only degree channel, with misreport probabilities 2→0 of 1/N² and 3→1 of 2/N²;
  the kernel depends only on visible irreps. Use the MAP-configuration square-root likelihood ratio and
  Bhattacharyya overlap, group by third edges/chords, obtain
  ρ=sqrt(p(1-p))(1+sqrt(1+p)/N), and supply a rigorous full-p certificate.
- N0=14: coarse counts from original irreps, minimum cardinality, and hiding at true 11 vertices; apply
  Cauchy–Schwarz to the two honeycomb colors, bounding joint hiding by [sqrt((1+5p)/2)/N²]^{#11}; use the Chernoff occupancy matrix and an analytic certificate.
- N0=13: GPT 02’s positive-cycle expansion / Ihara–Bass / analytic tail is also a valid route.
- Any larger explicit N0, such as19, also satisfies R3 if proved valid. Scientific correctness cannot be penalized for not reproducing the author’s tightest method.

## Uniform auditable evidence

`../.. /results/proof-certificate-checks.json` (the actual path is this review’s results/ directory) records:

| Proof | Rigorous bound from existing independent checks |
|---|---|
| Fable N19 | squared growth ≤0.9978532029240675 |
| Opus 01/02 N15 | squared growth ≤0.9987983641909155 |
| Opus 03 N15 | squared growth ≤0.9967961575574339 |
| GPT 01 N13 | growth <0.9991283076923076 (worst segment) |
| GPT 02 N13 | growth <0.9998879761451236 |
| GPT 03 N14 | growth <0.9999497492286578 |

Squared and unsquared values cannot be directly used to rank proofs; compare valid N0, scope, and proof transparency first.
This is mathematical review and arithmetic checking, not formal proof-assistant verification.
