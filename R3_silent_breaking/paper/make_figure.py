"""Figure 1 of the R3 paper: change kind x client impact (GPT final codes, observable changes only).
Reads only the frozen scorer output plan/r3_score_output.txt (the 'impact x kind' line); writes figures/fig_kind_impact.pdf
and figures/fig_kind_impact.csv (the plotted numbers, for the table view / replication).
Run: /usr/bin/python3 -I -B make_figure.py"""
import ast
import csv
import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt  # noqa: E402

H = Path(__file__).resolve().parent
SRC = H.parent / 'plan' / 'r3_score_output.txt'
OUT = H / 'figures'

LABEL = {'RESPONSE_CONTENT': 'Response content', 'STATUS_OR_ERROR_MAPPING': 'Status / error mapping', 'RESPONSE_SHAPE': 'Response shape',
         'SIDE_EFFECT_OR_STATE': 'Side effect / state', 'INPUT_STRICTER': 'Stricter input', 'INPUT_LOOSER': 'Looser input',
         'AUTHZ_OR_AUTH': 'Authorisation', 'HEADER_OR_MEDIA_TYPE': 'Header / media type', 'DEFAULT_OR_OPTIONALITY': 'Default / optionality',
         'ORDERING_PAGINATION_LIMITS': 'Ordering / pagination', 'OTHER': 'Other', 'UNCLEAR': 'Kind unclear'}
IMPACTS = [('BREAKING', 'Breaking', '#B5442C', '///'), ('COMPATIBLE', 'Compatible', '#2F6DB3', ''), ('UNCLEAR', 'Impact unclear', '#A3A3A3', '')]


def main():
    text = SRC.read_text(encoding='utf-8')
    line = re.search(r'impact x kind: (\{.*\})', text).group(1)
    cnt = Counter({k: v for k, v in ast.literal_eval(line).items()})
    kinds = sorted({k for k, _ in cnt}, key=lambda k: (k in ('UNCLEAR', 'OTHER'), -sum(cnt[(k, i)] for i, *_ in IMPACTS), LABEL[k]))
    assert sum(cnt.values()) == 60, sum(cnt.values())
    OUT.mkdir(exist_ok=True)
    with open(OUT / 'fig_kind_impact.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['kind'] + [i for i, *_ in IMPACTS] + ['total'])
        for k in kinds:
            w.writerow([k] + [cnt[(k, i)] for i, *_ in IMPACTS] + [sum(cnt[(k, i)] for i, *_ in IMPACTS)])
    plt.rcParams.update({'font.size': 8, 'font.family': 'serif', 'hatch.linewidth': 0.6, 'hatch.color': 'white'})
    fig, ax = plt.subplots(figsize=(3.45, 2.6))
    y = list(range(len(kinds)))[::-1]
    left = [0] * len(kinds)
    for imp, lab, col, hatch in IMPACTS:
        vals = [cnt[(k, imp)] for k in kinds]
        ax.barh(y, vals, left=left, color=col, hatch=hatch, edgecolor='white', linewidth=1.0, height=0.7, label=lab)
        left = [a + b for a, b in zip(left, vals)]
    for yy, tot in zip(y, left):
        ax.text(tot + 0.2, yy, str(tot), va='center', fontsize=7, color='#333333')
    ax.set_yticks(y); ax.set_yticklabels([LABEL[k] for k in kinds])
    ax.set_xlabel('Commits (observable changes, n = 60)')
    ax.set_xlim(0, max(left) + 1.5)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.spines['left'].set_color('#888888'); ax.spines['bottom'].set_color('#888888')
    ax.tick_params(colors='#333333', length=2)
    ax.xaxis.grid(True, color='#E5E5E5', linewidth=0.5); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=7, loc='lower center', bbox_to_anchor=(0.35, 1.0), ncol=3, handlelength=1.2, columnspacing=0.8)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / 'fig_kind_impact.pdf', bbox_inches='tight', pad_inches=0.02); fig.savefig(OUT / 'fig_kind_impact.png', dpi=200, bbox_inches='tight', pad_inches=0.02)
    print('kinds:', len(kinds), 'total', sum(cnt.values()), '->', OUT / 'fig_kind_impact.pdf')


if __name__ == '__main__':
    main()
