# Usage Guide

This document explains how to use the quantum diffusion library correctly and avoid common mistakes.

## Intended API

For experiments (forward diffusion, polarization decay, Bloch sphere visualization, etc.), use **only**:

- `ForwardDiffusion` — training data generation
- `BackwardDiffusion` — inference with a learned policy

`WeakMeasurement` is a **low-level building block**. You pass it to the diffusion classes when constructing, but you should **not** call its methods directly in experiment code. The policy returns a unitary matrix `U` directly; backward diffusion applies it to the state as `torch.einsum("...ij,...j->...i", U, state)`.

## Forward diffusion

### Correct usage

```python
wm = WeakMeasurement(0.1)
fd = ForwardDiffusion(wm)
fd.state = states0  # (n_traj, 2^n) initial states
m_seqs = fd.trajectory(T)  # (n_traj, T, n)

# fd.state now contains the final states after T steps — use it directly
final_states = fd.state
```

### Polarization decay (use `step`, not `trajectory` in a loop)

For polarization vs time, evolve once with `step()` in a loop — do not reset and re-run:

```python
fd.state = states0.clone()
polarization = []
for t in range(1, T_max + 1):
    _ = fd.step()  # one step; fd.state evolves in place
    bloch = np.array([bloch_vector(fd.state[i]) for i in range(n_traj)])
    polarization.append(np.linalg.norm(bloch.mean(axis=0)))
```

**Anti-pattern**: Resetting and running `trajectory(t)` each time is O(T_max²) work:

```python
# WRONG: O(T_max²) — resets and re-runs 1+2+...+T_max steps
for t in range(1, T_max + 1):
    fd.state = states0.clone()  # wasteful
    _ = fd.trajectory(t)        # re-runs from scratch each time
    ...
```

### Anti-pattern (avoid)

```python
# WRONG: Do not recompute final states by calling wm.operator()
K_all = wm.operator(batch)  # Unnecessary; breaks encapsulation
s = psi0.clone()
for k in range(T):
    K = K_all[:, k]
    s = K @ s
    ...
```

`ForwardDiffusion.trajectory(T)` already updates `fd.state` to the post-measurement state after each step. The final `fd.state` **is** the correct final state. Recomputing from `m_seqs` via `wm.operator()` is redundant, slower, and bypasses the intended API.

## Backward diffusion

The policy returns a unitary matrix `U`; backward diffusion applies it to the post-measurement state with `torch.einsum("...ij,...j->...i", U, state)`. No separate unitary-feedback object is used.

```python
bd = BackwardDiffusion(wm, policy)
bd.state = initial_state
bd.forward_trajectory = m_forward_seqs  # (..., T, n) from forward run
m_seqs, U_seqs = bd.trajectory(T)
# bd.state holds the recovered state
```

## When to use WeakMeasurement directly

Use it only when:

- Constructing `ForwardDiffusion` or `BackwardDiffusion` (pass as argument)
- Writing unit tests that verify implementation details (e.g. that `fd.step()` matches Kraus application)
- Implementing custom pipelines outside the standard diffusion workflows

For standard experiments, stick to `ForwardDiffusion` and `BackwardDiffusion`.

## Guidelines for contributors / AI agents

When modifying or extending this codebase:

1. **Encapsulation**: Use `ForwardDiffusion` and `BackwardDiffusion` as entry points. Do not call `WeakMeasurement.operator()` in experiment code. Use `fd.state` after `fd.trajectory(T)` — it already holds the final states. To apply a unitary to a state, use `torch.einsum("...ij,...j->...i", U, state)`.

2. **Final states**: After `fd.trajectory(T)`, `fd.state` is the batched final state. No need to recompute from measurement sequences via Kraus operators.

3. **Polarization decay**: Use `fd.step()` in a loop, not `fd.state = states0.clone(); fd.trajectory(t)` each iteration. The latter is O(T²) work; incremental steps are O(T).

4. **Unit tests** that verify implementation (e.g. that `fd.step()` matches Kraus application) may use `wm.operator()` — that is intentional for correctness checks.
