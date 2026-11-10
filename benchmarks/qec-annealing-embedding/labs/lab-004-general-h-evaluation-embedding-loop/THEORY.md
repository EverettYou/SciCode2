# A cheap thermal embedding evaluation for general sparse H

This is continuing research, not a blind test. The matrix compiler and Zephyr
adapter are reused read-only from Lab 002 with source SHA-256 hashes saved in
`results/source_provenance.json`. The new contribution in this round is the
repair certificate, physical allocation and certificate-constrained search loop.
It is not a claim of priority over the chain-penalty literature.

## 1. Faithful general-H logical model

For each sparse row, a left-to-right XOR network introduces prefix parity p and
carry a through the nonnegative integer penalty
M(x+y-p-2a)^2. The final two-bit parity constraint has penalty
M[x+y-2xy] for syndrome zero and M[1-x-y+2xy] for syndrome one.
Degree-one rows use M(x-s)^2; empty zero-syndrome rows cost zero. All auxiliaries
are binary. A check with d>=2 uses 2(d-2) auxiliaries and O(d) quadratic terms.
No code geometry, row independence, column-degree bound or decoding solution is
used. Repeated coordinates cancel over GF(2).

Let W=sum_i |w_i| and choose M>W. Every feasible error vector has a unique
zero-penalty auxiliary extension. Every infeasible full assignment pays at least
M. The largest possible objective improvement across two error patterns is W,
so every logical ground state has zero penalty and projects to a minimum-cost
feasible error pattern. Every tied minimum has its zero-penalty extension.
The declared syndrome is feasible; generators save a feasibility witness but
construction does not use its error values. Negative and zero weights are valid.
The implementation also preserves Lab 002's exact-rational coefficient and
binary64-error certificate.

Write x=(1+z)/2. For Q=c+sum a_i x_i+sum b_ij x_i x_j,
h_i=a_i/2+sum_j b_ij/4, J_ij=b_ij/4, and
c_I=c+sum a_i/2+sum b_ij/4. The actual nonzero interaction graph, including all
isolated variables, is embedded.

## 2. Physical allocation and rooted repair lemma

A valid minor embedding gives disjoint connected branches C_i in a fixed target.
Choose a spanning tree T_i and root r_i for every branch. Allocate every logical
J_ij across available physical interbranch contacts; our implementation uses
uniform splitting. The logical field h_i is placed entirely at r_i. The proof
also permits arbitrary field allocation, provided its absolute load is included.
Unused internal hardware edges are programmed to zero. For each physical site q,
let a_q be the sum of absolute nonchain couplings incident at q, plus the absolute
field at q. For an oriented tree edge e, let S_e be the descendant subtree and
L_e=sum_{q in S_e} a_q. These L_e are in unscaled logical units.

Use scaled nonchain coefficients alpha*h and alpha*J and ferromagnetic tree
coefficients -F_e. Set the physical offset to alpha*c_I+sum_e F_e. Thus on a
consistent spin assignment the physical energy is exactly alpha E_I(z).
For arbitrary sigma, let R(sigma) set each branch to its root spin, and let
D(sigma) be the tree edges whose endpoints disagree. Any spin differing from
its branch root has an odd number of walls on its root path; hence its indicator
is bounded by the number of walls on that path. For a field the repair changes
energy by at most 2|h_q| times that indicator; for an interbranch coupling,
by at most 2|J_qr| times the sum of the two endpoint indicators. Summing gives

    E(sigma)-E(R(sigma)) >= 2 sum_{e in D(sigma)} (F_e-alpha L_e).

This uses a union bound on endpoint effects, so frustration, cancellations and
simultaneous repair can only make the certificate conservative. It makes no
assumption about the logical ground state. The pair (root-spin vector, wall set)
is a bijection with all physical configurations: recover each spin by its root
spin times the product of wall signs along its path. Therefore any strictly
positive margin delta_e=F_e-alpha L_e guarantees all physical ground states are
consistent, and the projected ground states solve the original decoding problem.
The minimum improvement over repairing a broken configuration is at least
2 min_e delta_e. This is a chain-repair gap, not the global spectral gap or the
logical optimization gap.

The implemented root is a weighted centroid of the tree using interbranch
absolute loads. It minimizes the largest descendant component load over roots
and ensures every descendant component has at most half the total interbranch
load. This follows by walking from a vertex toward any component whose weight
exceeds half the total; that walk cannot reverse or revisit a vertex. At its
terminal centroid, every incident component is at most half the total. Any root
has maximum component load at least the centroid's maximum: for the centroid's
largest component, another root either leaves that component intact or leaves
the complement, whose load is no smaller. Root-concentrated field does not
contribute to descendant loads, but is charged to its physical h constraint.
This can reduce chain strengths relative to the usual whole-logical-load bound.

## 3. Gibbs certificate without a decoding partition function

The declared main model is terminal thermal equilibrium for the programmed
classical Ising Hamiltonian E. Its law is exp(-beta E)/Z, with beta in reciprocal
programmed-Ising-energy units. It is a conditional late-anneal model; no physical
runtime or initial state is asserted to produce equilibrium. For the prompt's
Hamiltonian convention, beta equals beta_physical*B/2 at A=0.

Let Z_C be the partition sum over consistent configurations. The repair lemma
and the bijection imply

    Z <= Z_C product_e [1+exp(-2 beta delta_e)].
    P(any chain broken) <= 1-product_e [1+exp(-2 beta delta_e)]^(-1).

The same derivation applied to one branch, with every outside spin fixed, gives
p_i <= 1-product_{e in T_i}[1+exp(-2 beta delta_e)]^(-1). Therefore
P(any broken) <= sum_i p_i <= sum_e exp(-2 beta delta_e).
No global energy range, logical gap or partition function is needed. The bound
is informative for frustrated ordinary logical models as well as special cases.
It need not be tight, and a smaller upper bound alone does not order actual
chain-break probabilities.

Conditioned on all branches consistent, the root-spin law is EXACTLY the
logical Gibbs law exp(-beta alpha E_I)/Z_I(beta alpha). Consequently the
unconditional root-decoded distribution is within the certified chain-break
probability in total variation of this logical Gibbs law. If G is the possibly
degenerate logical ground-state set with energy E0 and degeneracy g0, then

    g(t)=g0 exp(-t E0)/Z_I(t),    g'(t)=g(t)[<E_I>_t-E0] >= 0.

Thus alpha orders conditional equilibrium ground-state success for a fixed
logical model and beta. An embedding with alpha no smaller and a defect budget
no larger preserves the lower bound (1-epsilon)g(beta alpha) on consistent
optimal readout. Computing g is not required. Neither this bound nor conditional
ordering orders unconditional actual readout success, mixing time, finite-time
quantum annealing, or logical-observable success.

## 4. Optional nonzero transverse field: local quantum correction

For the Hamiltonian H=E(Z)-sum_q Gamma_q X_q at equilibrium, fix a branch C and
remove only its driver V_C=-sum_{q in C} Gamma_q X_q to obtain H0. Other branches
may retain arbitrary transverse drivers. H0 is block diagonal in the classical
spins of C. Repairing a C-block changes the outside bath Hamiltonian by an
operator bounded below by 2 sum_wall delta_e times identity. Eigenvalue minmax
then bounds its partition trace by the repaired block trace times
exp(-2 beta sum_wall delta_e). Therefore the single-branch classical bound p_C
continues to hold for H0, even with the outside quantum bath.

Let v_C=||V_C||=sum_{q in C}|Gamma_q| and F_C project onto broken configurations
of C. U_C=product_{q in C} Z_q commutes with H0 and F_C and anticommutes with
V_C. Every odd order in the Dyson series for
Tr[F_C exp(-beta(H0+lambda V_C))] therefore vanishes. Schatten Holder applied
to each ordered product bounds its absolute trace by Z0 v_C^k; the simplex
volume is beta^k/k!. The total numerator change is at most
Z0[cosh(beta v_C)-1]. Partition trace Z(lambda) is convex and even in lambda,
so Z(1)>=Z(0). Equivalently, Gibbs variational applied with rho0 gives
logZ1>=logZ0-beta Tr(rho0 V_C)=logZ0, since U symmetry forces that trace to zero. It follows that

    P_H(C broken) <= p_C + cosh(beta v_C)-1.

The optional alternative correction sqrt(beta v_C) follows from
D(rho0||rho1)<=2 beta v_C and quantum Pinsker. Indeed
D=beta Tr(rho0 V_C)+logZ1-logZ0, and operator-order/eigenvalue bounds
give |logZ1-logZ0|<=beta v_C while |Tr(rho0 V_C)|<=v_C.
Pinsker bounds outcome TV by sqrt(D/2). Take the smaller correction and
cap each branch at one; then union over branches. Singleton branches never
break and are excluded. This is a quantum equilibrium chain-consistency bound,
not an equality of conditioned quantum and classical logical laws. For large
transverse fields it correctly becomes inconclusive. Numerically stable
2*sinh(x/2)^2 computes cosh(x)-1; independent checks use outward rounding.

The terminal-equilibrium assumptions are essential. A standard transverse-field
schedule beginning in |+> and ending at Gamma=0 does not by itself imply this
Gibbs distribution. We provide no bath/mixing-time theorem and no finite-runtime
success comparison. The evaluator accepts declared beta and Gamma rather than
assuming a device temperature or freezeout point.

## 5. Certificate-driven programming and search

For K total tree edges and requested epsilon, choose

    d=log(K/epsilon)/(2 beta),  F_e=alpha L_e+d.

For K=0 take d=0. Then sum_e exp(-2 beta d)=epsilon, while the global product
bound is usually slightly smaller. Maximize alpha>0, capped at 1, subject to the
physical h, J and signed coupling-group constraints. Every programmed
coefficient is affine in alpha, so each range is a one-dimensional interval
constraint and their intersection gives the largest feasible alpha. If the
intersection is empty, return inconclusive/infeasible-for-this-certificate;
this is not an impossibility proof for other embeddings or programming choices.

The main model uses illustrative h in [-4,4], J in [-1,1] and signed group sums
in [-13,10]. The actual ideal-Zephyr Ocean group lists are saved. These are
parametric research constraints, not a downloaded Advantage2 device profile.
A device export would replace ranges, target defects and groups; all chain and
reduction coefficients must be included. Each saved physical witness provides
all coefficients, offsets, roots, trees, margins and group sums. Floating-point
program values are treated as exact binary rationals in independent audits;
analytical statements concern those actual coefficients after their actual
loads and margins are recomputed.

The search generates an eight-seed minorminer candidate pool, evaluates every
candidate, and freezes the first-valid candidate's alpha as the quality floor.
Guided selection minimizes qubits among candidates preserving that floor and
the 95% consistency certificate. A graph-valid one-qubit-deletion refinement
accepts only moves preserving the floor. Controls include the same-pool
unconstrained minimum-qubit candidate and unconstrained graph-valid deletion.
Thus compactness gains are measured against an already compact automatic
mapping, not against a large clique template. A conservative scale floor can
prevent all additional deletion; this is reported as a limitation.

## 6. Costs and reuse

Normalize/compile H in O(n+m+nnz(H)) arithmetic operations and memory (sorting
supports adds their local sorting cost). Logical variables/edges are
O(n+m+nnz(H)); rational numeric-certificate bit complexity also depends on
input precision. Generic minor search is heuristic with explicit fixed timeout;
no polynomial fit guarantee is claimed. Nlogical>Ntarget is a certified count
obstruction; an empty heuristic return is only search failure. The program
currently uses the inherited adapter's node/edge count checks and records them.

Given a valid embedding, scan occupied target adjacency for contacts in
O(Delta_T*Nphysical), construct tree/centroid/subtree loads in O(Nphysical),
and intersect ranges in O(Nphysical+physical_contacts+total_group_incidence).
On bounded-degree Zephyr with cached group incidence this is linear in target
and output size; the present implementation scans the cached full group list
for every candidate, so its actual bound includes O(|E_T|). No Hilbert-space
matrix or decoding solve occurs in evaluation. Storage is linear in physical
program and group lists. The K-edge certificate costs O(K); local quantum
corrections cost O(Nlogical). A deletion pass tests O(Nphysical) possible moves;
naive connectivity/contact checks and reallocation make its total cost quadratic
or worse in branch size, rather than the evaluator's linear cost. Timings and
proposal counts are charged separately.

For fixed H, cache the structural QUBO envelope and embedding; syndrome changes
only final parity factors. Updating s,w within a fixed M>sum|w| envelope costs
O(n+m+nnz(H)), then reallocate contacts/fields/chain strengths and reevaluate in
linear target/output cost. A structural envelope embedding covers interactions
that cancel for particular syndromes. If only the actual graph was embedded,
a new edge requires revalidation/routing. Matrix row/column/window changes
require recompiling affected XOR networks and checking all changed contacts;
the implementation conservatively permits full recompilation and search rather
than asserting an incremental speedup. Boundary parities must be supplied as
current decoder input. No future detector outcomes or causal-window claim is
used. Alpha and d may change after any update; a previously valid physical
program cannot simply be reused without reevaluation.

## 7. Relationship to references and limits

The logical compiler and standard whole-load chain condition are inherited from
Lab 002, building on ordinary quadratization and minor-embedding methods.
Choi (2008) and Fang & Warburton (2019) analyze embedding parameter choices;
this report does not assert the rooted load idea is new. The concrete research
result is an implemented, inexpensive endpoint Gibbs fidelity certificate with
parameter-aware constrained compactness selection on diverse sparse inputs.
The proof deliberately avoids adiabatic-gap or real-device-performance claims.

Primary references checked on 2026-10-16:
- https://arxiv.org/abs/0804.4884
- https://arxiv.org/abs/1905.03291
- https://arxiv.org/abs/1406.2741
- https://docs.dwavequantum.com/en/latest/quantum_research/solver_properties_all.html
- https://docs.dwavequantum.com/en/latest/quantum_research/annealing.html
- Generator documentation URLs were attempted but returned429/unavailable; actual generator version, parameters and full graph are verified locally in `results/target.json`.

## 8. Floating arithmetic and event distinctions

The exact conditional Gibbs identity is for the mathematical programmed model.
Actual binary64 contact splitting perturbs it. Final audits interpret every
programmed double as an exact rational, aggregate its fields/contact couplings,
and compare it with the authoritative exact-rational logical compiler model.
If coefficient L1 error is rho, the classical energy perturbation is uniformly
bounded by rho. The Gibbs law differs in TV by at most a conservative
exp(2 beta rho)-1 (or the independent review's sharper beta*rho bound).
The main witnesses have rho<=1.12e-14, so this correction is below4.48e-13.
Static projected ground-state fidelity is independently certified by
2rho<min(alpha*delta_Q,2min ideal_repair_margin), with all physical intervals
checked using exact rational arithmetic. Thus float approximation does not
silently stand in for exact energetic equivalence.

The monotone quantity g(t) is the FULL COMPILED MODEL ground-state mass. A
finite-temperature logical sample with excited, inconsistent auxiliaries can
still project to a minimum-cost feasible original error vector. That larger
projected-error event is not identical to model-ground readout and has no
monotonicity theorem here. Supplemental exact checks report both events.
A first validation assertion conflated them and was corrected; the original
trace is retained as `results/physical_gibbs_attempt1_event_mismatch.txt`.

## 9. Same-sign contact allocation as a sparse LP

For fixed branch roots and trees, give each possible physical contact b for
logical edge ij a nonnegative magnitude x_b, keeping sign(J_ij). Impose
sum_{b for ij} x_b=alpha |J_ij|. Let F_e>=0 be each chain strength. Every
root-to-contact path determines which descendant-load constraints include x_b:

    F_e - sum_{b incident in S_e} x_b >= d.

Root-concentrated fields are alpha*h_i. Each individual coefficient bound and
signed coupling-group bound is linear in x,F,alpha. Maximize alpha with
0<=alpha<=1. The uniform allocation from Sections2–5 is a feasible point of the
ideal LP, so the ideal optimum cannot have smaller alpha. This optimum concerns
only the fixed tree/root, same-sign splitting class, not all embeddings, roots,
field distributions, chain graphs or quantum dynamics.

The implementation constructs a sparse constraint matrix and solves it with
SciPy HiGHS. Its output is a numerical feasible candidate, not an exact optimality
certificate. We reserve1e-8 extra margin and back off alpha by1e-8 before
checking actual coefficients. Final selected witnesses receive exact rational
range, repair and projected-ground-state audits. The reserve can make a
numerical candidate slightly worse than uniform when the ideal optimum ties;
selection falls back to a known valid candidate if the frozen floor cannot be
met. No objective superiority is claimed from solver status alone.

LP size is O(number of contacts+number of chain edges) variables, with one
logical-edge conservation equation, one inequality per chain edge and the
physical programming constraints. Sparse nonzeros include contact-to-root-path
incidence and group incidence; worst-case path incidence can be quadratic in
branch size. General LP solving has polynomial algorithms, while the specific
HiGHS solver has no claimed linear-time bound. Measured cost, not a generic
"cheap LP" label, establishes usefulness in this experiment.

The exact-rational companion for an LP program distributes each authoritative
logical coefficient proportionally to the actual same-sign contact magnitudes;
this preserves the exact logical total and makes its perturbation from the
actual program directly auditable. Zero contacts remain valid unused couplers.
