"""Validation table: VMC (geminal-NQS) vs exact diagonalization on the 2x2 open bilayer."""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import Lattice, hamiltonian_terms
from ed import Sector, build_operator, ground_state

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lat = Lattice(2, 2, "oo")
rows = []
for f in sorted(glob.glob(os.path.join(ROOT, "data", "test2x2_*.json"))):
    r = json.load(open(f))
    sec = Sector(lat, r["N1"], r["N2"], r["Nup"], r["Ndn"])
    H = build_operator(sec, sec, hamiltonian_terms(lat, r["J"]))
    e0 = ground_state(H, k=1)[0][0]
    name = os.path.basename(f)[8:-5]
    rows.append((name, r["J"], r["N1"] + r["N2"], r["Nup"] - r["Ndn"], r["init"], r.get("triplet", False), r.get("qx", 0),
                 r["energy"], r["energy_err"], e0, (r["energy"] - e0) / abs(e0) * 100))
print("| run | J | N | 2Sz | init | triplet block | q/π | E_VMC | err | E_ED | rel. err (%) |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for row in rows:
    print(f"| {row[0]} | {row[1]:g} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | ({row[6]:g},{row[6]:g}) | {row[7]:.4f} | {row[8]:.4f} | {row[9]:.4f} | {row[10]:.2f} |")
