#!/bin/bash
# Plan runner. 4x4 plans on cores 0-47 (12 slots x 4 threads); 6x6 plans on cores 48-63 (2 slots x 8 threads).
# Each plan runs, then the quality checker moves bad runs aside, then the plan runs again to fill them.
cd /home/yzyou/SciCode2/benchmarks/lattice-gap-mechanism/problem2
while pgrep -f "batch.py halfcut_L4" > /dev/null; do sleep 30; done
run() { echo "$(date) starting $1 ($2 slots from $3, $4 threads)" >> logs/run_all.log; .venv/bin/python code/batch.py $1 --max_jobs $2 --slot0 $3 --threads $4 >> logs/batch_$1.log 2>&1; .venv/bin/python code/check_runs.py >> logs/check_runs.log 2>&1; .venv/bin/python code/batch.py $1 --max_jobs $2 --slot0 $3 --threads $4 >> logs/batch_$1.log 2>&1; echo "$(date) finished $1" >> logs/run_all.log; }
( run half_L6 2 6 8; run half_L6_extra 2 6 8; run quarter_L6 2 6 8 ) &
( run halfcut_L4 12 0 4; run quartercut_L4 12 0 4; run halfcut_L4_extra 12 0 4; run grid_L4 12 0 4; run grid_L4_extra 12 0 4; run quartercut_L4_extra 12 0 4 ) &
wait
echo "$(date) all plans done" >> logs/run_all.log
