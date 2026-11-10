import json, numpy as np
from scipy.optimize import brentq
with open('/app/measurements.json') as f:
    d = json.load(f)
nmr = {s['filling']: s for s in d['measurements'][1]['samples']}
N = 1200
kx = (np.arange(N)+0.5)/N*2*np.pi - np.pi
KX, KY = np.meshgrid(kx, kx, indexing='ij')
cx, cy = np.cos(KX), np.cos(KY)
t, tp = 1.0, 0.196
EPS = (-2*t*(cx+cy) - 4*tp*cx*cy)
ebar = (EPS.min()+EPS.max())/2
print("band: min %.3f max %.3f center %.3f mean %.4f vHs(pi,0) %.3f" % (EPS.min(), EPS.max(), ebar, EPS.mean(), -4*tp*(-1)))
def mu_of_nu(nu):
    return brentq(lambda m: (EPS<m).mean()-nu, EPS.min(), EPS.max())
for nu in [0.2, 0.3, 0.5, 0.6, 0.65, 0.7]:
    m = mu_of_nu(nu)
    print(f"  nu={nu}: bare mu = {m:.4f}  (mu - center = {m-ebar:.3f})")
# filling at which mu hits the vHs
print("  filling at vHs:", (EPS < -4*tp*(-1)).mean())
# fraction enclosed by contour eps_k = center (for Q5 preview), and by eps_k = mean (0)
print("  fraction of BZ with eps_k < band center:", (EPS<ebar).mean())
print("  fraction of BZ with eps_k < 0 (mean):", (EPS<0).mean())
# bare DOS at mu for the fillings (per site per spin)
hist, edges = np.histogram(EPS.ravel(), bins=400, range=(EPS.min(), EPS.max()), density=True)
cent = 0.5*(edges[1:]+edges[:-1])
for nu in [0.2,0.3,0.5]:
    m = mu_of_nu(nu); i = np.argmin(abs(cent-m)); print(f"  rho0(mu) at nu={nu}: {hist[max(i-3,0):i+4].mean():.4f} per spin per site per D")

# BCS gap equation: 1 = |U| * (1/N) sum_k 1/(2E_k)  with mu fixed to bare value (weak coupling) for nu=0.2, Delta=2
for nu, Delta in [(0.2, 2.0), (0.3, 2.5), (0.5, 4.0)]:
    m = mu_of_nu(nu)
    xi = EPS - m
    E = np.sqrt(xi**2 + Delta**2)
    S = np.mean(1/(2*E))
    print(f"  nu={nu}, Delta={Delta}: BCS gap eq -> |U| = {1/S:.3f} D (mu fixed at bare value); lambda=|U|rho0 ~ {1/S*hist[np.argmin(abs(cent-m))]:.2f}")
    # BCS Tc from gap eq at Delta->0: 1 = |U| sum tanh(xi/2T)/(2 xi)
    U = 1/S
    def g(T): return U*np.mean(np.tanh(xi/(2*T))/(2*xi)) - 1
    Tc = brentq(g, 0.01, 10)
    print(f"      mean-field Tc = {Tc:.3f}  -> 2Delta/Tc = {2*Delta/Tc:.2f}")

# Hebel-Slichter: BCS 1/T1 with Dynes broadening Gamma, Delta(T) BCS, compare with nu=0.2 data
from scipy.integrate import quad
def delta_T(T, D0=2.0, Tc=2.0/1.764):
    if T>=Tc: return 0.0
    return D0*np.tanh(1.74*np.sqrt(Tc/T-1))
def nmr_bcs(T, D0=2.0, Gamma=0.05, Tc=None):
    Tc = D0/1.764 if Tc is None else Tc
    D = delta_T(T, D0, Tc)
    w = np.linspace(-30, 30, 60001); dw = w[1]-w[0]
    z = w + 1j*Gamma
    Ns = np.real(z/np.sqrt(z**2 - D**2))
    Ms = np.real(D/np.sqrt(z**2 - D**2))
    f = 1/(np.exp(np.clip(w/T,-300,300))+1)
    return np.sum((Ns**2 + Ms**2)*f*(1-f))*dw
s = nmr['≈0.2']; T = np.array(s['temperature']); r = np.array(s['one_over_T1']); u = np.array(s['uncertainty'])
for Gamma in [0.02, 0.05, 0.1, 0.2]:
    model = np.array([nmr_bcs(Ti, 2.0, Gamma) for Ti in T])
    norm = model[T==4][0]/4   # 1/T1T=1 at T=4 ; our model at T=4 is normal-state  T*N^2 -> normalize ratio
    mod = model/ (model[T==4][0]) * 4
    chi2 = np.sum(((mod - r)/u)**2)/len(T)
    print(f"  HS test Gamma={Gamma}: chi2/N = {chi2:.2f}; peak ratio model max(1/T1T)/(1/T1T at T=4) = {np.max(mod/T):.3f} at T={T[np.argmax(mod/T)]:.3f}; data peak {np.max(r/T):.3f} at T={T[np.argmax(r/T)]:.3f}")
