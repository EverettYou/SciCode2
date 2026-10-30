"""Validate ed_gpu against an independent sparse construction (fock.py) on a 2x2 bilayer."""
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla, torch, sys, time
sys.path.insert(0, '.')
from fock import Fock
import ed_gpu as ed

def reference_energy(Lx, Ly, N, t1, t2, J, bc):
    Ns = 2*Lx*Ly; F = Fock(Ns, N)
    bl = ed.all_bonds(Lx, Ly, t1, t2, bc)
    H = sp.csr_matrix((F.dim, F.dim))
    for a, b, amp in bl:
        for s in (0, 1):
            H = H + F.hop(2*a+s, 2*b+s, -amp)
    for r in range(Lx*Ly):
        H = H + J*F.SdotS(r, r+Lx*Ly)
    w = sla.eigsh(H, k=1, which='SA')[0]
    return w[0]

dev = 'cuda'
for (Lx, Ly, N, bc) in [(2, 2, 8, (1, 1)), (2, 2, 7, (1, 1)), (2, 2, 9, (-1, 1)), (2, 2, 6, (1, -1)), (2, 2, 8, (-1, -1))]:
    t1, t2, J = 1.0, 0.2, 8.0
    Eref = reference_energy(Lx, Ly, N, t1, t2, J, bc)
    best = None
    for nup in range(max(0, N-2*Lx*Ly), min(N, 2*Lx*Ly)+1):
        ndn = N-nup
        if abs(nup-ndn) > 2: continue
        sec = ed.Sector(Lx, Ly, nup, ndn, t1, t2, J, bc, device=dev)
        E0, _, _, _ = ed.lanczos(sec, sec.random_vec(1), niter=200, tol=1e-12)
        best = E0 if best is None else min(best, E0)
    print(f'{Lx}x{Ly} N={N} bc={bc}: reference {Eref:.10f}  gpu {best:.10f}  diff {best-Eref:.2e}')
# test c+_k / c_k spectral sum rule and E0 consistency on 2x2, N=8 -> 9 and 7
Lx, Ly, t1, t2, J, bc = 2, 2, 1.0, 0.2, 8.0, (1, 1)
sec = ed.Sector(Lx, Ly, 4, 4, t1, t2, J, bc, device=dev)
E0, psi, _, _ = ed.lanczos(sec, sec.random_vec(1), niter=200, tol=1e-12, want_vec=True)
res = sec.matvec(psi) - E0*psi
print('ground-state residual', float(torch.linalg.norm(res)))
secp = ed.Sector(Lx, Ly, 5, 4, t1, t2, J, bc, device=dev); secm = ed.Sector(Lx, Ly, 3, 4, t1, t2, J, bc, device=dev)
tot = 0
for kx in ed.allowed_k(Lx, Ly, bc)[0]:
    for ky in ed.allowed_k(Lx, Ly, bc)[1]:
        re, im = ed.c_k_vector(sec, secp, psi, kx, ky, 0, True); wp = float((re*re).sum()+(im*im).sum())
        re, im = ed.c_k_vector(sec, secm, psi, kx, ky, 0, False); wh = float((re*re).sum()+(im*im).sum())
        print(f'k=({kx:.2f},{ky:.2f}): <c c+>={wp:.4f} <c+ c>={wh:.4f} sum={wp+wh:.4f}')
        tot += wh
print('total n_up layer0 =', tot, '(expected 2 = nup per layer at half filling)')
