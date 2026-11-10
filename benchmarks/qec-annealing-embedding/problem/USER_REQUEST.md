# User-supplied research direction

Recorded from the user chat on 7 October 2026. This English record preserves the scope of the request; it is not a verbatim translation of every sentence.

Create a separate SciCode2 benchmark motivated by the supplied DWaveProposal.pdf. First investigate D-Wave hardware connectivity and relevant literature. Define a clear English problem statement and PDF, following the existing SciCode2 problem style, before implementing or optimizing a decoder.

The scientific input should be a check matrix defining a quantum code. Study how to translate its syndrome-decoding problem efficiently into a quantum-annealing formulation and embed the resulting interaction graph on the connectivity available to D-Wave Advantage2. Pay particular attention to embedding quality, toric boundary conditions, and the eventual handling of excited or broken-chain samples. QPU resources are unavailable for this phase. Leave consequential scientific and algorithmic choices open to the researcher rather than supplying a detailed solution recipe.

The user reports that D-Wave recommended investigating embedding before further QPU optimization. Their discussion distinguished the nonlinear Stride hybrid solver from hybrid CQM. An earlier distance-9 CQM attempt did not always find the desired solutions after 20 seconds; the underlying data have not been supplied here, so neither its cause nor solver superiority is established.

The spoken/transcribed terms “Quantum Yi-Zhuang” and “Anila” are interpreted in context as quantum annealing and the annealer, respectively. No separate device named Anila has been verified. The documented target is Advantage2 with Zephyr connectivity, with the specific solver and working graph to be supplied or versioned later.

The attachment is source material. Its allocation request, later neural-decoder distillation, reinforcement-learning phase, and staffing intentions do not expand the present authorization. The present deliverable is research design, not a QPU experiment or implementation.
