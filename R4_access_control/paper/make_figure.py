"""Figure 1 of the R4 paper: minimal black-box setup (principals_needed) by access-control kind (GPT final codes, AC-relevant items).
Reads only the frozen scorer output plan/r4_score_output.txt (the 'EXPLORATORY ac_kind x principals' line); writes
figures/fig_r4_setup.pdf/.png and figures/fig_r4_setup.csv (plotted numbers).
Run: /usr/bin/python3 -I -B make_figure.py"""
import ast, collections, csv, re
from pathlib import Path

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt  # noqa: E402

H = Path(__file__).resolve().parent
SRC = H.parent / 'plan' / 'r4_score_output.txt'; OUT = H / 'figures'
KIND = {'OBJECT_LEVEL': 'Object level (BOLA)', 'FUNCTION_LEVEL': 'Function level (BFLA)', 'PROPERTY_LEVEL': 'Property level',
        'MISSING_AUTHENTICATION': 'Missing authentication', 'TENANT_ISOLATION': 'Tenant isolation', 'OTHER': 'Other', 'UNCLEAR': 'Kind unclear'}
SETUP = [('NONE', 'Anonymous request', '#9BC1E6', ''), ('ONE', 'One principal', '#4A87C7', ''),
         ('TWO_SAME_ROLE', 'Two principals, same role', '#B5442C', '///'), ('TWO_ROLES', 'Two roles', '#7A2A1A', '\\\\\\'),
         ('UNCLEAR', 'Setup unclear', '#A3A3A3', '')]


def main():
    line = re.search(r'EXPLORATORY ac_kind x principals: (\{.*\})', SRC.read_text(encoding='utf-8')).group(1)
    cnt = collections.Counter(ast.literal_eval(line))
    kinds = sorted({k for k, _ in cnt}, key=lambda k: (k in ('OTHER', 'UNCLEAR'), -sum(v for (a, _), v in cnt.items() if a == k), k))
    n = sum(cnt.values())
    OUT.mkdir(exist_ok=True)
    with open(OUT / 'fig_r4_setup.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['ac_kind'] + [s for s, *_ in SETUP] + ['total'])
        for k in kinds: w.writerow([k] + [cnt[(k, s)] for s, *_ in SETUP] + [sum(cnt[(k, s)] for s, *_ in SETUP)])
    plt.rcParams.update({'font.size': 8, 'font.family': 'serif', 'hatch.linewidth': 0.6, 'hatch.color': 'white'})
    fig, ax = plt.subplots(figsize=(3.45, 0.32 * len(kinds) + 0.9))
    y = list(range(len(kinds)))[::-1]; left = [0] * len(kinds)
    for s, lab, col, hatch in SETUP:
        vals = [cnt[(k, s)] for k in kinds]
        if not any(vals): continue
        ax.barh(y, vals, left=left, color=col, hatch=hatch, edgecolor='white', linewidth=1.0, height=0.7, label=lab)
        left = [a + b for a, b in zip(left, vals)]
    for yy, tot in zip(y, left): ax.text(tot + 0.3, yy, str(tot), va='center', fontsize=7, color='#333333')
    ax.set_yticks(y); ax.set_yticklabels([KIND.get(k, k) for k in kinds])
    ax.set_xlabel(f'Access-control vulnerabilities (n = {n})'); ax.set_xlim(0, max(left) * 1.12 + 1)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    ax.spines['left'].set_color('#888888'); ax.spines['bottom'].set_color('#888888'); ax.tick_params(colors='#333333', length=2)
    ax.xaxis.grid(True, color='#E5E5E5', linewidth=0.5); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=6.5, loc='lower center', bbox_to_anchor=(0.4, 1.0), ncol=2, handlelength=1.2, columnspacing=0.8)
    fig.tight_layout(pad=0.3)
    for ext in ('pdf', 'png'): fig.savefig(OUT / f'fig_r4_setup.{ext}', dpi=200, bbox_inches='tight', pad_inches=0.02)
    print('kinds', len(kinds), 'n', n)


if __name__ == '__main__':
    main()
