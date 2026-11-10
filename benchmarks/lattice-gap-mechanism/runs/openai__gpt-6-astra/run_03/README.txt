Start with answer.md.

The report uses measurements.json, which is preserved unchanged. It explains
the most plausible interpretation, fits observable activation energies, and
shows why a uniquely parameterized Hamiltonian and Green-function zero area
cannot be inferred from the supplied local measurements.

Run:
    python3 analyze.py

Dependencies: Python 3.11, numpy, scipy, matplotlib (already installed).

Generated numerical results:
    results.json
    conditional_band_fit.json

Generated figures (each supplied as PNG and PDF):
    activation_fits
    sts_features
    conditional_band_fit
    phase_constraints
    spectral_nonuniqueness
    zero_contour_nonuniqueness

The momentum-intensity and zero-contour examples are constructive demonstrations
of missing information. They are not ARPES predictions of a fitted interacting
Hamiltonian. This distinction is explicit in the report, code, and figures.
