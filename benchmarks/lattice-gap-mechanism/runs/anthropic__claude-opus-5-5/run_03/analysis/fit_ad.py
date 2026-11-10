import sys; sys.path.insert(0,'/app/analysis')
from stsfit import *
Vf = np.linspace(-10, 10, 801)
V, G = S['d']
def model_d(p, kind='g', tpp=False):
    if tpp: t, tp, tpp_, mu, sig, amp, b0, b1 = p
    else: t, tp, mu, sig, amp, b0, b1 = p; tpp_=0
    e = eps(t, tp, tpp_) - mu
    A = dos(e, np.ones_like(e), Vf, sig, kind)
    bg = np.where(Vf<e.min(), b0*np.abs(Vf), 0) + np.where(Vf>e.max(), b1*np.abs(Vf), 0)
    return amp*A + bg
for kind in ['g','l']:
    s = least_squares(lambda p: model_d(p,kind)-G, [1.0,0.19,-0.9,0.1,3,0.01,0.01], bounds=([0.8,0,-3,0.005,0.1,0,0],[1.2,0.4,1,0.6,30,0.05,0.05]), diff_step=1e-3)
    print('panel d (%s): '%kind + fitreport(s, ['t','tp','mu','sig','amp','b0','b1']))
    e = eps(s.x[0], s.x[1]); print('    filling of bare band below mu: nu = %.4f' % np.mean(e < s.x[2]))
s = least_squares(lambda p: model_d(p,'g',True)-G, [1.0,0.19,0.0,-0.9,0.1,3,0.01,0.01], bounds=([0.8,0,-0.2,-3,0.005,0.1,0,0],[1.2,0.4,0.2,1,0.6,30,0.05,0.05]), diff_step=1e-3)
print("panel d with t'': " + fitreport(s, ['t','tp','tpp','mu','sig','amp','b0','b1']))
V, G = S['a']
def model_a(p, kind='g'):
    t, tp, Phi, slope, sig, amp, b, alpha, d0 = p
    e = eps(t, tp); ec = 0.5*(e.min()+e.max()); x = slope*(e-ec)
    Ep = Phi + x + d0; Em = -Phi + x + d0
    Zp = 0.5*(1+alpha*(e-ec)); Zm = 0.5*(1-alpha*(e-ec))
    A = dos(np.concatenate([Ep,Em]), np.concatenate([Zp,Zm]), Vf, sig, kind)
    edge = Phi - slope*(e.max()-e.min())/2
    return amp*A + b*np.abs(Vf)*(np.abs(Vf-d0) > edge)
for kind in ['g','l']:
    s = least_squares(lambda p: model_a(p,kind)-G, [1.0,0.19,6.0,0.5,0.1,3,0.012,0.05,0.0], bounds=([0.8,0,4,0.3,0.005,0.1,0,-0.2,-0.5],[1.2,0.4,8,0.7,0.6,30,0.05,0.2,0.5]), diff_step=1e-3)
    print('panel a (%s): '%kind + fitreport(s, ['t','tp','Phi','slope','sig','amp','b','alpha','d0']))
