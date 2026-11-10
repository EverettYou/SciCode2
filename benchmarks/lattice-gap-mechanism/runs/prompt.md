# A layered oxide built from perovskite-type blocks

Low-temperature state of matter at half filling

## 1. Samples

We study the low-temperature state at half filling of a layered oxide built from perovskite-type blocks. Crystals of several compositions were grown by replacing a fraction of the cations on sites other than the transition metal. The transition-metal site itself is unchanged, and the replacement changes the filling of the band at the Fermi level. That band is dominated by a single orbital on the transition metal, with some admixture from other orbitals. Filling fraction $\nu = 1$ corresponds to two electrons of opposite spin in that orbital on each transition-metal site. The three crystals have $\nu = 1/2$, $\nu \approx 0.3$, and $\nu \approx 0.2$.

In a metal–oxygen plane the nearest metal–metal distances along the two in-plane axes are equal, and the fourfold axis takes one axis into the other. At every temperature, diffraction gives that metal–metal distance as the in-plane period, and the transition-metal sites are crystallographically equivalent. Cooling through the temperature range of the measurement data below adds no diffraction peaks and splits none.

Momenta are in units of $2\pi$ divided by that in-plane metal–metal distance. Energies and temperatures are in units of $D$, with $k_B = 1$.

## 2. Scanning tunneling spectroscopy (STS)

Figure 1 shows the STS differential conductance. The differential conductance is $dI/dV$, with $I$ the tunneling current and $V$ the bias voltage. Each trace is divided by its own maximum. In Figure 1(a)–(c), the differential conductance vanishes over a finite interval of $V$, and the origin of $V$ is the midpoint of that interval. Figure 1(d) is at high $T$. In that panel the origin is the chemical potential, and the thermal broadening has been deconvolved. On each crystal the differential conductance is the same at every location measured on the surface.

![Figure 1: STS differential conductance.](figure_1.png)

**Figure 1:** STS differential conductance.

## 3. Nuclear magnetic resonance (NMR) and resistivity

On each of the three crystals the transition-metal NMR remains a single line over the temperature range of the measurements below. Figure 2 shows the spin-lattice relaxation rate divided by temperature, $1/(T_1 T)$, versus inverse temperature. Figure 3 shows the in-plane resistivity. Each curve in Figures 2 and 3 is normalized to its value at $T = 4D$.

![Figure 2: Spin-lattice relaxation rate divided by temperature. Figure 3: In-plane resistivity.](figure_2_3.png)

**Figure 2:** Spin-lattice relaxation rate divided by temperature.

**Figure 3:** In-plane resistivity.

## 4. Task

Use the measurement data in `measurements.json` as given, rather than data published for a named compound. Give energies in units of $D$.

1. Propose the effective theory you find most credible. State the degrees of freedom, the lattice and the unit cell, and which symmetries the model has and which it lacks. Write out every term in the Hamiltonian. You may use a distinct symbol to denote the coefficient of each term. Give the value of each coefficient and an estimate of its uncertainty, both determined from the available measurement data.

2. Draw the phase diagram of this Hamiltonian. The horizontal axis is the filling fraction $\nu$, from 0 to 1. The vertical axis is the temperature. Mark the three crystals by vertical lines at $\nu = 1/2$, $\nu \approx 0.3$, and $\nu \approx 0.2$. For each crystal, state the phases from low temperature to high temperature.

3. Use this effective theory to explain the diffraction, the STS differential conductance, the NMR spin-lattice relaxation rate, and the resistivity. For each set of measurement data, state which feature of the theory produces it.

4. Predict the low-temperature angle-resolved photoemission spectroscopy (ARPES) intensity at $\nu = 1/2$, at $\nu \approx 0.3$, and at $\nu \approx 0.2$, after division by the Fermi function. For each filling, draw a density plot of this intensity along $(0, 0)$ to $(1/2, 0)$, then to $(1/2, 1/2)$, and back to $(0, 0)$, with momentum on the horizontal axis and energy on the vertical axis. Choose the energy window. Compare the three fillings. Name the features of physical significance, and state what each implies.

5. From your predicted spectrum at $\nu = 1/2$, recover the Green’s function by the Kramers–Kronig relation. Measure $\omega$ from the chemical potential of this crystal in the low-temperature limit. That chemical potential lies at the midpoint of the gap. The zeros at $\omega = 0$ form a closed curve. Report the fraction of the Brillouin zone on the side of this curve that contains $(0, 0)$. Compare that fraction with $\nu$.

A workstation-scale calculation is enough when you use one. State the approximation and the system size.
