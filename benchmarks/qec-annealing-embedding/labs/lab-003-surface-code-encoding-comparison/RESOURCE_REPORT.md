# Surface-code Ising resource comparison

The stabilizer/dual encoding used substantially fewer physical qubits than the
error-variable/XOR encoding on every tested patch. This persists when both use
the **same generic minorminer procedure**, and when the direct encoding's
penalty is improved using the patch geometry. These are embedding and coefficient
allocation results, not QPU sampling or annealing-speed results.

## Controlled comparison

The code is an unrotated planar relative-homology surface-code patch of width
and height `d`, with ideal syndrome measurements and unit positive error weights.
One Pauli error sector is considered. It has

\[
n_e=d^2+(d-1)^2,\quad m=d(d-1),\quad n_{\rm stab}=d(d-1),\quad k=1.
\]

The direct construction uses the previous lab's sequential XOR/carry compiler.
The dual construction uses a canonical syndrome representative plus independent
stabilizer variables, and solves both logical classes `ell=0,1`. This is a
comparison of two encodings of the same minimum-error-weight task. It does not
compare maximum-probability logical classes under degeneracy, noisy syndrome
histories, or correlated X/Z errors.

Both structural interaction graphs are submitted to `minorminer.find_embedding`
on the same ideal Zephyr `Z_(6,4)` graph: 1,248 qubits, 11,400 couplers, no defects.
Seeds are 11, 29 and 47; timeout is 5 seconds and tries is 4. Node labels,
structural edges, complete target graph, every embedding, physical coefficients,
and package versions are saved. Isolates are retained. Structural graphs allow
the same embedding to be reused across syndrome-dependent coefficient changes
and both dual logical classes.

One reproducible syndrome is used per patch: independent Bernoulli(0.1) error
bits from NumPy seed `3100+d`, with the first error bit forced to one, followed
by syndrome computation. Only the syndrome is supplied to either encoding.
Qubit counts concern the common structural graph; the coefficient tables are
for these particular syndrome instances. Their ranges vary embedding seeds,
not a sampled syndrome population.

The direct global and local penalty variants reuse **exactly the same embedding**
for each seed. Both dual classes also reuse one embedding. No universal-clique
template is used in this comparison.

## Qubit and chain counts

| `d` | Original error bits | Direct Ising spins | Dual spins per class | Direct physical qubits, median [range] | Dual physical qubits per class, median [range] | Median ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 5 | 9 | 2 | 9 [9–10] | 2 [2–2] | 4.50 |
| 3 | 13 | 29 | 6 | 31 [30–32] | 6 [6–6] | 5.17 |
| 5 | 41 | 105 | 20 | 121 [119–143] | 20 [20–20] | 6.05 |
| 7 | 85 | 229 | 42 | 319 [316–339] | 44 [44–49] | 7.25 |
| 9 | 145 | 401 | 72 | 639 [581–646] | 80 [76–80] | 7.99 |

All 30 searches returned valid embeddings. The maximum chain length ranges over
the three seeds were direct 1–2, 2, 2–3, 4, 5–9; dual 1, 1, 1, 2, 2 respectively.
At `d=5`, the dual graph embeds with every variable on one physical qubit. At
`d=9`, the direct graph requires appreciably more routing than the dual graph.

These resource savings have a simple logical origin. The direct construction
introduces `4(d-1)^2` auxiliary bits, so it has

\[
N_{\rm direct}=6d^2-10d+5,\qquad
N_{\rm dual}=d(d-1).
\]

Its structural edge count is `(d-1)(13d-12)`, compared with
`2d^2-4d+1` for the dual grid. Thus the direct-to-dual logical-spin ratio tends
to six for one logical class. The measured physical ratio also reflects the
heuristic's routing overhead. These finite-size observations do not prove an
asymptotic embedding overhead or globally minimal qubit count.

**Two-class accounting matters.** The direct encoding covers both logical
classes in one optimization. The dual approach needs two class-conditioned
anneals and then comparison of the decoded error weights. Sequential execution
uses the table's one-class footprint twice. Twice that footprint gives nominal
parallel resource counts 4, 12, 40, 88 and 160, still below the direct medians.
However, two disjoint simultaneous placements were not constructed, so these
doubled counts are bookkeeping estimates, not verified parallel embeddings.
The distinction is between logical classes inside one Pauli error sector;
decoding both X and Z sectors adds the corresponding work to either method.

## Coefficient range comparison

All models use the same unit error weights. Two exact direct penalties are
included:

- Global sufficient penalty `Lambda=n_e+1` from the generic compiler.
- Geometry-aware sufficient penalty `Lambda=R+1`, where `R` is the maximum,
  over checks, of the minimum unit-weight path to a rough boundary. Here
  `R=floor(d/2)`. The repair argument is in the lab's theory analysis.

Fields are divided uniformly over each physical branch. Each logical coupling
uses one contact; a BFS spanning tree within each branch carries ferromagnetic
strength `K_i=|h_i|+sum_j|J_ij|+1`. This is a sufficient ground-state-preserving
chain prescription, **not optimized chain tuning**.

One positive scale multiplies every field, logical coupling, chain coupling and
constant. Illustrative common ranges are `h in [-1,1]`, `J in [-1,1]`, and signed
Zephyr coupling-group sums in `[-13,10]`. These are controlled parametric
constraints, not a property export from a live device. The largest permitted
scale is used, including values greater than one; the dual classes share the
smaller of their two permitted scales for a fixed embedding. Exact rational
range tests can adjust a boundary scale downward by `nextafter`.

| `d` | Global direct scale | Local direct scale | Dual common scale | Dual/local ratio |
|---:|---:|---:|---:|---:|
| 2 | 0.0526–0.1667 | 0.1429–0.5000 | 1.0000 | 2.0–7.0 |
| 3 | 0.01418–0.01754 | 0.09524–0.11111 | 2.0000 | 18.0–21.0 |
| 5 | 0.0047506 | 0.0645161 | 2.0000 | 31.0 |
| 7 | 0.0023229 | 0.0487805 | 0.3333333 | 6.83 |
| 9 | 0.0013689 | 0.0392157 | 0.3333333 | 8.50 |

The scale is the physical energy assigned to one unit of original error weight,
up to the common annealing schedule's problem prefactor. It is not a measured
minimum spectral gap or speedup. The `d=5` to `d=7` drop in the dual scale is
caused by the first nontrivial chains under this conservative chain-strength
rule. A change of chain tuning, placement, or coefficient distribution can
change this table.

Comparing only against the global penalty would overstate the direct encoding's
disadvantage. At `d=9`, using geometry improves its scale by about 28.6 times
without changing the graph or qubit count. The dual encoding still has a larger
scale here because it needs no syndrome penalty. Neither the global penalty nor
the geometry-aware sufficient penalty is asserted to be the smallest possible
instance-specific faithful penalty.

## Search cost and validation

Median search times in milliseconds were:

| `d` | Direct | Dual |
|---:|---:|---:|
| 2 | 16.1 | 14.5 |
| 3 | 120.8 | 18.4 |
| 5 | 241.0 | 33.3 |
| 7 | 879.3 | 62.1 |
| 9 | 2727.8 | 106.7 |

They include the imported search wrapper's validation. This is one process run
with three seeds, not a machine-performance benchmark. Other concurrent lab
work can affect wall time. Both encodings can cache their structural embeddings;
these costs need not recur for each syndrome. The complete resource run,
including allocations, file writing and saved-witness audits, took 54.39 seconds.

An independent checker reread all 30 saved embedding witnesses and all 60
physical programs. It verified nonempty/disjoint/connected branches, realization
of every structural interaction, exact logical-coupling sums, spanning-tree
chain support and strength, coefficient ranges and coupling-group ranges, and
16 random consistent-state energy identities per program (960 total).

It also computes an exact rational L1 error `rho` between the actual binary64
physical coefficients and the ideally scaled rational allocation. Unit error
weights and integer penalties give an exact raw nonground energy separation of
at least one; the strict chain margin gives a broken-chain descent of at least
two. Every program satisfies `2*rho<alpha`, certifying that binary64 rounding
ensures every rounded physical ground state belongs to the exact physical
ground-state set. This certificate concerns ideal coefficients, not QPU analog
noise. All independent checks passed.

## Reproduction and artifacts

From the lab directory:

```sh
python3 scripts/resource_comparison.py
python3 scripts/resource_comparison.py --verify-only
```

The script imports `models.py` in this lab and the immutable prior lab's
`scripts/embedding.py`. It records their hashes and package versions. Primary
artifacts are:

- [resource_request.json](results/resource_request.json): frozen settings and dependency provenance.
- [resource_summary.json](results/resource_summary.json): aggregate counts, timing and scale results.
- [resource_runs.json](results/resource_runs.json): all individual seeds and program checks.
- [resource_inputs.json](results/resource_inputs.json): patch matrices, syndrome and logical Ising models.
- [resource_target.json](results/resource_target.json): full ideal target graph.
- [resource_saved_validation.json](results/resource_saved_validation.json): independent audit of serialized witnesses.
- `results/resource_witness_d*_*.json`: complete embeddings and physical coefficients.
- `results/resource_compact_d2_*_seed11.json`: compact witnesses for the lab's physical-annealing pilot.

The supported conclusion is that the dual construction is the stronger resource
baseline for these planar surface-code instances. Whether it also reaches the
desired decoded answer faster, after accounting for both class-conditioned
runs, requires the lab's separate annealing-dynamics comparison. No QPU was used
in this resource experiment.
