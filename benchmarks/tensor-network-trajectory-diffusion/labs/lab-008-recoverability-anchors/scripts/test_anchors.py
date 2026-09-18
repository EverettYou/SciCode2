import numpy as np
import pytest

from anchors import (instrument, make_certificates, objective,
                     reset_entanglement_fidelity, run, verify)


def test_exact_family_and_record_independence():
    data = run()
    assert len(data["rows"]) == 15
    for row in data["rows"]:
        assert abs(row["lower"] - row["exact"]) < 1e-12
        assert abs(row["upper"] - row["exact"]) < 1e-12


def test_bell_overlap_independent_of_choi_objective():
    # Explicit channel action on a joint density matrix checks the 1/4
    # normalization and vectorization without using objective().
    phi = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    rho = np.outer(phi, phi.conj())
    out = np.zeros_like(rho)
    for ops in instrument(.6, .75).values():
        for a in ops:
            full = np.kron(np.eye(2), a)
            out += full @ rho @ full.conj().T
    result = verify(.6, .75, make_certificates(.6, .75))
    assert abs(np.vdot(phi, out @ phi).real - result["lower"]) < 1e-12


def test_complex_kraus_and_recovery_conventions():
    # Diagonal real anchors alone would miss conjugation/transposition bugs.
    a = np.array([[1, 1j], [1, -1j]], dtype=complex) / np.sqrt(2)
    r = a.conj().T
    vr = r.reshape(-1)
    j = np.outer(vr, vr.conj())
    assert abs(np.trace(objective([a]) @ j).real - 1) < 1e-12
    assert abs(abs(np.trace(r @ a))**2 / 4 - 1) < 1e-12


def test_invalid_trace_rejected():
    cert = make_certificates(.5, .75)
    j, y = cert["+"]
    cert["+"] = (j * 1.01, y)
    with pytest.raises(ValueError, match="trace preserving"):
        verify(.5, .75, cert)


def test_false_upper_bound_rejected():
    cert = make_certificates(.5, .75)
    j, y = cert["?"]
    cert["?"] = (j, y - .01 * np.eye(2))
    with pytest.raises(ValueError, match="positive semidefinite"):
        verify(.5, .75, cert)


def test_nonfinite_rejected():
    cert = make_certificates(.5, .75)
    cert["+"][0][0, 0] = np.nan
    with pytest.raises(ValueError, match="nonfinite"):
        verify(.5, .75, cert)


def test_reset_is_not_unknown_state_recovery():
    assert abs(reset_entanglement_fidelity() - .25) < 1e-12
