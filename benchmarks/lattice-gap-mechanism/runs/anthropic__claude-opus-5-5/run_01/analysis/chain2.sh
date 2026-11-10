#!/bin/bash
cd /app/analysis
while kill -0 6823 2>/dev/null; do sleep 20; done
# wait for doped CPT runs too
while pgrep -f "cpt_run.py 1.8 6.5 4 2" > /dev/null; do sleep 20; done
python3 bilayer_gaps.py 1.8 6.5 "(2,2)" "(-2,2)" "[16]" > scan_U1.8_J6.5_half.log 2>&1
python3 ed_stiffness.py 1.8 6.5 "[6,10]" > stiff_U1.8_J6.5_doped.log 2>&1
python3 cpt_run.py 1.8 6.5 4 2 8 8 fin_half_4x2 0.2 60 > fin_half_4x2.log 2>&1
python3 bilayer_gaps.py 1.4 6.9 "(2,2)" "(-2,2)" "[16]" > scan_U1.4_J6.9_half.log 2>&1
python3 ed_stiffness.py 1.8 6.5 "[16]" > stiff_U1.8_J6.5_half.log 2>&1
python3 ed_bilayer_gk.py 1.8 6.5 fin > edgk_fin.log 2>&1
