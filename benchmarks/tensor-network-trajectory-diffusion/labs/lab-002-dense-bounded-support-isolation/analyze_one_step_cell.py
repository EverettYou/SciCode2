"""Analyze one complete Lab-002 family/panel validation matrix.

This script reads only learned-controller validation result JSON files. It
requires the five reviewed seeds for full, R2, and R1, verifies that every
training budget completed and that test data remained sealed, then writes the
predeclared paired Student-t intervals and conditional decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parent
RESULTS = LAB / "results" / "one-step-v1"
DECISION_JSON = LAB / "results" / "decision-table-v1.json"
DECISION_MARKDOWN = LAB / "results" / "decision-table-v1.md"
FAMILIES = ("product", "weak-local", "w3")
PANELS = ("coefficient", "depth-gate")
SUPPORTS = ("full", "r2", "r1")
SEEDS = (3301, 3303, 3305, 3307, 3309)
EXPECTED_UPDATES = 128
DELTA_F_THRESHOLD = 0.05
T_CRITICAL_95_DF4 = 2.7764451051977987


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def interval(values: list[float]) -> dict[str, Any]:
    if len(values) != len(SEEDS):
        raise ValueError(f"expected {len(SEEDS)} paired values, got {len(values)}")
    mean = statistics.fmean(values)
    sample_sd = statistics.stdev(values)
    half_width = T_CRITICAL_95_DF4 * sample_sd / math.sqrt(len(values))
    return {
        "values_by_seed": {str(seed): value for seed, value in zip(SEEDS, values, strict=True)},
        "mean": mean,
        "sample_sd": sample_sd,
        "ci95": [mean - half_width, mean + half_width],
    }


def load_matrix(family: str, panel: str) -> tuple[dict[str, list[float]], dict[str, Any]]:
    fidelities: dict[str, list[float]] = {}
    sources: dict[str, Any] = {}
    for support in SUPPORTS:
        support_values = []
        support_sources = []
        for seed in SEEDS:
            path = RESULTS / family / panel / support / f"seed-{seed}.json"
            if not path.is_file():
                raise FileNotFoundError(f"missing reviewed result: {path}")
            record = json.loads(path.read_text())
            expected = {
                "family": family,
                "panel": panel,
                "support": support,
                "seed": seed,
                "status": "completed",
                "completed_updates": EXPECTED_UPDATES,
                "test_evaluated": False,
            }
            for field, value in expected.items():
                if record.get(field) != value:
                    raise ValueError(f"{path}: expected {field}={value!r}, got {record.get(field)!r}")
            fidelity = float(record["validation"]["mean_fidelity"])
            if not math.isfinite(fidelity):
                raise ValueError(f"{path}: nonfinite validation fidelity")
            support_values.append(fidelity)
            support_sources.append(
                {
                    "seed": seed,
                    "path": path.relative_to(LAB).as_posix(),
                    "sha256": sha256(path),
                }
            )
        fidelities[support] = support_values
        sources[support] = support_sources
    return fidelities, sources


def analyze(family: str, panel: str) -> dict[str, Any]:
    fidelities, sources = load_matrix(family, panel)
    full_minus_r1 = [
        full - r1 for full, r1 in zip(fidelities["full"], fidelities["r1"], strict=True)
    ]
    r2_minus_r1 = [
        r2 - r1 for r2, r1 in zip(fidelities["r2"], fidelities["r1"], strict=True)
    ]
    full_r1_summary = interval(full_minus_r1)
    informative = full_r1_summary["ci95"][0] > DELTA_F_THRESHOLD
    if informative:
        q_values = []
        for numerator, denominator in zip(r2_minus_r1, full_minus_r1, strict=True):
            if denominator == 0.0:
                raise ZeroDivisionError("paired recovery score has a zero full-minus-R1 denominator")
            q_values.append(numerator / denominator)
        q_summary = interval(q_values)
        useful = q_summary["mean"] >= 0.5 and q_summary["ci95"][0] > 0.0
        label = "informative"
    else:
        q_summary = None
        useful = None
        label = "uninformative: R1 saturation or unresolved full-head advantage"

    return {
        "family": family,
        "panel": panel,
        "seeds": list(SEEDS),
        "source_records": sources,
        "support_fidelity": {support: interval(values) for support, values in fidelities.items()},
        "paired_differences": {
            "full_minus_r1": full_r1_summary,
            "r2_minus_r1": interval(r2_minus_r1),
        },
        "decision": {
            "delta_f_threshold": DELTA_F_THRESHOLD,
            "informative": informative,
            "label": label,
            "q_computed": informative,
            "q": q_summary,
            "practically_useful_partial_recovery": useful,
            "multistep_eligible": bool(informative and useful),
        },
        "test_evaluated": False,
    }


def render_markdown(table: dict[str, Any]) -> str:
    lines = [
        "# Lab 002 one-step validation decisions",
        "",
        "All intervals are two-sided 95% Student-t intervals over the five paired initialization seeds. Frozen test data were not evaluated.",
        "",
        "| Family | Panel | Full mean | R2 mean | R1 mean | Full-R1 95% CI | R2-R1 95% CI | Decision | q |",
        "|---|---|---:|---:|---:|---:|---:|---|---:|",
    ]
    for key in sorted(table["cells"]):
        cell = table["cells"][key]
        support = cell["support_fidelity"]
        paired = cell["paired_differences"]
        full_ci = paired["full_minus_r1"]["ci95"]
        r2_ci = paired["r2_minus_r1"]["ci95"]
        q = cell["decision"]["q"]
        q_text = "not computed" if q is None else f"{q['mean']:.6f}"
        lines.append(
            "| {family} | {panel} | {full:.6f} | {r2:.6f} | {r1:.6f} | "
            "[{full_lo:.6f}, {full_hi:.6f}] | [{r2_lo:.6f}, {r2_hi:.6f}] | {label} | {q} |".format(
                family=cell["family"],
                panel=cell["panel"],
                full=support["full"]["mean"],
                r2=support["r2"]["mean"],
                r1=support["r1"]["mean"],
                full_lo=full_ci[0],
                full_hi=full_ci[1],
                r2_lo=r2_ci[0],
                r2_hi=r2_ci[1],
                label=cell["decision"]["label"],
                q=q_text,
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=FAMILIES, required=True)
    parser.add_argument("--panel", choices=PANELS, required=True)
    args = parser.parse_args()

    if DECISION_JSON.is_file():
        table = json.loads(DECISION_JSON.read_text())
    else:
        table = {
            "schema_version": 1,
            "kind": "lab002_one_step_validation_decision_table",
            "confidence_level": 0.95,
            "student_t": {"sample_count": len(SEEDS), "degrees_of_freedom": 4, "critical_value": T_CRITICAL_95_DF4},
            "cells": {},
            "test_evaluated": False,
        }
    table["cells"][f"{args.family}/{args.panel}"] = analyze(args.family, args.panel)
    DECISION_JSON.write_text(json.dumps(table, indent=2, sort_keys=True) + "\n")
    DECISION_MARKDOWN.write_text(render_markdown(table))
    print(json.dumps(table["cells"][f"{args.family}/{args.panel}"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
