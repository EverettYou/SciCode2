# Candidate revision v0.5: useful annealing decisions under a fixed protocol

Date: 2026-10-16. Status: question-formulation proposal. This develops
[candidate v0.4](CANDIDATE-REVISION-v0.4.md) in response to the user's request for
SciCode-relevant challenge and verifiable results. It is not a frozen prompt,
prepared input suite or calibrated difficulty claim.

## Proposed central question

> Under a common finite forward-anneal protocol and a total resource budget, can
> an instance-dependent choice of encoding, embedding and sector-run allocation
> improve logical decoding, and can that choice be justified and independently
> checked on instances not used to tune it?

Treat a valid matrix-to-QUBO compiler and embedding construction as prerequisites
or reusable components, rather than the principal research answer. The result to
explain is logical decision quality after physical programming and finite-time
sampling. A smaller embedding, a sufficient chain penalty, or an isolated pause
theorem is not that result.

## Proposed problem definition

Each instance supplies H, an observable map O with at least two independent
logical degrees of freedom on ker(H), a valid syndrome s, independent mechanism
probabilities p_i strictly between zero and one, a target hardware graph, and
coefficient constraints. It may supply a move matrix B with

\[
\operatorname{im} B=\ker H\cap\ker O.
\]

The supplied file format must distinguish public decoding inputs from hidden
physical errors used by the evaluator. A reference correction and class
representatives may be constructed from the public matrices. Neither a planted
error nor its observable label is available to the decision routine.

The desired posterior and optimal logical decision are

\[
q_\lambda(s)=
\frac{\sum_{e:He=s,\;Oe=\lambda}\prod_i p_i^{e_i}(1-p_i)^{1-e_i}}
     {\sum_{e:He=s}\prod_i p_i^{e_i}(1-p_i)^{1-e_i}},
\qquad \hat\lambda^*(s)\in\arg\max_\lambda q_\lambda(s).
\]

The target is logical recovery, not exact recovery of the private error pattern.
Minimum-cost pattern decoding and logical-class posterior decoding must be
evaluated separately. Multiple maximum-posterior labels may be equally optimal;
that does not make every one of them correct for a particular private error.

To make the physical comparison definite, the proposed credential-free model is
an ideal closed-system forward anneal on the actual programmed physical spins:

\[
\mathcal H_{\mathcal E}(u)=
 -(1-u)\sum_{q\in V_{\mathcal E}}X_q
 +u\left(\sum_q h_q Z_q+\sum_{(q,r)}J_{qr}Z_qZ_r\right),
\quad u=t/T,\quad \hbar=1.
\]

Each run starts in |+> on every active physical spin and ends in a computational
basis measurement. Penalties, chain couplings and hardware rescaling are included
in h,J. Branch spins, not just unembedded logical spins, receive the driver.
This model makes a finite-size numerical comparison possible without QPU access;
it is not a model of all commercial-device noise or thermal behavior.

Use a declared finite menu of run durations, a common physical-qubit cap, common
coefficient limits and a total anneal-time allowance. Count every sector run and
repeat toward that allowance. Report classical construction, inference, tuning,
readout and evaluation costs separately, with a declared classical cost limit
where needed. Positive minimum run duration and readout accounting prevent free
unlimited zero-duration samples. Fixture sizes and these numerical budgets are
still to be selected before a trial; this is a mathematical candidate, not a
completed runnable input package.

## Proposed scientific task

Develop a public-input strategy that chooses a representation and allocates the
allowed anneals. Compare the conventional parity-penalty representation with at
least one justified alternative, on multiple-logical-outcome instances and under
the same physical constraints. Formulate and test a rule that predicts when the
choice is worthwhile, including its uncertainty and limitations. Assess it on
reserved instances after fixing the selection rule.

The principal outcome is physical-prior logical risk and its excess over the
Bayes reference on the same instances. Explain whether observed gains arise from
sector allocation, the represented energy landscape, hardware scaling, chain
behavior, finite-time dynamics, or classical processing, to the extent the
evidence distinguishes them. A supported absence of benefit is valid. No universal
winner, quantum advantage over classical decoders, or general large-device
simulation theorem is required.

The method remains open. Merely observing that MAP and logical ML differ is
insufficient. A useful answer must implement the chosen decision process, justify
its treatment of finite-time samples and test its prediction. If a cheap classical
method already makes annealing unnecessary on the supplied suite, that is a
legitimate finding and evidence to revise or abandon the candidate.

## Important correction to candidate v0.4

A finite-time closed-system annealer is not automatically a Gibbs sampler of the
decoding prior. Counting its outputs within logical sectors does not, without a
derivation or calibration, estimate the q_lambda above. The task must distinguish

1. the physical error distribution defining the inference target;
2. the quantum measurement distribution produced by the programmed anneal;
3. the inference procedure transforming public data and samples into a decision.

The full Schrödinger model specifies item 2; it does not establish equality with
item 1. A future guided prompt may discuss this principle without supplying the
entire solution. It should not be hidden as an unstated grading assumption.

## Independent verification design

| Scientific claim | Independent evidence |
| --- | --- |
| Correct logical target | Enumerate physical errors on small fixtures and sum their prior mass by syndrome and observable label, including ties. |
| Faithful reduction | Independently compare minimized auxiliary energies, parity feasibility and projected optima, including signed weights where allowed. |
| Valid hardware program | Read saved branch sets and coefficients; check connectivity, disjointness, interaction realization, limits and the consistent-state energy identity. |
| Correct finite-time probabilities | Evolve the specified physical Hamiltonian on tractable anchors with an independent integrator or exact limiting solution, normalization and numerical error checks. |
| Logical recovery and uncertainty | Evaluate the full decision routine on private physical errors or exact class probabilities, with all failures included and all resource costs charged. |
| Useful selection rule | Compare with fixed baselines on a reserved suite; distinguish lower risk from a post-hoc per-instance oracle and report unresolved comparisons. |

For any chosen output label a, the conditional logical risk is 1-q_a(s). The
Bayes risk is 1-max(q_lambda(s)); their difference measures decision suboptimality.
This permits checking a negative result or imperfect decoder without requiring a
globally optimal embedding. Quantum-model accuracy and physical-prior posterior
accuracy are different checks and need independent references.

Use tiny exact anchors plus an informative challenge cohort. Do not choose sizes
solely to make state-vector simulation time out, or require an unaffordable
reference. The conditional uncertainty and cost of the challenge reference must
be established before formal scored calibration, not invented as a numerical
pass mark. Small fixtures for which direct enumeration solves everything may be
excellent unit checks and weak challenge cases at the same time.

## Why this change follows the existing evidence

[Lab 002](../labs/lab-002-agent-test-general-h/REPORT.md) provisionally passed the
old question in 56.85 minutes. Its sound comparison used a specified encoded
initial state during a pause; preparation and ramps were outside that claim.
All 25 ordinary-strength dynamics certificates were inconclusive. This is a
successful solution to the allowed earlier scope, not a failure to relabel after
the fact. The proposed new objective requires useful evidence under a common
forward protocol and across a declared suite.

[Lab 003](../labs/lab-003-surface-code-encoding-comparison/REPORT.md) supports a
structured-encoding resource and tiny-system forward-dynamics advantage for one
logical observable. It is supervised research, not a fresh autonomous difficulty
test. It also shows why geometry-aware penalties, both logical classes, common
search and physical scaling matter. Its equally weighted syndrome comparisons
are not already a physical-noise logical-risk benchmark.

[Choi](https://arxiv.org/abs/0804.4884) separates minor placement and parameter
setting. [D-Wave's embedding guidance](https://docs.dwavequantum.com/en/latest/quantum_research/embedding_guidance.html)
discusses the chain-strength/problem-range tradeoff. Those are starting principles,
not a ready solution to this decision problem.

## Text-only assessment and next step

**Recommendation: pass-to-testing as a formulation candidate, with a substantial
feasibility uncertainty.** Several linked scientific choices remain, and the
target can be checked in an explicit finite model. The main risks are reference
cost, trivially enumerable challenge fixtures and scope creep from combining
compilation, dynamics and inference. The pure symmetry-information decoder
candidate is the lower-cost first benchmark to test.

The [participant introduction](../../../docs/scicode2/project-sycamore-introduction.md),
[organizer-source requirements](../../../docs/scicode2/requirements.md) and
[user-supplied example summaries](../../../docs/scicode2/example-bank.md) motivate
the task shape; they do not establish empirical difficulty. The original linked
example case reports have not been reviewed here.

Next, make a complete trial-specific statement and public input bundle in a
benchmark-local lab, then test in a fresh user-opened session. Preserve final
outputs and transcript and revise based on actual scientific outcomes. No new
simulation, reference campaign, model trial or screening was run in this revision.
