# Target construction, embedding, and programming notes

This note records the embedding subtask of this autonomous run. It used only the
run prompt, public sources, and artifacts newly written in this run. The target
is an **ideal** Zephyr graph, not an exported device working graph. The installed
generator is `dwave_networkx.zephyr_graph` 0.8.18, the predecessor of the current
`dwave.graphs.zephyr_graph` name. Every saved witness includes all target nodes,
edges, generator version, and parameters. The environment also has minorminer
0.2.21, dwave-system 1.34.0, dimod 0.12.21, networkx 3.5, and Python 3.13.2.

## Explicit polynomial construction

`CliqueTemplate(target, engine="tracks")` is the default. For integer-labeled,
ideal `Z_(g,4)` with `g>=2`, it constructs the published track embedding of
`K_(16g+1)` from Section 5.1 of [Boothby, King, and Raymond, *Zephyr Topology of
D-Wave Quantum Processors*, 2021](https://www.dwavequantum.com/media/2uznec4s/14-1056a-a_zephyr_topology_of_d-wave_quantum_processors.pdf).
A track `(u,w,k,j)` contains every `(u,w,k,j,z)` for `0<=z<g`. The branch
descriptors are implemented literally as A--E in `embedding.py`. Two branches
have length `g`; the other `16g-1` have length `2g`. Thus this complete template
uses exactly `32g^2` qubits, within the target's `32g^2+16g` qubits. This is a
known construction, not a claimed new clique-embedding result.

Here is a direct validity argument for the descriptors. External couplers join
each track. Every vertical interior track (`1<=w<=2g-1`) meets every horizontal
interior track, as follows by choosing the internal-coupler indices in the
published coordinate rule. A peripheral `w=0` track meets the opposite tracks
whose shift is zero. In descriptors B and E each branch has both orientations
of interior tracks. Descriptors C and D have one interior zero-shift track and
one perpendicular peripheral track. The two A branches are the two zero-shift
interior tracks at `w=3,k=0`. These observations give an internal connection
within each two-track branch and a contact for each pair of branches. The
descriptor ranges partition their tracks: B uses interior `w=1,2` with shift
one, C and D use the peripheral tracks and the remaining shift-zero tracks at
`w=1,2`, and E uses `w>=3`, excluding the two A tracks. Thus branch sets are
disjoint. Each constructed template is additionally checked against the exact
generated target graph before use.

For `g=1`, the code explicitly contracts a matching of the interior `K_(8,8)`:
branch `2k+j` contains `(0,1,k,j,0)` and `(1,1,k,j,0)` for `k=0,...,3`,
`j=0,1`. This gives a checked `K_8` using 16 qubits. There is no assertion that
these capacities are maximum minors. Inputs beyond capacity may still fit.

The track construction emits `O(g^2)` qubits. The ideal target has bounded
degree 20 and `O(g^2)` edges. Branch-tree construction, full clique verification,
and extraction of one contact for each logical pair each take `O(g^2)` time and
memory. The implementation traverses integer target labels and sorts only
bounded-degree neighbor lists, so it does not need a global edge sort in this
path. Serialization may separately sort witness lists. These are arithmetic
operation counts; rational bit complexity must be charged separately.

`engine="native"` retains the practical Ocean clique routine
`minorminer.busclique.find_clique_embedding(...,use_cache=False,seed=...)`.
Its default sufficient capacity is `16g-8` and observed branches are shorter.
The explicit path establishes the construction bound; the native path is an
optional measured library baseline. The [Ocean clique documentation](https://docs.dwavequantum.com/en/latest/ocean/api_ref_minorminer/source/clique_embedding.html)
describes native clique search and its caching interface. No persistent cache
was used in the measured native runs.

## Universal restriction and pruning

Once a complete template is checked, every integer-labeled graph with at most
its capacity embeds by assigning variables in sorted order to its first branch
sets. This includes isolated variables. The graph is the actual nonzero
quadratic interaction graph, not the check incidence graph.

Preprocessing fixes a spanning tree for each branch and one contact edge for
every template pair. For a new graph, mark the endpoints of the contact edges
needed by its interactions; remove nonterminal leaves from each branch tree.
An isolated variable keeps one qubit. The remaining tree is the unique minimal
subtree of the chosen tree spanning its terminals. It is nonempty and connected,
contains all required contacts, remains disjoint from other branches, and uses
no more qubits than the original branch. This proves validity and resource
nonincrease relative to this template; it does not compare quantum dynamics.

For `N` source variables, `M` interactions, and `Q<=2gN` selected full-template
qubits, a query costs `O(N log N + Q + M)` time and `O(Q+M)` working/output space.
Its logical ordering can be retained across updates. Repeated syndrome/weight
instances with unchanged graph need no new embedding query. The same reuse is
also available to any previously successful automatic embedding. If H or the
variable graph changes, a fresh query is guaranteed within capacity; a larger
graph requires another declared target/template or a search. A damaged target
must be revalidated and may invalidate the template.

`find_automatic_embedding` calls the general `minorminer.find_embedding`, then
places isolated variables and independently checks the result. Exceeding target
node/edge counts is a certified counting obstruction. An exhausted search,
insufficient leftover isolate space in a found partial embedding, or exceeding
template capacity is **not** a proof that the input has no minor embedding.

## Physical allocation and fidelity

The convention is `x_i=(1+z_i)/2`. The exact Ising conversion preserves constants.
Fields are shared uniformly over a branch; each logical coupler is placed on one
deterministically chosen available contact. Every branch has a BFS tree with
ferromagnetic coupling `-K_i`. Define

`L_i=|h_i|+sum_j |J_ij|`, and choose `K_i=chain_factor*L_i+chain_margin`

with `chain_factor>=1` and positive `chain_margin`. The physical offset is the
logical offset plus the sum of `K_i` over tree edges. Consequently the raw
physical energy of every consistent assignment equals the logical energy.

If a branch is broken, choose one monochromatic component of its tree and flip
the whole component. Every incident tree wall disappears, improving chain energy
by at least `2K_i`. The change of all nonchain terms incident to this component
is at most `2L_i`. Thus some change strictly lowers energy by at least
`2(K_i-L_i)`, and no broken state can be a global ground state. Applying this
argument until consistent proves physical ground-state fidelity. If the exact
logical nonoptimal gap is bounded below by `delta_Q`, the exact raw physical
nonoptimal gap is at least

`min(delta_Q, 2 min_(nonsingleton i)(K_i-L_i))`.

The minimum over no nonsingleton branches is omitted. The argument permits
degenerate optima and does not assume a unique correction.

All fields, logical couplers, reduction penalties, and chain couplers enter a
common positive scale `alpha`. The code supports asymmetric intervals for h and
J and signed sums of coupling strengths in the Zephyr groups generated by
`dwave.system.coupling_groups`. The [official solver-property description](https://docs.dwavequantum.com/en/latest/quantum_research/solver_properties_all.html)
states these are separate constraints. The defaults `h=(-4,4)`, `J=(-1,1)`,
and groups `(-13,10)` are illustrative parameter choices, not claimed properties
of a particular QPU. No device export was available. All alternatives in a
comparison must use the same target and these same chosen intervals. For other
Zephyr tile sizes, callers must supply the correct coupling groups explicitly.

`allocate_physical_exact` builds an exact companion from the compiler's rational
coefficients. The chosen binary64 K values and alpha are treated as exact rational
parameters, and their positive margin is checked against exact logical loads.
Let rho be the sum of absolute errors of all actual programmed h and J values
relative to that companion. If `2 rho < alpha*delta_raw`, every rounded ground
state belongs to the exact ground set. This is the elementary uniform diagonal
energy perturbation bound; it allows selection within a tied optimum. Constant
offset error is recorded but does not affect minimizers. Actual binary64 h/J and
group sums are checked using exact rational arithmetic. If necessary, alpha is
moved toward zero with `nextafter` to make every programmed constraint hold.
Failure of the sufficient fidelity certificate is explicit and means
inconclusive, not proof that the physical minimizers are wrong.

The allocator currently scans the target and groups on every program update:
`O(|E_T|+Q+M)` arithmetic work on ideal Zephyr, with rational error-certificate
work linear in programmed coefficients and group incidences before canonical
witness sorting. Sorting the exact companion's coefficient rows adds
`O((Q+M) log(Q+M))` comparison work. The later exact-only symbolic allocator
also sorts the full target edge list, adding `O(|E_T| log |E_T|)` in that path.
It does not claim
that these scans are already reduced to the changed weights alone. Contacts,
trees, and group membership could be cached further. This is one limitation of
the implementation's update cost.

## Checks, evidence, and limitations

`results/embed_explicit_tracks_checks.json` verifies explicit complete minors for
g=1,2,3,4,6,8,12. `embed_explicit_tracks_witness.json` contains the entire g=6
target and K97 template. Observed template preprocessing was about 20 ms at g=6
and 96 ms at g=12 in the first run; timings are observations, not asymptotic
proofs. The g=6 complete template has 1152 qubits and maximum branch length 12.

`results/embed_checks.json` records all 1024 graphs on five vertices surviving
template pruning, six kinds of invalid embeddings rejected, 496 QUBO-to-Ising
assignment checks, and physical consistency/ground-state checks on small models.
`embed_physical_witness.json` is an independently inspectable small programmed
model. Additional exact numeric-certificate checks are recorded in the same file.

The separate `embed_benchmark.json` and `embed_target_and_witnesses.json` preserve
the initial nine-graph **native-template** experiment on the same ideal g=4
target, with three seeded automatic reference runs per graph. Graphs include
paths, random cubic graphs, and seeded Erdos-Renyi graphs of 24,40,56 variables.
Native full-template counts were 120,200,280 respectively. Pruned counts ranged
37--246; automatic outputs ranged 24--244. Automatic embedding usually used
fewer physical qubits, while pruned-template queries were faster. Template
queries exclude independent revalidation, whereas the recorded automatic call
includes it; both timing components are given. No claim of overall quality or
annealing superiority follows from these observations. Parent-run matrix
experiments provide the decoding-specific comparison.

Two initial invocations of the uncached native clique routine at g=1 stalled
and later exited with code 137; the precise cause was not diagnosed. This
affected exploratory checks, not saved successful timings. The explicit g=1
construction above avoids that call. The g>=2 native runs completed normally.

Reproduce these checks without credentials:

```sh
python /absolute/path/to/lab/scripts/embedding_checks.py --output /absolute/path/to/lab/results
```

The guarantees concern valid minors, faithful final classical ground states,
explicit programming constraints, finite-precision certification, and
resource/processing costs. Any annealing-path theorem is separate; a smaller
branch count, shorter chain, or larger final-energy scale alone does not prove
better finite-time quantum-annealing success.
