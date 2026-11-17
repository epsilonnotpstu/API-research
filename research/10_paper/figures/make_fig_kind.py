"""Figure: P(SPEC repair | divergence kind) across samples, with Wilson 95% CIs.
Counts are copied from the frozen result files cited in SAMPLES. Run: /usr/bin/python3 -I -B make_fig_kind.py"""
import math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# (label, source, deliberate SPEC, deliberate n, accidental SPEC, accidental n)
SAMPLES = [
    ('E7 new\n(miner text)', 'E7_RESULTS.md primary', 26, 33, 0, 11),
    ('E8+E8b pooled\n(direction-blind text)', 'E8_RESULTS.md E8b primary', 39, 48, 0, 10),
    ('T47 items\n(miner text, new coders)', 'E9_RESULTS.md Part B descriptive', 23, 28, 0, 13),
    ('E10 new\n(T48, new coders)', 'E10_RESULTS.md H-E10-3', 19, 24, 2, 13),
    ('E12 new, fix-capped\n(T49, GPT coders)', 'E12_RESULTS.md H-E12-1', 17, 17, 3, 19),
    ('E12 new, fix-capped\n(T49, Claude coders)', 'E12_RESULTS.md H-E12-2', 17, 17, 1, 17),
    ('E13 new repositories\n(T50, GPT coders)', 'E13_RESULTS.md H-E13-1', 33, 43, 1, 18),
    ('E13 new repositories\n(T50, Claude coders)', 'E13_RESULTS.md H-E13-2', 34, 40, 0, 18),
    ('E6 items\n(exploratory)', 'E7_RESULTS.md exploratory', 11, 15, 0, 10),
]
INK, INK2, MUTED, GRID, BASE, SURF = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7', '#fcfcfb'
C_D, C_A = '#2a78d6', '#eb6834'  # categorical slots 1, 2 (validated: scripts/validate_palette.js, light)


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def main():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': BASE,
                         'axes.labelcolor': INK2, 'xtick.color': MUTED, 'ytick.color': INK2})
    fig, ax = plt.subplots(figsize=(6.4, 5.6), facecolor=SURF)
    ax.set_facecolor(SURF)
    off = 0.17
    for r, (lab, _, dk, dn, ak, an) in enumerate(SAMPLES):
        y = len(SAMPLES) - 1 - r
        for k, n, dy, col, mk, name in ((dk, dn, off, C_D, 'o', 'Deliberate'), (ak, an, -off, C_A, 's', 'Accidental')):
            p, lo, hi = wilson(k, n)
            ax.plot([lo, hi], [y + dy] * 2, color=col, lw=2, solid_capstyle='round', zorder=2)
            ax.plot(p, y + dy, marker=mk, ms=7, color=col, mec=SURF, mew=2, zorder=3,
                    label=name if r == 0 else None)
            ax.text(hi + 0.02, y + dy, f'{k}/{n}', va='center', ha='left', fontsize=8, color=INK2)
    ax.set_yticks(range(len(SAMPLES)))
    ax.set_yticklabels([s[0] for s in reversed(SAMPLES)], fontsize=8)
    ax.set_xlim(-0.02, 1.12); ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0]); ax.set_xticklabels(['0', '0.25', '0.5', '0.75', '1'])
    ax.set_xlabel('Share of divergences repaired in the contract (SPEC), Wilson 95% CI')
    ax.grid(axis='x', color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
    ax.tick_params(axis='y', length=0)
    leg = ax.legend(loc='upper center', bbox_to_anchor=(0.45, 1.13), ncol=2, frameon=False, fontsize=8, labelcolor=INK2)
    fig.tight_layout()
    out = Path(__file__).resolve().parent
    fig.savefig(out / 'fig_kind_direction.pdf', facecolor=SURF)
    fig.savefig(out / 'fig_kind_direction.png', dpi=200, facecolor=SURF)
    with open(out / 'fig_kind_direction_table.csv', 'w') as f:
        f.write('sample,source,kind,spec,n,p,wilson_lo,wilson_hi\n')
        for lab, src, dk, dn, ak, an in SAMPLES:
            for kind, k, n in (('DELIBERATE', dk, dn), ('ACCIDENTAL', ak, an)):
                p, lo, hi = wilson(k, n); f.write(f'"{lab.replace(chr(10), " ")}",{src},{kind},{k},{n},{p:.3f},{lo:.3f},{hi:.3f}\n')


if __name__ == '__main__':
    main()
