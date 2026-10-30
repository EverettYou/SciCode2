# Superseded schematic

The solver figures are drawn in `../prompt.pdf` from Lab 002. Do not use the coordinates below as the current data.

# Public schematic data

`schematic-observables.svg` repeats the coordinates that are drawn in `../prompt.pdf`. It is a designed stimulus, not a measurement and not a curve from either source paper. Axes are dimensionless. The handed document is `../prompt.pdf`. Rebuild the preview with `python3 make_schematic.py`.

## What the solver is allowed to see

The figure and the fenced prompt in `../TASK.md`. The three panels are tunneling conductance versus bias, neutron magnetic intensity versus energy transfer, and resistivity versus temperature.

## Author boundary

Inferences from these curves are written in `../TASK.md` and stay there. Do not copy them onto the figure or into the solver prompt.

## Numbers

The plot uses the following coordinates.

Tunneling, bias in units of V0, conductance relative to high bias: (-2, 1), (-1.2, 0.98), (-0.6, 0.72), (-0.25, 0.16), (0, 0.05), and the even continuation.

Neutron onset, in units of E0, along the path index 0, 1, 2, 3, 4. Those indices are the momenta (0,0), (1/4,0), (1/2,0), (1/2,1/4), and (1/2,1/2) in the prompt: (0, 0.55), (1, 0.50), (2, 0.46), (3, 0.43), (4, 0.40). The prompt, not this preview, states that the grid fills the reciprocal cell and that every onset is at least 0.40.

Transport, temperature in units of the highest measured temperature, resistivity relative to that point: (0.05, 9.2), (0.15, 6.5), (0.3, 3.8), (0.5, 2.1), (0.75, 1.35), (1, 1). The temperature axis increases from left to right.
