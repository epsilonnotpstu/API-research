"""Convert R4_draft.md into an IEEE conference (IEEEtran, double-anonymous) LaTeX source: latex/main.tex.
Derived from research/10_paper/latex/md2acm.py (same Markdown subset). Author-year citations such as [Chen et al. 2026]
are mapped to BibTeX keys through CITE; an unknown citation raises KeyError (so no reference can silently go missing).
"**Figure 1.** caption" on its own line inserts figures/fig_r4_setup.pdf. Text after "## References" is not converted.
Run: /usr/bin/python3 -I -B md2ieee.py   (paths are relative to this file). Compile: pdflatex main; bibtex main; pdflatex main x2."""
import re
from pathlib import Path

H = Path(__file__).resolve().parent
SRC = H.parent / 'R4_draft.md'; OUT = H / 'main.tex'
CITE = {'Huang et al. 2024': 'huang2024bola', 'Lercher et al. 2024': 'lercher2024evolution', 'Atlidakis et al. 2019': 'atlidakis2019restler'}
STAR = {'data availability', 'disclosure of ai use', 'ai use disclosure'}

SUP = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁻', '0123456789-')
UNI = [('≥', r'$\geq$'), ('≤', r'$\leq$'), ('→', r'$\rightarrow$'), ('←', r'$\leftarrow$'), ('κ', r'$\kappa$'), ('α', r'$\alpha$'),
       ('±', r'$\pm$'), ('≈', r'$\approx$'), ('×', r'$\times$'), ('–', '--'), ('—', '---'), ('“', '``'), ('”', "''"), ('’', "'"),
       ('‘', '`'), ('…', r'\ldots{}'), ('ä', r'\"a'), ('é', r"\'e"), ('ö', r'\"o'), ('ü', r'\"u'), ('⚠️', r'\inferred{}'), ('⚠', r'\inferred{}'),
       ('✓', r'\checkmark{}'), ('§', r'\S{}'), (' ', ' ')]


def esc(t):
    return (t.replace('\\', r'\textbackslash{}').replace('&', r'\&').replace('%', r'\%').replace('$', r'\$').replace('#', r'\#')
            .replace('_', r'\_').replace('{', r'\{').replace('}', r'\}').replace('~', r'\textasciitilde{}').replace('^', r'\textasciicircum{}')
            .replace('<', r'\textless{}').replace('>', r'\textgreater{}'))


def code(t):
    return r'\texttt{' + esc(t).replace('/', r'/\allowbreak{}') + '}'


def cite_keys(s):
    return ','.join(k.strip() for k in s.split(','))


def inline(t):
    """Markdown inline -> LaTeX. Protect code and citations first, then escape, then restore."""
    keep = []

    def stash(v):
        keep.append(v); return f'\x00{len(keep) - 1}\x00'
    t = re.sub(r'\[`([^`]+)`(?:,\s*`([^`]+)`)*\]', lambda m: stash(r'\artifact{' + ', '.join(code(x) for x in re.findall(r'`([^`]+)`', m.group(0))) + '}'), t)
    t = re.sub(r'\s?\[([^\]`]*?(?:19|20)\d\d)\]', lambda m: stash(r'~\cite{' + CITE[m.group(1).strip()] + '}'), t)
    t = re.sub(r'\(arXiv (\d{4})\.(\d{4,5})\)', lambda m: stash(r'~\cite{arXiv' + m.group(1) + '_' + m.group(2) + '}'), t)
    t = re.sub(r'arXiv (\d{4})\.(\d{4,5})', lambda m: stash(r'\cite{arXiv' + m.group(1) + '_' + m.group(2) + '}'), t)
    t = re.sub(r'`([^`]+)`', lambda m: stash(code(m.group(1))), t)
    # numbers like 1.8 × 10⁻⁶  or 10⁻⁴ -> maths
    t = re.sub(r'(\d+(?:\.\d+)?)\s*×\s*10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)', lambda m: stash(f'${m.group(1)} \\times 10^{{{m.group(2).translate(SUP)}}}$'), t)
    t = re.sub(r'10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)', lambda m: stash(f'$10^{{{m.group(1).translate(SUP)}}}$'), t)
    t = re.sub(r'(\d(?:\.\d+)?)e-(\d+)', lambda m: stash(f'${m.group(1)} \\times 10^{{-{int(m.group(2))}}}$'), t)
    t = esc(t)
    t = re.sub(r'"([^"]*)"', r"``\1''", t)
    for a, b in UNI: t = t.replace(a, b)
    t = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'\\emph{\1}', t)
    t = re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], t)
    t = re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], t)
    return t


def table(rows, cap=None):
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows if not re.match(r'^\s*\|?\s*:?-{2,}', r)]
    n = max(len(c) for c in cells)
    spec = 'X' + 'l' * (n - 1) if n > 1 else 'X'   # first column wraps (narrow IEEE column)
    out = [r'\begin{table}[t]'] + ([r'\caption{' + inline(cap) + '}'] if cap else []) + [r'\footnotesize', r'\begin{tabularx}{\linewidth}{' + spec + '}', r'\toprule']
    for i, c in enumerate(cells):
        c += [''] * (n - len(c))
        out.append(' & '.join(inline(x) for x in c) + r' \\')
        if i == 0: out.append(r'\midrule')
    out += [r'\bottomrule', r'\end{tabularx}', r'\end{table}']
    return out


def lists(block):
    """block: list of (indent, ordered, text) -> nested itemize/enumerate"""
    out, stack = [], []
    for ind, ordered, text in block:
        lvl = ind // 2
        while len(stack) > lvl + 1: out.append(r'\end{' + stack.pop() + '}')
        if len(stack) == lvl + 1 and stack[-1] != ('enumerate' if ordered else 'itemize'):
            out.append(r'\end{' + stack.pop() + '}')
        while len(stack) < lvl + 1:
            env = 'enumerate' if ordered else 'itemize'; stack.append(env); out.append(r'\begin{' + env + '}')
        out.append(r'\item ' + inline(text))
    while stack: out.append(r'\end{' + stack.pop() + '}')
    return out


def convert(md):
    lines = md.splitlines(); body = []; title = ''; abstract = []; mode = None; i = 0
    while i < len(lines):
        l = lines[i]
        if l.startswith('# ') and not title: title = l[2:].strip(); i += 1; continue
        if re.match(r'^\*Working draft', l) or l.strip() == '---': i += 1; continue
        m = re.match(r'^(#{2,4})\s+(.*)$', l)
        if m:
            lev, txt = len(m.group(1)), re.sub(r'^\d+(\.\d+)*\.?\s+', '', m.group(2)).strip()
            if txt.lower() == 'abstract': mode = 'abstract'
            elif txt.lower().startswith('references'): break
            else:
                mode = None
                cmd = {2: 'section', 3: 'subsection', 4: 'subsubsection'}[lev]
                if txt.lower() in STAR: cmd += '*'
                body.append(f'\\{cmd}{{{inline(txt)}}}')
            i += 1; continue
        tgt = abstract if mode == 'abstract' else body
        mt = re.match(r'^\*\*Table \d+\.\*\*\s*(.*)$', l.strip())
        if mt and i + 1 < len(lines) and lines[i + 1].lstrip().startswith('|'):
            cap = mt.group(1); i += 1; l = lines[i]
        else: cap = None
        if l.lstrip().startswith('|'):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'): rows.append(lines[i]); i += 1
            tgt.extend(table(rows, cap)); continue
        if re.match(r'^\s*(?:[-*]|\d+\.)\s+', l):
            blk = []
            while i < len(lines) and (re.match(r'^\s*(?:[-*]|\d+\.)\s+', lines[i]) or (lines[i].startswith('   ') and lines[i].strip() and blk)):
                mm = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', lines[i])
                if mm: blk.append((len(mm.group(1).replace('\t', '  ')) // 1 if False else len(mm.group(1)) - (len(mm.group(1)) % 2), mm.group(2)[0].isdigit(), mm.group(3)))
                else: blk[-1] = (blk[-1][0], blk[-1][1], blk[-1][2] + ' ' + lines[i].strip())
                i += 1
            norm = []
            for ind, o, t in blk:   # numbered items use 3-space child indent in the draft
                norm.append((ind if ind % 2 == 0 else ind - 1, o, t))
            tgt.extend(lists(norm)); continue
        mf = re.match(r'^\*\*Figure 1\.\*\*\s*(.*)$', l.strip())
        if mf:
            body += [r'\begin{figure}[t]', r'\centering', r'\includegraphics[width=\linewidth]{fig_r4_setup.pdf}',
                     r'\caption{' + inline(mf.group(1)) + '}', r'\label{fig:kind}', r'\end{figure}']
            i += 1; continue
        if l.strip() == '': tgt.append(''); i += 1; continue
        tgt.append(inline(l.strip())); i += 1
    return title, abstract, body


PRE = r"""%% Generated by md2ieee.py from R4_draft.md -- edit the Markdown, then regenerate.
\documentclass[conference]{IEEEtran}
\usepackage{cite}
\usepackage{graphicx}
\graphicspath{{../figures/}{figures/}{./}}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{amssymb}
\usepackage[hidelinks]{hyperref}
\newcommand{\inferred}{\textsuperscript{\dag}}
\newcommand{\artifact}[1]{{\footnotesize [artifact: #1]}}
\begin{document}
"""


def main():
    title, abstract, body = convert(SRC.read_text(encoding='utf-8'))
    tex = PRE + f'\\title{{{inline(title)}}}\n\\author{{\\IEEEauthorblockN{{Anonymous Author(s)}}\\IEEEauthorblockA{{Under double-anonymous review}}}}\n\\maketitle\n' \
        '\\begin{abstract}\n' + '\n'.join(abstract).strip() + '\n\\end{abstract}\n\n' + '\n'.join(body) + \
        '\n\n\\bibliographystyle{IEEEtran}\n\\bibliography{references}\n\\end{document}\n'
    tex = re.sub(r'\n{3,}', '\n\n', tex)
    OUT.write_text(tex, encoding='utf-8')
    bad = sorted({ch for ch in tex if ord(ch) > 127})
    envs = re.findall(r'\\(begin|end)\{(\w+\*?)\}', tex); stack = []
    for be, e in envs:
        if be == 'begin': stack.append(e)
        else: assert stack and stack.pop() == e, f'unbalanced environment {e}'
    assert not stack, stack
    assert tex.count('{') == tex.count('}') + tex.count('\\{') - tex.count('\\}'), 'unbalanced braces'
    print(f'wrote {OUT} ({len(tex.splitlines())} lines); environments balanced; non-ASCII left: {"".join(bad) or "none"}')


if __name__ == '__main__':
    main()
