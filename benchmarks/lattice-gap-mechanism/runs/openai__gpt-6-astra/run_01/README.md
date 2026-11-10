Read [report.md](/app/report.md) for the answer, quantitative constraints, and the limits of the inverse problem.

The measurements support a gapped insulating parent and gapped superconductivity at the two lower fillings. They do not identify all microscopic Hamiltonian coefficients. The report includes an explicit trial Hamiltonian, a diagram of measured phase constraints, spectral illustrations, and a conditional Kramers–Kronig calculation. It distinguishes those calculations from established properties of the samples.

Reproduce the calculations with Python 3.11 and the preinstalled numpy, scipy, and matplotlib:

    python3 fit_spectra.py
    python3 analyze.py

The original input files are unchanged.

- conditional_spectral_fits.png / .pdf: data and conditional STS fits; the BCS fit at filling 0.3 is rejected.
- response_fits.png / .pdf: NMR and resistivity fits, including resistance transition brackets.
- phase_constraints.png / .pdf: the phase information supported by the three crystals.
- conditional_arpes.png / .pdf: illustrative spectral completions; the middle panel is a deliberate counterexample, not predicted flat bands.
- conditional_zeros.png / .pdf: a model-dependent zero curve and a momentum-shifted completion with the same local spectrum.
- kk_validation.png / .pdf: independent KK check and conditional parameter uncertainty.
- spectral_fit_results.json and analysis_results.json: fit parameters, errors, checks, and counterexamples.
- spectrum_a.npz, spectrum_b.npz, and spectrum_c.npz: arrays underlying the illustrative spectral maps.

The illustrative half-filled zero area is about 0.0754 of the Brillouin zone on the Γ side. It is not a measurement-derived area: the report constructs other positive, normalized spectra with the same normalized STS window, the same filling, and different closed zero-curve areas.
