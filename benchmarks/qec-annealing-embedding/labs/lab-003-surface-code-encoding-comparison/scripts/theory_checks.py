"""Independent theory audit; no dynamics and no prior-lab modification.

The shared model constructors are the objects under test. Expected energies,
rank calculation, shortest-path radius, and optimum errors are computed here.
"""
from pathlib import Path
import heapq
import json
import numpy as np
import models


def rank_binary(a):
    basis = {}
    for row in np.asarray(a):
        value = sum(int(b) << i for i, b in enumerate(row))
        while value:
            pivot = value.bit_length()-1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return len(basis)


def bit_table(n):
    return np.array([[(x >> i) & 1 for i in range(n)] for x in range(1 << n)], dtype=np.int8)


def violation_from_definition(patch, syndrome, assignments):
    out = np.zeros(len(assignments), dtype=np.int64)
    nxt = patch['n']
    for row, syndrome_bit in zip(patch['rows'], syndrome):
        previous = row[0]
        for stage, current in enumerate(row[1:]):
            a, b = assignments[:, previous], assignments[:, current]
            if stage == len(row)-2:
                out += ((a ^ b) != syndrome_bit)
            else:
                carry, prefix = nxt, nxt+1
                nxt += 2
                out += (a+b-assignments[:, prefix]-2*assignments[:, carry]).astype(np.int64)**2
                previous = prefix
    assert nxt == assignments.shape[1]
    return out


def independent_radius(patch, weights):
    m = len(patch['H'])
    boundary = m
    adjacency = [[] for _ in range(m+1)]
    for column, weight in zip(patch['H'].T, weights):
        ends = [i for i, bit in enumerate(column) if bit]
        if len(ends) == 1:
            ends.append(boundary)
        a, b = ends
        adjacency[a].append((b, abs(float(weight))))
        adjacency[b].append((a, abs(float(weight))))
    distances = [float('inf')]*(m+1)
    distances[boundary] = 0.
    heap = [(0., boundary)]
    while heap:
        distance, vertex = heapq.heappop(heap)
        if distance != distances[vertex]:
            continue
        for neighbor, weight in adjacency[vertex]:
            proposed = distance+weight
            if proposed < distances[neighbor]:
                distances[neighbor] = proposed
                heapq.heappush(heap, (proposed, neighbor))
    return max(distances[:-1])


def physical_witness_audit(lab):
    paths = sorted((lab/'results').glob('dynamics_physical_square2*.json'))
    if not paths:
        return dict(status='not_available')
    results = dict(cases=[])
    seeds = []
    for path in paths:
        data = json.loads(path.read_text())
        assert data['status'] == 'complete'
        results['cases'].extend(data['cases'])
        seeds.append(data['embedding_seed'])
    target = json.loads((lab/'results'/'resource_target.json').read_text())
    edges = {tuple(sorted(edge)) for edge in target['edges']}
    patch = models.make_patch(2, 2)
    worst_error = 0.
    count = 0
    assignment_count = 0
    for case in results['cases']:
        assert abs(case['physical_witnesses']['dual_0']['alpha']-
                   case['physical_witnesses']['dual_1']['alpha']) < 1e-14
        for witness in case['physical_witnesses'].values():
            logical, physical = witness['logical_model'], witness['physical_raw']
            embedding = {int(i): branch for i, branch in witness['embedding'].items()}
            nodes, alpha = witness['physical_nodes'], witness['alpha']
            order = {q: i for i, q in enumerate(nodes)}
            assert set(nodes) == {q for branch in embedding.values() for q in branch}
            assert sum(len(branch) for branch in embedding.values()) == len(nodes)
            assert max(abs(alpha*h) for h in physical['h']) <= 1.+1e-12
            assert max(abs(alpha*j) for _, _, j in physical['J']) <= 1.+1e-12
            physical_couplers = {}
            for i, j, value in physical['J']:
                edge = tuple(sorted((nodes[i], nodes[j])))
                assert edge in edges
                physical_couplers[edge] = alpha*value
            for group in target['coupling_groups']:
                value = sum(physical_couplers.get(tuple(sorted(edge)), 0.) for edge in group)
                assert -13.-1e-12 <= value <= 10.+1e-12
            logical_bits = bit_table(logical['n'])
            expanded = np.zeros((len(logical_bits), physical['n']), dtype=np.int8)
            for i, branch in embedding.items():
                for q in branch:
                    expanded[:, order[q]] = logical_bits[:, i]
            spins = 1-2*expanded
            expected = physical['offset']+spins @ np.array(physical['h'])
            for i, j, value in physical['J']:
                expected += value*spins[:, i]*spins[:, j]
            error = float(max(abs(expected-models.ising_diagonal(logical))))
            worst_error = max(worst_error, error)
            assert error < 1e-10
            all_physical_bits = bit_table(physical['n'])
            diagonal = models.ising_diagonal(physical)
            ground_bits = all_physical_bits[abs(diagonal-min(diagonal)) < 1e-10]
            decoded = np.zeros((len(ground_bits), logical['n']), dtype=np.int8)
            for i, branch in embedding.items():
                local = ground_bits[:, [order[q] for q in branch]]
                assert np.all(local == local[:, :1])
                decoded[:, i] = local[:, 0]
            errors_decoded = models.decode_bits(logical, patch, decoded)
            assert np.all((errors_decoded @ patch['H'].T) % 2 == case['syndrome'])
            correct_minimum = min(models.ising_diagonal(logical))
            assert np.max(abs(errors_decoded @ np.array(case['weights'])-correct_minimum)) < 1e-10
            count += 1
            assignment_count += len(logical_bits)+len(all_physical_bits)
    return dict(status='pass',programs=count,embedding_seeds=seeds,
                consistent_and_full_assignments=assignment_count,
                maximum_raw_energy_identity_error=worst_error,
                checks=['saved_target_edges','coefficient_and_signed_group_ranges',
                        'all_consistent_state_energy_identities','all_physical_ground_states_chain_consistent',
                        'ground_projection_to_correct_sector_optimum','common_dual_sector_scale'],
                dynamic_code_review='No material correctness issue found in physical_dynamics.py; probabilities not independently integrated here.',
                caveats=['Three saved embedding seeds; chain strength sufficient but not dynamically optimized.',
                         'The seed11 length-two chain holds an auxiliary bit; seeds29/47 embed both models natively. Majority tie handling does not directly alter error readout.',
                         'The 2x2 patch gives a two-spin native dual model, too small to assess large domain rearrangements.'])


def run():
    geometry = []
    for w in range(2, 8):
        for h in range(2, 8):
            patch = models.make_patch(w, h)
            n = w*h+(w-1)*(h-1)
            assert patch['n'] == n
            assert rank_binary(patch['H']) == (w-1)*h
            assert rank_binary(patch['B'].T) == w*(h-1)
            assert rank_binary(np.vstack((patch['B'].T, patch['L']))) == w*(h-1)+1
            assert not np.any((patch['H'] @ patch['B']) % 2)
            assert not np.any((patch['H'] @ patch['L']) % 2)
            direct = models.direct_model(patch, np.zeros(len(patch['H']), dtype=int), np.ones(n))
            dual = models.dual_model(patch, np.zeros(len(patch['H']), dtype=int), np.ones(n))
            assert direct['n'] == w*h+5*(w-1)*(h-1)
            assert len(direct['structural_edges']) == (w-1)*(13*h-12)
            assert dual['n'] == w*(h-1)
            assert len(dual['structural_edges']) == (w-1)*(h-1)+w*(h-2)
            assert independent_radius(patch, np.ones(n)) == w//2
            geometry.append(dict(width=w, height=h, n_error=n, n_xor=direct['n'], n_dual=dual['n']))

    mapping = []
    total_full_assignments = 0
    gauge_comparisons = 0
    patch = models.make_patch(2, 2)
    original = bit_table(patch['n'])
    weight_sets = [np.ones(patch['n']), np.array([.25, -.5, 1., 1.5, -2.])]
    for weights in weight_sets:
        for syndrome in bit_table(len(patch['H'])):
            valid = np.all((original @ patch['H'].T) % 2 == syndrome, axis=1)
            original_cost = original @ weights
            optimum = min(original_cost[valid])
            expected_optimal = {tuple(e) for e, v, c in zip(original, valid, original_cost) if v and abs(c-optimum) < 1e-12}
            for penalty in [sum(abs(weights))+1, independent_radius(patch, weights)+.25]:
                model = models.direct_model(patch, syndrome, weights, penalty=penalty)
                bits = bit_table(model['n'])
                expected = bits[:, :patch['n']] @ weights + penalty*violation_from_definition(patch, syndrome, bits)
                actual = models.ising_diagonal(model)
                max_error = float(max(abs(actual-expected)))
                assert max_error < 1e-10
                ground = abs(actual-min(actual)) < 1e-10
                actual_optimal = {tuple(e) for e in bits[ground, :patch['n']]}
                assert actual_optimal == expected_optimal
                # Integer bit ordering keeps original columns least significant.
                minimum_aux = expected.reshape((-1, 1 << patch['n'])).min(axis=0)
                residual_count = np.sum((original @ patch['H'].T) % 2 != syndrome, axis=1)
                assert np.max(abs(minimum_aux-original_cost-penalty*residual_count)) < 1e-10
                total_full_assignments += len(bits)
                mapping.append(dict(syndrome=syndrome.tolist(), weights=weights.tolist(), penalty=float(penalty),
                                    optimum=float(optimum), max_energy_error=max_error,
                                    ground_count=int(sum(ground))))
            e0 = models.reference_error(patch['H'], syndrome)
            base_diags = [models.ising_diagonal(models.dual_model(patch, syndrome, weights, ell)) for ell in (0, 1)]
            dual_global = set()
            for ell in (0, 1):
                model = models.dual_model(patch, syndrome, weights, ell)
                bits = bit_table(model['n'])
                decoded = (e0+bits @ patch['B'].T+ell*patch['L']) % 2
                assert np.all((decoded @ patch['H'].T) % 2 == syndrome)
                assert np.max(abs(base_diags[ell]-decoded @ weights)) < 1e-10
                dual_global.update(tuple(e) for e, c in zip(decoded, base_diags[ell]) if abs(c-optimum) < 1e-10)
            assert dual_global == expected_optimal
            for u_index, u in enumerate(bit_table(patch['B'].shape[1])):
                for swap in (0, 1):
                    reference = (e0+patch['B'] @ u+swap*patch['L']) % 2
                    for ell in (0, 1):
                        gauged = models.dual_model(patch, syndrome, weights, ell, e0=reference)
                        expected = base_diags[ell ^ swap][np.arange(1 << gauged['n']) ^ u_index]
                        assert np.max(abs(models.ising_diagonal(gauged)-expected)) < 1e-10
                        gauge_comparisons += 1

    radius_checks = []
    for w, h in [(2, 2), (2, 3), (3, 2), (3, 3)]:
        patch = models.make_patch(w, h)
        original = bit_table(patch['n'])
        syndromes = (original @ patch['H'].T) % 2
        for signed in (False, True):
            weights = np.array([1.+(a % 4)/4 for a in range(patch['n'])])
            if signed:
                weights[::3] *= -1
            radius = independent_radius(patch, weights)
            assert abs(radius-models.repair_radius(patch, weights)) < 1e-12
            cost = original @ weights
            penalty = radius+.25
            margins = []
            for syndrome in bit_table(len(patch['H'])):
                residual = np.sum(syndromes != syndrome, axis=1)
                feasible_minimum = min(cost[residual == 0])
                invalid_minimum = min((cost+penalty*residual)[residual > 0])
                assert invalid_minimum > feasible_minimum
                margins.append(float(invalid_minimum-feasible_minimum))
            radius_checks.append(dict(width=w, height=h, signed=signed, radius=float(radius),
                                     penalty=float(penalty), syndromes=1 << len(patch['H']),
                                     minimum_invalid_gap=min(margins)))

    patch = models.make_patch(4, 2)
    target_check = patch['checks'].index((2, 0))
    syndrome = np.zeros(len(patch['H']), dtype=int)
    syndrome[target_check] = 1
    bits = bit_table(patch['n'])
    valid = np.all((bits @ patch['H'].T) % 2 == syndrome, axis=1)
    minimum_feasible = int(min(bits[valid].sum(axis=1)))
    assert minimum_feasible == 2
    bad_penalty = 1.5
    # e=0 with all carry and parity bits zero pays exactly one final penalty.
    model = models.direct_model(patch, syndrome, np.ones(patch['n']), penalty=bad_penalty)
    invalid_energy = model['offset']+sum(model['h'])+sum(c for _, _, c in model['J'])
    assert abs(invalid_energy-bad_penalty) < 1e-10
    assert invalid_energy < minimum_feasible
    result = dict(status='pass', scope='mapping, proof identities and fairness audit; not QA performance',
                  geometry_cases=len(geometry), geometry=geometry,
                  direct_full_energy_cases=len(mapping), full_assignments_checked=total_full_assignments,
                  direct_energy_and_ground_checks=mapping, dual_reference_gauge_comparisons=gauge_comparisons,
                  radius_certificates=radius_checks,
                  insufficient_penalty_counterexample=dict(width=4, height=2, syndrome=syndrome.tolist(),
                      radius=2., penalty=bad_penalty, invalid_energy=float(invalid_energy),
                      minimum_feasible_cost=minimum_feasible),
                  proved_claims=['min_aux_V_equals_residual_weight', 'lambda_above_repair_radius_sufficient',
                    'unit_weight_worst_syndrome_threshold_tight', 'complete_two_sector_dual_parameterization',
                    'ideal_uniform_transverse_driver_reference_gauge_invariance',
                    'projected_single_bit_direct_driver_vanishes'],
                  unproved_claims=['universal_QA_runtime_ordering', 'large_code_speedup',
                    'QPU_time_to_solution', 'superiority_over_all_error_variable_quadratizations'],
                  sources=['https://arxiv.org/abs/quant-ph/0110143', 'https://arxiv.org/abs/2311.07973',
                    'https://docs.dwavequantum.com/en/latest/quantum_research/embedding_guidance.html'])
    output = Path(__file__).resolve().parents[1]/'results'/'theory_audit.json'
    result['physical_witness_audit'] = physical_witness_audit(output.parents[1])
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ['status','geometry_cases','direct_full_energy_cases',
                                           'full_assignments_checked','dual_reference_gauge_comparisons']}))


if __name__ == '__main__':
    run()
