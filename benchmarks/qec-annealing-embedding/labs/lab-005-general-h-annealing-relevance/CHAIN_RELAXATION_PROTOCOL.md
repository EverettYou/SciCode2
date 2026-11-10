# Exploratory dynamics-aware chain relaxation, frozen2026-10-16T09:26Z

Motivation observed after the main results: LP maximizes alpha but leaves chain
strengths unconstrained in ties. Some chains are much stronger than their repair
load plus required margin, generating extreme local-bath mixing obstructions.
This extension is exploratory and cannot retrospectively upgrade main evidence.

For EVERY successful balanced main model, keep embedding, roots/trees, all
nonchain coefficients and alpha EXACTLY fixed. Minimize the sum of chain
strengths subject to the original requested margin d, individual J ranges and
all signed coupling-group bounds. Reserve numerical slack and rationally audit
actual coefficients. This changes no consistent-state logical energy after
adjusting the offset; it preserves the requested static consistency guarantee
but may worsen the tighter bound of an overstrong program. Report that tradeoff.

Evaluate the same local-dynamics obstruction before/after; a weaker obstruction
alone is not evidence of faster mixing. Add finite-budget CLASSICAL forward
heat-bath annealing diagnostics on both allocations, identical random initial
physical spins, same physical target and same proposal streams. Schedule is
beta(u)=20u, Gamma=0 throughout, random single-site attempts. Attempts per replica
are n_original×100,×1000,×10000, giving matched update budgets within each pair.
Use512 replicas for n16/32 and128 for n64, deterministic shared seeds; measure
actual computation cost. Save individual final physical/error states and scores.

Original-error feasibility is scored on all cases. Exact optimum cost reference
is allowed only when affine-kernel dimension<=18, via exhaustive feasible-space
enumeration; no such optimum enters the annealing transition or construction.
For larger nullity, report feasibility and feasible sample costs, and leave
optimal-error success unassessed. Keep chain agreement, feasibility, optimum
success, physical work and wall time separate. Report paired changes with
uncertainty and all budget points; no claim of QPU or quantum dynamics.

This is not a universal finite-time ordering theorem: the scientific outcome can
be a useful witnessed failure of the endpoint certificate to predict local
annealing, plus a successful or unsuccessful corrective allocation experiment.
