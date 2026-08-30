---
title: Simulation-to-experiment image transfer
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/wang2020mlioi/paper.pdf
idea_ids: []
topics:
- Machine Learning
- Correlated Systems
---

# Simulation-to-experiment image transfer

**Summary**: Physics-informed synthetic labels can train experimental-image detectors when nuisance noise and nonuniversal short-range simulation errors are explicitly controlled.

**Sources**: [Wang et al. (2020)](../../papers/wang2020mlioi/paper.pdf)

**Last updated**: 2026-08-23

---

## Transfer design

The source trains an impurity-localization network on simulated Friedel oscillations, then applies it to voltage-resolved STM maps. Convolutions extract spatial features and attention aggregates structures that persist across voltage, helping distinguish physical impurity signatures from single-image noise [Wang et al. (2020), Figs. 1–3](../../papers/wang2020mlioi/paper.pdf#page=2).

Two interventions address the synthetic–real gap. Gaussian white-noise augmentation prevents reliance on perfectly clean simulations. An entropy penalty on predictions for unlabeled experimental images encourages concentrated locations when incorrect simulated short-range impurity physics otherwise lowers confidence. Both improve agreement with an independently extracted bound-state reference, with the combination performing best in the reported experiment [Wang et al. (2020), Fig. 4](../../papers/wang2020mlioi/paper.pdf#page=4).

## Validation boundary

The experiment covers one Au(111) dataset, a chosen noise family, and a tuned regularization weight. Low predictive entropy is not calibrated correctness and can amplify confident domain-shift errors. A method intended to support or falsify physical theory must therefore separate robustness to nuisance variation from fidelity to the theory-specific universal signal and validate against independent measurements.

## Benchmark hooks

- Generate synthetic images with independently tunable universal tails, short-range mismatch, correlated noise, and instrumental drift.
- Compare white-noise augmentation with learned, colored, and adversarial nuisance models under held-out shifts.
- Measure accuracy and calibration when entropy minimization is applied to unlabeled target data.
- Ablate cross-condition attention to test whether it learns persistent physics rather than shared artifacts.

## Related pages

- [[topics/machine-learning-and-physics|Machine learning and physics]]
- [[topics/correlated-quantum-many-body-systems|Correlated quantum many-body systems]]
- [[papers/wang2020mlioi|Machine learning identification of impurities in the STM images]]
