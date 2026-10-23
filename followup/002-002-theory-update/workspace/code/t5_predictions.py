#!/usr/bin/env python3
"""T5 falsifiable predictions for the next tick. Each carries sign, magnitude,
interval, and the data that will test it. Empirical bands come from 001's
results; model bands from the T1 grid fitted cells.
"""
import os, json
import numpy as np
import pandas as pd
from scipy.stats import binom

ONE = "/workspace/eval/followup/001-001-living-update"
OUT = "/workspace/eval/followup/002-002-theory-update/results"
grid = pd.read_csv(os.path.join(OUT, "calibration_grid.csv"))
fits = json.load(open(os.path.join(OUT, "domain_fits.json")))
tjson = json.load(open(os.path.join(ONE, "results", "domain_tennis.json")))
cjson = json.load(open(os.path.join(ONE, "results", "domain_chess.json")))


def cell(alpha, pL):
    r = grid[(grid.alpha == alpha) & (grid.p_L == pL)].iloc[0]
    return r


preds = []

# ---- P1: tennis year-end 2026 top-100 persistence ----
tfit = fits["tennis"]
mc = cell(tfit["fitted_alpha"], tfit["fitted_pL"])
model_band = [round(mc["persist_y2y_top100"] - 2 * mc["persist_y2y_top100_mcse"], 3),
              round(mc["persist_y2y_top100"] + 2 * mc["persist_y2y_top100_mcse"], 3)]
emp_rhos = np.array([p["rho"] for p in tjson["persistence_2011_2025"]["pairs"].values()])
emp_mean = float(emp_rhos.mean()); emp_lo, emp_hi = float(emp_rhos.min()), float(emp_rhos.max())
preds.append({
    "id": "P1_tennis_2026_persistence",
    "statement": "Tennis year-end 2026 top-100 points-rank y2y Spearman persistence.",
    "model_prediction": f"model (fitted cell alpha={tfit['fitted_alpha']},pL={tfit['fitted_pL']}) band {model_band} (~0.96, essentially pinned)",
    "empirical_prediction": f"empirical continuation ~{emp_mean:.3f} (2011-2025 range [{emp_lo:.3f},{emp_hi:.3f}])",
    "sign": "model OVER-predicts persistence vs the empirical series",
    "magnitude": f"gap ~{mc['persist_y2y_top100'] - emp_mean:.2f} (model {mc['persist_y2y_top100']:.3f} vs empirical mean {emp_mean:.3f})",
    "interval": {"model_band": model_band, "empirical_2011_2025": [round(emp_lo, 3), round(emp_hi, 3)]},
    "falsifies_model_if": f"2026 year-end top-100 persistence lands in [{emp_lo:.2f},{emp_hi:.2f}] (as the trend implies) rather than the model band {model_band}",
    "test_data": "ATP year-end 2026 top-100 rankings (shared-data/tennis/atp_rankings_current.csv once the 2026 season closes)",
})

# ---- P2: chess Jan-2027 persistence exceeds tennis by >= x ----
cfit = fits["chess"]
cmc = cell(cfit["fitted_alpha"], cfit["fitted_pL"])
chess_emp = float(cjson["persistence_top100"]["mean_rho"])
obs_gap = chess_emp - emp_mean
model_gap = float(cmc["persist_y2y_top100"] - mc["persist_y2y_top100"])
x = 0.10  # conservative lower bound below observed gap 0.19
preds.append({
    "id": "P2_chess_minus_tennis_persistence_gap",
    "statement": "Chess Jan-2027 top-100 persistence minus tennis year-end-2026 top-100 persistence.",
    "model_prediction": f"model gap ~{model_gap:+.3f} (both pinned near 0.96 -> NO ordering)",
    "empirical_prediction": f"empirical gap ~{obs_gap:.3f} (chess {chess_emp:.3f} - tennis {emp_mean:.3f})",
    "sign": "chess > tennis (empirical ladder); model predicts ~0",
    "magnitude": f">= {x} (observed 2015-2026 gap {obs_gap:.2f})",
    "interval": {"predicted_gap_lower_bound": x, "observed_gap": round(obs_gap, 3), "model_gap": round(model_gap, 3)},
    "falsifies_model_if": "the gap stays >= 0.10 (it does empirically); the model's point-free structure predicts ~0, so a persistent gap further falsifies the model's persistence channel",
    "test_data": "FIDE January 2027 standard list (top-100) vs ATP year-end 2026 top-100",
})

# ---- P3: 2027 WSOP Main-Event repeat-champion count vs no-skill null E_0 ----
ev = pd.read_csv(os.path.join(ONE, "results", "poker_events.csv"))
ev = ev.dropna(subset=["entrants"])
w = ev[(ev.year >= 1990) & (ev.year <= 2026)].copy()        # window extended one year (2026 observed)
champs_through_2026 = set(w.champion.dropna())
D = len(champs_through_2026)                                  # distinct prior winners eligible to repeat
n_2025 = int(ev[ev.year == 2025].entrants.iloc[0])
n_2027 = n_2025                                               # field assumed within +-20% of 2025 entrants
E0 = D / n_2027
band20 = [int(round(0.8 * n_2025)), int(round(1.2 * n_2025))]
# repeat count in 2027 ~ Binomial(1, E0): 95% null interval
lo, hi = int(binom.ppf(0.025, 1, E0)), int(binom.ppf(0.975, 1, E0))
preds.append({
    "id": "P3_wsop_2027_repeat_champion",
    "statement": "2027 WSOP Main-Event repeat-champion count under the no-skill null (001 power-statement machinery extended one year).",
    "model_prediction": f"no-skill null E_0 = {E0:.4f} = D({D})/n({n_2027}); repeat count ~ Binomial(1, {E0:.4f})",
    "empirical_prediction": "0 repeat champions (observed count 1990-2026 is 0)",
    "sign": "count stays at the no-skill-null expectation",
    "magnitude": f"E_0 = {E0:.4f} expected repeats in 2027",
    "interval": {"E0": round(E0, 4), "binomial_95_null_interval_count": [lo, hi],
                 "field_assumed_n2027": n_2027, "field_pm20pct_band": band20,
                 "distinct_prior_champions_D": D},
    "falsifies_model_if": "a repeat 2027 champion appears AND field size is materially < the modern ~8-10k "
                          "(so recurrence would carry power); at n~9.7k the test has essentially no power, as 001 found",
    "test_data": "2027 WSOP Main-Event champion + entrant count (next year's poker_events row)",
    "note": "replaces the previously planned bracelet permutation-null prediction (TvL-A5 demotion: no "
            "permutation null computable from staged data; bracelet concentration descriptive-only).",
})

# ---- P4: MusicLab -- conditional, NOT applicable ----
musiclab_note = ("P4 (MusicLab winner-quality percentile band) is NOT issued: 001 took the honest-exclusion "
                 "ELSE branch (shared-data/entertainment/musiclab absent), so no FULL branch ran. Condition unmet.")

out = {"predictions": preds, "P4_musiclab": musiclab_note}
json.dump(out, open(os.path.join(OUT, "predictions.json"), "w"), indent=2)
for p in preds:
    print(f"\n[{p['id']}] {p['statement']}\n  sign: {p['sign']}\n  magnitude: {p['magnitude']}\n  interval: {p['interval']}\n  test: {p['test_data']}")
print("\n" + musiclab_note)
