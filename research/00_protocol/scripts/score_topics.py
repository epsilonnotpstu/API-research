"""Weighted scoring + sensitivity analysis for Phase E research candidates."""
import json, sys
C = ['novelty', 'feasibility', 'significance', 'data', 'evaluation']
S = {  # 1-5 scores; justification in ranked_research_topics.md
 'R1 Spec-impl mismatch triage + dynamic repair (G14)':   [4.0, 4.0, 4.0, 4.0, 4.0],
 'R2 Downstream value of inferred specs (G9)':            [3.0, 5.0, 3.0, 5.0, 4.0],
 'R3 Behavioural breaking changes benchmark+detector (G1/G2)': [4.0, 3.0, 5.0, 3.0, 4.0],
 'R4 Neutral budget-equal LLM REST tool comparison (G10)': [2.5, 4.0, 3.5, 5.0, 5.0],
 'R5 Spec-quality mutation study for LLM agents (G4)':    [3.0, 4.0, 4.5, 4.0, 3.5],
 'R6 Access-policy testing of REST-wrapping MCP servers (G3)': [3.0, 3.0, 4.0, 3.5, 3.0],
 'R7 Real-world REST authorization benchmark (G5)':       [4.0, 2.0, 4.5, 2.0, 3.5],
}
W = {'base (prompt)': [25, 25, 20, 15, 15],
     'importance-heavy': [30, 15, 30, 10, 15],
     'feasibility-heavy': [15, 35, 15, 20, 15],
     'novelty-heavy': [40, 20, 20, 10, 10],
     'equal': [20, 20, 20, 20, 20]}
out = {}
for wn, w in W.items():
    sc = {k: round(sum(a * b for a, b in zip(v, w)) / 100, 3) for k, v in S.items()}
    out[wn] = sorted(sc.items(), key=lambda x: -x[1])
# one-point perturbation of novelty for R1 and R5 (most uncertain)
pert = {}
for k, d in [('R1 Spec-impl mismatch triage + dynamic repair (G14)', -1), ('R5 Spec-quality mutation study for LLM agents (G4)', +1),
             ('R4 Neutral budget-equal LLM REST tool comparison (G10)', +0.5)]:
    v = S[k][:]; v[0] += d
    pert[f'{k} novelty {d:+}'] = round(sum(a * b for a, b in zip(v, W['base (prompt)'])) / 100, 3)
json.dump({'scores': S, 'weights': W, 'rankings': out, 'perturbation': pert}, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
for wn, r in out.items():
    print('==', wn); [print(f'  {s:.3f}  {k}') for k, s in r]
print(pert)
