#!/usr/bin/env python3
"""T2 reconciliation table: our T1 fitted alpha per domain beside the 2018-2026
literature estimates (same-construct-family comparisons only; cross-construct
comparisons kept qualitative). Every number traces to literature/PROVENANCE.md;
abstract-verified numbers carry a dagger (+).
"""
import os, json
import pandas as pd

OUT = "/workspace/eval/followup/002-002-theory-update/results"
fits = json.load(open(os.path.join(OUT, "domain_fits.json")))

TENNIS_NOTE = ("BINDING: our fitted alpha is a CAREER-level talent-leverage in the point-free TvL "
               "engine; Zappala's a is a per-POINT talent weight inside a tournament-structured ABM. "
               "They are NOT the same parameter and are compared only after this is acknowledged. "
               "They disagree in the informative direction: points are luck-dominated (a=0.20-0.30) "
               "yet careers aggregate skill, which pushes the career-level leverage to its ceiling "
               "(alpha=1) -- the aggregation paradox, not a contradiction.")

rows = [
    {"row": "our_fit_tennis", "quantity": "fitted alpha (career leverage, T1 nearest cell)",
     "value": fits["tennis"]["fitted_alpha"], "construct_family": "TvL career-level leverage (this study)",
     "dagger": "", "note": "nearest grid cell; tennis FAILS joint 3-SE fit (winner-skill & persistence unreachable)"},
    {"row": "our_fit_movies", "quantity": "fitted alpha (career leverage, T1 nearest cell)",
     "value": fits["movies"]["fitted_alpha"], "construct_family": "TvL career-level leverage (this study)",
     "dagger": "", "note": "nearest grid cell; movies FAILS joint 3-SE fit"},
    {"row": "our_fit_chess", "quantity": "fitted alpha (persistence-only)",
     "value": fits["chess"]["fitted_alpha"], "construct_family": "TvL career-level leverage (this study)",
     "dagger": "", "note": "persistence-only fit; FAILS (model y2y ~0.96 > chess 0.87)"},
    {"row": "our_fit_baseball", "quantity": "fitted alpha (career leverage, T1 nearest cell)",
     "value": fits["baseball"]["fitted_alpha"], "construct_family": "TvL career-level leverage (this study)",
     "dagger": "", "note": "nearest grid cell; FAILS joint 3-SE fit"},
    {"row": "Zappala2023_tennis", "quantity": "talent weight a (per point)",
     "value": "0.20-0.30", "construct_family": "point-level weight in a tournament-structured ABM — different aggregation level; see T2 note",
     "dagger": "", "note": "Chaos Solitons & Fractals 176:114088 (staged PDF); a=1 => only talent. " + TENNIS_NOTE},
    {"row": "Janosov2020_creative", "quantity": "luck/impact share in creative careers",
     "value": "qualitative (Q/R impact-decomposition)", "construct_family": "impact-decomposition, no ex-ante skill",
     "dagger": "", "note": "EPJ Data Science 9:9 (staged PDF); NOT converted to alpha (different construct, out of scope) — luck governs the timing/magnitude of the single biggest hit; comparison stays qualitative"},
    {"row": "LevittMiles2014_poker", "quantity": "a-priori-skilled ROI gap (WSOP 2010)",
     "value": "+30.5% vs -15.6%", "construct_family": "returns-based skill evidence, not a model weight",
     "dagger": "+", "note": "J. Sports Economics 15(1):31 (abstract-verified); evidence that skill IS detectable in poker returns — consistent with alpha>0, not a fitted weight"},
    {"row": "Sobkowicz2020_sprint", "quantity": "luck contribution lower bound (100m dash)",
     "value": "small but non-zero (lower bound)", "construct_family": "sprint randomness lower bound",
     "dagger": "", "note": "Physica A 557:124899 (staged PDF); a small non-zero luck floor even in the most skill-stringent sport — sets a lower bound on luck, i.e. an UPPER bound on effective alpha<1 in physical sport"},
    {"row": "Csurilla2023_3x3v5v5", "quantity": "3x3 vs 5v5 luck direction",
     "value": "direction-only (NOT a staged number)", "construct_family": "3x3 vs 5v5 direction only",
     "dagger": "", "note": "DEVIATION: Csurilla et al. 2023 is named in the T2 spec but is ABSENT from literature/PROVENANCE.md; no number is cited (gate-3 compliant). Direction-only: fewer-possession formats (3x3) are expected luckier than 5v5 — consistent with luck rising as sample size falls; recorded qualitatively, untraceable to the staged record"},
]

df = pd.DataFrame(rows, columns=["row", "quantity", "value", "construct_family", "dagger", "note"])
df.to_csv(os.path.join(OUT, "reconciliation.csv"), index=False)
json.dump({"binding_tennis_note": TENNIS_NOTE, "rows": rows},
          open(os.path.join(OUT, "reconciliation.json"), "w"), indent=2)
print(df[["row", "quantity", "value", "dagger"]].to_string(index=False))
print("\nBINDING tennis note:\n", TENNIS_NOTE)
