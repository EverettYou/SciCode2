# Lab 001: translation-averaged cluster certificates

## Objective

Compare certified local-support bounds and independently validate the physical maps and selected operator space.

## Stable interfaces

Exploratory scripts and data stay in this lab. Supported final interfaces are documented in [the stable implementation](../../src/README.md); the promoted portable replay imports no lab module.

## Steps

Question: how much lower-bound improvement is obtained by increasing a cluster's
support and by optimizing the distribution of onsite and bond coefficients?

1. Construct exact dyadic Hubbard cluster matrices, exploiting separate particle
   numbers, spin interchange, and bipartite simultaneous particle-hole symmetry.
2. Certify all sectors with complete approximate eigenbases and explicit floating
   arithmetic error bounds; skip a sector only using separately certified kinetic
   minima plus an exact interaction lower bound.
3. Compare 2x2, 2x3, optimized 2x3, and a 2x4 cylinder inside the physical 4x4 torus.
4. Stop increasing support when the independent degree-two moment SDP provides a
   stronger bound at smaller measured cost.
5. Independently reconstruct exported moment-SDP physical maps with a different
   CAR algorithm, checking every coefficient before exact dual verification.


## Completion criteria

Record actual findings, resources, uncertainty, failed attempts, and evidence paths. A promoted lower bound requires both a valid physical/operator formulation and independent numerical error control. A negative branch completes when its discriminating experiment supports a documented prune decision.
