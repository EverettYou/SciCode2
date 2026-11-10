Per-process measured comparisons. Bounds are total energies; a larger lower bound is stronger. “Float” rows have no completed exact certificate and physical audit pair in this table. Missing phases stay unrecorded.

| Branch | literal dim O | lower bound | model/build/solve s | RSS MB | audit s / exact s | cones / max dim |
|---|---:|---:|---:|---:|---:|---:|
| results-2x2 | — | -16.821987868 validated | 0.040 total | 59.2 | included | sectors max36 |
| results-2x3-optimized | — | -14.670935398 validated | 0.294 total | 70.7 | included | sectors max400 |
| results-2x3 | — | -15.373681304 validated | 0.203 total | 70.1 | included | sectors max400 |
| results-2x4-cylinder | — | -14.253424690 validated | 105.365 total | 978.4 | included | sectors max4900 |
| full-reproduction fresh sequential pipeline | 33825 | -8.764969113 exact | 198.865 end-to-end | 388.2 max stage | included | 244 / 233 |
| portable-reproduction fresh sequential pipeline | 2257 | -8.763353355 exact | 22.953 end-to-end | 404.5 max stage | included | 54 / 32 |
| adaptive/round_01 | — | -8.860870243 float | 0.95/0.00/33.80 | 578.7 | — / — | 186 / 45 |
| adaptive/round_02 | — | -8.860649934 float | 0.95/0.00/19.02 | 899.2 | — / — | 186 / 45 |
| adaptive/round_03 | — | -8.861000864 float | 0.95/0.00/13.58 | 900.1 | — / — | 186 / 45 |
| adaptive/round_04 | — | -8.860047786 float | 0.95/0.00/13.27 | 914.4 | — / — | 186 / 45 |
| adaptive/round_05 | — | -8.859807629 float | 0.95/0.00/18.28 | 914.4 | — / — | 186 / 45 |
| adaptive/round_06 | — | -8.860244406 float | 0.95/0.00/37.30 | 914.4 | — / — | 186 / 45 |
| adaptive/round_07 | — | -8.859640300 float | 0.95/0.00/59.35 | 914.4 | — / — | 186 / 45 |
| adaptive/round_08 | — | -8.859559067 float | 0.95/0.00/36.63 | 914.4 | — / — | 186 / 45 |
| adaptive/round_09 | — | -8.859734756 float | 0.95/0.00/38.68 | 914.4 | — / — | 186 / 45 |
| adaptive/round_10 | — | -8.859542438 float | 0.95/0.00/30.02 | 914.4 | 23.74 / — | 186 / 45 |
| dual-16-pqg | 2257 | -8.763365270 exact | 0.81/0.06/27.60 | 262.6 | 7.44 / 0.60 | 64 / 32 |
| dual-blocks-pqg | 2257 | -8.763353355 exact | 0.59/0.02/13.82 | 361.9 | 3.15 / 0.28 | 54 / 32 |
| pqg-eps6 | 2081 | -10.566825374 exact | —/0.09/41.25 | 138.0 | 2.30 / 1.35 | 208 / 32 |
| pqg-eps8 | 2081 | -10.566721991 exact | 0.10/0.09/314.17 | 160.1 | 7.20 / 0.76 | 208 / 32 |
| selected-t2-eps6 | 3041 | -10.268038997 exact | 2.01/0.08/46.84 | 189.9 | 29.06 / 1.27 | 240 / 32 |
| t1-two-site-t2-sym | 15841 | -8.856092835 exact | 111.05/0.08/569.24 | 256.0 | 30.76 / 3.67 | 102 / 72 |
| three-site-stars-clarabel | 7457 | -8.859051476 exact | 2.36/0.04/43.15 | 1475.1 | 11.95 / 4.78 | 66 / 59 |
| two-site-spin-complete | 6881 | -8.864590507 exact | 2.03/0.02/249.04 | 261.3 | 29.99 / 3.08 | 84 / 45 |
| two-site-t2-eps5 | 5921 | -8.885023369 float | 34.63/0.30/911.56 | 657.8 | — / — | 240 / 61 |
| two-site-t2-sym | 5921 | -8.864558789 exact | 61.06/0.10/278.21 | 188.5 | 34.39 / 1.39 | 66 / 45 |
| two-site-t2-sym-clarabel | 5921 | -8.864118703 exact | 0.27/0.03/64.06 | 600.5 | 34.39 / 1.92 | 66 / 45 |
| pqgt1 | 12001 | -9.847999995 exact | 35.60/0.25/472.98 | 390.5 | 35.54 / 7.74 | 272 / 120 |
| pqgt1_sym | 12001 | -9.839898719 exact | 6.89/0.06/156.99 | 192.2 | 4.95 / 2.89 | 244 / 72 |
| pqgt1t2prime_sym_s0 | 43745 | -8.763432534 exact | 39.82/0.18/1273.29 | 330.7 | 13.68 / 4.09 | 280 / 233 |
| pqgt2prime_mixed_sym | 18465 | -8.790405274 exact | 4.65/0.07/559.20 | 237.4 | 5.06 / 4.47 | 226 / 161 |
| pqgt2prime_sym | 33825 | -8.764969113 exact | 50.88/0.27/511.52 | 265.6 | 20.91 / 3.39 | 244 / 233 |
| warm_start_smoke | 33825 | -8.765749110 float | —/0.00/0.19 | 272.2 | 20.91 / — | 244 / 233 |
| fixed_full_t2_extension | — | no bound | —/—/3.13 | 278.2 | — / — | 12 / 32 |
| full_t2_plus_true_density | — | -10.663187971 float | 5.12/0.21/628.27 | 457.6 | — / — | 656 / 233 |

These rows include repeated runs and adaptive checkpoints. They cannot be summed into a single wall-clock runtime. The JSON records shared adaptive costs, abandoned runs, all validation invocations, and map-audit reuse explicitly.

The final2257-dimensional space is PQG2081 plus88 symmetry-closed cubic directions and88 adjoints. Six added matrix cones constrain16 selected directions with one-body augmentation. Validation reconstructs their raw CAR maps directly; it does not use the discovery oracle.

The final adaptive checkpoint passed all120 dyadic physical-map checks but remains a floating bound. Its weaker result was not sent through an additional exact verification. No further numerical branch is planned.
