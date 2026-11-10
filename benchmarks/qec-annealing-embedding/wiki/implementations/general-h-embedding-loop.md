---
title: General-H evaluation-guided embedding implementation
page_type: implementation
status: active
updated: '2026-10-16'
source_refs:
- labs/lab-002-agent-test-general-h/REPORT.md
- labs/lab-003-surface-code-encoding-comparison/REPORT.md
- labs/lab-004-general-h-evaluation-embedding-loop/REPORT.md
- labs/lab-005-general-h-annealing-relevance/REPORT.md
idea_ids:
- c-004
- k-003
- c-003
topics:
- Quantum Information
---

# General-H evaluation-guided embedding implementation

**Summary**: An exploratory reusable sparse-input constructor combines the inherited faithful XOR model with tree-load thermal evaluation, automatic candidate selection and optional fixed-tree LP contact allocation.

**Sources**: [Lab 004 report](../../labs/lab-004-general-h-evaluation-embedding-loop/REPORT.md), [constructor](../../labs/lab-004-general-h-evaluation-embedding-loop/scripts/construct.py), [theory](../../labs/lab-004-general-h-evaluation-embedding-loop/THEORY.md).

**Last updated**: 2026-10-16.

## Interface and ownership

Input JSON contains n, sparse rows, syndrome and weights; custom targets require explicit coupling groups, with ranges optionally declared. Output contains the compiled model, target, branches/trees/roots, actual physical coefficients, margins, numeric fidelity audit and a success or failure/inconclusive status. Construction consumes no code-family metadata, hidden error witness or decoding optimum. The compiler/adapter are imported read-only from Lab 002 with saved hashes. [Interface](../../labs/lab-004-general-h-evaluation-embedding-loop/scripts/construct.py), [source provenance](../../labs/lab-004-general-h-evaluation-embedding-loop/results/source_provenance.json).

## Evaluation and cost

Rooted branch-tree external loads give repair margins and a product Gibbs defect bound without a decoding solve. Uniform contact splitting reduces scale maximization to affine interval intersection. A sparse LP optimizes same-sign contacts/chain strengths for fixed trees/roots; numerical feasible outputs receive exact-rational audits, without exact LP-optimality or globally optimal embedding claims. Current main evaluation median is 18.6 ms, scanning cached target groups. Generic eight-seed heuristic search and final exact audits are additional costs; no universal polynomial search bound exists. [Mathematics/costs](../../labs/lab-004-general-h-evaluation-embedding-loop/THEORY.md).

## Coverage and limitations

Ordinary main inputs cover four sparse generators and n=16,32,64; selection is matched on common candidate pools. Uniform guided/pruned average physical-qubit reduction is 6.57%; a later LP/pruning combination gives 5.53% on eight new inputs. The main target is ideal Zephyr g=6,t=4 with illustrative parameter limits. Synthetic defects pass, but all tested n=256 searches fail. This is not a live Advantage2 device profile or all-sparse-H fit guarantee. [Results and retained failures](../../labs/lab-004-general-h-evaluation-embedding-loop/REPORT.md).

Independent code validates 313 selected actual programs, including defective graphs and LP refinements. Interval probability comparisons refer to chain-consistent full-QUBO-ground readout; root-decoded optimum comparisons remain inconclusive. Terminal equilibrium and small-driver corrections do not prove finite-time annealing performance. [Independent coefficient audit](../../labs/lab-004-general-h-evaluation-embedding-loop/results/independent_program_audit.json), [interval results](../../labs/lab-004-general-h-evaluation-embedding-loop/results/independent_logical_gibbs_intervals.json).

## Lab005 interfaces and evidence

[Weighted repair witness](../../labs/lab-005-general-h-annealing-relevance/independent/penalty_bound.py) computes exact GF2 repair loads and sufficient parity penalties without weighted decoding. [Sparse quantum moments](../../labs/lab-005-general-h-annealing-relevance/independent/forward_moments.py) and [event selector](../../labs/lab-005-general-h-annealing-relevance/independent/certified_mapping.py) evaluate actual physical readout polynomials/word tails, with explicit inconclusive output. Different physical sizes and root sites are allowed; offsets, couplers, branches and ranges are saved. [Proof and cost scope](../../labs/lab-005-general-h-annealing-relevance/independent/CERTIFIED_EVENT_THEORY.md).

The cost-Lagrange study evaluates375 successful actual candidates from47 compiler models on24 original inputs. Criterion work totals34.67s, median0.608s per pool, excluding prior search and cached standard LP reconstruction. Within balanced compilation,15/23 strictly smaller mappings have actual early-time optimum-event guarantees. All375 actual candidate programs and329 exact selections pass independent audit. [Audit](../../labs/lab-005-general-h-annealing-relevance/results/independent_certified_mapping_audit.json).

[Optimal-set LP](../../labs/lab-005-general-h-annealing-relevance/standard_extension/scripts/optimality_lp.py) only proposes multipliers; exact rational box evaluation validates the bound. Feasible-witness preprocessing is separated into zero-search particular cost and charged bounded descent. It yields1/24 or3/24 standard compact changes, all n16; large cases remain inconclusive. Parent replay checks192 physical root polynomials,960 dual bounds and48 feasible witnesses without an LP/reference solve. [Evidence](../../labs/lab-005-general-h-annealing-relevance/results/independent_standard_extension_audit.json).

Exact rational witnesses use hexadecimal numerator/denominator strings to avoid JSON integer limits. All physical/quantum claims concern the declared ideal model, not a live working graph or QPU. Small exact state/optimum enumeration is reference validation only. Canonical code remains with the lab; [entry points](../../src/README.md) do not maintain duplicate copies.

The [support-growth proof clarification](../../labs/lab-005-general-h-annealing-relevance/independent/PROOF_CLARIFICATION.md) tracks each displacement term’s union of diagonal-function and flipmask support. It corrects an overly strong sentence in the frozen child text while preserving the word recurrence, every constant and every certificate. Frozen child snapshots remain unchanged.

## Related pages

[Thesis](../thesis.md); [frontier](../ideas/research-frontier.md); [stable takeaway](../../note/general-h-tree-gibbs.md); [source entry points](../../src/README.md).
