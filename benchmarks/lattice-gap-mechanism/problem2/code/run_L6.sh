#!/bin/bash
# 6x6 priority chain: J=4 gap sectors, then J=6 ground state and gap sectors (2 slots x 8 threads, cores 48-63).
cd /home/yzyou/SciCode2/benchmarks/lattice-gap-mechanism/problem2
run() { echo "$(date) starting $1 ($2 slots from $3, $4 threads)" >> logs/run_all.log; .venv/bin/python code/batch.py $1 --max_jobs $2 --slot0 $3 --threads $4 >> logs/batch_$1.log 2>&1; echo "$(date) finished $1" >> logs/run_all.log; }
run L6_J4gaps 2 6 8; run L6_J6 2 6 8
echo "$(date) L6 plans done" >> logs/run_all.log
