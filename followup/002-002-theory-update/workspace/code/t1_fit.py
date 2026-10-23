#!/usr/bin/env python3
"""T1 per-domain fit: nearest grid cell minimizing standardized L2 distance over
the pre-declared (TvL-B1) statistic list, with the pre-declared 3-SE joint
falsification test. Writes results/domain_fits.csv and domain_fits.json.
"""
import os, json
import numpy as np
import pandas as pd

OUT = "/workspace/eval/followup/002-002-theory-update/results"
grid = pd.read_csv(os.path.join(OUT, "calibration_grid.csv"))
targets = json.load(open(os.path.join(OUT, "domain_targets.json")))

# Pre-declared statistic lists (TvL-B1). poker & musiclab excluded.
STAT_LISTS = {
    "tennis": ["top20_share", "winner_skill_pct", "P_top_decile", "y2y_persist"],
    "chess": ["y2y_persist"],
    "movies": ["top20_share", "top1_share", "winner_skill_pct", "P_top_decile"],
    "baseball": ["top20_share", "top1_share", "winner_skill_pct", "P_top_decile", "OPS_persist"],
}
EXCLUDED = {
    "poker": "TvL-A5 demotion: only staged outputs are the Main-Event power STATEMENT "
             "(not a signature statistic) and a selection-biased descriptive concentration "
             "row; no fittable signature triple.",
    "musiclab": "gated ELSE branch in 001 (shared-data/entertainment/musiclab absent); "
                "no per-world statistics staged.",
}

NEIGH = 1.0  # 1-SE neighbourhood: cells with L2 within 1.0 of the minimum


def fit_domain(dom):
    stats = STAT_LISTS[dom]
    tg = targets[dom]
    # per-cell standardized residuals and L2
    L2 = np.zeros(len(grid))
    zmat = {}
    for s in stats:
        mstat = tg[s]["model_stat"]
        tv = tg[s]["value"]; se = tg[s]["se"]
        z = (grid[mstat].values - tv) / se
        zmat[s] = z
        L2 += z ** 2
    L2 = np.sqrt(L2)
    best = int(np.argmin(L2))
    bc = grid.iloc[best]
    neigh = grid.iloc[np.where(L2 <= L2[best] + NEIGH)[0]][["alpha", "p_L"]]
    neigh_set = [(float(a), int(p)) for a, p in neigh.itertuples(index=False)]

    # per-statistic closest |z| over ALL cells (structural reachability)
    per_stat = {}
    breaks_best = []
    structurally_unreachable = []
    for s in stats:
        z = zmat[s]
        per_stat[s] = {
            "target": tg[s]["value"], "se": tg[s]["se"], "model_stat": tg[s]["model_stat"],
            "model_at_best": float(bc[tg[s]["model_stat"]]),
            "z_at_best": float(zmat[s][best]),
            "min_abs_z_over_grid": float(np.min(np.abs(z))),
        }
        if abs(zmat[s][best]) >= 3:
            breaks_best.append(s)
        if np.min(np.abs(z)) >= 3:
            structurally_unreachable.append(s)

    # pre-declared falsification: does ANY cell fit ALL stats within 3 SE?
    all_within3 = np.ones(len(grid), bool)
    for s in stats:
        all_within3 &= (np.abs(zmat[s]) < 3)
    joint_fit_exists = bool(all_within3.any())

    return {
        "domain": dom,
        "stat_list": stats,
        "fitted_alpha": float(bc["alpha"]),
        "fitted_pL": int(bc["p_L"]),
        "L2_min": float(L2[best]),
        "neighbourhood_1SE": neigh_set,
        "joint_3SE_fit_exists": joint_fit_exists,
        "breaking_statistics_at_best": breaks_best,
        "structurally_unreachable_statistics": structurally_unreachable,
        "per_statistic": per_stat,
        "falsification": (
            None if joint_fit_exists else
            f"The TvL family (single alpha-dial, p_L in {{20,35,50,65,80}}) CANNOT jointly "
            f"reproduce {dom}'s signature triple within 3 SE. Breaks: "
            + ", ".join(f"{s} (model best {per_stat[s]['model_at_best']:.3f} vs "
                        f"{per_stat[s]['target']:.3f}, {per_stat[s]['z_at_best']:+.1f} SE"
                        + ("; unreachable in EVERY cell" if s in structurally_unreachable else "")
                        + ")" for s in breaks_best)
        ),
    }


def main():
    fits = {d: fit_domain(d) for d in STAT_LISTS}
    rows = []
    for d, f in fits.items():
        rows.append({
            "domain": d,
            "stat_list": "|".join(f["stat_list"]),
            "fitted_alpha": f["fitted_alpha"],
            "fitted_pL": f["fitted_pL"],
            "L2_min_SE": round(f["L2_min"], 2),
            "neighbourhood_1SE": ";".join(f"({a},{p})" for a, p in f["neighbourhood_1SE"]),
            "joint_3SE_fit": f["joint_3SE_fit_exists"],
            "breaking_stats": "|".join(f["breaking_statistics_at_best"]) or "(none)",
            "structurally_unreachable": "|".join(f["structurally_unreachable_statistics"]) or "(none)",
            "dropped_statistics": "(none; all pre-declared stats available & used)",
        })
    for d, why in EXCLUDED.items():
        rows.append({"domain": d, "stat_list": "EXCLUDED", "fitted_alpha": None, "fitted_pL": None,
                     "L2_min_SE": None, "neighbourhood_1SE": None, "joint_3SE_fit": None,
                     "breaking_stats": None, "structurally_unreachable": None,
                     "dropped_statistics": why})
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "domain_fits.csv"), index=False)
    json.dump(fits, open(os.path.join(OUT, "domain_fits.json"), "w"), indent=2)

    print("=== T1 FITS ===")
    for d, f in fits.items():
        print(f"\n{d}: fitted (alpha={f['fitted_alpha']}, p_L={f['fitted_pL']}), "
              f"L2={f['L2_min']:.1f} SE, joint-3SE-fit={f['joint_3SE_fit_exists']}")
        for s, ps in f["per_statistic"].items():
            print(f"   {s:16s} target={ps['target']:.3f} se={ps['se']:.4f} "
                  f"model@best={ps['model_at_best']:.3f} z={ps['z_at_best']:+.1f} "
                  f"(min|z| over grid={ps['min_abs_z_over_grid']:.1f})")
        if f["falsification"]:
            print("   FALSIFIED:", f["falsification"])


if __name__ == "__main__":
    main()
