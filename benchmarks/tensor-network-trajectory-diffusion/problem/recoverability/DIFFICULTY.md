# Author-only difficulty and shortcut audit

## Claim we can make now

The proposed task asks for a decoder-independent optimum and verification, so
reproducing a familiar network or reporting high target fidelity is insufficient.
It leaves representation, solver, approximation and validation choices open.
There are plausible scientific obstacles, but **no evidence yet that a frontier
model has success probability below 10%, or that the task takes 10–20 active hours**.
Historical multi-turn human/AI work is not a blind baseline for this new problem.

## Candidate difficulties and required evidence

| Candidate obstacle | What would demonstrate it | Current status |
|---|---|---|
| Distinguishing decoder failure from information loss | A feasible recovery and independent upper bound nearly coincide | N=2,4 reference grid and one N=6 pilot verified |
| Missing-record mixtures | Compare fully observed and partially observed optima on the same code | Positive record effect resolved at N=2,4 and N=6,g=.5 |
| Efficient certification at larger sizes | Matched accurate small cases and controlled large-case bounds, measured resources | N=6 pilot passes 1e-4; N=8 remains pending |
| Diagnosing finite-size trends | Effects survive error budgets and multiple sizes | Pending |
| Avoiding plausible but incorrect simulation | Known incorrect updates fail independent checks | Historical TDVP repair demonstrates this risk, not model failure rate |

## Legitimate shortcuts to test first

1. **Fixed-state preparation:** removed by the inaccessible-reference task. A
   reset decoder scores 1/4. Enforcing this is a physical definition, not an
   architectural restriction.
2. **Invert each Kraus matrix:** a normalized algebraic inverse is not generally
   a deterministic CPTP recovery. If a solver supplies a valid inverse recovery
   channel or includes success probabilities in a different permitted task,
   check it rather than dismissing it.
3. **All outcomes observed:** for a fixed encoding and one effective Kraus map A_c
   per classical record, test the analytic route

       F_opt = sum_c (Tr sqrt(A_c^dagger A_c))^2 / 4.

   For input dimension two this uses 2x2 Gram matrices. Polar recovery supplies
   achievability; the corresponding optimum can be checked with small dense
   certificates. Evaluating the sum may still be expensive. Do not confuse the
   optimization formula with a scalable way to evaluate its Born-weighted sum.
   If this route or a related identity also solves partial records cheaply, that
   is a legitimate solution; revise the task only before freezing it.
4. **Stabilizer/classical reduction:** tilted weak measurements and the explicit
   non-Clifford encoding do not automatically guarantee difficulty. Check whether
   symmetries, factorization, channel sufficiency, or a transfer matrix solve the
   constructed family. Adding non-Clifford gates solely to defeat AI is not a
   scientific rationale; retain this family only if record loss has a useful effect.
5. **Dense SDP solves everything:** if small sizes already resolve the scientific
   question, either accept the simpler problem and calibrate its difficulty, or
   identify a scientifically motivated scale that needs a substantive advance.
6. **Trivial intervals suffice:** baseline L=1/4,U=1 always encloses the optimum.
   Precision targets must exclude this without becoming unachievable. Test simple
   decode-and-discard and standard recovery baselines before choosing thresholds.

## Blind calibration protocol

First complete and freeze the reference solution. Give each model only the public
task, its pinned dependencies, and public input generator. Remove author notes,
lab directories, cached outputs, checkpoints, this conversation, and hidden tests
from the solver filesystem. Freeze model identifier, tool access, internet policy,
hardware, token/time budget, and whether autonomous self-revision is permitted.

Use independent runs with no human hints. Log all calls, compute, artifacts,
failures, and verifier results. More than one independently solved instance family
is desirable; random seeds alone do not establish scientific diversity.

Score whole-task success against prespecified correctness, precision, and resource
gates. Report numerical failures, invalid certificates, inconclusive bounds, and
resource overruns separately. Compare an ordinary solve prompt with a strong
autonomous-research baseline. Do not tune the task on the final evaluation trials.

Zero successes in ten independent identically distributed runs has a one-sided
95% binomial upper bound of about 25.9%; it does not support a <10% success claim.
Zero in 29 gives 1-0.05^(1/29), about 9.8%, under that sampling model. Multiple
models, correlated runs, or adaptive task selection require additional care.
Always publish counts and uncertainty, not a guarantee that AI cannot solve it.

## Release/keep/prune decisions

- **Keep:** nontrivial record effect, reference interval closure at workstation
  scale, independently checkable outputs, and appropriate blind difficulty.
- **Revise:** feasible but trivial/too easy; revise the physical question before
  another frozen evaluation, retaining pilot outcomes.
- **Prune:** no useful effect, no independent upper bound, or unmanageable cost.
- **Later phase-transition branch:** requires a defined thermodynamic family,
  evidence of a transition, controlled finite-size/time scaling and viable error
  bars. A fitted decay of one decoder is insufficient. Critical values need not
  be universal; exponents cannot be made gold by a single scaling collapse.

## Measured calibration update: Lab 009

The N=2,4 exact dense pilot now has independently verified numerical reference
bounds. Those small sizes are calibration cases, not evidence of a hard research
benchmark. For N=4, the partial-record solves take seconds to a few minutes on
one CPU thread after implementation; they do not by themselves establish 10–20
hours of active scientific work.

A standard transpose-recovery construction with no training and no SDP, together
with the fully observed analytic upper bound, attains width below 0.02 on every
N=4,6 tested cell. At N=6 it takes about two seconds per strength. Thus the old
0.02 gate is insufficient. The measured full-versus-partial record effect at
N=2,4 is only about 0.00028–0.00486. The revised pilot width 1e-4 would resolve
these effects and rejects this particular simple baseline, but is not evidence
that a different straightforward method or AI cannot meet it.

The N=6,g=.5 pilot has now passed the 1e-4 gate after targeted refinement of one
record, with final width 1.51e-5. Next calibrate N=8. Do not inflate the grid
to N=12,16 just to defeat dense enumeration without a validated scalable verifier.
No blind model trials have been conducted.
