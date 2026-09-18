"""Physical instance, with no recovery ansatz or solver dependency."""
import itertools
import numpy as np

I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], complex)
Y = np.array([[0, -1j], [1j, 0]], complex)
Z = np.diag([1., -1.]).astype(complex)


def local(a, gate, j, n):
    t = a.reshape([2]*n + [a.shape[1]])
    t = np.tensordot(gate, t, axes=(1, j))
    return np.moveaxis(t, 0, j).reshape(a.shape)


def kron_all(matrices):
    a = np.ones((1, 1), complex)
    for m in matrices:
        a = np.kron(a, m)
    return a


def encoding(n, dense=False):
    if n < 1:
        raise ValueError('N must be positive')
    a = np.zeros((2**n, 2), complex)
    a[0, 0] = 1
    a[1 << (n-1-n//2), 1] = 1
    for ell in range((n+1)//2):
        for j in range(n):
            alpha = np.pi*(2+(j+2*ell)%5)/11
            beta = np.pi*(1+(2*j+ell)%7)/13
            for theta, p in [(alpha, Y), (beta, Z)]:
                gate = np.cos(theta/2)*I - 1j*np.sin(theta/2)*p
                if dense:
                    a = kron_all([gate if k == j else I for k in range(n)]) @ a
                else:
                    a = local(a, gate, j, n)
        for j in range(ell % 2, n-1, 2):
            if dense:
                u = np.zeros((2**n, 2**n))
                for k in range(2**n):
                    output = k ^ (1 << (n-2-j)) if k & (1 << (n-1-j)) else k
                    u[output, k] = 1
                a = u @ a
            else:
                t = a.reshape([2]*n+[2]).copy()
                index = [slice(None)]*(n+1)
                index[j] = 1
                block = t[tuple(index)].copy()
                # Removing control axis shifts target j+1 to j.
                t[tuple(index)] = np.flip(block, axis=j)
                a = t.reshape(a.shape)
    return a


def kraus(n, g):
    if not 0 <= g <= 1:
        raise ValueError('g outside [0,1]')
    result = []
    for j in range(n):
        theta = np.pi*(1+j%3)/10
        p = np.cos(theta)*Z + np.sin(theta)*X
        a = (np.sqrt((1+g)/2)+np.sqrt((1-g)/2))/2
        b = (np.sqrt((1+g)/2)-np.sqrt((1-g)/2))/2
        result.append({s:a*I+s*b*p for s in (-1, 1)})
    return result


def effective_kraus(n, g, dense=False):
    v = encoding(n, dense=dense)
    operators = kraus(n, g)
    result = {}
    for outcomes in itertools.product((-1, 1), repeat=n):
        if dense:
            a = kron_all([operators[j][s] for j,s in enumerate(outcomes)]) @ v
        else:
            a = v.copy()
            for j,s in enumerate(outcomes):
                a = local(a, operators[j][s], j, n)
        result[outcomes] = a
    return result


def objectives(n, g, eta, dense=False):
    if not 0 <= eta <= 1:
        raise ValueError('eta outside [0,1]')
    maps = effective_kraus(n, g, dense=dense)
    cs = {}
    total = np.zeros((2,2), complex)
    for a in maps.values():
        total += a.conj().T @ a
    if np.max(np.abs(total-I)) > 1e-11:
        raise ValueError('channel completeness failure')
    for c in itertools.product((-1, 0, 1), repeat=n):
        erased = c.count(0)
        weight = eta**(n-erased)*(1-eta)**erased
        if weight == 0:
            continue
        matrix = np.zeros((2**(n+1), 2**(n+1)), complex)
        for s,a in maps.items():
            if all(observed == 0 or observed == actual for observed,actual in zip(c,s)):
                if dense:
                    # Direct unnormalized Bell state in R,B order.
                    bell = a.T.reshape(-1)/np.sqrt(2)
                    rho = np.outer(bell, bell.conj())
                    matrix += weight * rho.conj()/2
                else:
                    v = a.conj().T.reshape(-1)
                    matrix += weight * np.outer(v, v.conj())/4
        cs[c] = matrix
    return cs


def full_record_formula(n, g):
    return sum(np.linalg.svd(a, compute_uv=False).sum()**2/4
               for a in effective_kraus(n,g).values())
