"""Independent dense truth and physical regression gates for corrected TDVP."""
import pytest
import torch
import mps_backend as mb
from diagnose_tdvp_gap import parity
from shared_cluster import Windows,cluster_mps,pad_bonds,check_values,middle_entropy

def test_dense_states_parameter_gradients_and_finite_differences():
    torch.set_num_threads(1)
    rows=parity()
    assert max(x['state_error'] for x in rows)<1e-10

def test_zero_rank_qr_preserves_isometry():
    a=torch.zeros(1,4,2,dtype=torch.complex128)
    q,r=mb._phase_qr(a)
    torch.testing.assert_close(q.mH@q,torch.eye(2,dtype=a.dtype).unsqueeze(0))
    torch.testing.assert_close(q@r,a)

@pytest.mark.parametrize('n',[3,5])
def test_window_features_and_ancilla_initialization(n):
    torch.manual_seed(10)
    psi=torch.randn(2,2**n,dtype=torch.complex128); psi/=psi.norm(dim=-1,keepdim=True)
    state=mb.mps_from_dense(psi,n); w=Windows(n,'cpu')
    torch.testing.assert_close(w.mps(state),w.dense(psi),atol=1e-12,rtol=1e-12)
    cluster=cluster_mps(n,2,'cpu')
    torch.testing.assert_close(check_values(cluster),torch.ones(2,n,dtype=torch.float64))
    torch.testing.assert_close(middle_entropy(cluster),torch.ones(2,dtype=torch.float64))
    if n==5:
        import train_mps_ancilla_cluster as anc
        torch.testing.assert_close(cluster_mps(n,2,'cpu',ancilla=True).to_dense(),anc.ancilla_locked_state(2,torch.device('cpu')),atol=1e-12,rtol=1e-12)

def test_long_chain_local_path_never_densifies(monkeypatch):
    torch.manual_seed(19); state=pad_bonds(cluster_mps(8,2,'cpu'),4)
    monkeypatch.setattr(mb.BatchMPS,'to_dense',lambda self: (_ for _ in ()).throw(AssertionError('densification')))
    z=Windows(8,'cpu').mps(state); assert z.shape==(2,8,64)
    on=torch.randn(2,8,3,dtype=torch.float64); bo=torch.randn(2,7,9,dtype=torch.float64)
    out=mb.reverse_tdvp_local(state,on,bo,torch.randint(3,(2,8)),1.,.01)
    assert out.max_bond_dim()==4
    torch.testing.assert_close(out.inner().real,torch.ones(2,dtype=torch.float64),atol=1e-12,rtol=1e-12)
    assert torch.isfinite(check_values(out)).all()

def test_ancilla_controller_basis_conversion():
    from shared_cluster import boundary_hadamards,ancilla_fields
    torch.manual_seed(314); n=5
    psi=torch.randn(2,2**n,dtype=torch.complex128);psi/=psi.norm(dim=-1,keepdim=True)
    canonical=mb.mps_from_dense(psi,n); physical=boundary_hadamards(canonical)
    on=torch.randn(2,n,3,dtype=torch.float64); bo=torch.randn(2,n-1,9,dtype=torch.float64)
    axes=torch.randint(3,(2,n)); physical_axes=axes.clone(); physical_axes[:,0]=2-axes[:,0];physical_axes[:,-1]=2-axes[:,-1]
    pon,pbo=ancilla_fields(on,bo)
    expected=boundary_hadamards(mb.reverse_tdvp_local(canonical,on,bo,axes,1.,.01))
    got=mb.reverse_tdvp_local(physical,pon,pbo,physical_axes,1.,.01)
    torch.testing.assert_close(got.to_dense(),expected.to_dense(),atol=1e-12,rtol=1e-12)
