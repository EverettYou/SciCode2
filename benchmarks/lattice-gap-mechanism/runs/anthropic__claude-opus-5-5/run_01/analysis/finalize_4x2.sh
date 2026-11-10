#!/bin/bash
# post-processing once cgf_fin_half_4x2.npz exists
cd /app/analysis
python3 cpt_report.py cgf_fin_half_4x2.npz 4 2 1 > report_4x2.json 2>&1
python3 kk_zeros.py cgf_fin_half_4x2.npz 4 2 48 > kk_4x2.json 2>&1
MID=$(python3 -c "import json;print(json.load(open('kk_4x2.json'))['midgap'])")
python3 frac_vs_mu.py cgf_fin_half_4x2.npz 4 2 $MID > fracmu_4x2.log 2>&1
python3 fig_data.py > /dev/null 2>&1
python3 fig_arpes.py cgf_fin_half_4x2_analysis.npz 16-site > /dev/null 2>&1
python3 fig_zeros.py cgf_fin_half_4x2_Gfine.npy 16-site > zeros_4x2.json 2>&1
echo done
