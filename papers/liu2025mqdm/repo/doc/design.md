## Overview

The objective of this project is to develop a diffusion model for quantum state generation.

**Key ideas**:

- Quantum state undergoes stochastic evolution (diffusion) under randomized weak measurements.
- Use measurement to drive forward diffusion of quantum state, and use the measurement outcome sequence to train a controller that drives the quantum state backward.
- In the backward diffusion process, first apply a randomized weak measurement, then condition on the measurement outcome, a policy model predicts the driving Hamiltonian to generate a unitary to drive the state backward.

**Assumptions**:

- Consider single-qubit randomized measurement in both forward and backward process.

## Theory

### Weak measurement

Weak measurement on a quantum state $|\psi\rangle$ is described by the Krause operator $K_m$

$$|\psi\rangle \to \frac{K_m |\psi\rangle}{\sqrt{\langle\psi|K_m^\dagger K_m|\psi\rangle}}.$$

- Each Krause operator $K_m$ is associated with an measurement event (labeled by $m$).
- The probability for the event $m$ to happen is
    $$p(m|\psi)=\langle\psi|K_m^\dagger K_m|\psi\rangle.$$
  Normalization condition of the probability implies
    $$\sum_m K_m^\dagger K_m = \mathbb{I}.$$

We will consider local (single-qubit) weak measurement of measurement strength $\epsilon\in[0,1]$

$$K_m=K_{P,b} = \frac{\mathbb{I} + (-1)^b \epsilon \, P}{\sqrt{6(1+\epsilon^2)}}, \qquad P \in \{X, Y, Z\},\quad b \in \{0,1\}.$$

| $m$ | $P$ | $b$ | Expression |
|-----|-----|-----|------------|
| 0 | $X$ | 0 | $\dfrac{\mathbb{I} + \epsilon X}{\sqrt{6(1+\epsilon^2)}}$ |
| 1 | $X$ | 1 | $\dfrac{\mathbb{I} - \epsilon X}{\sqrt{6(1+\epsilon^2)}}$ |
| 2 | $Y$ | 0 | $\dfrac{\mathbb{I} + \epsilon Y}{\sqrt{6(1+\epsilon^2)}}$ |
| 3 | $Y$ | 1 | $\dfrac{\mathbb{I} - \epsilon Y}{\sqrt{6(1+\epsilon^2)}}$ |
| 4 | $Z$ | 0 | $\dfrac{\mathbb{I} + \epsilon Z}{\sqrt{6(1+\epsilon^2)}}$ |
| 5 | $Z$ | 1 | $\dfrac{\mathbb{I} - \epsilon Z}{\sqrt{6(1+\epsilon^2)}}$ |

So the unpacking map is simply:

$$m \mapsto P = \{X,Y,Z\}[\lfloor m/2 \rfloor], \quad b = m \mod 2$$

In a many-body system, the measurement operator is a product of Kraus operator on every qubit.

$$K_\mathbf{m}=\bigotimes_i K_{m_i}.$$

- The joint measurement event is described by a sequence $\mathbf{m}=[m_1,m_2,\cdots, m_N]$ (assuming totally $N$ qubits).
- $K_{m_i}$ is the Kraus operator of event $m_i$ acting on qubit $i$.

### Forward Diffusion

Starting from an initial state $|\psi^{(0)}\rangle$, the forward diffusion is a time series:

$$|\psi^{(0)}\rangle \xrightarrow{K^{(0)}} |\psi^{(1)}\rangle \xrightarrow{K^{(1)}} \cdots \xrightarrow{K^{(t-1)}} |\psi^{(t)}\rangle \xrightarrow{K^{(t)}} \cdots \xrightarrow{K^{(T-1)}} |\psi^{(T)}\rangle$$

Here $K^{(t)}=K_{m^{(t)}}$ denotes the Kraus operator at time step $t$. At each step
- The measurement event is sampled from probability $p(m^{(t)}|\psi^{(t)})=\|K_{m^{(t)}}|\psi^{(t)}\rangle\|^2$.
- Then the state is updated by:
    $$|\psi^{(t+1)}\rangle = \frac{K^{(t)}|\psi^{(t)}\rangle}{\|K^{(t)}|\psi^{(t)}\rangle\|}$$

### Backward Diffusion

The backward diffusion reverses the forward process one step at a time. The diagram below shows the role of each operation within one backward step, starting from $|\psi^{(t)}\rangle$:

**Forward** (for context):  
$|\psi^{(t-1)}\rangle \xrightarrow{K^{(t-1)}} |\psi^{(t)}\rangle \xrightarrow{K^{(t)}} |\psi^{(t+1)}\rangle$

**Backward** (one step, net $t \to t-1$): starting from $|\psi^{(t)}\rangle$, we first measure (which advances to $|\psi^{(t+1)}\rangle$), then apply $U^{(t)}$ to recover $|\hat\psi^{(t-1)}\rangle$. So the overall step maps $|\psi^{(t)}\rangle \to |\hat\psi^{(t-1)}\rangle$ — one backward step in time.

The backward protocol consists of the following steps, starting from $|\psi^{(t)}\rangle$:

1. **Randomized weak measurement**: apply a randomly sampled Kraus operator $K^{(t)}$, which advances the state one step forward to $|\psi^{(t+1)}\rangle$. This is necessary: without measuring the state we have no information about it, and cannot make an informed decision about how to drive it backward.
2. **Conditioned unitary feedback**: the policy (conditioned on the full future measurement trajectory) outputs a unitary $U^{(t)}$.
3. **State recovery**: apply $U^{(t)}$ to $|\psi^{(t+1)}\rangle$ via $U^{(t)} |\psi^{(t+1)}\rangle$ (in code: `torch.einsum("...ij,...j->...i", U, state)`) to recover an estimate $|\hat{\psi}^{(t-1)}\rangle \approx |\psi^{(t-1)}\rangle$ (on average). There is no separate unitary-feedback class; the policy returns $U$ directly.

Note the accounting carefully: the weak measurement advances the state by $+1$, while the unitary feedback $U^{(t)}$ must effectively undo two Kraus operators ($K^{(t)}$ and $K^{(t-1)}$), bringing the state back by $-2$. The net displacement per backward step is therefore $+1 - 2 = -1$, i.e. one backward step maps $|\psi^{(t)}\rangle \to |\hat\psi^{(t-1)}\rangle$. To reverse a forward trajectory of length $T$, exactly $T$ backward steps are needed.

The ideal condition on $U^{(t)}$ follows from requiring the combined action of feedback and both Kraus operators to be proportional to the identity:

$$U^{(t)} K^{(t)} K^{(t-1)} \propto \mathbb{I}$$

This means $U^{(t)}$ must invert the combined action of two successive weak measurements, using only the information available from $m^{(t)}$.

### Modeling and Training Strategy

#### Policy Model: transformer with full-trajectory conditioning and QR unitary

Instead of predicting Hamiltonian coefficients $h^{(t)}$ from only the current outcome $m^{(t)}$, the policy model observes the **full future measurement trajectory** from the forward diffusion and directly produces a unitary via QR.

- Let the forward trajectory of measurement outcomes be
  $$m = (m^{(0)}, m^{(1)}, \ldots, m^{(T-1)}),$$
  and the corresponding Kraus operators be $(K^{(0)}, K^{(1)}, \ldots, K^{(T-1)})$.
- For each time index $t = 1,\dots,T-1$, we define the **future slice**
  $$m_{\ge t} = (m^{(t)}, m^{(t+1)}, \ldots, m^{(T-1)}).$$

The policy is implemented as a PyTorch module `PolicyModel(nn.Module)` with

- **Input**: the tensor representation of the future slice $m_{\ge t}$ (all qubits, all times from $t$ to $T-1$),
- **Output**: a unitary matrix $U^{(t)}$ of shape $(2^N, 2^N)$.

Internally:

1. The future measurement sequence $m_{\ge t}$ is tokenized into a 1D token sequence (time and qubits flattened), optionally inserting a **separator token** between time steps.
2. Tokens are embedded and passed through a small Llama-style transformer (e.g. 2 layers, hidden size 64, a few attention heads).
3. The final hidden states are pooled and projected linearly to produce a complex matrix $A^{(t)}$ of shape $(2^N, 2^N)$.
4. A **QR decomposition** is applied:
   $$A^{(t)} = Q^{(t)} R^{(t)},$$
   and we take the unitary factor $U^{(t)} := Q^{(t)}$.

This parameterization introduces some redundancy (many $A^{(t)}$ map to the same $Q^{(t)}$), but gradients flow directly to $A^{(t)}$ and then to $Q^{(t)}$, often leading to more stable and efficient optimization than going through $\exp(i H)$.

#### Loss Function

The ideal backward condition remains

$$U^{(t)} K^{(t)} K^{(t-1)} \propto \mathbb{I}.$$

To remove overall scale, we normalize by the trace and define, for each $t$,

$$\mathcal{L}_t = \left\| U^{(t)} K^{(t)} K^{(t-1)} - \frac{1}{2^N}\mathrm{Tr}\!\left(U^{(t)} K^{(t)} K^{(t-1)}\right)\mathbb{I} \right\|^2_F.$$

The global loss averages over all $t$ and trajectories:

$$\mathcal{L} = \mathbb{E}_{\text{traj}} \left[ \frac{1}{T-1} \sum_{t=1}^{T-1} \mathcal{L}_t \right].$$

Here $U^{(t)}$ is the output of `PolicyModel` conditioned on the full future slice $m_{\ge t}`.

#### Training Strategy

1. **Data collection**: run the forward diffusion to collect a trajectory of measurement outcomes
   $$m = (m^{(0)}, m^{(1)}, \ldots, m^{(T-1)})$$
   and the corresponding Kraus operator sequence $(K^{(0)}, K^{(1)}, \ldots, K^{(T-1)})$.
2. **Per-time inputs**: for each $t = 1,\dots,T-1$, form the future slice $m_{\ge t}$ and feed it to the policy model to obtain $U^{(t)}`.
3. **Loss accumulation**: compute $\mathcal{L}_t$ for each $t$ as above and average over $t$ and over the batch of trajectories. Backpropagate through the transformer and the QR operation to update the parameters of `PolicyModel`.

---

## PyTorch Design

### Design Principles

- **State**: $|\psi\rangle$ as tensor shape `(2^N,)` (full Hilbert space). For N = O(1), full Hilbert space is tractable.
- **Product operators via Kronecker**: Build $\bigotimes_i M_i$ using `torch.kron`. Batch-safe: `(..., N)` → `(..., 2^N, 2^N)`; `...` enables any batch shape.
- **State opacity**: ForwardDiffusion and BackwardDiffusion hold state internally; API exposes measurement outcomes and controls only. Use property get/set for state I/O.
- **Batch safety**: All methods support `...` for arbitrary batch dimensions. Shapes like `(..., N)`, `(..., 2^N)` — `...` can be `()`, `(B,)`, `(B,T)`, etc.

### Classes

| Class | Role |
|-------|------|
| `WeakMeasurement` | Cache $K_m$ as `(6,2,2)`; `operator`, `logprob`, `sample`, `apply` (end-to-end) |
| `ForwardDiffusion` | State internal; `step()`, `trajectory(T)` |
| `PolicyModel` | Transformer-based policy, `forward(m_future)` → `U` via QR(A) |
| `BackwardDiffusion` | Inference only; uses `WeakMeasurement` and `PolicyModel` with recorded forward trajectory; applies U to state as `torch.einsum("...ij,...j->...i", U, state)`; `step()`, `trajectory(T)` |
| `DiffusionTrainer` | `collect(n_traj, T)`, `train_step(batch)`, `train()` |

### Data Flow

1. **Data generation**: Set `forward.state`, run `forward.trajectory(T)` → m_seqs (T, n).
2. **Training**: `trainer.collect(n_traj, T)` → batch; `loss_fn(batch)` → loss (policy predicts U from full future slice; loss uses U and Kraus pairs).
3. **Inference**: Set `backward.state` and `backward.forward_trajectory` (recorded m from forward run), run `backward.trajectory(T)` → (m_seqs, U_seqs). Each step applies the policy’s U to the post-measurement state via `torch.einsum("...ij,...j->...i", U, state)`.

### Dtype convention

- **Quantum state and operators** use `complex128` (double precision): `PAULI`, `WeakMeasurement.operator`, forward/backward diffusion state, and Kraus operators in the loss. This keeps numerics stable for long trajectories.
- **PolicyModel** keeps its transformer in float32 for speed. Its `forward(m_future, dtype=None)` returns `complex64` by default. When `dtype=torch.complex128` is passed, the head output is cast to float64 and the unitary is computed in complex128 so it can be used with state/Kraus tensors without ad-hoc casts. `QuantumDiffusionLoss` and `BackwardDiffusion.step` call the policy with the appropriate dtype (e.g. `K_all.dtype`, `post_state.dtype`) so all matrix products are in one dtype.