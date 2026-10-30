"""Pfaffian of a real antisymmetric matrix in JAX (Parlett-Reid elimination with
pivoting), returning (sign, log|Pf|). Differentiable through lax.fori_loop."""
import jax
import jax.numpy as jnp


def slogpf(A):
    n = A.shape[0]
    assert n % 2 == 0
    idx = jnp.arange(n)

    def body(step, carry):
        A, sign, logabs = carry
        k = 2 * step
        col = A[:, k]
        cand = jnp.where(idx > k, jnp.abs(col), -1.0)
        kp = jnp.argmax(cand)
        # swap rows/cols k+1 and kp
        perm = idx.at[k + 1].set(kp).at[kp].set(k + 1)
        A = A[perm][:, perm]
        sign = jnp.where(kp != k + 1, -sign, sign)
        piv = A[k, k + 1]
        sign = sign * jnp.sign(piv)
        logabs = logabs + jnp.log(jnp.abs(piv))
        tau = jnp.where(idx > k + 1, A[k, :] / piv, 0.0)
        v = jnp.where(idx > k + 1, A[:, k + 1], 0.0)
        A = A + jnp.outer(tau, v) - jnp.outer(v, tau)
        return A, sign, logabs

    A, sign, logabs = jax.lax.fori_loop(0, n // 2, body, (A, 1.0, 0.0))
    return sign, logabs


if __name__ == "__main__":
    import numpy as np
    jax.config.update("jax_enable_x64", True)
    rng = np.random.default_rng(0)
    for n in (2, 4, 8, 16, 32):
        M = rng.normal(size=(n, n)); A = M - M.T
        s, la = slogpf(jnp.asarray(A))
        pf2 = float(s) ** 2 * np.exp(2 * float(la))
        print(n, "Pf^2 / det =", pf2 / np.linalg.det(A))
    # block check: Pf([[0,Phi],[-Phi^T,0]]) = (-1)^{m(m-1)/2} det(Phi)
    m = 5
    Phi = rng.normal(size=(m, m))
    A = np.block([[np.zeros((m, m)), Phi], [-Phi.T, np.zeros((m, m))]])
    s, la = slogpf(jnp.asarray(A))
    print("block: Pf =", float(s) * np.exp(float(la)), " (-1)^(m(m-1)/2) det =", (-1) ** (m * (m - 1) // 2) * np.linalg.det(Phi))
    # gradient check
    f = lambda A: slogpf(A)[1]
    g = jax.grad(f)(jnp.asarray(A + 0.1 * (rng.normal(size=A.shape) - rng.normal(size=A.shape).T)))
    print("grad finite:", bool(jnp.all(jnp.isfinite(g))))
    import time
    B = jnp.asarray(rng.normal(size=(1000, 32, 32))); B = B - jnp.swapaxes(B, 1, 2)
    fb = jax.jit(jax.vmap(slogpf)); fb(B); t0 = time.time(); fb(B)[1].block_until_ready(); print("1000 pf 32x32:", time.time() - t0, "s")
    fd = jax.jit(jax.vmap(jnp.linalg.slogdet)); fd(B); t0 = time.time(); fd(B)[1].block_until_ready(); print("1000 det 32x32:", time.time() - t0, "s")
