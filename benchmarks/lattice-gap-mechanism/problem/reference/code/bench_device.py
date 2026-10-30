import torch, time, sys, numpy as np
sys.path.insert(0, '.')
import ed_gpu as ed
torch.set_num_threads(32)
def bench(Lx, Ly, nup, ndn, dev, nrep=3):
    t0 = time.time(); sec = ed.Sector(Lx, Ly, nup, ndn, 1.0, 0.2, 8.0, (1, 1), device=dev); tb = time.time()-t0
    v = sec.random_vec(0)
    if dev == 'cuda': torch.cuda.synchronize()
    t0 = time.time()
    for _ in range(nrep): w = sec.matvec(v)
    if dev == 'cuda': torch.cuda.synchronize()
    tm = (time.time()-t0)/nrep
    mem = torch.cuda.max_memory_allocated()/1e9 if dev == 'cuda' else 0
    print(f'{Lx}x{Ly} ({nup},{ndn}) dim={sec.dim:,} {dev}: build {tb:.1f}s, matvec {tm:.3f}s, peak GPU mem {mem:.1f} GB', flush=True)
    del sec, v, w
    if dev == 'cuda': torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
bench(4, 2, 5, 5, 'cpu'); bench(4, 2, 5, 5, 'cuda')
bench(4, 2, 8, 8, 'cuda'); bench(4, 2, 9, 8, 'cuda')
try:
    bench(3, 3, 9, 9, 'cuda', nrep=1)
except Exception as e:
    print('3x3 failed:', type(e).__name__, str(e)[:200])
