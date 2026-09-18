import numpy as np
import pytest
from physical import encoding, kraus, effective_kraus, objectives, full_record_formula
from certificates import repair, verify


@pytest.mark.parametrize('n',[1,2,3,4])
def test_independent_physical_constructions(n):
    v=encoding(n)
    assert np.max(np.abs(v-encoding(n,dense=True)))<1e-12
    assert np.max(np.abs(v.conj().T@v-np.eye(2)))<1e-12
    a=objectives(n,.5,.75)
    b=objectives(n,.5,.75,dense=True)
    assert a.keys()==b.keys()
    assert max(np.max(np.abs(a[k]-b[k])) for k in a)<1e-13
    assert abs(sum(np.trace(c).real for c in a.values())-.5)<1e-12


@pytest.mark.parametrize('g',[0,.2,.8,1])
def test_completeness_and_limits(g):
    for site in kraus(3,g):
        assert np.max(np.abs(sum(a.conj().T@a for a in site.values())-np.eye(2)))<1e-12
    assert abs(full_record_formula(1,g)-(1+np.sqrt(1-g*g))/2)<1e-12
    if g==0:
        assert abs(full_record_formula(4,g)-1)<1e-12
    if g==1:
        assert abs(full_record_formula(4,g)-.5)<1e-12


def test_repair_and_mutation():
    c=np.eye(4)/4
    cert=repair(c,np.eye(4)/2,np.eye(2)/4)
    verify(c,cert)
    cert['y']-=.01*np.eye(2)
    with pytest.raises(ValueError):verify(c,cert)


@pytest.mark.parametrize('n',[2,4])
def test_transpose_recovery_full_record_limit(n):
    from baselines import evaluate
    row=evaluate(n,.5,eta=1.)
    assert abs(row['lower']-full_record_formula(n,.5))<1e-10
    assert row['max_negative_completion_eigenvalue']<1e-12


def test_primal_mutation_rejected():
    c=np.eye(4)/4
    cert=repair(c,np.eye(4)/2,np.eye(2)/4)
    cert['j']*=1.01
    with pytest.raises(ValueError):verify(c,cert)
