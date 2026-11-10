"""Compare submitted phase endpoints; no new scientific simulation or fit."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SOURCE = Path('/Users/home/Downloads/20261014-102308_d89b765a')
OUT = Path(__file__).resolve().parents[1] / 'figures'
OUT.mkdir(exist_ok=True)
RUNS = [
    ('Fable 03', 'anthropic__claude-fable-5-1/run_03'),
    ('Opus 01', 'anthropic__claude-opus-5-5/run_01'),
    ('Opus 02', 'anthropic__claude-opus-5-5/run_02'),
    ('Opus 03', 'anthropic__claude-opus-5-5/run_03'),
    ('GPT 01', 'openai__gpt-6-astra/run_01'),
    ('GPT 02', 'openai__gpt-6-astra/run_02'),
    ('GPT 03', 'openai__gpt-6-astra/run_03'),
]
data = [(label, json.loads((SOURCE / folder / 'answers.json').read_text()))
        for label, folder in RUNS]
plt.rcParams.update({'font.size': 12, 'axes.spines.top': False,
                     'axes.spines.right': False})
fig, axes = plt.subplots(1, 2, figsize=(11.6, 5.1), sharey=True)
for ax, title, pair_index, center_index, error_index, limits in [
    (axes[0], r'$O_1,\ N=4$: low-$p$ transition', 0, 2, 3, (.315, .395)),
    (axes[1], r'$O_1,\ N=4$: high-$p$ transition', 1, 0, 1, (.775, .900)),
]:
    for row, (label, obj) in enumerate(data):
        answer = obj['R1']['O1']['4']
        if isinstance(answer, dict):
            ax.text(sum(limits)/2, row, 'unresolved', ha='center', va='center',
                    color='#777777', fontstyle='italic')
        else:
            segment = answer[pair_index]
            ax.errorbar(segment[center_index], row, xerr=segment[error_index],
                        fmt='o', color='#D2691E', capsize=4, markersize=6, lw=1.6)
    ax.set_title(title, pad=14)
    ax.set_xlim(*limits)
    ax.set_xlabel('Physical error probability p')
    ax.grid(axis='x', color='#dddddd', lw=.8)
    ax.set_axisbelow(True)
axes[0].set_yticks(range(len(data)), [label for label, _ in data])
axes[0].invert_yaxis()
fig.suptitle('Reported endpoints agree within their quoted allowances', y=.98, fontsize=15)
fig.text(.5, .015, 'Source: submitted answers.json. Allowance definitions differ across runs; these are not uniform confidence intervals.',
         ha='center', fontsize=10, color='#555555')
fig.tight_layout(rect=(0, .05, 1, .93))
fig.savefig(OUT / 'reported-z4-endpoints.png', dpi=160, facecolor='white')
rows = []
for label, obj in data:
    rows.append({'run': label, 'O1_N4': obj['R1']['O1']['4'],
                 'O1_N3': obj['R1']['O1']['3'], 'O1_N5': obj['R1']['O1']['5']})
(OUT / 'reported-phase-comparison.json').write_text(json.dumps(rows, indent=2) + '\n')
print(OUT / 'reported-z4-endpoints.png')
