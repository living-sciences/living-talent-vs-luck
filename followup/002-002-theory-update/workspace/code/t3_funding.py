#!/usr/bin/env python3
"""T3 funding confrontation (engine-vs-engine; TvL-B3: NO paper Section-3 P_T/F_T
value is used as a quantitative reference band anywhere).

Re-runs the paper's 8-injection funding design on the alpha-generalized engine:
  egalitarian = ALL EQUAL 1u/agent      (kind=equal, units=1)
  elitarian   = 25% BEST 10u            (kind=best, frac=0.25, units=10)
for alpha in {0,0.1,...,1.0} (covers fitted tennis=1.0 and fitted movies=1.0 and 1.0),
200 runs each (paired seeds), plus NO FUNDING for PT0(alpha).

Efficiency (paper's definition, reused from reimpl/run_funding.py):
  PT  = mean over runs of [% of agents with T>mT+sigmaT(=0.7) and final C>C0(=10)]
  PT* = PT - PT0 ;  E = PT*/FT
Egalitarian "beats" elitarian iff E_egal > E_elit (the paper's C5 ordering).
Reports the flip-alpha (funding-claim robustness frontier) if any.
"""
import os, sys, json
import numpy as np
import torch

CODE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE)
from tvl_alpha import simulate_batch

OUT = "/workspace/eval/followup/002-002-theory-update/results"
CKPT = "/workspace/eval/followup/002-002-theory-update/workspace/checkpoints"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
mT, sT = 0.6, 0.1
N, NE, I, C0 = 1000, 500, 80, 10.0
INJECT = [10, 20, 30, 40, 50, 60, 70, 80]
ALPHAS = [round(0.1 * i, 1) for i in range(11)]
RUNS = 200
SEED = 7000

STRATS = {
    "no_funding": None,
    "egalitarian_equal_1u": dict(kind="equal", units=1, steps=INJECT),
    "elitarian_25best_10u": dict(kind="best", frac=0.25, units=10, steps=INJECT),
}


def run_strategy(funding, alpha, runs=RUNS, chunk=100):
    thr = mT + sT
    pts, fts = [], []
    done = 0; cid = 0
    while done < runs:
        R = min(chunk, runs - done)
        out = simulate_batch(R, N, NE, I, mT, sT, 50, C0=C0, device=DEVICE,
                             seed=SEED + cid, truncate_talent=True, funding=funding,
                             alpha=alpha)
        tal = out["talent"]; succ = out["success"]; inv = out["invested"]
        mask = tal > thr
        pt = 100.0 * ((succ > C0) & mask).sum(1).float() / mask.sum(1).clamp(min=1).float()
        pts.append(pt.cpu().numpy()); fts.append(inv.cpu().numpy())
        done += R; cid += 1
    return float(np.concatenate(pts).mean()), float(np.concatenate(fts).mean())


def main():
    rows = []
    for a in ALPHAS:
        res = {}
        for name, f in STRATS.items():
            PT, FT = run_strategy(f, a)
            res[name] = {"PT": PT, "FT": FT}
        PT0 = res["no_funding"]["PT"]
        for name in ("egalitarian_equal_1u", "elitarian_25best_10u"):
            r = res[name]
            r["PT_star"] = r["PT"] - PT0
            r["E"] = r["PT_star"] / r["FT"] if r["FT"] > 0 else 0.0
        eg = res["egalitarian_equal_1u"]; el = res["elitarian_25best_10u"]
        rows.append({
            "alpha": a, "PT0": round(PT0, 3),
            "egal_PT": round(eg["PT"], 3), "egal_FT": round(eg["FT"], 0),
            "egal_PTstar": round(eg["PT_star"], 3), "egal_E": eg["E"],
            "elit_PT": round(el["PT"], 3), "elit_FT": round(el["FT"], 0),
            "elit_PTstar": round(el["PT_star"], 3), "elit_E": el["E"],
            "egal_minus_elit_E": eg["E"] - el["E"],
            "egalitarian_beats_elitarian": bool(eg["E"] > el["E"]),
        })
        print(f"alpha={a}: egal_E={eg['E']:.3e} elit_E={el['E']:.3e} "
              f"egal_wins={eg['E']>el['E']}  (PT*: egal {eg['PT_star']:.2f} vs elit {el['PT_star']:.2f})")

    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "funding_comparison.csv"), index=False)

    # flip-alpha: smallest alpha where egalitarian stops beating elitarian
    wins = df.egalitarian_beats_elitarian.values
    flip_alpha = None
    for i in range(1, len(wins)):
        if wins[i] != wins[0]:
            flip_alpha = float(df.alpha.values[i]); break
    fitted = json.load(open(os.path.join(OUT, "domain_fits.json")))
    fit_tennis = fitted["tennis"]["fitted_alpha"]
    fit_movies = fitted["movies"]["fitted_alpha"]
    career_max = max(fit_tennis, fit_movies)

    # verdict vocabulary (TvL-B4). Two axes, reported separately:
    #   model_internal = robustness of the ordering to the talent-leverage dial
    #   P4_verdict_word (M5) = the funding-claim-vs-reality verdict the reader asked for
    if flip_alpha is None:
        model_internal = "robust (no flip in [0,1])"
    else:
        tennis_side = "egal" if df[df.alpha == fit_tennis].egalitarian_beats_elitarian.values[0] else "elit"
        movies_side = "egal" if df[df.alpha == fit_movies].egalitarian_beats_elitarian.values[0] else "elit"
        if tennis_side != movies_side:
            model_internal = (f"domain-dependent (tennis alpha={fit_tennis} on {tennis_side} side, "
                              f"movies alpha={fit_movies} on {movies_side} side of flip-alpha={flip_alpha})")
        elif flip_alpha < career_max:
            model_internal = "model-fragile"
        else:
            model_internal = "robust (flip at alpha >= fitted career alphas)"
    # P4 verdict word (M5): no staged outcome study shows merit>lottery -> not 'contradicted';
    # ordering is robust across the fitted career alphas and no real outcome evidence contradicts
    # -> the pre-declared DEFAULT applies.
    ordering_robust_across_fitted = bool(
        df[df.alpha == fit_tennis].egalitarian_beats_elitarian.values[0]
        and df[df.alpha == fit_movies].egalitarian_beats_elitarian.values[0])
    contradicting_outcome_study = False  # none staged through 2026
    if contradicting_outcome_study:
        verdict = "contradicted"
    elif ordering_robust_across_fitted:
        verdict = "untested but consistent"
    else:
        verdict = model_internal
    summary = {
        "flip_alpha": flip_alpha,
        "egalitarian_beats_elitarian_at_alpha0": bool(wins[0]),
        "egal_minus_elit_E_range": [round(float(df.egal_minus_elit_E.min()), 6),
                                    round(float(df.egal_minus_elit_E.max()), 6)],
        "fitted_tennis_alpha": fit_tennis, "fitted_movies_alpha": fit_movies,
        "career_max_fitted_alpha": career_max,
        "model_internal_robustness": model_internal,
        "verdict_word": verdict,
        "no_flip_card_note": "no flip" if flip_alpha is None else f"flip at alpha={flip_alpha}",
        "falsifier_of_C5": "A lottery-vs-panel OUTCOME comparison at equal budget (e.g. a future "
                           "HRC NZ or SNSF cohort study tracking later research success) that showed "
                           "merit-selected cohorts outperforming lottery cohorts would contradict C5; "
                           "no such outcome study exists in the staged record through 2026.",
        "paper_caveat_verbatim": "the paper's unreleased experiment code evidently differed from the "
                                 "released demo; one F_T cell is an arithmetic error (70000->50000)",
    }
    json.dump(summary, open(os.path.join(OUT, "funding_verdict.json"), "w"), indent=2)
    print("\n=== FUNDING VERDICT ==="); print(json.dumps(summary, indent=2))
    open(os.path.join(CKPT, "T3.done"), "w").write("done")


if __name__ == "__main__":
    main()
