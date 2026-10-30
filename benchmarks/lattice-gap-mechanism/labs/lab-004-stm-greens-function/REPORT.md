---
document_type: lab_report
lab_id: lab-004
status: completed
idea_ids:
  - x-001
  - k-005
  - k-006
wiki_context:
  - benchmarks/lattice-gap-mechanism/wiki/thesis.md
  - benchmarks/lattice-gap-mechanism/problem/TASK.md
related_labs:
  - lab-002-cluster-spectra
  - lab-003-local-spin-dos
---

# Lab 004: Tunneling spectrum from the strong-coupling Green's function

## Motivation

Eight-site poles cannot show the density of states of a cosine band, and a nearest-neighbor-only band puts the saddle in the middle of that band. This lab computes the local tunneling spectrum from the strong-coupling Green's function on a dispersion with a second hopping, so the saddle is offset.

## Design

The dispersion on the infinite square lattice is

$$\varepsilon(k)=-2t_1(\cos k_x+\cos k_y)-4t_2\cos k_x\cos k_y,$$

with $t_1=1$ and $t_2=0.2$. For this ratio the only saddle is at $(\pi,0)$ and $(0,\pi)$, where $\varepsilon=4t_2=0.8$. The band runs from $-4.8$ to $3.2$. Its midpoint is $-0.8$, so the saddle is $1.6$ above the midpoint.

The Green's function is Eq. (19) of Lu, Zeng, and You, arXiv:2307.12223:

$$G(\omega,k)=\frac{\omega+\alpha\varepsilon(k)/J^2}{(\omega-\varepsilon(k)/2)^2-J^2}.$$

$J=8t_1$. The coefficient $\alpha$ is an order-one choice, set here to $1$; the paper does not fix it. The spectral function is $-\mathrm{Im}\,G(\omega+i\eta)/\pi$ with $\eta=0.05t_1$. The tunneling curve is the average over a $301^2$ mesh of the Brillouin zone. Bias zero is the midpoint of the two inner edges, which is $-0.4$ in the zero of $\varepsilon$. The plotted conductance is divided by the height of the plateau inside the lower band.

High-temperature peaks are $\varepsilon(k)-\mu$ on the same dispersion. $\mu$ is the energy at which the occupied fraction of the mesh equals half the electron density, counting both spins. One electron per site is half filling of that band.

## Methods and execution

Command: `/home/yzyou/SciCode2/.venv/bin/python scripts/stm_dos.py`. NumPy 2.4.6. Runtime about one second. Outputs: `results/summary.json` and `results/stm-dos.dat`. The tables are written under `problem/figures/data/`. The plotted PDFs are `problem/figures/stm-conductance.pdf`, `problem/figures/local-magnetic.pdf`, and `problem/figures/resistivity.pdf`.

## Findings

The sum rule $\int\mathrm{d}\omega\,\rho(\omega)$ is $0.996$.

From the tunneling zero, the lower side runs from $-10$ to $-6$ and the upper side from $6$ to $10$. The maxima are at $-7.2$ and $+8.8$. The middle of each side would be $-8$ and $+8$. Both maxima lie $0.8$ above those middles, which is $4t_2$ after the strong-coupling map $\omega=\varepsilon/2\pm J$.

Occupied poles from the same zero: $-10$ at $(0,0)$, $-7.2$ at $(1/2,0)$, and $-6$ at $(1/2,1/2)$.

Chemical potentials: $0.476$ at one electron per site, $-0.290$ at $0.75$, and $-1.384$ at $0.50$. High-temperature peaks at one electron per site, from that chemical potential: $-5.28$, $-2.48$, $0.32$, $1.52$, $2.72$, and $-0.48$ at $(0,0)$, $(1/4,0)$, $(1/2,0)$, $(1/2,1/4)$, $(1/2,1/2)$, and $(1/4,1/4)$. The entries $(1/2,0)$ and $(1/4,1/4)$ differ by $4t_2$.

The triplon dispersion is $\omega(k)=6.613+ \cos k_x+\cos k_y+0.080\cos k_x\cos k_y$. It runs from $4.693$ at $(1/2,1/2)$ to $8.693$ at $(0,0)$, with the saddle at $6.533$. The plotted local intensity is zero below the lower edge. The resistivity ratio uses activation energy $6$, the tunneling inner edge: $90.02$, $12.18$, $4.48$, $1.65$, and $1$ at temperatures $1$, $1.5$, $2$, $3$, and $4$.

## Limitations

Eq. (19) is a fit to cluster perturbation at $J/t=8$, not a theorem. $\alpha=1$ is a choice. The triplon band keeps the second-order single-bond processes for both hoppings; a three-rung calculation found no extra cross term at this order. The eight-site removal ladder is a different spectrum and is not used. No doped Green's function was computed. The open prediction at $0.75$ electrons per site is not this curve.

## Search decision

Use this conductance curve, this magnetic curve, this resistivity, and these high-temperature peaks in the solver prompt. Do not name $t_1$, $t_2$, the saddle, or Eq. (19) there. Do not put the eight-site removal ladder in the prompt.

## Wiki ingest handoff

Ingest $t_2/t_1=0.2$, the bias positions of the two maxima, the triplon edges $4.693$ and $8.693$, the resistivity activation energy $6$, and the high-temperature inequality of $(1/2,0)$ and $(1/4,1/4)$. Do not ingest the eight-site removal ladder, a doped spectrum, or a transition temperature. Do not add arXiv:2307.12223 to the benchmark paper list.
