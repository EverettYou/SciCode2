"""Exact one-qubit anchors; no multi-qubit reference solution is claimed."""
import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np


def instrument(g, eta):
    """Record -> list of physical Kraus operators, including mask weights."""
    if not (0 <= g <= 1 and 0 <= eta <= 1):
        raise ValueError("g and eta must lie in [0,1]")
    kplus = np.diag(np.sqrt([(1 + g) / 2, (1 - g) / 2]))
    kminus = np.diag(np.sqrt([(1 - g) / 2, (1 + g) / 2]))
    return {
        "+": [np.sqrt(eta) * kplus],
        "-": [np.sqrt(eta) * kminus],
        "?": [np.sqrt(1 - eta) * kplus, np.sqrt(1 - eta) * kminus],
    }


def objective(kraus):
    result = np.zeros((4, 4), dtype=complex)
    for a in kraus:
        v = a.conj().T.reshape(-1)
        result += np.outer(v, v.conj()) / 4
    return result


def make_certificates(g, eta):
    """Identity recovery and analytic dual; independent verifier below."""
    vec_i = np.eye(2).reshape(-1)
    primal = np.outer(vec_i, vec_i).astype(complex)
    result = {}
    for record, ops in instrument(g, eta).items():
        # For positive diagonal Kraus maps, C is supported on |00>,|11>.
        # Taking its two supported row sums gives a dual slack with a PSD
        # 2x2 block proportional to [[1,-1],[-1,1]].
        diag = np.zeros(2)
        for a in ops:
            vals = np.diag(a).real
            diag += vals * vals.sum() / 4
        result[record] = (primal.copy(), np.diag(diag).astype(complex))
    return result


def verify(g, eta, certificates, tol=1e-10):
    """Rebuild objectives from physical inputs; never accept a submitted C."""
    physical = instrument(g, eta)
    if set(certificates) != set(physical):
        raise ValueError("wrong record set")
    completeness = sum(a.conj().T @ a for ops in physical.values() for a in ops)
    if not np.allclose(completeness, np.eye(2), atol=tol, rtol=0):
        raise ValueError("instrument incomplete")
    lower, upper, diagnostics = 0.0, 0.0, []
    for record, ops in physical.items():
        j, y = certificates[record]
        if j.shape != (4, 4) or y.shape != (2, 2):
            raise ValueError("certificate dimensions")
        for a in (j, y):
            if not np.isfinite(a).all() or np.max(np.abs(a - a.conj().T)) > tol:
                raise ValueError("nonfinite or non-Hermitian certificate")
        partial = np.trace(j.reshape(2, 2, 2, 2), axis1=0, axis2=2)
        residual = float(np.max(np.abs(partial - np.eye(2))))
        if residual > tol:
            raise ValueError("recovery is not trace preserving")
        c = objective(ops)
        min_j = float(np.linalg.eigvalsh(j).min())
        slack = np.kron(np.eye(2), y) - c
        min_slack = float(np.linalg.eigvalsh(slack).min())
        if min_j < -tol or min_slack < -tol:
            raise ValueError("primal or dual is not positive semidefinite")
        lower += float(np.trace(c @ j).real)
        upper += float(np.trace(y).real)
        diagnostics.append(dict(record=record, trace_residual=residual,
                                primal_min_eigenvalue=min_j,
                                dual_slack_min_eigenvalue=min_slack))
    if lower < -tol or upper > 1 + tol or lower > upper + tol:
        raise ValueError("invalid fidelity bounds")
    return dict(lower=lower, upper=upper, diagnostics=diagnostics)


def reset_entanglement_fidelity():
    """Explicit R,L density matrix: a reset channel destroys Bell correlations."""
    rho_r = np.eye(2) / 2
    reset = np.diag([1.0, 0.0])
    phi = np.array([1, 0, 0, 1]) / np.sqrt(2)
    return float(phi @ np.kron(rho_r, reset) @ phi)


def run():
    rows = []
    for g in (0.0, 0.2, 0.5, 0.8, 1.0):
        for eta in (0.0, 0.75, 1.0):
            result = verify(g, eta, make_certificates(g, eta))
            exact = (1 + np.sqrt(1 - g * g)) / 2
            if max(abs(result[k] - exact) for k in ("lower", "upper")) > 1e-10:
                raise ValueError("certificate disagrees with analytic anchor")
            rows.append(dict(g=g, eta=eta, exact=float(exact), **result))
    return dict(status="anchor-only", python=platform.python_version(),
                numpy=np.__version__, source_sha256=hashlib.sha256(
                    Path(__file__).read_bytes()).hexdigest(), rows=rows,
                reset_fidelity=reset_entanglement_fidelity())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps(dict(status=data["status"], cases=len(data["rows"]),
                          max_gap=max(abs(r["upper"]-r["lower"]) for r in data["rows"]),
                          reset_fidelity=data["reset_fidelity"])))
