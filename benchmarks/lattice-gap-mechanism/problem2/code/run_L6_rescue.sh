#!/bin/bash
# 6x6 J=4 rescue: re-optimize the ground state from the lowest-energy (N+2) parameters, then N+-2 from it.
cd /home/yzyou/SciCode2/benchmarks/lattice-gap-mechanism/problem2
export XLA_FLAGS="--xla_cpu_multi_thread_eigen=false intra_op_parallelism_threads=8" OMP_NUM_THREADS=8 JAX_PLATFORMS=cpu
PY=.venv/bin/python
COMMON="--Lx 6 --Ly 6 --bc pa --J 4.0 --n_samples 1024 --n_chains 64 --momentum 0.8 --no_ntk --n_hidden 16"
echo "$(date) L6 rescue: gs from p2 params" >> logs/run_all.log
taskset -c 48-55 $PY code/run_point.py $COMMON --N1 36 --N2 36 --Nup 36 --Ndn 36 --init file:data/L6_pa_nu0.500_J4.00_p2.mpack --n_iter 150 --n_final 2048 --measure spin_lite,nk_lite,pair,local,dens --out data/L6_pa_nu0.500_J4.00_xr2_gs_bcs > logs/L6_pa_nu0.500_J4.00_xr2_gs_bcs.log 2>&1
echo "$(date) L6 rescue: gaps from new gs" >> logs/run_all.log
taskset -c 48-55 $PY code/run_point.py $COMMON --N1 37 --N2 37 --Nup 37 --Ndn 37 --init file:data/L6_pa_nu0.500_J4.00_xr2_gs_bcs.mpack --n_iter 80 --n_final 4096 --measure "" --out data/L6_pa_nu0.500_J4.00_xr2_p2 > logs/L6_pa_nu0.500_J4.00_xr2_p2.log 2>&1 &
taskset -c 56-63 $PY code/run_point.py $COMMON --N1 35 --N2 35 --Nup 35 --Ndn 35 --init file:data/L6_pa_nu0.500_J4.00_xr2_gs_bcs.mpack --n_iter 80 --n_final 4096 --measure "" --out data/L6_pa_nu0.500_J4.00_xr2_m2 > logs/L6_pa_nu0.500_J4.00_xr2_m2.log 2>&1 &
wait
echo "$(date) L6 rescue done" >> logs/run_all.log
