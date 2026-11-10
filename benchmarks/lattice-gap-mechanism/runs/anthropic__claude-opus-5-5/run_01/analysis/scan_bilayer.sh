#!/bin/bash
cd /app/analysis
for UJ in "3.0 5.5" "2.2 6.2" "1.4 6.9"; do
  set -- $UJ
  python3 bilayer_gaps.py $1 $2 "(2,2)" "(-2,2)" "[6,10]" > scan_U$1_J$2_doped.log 2>&1
done
for UJ in "3.0 5.5" "2.2 6.2" "1.4 6.9"; do
  set -- $UJ
  python3 bilayer_gaps.py $1 $2 "(2,2)" "(-2,2)" "[16]" > scan_U$1_J$2_half.log 2>&1
done
