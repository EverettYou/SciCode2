"""Planar relative-homology surface code and two exact Ising encodings.

All Ising models use bit b=(1-z)/2, so computational bit zero has z=+1.
This module imports (does not modify) the preceding lab's tested XOR compiler.
"""
from pathlib import Path
import importlib.util
import numpy as np
import networkx as nx

PREVIOUS = Path(__file__).resolve().parents[2] / 'lab-002-agent-test-general-h' / 'scripts' / 'compiler.py'
_spec = importlib.util.spec_from_file_location('previous_xor_compiler', PREVIOUS)
compiler = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(compiler)


def gf2_rank(a):
    a = np.array(a, dtype=np.uint8, copy=True)
    rank = 0
    for j in range(a.shape[1]):
        pivots = np.flatnonzero(a[rank:, j])
        if len(pivots) == 0:
            continue
        k = rank + int(pivots[0])
        a[[rank, k]] = a[[k, rank]]
        for i in range(a.shape[0]):
            if i != rank and a[i, j]:
                a[i] ^= a[rank]
        rank += 1
        if rank == a.shape[0]:
            break
    return rank


def reference_error(H, syndrome):
    H = np.asarray(H, dtype=np.uint8)
    a = np.column_stack((H, np.asarray(syndrome, dtype=np.uint8)))
    pivots = []
    r = 0
    for j in range(H.shape[1]):
        found = np.flatnonzero(a[r:, j])
        if not len(found):
            continue
        k = r + int(found[0])
        a[[r, k]] = a[[k, r]]
        for i in range(len(a)):
            if i != r and a[i, j]:
                a[i] ^= a[r]
        pivots.append(j)
        r += 1
        if r == len(a):
            break
    if np.any(a[r:, -1]):
        raise ValueError('Inconsistent syndrome')
    e = np.zeros(H.shape[1], dtype=np.uint8)
    e[pivots] = a[:r, -1]
    assert np.array_equal((H @ e) % 2, syndrome)
    return e


def make_patch(width, height=None):
    height = width if height is None else height
    if width < 2 or height < 2:
        raise ValueError('Both dimensions must be >=2')
    edges = [('h', x, y) for y in range(height) for x in range(width)]
    edges += [('v', x, y) for y in range(height-1) for x in range(1, width)]
    lookup = {e: i for i, e in enumerate(edges)}
    vertices = [(x, y) for y in range(height) for x in range(1, width)]
    H = np.zeros((len(vertices), len(edges)), dtype=np.uint8)
    for r, (x, y) in enumerate(vertices):
        for edge in [('h', x-1, y), ('h', x, y), ('v', x, y-1), ('v', x, y)]:
            if edge in lookup:
                H[r, lookup[edge]] = 1
    faces = [(x, y) for y in range(height-1) for x in range(width)]
    B = np.zeros((len(edges), len(faces)), dtype=np.uint8)
    for f, (x, y) in enumerate(faces):
        for edge in [('h', x, y), ('h', x, y+1), ('v', x, y), ('v', x+1, y)]:
            if edge in lookup:
                B[lookup[edge], f] = 1
    L = np.zeros(len(edges), dtype=np.uint8)
    for x in range(width):
        L[lookup['h', x, 0]] = 1
    assert not np.any((H @ B) % 2)
    assert not np.any((H @ L) % 2)
    assert gf2_rank(H) == len(vertices)
    assert gf2_rank(B) == len(faces)
    assert gf2_rank(np.column_stack([B, L])) == len(faces)+1
    assert len(edges)-len(vertices)-len(faces) == 1
    assert max(B.sum(axis=1)) <= 2
    return dict(width=width, height=height, n=len(edges), edges=edges,
                checks=vertices, faces=faces, H=H, B=B, L=L,
                rows=[np.flatnonzero(row).tolist() for row in H])


def direct_model(patch, syndrome, weights, penalty=None):
    weights = list(map(float, weights))
    # Reuse the identical XOR construction at any positive Lambda. The original
    # generic compiler only certifies Lambda>sum|w|. Geometry-aware smaller
    # penalties are proved separately in THEORY.md and checked by enumeration.
    if penalty is not None and penalty <= sum(map(abs, weights)):
        q = compiler.compile_instance(patch['rows'], patch['n'], list(map(int, syndrome)),
                                      [0.]*patch['n'], penalty=penalty)
        for i,w in enumerate(weights):
            q['linear'][i] += w
    else:
        q = compiler.compile_instance(patch['rows'], patch['n'], list(map(int, syndrome)), weights,
                                      penalty=penalty)
    h = -np.asarray(q['linear'], dtype=float)/2
    J = []
    offset = float(q['offset']) + sum(q['linear'])/2
    for i, j, b in q['quadratic']:
        J.append((i, j, b/4))
        h[i] -= b/4
        h[j] -= b/4
        offset += b/4
    return dict(n=len(h), h=h.tolist(), J=J, offset=offset, kind='direct',
                n_original=patch['n'], penalty=q['penalty'],
                structural_edges=q['structural_edges'])


def dual_model(patch, syndrome, weights, ell=0, e0=None):
    e0 = reference_error(patch['H'], syndrome) if e0 is None else np.asarray(e0, dtype=np.uint8)
    base = (e0 + ell*patch['L']) % 2
    n = patch['B'].shape[1]
    h = np.zeros(n)
    couplings = {}
    offset = sum(weights)/2
    structural = set()
    for a, w in enumerate(weights):
        incident = np.flatnonzero(patch['B'][a])
        coeff = -float(w)*(1-2*int(base[a]))/2
        if len(incident) == 2:
            i, j = map(int, incident)
            structural.add((i,j))
            couplings[i,j] = couplings.get((i,j),0.)+coeff
        elif len(incident) == 1:
            h[int(incident[0])] += coeff
        else:
            offset += coeff
    J = [(i,j,c) for (i,j),c in sorted(couplings.items()) if c]
    return dict(n=n, h=h.tolist(), J=J, offset=float(offset), kind='dual',
                ell=int(ell), e0=e0.tolist(), n_original=patch['n'],
                structural_edges=sorted(structural))


def interaction_graph(model, structural=True):
    G=nx.Graph()
    G.add_nodes_from(range(model['n']))
    G.add_edges_from(model['structural_edges'] if structural else [(i,j) for i,j,c in model['J'] if c])
    return G


def all_bits(n):
    return ((np.arange(1 << n, dtype=np.uint64)[:,None] >> np.arange(n,dtype=np.uint64)) & 1).astype(np.uint8)


def ising_diagonal(model):
    bits=all_bits(model['n'])
    z=1-2*bits.astype(float)
    out=np.full(len(bits), model['offset']) + z @ np.asarray(model['h'])
    for i,j,c in model['J']:
        out += c*z[:,i]*z[:,j]
    return out


def decode_bits(model, patch, bits):
    bits=np.asarray(bits,dtype=np.uint8)
    if model['kind']=='direct':
        return bits[..., :patch['n']]
    return (np.asarray(model['e0'],dtype=np.uint8) + model['ell']*patch['L'] + bits @ patch['B'].T) % 2


def coefficient_scale(models, h_limit=1., j_limit=1.):
    hmax=max((abs(h) for m in models for h in m['h']), default=0.)
    jmax=max((abs(c) for m in models for i,j,c in m['J']), default=0.)
    return min(h_limit/hmax if hmax else float('inf'), j_limit/jmax if jmax else float('inf')) if hmax or jmax else 1.


def repair_radius(patch, weights):
    """Worst minimum |weight| path from a detector to either rough boundary.

    Lambda>R guarantees direct ground fidelity for this relative graph code;
    each violated check can be repaired by its own boundary path, with overlap
    cancelled mod2. This improves the generic sum(abs(weights)) sufficient bound.
    """
    G=nx.Graph()
    G.add_nodes_from(range(len(patch['H'])))
    G.add_node(-1)
    for col,weight in zip(patch['H'].T,weights):
        incident=list(map(int,np.flatnonzero(col)))
        if len(incident)==1:
            incident.append(-1)
        if len(incident)!=2:
            raise ValueError('Need graphlike column with one or two incident checks')
        i,j=incident
        c=abs(float(weight))
        if not G.has_edge(i,j) or c<G[i][j]['weight']:
            G.add_edge(i,j,weight=c)
    paths=nx.single_source_dijkstra_path_length(G,-1,weight='weight')
    return max(paths[i] for i in range(len(patch['H'])))
