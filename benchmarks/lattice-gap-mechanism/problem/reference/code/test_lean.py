import torch, sys, time, numpy as np
sys.path.insert(0, '.'); import ed_gpu as ed
for bc in [(1, 1), (-1, 1)]:
    s1 = ed.Sector(2, 2, 4, 4, 1.0, 0.2, 8.0, bc); s2 = ed.Sector(2, 2, 4, 4, 1.0, 0.2, 8.0, bc, lean=True, chunk=17)
    v = s1.random_vec(3); print('lean vs full matvec diff:', float(torch.linalg.norm(s1.matvec(v)-s2.matvec(v))))
    s3 = ed.Sector(4, 2, 5, 5, 1.0, 0.2, 8.0, bc); s4 = ed.Sector(4, 2, 5, 5, 1.0, 0.2, 8.0, bc, lean=True, chunk=1000)
    v = s3.random_vec(3); print('4x2 lean vs full diff:', float(torch.linalg.norm(s3.matvec(v)-s4.matvec(v))))
torch.cuda.reset_peak_memory_stats()
t0 = time.time(); s = ed.Sector(3, 3, 9, 9, 1.0, 0.2, 8.0, (1, 1), lean=True, chunk=4096); print('3x3 lean build', time.time()-t0)
v = s.random_vec(0); torch.cuda.synchronize(); t0 = time.time(); w = s.matvec(v); torch.cuda.synchronize()
print('3x3 lean matvec %.2f s, peak mem %.1f GB' % (time.time()-t0, torch.cuda.max_memory_allocated()/1e9))
