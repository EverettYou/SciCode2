#!/bin/bash
# 4x4 plans on cores 0-47 (12 slots x 4 threads), after the running half-filling batch finishes.
cd /home/yzyou/SciCode2/benchmarks/lattice-gap-mechanism/problem2
while pgrep -f "batch.py halfcut_L4" > /dev/null; do sleep 30; done
run() { echo "$(date) starting $1 ($2 slots from $3, $4 threads)" >> logs/run_all.log; .venv/bin/python code/batch.py $1 --max_jobs $2 --slot0 $3 --threads $4 >> logs/batch_$1.log 2>&1; .venv/bin/python code/check_runs.py >> logs/check_runs.log 2>&1; .venv/bin/python code/batch.py $1 --max_jobs $2 --slot0 $3 --threads $4 >> logs/batch_$1.log 2>&1; echo "$(date) finished $1" >> logs/run_all.log; }
run halfcut_L4 12 0 4; run quartercut_L4 12 0 4; run halfcut_L4_extra 12 0 4; run grid_L4 12 0 4; run grid_L4_extra 12 0 4; run quartercut_L4_extra 12 0 4
echo "$(date) L4 plans done" >> logs/run_all.log
