# Isolated relative-event finite-forward extension

Read `RESEARCH_REPORT.md` for all ordinary-instance outcomes and `THEORY.md` for
the proof. Protocols predate their corresponding result inspection. This branch
is separate from the frozen Lab005 main snapshot; it reuses parent-owned actual
programs without changing them. It is continuing reference research, not a new
blind test or calibration.

From this directory, reproduce exact inequalities and local algebra checks:

```sh
python3 scripts/relative_event.py
python3 scripts/word_majorant.py
python3 scripts/check_words.py
```

These use Python standard-library exact rational arithmetic. The 48 parent
inputs live in `../results/forward_ordinary/`; each input file is SHA256-hashed
in the extension results. The extension performs no embedding search, original
optimum solve or ordinary-size Hilbert-space simulation. Rerunning overwrites
this branch's own results only.

The callable tail API is:

```python
from fractions import Fraction
from word_majorant import schedule_coefficients, remainder

C = schedule_coefficients(n, 12)  # cache by original readout size n
R = remainder(n, gE, T, C, K=12, through_order=4)
```

Here `gE` and `T` are Fractions. `R` bounds the relative even event tail after
T4, retaining majorants C6,...,C12 and the generic tail beyond12. It returns
`None` outside `(1+gE)*T<1`. Use `through_order=2` for the original certificate,
which includes C4. This API bounds arbitrary original-root events relative to
their uniform initial mass; it does not supply their low-order coefficients.
All local terms and support counts refer to the full physical program.

Saved exact fractions use objects with `numerator_hex` and `denominator_hex`.
Recover one using:

```python
Fraction(int(value['numerator_hex'], 16), int(value['denominator_hex'], 16))
```

This avoids Python/JSON's decimal integer digit limits. The first serialization
failure is retained in `results/attempt1_integer_serialization.txt`.

`results/summary.json` retains the simple support-relative branch and global
controls. `results/word_summary.json` contains all refined outcomes;
`results/word_majorant/` contains exact program-specific witnesses.
`results/exact_word_checks.json` is an independent displacement-matrix Dyson
check. `results/independent_word_crosscheck.json` records agreement with the
parent's separate explicit-word integration. Small checks validate formulas;
the 48 ordinary sparse-H inputs supply coverage.

The guarantees concern actual ORIGINAL-ERROR feasible-optimum probability under
the stated finite-forward closed quantum model. Certified durations remain very
early and relative probability gains tiny; no useful moderate-time or QPU
success claim follows. The extension does not modify the main lab report,
manifest or prior labs. Its own manifest records this isolated snapshot.
