# Parent adaptive extension: inexpensive finite-forward readout moments

Frozen after the first penalty/forward studies and before this extension's calculations. This is exploratory scientific development, not a new held-out or calibration trial.

The purpose is to test whether a sparse linked expansion provides more informative general-H quantum readout criteria than a global-norm short-time bound. The scored quantities are syndrome feasibility and conditional original-error cost, explicitly proxies supporting (not replacing) the original optimum probability.

1. Derive the log-amplitude expansion through T^4 for the same normalized full forward schedule. With Lf=sum_q[f(z^q)-f(z)], define B=sum_q(Delta_qE)^2, C=sum_q Delta_qE Delta_qLE, D=sum_q(Delta_qE)^3. The proposed log-probability polynomials are q2=LE/12 and q4=-L^3E/1344+LB/2240+C/576-D/1344. Verify independently using exact rational time-polynomial Dyson recursion on small physical models; do not treat agreement of two identical implementations as proof.
2. Compute uniform-feasible moments of q2, q4 and q2² using GF2 kernel characters of original roots and independent characters for unobserved physical spins. This must avoid decoding and Hilbert-space enumeration; show actual complexity and costs. Use all47 successful child main physical programs and all48 parent fixed-coupling pairs. Preserve any computational limit/inconclusive cases.
3. Identify exact T² feasibility/conditional-cost coefficients and T^4 corrections, including tie cases and fixed coordinates. In particular, objective-field amplification changes the conditional-cost coefficient by -(Delta_eta/6)*Var_F(w·e). This is a standard-initial-state quantum statement, not a terminal-Gibbs statement.
4. Independently integrate four representative n6 physical forward anchors (one per generator,seed9611), both programs at T=.05,.25,1,4,16. Check the existing Strang optimum scores and the new feasibility/conditional-cost expansion. Report where the truncated expansion ceases to be informative; do not use an unbounded polynomial outside its verified regime as a certificate.

Only this extension's original-input construction and evaluation use cheap algebra. Exact small-model references are validation only. No claim of global optimality, large-time QA or real-device performance is authorized by positive coefficients.
