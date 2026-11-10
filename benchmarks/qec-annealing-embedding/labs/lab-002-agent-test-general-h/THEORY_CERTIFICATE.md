# A polynomial certificate for frozen encoded variables during a transverse-field hold

Status: independently derived theorem and reproducible small-matrix checks for
this trial. This is a conditional, closed-system, finite-time result. It is not a
claim about the success of a complete forward anneal or a real noisy processor.

Research subtask started 2026-10-07 at approximately 20:11 UTC. The first recorded
clock read was 20:12:01 UTC. The inherited trial deadline is 21:55:30 UTC.
Initially only the lab's `prompt.md` and public sources were read. After deriving
the theorem, the parent authorized an independent review of this trial's new
`scripts/compiler.py`, `scripts/exact_pipeline.py`, and their `embedding.py`
helpers; no prior lab or author guidance was used.
Scientific-trial child session ID:
`01a117fe-0bfd-7be3-bceb-77efccafaa8b`.

## Model and inexpensive inputs

Fix a valid minor embedding with disjoint connected branch sets
\(C_1,\ldots,C_L\), using \(N=\sum_i |C_i|\) physical qubits. At a fixed
anneal coordinate, hold the transverse-field Hamiltonian constant for time \(t\):

\[
 H=C+D-\Gamma\sum_{q=1}^N X_q,\qquad
 C=\sum_{qr\in E_{\rm chain}} c_{qr}(1-Z_qZ_r),\quad c_{qr}>0.
\]

Here \(D\) contains all programmed problem fields and inter-branch couplings and
is diagonal in the computational basis. Constants are discarded. Use
\(\hbar=1\), so time is measured in reciprocal units of Hamiltonian energy.
This is exactly the prompt's Hamiltonian up to a scalar offset when

\[
 \Gamma=A(u_*)/2,\quad c_{qr}=B(u_*)|J^{\rm chain}_{qr}|/2,\quad
 D={B(u_*)\over2}\left(\sum_qh_qZ_q+
             \sum_{qr\in E_{\rm problem}}J_{qr}Z_qZ_r\right).
\]

The programmed coefficients in these equations already include *every*
hardware rescaling factor. A large unscaled chain penalty does not imply an
arbitrarily large physical \(c\) under a finite coupling range.

Let \(P\) project onto states in which every branch set is constant and set
\(Q=I-P\). Its rank is \(2^L\); it includes all encoded assignments, not just
the optimum. For each nonsingleton branch, compute its minimum positive weighted
cut \(\kappa_i=\min_{\varnothing\ne S\subsetneq C_i}
\sum_{qr\in\partial S}c_{qr}\). Define

\[
 \Delta=2\min_{i:|C_i|>1}\kappa_i,\qquad
 R=\sum_q|d_q|+\sum_{qr}|d_{qr}|\ \geq\ \|D\|.
\]

Then \(C P=0\) and \(QCQ\succeq\Delta Q\). Write \(n_1\) for the number
of singleton branches, \(n_2\) for the number of branches of size two, and
\(M=N-n_1\), the number of physical qubits in nonsingleton branches. Define

\[
 g=\Delta-2R-\Gamma(N+n_1),\qquad
 b=\Gamma\sqrt{M+2n_2}.
\]

The evaluator requires \(g>0\); otherwise it returns **inconclusive**, not a
claim that the embedding has bad dynamics. With no nonsingleton branches,
\(P=I\) and there is no approximation error. With \(\Gamma=0\), all encoded
computational-basis probabilities are exactly frozen without needing \(g>0\).

## Finite-time theorem

If \(g>0\), set \(s=b/g\). For every \(t\geq0\),

\[
 \left\|\left(e^{-itH}-e^{-itPHP}\right)P\right\|
 \leq \varepsilon(t)
 :=2s+t\,{b^2\over g}\exp(2s).
 \tag{1}
\]

The exponential of \(PHP\) on the right is restricted to \(P\). This estimate
holds uniformly for *every* initial pure state in \(P\), and by purification
for every density matrix \(\rho=P\rho P\). It does not assume a unique
logical or physical ground state. One may cap an operator-norm bound at two and
a probability bound at one.

On the encoded space the first-order Hamiltonian is exactly

\[
 PHP=D_{\rm logical}-\Gamma\sum_{i:|C_i|=1}X_i^{\rm logical}.
 \tag{2}
\]

Consequently, if \(F\) is any physical measurement effect whose restriction to
\(P\) is a diagonal event depending only on nonsingleton logical variables,
then for every such initial state

\[
 |\operatorname{Tr}(F e^{-itH}\rho e^{itH})-
            \operatorname{Tr}(F\rho)|\leq\min(1,\varepsilon(t)).
 \tag{3}
\]

The definition of \(F\) on broken-chain states can be arbitrary. Thus the
bound applies both to strict consistent-ground-state success and to any fixed
chain recovery rule agreeing on consistent states. If every branch is a
nonsingleton, \(F\) may be the projector onto *all* optimal decoding assignments,
including any degeneracy. Starting outside that set, the stronger bound
\(p_{\rm repair}(t)\leq\min(1,\varepsilon(t)^2)\) holds. More generally this
square bound applies to every such event with zero initial probability. Leakage
itself has probability at most \(\min(1,\varepsilon(t)^2)\).

This provides a substantive negative certificate: very robust chains can make
a hold incapable of appreciable logical correction. Conversely, for a state
whose encoded values should remain fixed it is a retention certificate. A
smaller bound alone is not an ordering of full annealing success.

## Proof, with explicit constants

Put \(A=PHP\), \(F_Q=QHQ\), and
\(H_0=A\oplus F_Q\). Write \(V=H-H_0\); this is purely block off diagonal.
First,

\[
 \lambda_{\max}(A)\leq R+\Gamma n_1,\qquad
 \lambda_{\min}(F_Q)\geq\Delta-R-\Gamma N.
\]

Their ordered spectral separation is therefore at least \(g\). These coarse
bounds use only coefficient norms, not exponentially costly diagonalization.

Second, the exact off-diagonal norm is \(\|V\|=b\). To see this, set
\(B=QHP\). A physical \(X_q\) on a singleton never leaves \(P\); every
\(X_q\) on a nonsingleton does. In
\(B^\dagger B=\Gamma^2\sum_{q,r}P X_qQX_rP\), an encoded state can return
to \(P\) after two flips only when \(q=r\) or when \(q,r\) are the two
vertices of a size-two branch. Hence

\[
 B^\dagger B=\Gamma^2\left(MP+2\sum_{i:|C_i|=2}X_i^{\rm logical}\right).
\]

The logical \(X_i\)'s commute and have a simultaneous all-positive eigenstate,
giving \(\|B\|=\|V\|=\Gamma\sqrt{M+2n_2}\). This calculation does not
make an assumption about the allocation of the diagonal coefficients.

Choose \(a=R+\Gamma n_1\). The Sylvester equation

\[
 F_QY-YA=B
\]

has the solution
\(Y=\int_0^\infty e^{-(F_Q-a)r}B e^{(A-a)r}\,dr\), with
\(\|Y\|\leq b/g\). Define the anti-Hermitian operator

\[
 S=\begin{pmatrix}0&-Y^\dagger\\Y&0\end{pmatrix},\qquad
 \|S\|=\|Y\|\leq s.
\]

Then \([S,H_0]=-V\). The convergent finite-dimensional conjugation expansion
has an exact first-order cancellation:

\[
 e^SHe^{-S}=H_0+E,\qquad
 E=\sum_{k=1}^\infty {k\over(k+1)!}\operatorname{ad}_S^k(V).
\]

Since \(\|\operatorname{ad}_S^k(V)\|\leq(2s)^k b\) and
\(k/(k+1)!\leq1/[2(k-1)!]\),

\[
 \|E\|\leq bs e^{2s}={b^2\over g}e^{2s}.
\]

The unitary \(e^S\) satisfies \(\|e^S-I\|\leq\|S\|\). Duhamel's
formula bounds the difference between the evolutions of \(H_0+E\) and
\(H_0\) by \(t\|E\|\). The two conjugating unitaries contribute at most
\(2\|S\|\), proving (1). Equation (2) follows by projecting individual
physical flips. In the ideal evolution all events described in (3) commute
with \(A\), so their probabilities are constant. The trace distance of pure
states is at most their vector-norm distance, and purification gives the same
measurement bound for mixed states. Projection onto \(Q\) gives the leakage
bound. If an event has zero initial probability, its positive square root
annihilates the ideal evolved state. Applying that contraction to the vector
difference gives the stronger squared bound. No adiabatic theorem or
nondegenerate perturbation formula is used.

For multiple piecewise constant holds with the same embedding, one can telescope
the operator bounds against the ideal projected evolution to obtain a sum of
the individual \(\varepsilon_j\). Each ideal intermediate state remains in
\(P\). This is mathematically valid but can be loose; it does not cover a
continuous schedule without an independently controlled discretization error.

A limited extension admits initial broken-chain probability
\(\eta=\operatorname{Tr}(Q\rho)\). For a computational-basis event with zero
initial probability, and whose restriction to \(P\) is frozen as above,
\(p(t)\leq\min[1,(\varepsilon(t)\sqrt{1-\eta}+\sqrt\eta)^2]\).
Decompose a purification into its orthogonal \(P\) and \(Q\) components;
the event annihilates the ideal evolution of the former, while unitary
evolution preserves the latter's norm. The triangle inequality proves the
claim. Thus a certified or independently estimated initial leakage bound can
be incorporated, although this work does not infer that bound from a previous
uncontrolled annealing segment.

## Computational cost and selection rule

Given the embedding and coefficient allocation, \(R,N,n_1,n_2,M\) take
\(O(N+|E|)\) time and linear input memory. For tree branches, the minimum cut
is the minimum edge weight, so the entire evaluator is linear in programmed
model size. For arbitrary positive-weight connected branches, a global weighted
min-cut algorithm gives a polynomial certificate; a simple dense Stoer-Wagner
implementation costs \(O(\sum_i|C_i|^3)\) time and
\(O(\max_i|C_i|^2+N+|E|)\) memory. Alternatively, twice the minimum positive
edge weight in a selected spanning tree is a valid inexpensive lower bound on
\(\Delta\). Replacing \(\Delta\) by a lower bound preserves the theorem.

The public function `pause_certificate` in `scripts/theory_checks.py` uses the
exact tree minimum edge or the minimum edge of a connected cyclic branch as a
certified cut lower bound. It labels these cases separately; it does not present
the cyclic lower bound as an exact minimum cut. Thus its graph traversal and
number of rational arithmetic operations are linear in programmed model size.
An exact weighted min-cut could improve the bound at the polynomial cost above,
but is not used by this implementation. It returns parameters, conditions, and
bounds separately. No eigenvalue problem occurs in evaluation.
The exponential matrices in that file are validation only and scale as
\(O(2^{3N})\) time and \(O(2^{2N})\) memory.

## Rigorous numerical evaluation

The default evaluator interprets every supplied finite binary64 coefficient and
duration as its exact rational value. It sums \(R\), obtains the cut lower bound,
and tests \(g>0\) in rational arithmetic. A JSON `rational_g_witness` records
the exact numerator and denominator, while `numeric_certification` identifies
the arithmetic. A floating display of \(R\) is rounded upward and displays of
\(\Delta\) and \(g\) downward; these displays are not used in the decision.

For \(b^2=\Gamma^2(M+2n_2)\), an integer square-root calculation produces
a dyadic upper bound \(\bar b\) with 128 significant bits. This is relative
precision, so it also handles subnormal binary64 drivers. Put
\(\bar s=\bar b/g\). If \(2\bar s\geq1\), the evaluator returns the
universal probability bound one without evaluating an exponential. Otherwise,
for \(x=2\bar s<1\), it uses the exact rational upper bound

\[
 U_{24}(x)=\sum_{k=0}^{24}{x^k\over k!}
       +{x^{25}/25!\over1-x/26}\ \geq\ e^x.
\]

The omitted series has successive ratios at most \(x/26\), proving the tail
bound. The evaluator then computes
\(\bar\varepsilon=2\bar s+t(b^2/g)U_{24}(2\bar s)\) and its square as
rationals. Only after clipping to the universal bounds are the reported numbers
converted to binary64, with an exact rational comparison and `nextafter` ensuring
outward rounding. Large intermediate exponential fractions are not serialized.
Finite energy statistics outside the binary64 display range use JSON null when
no finite outward-rounded display exists; the exact gap witness and decision
remain available. Bit-operation costs are polynomial in the input bit length;
the operation-count claim above is not a unit-cost claim for unbounded integers.

Boundary checks cover a zero gap, its two neighboring input values, subnormal
positive probabilities, and near-maximum finite magnitudes. For example,
\(c=1\), fields \((0.99,10^{-17})\), and \(\Gamma=0.01\) produce a
naively rounded gap \(+1.7347\times10^{-17}\), although the gap for the exact
binary64 inputs is negative. The rational evaluator correctly returns
inconclusive. A subnormal nonzero upper probability rounds upward to the least
positive binary64 value rather than incorrectly becoming zero.

For a proposed pause intended to repair an encoded variable, reject a candidate
if its certified success upper bound lies below an independently established
success lower bound for another candidate. If the gap condition fails, or
the intervals overlap, report an inconclusive comparison. The construction
algorithm need not alter its general sparse-matrix input interface to use this
certificate; only the theorem's useful regime is restricted.

## Explicit decoding comparison on a common target

Use \(H=[1\ 1]\), \(s=1\), and \(w=(0,0)\), so both \(e=01\) and
\(e=10\) are optimal. The quadratic penalty
\(Q(e)=2J(e_1+e_2-1)^2\), with \(e_i=(z_i+1)/2\), is \(J+Jz_1z_2\).
It represents the required decoding problem faithfully for every \(J>0\).

Take a physical four-vertex path \(0-1-2-3\). The native embedding uses
singletons 1 and 2; the other embedding uses branches \(\{0,1\}\) and
\(\{2,3\}\), with problem interaction on edge \(1-2\). Both have the
same logical problem coefficient \(J=10^{-4}\), transverse field
\(\Gamma=0.02\), field range \(|h|\leq1\), coupler range \(|J_{qr}|\leq1\),
and the same available target. Embedded chain couplings are \(-K=-1\).
A per-node absolute coupling-group cap of 2 suffices for both; any smaller
provided cap must be checked or the common scale changed. This is a parametric
programming model, not a claim about an exported Advantage2 processor. The
path can be selected from an ideal Zephyr target without adding edges.

Both are initialized in encoded \(e=00\) and held for
\(t=\pi/(2\sqrt{J^2+4\Gamma^2})\), about 39.27. No bath, decoherence,
temperature, control error, or preparation/ramp time is included. For a
reverse-anneal interpretation, these statements are conditional on the state
at the start of the pause. A complete anneal would require analyzing its
preparation and ramps separately.

The native Hamiltonian is
\(H_{\rm native}=JZ_1Z_2-\Gamma(X_1+X_2)\). An exact two-dimensional
bright/dark-state calculation yields

\[
 p_{\rm native}(t)={2\Gamma^2\over J^2+4\Gamma^2}
   \sin^2\!\left(t\sqrt{J^2+4\Gamma^2}\right).
\]

At the selected time this is approximately 0.499997. For the four-qubit
embedding, \(\Delta=2K=2\), \(R=J\), \(N=M=4\), \(n_1=0,n_2=2\),
so \(g=1.9198\), \(b=0.02\sqrt8\), and the theorem gives
\(p_{\rm encoded}\leq\varepsilon(t)^2<0.016477\). Thus the native mapping has
strictly greater finite-time decoding success under the stated protocol, proved
without simulating the embedded dynamics. The success projector includes
both tied optima. Exact simulation in the companion script checks the values.

The strict ordering can also be checked with deliberately loose rational bounds,
without trusting floating-point transcendental evaluations: \(g>1.9\),
\(b<0.057\), \(s<0.03\), \(b^2/g<0.001685\), \(t<40\), and
\(e^{2s}<1/(1-0.06)=50/47\) imply \(\varepsilon<0.132\), hence
\(p_{\rm encoded}<0.018\); the native exact expression is greater than 0.499.

For a second comparison change only the encoded initial state to an optimal
assignment \(e=01\). The native success probability is now
\(1-0.499996875\approx0.500003125\). Apply the zero-initial-event bound to
failure: the encoded success is at least
\(1-\varepsilon(t)^2>0.983523\). Thus the direction of the performance
ordering reverses under a change of initial state, with the same task,
Hamiltonians, target, and pause duration. Larger chains inhibit repair but
protect an answer already present. This is a certified limitation on any
universal preference based only on chain size or final-energy equivalence.

This comparison uses a common problem-energy scale. Maximizing the available
problem scale separately in each embedding changes the Hamiltonians and can
change the comparison. The result does not claim native embeddings always
win or that chain count alone orders performance.

## Reproduction and public resources

From the repository root:

```sh
python3 -B benchmarks/qec-annealing-embedding/labs/lab-002-agent-test-general-h/scripts/theory_checks.py --output benchmarks/qec-annealing-embedding/labs/lab-002-agent-test-general-h/results/theory_validation.json
```

The script emits JSON with environment versions, the exact comparison, and
independent random-matrix checks. It accepts `--output PATH` to save those
results; it does not access another lab or scientific history.

The saved validation run used Python 3.13.2, NumPy 2.2.6, SciPy 1.15.3, and
NetworkX 3.5. It passed 24 generated models with two through six physical
qubits, mixed singleton and nonsingleton branches, weighted trees and cyclic
branches, and four hold times per model. Independent dense-matrix checks tested
the exact off-diagonal norm, the lower block gap, the Sylvester equation, the
conjugation remainder, the uniform dynamical bound, and worst-state leakage.
The maximum ratio of measured state-vector error to its bound was 0.838191;
the maximum conjugation-remainder ratio was 0.948160. The saved script execution
took 0.315 seconds excluding process startup/imports. This is a measured
small-system validation cost, not a large-QPU simulation estimate.

For the explicit parity example, dense evolution found native repair success
0.4999968750, encoded consistent-ground repair success 0.0004932334, and encoded
representative-recovery repair success 0.0012909781, all consistent with the
analytic upper bound 0.0164766888. From an initially optimal state, encoded
consistent-ground retention was 0.9979117909, above its analytic lower bound
0.9835233112. The subsequent rigorous evaluator upgrade preserves these
comparisons and additionally passes the numerical boundary checks described
above. The rational inequalities also independently establish the strict
comparison used in the report.

Public resources consulted on 2026-10-07:

- D-Wave, [Annealing Implementation and Controls](https://docs.dwavequantum.com/en/latest/quantum_research/annealing.html),
  for the normalization of the transverse-field Hamiltonian and the distinction
  between pauses, reverse annealing, and complete schedules.
- S. Bravyi, D. DiVincenzo, and D. Loss,
  [Schrieffer-Wolff transformation for quantum many-body systems](https://arxiv.org/abs/1105.0675),
  Ann. Phys. 326, 2793–2826 (2011), for context on block-unitary effective
  Hamiltonians. The explicit Sylvester/conjugation proof above is given in full;
  no undocumented constant is imported from this reference.
- V. Choi, [Minor-Embedding in Adiabatic Quantum Computation: I. The Parameter
  Setting Problem](https://arxiv.org/abs/0804.4884), for static minor-embedding
  context. Static parameter fidelity is distinct from theorem (1).

The global bandwidth separation \(\Delta>2R+\Gamma(N+n_1)\) is deliberately
conservative. It can fail for useful embeddings, and late holds cannot repair
all the limitations of an earlier anneal. General early-time or open-system
dynamics, a sharp ranking between long chains, and universal forward-anneal
success remain outside this result.
