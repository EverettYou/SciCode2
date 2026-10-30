"""Draw the solver-facing schematic curves as SVG.

The curves are a designed stimulus. They are not measurements.
Axis labels name the measured quantities and do not state an inference.
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent / "schematic-observables.svg"

PANELS = (
    (
        "tunneling",
        "sample bias / V0",
        "differential conductance",
        [(-2.0, 1.0), (-1.2, 0.98), (-0.6, 0.72), (-0.25, 0.16), (0.0, 0.05), (0.25, 0.16), (0.6, 0.72), (1.2, 0.98), (2.0, 1.0)],
        False,
    ),
    (
        "neutron scattering",
        "path index",
        "onset / E0",
        [(0.0, 0.55), (1.0, 0.50), (2.0, 0.46), (3.0, 0.43), (4.0, 0.40)],
        False,
    ),
    (
        "transport",
        "temperature / T_high",
        "resistivity / rho(T_high)",
        [(0.05, 9.2), (0.15, 6.5), (0.3, 3.8), (0.5, 2.1), (0.75, 1.35), (1.0, 1.0)],
        False,
    ),
)


def polyline(points, x_reverse):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = 0.0, max(ys) * 1.08

    def sx(x):
        frac = (x - xmin) / (xmax - xmin)
        if x_reverse:
            frac = 1.0 - frac
        return 48 + frac * 200

    def sy(y):
        frac = (y - ymin) / (ymax - ymin)
        return 150 - frac * 110

    coords = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in points)
    dots = "\n".join(
        f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="2.4" fill="#1f4e79"/>'
        for x, y in points
    )
    return coords, dots


def main() -> None:
    blocks = []
    for index, (title, xlabel, ylabel, points, reverse) in enumerate(PANELS):
        origin = 20 + index * 280
        coords, dots = polyline(points, reverse)
        blocks.append(
            f'<g transform="translate({origin},0)">'
            f'<text x="148" y="18" text-anchor="middle" font-size="13">{title}</text>'
            f'<line x1="48" y1="150" x2="248" y2="150" stroke="#444"/>'
            f'<line x1="48" y1="150" x2="48" y2="36" stroke="#444"/>'
            f'<polyline fill="none" stroke="#1f4e79" stroke-width="1.6" points="{coords}"/>'
            f"{dots}"
            f'<text x="148" y="176" text-anchor="middle" font-size="11">{xlabel}</text>'
            f'<text x="16" y="96" font-size="11" transform="rotate(-90 16 96)">{ylabel}</text>'
            f"</g>"
        )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="860" height="190" '
        'viewBox="0 0 860 190">\n'
        + "\n".join(blocks)
        + "\n</svg>\n"
    )
    OUT.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
