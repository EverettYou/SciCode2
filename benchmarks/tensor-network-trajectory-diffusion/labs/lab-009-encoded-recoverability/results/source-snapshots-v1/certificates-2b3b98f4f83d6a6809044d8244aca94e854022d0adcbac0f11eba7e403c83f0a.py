"""Solver-independent feasibility repairs and numerical certificate verifier.

Bounds use explicit PSD-factor residuals; floating arithmetic guard is reported.
This is numerical verification, not formal interval arithmetic.
"""
import numpy as np


def herm(a):
    return (a+a.conj().T)/2


def psd_factor(a):
    w,v = np.linalg.eigh(herm(a))
    return v*np.sqrt(np.maximum(w,0))


def repair(c, raw_j, raw_y, guard=1e-12):
    d = raw_y.shape[0]
    factor = psd_factor(raw_j)
    j0 = factor @ factor.conj().T
    t = j0[:d,:d] + j0[d:,d:]
    scale = max(1., float(np.max(np.sum(np.abs(t),axis=1)))) + guard
    # PSD factor / scale is a trace-nonincreasing CP operation. Complete with
    # a reset on its positive residual to make a deterministic recovery.
    j = j0/scale
    j[:d,:d] += np.eye(d)-t/scale
    y = herm(raw_y)
    slack = np.kron(np.eye(2),y)-c
    slack_factor = psd_factor(slack)
    residual = slack-slack_factor@slack_factor.conj().T
    shift = float(np.linalg.norm(residual,'fro')) + guard
    y = y+shift*np.eye(d)
    return dict(j=j,y=y,primal_factor=factor,slack_factor=slack_factor,
                scale=scale,shift=shift,guard=guard)


def verify(c, cert, tol=1e-10):
    if not all(np.isfinite(a).all() for a in [c,cert['j'],cert['y'],cert['primal_factor'],cert['slack_factor']]):
        raise ValueError('nonfinite certificate')
    j,y = cert['j'],cert['y']
    d = y.shape[0]
    if j.shape!=(2*d,2*d) or c.shape!=j.shape:
        raise ValueError('certificate shape mismatch')
    if max(np.max(np.abs(a-a.conj().T)) for a in [c,j,y]) > tol:
        raise ValueError('non-Hermitian certificate')
    f=cert['primal_factor']; j0=f@f.conj().T
    t=j0[:d,:d]+j0[d:,d:]
    # Independent cheap bound ||t||_2 <= max absolute row sum.
    required_scale=float(np.max(np.sum(np.abs(t),axis=1)))
    if cert['scale'] < required_scale:
        raise ValueError('invalid primal normalization certificate')
    expected=j0/cert['scale']
    expected[:d,:d]+=np.eye(d)-t/cert['scale']
    if np.max(np.abs(expected-j))>tol:
        raise ValueError('primal completion mismatch')
    slack=np.kron(np.eye(2),y)-c
    base_slack=slack-cert['shift']*np.eye(2*d)
    q=cert['slack_factor']
    residual=float(np.linalg.norm(base_slack-q@q.conj().T,'fro'))
    if cert['shift']+1e-14 < residual:
        raise ValueError('invalid dual residual bound')
    tp=float(np.max(np.abs(j[:d,:d]+j[d:,d:]-np.eye(d))))
    min_j=float(np.linalg.eigvalsh(j).min())
    min_s=float(np.linalg.eigvalsh(slack).min())
    if tp>tol or min_j < -tol or min_s < -tol:
        raise ValueError('physical feasibility residual failed')
    lo=float(np.trace(c@j).real)
    hi=float(np.trace(y).real)
    if lo>hi+tol:
        raise ValueError('weak duality violation')
    return dict(lower=lo,upper=hi,gap=hi-lo,tp_residual=tp,
                primal_min_eig=min_j,dual_min_eig=min_s,
                primal_scale=float(cert['scale']),dual_shift=float(cert['shift']),
                slack_factor_residual=residual)
