# Exact-posterior, decoder and reproducibility audit

Date: 2026-10-16. Inputs: the seven scientific submissions in the supplied `20261014-102308_d89b765a` archive. Fable01 and Fable02 ended in API output-limit errors and have no scientific deliverable; their scientific scores are **NA**, not zero.

This is a newly defined, post-hoc weighted rubric, with **D=20 and E=15 points**. It is not the organizer's original frozen grading scale. It scores deliverable compliance and scientific evidence separately: an `answers.json` that contains all 21 entries receives packaging credit even if an entry's scientific conclusion is unsupported. It does not reward a prescribed algorithm, a larger study, or a more optimistic phase assignment.

## Reference answer for R4 and the decoder interface

Give each edge a microstate \(y_e\in\{0,+,-\}\), with weights \(w(0)=1-p\), \(w(+)=w(-)=p/2\). The sign identifies which endpoint receives \(V\); the opposite endpoint receives \(\bar V\). Set \(x_e=1_{y_e\ne0}\). The same edge's sign is shared by its two endpoints; it cannot be redrawn independently for adjacent vertices. A valid alternative may analytically marginalize these signs, provided it preserves their joint endpoint dependence.

For a detector, define its local observed-record likelihood
\[
L_{0,v}=1_{s_v=(a_v+b_v)\bmod2},\qquad
L_{1,v}=L_{0,v}\,1_{k_v=(a_v-b_v)\bmod N},
\]
\[
L_{2,v}=L_{0,v}\,\frac{m_{R_v}(a_v,b_v)\dim R_v}{N^{a_v+b_v}}.
\]
Then the sector partition functions are
\[
Z_\lambda(o)=\sum_{y:\,\ell(x(y))=\lambda}
\prod_e w(y_e)\prod_v L_{r,v}(o_v\mid a_v(y),b_v(y)).
\]
The posterior is \(Z_0/(Z_0+Z_1)\). Computing a MAP microstate, normalizing local likelihoods separately, or taking a product of independent vertex posteriors does **not** evaluate this sum. After choosing the larger sector, construct any binary correction with \(Hc=s\) and the chosen \(\ell(c)\). The correction does not have to be a globally charge/irrep-compatible putative error microstate; it is a recovery action, and the task defines success by syndrome and logical parity.

One satisfactory exact algorithm is a frontier/transfer-matrix contraction with three states per crossing edge and an explicit logical-parity bit. It keeps all states, sums local factors, rescales by a common positive factor, and closes unmeasured boundaries correctly. Working storage and time grow exponentially in width \(L\), not in the number of edges \(O(L^2)\). Exact generic tensor elimination, direct enumeration at these sizes, or a different certified algorithm is equally acceptable. The benchmark does not demand a free-fermion map. To satisfy the declared positive-probability domain in floating arithmetic, local underflow must be handled by log weights, sufficiently wide exponents, exact/Decimal arithmetic or rigorous bounds; global rescaling alone cannot revive a frontier contribution already rounded to zero.

All seven submissions implement this finite tensor-sum structure. Their main exact solvers are transfer matrices / frontier contractions, which are tensor-network contractions. **None requires a free-fermion solution.** Opus01/02/03 additionally use truncated boundary-MPS for larger phase-evidence patches. This does not make their mandatory \(L\le4\) R4 routines approximate. Opus02's public API itself switches to MPS above \(L=9\) (`hexsym/api.py:15,87-100`); its broad README claim of no truncation should therefore be read as applying to the required small-size range, rather than all `L`.

## What existing independent checks establish

The review independently constructed geometry, irrep probabilities, a physical-record generator and generic-einsum elimination. Twenty-one literal microscopic enumerations at \(L=2\) validated the oracle, maximum discrepancy \(8.67\times10^{-19}\). For each submission, **210/210** ordinary posterior cases and **210/210** corrections pass. These comprise **140 R4 O1/O2 cases and 70 O0 controls**, not 210 required R4 cases. The largest cross-run ordinary posterior discrepancy is \(1.033\times10^{-14}\), below \(10^{-9}\). The correction check explicitly verifies canonical valid edges, recorded syndrome and the reference MAP logical sector; it does not incorrectly require edgewise recovery of the true error.

The additional **18** positive-probability stress records force all edges active, so their true posterior is known analytically. At \(p=10^{-180},10^{-310}\) and the smallest positive binary64 value, GPT01/02/03 pass 18/18; Fable03 and Opus01/02/03 pass 0/18 on the reviewer's macOS environment. This diagnoses a full-domain numerical limitation, not scientific failure of the statistical model. In particular, macOS NumPy 1.26.4 `longdouble` has only binary64 exponent range, unlike the original Linux NumPy 2.1.3 environment; the Opus02 result must carry that qualification. Its `p/2` is computed as Python float before casting to longdouble (`hexsym/api.py:45`), so the smallest-positive-float issue persists across platforms.

Small-size independent checks verify a method's implementation on the tested domain. They do **not** make a larger-chi MPS contraction a gold reference for all larger sizes. Agreement between chi and 2chi, small discarded weight or agreement between posterior-risk and hard-failure means is useful convergence evidence, but alone does not bound common bias or prove that approximation cannot alter an R1 assignment. This limitation should be scored in the R1 approximation-uncertainty item, not charged again against the exact small-size solver.

## Weighted scores

D1: joint microstate posterior /6; D2: exact algorithm and complexity /3; D3: independent validation /5; D4: numerical range /3; D5: valid logical correction /3. E1: answer schema /4; E2: report, proof and figure /3; E3: code, environment and commands /3; E4: raw evidence, seeds, stopping, resources and unconditional accounting /5.

For D4, ordinary correct arithmetic and regular rescaling receive 1 point; robust preservation of extreme positive-probability records receives the other 2. Stress tests are explicitly labelled new reviewer diagnostics, not a preexisting hidden official test. A score is supported by finite test evidence and source inspection; none asserts an exhaustive proof of all inputs.

| Run | D1 | D2 | D3 | D4 | D5 | E1 | E2 | E3 | E4 | D+E /35 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fable03 | 6 | 3 | 5 | 1 | 3 | 4 | 3 | 3 | 4 | 32 |
| Opus01 | 6 | 3 | 5 | 1 | 3 | 4 | 3 | 3 | 4.5 | 32.5 |
| Opus02 | 6 | 3 | 5 | 1 | 3 | 4 | 3 | 3 | 4.5 | 32.5 |
| Opus03 | 6 | 3 | 5 | 1 | 3 | 4 | 3 | 3 | 4.5 | 32.5 |
| GPT01 | 6 | 3 | 5 | 3 | 3 | 4 | 3 | 3 | 5 | 35 |
| GPT02 | 6 | 3 | 5 | 3 | 3 | 4 | 3 | 3 | 5 | 35 |
| GPT03 | 6 | 3 | 5 | 3 | 3 | 4 | 3 | 3 | 5 | 35 |

## Unconditional-denominator detail discovered in this audit

The problem explicitly says an exception or invalid correction is a failure. Retaining an attempt in the denominator is necessary, but insufficient if the attempt receives only half the required loss.

* **Fable03:** `src/run_mc.py:56-58` substitutes posterior 0.5 on exception. `analysis/aggregate.py:28-29` consequently gives both posterior loss and hard tie loss 0.5. It saves a count of exceptions, but not a per-attempt exception mask. The existing `data/summary.csv` sums to zero exceptions, so this is a **latent accounting defect**, not evidence that an archived point was changed. E4=4/5.
* **Opus01:** `src/mc.py:146-148,257-259` assigns `r=.5,f=1` on exception. The hard-failure column correctly counts failure, but the reported posterior-min estimator is not conservative under the stipulated administrative loss. `report.md:228` documents two actual exceptions, a tiny effect that cannot explain the major phase disagreement. E4=4.5/5.
* **Opus02:** `hexsym/sim.py:49-54` gives invalid hard failure 1 but posterior risk .5. E4=4.5/5.
* **Opus03:** `symdec/mc.py:121-129` does the same. E4=4.5/5.
* **GPT01/02:** all attempts and invalid flags are retained, with invalid computations/corrections conservatively scored as failures. E4=5/5.
* **GPT03:** explicitly retains 200 reserved slots of an externally terminated job as conservative administrative failures. Its archived **340600 slots are not evidence of 340600 completed physical trials**; the number completed in the lost batch is unknown. This limitation is disclosed in `README.md:62-77` and `data/execution_incident.json`, rather than hidden or treated as unbiased physical Bayes-risk data. E4=5/5.

The prior saved-data audit found no summary inconsistency in GPT01's 677 main-study NPZ files /1319100 trials, GPT02's 305024 decoder evaluation rows with four matching archived CSV hashes, or GPT03's 423 NPZ files /340600 slots. It did not constitute a fresh replay of every physical trial or a proof of every fitted threshold. Resources and commands here were inspected, not independently reexecuted as full production jobs.

## Per-aspect primary evidence

The companion JSON contains absolute paths, source line numbers, reasons and independent-check references for every score. The following direct pointers provide a compact audit trail:

**Fable03**

- D1 6/6: [anthropic__claude-fable-5-1/run_03/src/model.py:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/src/model.py:1>) — Uses three-state edge variables 0,+,- to preserve orientation and separates Z0,Z1 by ell; it does not make the arrivals at the two endpoints independent. Independent routine checks support the implementation.
- D2 3/3: [anthropic__claude-fable-5-1/run_03/README.md:25](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/README.md:25>) — Exact finite-width frontier/transfer-matrix contraction; memory grows exponentially with width. The task does not prescribe free fermions or a particular tensor-network method.
- D3 5/5: [anthropic__claude-fable-5-1/run_03/tests_validate.py:18](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/tests_validate.py:18>) — The submission includes independent small-lattice enumeration or comparisons using different elimination orders; the review additionally checks 210 routine cases per submission with independent irreps, geometry and generic einsum.
- D4 1/3: [anthropic__claude-fable-5-1/run_03/src/model.py:198](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/src/model.py:198>) — Passes 210/210 routine cases; fails 18 extremely low-p positive-probability stress cases. Ordinary stepwise normalization is present, but local products or edge weights can still underflow.
- D5 3/3: [anthropic__claude-fable-5-1/run_03/src/model.py:280](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/src/model.py:280>) — In the review, 210/210 routine corrections are legal edge sets, satisfy the syndrome, and choose the reference posterior's maximum logical sector; either sector is allowed at a tie.
- E1 4/4: [anthropic__claude-fable-5-1/run_03/answers.json:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/answers.json:1>) — answers.json parses; R1 contains all 21 O0/O1/O2 entries at N=2..8, and R3_N0 is an integer. Scientific support is scored separately under R1/R2/R3.
- E2 3/3: [anthropic__claude-fable-5-1/run_03/README.md:6](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/README.md:6>) — The required report, proofs and combined (p,N) phase diagram are delivered; correctness and evidence strength are scored in the scientific items, without double penalties.
- E3 3/3: [anthropic__claude-fable-5-1/run_03/README.md:30](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/README.md:30>) — Provides code, environment/dependency versions and reproduction commands. The review inspected and reused existing small-scale checks, without rerunning all production research.
- E4 4/5: [anthropic__claude-fable-5-1/run_03/src/run_mc.py:56](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/src/run_mc.py:56>) — Preserves seeds, fixed job counts, resources, raw arrays and denominators; exceptions become P0=.5 and aggregation gives both risk and hard tie .5, whereas the task requires failure. data/summary.csv has total nfail_exc=0, so this is a latent defect with no observed effect on archived estimates.

**Opus01**

- D1 6/6: [anthropic__claude-opus-5-5/run_01/src/tm.py:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/src/tm.py:1>) — Uses three-state edge variables 0,+,- to preserve orientation and separates Z0,Z1 by ell; it does not make the arrivals at the two endpoints independent. Independent routine checks support the implementation.
- D2 3/3: [anthropic__claude-opus-5-5/run_01/report.md:67](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:67>) — Exact finite-width frontier/transfer-matrix contraction; memory grows exponentially with width. The task does not prescribe free fermions or a particular tensor-network method.
- D3 5/5: [anthropic__claude-opus-5-5/run_01/tests/test_small.py:8](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/tests/test_small.py:8>) — The submission includes independent small-lattice enumeration or comparisons using different elimination orders; the review additionally checks 210 routine cases per submission with independent irreps, geometry and generic einsum.
- D4 1/3: [anthropic__claude-opus-5-5/run_01/solution.py:71](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/solution.py:71>) — Passes 210/210 routine cases; fails 18 extremely low-p positive-probability stress cases. Ordinary stepwise normalization is present, but local products or edge weights can still underflow.
- D5 3/3: [anthropic__claude-opus-5-5/run_01/solution.py:102](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/solution.py:102>) — In the review, 210/210 routine corrections are legal edge sets, satisfy the syndrome, and choose the reference posterior's maximum logical sector; either sector is allowed at a tie.
- E1 4/4: [anthropic__claude-opus-5-5/run_01/answers.json:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/answers.json:1>) — answers.json parses; R1 contains all 21 O0/O1/O2 entries at N=2..8, and R3_N0 is an integer. Scientific support is scored separately under R1/R2/R3.
- E2 3/3: [anthropic__claude-opus-5-5/run_01/report.md:5](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:5>) — The required report, proofs and combined (p,N) phase diagram are delivered; correctness and evidence strength are scored in the scientific items, without double penalties.
- E3 3/3: [anthropic__claude-opus-5-5/run_01/reproduce.sh:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/reproduce.sh:1>) — Provides code, environment/dependency versions and reproduction commands. The review inspected and reused existing small-scale checks, without rerunning all production research.
- E4 4.5/5: [anthropic__claude-opus-5-5/run_01/src/mc.py:146](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/src/mc.py:146>) — Raw data, seeds, fixed-block stopping rules, resources and denominators for all attempts are recorded; bad hard failure is 1, but the reported posterior-min risk is still .5 rather than 1 on exception.

**Opus02**

- D1 6/6: [anthropic__claude-opus-5-5/run_02/hexsym/api.py:43](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/hexsym/api.py:43>) — Uses three-state edge variables 0,+,- to preserve orientation and separates Z0,Z1 by ell; it does not make the arrivals at the two endpoints independent. Independent routine checks support the implementation.
- D2 3/3: [anthropic__claude-opus-5-5/run_02/README.md:18](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/README.md:18>) — Exact finite-width frontier/transfer-matrix contraction; memory grows exponentially with width. The task does not prescribe free fermions or a particular tensor-network method.
- D3 5/5: [anthropic__claude-opus-5-5/run_02/tests/validate.py:21](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/tests/validate.py:21>) — The submission includes independent small-lattice enumeration or comparisons using different elimination orders; the review additionally checks 210 routine cases per submission with independent irreps, geometry and generic einsum.
- D4 1/3: [anthropic__claude-opus-5-5/run_02/hexsym/api.py:45](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/hexsym/api.py:45>) — Passes 210/210 routine cases; fails 18 extremely low-p positive-probability stress cases. Ordinary stepwise normalization is present, but local products or edge weights can still underflow. macOS longdouble has a different range from the original Linux environment, so not all macOS failures can be attributed directly to the original environment; however, p/2 in pri rounds to zero in Python float before conversion to dtype, a cross-platform issue at the smallest positive float.
- D5 3/3: [anthropic__claude-opus-5-5/run_02/hexsym/api.py:143](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/hexsym/api.py:143>) — In the review, 210/210 routine corrections are legal edge sets, satisfy the syndrome, and choose the reference posterior's maximum logical sector; either sector is allowed at a tie.
- E1 4/4: [anthropic__claude-opus-5-5/run_02/answers.json:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/answers.json:1>) — answers.json parses; R1 contains all 21 O0/O1/O2 entries at N=2..8, and R3_N0 is an integer. Scientific support is scored separately under R1/R2/R3.
- E2 3/3: [anthropic__claude-opus-5-5/run_02/README.md:4](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/README.md:4>) — The required report, proofs and combined (p,N) phase diagram are delivered; correctness and evidence strength are scored in the scientific items, without double penalties.
- E3 3/3: [anthropic__claude-opus-5-5/run_02/README.md:24](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/README.md:24>) — Provides code, environment/dependency versions and reproduction commands. The review inspected and reused existing small-scale checks, without rerunning all production research.
- E4 4.5/5: [anthropic__claude-opus-5-5/run_02/hexsym/sim.py:49](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/hexsym/sim.py:49>) — Raw data, seeds, fixed-block stopping rules, resources and denominators for all attempts are recorded; bad hard failure is 1, but the reported posterior-min risk is still .5 rather than 1 on exception.

**Opus03**

- D1 6/6: [anthropic__claude-opus-5-5/run_03/symdec/tm.py:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/symdec/tm.py:1>) — Uses three-state edge variables 0,+,- to preserve orientation and separates Z0,Z1 by ell; it does not make the arrivals at the two endpoints independent. Independent routine checks support the implementation.
- D2 3/3: [anthropic__claude-opus-5-5/run_03/solution.py:12](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/solution.py:12>) — Exact finite-width frontier/transfer-matrix contraction; memory grows exponentially with width. The task does not prescribe free fermions or a particular tensor-network method.
- D3 5/5: [anthropic__claude-opus-5-5/run_03/tests/test_validate_small.py:7](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/tests/test_validate_small.py:7>) — The submission includes independent small-lattice enumeration or comparisons using different elimination orders; the review additionally checks 210 routine cases per submission with independent irreps, geometry and generic einsum.
- D4 1/3: [anthropic__claude-opus-5-5/run_03/symdec/api.py:43](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/symdec/api.py:43>) — Passes 210/210 routine cases; fails 18 extremely low-p positive-probability stress cases. Ordinary stepwise normalization is present, but local products or edge weights can still underflow.
- D5 3/3: [anthropic__claude-opus-5-5/run_03/symdec/api.py:74](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/symdec/api.py:74>) — In the review, 210/210 routine corrections are legal edge sets, satisfy the syndrome, and choose the reference posterior's maximum logical sector; either sector is allowed at a tie.
- E1 4/4: [anthropic__claude-opus-5-5/run_03/answers.json:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/answers.json:1>) — answers.json parses; R1 contains all 21 O0/O1/O2 entries at N=2..8, and R3_N0 is an integer. Scientific support is scored separately under R1/R2/R3.
- E2 3/3: [anthropic__claude-opus-5-5/run_03/README.md:3](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/README.md:3>) — The required report, proofs and combined (p,N) phase diagram are delivered; correctness and evidence strength are scored in the scientific items, without double penalties.
- E3 3/3: [anthropic__claude-opus-5-5/run_03/README.md:29](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/README.md:29>) — Provides code, environment/dependency versions and reproduction commands. The review inspected and reused existing small-scale checks, without rerunning all production research.
- E4 4.5/5: [anthropic__claude-opus-5-5/run_03/symdec/mc.py:121](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/symdec/mc.py:121>) — Raw data, seeds, fixed-block stopping rules, resources and denominators for all attempts are recorded; bad hard failure is 1, but the reported posterior-min risk is still .5 rather than 1 on exception.

**GPT01**

- D1 6/6: [openai__gpt-6-astra/run_01/decoder.py:232](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/decoder.py:232>) — Uses three-state edge variables 0,+,- to preserve orientation and separates Z0,Z1 by ell; it does not make the arrivals at the two endpoints independent. Independent routine checks support the implementation.
- D2 3/3: [openai__gpt-6-astra/run_01/decoder.py:279](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/decoder.py:279>) — Exact finite-width frontier/transfer-matrix contraction; memory grows exponentially with width. The task does not prescribe free fermions or a particular tensor-network method.
- D3 5/5: [openai__gpt-6-astra/run_01/validate.py:1](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/validate.py:1>) — The submission includes independent small-lattice enumeration or comparisons using different elimination orders; the review additionally checks 210 routine cases per submission with independent irreps, geometry and generic einsum.
- D4 3/3: [openai__gpt-6-astra/run_01/decoder.py:271](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/decoder.py:271>) — Passes 210/210 routine and 18/18 extremely low-p positive-probability stress cases; uses Decimal or log-domain fallback.
- D5 3/3: [openai__gpt-6-astra/run_01/decoder.py:403](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/decoder.py:403>) — In the review, 210/210 routine corrections are legal edge sets, satisfy the syndrome, and choose the reference posterior's maximum logical sector; either sector is allowed at a tie.
- E1 4/4: [openai__gpt-6-astra/run_01/answers.json:1](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/answers.json:1>) — answers.json parses; R1 contains all 21 O0/O1/O2 entries at N=2..8, and R3_N0 is an integer. Scientific support is scored separately under R1/R2/R3.
- E2 3/3: [openai__gpt-6-astra/run_01/README.md:3](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/README.md:3>) — The required report, proofs and combined (p,N) phase diagram are delivered; correctness and evidence strength are scored in the scientific items, without double penalties.
- E3 3/3: [openai__gpt-6-astra/run_01/README.md:17](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/README.md:17>) — Provides code, environment/dependency versions and reproduction commands. The review inspected and reused existing small-scale checks, without rerunning all production research.
- E4 5/5: [openai__gpt-6-astra/run_01/README.md:50](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/README.md:50>) — Retains all attempts; exception/invalid-correction risk and actual failure are both 1. Planned seeds, fixed stopping counts, resources and raw arrays can be recomputed; the existing archive audit found no inconsistency.

**GPT02**

- D1 6/6: [openai__gpt-6-astra/run_02/decoder.py:175](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/decoder.py:175>) — Uses three-state edge variables 0,+,- to preserve orientation and separates Z0,Z1 by ell; it does not make the arrivals at the two endpoints independent. Independent routine checks support the implementation.
- D2 3/3: [openai__gpt-6-astra/run_02/decoder.py:314](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/decoder.py:314>) — Exact finite-width frontier/transfer-matrix contraction; memory grows exponentially with width. The task does not prescribe free fermions or a particular tensor-network method.
- D3 5/5: [openai__gpt-6-astra/run_02/validate.py:1](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/validate.py:1>) — The submission includes independent small-lattice enumeration or comparisons using different elimination orders; the review additionally checks 210 routine cases per submission with independent irreps, geometry and generic einsum.
- D4 3/3: [openai__gpt-6-astra/run_02/decoder.py:224](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/decoder.py:224>) — Passes 210/210 routine and 18/18 extremely low-p positive-probability stress cases; uses Decimal or log-domain fallback.
- D5 3/3: [openai__gpt-6-astra/run_02/decoder.py:391](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/decoder.py:391>) — In the review, 210/210 routine corrections are legal edge sets, satisfy the syndrome, and choose the reference posterior's maximum logical sector; either sector is allowed at a tie.
- E1 4/4: [openai__gpt-6-astra/run_02/answers.json:1](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/answers.json:1>) — answers.json parses; R1 contains all 21 O0/O1/O2 entries at N=2..8, and R3_N0 is an integer. Scientific support is scored separately under R1/R2/R3.
- E2 3/3: [openai__gpt-6-astra/run_02/README.md:3](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/README.md:3>) — The required report, proofs and combined (p,N) phase diagram are delivered; correctness and evidence strength are scored in the scientific items, without double penalties.
- E3 3/3: [openai__gpt-6-astra/run_02/README.md:32](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/README.md:32>) — Provides code, environment/dependency versions and reproduction commands. The review inspected and reused existing small-scale checks, without rerunning all production research.
- E4 5/5: [openai__gpt-6-astra/run_02/README.md:61](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/README.md:61>) — Retains all attempts; exception/invalid-correction risk and actual failure are both 1. Planned seeds, fixed stopping counts, resources and raw arrays can be recomputed; the existing archive audit found no inconsistency.

**GPT03**

- D1 6/6: [openai__gpt-6-astra/run_03/decoder.py:182](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/decoder.py:182>) — Uses three-state edge variables 0,+,- to preserve orientation and separates Z0,Z1 by ell; it does not make the arrivals at the two endpoints independent. Independent routine checks support the implementation.
- D2 3/3: [openai__gpt-6-astra/run_03/decoder.py:267](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/decoder.py:267>) — Exact finite-width frontier/transfer-matrix contraction; memory grows exponentially with width. The task does not prescribe free fermions or a particular tensor-network method.
- D3 5/5: [openai__gpt-6-astra/run_03/validate.py:1](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/validate.py:1>) — The submission includes independent small-lattice enumeration or comparisons using different elimination orders; the review additionally checks 210 routine cases per submission with independent irreps, geometry and generic einsum.
- D4 3/3: [openai__gpt-6-astra/run_03/decoder.py:187](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/decoder.py:187>) — Passes 210/210 routine and 18/18 extremely low-p positive-probability stress cases; uses Decimal or log-domain fallback.
- D5 3/3: [openai__gpt-6-astra/run_03/decoder.py:312](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/decoder.py:312>) — In the review, 210/210 routine corrections are legal edge sets, satisfy the syndrome, and choose the reference posterior's maximum logical sector; either sector is allowed at a tie.
- E1 4/4: [openai__gpt-6-astra/run_03/answers.json:1](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/answers.json:1>) — answers.json parses; R1 contains all 21 O0/O1/O2 entries at N=2..8, and R3_N0 is an integer. Scientific support is scored separately under R1/R2/R3.
- E2 3/3: [openai__gpt-6-astra/run_03/README.md:3](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/README.md:3>) — The required report, proofs and combined (p,N) phase diagram are delivered; correctness and evidence strength are scored in the scientific items, without double penalties.
- E3 3/3: [openai__gpt-6-astra/run_03/README.md:24](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/README.md:24>) — Provides code, environment/dependency versions and reproduction commands. The review inspected and reused existing small-scale checks, without rerunning all production research.
- E4 5/5: [openai__gpt-6-astra/run_03/README.md:62](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/README.md:62>) — Raw arrays and summaries agree; 423 NPZ files /340600 archived slots include 200 conservatively failed reserved slots from an externally terminated batch, and the number of completed physical trials is unknown. This is disclosed correctly and the denominator is retained; slots are not called completed trials, and no scientific-failure penalty is assigned for this incident.

## Reviewer evidence files

- [results/oracle-check.json](../../results/oracle-check.json)
- [results/heldout-cases.json](../../results/heldout-cases.json)
- [scripts/independent_oracle.py](../../scripts/independent_oracle.py)
- [scripts/check_run.py](../../scripts/check_run.py)
- [results/saved-data-audit.json](../../results/saved-data-audit.json)
- [REPORT.md](../../REPORT.md)
