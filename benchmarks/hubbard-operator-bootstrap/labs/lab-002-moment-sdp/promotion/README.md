# Portable compact bootstrap replay

This directory constructs the final problem directly from the Hubbard CAR algebra and six bundled integer operator projections. It does not load a lab model or the expensive full-T2 discovery oracle.

Activate the benchmark's pinned environment, then run:

```sh
python compact_replay.py --out /tmp/hubbard-compact-replay --eps 1e-9
```

When launched from a different directory, pass an absolute script path. The default input path is resolved beside the script. `--input` can select a copied input directory.

The input describes sixteen discovered cubic directions in six momentum/character sectors. Adding all D4/spin images and adjoints to the quadratic CAR core gives a resolved operator dimension of 2257. Existing creation operators provide the linear augmentation. The induced optimization has 331 real moments and 54 PSD blocks; the largest is 32. Six new blocks have dimensions 4,4,4,4,3,3.

Construction uses integer arithmetic before an exact 2^-40 coefficient scaling. Replaying the final solver gives an independently validated total-energy lower bound of approximately -8.7633533548. The exact certificate and independent physical-map audit are maintained in the benchmark's verification labs. `selection_summary.json` records the full-oracle discovery cost separately from this portable replay.
