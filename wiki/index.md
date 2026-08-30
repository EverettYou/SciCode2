# SciCode2 knowledge map

Read this page first. The global wiki connects knowledge about the project itself with knowledge compiled from papers and the benchmark projects that use it.

## Project

- [[project/overview|Project overview]] — what SciCode2 is, what it produces, and where canonical state lives.
- [[project/problem-design-strategy|Problem-design strategy]] — the qualities required of a research benchmark and the human design gate.
- [[project/research-loop|Research loop]] — how ideas, labs, evidence, compiled knowledge, and deliverables compound.
- [[project/knowledge-layer|Knowledge-layer design]] — the boundary between global knowledge, benchmark knowledge, sources, and deliverables.
- [[project/agent-workflow|Agent workflow]] — how focused skills, human supervision, and durable artifacts coordinate work.
- [[project/talk|Research talk]] — the asynchronous project-wide supervision channel.
- [[project/skills|Reusable skills]] — the procedural layer and where its operational detail lives.

## Collections

- [[papers/index|Papers]] — the publication inventory and its path into global knowledge and benchmark design.
- [[benchmarks/index|Benchmarks]] — research projects, their local knowledge graphs, experiments, and deliverables.

## Research areas

- [[topics/correlated-quantum-many-body-systems|Correlated quantum many-body systems]] — superconductivity, spin liquids, and Fermi-surface phenomena.
- [[topics/topological-phases-of-matter|Topological phases of matter]] — phases, anomalies, responses, and topological transitions.
- [[topics/quantum-information-dynamics|Quantum information dynamics]] — entanglement, measurements, random circuits, and recovery.
- [[topics/machine-learning-and-physics|Machine learning and physics]] — learning as a physics method and physics of learned systems.

## Quantum measurement, shadows, and control

- [[methods/information-scrambling-diagnostics-for-quantum-neural-networks|Information-scrambling diagnostics for quantum neural networks]] — tripartite-information probes of learned circuit structure.
- [[methods/monte-carlo-operator-dynamics|Monte Carlo operator dynamics]] — support-space simulation and replica estimators for dual-unitary scrambling.
- [[concepts/self-organized-error-correction|Self-organized error correction in monitored circuits]] — information-depth protection in measurement-stable volume-law states.
- [[methods/entanglement-feature-dynamics|Entanglement-feature dynamics]] — MPS compression and effective evolution of all subsystem purities.
- [[methods/replica-statistical-mechanics-of-monitored-circuits|Replica statistical mechanics of monitored circuits]] — replica, CFT, and percolation descriptions of monitored entanglement transitions.
- [[concepts/random-tensor-network-entanglement-transitions|Random-tensor-network entanglement transitions]] — bulk ordering and fluctuating-geometry routes among entanglement laws.
- [[methods/decoherent-kibble-zurek-scaling|Decoherent Kibble–Zurek scaling]] — freeze-out controlled by energy-basis monitoring.
- [[concepts/classical-shadow-tomography|Classical shadow tomography]] — randomized measurement and observable-specific reconstruction.
- [[methods/holographic-classical-shadows|Holographic classical shadows]] — hierarchical measurements that cover contiguous observables across scales.
- [[methods/hybrid-circuit-classical-shadows|Hybrid-circuit classical shadows]] — intermittent measurements tuned to a tomography-optimal critical point.
- [[comparisons/structured-classical-shadow-protocols|Structured classical-shadow protocols]] — depth, noise, variance, and post-processing tradeoffs.
- [[concepts/learned-quantum-state-models|Learned quantum-state models]] — generative and conditional models of measurement data.
- [[methods/measurement-conditioned-quantum-control|Measurement-conditioned quantum control]] — adaptive state preparation and recovery from measurement records.
- [[concepts/weak-measurement-quantum-diffusion|Weak-measurement quantum diffusion]] — conditioned pure trajectories and ensemble-average mixed dynamics are distinct recovery targets.
- [[concepts/finite-markov-length|Finite Markov length]] — CMI decay across a buffer controls local recoverability.
- [[methods/twirled-petz-recovery|Twirled Petz recovery]] — channel reversal relative to evolving state priors, with a local restriction under a Markov condition.
- [[comparisons/global-vs-local-petz|Global versus local Petz recovery]] — the full-system reference and its windowed approximation.
- [[comparisons/trajectory-vs-ensemble-recovery|Trajectory versus ensemble recovery]] — separates learned pure-state feedback from ensemble recovery channels.
- [[implementations/liu-quantum-diffusion-companion|Companion quantum-diffusion implementation]] — static architecture of the trajectory-level PyTorch package and its validation boundary.

## Interacting fermions and topology

- [[concepts/dynamical-signatures-of-compact-qed3|Dynamical signatures of compact QED3]] — QMC/SAC spectra across deconfinement and VBS confinement.
- [[concepts/vestigial-and-charge-4e-superconducting-order|Vestigial and charge-4e superconducting order]] — composite normal and quartetting phases from two-gap fluctuations.
- [[concepts/intervalley-coherence|Intervalley coherence]] — valley hybridization, Fermi-surface reconstruction, and nearby pairing.
- [[methods/nonorthogonal-orbital-strong-coupling|Nonorthogonal-orbital strong-coupling expansion]] — localized Mott bases and exchange models for Wannier-obstructed bands.
- [[methods/parton-guided-variational-monte-carlo|Parton-guided variational Monte Carlo]] — symmetry-restored correlated ansätze with gauge-charged diagnostic parameters.
- [[methods/symmetry-complete-hot-spot-rg|Symmetry-complete hot-spot renormalization group]] — automated one-loop flow in a symmetry-reduced Majorana interaction basis.
- [[concepts/symmetry-protected-topological-ensembles|Symmetry-protected topological ensembles]] — decodable and globally retained SPT information under decoherence.
- [[concepts/intrinsically-gapless-topological-states|Intrinsically gapless topological states]] — anomaly-protected boundary structure without a gapped counterpart.
- [[concepts/symmetry-enriched-infinite-randomness|Symmetry-enriched infinite-randomness criticality]] — topological boundary distinctions at strong-disorder fixed points.
- [[concepts/symmetric-mass-generation|Symmetric mass generation]] — interaction-generated fermion gaps without symmetry breaking.
- [[concepts/kahler-dirac-symmetric-mass-generation|Kähler–Dirac symmetric mass generation]] — dimension-uniform two-copy gapping from bosonic SPT cancellation.
- [[concepts/fermi-surface-anomalies|Fermi-surface anomalies]] — defect, phase-space, and cobordism criteria for symmetric Fermi-surface gapping.
- [[concepts/green-function-zero-surfaces|Green-function zero surfaces]] — Luttinger-volume remnants after quasiparticle poles are gapped.
- [[comparisons/smg-regimes-and-diagnostics|SMG regimes and diagnostics]] — evidence across Dirac, Fermi-surface, and chiral settings.
- [[concepts/doped-smg-superconductivity|Doped SMG and superconductivity]] — pairing from a bilayer SMG parent.
- [[concepts/crt-fractionalization|CRT fractionalization]] — fermionic group extensions, anomalies, and mod-8 structure.
- [[methods/clifford-algebra-crt-classification|Clifford-algebra CRT classification]] — representations, invariant groups, mass manifolds, and domain-wall reduction.
- [[methods/systematic-fermion-symmetry-analysis|Systematic fermion symmetry analysis]] — Majorana/Lie-algebra symmetry and order enumeration.
- [[concepts/noninvertible-spt-diagnostics|Non-invertible SPT diagnostics]] — strange correlators, strings, and interface algebras.
- [[methods/twisted-lattice-gauging|Twisted lattice gauging]] — triality, p-ality, and postselected non-invertible duality maps.
- [[concepts/self-duality-protected-multicriticality|Self-duality-protected multicriticality]] — duality-constrained junctions of continuous and first-order transitions.
- [[models/parametric-random-matrix-topology|Parametric random-matrix topology]] — Weyl-point statistics and Chern-number fluctuations.
- [[concepts/topological-responses-of-gauge-groups|Topological responses of gauge groups]] — fractional responses that probe global gauge-group variants.
- [[concepts/grand-unified-deconfined-criticality|Grand-unified deconfined criticality]] — anomaly-constrained criticality between competing GUT Higgs phases.
- [[methods/emergent-symmetry-current-diagnostics|Emergent-symmetry current diagnostics]] — MPS tests of critical multiplets and conserved-current dimensions.
- [[methods/material-facing-dqcp-diagnostics|Material-facing DQCP diagnostics]] — symmetry-resolved numerics and extinction-point spectroscopy.
- [[methods/exact-lattice-duality-constructions|Exact lattice duality constructions]] — exact path-integral maps with separately tested infrared interpretations.

## Machine learning and computational methods

- [[methods/machine-learning-symmetry-discovery|Machine-learning symmetry discovery]] — conserved generators and Lie algebras learned from canonical trajectories.
- [[methods/introspective-latent-dynamics-discovery|Introspective latent-dynamics discovery]] — minimal variables and update laws distilled from learned hidden trajectories.
- [[methods/machine-learning-renormalization-group|Machine-learning renormalization group]] — hierarchical flows, learned coarse graining, and RG equations.
- [[methods/data-driven-self-similar-dynamics|Data-driven self-similar dynamics]] — learned dynamic fixed points with explicit protection against trivial coarse variables.
- [[methods/learned-statistical-gravity|Learned statistical gravity from entanglement]] — generative inference of fluctuating holographic geometry.
- [[methods/frequency-domain-diffusion-models|Frequency-domain diffusion models]] — momentum-aware noise schedules and an explicit speed–detail frontier.
- [[methods/trainable-povm-tensor-network-born-machines|Trainable-POVM tensor-network Born machines]] — constrained token embeddings, exact tensor-network likelihoods, and arbitrary-mask sampling.
- [[concepts/repetitive-task-accuracy-cliffs|Repetitive-task accuracy cliffs]] — correlated reliability loss with sequence length.
- [[concepts/information-bottleneck-quantum-classicality|Information-bottleneck quantum classicality]] — selective loss of global coherence in compressed shadow models.
- [[methods/output-space-model-evaluation|Output-space model evaluation]] — model-human disagreement over non-enumerable domains.
- [[methods/simulation-to-experiment-image-transfer|Simulation-to-experiment image transfer]] — robust transfer from theory-generated images to scarce experimental data.
- [[methods/quantum-process-code-constructions|Quantum processes for code constructions]] — LDPC algebra maps, ZX circuits, and measurement-assisted transformations.

## Current thesis

- [Project thesis](thesis.md) — the global knowledge layer should make each new paper and completed benchmark reduce the cost of the next research decision.

## Knowledge graph convention

Wiki links express conceptual relationships. `source_refs` connect claims to project resources. Paper and benchmark IDs connect the knowledge graph to the dashboard catalogs. No separate hand-maintained graph database is canonical.
