"""Convert R1_draft.md into an ACM acmart (acmsmall, review, anonymous) LaTeX source: latex/main.tex.
Handles the subset of Markdown used in the draft: # title, ## sections, ### subsections, nested -/1. lists, pipe tables,
**bold**, *italic*, `code`, [Pnnn] and (arXiv NNNN.NNNNN) citations, [`artifact`] references, unicode maths.
Run: /usr/bin/python3 -I -B md2acm.py   (from anywhere; paths are relative to this file)"""
import re
from pathlib import Path

H = Path(__file__).resolve().parent
SRC = H.parent / 'R1_draft.md'; OUT = H / 'main.tex'

SUP = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁻', '0123456789-')
UNI = [('≥', r'$\geq$'), ('≤', r'$\leq$'), ('→', r'$\rightarrow$'), ('←', r'$\leftarrow$'), ('κ', r'$\kappa$'), ('α', r'$\alpha$'),
       ('±', r'$\pm$'), ('≈', r'$\approx$'), ('×', r'$\times$'), ('–', '--'), ('—', '---'), ('“', '``'), ('”', "''"), ('’', "'"),
       ('‘', '`'), ('…', r'\ldots{}'), ('ä', r'\"a'), ('é', r"\'e"), ('ö', r'\"o'), ('ü', r'\"u'), ('⚠️', r'\inferred{}'), ('⚠', r'\inferred{}'),
       ('✓', r'\checkmark{}'), (' ', ' ')]


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
    t = re.sub(r'\[(P\d{3}(?:\s*,\s*P\d{3})*)\]', lambda m: stash(r'~\cite{' + cite_keys(m.group(1)) + '}'), t)
    t = re.sub(r'\(arXiv (\d{4})\.(\d{4,5})\)', lambda m: stash(r'~\cite{arXiv' + m.group(1) + '_' + m.group(2) + '}'), t)
    t = re.sub(r'arXiv (\d{4})\.(\d{4,5})', lambda m: stash(r'\cite{arXiv' + m.group(1) + '_' + m.group(2) + '}'), t)
    t = re.sub(r'`([^`]+)`', lambda m: stash(code(m.group(1))), t)
    # numbers like 1.8 × 10⁻⁶  or 10⁻⁴ -> maths
    t = re.sub(r'(\d+(?:\.\d+)?)\s*×\s*10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)', lambda m: stash(f'${m.group(1)} \\times 10^{{{m.group(2).translate(SUP)}}}$'), t)
    t = re.sub(r'10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)', lambda m: stash(f'$10^{{{m.group(1).translate(SUP)}}}$'), t)
    t = re.sub(r'(\d(?:\.\d+)?)e-(\d+)', lambda m: stash(f'${m.group(1)} \\times 10^{{-{int(m.group(2))}}}$'), t)
    t = esc(t)
    for a, b in UNI: t = t.replace(a, b)
    t = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'\\emph{\1}', t)
    t = re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], t)
    t = re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], t)
    return t


def table(rows):
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows if not re.match(r'^\s*\|?\s*:?-{2,}', r)]
    n = max(len(c) for c in cells)
    spec = 'l' + 'X' * (n - 1) if n > 1 else 'X'
    out = [r'\begin{table}[t]', r'\small', r'\begin{tabularx}{\linewidth}{' + spec + '}', r'\toprule']
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
            lev, txt = len(m.group(1)), re.sub(r'^\d+(\.\d+)*\s+', '', m.group(2)).strip()
            if txt.lower() == 'abstract': mode = 'abstract'
            else:
                mode = None
                cmd = {2: 'section', 3: 'subsection', 4: 'subsubsection'}[lev]
                body.append(f'\\{cmd}{{{inline(txt)}}}')
            i += 1; continue
        tgt = abstract if mode == 'abstract' else body
        if l.lstrip().startswith('|'):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'): rows.append(lines[i]); i += 1
            tgt.extend(table(rows)); continue
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
        if l.strip().startswith('**Figure 1**'):
            body += [r'\begin{figure}[t]', r'\centering', r'\includegraphics[width=\linewidth]{figures/fig_kind_direction.pdf}',
                     r'\caption{Share of divergences repaired in the contract (SPEC), by divergence kind, with Wilson 95\% CIs. '
                     r'Rows are not independent samples (see text).}', r'\Description{Forest-style plot of SPEC shares for deliberate and accidental divergences across samples.}',
                     r'\label{fig:kind}', r'\end{figure}']
            i += 1; continue
        if l.strip() == '': tgt.append(''); i += 1; continue
        tgt.append(inline(l.strip())); i += 1
    return title, abstract, body


PRE = r"""%% Generated by md2acm.py from R1_draft.md -- edit the Markdown, then regenerate.
\documentclass[acmsmall,screen,review,anonymous]{acmart}
\usepackage{tabularx}
\usepackage{amssymb}
\newcommand{\inferred}{\textsuperscript{\dag}}
\newcommand{\artifact}[1]{{\footnotesize [artifact: #1]}}
\setcopyright{none}
\acmConference[ISSTA '27]{ACM SIGSOFT International Symposium on Software Testing and Analysis}{September 2027}{Singapore}
\begin{document}
"""


def main():
    title, abstract, body = convert(SRC.read_text(encoding='utf-8'))
    tex = PRE + f'\\title{{{inline(title)}}}\n\\author{{Anonymous Author(s)}}\n\\begin{{abstract}}\n' + '\n'.join(abstract).strip() + \
        '\n\\end{abstract}\n\\maketitle\n\n' + '\n'.join(body) + \
        '\n\n\\bibliographystyle{ACM-Reference-Format}\n\\bibliography{../references}\n\\end{document}\n'
    tex = re.sub(r'\n{3,}', '\n\n', tex)
    OUT.write_text(tex, encoding='utf-8')
    bad = sorted({ch for ch in tex if ord(ch) > 127})
    print(f'wrote {OUT} ({len(tex.splitlines())} lines); non-ASCII left: {"".join(bad) or "none"}')


if __name__ == '__main__':
    main()
