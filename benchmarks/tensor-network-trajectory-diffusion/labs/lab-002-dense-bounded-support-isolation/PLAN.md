# Lab 002 execution plan

## Objective

Determine, on exact dense three-qubit trajectories, when a controller composed from gates of maximum support $R=2$ recovers useful record-conditioned reversal capacity relative to $R=1$ and a full-system QR controller. The experiment is state-conditioned and resource-aware: it may support a bounded-support result, identify a capacity or optimization boundary, or conclude that a cell is uninformative for locality.

Human checkpoint `T-0006` approved this plan family. Approval covers only dense $N=3$ execution under the stages and gates below. It does not authorize MPS execution, truncation, size transfer, spatial parameter sharing, Hamiltonian heads, or $N>3$ work.

## Hypotheses and alternatives

- **H1 — useful bounded support:** in at least one state-family/resource-panel cell where full QR has a non-negligible advantage over $R=1$, the $R=2$ controller closes a practically useful fraction of that gap.
- **H2 — state-family saturation:** $R=1$ already reaches the full-controller fidelity within tolerance, so that cell cannot test locality.
- **H3 — support/depth capacity boundary:** full QR succeeds but the fixed $R=2$ schedule fails even under direct per-trajectory oracle fitting.
- **H4 — learned-controller bottleneck:** the oracle $R=2$ schedule succeeds but the record-conditioned $R=2$ controller fails, implicating record decoding or optimization rather than support alone.
- **H5 — resource confounding:** the coefficient-matched and depth/gate-matched panels disagree, preventing a support-only conclusion.
- **H6 — general optimization or loss failure:** the full controller also fails, gradients are unhealthy, or the declared optimizer budget does not reach a stable reference.

No hypothesis requires $R=2$ to outperform $R=1$ for every state family.

## Fixed physical setting

- System: open three-qubit chain, exact dense complex128 state vectors.
- Weak measurement: the Lab 001 companion convention with $\epsilon=0.5$, $T=6$, and the same Kraus normalization, tokenization, future-record slicing, and reverse-time indexing.
- Splits: 256/64/64 train/validation/test trajectories per state family, generated from distinct immutable split seeds and stored with the initial state, record, normalized final state, configuration, and SHA-256 hashes.
- Record model: the qualified Lab 001 future-record encoder architecture and pooling convention. Each controller in a paired seed cell receives the same copied encoder initialization and the same batches.
- Learned controller optimizer: Adam, learning rate $10^{-3}$, batch size 16, at most 128 updates, and a hard eight-minute wall-time cap per cell. A cell that cannot complete all 128 updates inside the cap is budget-failed and is not compared by silently changing its step count.
- Initialization seeds: 3301, 3303, 3305, 3307, and 3309 for every learned-controller/state-family/resource-panel cell.

## Predeclared state families

1. **Product-like:** seeded random product states $\bigotimes_{j=0}^{2}R_z(\phi_j)R_y(\theta_j)\lvert0\rangle$, with angles generated from the frozen trajectory seed. Include $\lvert000\rangle$ as a separately reported sentinel, not as an extra pooled family.
2. **Weakly entangled/local:** the same seeded product construction followed by one $\exp[-i(\pi/12)X_jX_{j+1}]$ gate. The active bond is balanced between $[0,1]$ and $[1,2]$ across every split and recorded per trajectory.
3. **Long-range correlated:** the exact $\lvert W_3\rangle=(\lvert100\rangle+\lvert010\rangle+\lvert001\rangle)/\sqrt{3}$ initial state.

State-family results remain separate. A pooled mean is descriptive only and cannot drive the locality decision.

## Stable interfaces

Reuse the Lab 001 seam `encode(m_future) -> h`, then map $h$ to ordered raw complex matrices, apply the companion QR convention within each block, and compose the embedded gates on the dense state. The stable prospective contracts are:

```text
encode(m_future) -> h
emit_block_gates(h, panel, support, reverse_step) -> [(sites, U_block), ...]
apply_block_schedule(state, gates) -> state
```

Controllers are:

- **full:** generic QR gates on all three sites;
- **R2:** generic $4\times4$ QR gates alternating on $[0,1]$ and $[1,2]$;
- **R1:** generic $2\times2$ QR gates in a mirror-balanced site schedule;
- **no-control:** identity rollout, evaluated but not trained.

Heads are slot- and position-conditioned, not translation shared. Spatial sharing is a later hypothesis.

## Complementary resource panels

Intrinsic QR dimensions make exact simultaneous matching of trainable coefficients, gate count, and depth impossible without changing the hypothesis class. Run both panels and report native controller parameters, gate applications, sequential depth, optimizer steps, wall time, and peak memory.

### Panel A — raw-QR-coefficient matched

Emit exactly 128 real QR inputs per reverse step:

- full: one three-qubit gate ($1\times128$ reals);
- $R=2$: four two-qubit gates on $[0,1],[1,2],[0,1],[1,2]$ ($4\times32$ reals);
- $R=1$: sixteen one-qubit gates in a mirror-balanced schedule with site counts $(5,6,5)$ ($16\times8$ reals).

This panel matches the learned QR-output dimension and output-projection parameter count but not gate count or sequential depth.

### Panel B — depth and gate-count matched

Apply six sequential gate slots per reverse step:

- full: six three-qubit QR gates;
- $R=2$: six gates alternating $[0,1],[1,2]$;
- $R=1$: six gates on $[0,1,2,2,1,0]$.

This panel matches gate applications and sequential depth but not QR-output dimension. A locality interpretation requires qualitatively consistent controller ordering across both panels. Panel disagreement is recorded as resource confounding.

## Evidence and uncertainty

For every state-family/resource-panel cell, write per-trajectory and per-seed records for:

- held-out teacher-forced one-step fidelity and reverse loss;
- paired $F_{\mathrm{full}}-F_{R=1}$ and $F_{R=2}-F_{R=1}$ differences;
- multistep reversal fidelity only after its gate;
- unitary residual, dense-versus-Quimb state error, finite-difference gradient error, gradient norms and failures;
- native parameter count, gate count, depth, completed optimizer steps, wall time, and peak memory.

Use the five paired initialization-seed means for primary Student-$t$ 95% intervals and retain the full per-trajectory distributions. The frozen test set is touched only after architecture, optimizer, and thresholds are locked from train/validation evidence.

Teacher-forced one-step examples follow the companion adjacent-Kraus convention. For every trajectory and $t=1,\ldots,T-1$, reconstruct the normalized source state after applying $K_tK_{t-1}$ to the state preceding that pair, target that preceding state, and condition the controller on the frozen future record $m_{t:}$. Average fidelity loss over the five time indices within each trajectory batch. Verify reconstructed final states against the frozen fixture before optimization.

## Conditional decision rules

For each state family and panel define

$$
\Delta_{\mathrm{full},1}=F_{\mathrm{full}}-F_{R=1}.
$$

The cell is informative for locality only if the lower 95% confidence bound for $\Delta_{\mathrm{full},1}$ exceeds $\delta_F=0.05$ absolute fidelity. Otherwise label it `uninformative: R1 saturation or unresolved full-head advantage` and make no $R=2$ claim.

Only for informative cells compute

$$
q=\frac{F_{R=2}-F_{R=1}}{F_{\mathrm{full}}-F_{R=1}}.
$$

Classify $q\geq0.5$ with a 95% interval excluding zero as practically useful partial recovery for that state family and panel. This is not a universal success requirement. Multistep evaluation is allowed only after the cell is informative, the numerical gates pass, and $R=2$ has a positive paired one-step effect.

## Oracle attribution diagnostic

For each informative or ambiguous state family, directly optimize the declared gate variables for the same fixed schedule on 32 frozen validation trajectories, one trajectory at a time. Use the same dense loss, 256 Adam updates, and an eight-minute cap; never use test trajectories. This is a reachability diagnostic, not a deployable baseline.

- full and oracle $R=2$ succeed, learned $R=2$ fails: record-decoding or learned-optimization bottleneck;
- full succeeds, oracle and learned $R=2$ fail after parity/restart checks: support/depth capacity boundary;
- full lacks an $R=1$ advantage: saturation or uninformative cell;
- all learned controllers fail or gradients are unhealthy: optimizer/loss failure;
- panels disagree: resource confounding and no locality conclusion.

## Steps

1. **Fixture stage:** implement the three state-family generator; freeze and hash splits; validate normalization, token ranges, state-family invariants, bond balance, and reload equality. No controller optimization.
2. **Interface stage:** implement full, $R=2$, and $R=1$ emit/apply contracts for both panels; record exact parameter, gate, and depth counts.
3. **Numerical gate:** run zero optimizer steps for shape, complex128 unitarity, dense-versus-Quimb circuit parity, copied-encoder parity, and central finite-difference gradients.
4. **One-step stage:** execute at most one bounded seed/family/panel/controller cell per research transition and save a reloadable result after every cell.
5. **Analysis stage:** compute per-family paired intervals and informativeness labels without pooling families.
6. **Oracle stage:** run only for cells required by the attribution table.
7. **Multistep stage:** run only for cells passing its explicit gate.
8. **Report stage:** preserve positive, negative, uninformative, and resource-confounded outcomes; ingest the completed report before proposing MPS work.

## Completion criteria

- All fixture hashes and state-family invariants remain valid.
- Every interface and numerical gate passes its predeclared tolerance.
- Every planned learned-controller cell either completes all 128 updates or records a budget/numerical failure without substitution.
- Per-family, per-panel paired intervals and informativeness labels are complete before any locality interpretation.
- Oracle and multistep stages run only where their gates require them.
- The completed report preserves saturation, capacity, optimization, resource-confounded, and null outcomes and is ingested before any MPS proposal.

## Numerical gates and stop conditions

- Require $\lVert U^\dagger U-I\rVert_\infty\leq10^{-10}$ in complex128 for every emitted block.
- Require dense-versus-Quimb final-state maximum error $\leq10^{-10}$ for identical schedules.
- Require central finite-difference agreement on declared coordinates to absolute error $\leq5\times10^{-5}$ or relative error $\leq10^{-3}$ away from zero.
- Pause on nonfinite states, losses, gradients, invalid probabilities, split-hash drift, seed mismatch, or failure to complete the matched optimizer budget inside the wall-time cap.
- Do not repair a failed $R=2$ result by increasing $N$, introducing MPS, changing the record encoder, adding spatial sharing, or silently enlarging depth or compute.
- Do not infer locality from an uninformative family, pooled mean, a single resource panel, or a failed full-controller reference.

## Expected artifacts

- `artifacts/dense-n3-state-families-v1/manifest.json` and immutable split tensors;
- `results/numerical-gate-v1/*.json`;
- `results/one-step-v1/<family>/<panel>/<controller>/seed-*.json`;
- `results/oracle-capacity-v1/*.json` when triggered;
- `results/multistep-v1/*.json` only for eligible cells;
- `results/decision-table-v1.json` plus a Markdown summary;
- a completed `REPORT.md` with exact commands, environment lock, deviations, evidence classification, and wiki-ingest handoff.
