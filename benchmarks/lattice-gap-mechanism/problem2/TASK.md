# Forward problem: bilayer phase diagram

This is the forward counterpart of [`../problem/prompt.pdf`](../problem/prompt.pdf). The solver is given the Hamiltonian. The hidden-mechanism prompt is not replaced.

## Why this is unresolved

At $t_2=0$ the half-filled square bilayer is perfectly nested, so weak interlayer exchange orders before a symmetric gap can form. $t_2=0.2t_1$ moves the saddle off the band center and removes that nesting. The weak-coupling state can then keep a Fermi surface. The strong-coupling state is still a product of interlayer singlets. Where the symmetric gapped phase replaces the Fermi liquid, and whether doping next to it produces superconductivity, is not settled by the $t_2=0$ literature value $J/t\approx 3.24$. A neural-network variational Monte Carlo calculation on this Hamiltonian has not been run. No phase boundary is known for these parameters, so none is written into `prompt.pdf`.

## Research question

For the bilayer square-lattice Hamiltonian with nearest-neighbor hopping $t_1$, next-nearest hopping $t_2=0.2t_1$, and interlayer exchange $J$, which phases appear as functions of filling $\nu\in(0,1]$ and $J/t_1$, and what charge, spin, and transport spectra does the gapped phase on the half-filling line produce?

## Objective

Compute that phase diagram with neural quantum state variational Monte Carlo, then the three spectra at one point in the gapped phase on the half-filling line.

## Expected outcomes

- Filling $\nu$ counts electrons per layer per spin, divided by the number of square-lattice sites. Full filling is $\nu=1$. Half filling is $\nu=1/2$, which is two electrons per lattice site. Quarter filling is $\nu=1/4$.
- At $\nu=1/2$ and small $J/t_1$, a Fermi liquid with a Fermi surface that is not the nested diamond.
- At $\nu=1/2$ and large $J/t_1$, a symmetric gapped state, the interlayer-singlet product, with a charge gap and a spin gap and no magnetic Bragg peak. That gapped phase is expected on the half-filling line.
- The phase diagram is expected to be symmetric under $\nu\to 1-\nu$. That symmetry is not stated in `prompt.pdf`.
- Away from half filling, a superconducting region can sit next to that gapped region. Its presence and its filling window are part of the result, not an input.
- Charge, spin, and resistivity spectra are required for the gapped phase on the half-filling line, not copied from the hidden-mechanism prompt.

## Scope and approach

The public statement is [`prompt.pdf`](prompt.pdf). It fixes $t_1=1$ and $t_2=0.2$, defines $\nu=1/2$ as half filling and $\nu=1/4$ as quarter filling, and asks for those two line cuts and then the $(\nu,J)$ plane. It does not mention symmetry about half filling. The method is neural quantum state variational Monte Carlo. Real-frequency tunneling, the spin spectrum, and resistivity may use a further approximation only if that approximation is stated and is tied to the variational state. The $t_2=0$ transition at $J/t\approx 3.24$ is not the answer for this model. Lab 005 runs the half-filling cut. No phase boundary is published until that lab reports one.

