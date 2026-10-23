#!/usr/bin/env python3
"""Validation gates 1-4 for study 002."""
import os, sys, json
import numpy as np
import pandas as pd
from scipy.stats import norm, spearmanr
import torch

CODE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE)
from tvl_alpha import simulate_batch, assert_alpha1_bit_identical

ONE = "/workspace/eval/followup/001-001-living-update"
OUT = "/workspace/eval/followup/002-002-theory-update/results"
LIT = "/workspace/eval/followup_staging/shared-data/literature"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
mT, sT = 0.6, 0.1
N, NE, I, C0 = 1000, 500, 80, 10.0
TOP_DECILE_CUT = mT + norm.ppf(0.9) * sT


def reproduce_baseline(R=1000, seed=1, chunk=100):
    """Bit-identical (alpha=1) reproduction of 001 g2 baseline (seeds 1..10)."""
    acc = {k: [] for k in ["winner_pct", "win_decile", "top20", "persist_y2y"]}
    done = 0; cid = 0
    while done < R:
        r = min(chunk, R - done)
        res = simulate_batch(r, N, NE, I, mT, sT, 50, C0=C0, device=DEVICE,
                             seed=seed + cid, truncate_talent=True, record_traj=True, alpha=1.0)
        succ = res["success"].cpu().numpy(); tal = res["talent"].cpu().numpy()
        traj = res["traj"].cpu().numpy()
        for i in range(r):
            s = succ[i]; t = tal[i]
            wi = int(np.argmax(s)); wt = t[wi]
            acc["winner_pct"].append((t < wt).mean())
            acc["win_decile"].append(float(wt > TOP_DECILE_CUT))
            acc["top20"].append(np.sort(s)[::-1][:int(0.2 * N)].sum() / s.sum())
            ys = list(range(40, 81, 2)); rhos = []
            for a_, b_ in zip(ys[:-1], ys[1:]):
                ca = traj[i, :, a_]; cb = traj[i, :, b_]
                tp = np.argsort(ca)[::-1][:100]
                rr = spearmanr(ca[tp], cb[tp]).statistic
                if np.isfinite(rr): rhos.append(rr)
            acc["persist_y2y"].append(np.mean(rhos))
        done += r; cid += 1
    return {k: np.asarray(v, float) for k, v in acc.items()}


def main():
    gates = {}

    # ---- Gate 1: 001 completed + G1-G3 passed ----
    card = json.load(open(os.path.join(ONE, "result_card.json")))
    g001 = json.load(open(os.path.join(ONE, "results", "gates.json")))
    g1_ok = (card.get("status") == "completed"
             and g001["G1_integrity"]["status"] == "PASS"
             and g001["G2_model_reference"]["status"] == "PASS"
             and all(v.get("PASS") for k, v in g001["G3_proxy_validity"].items() if isinstance(v, dict) and "PASS" in v))
    gates["gate1_001_completed_and_gated"] = {"pass": bool(g1_ok),
        "detail": {"status": card.get("status"), "G1": g001["G1_integrity"]["status"],
                   "G2": g001["G2_model_reference"]["status"],
                   "G3": {k: v.get("PASS") for k, v in g001["G3_proxy_validity"].items() if isinstance(v, dict)}}}

    # ---- Gate 2: (alpha=1,pL=50) reproduces tvl_reference within Monte-Carlo CI ----
    ref = pd.read_csv(os.path.join(ONE, "results", "tvl_reference.csv"))
    base = ref[ref.block == "baseline_pL50"].iloc[0]
    rep = reproduce_baseline()
    def mean_se(x): return float(x.mean()), float(x.std(ddof=1) / np.sqrt(len(x)))
    checks = {}
    for name, key, refcol in [("winner_pct_emp", "winner_pct", "winner_pct_emp_mean"),
                              ("P_winner_top_decile", "win_decile", "P_winner_top_decile"),
                              ("top20_share", "top20", "top20_share_mean"),
                              ("persist_y2y_top100", "persist_y2y", "persist_y2y_top100_mean")]:
        m, se = mean_se(rep[key])
        refv = float(base[refcol])
        # bit-identical 1000-run reproduction should match to MC noise ~0; within 3 MC-SE is the CI test
        checks[name] = {"reproduced_mean": m, "reproduced_mcse": se, "ref_001": refv,
                        "abs_diff": abs(m - refv), "within_3_mcse": bool(abs(m - refv) <= 3 * max(se, 1e-9) + 1e-6)}
    # also the independent grid cell
    grid = pd.read_csv(os.path.join(OUT, "calibration_grid.csv"))
    gc = grid[(grid.alpha == 1.0) & (grid.p_L == 50)].iloc[0]
    grid_cell = {k: float(gc[k]) for k in ["top20_capital_share", "winner_pct_emp",
                                           "P_winner_top_decile", "persist_y2y_top100"]}
    gates["gate2_anchor_reproduces_tvl_reference"] = {
        "pass": bool(all(c["within_3_mcse"] for c in checks.values())),
        "bit_identical_1000run_reproduction": checks,
        "independent_grid_cell_alpha1_pL50": grid_cell,
        "note": "1000-run reproduction uses alpha=1 (bit-identical path) with 001's seed/chunk recipe "
                "(seeds 1..10, chunk 100); agreement is to Monte-Carlo noise."}

    # ---- Gate 3: literature numbers trace to PROVENANCE.md with verification level ----
    prov = open(os.path.join(LIT, "PROVENANCE.md")).read()
    staged_pdfs = ["zappala2023", "janosov2020", "sobkowicz2020", "liu2020_hrcnz", "heyard2022_snsf"]
    abstract_verified = {"Bol2018": "Bol, de Vaan & van de Rijt, PNAS 115(19):4887",
                         "LevittMiles2014": "Levitt & Miles, J. Sports Economics 15(1):31"}
    lit_trace = {}
    for tag in staged_pdfs:
        present = any(tag.split("_")[0] in f for f in os.listdir(LIT))
        lit_trace[tag] = {"level": "staged-PDF", "in_provenance": tag.split("2")[0] in prov.lower() or tag[:5] in prov.lower(),
                          "pdf_present": present}
    for tag, needle in abstract_verified.items():
        lit_trace[tag] = {"level": "abstract-verified (dagger)", "in_provenance": needle.split(",")[0] in prov,
                          "pdf_present": False}
    # Csurilla 2023 is named in the T2 spec but NOT staged in PROVENANCE -> recorded as untraceable
    lit_trace["Csurilla2023"] = {"level": "NOT in staged PROVENANCE.md",
                                 "in_provenance": "Csurilla" in prov, "pdf_present": False,
                                 "handling": "direction-only qualitative note; no number cited (gate-3 compliant: no untraceable number used)"}
    gates["gate3_literature_traceable"] = {
        "pass": bool(all(v["in_provenance"] for k, v in lit_trace.items() if "NOT" not in v["level"])),
        "traces": lit_trace}

    # ---- Gate 4: alpha=1 bit-identical to staged engine ----
    g4 = assert_alpha1_bit_identical(device=DEVICE)
    gates["gate4_alpha1_bit_identical"] = {"pass": bool(g4["ALL_BIT_IDENTICAL"]), "detail": g4}

    gates["ALL_GATES_PASS"] = bool(all(gates[g]["pass"] for g in gates if g.startswith("gate")))
    json.dump(gates, open(os.path.join(OUT, "gates_002.json"), "w"), indent=2)
    print(json.dumps({g: gates[g]["pass"] for g in gates if g.startswith("gate")}, indent=2))
    print("ALL_GATES_PASS:", gates["ALL_GATES_PASS"])
    print("\ngate2 reproduction vs 001 baseline:")
    for k, c in checks.items():
        print(f"   {k:20s} repro={c['reproduced_mean']:.5f} ref001={c['ref_001']:.5f} "
              f"diff={c['abs_diff']:.2e} within_3mcse={c['within_3_mcse']}")


if __name__ == "__main__":
    main()
