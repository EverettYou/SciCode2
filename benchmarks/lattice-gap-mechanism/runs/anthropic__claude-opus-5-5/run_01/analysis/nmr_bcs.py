import json, numpy as np
from scipy.optimize import brentq, least_squares
d = json.load(open('/app/measurements.json'))
s = d['measurements'][1]['samples'][2]
T = np.array(s['temperature']); r = np.array(s['one_over_T1']); e = np.array(s['uncertainty'])
y = r/T; ey = e/T
def bcs_gap(t):  # weak-coupling BCS Delta(T)/Delta0 via standard interpolation of the exact gap equation
    if t >= 1: return 0.0
    # solve ln(1/t) = 2 sum_n [1/(2n+1) - 1/sqrt((2n+1)^2 + (d/(pi t))^2)] with d=Delta/(pi... use numeric
    from scipy.integrate import quad
    def f(D):  # D = Delta/Delta0 ; T in units of Delta0: t*Tc/Delta0, Tc/Delta0 = exp(gamma)/pi
        Tt = t*np.exp(0.5772)/np.pi
        g = quad(lambda x: (np.tanh(np.sqrt(x**2+D**2)/(2*Tt))/np.sqrt(x**2+D**2) - 1/np.sqrt(x**2+1)), 0, 50, limit=200)[0]
        return g
    return brentq(f, 1e-6, 1.0)
def rate(Tv, Tc, D0, Gam, withM=True):
    E = np.linspace(-12, 12, 24001)
    out = []
    for Ti in Tv:
        D = D0*bcs_gap(Ti/Tc)
        z = E + 1j*Gam
        sq = np.sqrt(z**2 - D**2 + 0j)
        sq = np.where(sq.imag*z.imag < 0, -sq, sq)  # retarded branch
        N = (z/sq).real
        M = (D/sq).real
        integrand = N**2 + (M**2 if withM else 0)
        mf = 1/(4*Ti*np.cosh(E/(2*Ti))**2)
        out.append(np.trapezoid(integrand*mf, E))
    return np.array(out)
Tc = 1.11; D0 = 1.98
for withM in [True, False]:
    def res(p):
        Gam, A = p
        return (A*rate(T, Tc, D0, abs(Gam), withM) - y)/ey
    sol = least_squares(res, [0.1, 1.0])
    chi2 = np.sum(sol.fun**2)/(len(T)-2)
    print(f'withM={withM}: Gamma={abs(sol.x[0]):.3f}, norm={sol.x[1]:.3f}, chi2/dof={chi2:.3f}')
    model = sol.x[1]*rate(T, Tc, D0, abs(sol.x[0]), withM)
    for Ti, yi, mi in zip(T[::3], y[::3], model[::3]):
        print(f'    T={Ti:.3f} data={yi:.4f} model={mi:.4f}')
