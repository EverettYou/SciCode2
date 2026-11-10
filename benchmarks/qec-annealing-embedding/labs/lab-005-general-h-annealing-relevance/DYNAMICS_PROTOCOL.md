# Supplemental late-hold local dynamics limitation, frozen2026-10-16T09:19Z

This extension is selected after early compiler/thermal results. It does not
change the primary protocol. Model: Gamma=0 terminal hold, random-scan single-site
heat-bath updates, one uniformly selected physical qubit per attempted update,
fixed beta and programmed Ising coefficients. Equilibrium is the physical Gibbs
law. This is an explicit classical local-bath model, not quantum dynamics or a
model asserted for D-Wave hardware.

Prove and audit a conductance limitation: a root flip on a nonsingleton branch
has a broken-chain endpoint, so stationary cut flow is at most that branch's
broken probability divided by Nphysical. For balanced compilation, a verified
kernel vector containing original variable i bounds its logical marginal using
its absolute weight cost. Combine the chain-distortion bound to lower-bound
physical root marginal variance, and upper-bound the random-scan spectral gap.
Report resulting rigorous LOWER bounds on worst-case mixing time; do not infer
an ordering of actual decoding success or actual gap from upper bounds.

Apply this inexpensive certificate to every successful saved balanced ordinary
model at beta10,20,40,80. Return inconclusive for singleton original branches,
fixed original bits, or root-variance bounds that vanish. Report coverage and
whether mixing lower bounds exceed1,10,100 sweeps. Include all temperatures.

Independently validate local flow and Rayleigh inequalities on tiny exact
compiled general-H models with deliberately expanded physical branches; this
is proof validation, not the routine-coverage result. No claim is completed
solely by these tiny examples. Future empirical finite-budget classical runs,
if used, receive a separate frozen protocol and remain classical simulations.
