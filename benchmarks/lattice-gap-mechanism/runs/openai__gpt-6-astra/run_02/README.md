**Deliverables**

Read [report.md](report.md) for the scientific answer. It addresses all five requested inferences, separates measured constraints from model assumptions, and explains why a fully parameterized Hamiltonian and a unique zero-curve area are not determined by the supplied data.

The main numerical results are NMR activation scales \(5.54\pm0.13,\ 2.63\pm0.06,\ 1.735\pm0.039D\), and resistive transition brackets \([0.325,0.400]D\) and \([1.075,1.150]D\). The reported errors are conditional fitting errors; limitations are explained in the report.

- [analyze.py](analyze.py): all analysis and figure-generation code.
- [results.json](results.json): numerical fits, covariances, assumptions, and spectral checks.
- [figures/](figures/): PNG and PDF versions of all plots.
- The original measurements and supplied figures are preserved.

Reproduce the calculation from this directory:

    python3 analyze.py

Dependencies are numpy, scipy, and matplotlib. No external material data or additional packages are needed.

**The ARPES and zero-contour figures are explicitly labeled non-uniqueness examples. They are causal spectral constructions, not predictions of a fitted Hamiltonian or estimates of the oxide's zero-curve area.**
