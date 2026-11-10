# Surface-code encoding comparison in quantum annealing

Status: completed; started 2026-10-08 00:40 America/Los_Angeles.

## Authorized question and context

The user asks whether direct error-bit/parity-auxiliary encoding or reference-chain/stabilizer-spin encoding is preferable for surface-code quantum annealing. Interpret the dictated “surface hole” as surface code from the preceding discussion. This is supervised follow-up research using prior lab002 code and discussion, not an autonomous benchmark trial or difficulty calibration. Do not change the frozen previous lab artifacts or benchmark problem.

## Fixed scientific design

- Ideal measurements, one CSS error sector, independent errors with positive additive weights; unrotated planar rectangular surface-code patch, two rough and two smooth boundaries.
- Error edges: horizontal x=0..w-1,y=0..h-1 and vertical x=1..w-1,y=0..h-2. Checks at interior vertices; stabilizer generators are elementary relative face boundaries. n=wh+(w-1)(h-1), rank(H)=(w-1)h, rank(B)=w(h-1), one logical degree of freedom. Validate HB=0, HL=0, and ranks.
- Direct construction A: existing exact XOR/carry compiler, Lambda=sum(abs(weights))+1. Record it as a conservative baseline, not optimal penalty choice.
- Constraint-free construction B: find a feasible reference e0 by GF(2) elimination, then e=e0+B x+ell L mod2. Solve ell=0 and ell=1. Explicitly account for both runs; all states are syndrome-feasible. Both sectors share a common coefficient normalization.
- Dynamics: closed-system forward anneal H(u)=-(1-u) sum X + u H_P, u=t/T, initial uniform |+> state, hbar=1. Compare identical per-spin driver and |h|,|J|<=1 normalized problem coefficients; also inspect unscaled logical energy as a diagnostic. No bath, calibration error, analog precision, hardware A/B schedule, or QPU claims.
- Primary dynamic score: probability of returning a globally minimum-cost feasible original error pattern; sum all tied optima and all auxiliary states projecting to an optimum. Also record feasibility and exact programmed-ground probability where useful. Report the whole syndrome ensemble, not selected favorable instances.
- Charge B's two sequential anneals: at total anneal budget C, A gets T=C and each B sector T=C/2. Additionally compare A two independent runs of C/2 to B two runs of C/2, to expose allocation effects. Repeated sampling comparisons should account for time and success probability.
- Exact state-vector integration on tiny patches where feasible, with norm and step/tolerance convergence checks. Exact small examples support conditional findings only. Spectral gaps require degeneracy-aware interpretation; do not use endpoint zero gaps as a speed prediction.
- Resource sweep: d=2,3,5,7 (extend to9 if affordable), SAME Zephyr Z6 hardware and SAME minorminer search policy for both encodings, three seeds; save embeddings and validate. Charge all original/auxiliary/chain spins. Count B's per-sector sequential hardware versus simultaneous two-sector hardware separately.
- Primary sources and independent theoretical review accompany numerical results. No assertion of superiority over MWPM.

## Acceptance and decision rules

Complete when: mappings independently validated; resource results exist across sizes; full forward-anneal probabilities and convergence evidence exist for at least one complete tiny syndrome ensemble; both logical sectors and physical normalization are accounted for; report states where each encoding wins/loses and which broader conclusions remain untested. A universal winner is not required. Structural savings alone cannot establish dynamical speedup.

## Ownership and next operation

Root: models, validation, exact dynamics, synthesis, final report and manifest.
surface_embedding: hardware resource comparison and report.
surface_theory_audit: independent theory/fairness/source review.

Completed: shared models, independent exact mapping audit, resource sweeps,
full forward-anneal ensembles, all three tiny physical embeddings, doubled-step
convergence and independent adaptive ODE cross-check, report and figure.

Protocol refinements before reporting: add a geometry-certified local penalty;
add weight-independent syndrome repair as a separately scored direct variant;
compare zero-time sampling baselines; extend tiny physical dynamics from the
first embedding seed to all three. No failed/favorable cases were excluded.

Acceptance criteria are met. Larger-distance quantum dynamics, alternative
quadratizations, optimized schedules and live-device tests remain follow-up work.
No current computation or approval is pending.
