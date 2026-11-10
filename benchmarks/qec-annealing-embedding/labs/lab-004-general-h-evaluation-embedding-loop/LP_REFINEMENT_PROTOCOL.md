# Exploratory LP+deletion combination, frozen2026-10-16T08:36Z

The uniform main suite and supplemental fixed-pool LP results are already seen.
Test a combined allocator/topology loop on the12 development cases only, then
validate the unchanged algorithm on8 newly generated inputs: all4 families,
n32/64,seed7703. Do not call previously seen main held-out inputs fresh validation
of this adaptively chosen combination. Keep the original target,beta,epsilon,
8-seed minorminer proposal budget and original first-uniform-alpha floor.

Select a minimum-qubit LP-programmed candidate meeting that frozen floor, then
perform exactly one deterministic deletion pass as in the main protocol.
Each graph-valid deletion recomputes the centroid/root/tree and LP allocation.
Accept only actual-feasible programs meeting the frozen floor. Compare with
LP-before-pruning and unconstrained LP deletion from the identical start.
Adaptive paths can differ, so report actual proposal counts and all timings;
no equal-proposal claim is attached to these paths. Preserve all solver failures
and rationally audit selected final programs. No further algorithm tuning follows.
