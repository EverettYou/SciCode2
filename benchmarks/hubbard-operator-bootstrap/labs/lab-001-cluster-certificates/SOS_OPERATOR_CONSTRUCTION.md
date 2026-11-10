# Relating moment certificates to the requested operator subspace

The moment SDP and a lower-bound certificate for the literal operator-space
relaxation should be distinguished. The P/Q/G constraints are degree-two Gram
constraints. T1 and T2 anticommutator constraints are sums of Gram matrices:
retaining only their degree-four sum avoids introducing degree-six moments.
Their SDP optimum need not equal the full cubic operator-space optimum.
Nevertheless every dual lower bound is a lower bound for the full operator-space
relaxation, because its positive terms are sums of squares of actual operators.

Take the linear span of the following seed operators, including their spatial
D4 and spin-interchange orbits, and the identity:

- Linear annihilation and creation operators.
- Pair annihilation and creation operators used by P and Q.
- Particle-hole bilinears used by G.
- Selected triple annihilation operators and their adjoints for T1.
- Selected cubic c_a^dagger c_b^dagger c_c operators, or the declared linear
  combinations of these words, and their adjoints for T2/T2'.

Translation acts diagonally by phases on the momentum operators, so taking the
translation closure does not increase their linear span. D4 and spin interchange
must include any omitted cone-orbit representatives. This closure permits
symmetrizing an arbitrary feasible functional without increasing its energy.
All these operators act on the original fermionic Fock space. Their net spin
and particle-number charges determine the symmetry blocks of their Gram matrix.

For T1, let A_i be the selected triple annihilators. A positive dual matrix
Y=B B^T gives

sum_ij Y_ij (A_i^dagger A_j + A_j A_i^dagger)
 = sum_r [(sum_i B_ir A_i)^dagger(sum_i B_ir A_i)
          +(sum_i B_ir A_i^dagger)^dagger(sum_i B_ir A_i^dagger)].

The displayed identity uses real coefficients; all data in this benchmark are
real after the valid antiunitary symmetry average. The degree-six terms cancel
as operator identities, independently of the state.

For T2', let A_i be cubic creators and B0 the declared linear augmentation.
For each column of a dual Gram factor, the square operators are

Q_r = sum_i B_ir A_i + B_last,r B0,
R_r = sum_i B_ir A_i^dagger.

The T2' block is the Gram matrix of (A_i,B0), plus the transposed Gram matrix of
(A_i^dagger,0). Hence its dual contraction is sum_r(Q_r^dagger Q_r +
R_r^dagger R_r). Integer little-group projections simply replace these operators
by the declared real linear combinations. Any such projection is physically
valid; complete character bases additionally preserve the entire source cone.

The exact verifier's coefficient residual correction also has an explicit SOS
interpretation. Let P and Q be any two pair annihilators, so that
Gamma=<P^dagger Q>. Then

1 +/- Re(P^dagger Q)
 = 1/2 [(P +/- Q)^dagger(P +/- Q)
        +(1-P^dagger P)+(1-Q^dagger Q)].

For P=c_b c_a with a!=b,

1-P^dagger P = (1-n_a)+n_a(1-n_b)
 = (c_a^dagger)^dagger c_a^dagger
   +(c_b^dagger c_a)^dagger(c_b^dagger c_a).

Similarly 1-n_a is a creation-operator square and 1+n_a is the sum of the
identity square and an annihilation-operator square. Thus all coordinate bounds
|n_a|<=1 and |Re Gamma|<=1 follow from the listed operator space, and every
residual term r_j x_j+|r_j| is itself a positive SOS combination. No full-state
positivity assumption is needed to justify the coefficient residual correction
inside that operator-space relaxation.

Fixed-number contraction equalities hold as exact operator identities after
compression to Nup=Ndown=8. Symmetry constraints can be justified by twirling
the state, or equivalently by twirling the complete SOS certificate. The latter
produces a certificate on the original fixed-number sector and uses the symmetry
closure of the seed operators above.

A spin-singlet equation has a different status: S^2=0 is not an identity on the
specified fixed-number sector. Imposing it requires a separate theorem that a
spin-singlet physical ground state exists. A singlet-constrained result should
therefore be reported as a theorem-backed ground-sector refinement, and should
not be identified with the original-P operator-space optimum without this
explicit distinction.
