# Project Sycamore example tasks

This summary preserves the three strong examples and seven rejected examples
provided by the user on 2026-10-16. The task descriptions and rejection reasons
below are user-supplied summaries. The linked prompts, case reports, and final task
remain the primary materials for detailed comparison; their contents have not been
independently checked here.

## Strong examples

### Rigidity transition in an actively remodeling epithelium

**Domain:** Theoretical biophysics. Implement an epithelial vertex model with
active contractility and tension remodeling, then locate its solid-to-fluid
transition using shear modulus and cell diffusivity. The key judgment is how to
measure stiffness and flow in a driven system where standard methods can fail.

[Task prompt](https://drive.google.com/file/d/1hDvdJh5M6xLl7256j7Y54emutjQ0YOi0/view) · [Case report](https://drive.google.com/file/d/1d6npi19qLKbU0-QLHAKS6JYzUuv4OVz5/view)

### Heat transfer between two AlN crystals at sub-20 nm separation

**Domain:** Mechanical engineering. Calculate near-field heat flux between AlN
crystals across vacuum gaps from 20 nm to 0.3 nm using fluctuational
electrodynamics and atomistic phonon calculations. The key judgment is recognizing
where standard electromagnetic theory breaks down below about a nanometre and
accounting for lattice vibrations coupled through ionic Coulomb forces.

[Task prompt](https://drive.google.com/file/d/1l2Lwi6XHJXY-QgjLfXP5uxfYcPhI2WIS/view) · [Case report](https://drive.google.com/file/d/1l6t69L99DrtNF0ctEuSlmCnvZx_ktUkn/view)

### A weighted conformational ensemble of apo adenylate kinase

**Domain:** Structural biology. Build an adenylate-kinase ensemble with molecular
dynamics, umbrella sampling, and maximum-entropy reweighting to fit DEER distance
distributions within a 12-hour GPU budget. The key judgment is diagnosing a missing
conformational state from the misfit and choosing a new sampling coordinate.

[Task prompt](https://drive.google.com/file/d/1cY4M9gGpkLXLn0HR4q6CBXhUpSaV55Q1/view) · [Case report](https://drive.google.com/file/d/1aQ5SWS9bvSesHki1Jok4GnbTxUa1OJsP/view) · [Final task](https://drive.google.com/file/d/1sV5o3ff6Do95FFSEWDJi7QHPDh59xQy7/view?usp=drive_link)

## Rejected examples

The supplied summary says the first four were rejected because of task shape; the
last three were solved autonomously.

| Task | Domain | Supplied rejection reason |
|---|---|---|
| [Mixed-state topological order in a twice-decohered toric code: quantum or classical?](https://drive.google.com/file/d/1mTrsgblm_PHn0JvXRoC_1DXkqez2MH8T/view) | Condensed matter | Hinged on one judgment call: choosing relative entropy or coherent information instead of negativity. After that choice, the model solved the rest in one shot. |
| [Optimizing entanglement from the quantum field](https://drive.google.com/file/d/185RIrbvRpv118tLHmhzyZQHGxzhvGTPX/view) | Quantum information | Too open-ended to grade. |
| [Tissue specificity of tRNA intron splicing in mouse small RNA-seq](https://drive.google.com/file/d/17Qoouq1gIZA2cwtqxXhnCeTtzRuaKnAm/view) | Bioinformatics | Failure depended on very specific domain knowledge; an agent could build the pipeline scaffold quickly (20–30 minutes). |
| [Egg-laying event times for a held-out fly from a six-fly video recording](https://drive.google.com/file/d/1tlvTz6LyW4_k8jCA46QuA5ie0e9JF-K_/view) | Neuroscience | Frame-by-frame event annotation required careful human judgment rather than scientific reasoning. |
| [Spontaneous ferroelectric polarization of (MDABCO)(NH4)I3](https://drive.google.com/file/d/1fO546wXPl7NER4doEtZ2N1-nqStLSsV7/view) | Materials science | Both test runs got the correct polarization; the prompt fixed the functional, pseudopotentials, cutoffs, and other recipe details. |
| [Cooperative quantum energy teleportation under a classical-communication budget](https://drive.google.com/file/d/1nUwY0MbkcuY33AjRTTcguMkeYStBV_G3/view) | Quantum information | All ten test runs agreed on the answer. |
| [Decoherence transition of the Z₃ toric code under particle–hole asymmetric phase noise](https://drive.google.com/file/d/1CUnO7-1IRq-T7SqbrOTCDzrBaFNqAxuD/view) | Condensed matter | The model solved it in the first round of test runs. |

## Use in candidate screening

Use these summaries to prompt the right questions: does the task require multiple
consequential scientific judgments; can an answer be checked; is the work more
than standard pipeline construction; does the prompt leave the substantive method
open; and is the task still solvable with practical resources? Read the linked
primary materials when accessible before making a close comparison. These examples
are guidance, not a mechanical acceptance checklist.
