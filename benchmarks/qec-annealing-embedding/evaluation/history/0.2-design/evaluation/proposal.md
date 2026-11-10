# Quantum Error-Correction Decoding on D-Wave: Formulation and Embedding

## Objective and motivation

Construct a faithful matrix-to-QUBO compiler and resource-efficient minor embeddings for CSS decoding on Advantage2 connectivity. The standalone task defines the minimum-cost syndrome problem, stabilizer equivalence, periodic toric family, Steane example and ideal Zephyr target generator. All scientific references are public and listed in [the statement](prompt.md).

Prior Ising decoding work motivates the application, while the research question concerns the joint cost of representation and embedding: a smaller quadratic model need not have a better physical footprint or programmable scale. Substantive decisions remain about representation, quadratic reduction, penalties, placement, reuse and sample recovery. The statement specifies invariants and evidence, without prescribing their solution.

## Feasibility and evidence boundary

The required scope is offline and needs no QPU credentials, private dataset or unpublished proposal. The explicit small codes permit later exact checks, and the public graph generator supplies a reproducible target family. This is an input-availability argument, not a completed reference result or empirical achievability certificate. No formulation, embedding, decoder, pilot or model trial has been run for this design revision.

## Outputs and acceptance

The task requests reusable code, mathematical justification, independently validated portable models/embeddings and a controlled comparison on declared budgets. A positive construction, conditional tradeoff or supported capacity limitation can meet the objective. No universal numerical performance target, global-optimality requirement or hardware speedup is imposed. The author-side [acceptance plan](evaluation-plan.md) explains the intended assessment without supplying a solution.

## Design status

Revision 0.2-design is ready as a standalone question draft; expert review remains pending. A/B screening, reference development and difficulty calibration are deferred to a later phase under the user's direction. Example bank comparison is pending access and is not claimed complete. No experimental task version has been frozen and no organizer acceptance is claimed.
