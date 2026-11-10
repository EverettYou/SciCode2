#!/bin/bash
cd /app/analysis
while pgrep -f "ed_bilayer_gk.py 1.8 6.5" > /dev/null; do sleep 30; done
python3 cpt_half16_lean.py 1.8 6.5 0.2 60 fin_half_4x2 4 > fin_half_4x2_lean.log 2>&1
./finalize_4x2.sh > finalize_4x2.log 2>&1
