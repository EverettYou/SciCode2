"""Interface, unitarity, and gradient smoke tests for the Phase-1 heads."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import torch


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("lab001_prototype", HERE / "prototype.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def main() -> None:
    torch.manual_seed(7)
    for n_qubits in (1, 2):
        records = torch.randint(0, 6, (3, 3, n_qubits))
        identity = torch.eye(2 ** n_qubits, dtype=torch.complex128)
        for family in ("hamiltonian", "gates"):
            policy = module.CircuitPolicy(
                n_qubits=n_qubits,
                family=family,
                max_T=4,
                d_model=16,
                n_layer=1,
                n_head=1,
            )
            unitary = policy(records, dtype=torch.complex128)
            residual = (unitary.conj().transpose(-2, -1) @ unitary - identity).abs().max()
            loss = unitary.real.square().mean()
            loss.backward()
            grad_finite = all(
                parameter.grad is None or torch.isfinite(parameter.grad).all()
                for parameter in policy.parameters()
            )
            assert residual < 1e-10, (n_qubits, family, residual.item())
            assert grad_finite, (n_qubits, family)
            print(f"N={n_qubits} family={family} residual={residual.item():.3e} gradients=finite")


if __name__ == "__main__":
    main()
