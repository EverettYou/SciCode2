# Candidate revision 0.4: multi-sector quantum decoding

**Status:** formulation draft for discussion and exploratory testing. It does not
replace the current 0.3-general-H proposal or freeze a test prompt.

## Recommendation

Narrow the next candidate from “solve general sparse-H compilation, embedding,
and annealing-quality theory” to one linked question:

> When a decoding problem has multiple logical outcomes, how should its annealing
> formulation and finite run budget be chosen so that the decoder returns the
> correct logical outcome reliably under a fixed hardware-resource limit?

This keeps the work centered on decoder behavior while retaining embedding as a
measured physical constraint. It uses the second research round's verified
encoding contrast, but moves beyond its single-logical-sector surface-code case.
The central outcome is logical-decision reliability under an explicit model, not
an unqualified claim that one embedding or code is universally better.

## Draft task statement

### Scientific objective

Determine whether and when a sector-aware annealing decoder can lower logical
failure probability compared with a parity-penalty decoder under the same fixed
hardware and total anneal budget. Develop a reproducible decoder and explain the
tradeoff among logical-class degeneracy, feasible-state representation, embedding
cost, coefficient scaling, and finite-time dynamics.

The goal is a reproducible decoder and a scientifically justified comparison on a
declared family of instances. A universal winning encoding or a claim about a
commercial device is not required.

### Problem definition and inputs

Each instance supplies sparse binary matrices \(H\), \(B\), and \(O\), a syndrome
\(s\), independent mechanism probabilities \(p_i\), a planted error \(e_{true}\)
for evaluation only, a target hardware graph, coefficient limits, and a fixed
anneal schedule and total run budget. Here \(He=s\); columns of \(B\) span the
zero-syndrome, zero-observable moves, so \(HB=0\), \(OB=0\), and
\(\operatorname{im}B=\ker H\cap\ker O\). The map \(Oe\) labels the logical outcome
and distinguishes the remaining classes in \(\ker H/\operatorname{im}B\). The
true error and its outcome are evaluator-only labels and are never decoder
inputs. The solver receives only the declared decoding inputs.

Use \(w_i=\log[(1-p_i)/p_i]\) for the independent-error model. The decoding
target is the maximum-posterior logical class
\(\arg\max_\ell\sum_{e:He=s,\,Oe=\ell}P(e)\), not the single minimum-cost
error pattern. The evaluation target is the logical outcome, not exact recovery
of the planted mechanism pattern. Tied maximum-posterior classes are all optimal.
All matrices, generators, probability parameters, hardware graphs and schedules
needed for a trial must be supplied or reproducibly generated from the task
inputs.

### Central research question

Construct a decoder that predicts a logical outcome from annealing samples within
the stated total budget. Compare a conventional parity-penalty formulation with
at least one alternative justified by the supplied \((H,B,O)\) structure. The
solver may develop another formulation. Account for the cost of testing multiple
logical sectors, embedding, coefficient scaling, and repeated anneals under the
same total resource budget.

Determine whether a useful instance-dependent rule can choose the formulation or
allocate runs without performing the full annealing calculation for every choice.
The comparison may be conditional and may return “no reliable preference” when
the evidence does not support a choice. Explain when the rule fails and what
remains unproved.

### Expected evidence

- Show the decoder preserves the supplied parity constraints and maps its
  programmed ground states to valid corrections with the intended costs.
- Supply independently checkable embedding and coefficient witnesses, or
  explicitly report a certified resource obstruction. Distinguish these from
  heuristic search failures.
- For the supplied small instances, compare logical-outcome success with an
  independent exact reference obtained by enumerating errors and summing their
  prior probability within each logical class. Include all ties and distinguish
  minimum-cost patterns from the most likely logical class under the stated
  probability model.
- Evaluate finite-time behavior under the supplied annealing model. Demonstrate
  numerical convergence and compare strategies under the same total anneal and
  hardware budget. Separate modeled closed-system dynamics from actual device
  performance.
- Report resource use and explain any performance reversal across instance
  families. A smaller model or shorter chain alone is not evidence of higher
  logical success.

## Why this is a better candidate shape

The earlier general-H proposal combines a general compiler, embedding algorithm,
update strategy and a useful annealing-quality theory. The first round produced a
sound generic baseline and a mathematically valid but often inconclusive dynamics
certificate. The second round established a meaningful resource and small-system
dynamics comparison for one encoded observable. A benchmark that asks for every
piece at once can reward an impressive scaffold even when its central quality
claim is not informative.

This formulation requires several linked scientific judgments: define logical
success correctly; account for degeneracy and sector-selection cost; decide
whether a proposed encoding remains useful after coefficient rescaling and
embedding; distinguish algorithmic stratification from a quantum-dynamics gain;
and choose a comparison that can be checked without claiming real-device
performance. Those checks directly address the supplied strong/rejected example
lessons: avoid a task decided by one diagnostic choice, avoid an ungradeable open
question, and do not hand the model a complete recipe.

## Feasibility and verification plan

Keep the test family small enough for exact enumeration and full state-vector
simulation, with at least two distinct logical observables and more than one
structural regime. A practical author-side fixture set would include a regular
patch, a punctured or otherwise multi-logical instance, and an irregular sparse
instance. The precise fixtures should be chosen before testing and included in
the isolated lab input bundle; the listed examples are design guidance, not a
claim that these data are already prepared.

Use four independent checks:

1. Exhaustive enumeration of \(e\) gives the valid corrections, costs, ties and
   posterior weight of every logical class.
2. A compiler checker verifies \(H\), \(B\), \(O\), ground-state projection and
   logical labels independently of the submitted decoder.
3. A graph checker validates each embedding witness and programmed coefficient
   limits.
4. Exact finite-size annealing simulation, with tolerance/step refinement and
   probability-normalization checks, evaluates the stated model. This supports
   only conclusions within that model.

The test must supply a fixed schedule and total budget so alternative formulations
can be compared fairly. Do not score a method on an easier syndrome, a larger
aggregate runtime, or extra uncharged sector runs. Keep exact posterior decoding,
minimum-cost pattern decoding, and finite-time annealer success as distinct
quantities.

## What counts as success or failure

This is a falsifiable comparison, not “write an algorithm and describe it.” The
test package must freeze the instances, noise distribution, target graph,
coefficient limits, anneal schedule, total shot/time budget, and baseline before a
trial starts. One suitable primary metric is the exact expected logical-failure
probability under the supplied independent-error distribution. For each syndrome
and logical class, an exact enumerator sums the prior probability of every
compatible error. The evaluator can then score the decoder's stochastic outputs
against the planted logical class, averaged over the declared error distribution
and annealing samples.

Use separate, non-compensating checks rather than a subjective composite score:

1. **Decoding:** independent algebraic checks verify parity constraints, logical
   labels, and objective values. Evaluation compares the decoder's logical
   decisions with the exact logical-class posterior and measures expected logical
   failure. Returning a low-cost pattern alone does not pass this check.
2. **Embedding:** an independent checker validates connected, disjoint branch
   sets, required couplers, and programmed coefficient limits. A heuristic search
   timeout is not evidence that no embedding exists.
3. **Annealing comparison:** a converged reference calculation evaluates the
   same finite-time model for the submitted method and the fixed baseline at equal
   total anneal time and shot count. Claim an improvement only when probability
   intervals are separated beyond the independently measured numerical error;
   overlapping intervals mean “inconclusive.”
4. **Efficiency:** report preprocessing, per-syndrome work, embedding time,
   physical qubits, and anneal calls separately. The method is operationally
   feasible only within the frozen resource caps. Do not reward accuracy bought
   with uncharged extra runs or hardware.
5. **Scope:** claims must match the supplied instances and specified model. A
   modeled advantage does not establish an advantage on a physical device.

For an autonomous test, **complete and correct** means the decoder and any
embedding witnesses pass independent checks, the measured logical-failure result
agrees with the reference within a predeclared numerical tolerance, and the final
claim correctly reports improvement, no improvement, or an inconclusive result.
**Failed** means a correctness claim is false, the reported performance ranking
contradicts the reference, or the conclusion overstates what the model supports.
**Partial** means a correct compiler or decoder is delivered but its quality claim
is not evaluated or supported. A scientifically supported “no improvement” is a
valid completed investigation; the test measures whether the agent reaches and
supports the result, not whether it invents a winner.

The fixtures, baseline artifact, numerical tolerance, and resource caps still need
to be prepared by the author and fixed before a clean test. These are local
evaluation choices, not organizer-prescribed thresholds.

## Likely failure modes to capture in the case report

These author-side diagnostic categories should not be appended as hints to the
minimal prompt:

- selecting the minimum-cost error pattern when the target is the most probable
  logical class, whose probability sums over many compatible patterns;
- omitting a logical sector or failing to charge its additional anneals;
- comparing encodings with different total budgets or coefficient scales;
- treating a correct logical QUBO as proof that the physical embedding preserves
  its ground states;
- inferring annealing quality from qubit count, chain length, or a static gap
  alone;
- treating a nonconverged simulation or inconclusive bound as a ranking;
- presenting an ideal closed-system result as a prediction for a noisy device.

When these occur, preserve the transcript evidence, the relevant scientific
principle, the expert correction, and its effect on the result. Coding defects,
missing inputs, and failed launchers are not automatically scientific failures.

## Text-only screen

**Recommendation: pass-to-testing as a candidate, with input design still open.**
The question has a concrete scientific target and multiple coupled decisions; its
outputs can be checked against exact logical-class enumeration, embedding
witnesses, and converged finite-size dynamics. It appears achievable for a small
family without QPU access. It should not require a universal theorem or large-scale
device simulation.

The main risk is scope creep: if the fixtures, open-system physics, broad code
families, real-time windows, or general compiler optimization are all required,
the task will again be too large. A dry-run test should check whether the supplied
multi-sector instances actually produce more than one meaningful representation
or budget decision. Difficulty remains unmeasured until a clean autonomous run.

## Provenance and related records

- Current proposal and source PDF: [TASK.md](TASK.md) and
  [scicode2-qec-annealing-embedding.pdf](scicode2-qec-annealing-embedding.pdf).
- First-round evidence: [lab 002 report](../labs/lab-002-agent-test-general-h/RESEARCH_REPORT.md)
  and [conditional dynamics certificate](../labs/lab-002-agent-test-general-h/THEORY_CERTIFICATE.md).
- Second-round evidence: [lab 003 report](../labs/lab-003-surface-code-encoding-comparison/REPORT.md)
  and [theory audit](../labs/lab-003-surface-code-encoding-comparison/THEORY.md).
- Participant context and example-bank screen:
  [Project Sycamore introduction](../../../docs/scicode2/project-sycamore-introduction.md),
  [motivation](../../../docs/scicode2/project-motivation.md), and
  [strong and rejected examples](../../../docs/scicode2/example-bank.md).

The linked lab reports are author-side evidence for design, not scientific answers
to preload into a fresh autonomous test.
