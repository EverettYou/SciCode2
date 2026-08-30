---
id: T-0006
title: Approve dense N=3 bounded-support test
status: closed
priority: blocking
category: checkpoint
created: '2026-08-23T06:25:38Z'
updated: '2026-08-23T06:54:48Z'
context: 'Benchmark: tensor-network-trajectory-diffusion

  Lab 001 qualified the dense QR reference and exact encoder/QR seam at N=1,2, but supplied no evidence for bounded support. The benchmark review gate requires separate approval before any N>R training. The selected proposal is exact dense N=3 with R=2; it deliberately retains the global future-record encoder and uses position-specific heads so spatial support is tested before parameter sharing.'
benchmark_ids:
- tensor-network-trajectory-diffusion
related:
- benchmarks/tensor-network-trajectory-diffusion/wiki/ideas/research-frontier.md
- benchmarks/tensor-network-trajectory-diffusion/wiki/implementations/dense-qr-controller-reference.md
- benchmarks/tensor-network-trajectory-diffusion/labs/lab-001-local-controller-feasibility/REPORT.md
- benchmarks/tensor-network-trajectory-diffusion/problem/TASK.md
---

# Approve dense N=3 bounded-support test

## M-001 · agent · question · 2026-08-23T06:25:38Z

I compared three next-step designs. Recommendation: approve the least-confounded support-isolation test—on identical frozen dense N=3 trajectories, compare the full-system 8x8 QR head with two composed position-specific 4x4 QR heads on blocks [0,1] and [1,2], plus R=1 product and no-control baselines. Start with zero-step parity/gradient checks and a bounded teacher-forced one-step, multi-seed comparison; proceed to multistep reversal only if R=2 beats both lower-support controls. Spatial sharing, MPS, truncation, N>3, Hamiltonian heads, and size transfer remain excluded. Alternatives preserved are a shared N=3,R=2 head (more scalable but confounded) and N=4,R=2 brickwork (clearer geometry but costlier). Do you approve this selected design for a separately created Lab 002, or require a specific minimal change?

## M-002 · user · response · 2026-08-23T06:36:56Z

Thanks. I cannot approve T-0006 as currently phrased. The requirement that “R=2 must clearly outperform the lower-support baselines” is not an operationally valid decision rule for this problem.

First, R=1, R=2, and R=3 are nested support classes in expressive power, but they are not automatically comparable under a fixed parameter budget, circuit depth, optimizer budget, or number of applied gates. An apparent R=2 gain could reflect extra capacity or easier optimization rather than a meaningful locality effect. The experiment must therefore declare what is held fixed: parameter count, gate count, depth, record encoder, optimizer steps, and compute budget.

Second, the expected fidelity gain is state-dependent. For product-like states, R=1 may already saturate the achievable reversal or preparation fidelity, so the absence of an R=2 improvement would be uninformative rather than evidence against bounded support. Conversely, states with long-range correlations can expose a real support limitation. A W-like state is an important example: under a fixed-depth local circuit, exact preparation of a globally correlated state from a product state is itself constrained by the causal light cone. That is a capacity boundary, not simply an optimization failure.

The current proposal uses identical frozen dense N=3 trajectories, but it does not stratify them by state complexity or test whether the full QR controller has an advantage over R=1 for each state family. Without that check, an R=2 failure is ambiguous: it could mean that R=1 is already sufficient, that the target is outside the finite-depth local circuit class, or that the local controller is under-optimized.

Please revise the plan around a conditional, state-aware criterion:

1. Define predeclared state families, at minimum product-like, weakly entangled/local, and long-range-correlated or W-like cases.
2. For each family, first check whether full QR provides a measurable advantage over R=1. If not, label that family “uninformative for locality” rather than declaring R=2 unsuccessful.
3. Compare R=1, R=2, and full QR under matched parameter, depth, gate-count, record-conditioning, seed, and optimization budgets.
4. Report per-family distributions and uncertainty across predeclared seeds, not only pooled means.
5. Use a normalized conditional quantity such as (F_R2 - F_R1) / (F_full - F_R1) only when the denominator is demonstrably non-negligible, and predeclare a practical tolerance for what counts as useful recovery.
6. Distinguish capacity limits, optimization failures, and state-family saturation in the decision table. Do not require R=2 to beat R=1 universally.

The minimal N=3, R=2 support-isolation experiment may still be useful, but it needs this state-conditioned design and an explicit “no locality conclusion” outcome. Please update the plan and decision rule before creating or executing Lab 002.

## M-003 · agent · acknowledgment · 2026-08-23T06:43:38Z

[process-talk:working] I will revise the Lab 002 proposal around predeclared state families, matched capacity/optimization budgets, conditional normalized recovery gains, and explicit capacity-versus-optimization-versus-saturation outcomes, then validate the updated plan without creating or running the lab.

## M-004 · agent · resolution · 2026-08-23T06:44:32Z

[process-talk:done] Revised the Lab 002 proposal without creating or executing the lab. The design now predeclares product-like, weakly entangled/local, and long-range-correlated or W-like state families; matches parameter count, depth, gate count, record conditioning, optimizer steps, seed set, dtype, data split, and compute budget across R=1, R=2, and full QR; and reports per-family distributions with uncertainty. The decision rule is conditional: first require a non-negligible full-QR versus R=1 denominator, then report q=(F_R2-F_R1)/(F_full-F_R1) with a declared useful-recovery tolerance. It distinguishes capacity limits, optimization failures, state-family saturation, and genuine support evidence, and records a null result as no locality conclusion rather than an R=2 failure. Updated  and . Validation:  passed and the new state-aware criteria are present; no Lab 002, N>3, MPS, truncation, or transfer work was started.

## M-005 · agent · resolution · 2026-08-23T06:44:48Z

[process-talk:done] Correction to M-004: the revised state-aware Lab 002 proposal is recorded in `benchmarks/tensor-network-trajectory-diffusion/wiki/ideas/research-frontier.md` and `benchmarks/tensor-network-trajectory-diffusion/wiki/questions/scalable-trajectory-reversal.md`. No Lab 002 or experiment was created or run. `git diff --check` passed. The proposal predeclares three state families, matches capacity and optimization budgets, uses the conditional normalized gain q only when the full-QR versus R=1 denominator is non-negligible, and distinguishes capacity limits, optimization failures, state-family saturation, support evidence, and no-locality-conclusion outcomes.

## M-006 · agent · resolution · 2026-08-23T06:46:31Z

Applied your review to benchmarks/tensor-network-trajectory-diffusion/wiki/ideas/research-frontier.md. The proposal now freezes separate product, shallow locally entangled, and W3 state families; reports five-seed per-family distributions; gates locality interpretation on a full-QR-minus-R1 lower 95% confidence bound above 0.05 fidelity; and computes q=(F_R2-F_R1)/(F_full-F_R1) only in informative cells, with q>=0.5 and an interval excluding zero as useful partial recovery rather than a universal requirement. Because generic 1-, 2-, and 3-qubit QR gates cannot simultaneously match intrinsic parameter dimension, depth, and gate count without changing the hypothesis class, I replaced the false single match with two declared panels: 128 raw QR coefficients per step, and six matched sequential gate slots; record conditioning, split/initialization seeds, optimizer steps, batch schedule, stopping rule, and wall-time cap remain identical. A direct per-trajectory oracle schedule fit distinguishes circuit capacity from learned record decoding/optimization, and resource-panel disagreement is explicitly no locality conclusion. Wiki lint passes with zero errors and warnings. No Lab 002 or N>2 execution was created. Do you approve this revised design, or require one specific remaining change?

## M-007 · user · response · 2026-08-23T06:54:44Z

Approve.

## M-008 · user · decision · 2026-08-23T06:54:48Z

Closed by user.
