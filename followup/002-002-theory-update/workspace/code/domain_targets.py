#!/usr/bin/env python3
"""Assemble each domain's T1 target statistics and their standardization SEs
("001's bootstrap SEs") from the completed 001 study, re-fetching NOTHING.

Target values are read from 001's results/ domain JSONs (authoritative).
SE hierarchy (pre-declared, recorded per statistic in domain_targets.json):
  (a) 001 bootstrap 95% CI present  -> SE = (ci_hi - ci_lo) / (2*1.959964)
  (b) persistence (mean over year-pairs) -> bootstrap SE over the year-pair rhos
  (c) concentration share, no 001 CI -> bootstrap SE by resampling the per-entity
      success vector (vector reconstructed from staged data via 001's own filters;
      the reconstructed point estimate is asserted == 001's reported share)
  (d) P(top-decile) overlap, no 001 CI -> binomial-proportion SE sqrt(p(1-p)/k),
      k = round(0.1*n) = decile size (analytic; recorded)

Mapping of each domain statistic to the MODEL statistic it is compared against
(T1 distance) is fixed here and echoed into domain_fits.csv:
  top20_share  -> model top20_capital_share
  top1_share   -> model top1_capital_share
  winner_skill_pct -> model winner_pct_emp
  P_top_decile -> model P_winner_top_decile
  y2y_persist / OPS_persist -> model persist_y2y_top100
"""
import os, sys, json
import numpy as np
import pandas as pd

ONE = "/workspace/eval/followup/001-001-living-update"
ONE_RES = os.path.join(ONE, "results")
ONE_CODE = os.path.join(ONE, "workspace", "code")
SHARED = "/workspace/eval/followup_staging/shared-data"
OUT = "/workspace/eval/followup/002-002-theory-update/results"
os.makedirs(OUT, exist_ok=True)

Z = 1.959963985  # 95% normal quantile
RNG = np.random.default_rng(2026)
B = 2000


def se_from_ci(lo, hi):
    return float((hi - lo) / (2 * Z))


def boot_share_se(vec, frac):
    """Bootstrap SE of top-`frac` concentration share of a success vector."""
    v = np.asarray(vec, float)
    n = len(v)
    k = max(1, int(frac * n))
    point = np.sort(v)[::-1][:k].sum() / v.sum()
    ests = np.empty(B)
    for b in range(B):
        s = v[RNG.integers(0, n, n)]
        ests[b] = np.sort(s)[::-1][:k].sum() / s.sum()
    return float(point), float(ests.std(ddof=1))


def boot_pairs_se(rhos):
    """Bootstrap SE of the mean over year-pair Spearman rhos."""
    r = np.asarray([x for x in rhos if np.isfinite(x)], float)
    means = np.array([r[RNG.integers(0, len(r), len(r))].mean() for _ in range(B)])
    return float(r.mean()), float(means.std(ddof=1))


def binom_prop_se(p, n, frac=0.1):
    k = max(1, int(round(frac * n)))
    return float(np.sqrt(max(p * (1 - p), 1e-12) / k))


# ---- reconstruct success vectors (001 filters) for share-SE bootstrap ----
def tennis_titles_vector():
    sys.path.insert(0, ONE_CODE)
    import b1_tennis as b1
    m = b1.load_matches()
    valid = b1.points_won(m)
    counts = b1.career_match_counts(valid)
    panel_ids = counts[counts >= 200].index
    g_full = b1.skill_panel(valid)
    titles, _gs, _nm = b1.success_measures(m)
    skill = g_full.loc[g_full.index.intersection(panel_ids)].skill
    succ = titles.reindex(skill.index).fillna(0)
    return succ.values.astype(float)


def movies_votes_panel():
    import pandas as pd
    IM = os.path.join(SHARED, "entertainment", "imdb")
    rat = pd.read_csv(os.path.join(IM, "title.ratings.tsv.gz"), sep="\t")
    bas = pd.read_csv(os.path.join(IM, "title.basics.tsv.gz"), sep="\t",
                      usecols=["tconst", "titleType"], dtype=str, low_memory=False)
    mov = bas[bas.titleType == "movie"].merge(rat, on="tconst")
    mov["numVotes"] = pd.to_numeric(mov.numVotes, errors="coerce")
    mov["averageRating"] = pd.to_numeric(mov.averageRating, errors="coerce")
    mov = mov[(mov.numVotes >= 1000) & mov.averageRating.notna()].copy()
    return mov.numVotes.values.astype(float)


def baseball_salary_vector():
    import pyreadr
    sal = list(pyreadr.read_r(os.path.join(SHARED, "baseball", "lahman_rda",
                                            "Salaries.RData")).values())[0]
    sc = sal.groupby("playerID").agg(tot=("salary", "sum"), nyr=("yearID", "nunique"))
    sc5 = sc[sc.nyr >= 5]
    return sc5.tot.values.astype(float)


def main():
    dj = {d: json.load(open(os.path.join(ONE_RES, f"domain_{d}.json")))
          for d in ["tennis", "chess", "movies", "baseball"]}

    targets = {}

    # ---------------- TENNIS ----------------
    t = dj["tennis"]
    tv = tennis_titles_vector()
    pt20, se20 = boot_share_se(tv, 0.20)
    assert abs(pt20 - t["P1_shape"]["concentration_titles_incl_zeros"]["top20_share"]) < 1e-6, \
        f"tennis top20 reconstruct mismatch {pt20}"
    pers_rhos = [p["rho"] for p in t["persistence_2011_2025"]["pairs"].values()]
    pm, pse = boot_pairs_se(pers_rhos)
    p2 = t["P2_primary_titles"]
    targets["tennis"] = {
        "top20_share": {"value": p2 and t["P1_shape"]["concentration_titles_incl_zeros"]["top20_share"],
                        "se": se20, "se_source": "(c) bootstrap on titles-incl-zeros vector",
                        "model_stat": "top20_capital_share"},
        "winner_skill_pct": {"value": p2["winner_skill_pct"],
                             "se": se_from_ci(*p2["winner_skill_pct_CI"]),
                             "se_source": "(a) 001 bootstrap CI", "model_stat": "winner_pct_emp"},
        "P_top_decile": {"value": p2["P_top_decile_cond"],
                         "se": se_from_ci(*p2["P_top_decile_cond_CI"]),
                         "se_source": "(a) 001 bootstrap CI", "model_stat": "P_winner_top_decile"},
        "y2y_persist": {"value": pm, "se": pse,
                        "se_source": "(b) bootstrap over 14 year-pair rhos",
                        "model_stat": "persist_y2y_top100"},
    }

    # ---------------- CHESS ----------------
    c = dj["chess"]
    crhos = [p["rho"] for p in c["persistence_top100"]["pairs"].values()]
    cm, cse = boot_pairs_se(crhos)
    targets["chess"] = {
        "y2y_persist": {"value": cm, "se": cse,
                        "se_source": "(b) bootstrap over 11 year-pair rhos",
                        "model_stat": "persist_y2y_top100"},
    }

    # ---------------- MOVIES ----------------
    mv = dj["movies"]
    vv = movies_votes_panel()
    m20, mse20 = boot_share_se(vv, 0.20)
    m01, mse01 = boot_share_se(vv, 0.01)
    assert abs(m20 - mv["S1_concentration"]["top20_share"]) < 1e-6, f"movies top20 mismatch {m20}"
    assert abs(m01 - mv["S1_concentration"]["top1_share"]) < 1e-6, f"movies top1 mismatch {m01}"
    s2 = mv["S2"]
    nmov = mv["panel"]["n"]
    targets["movies"] = {
        "top20_share": {"value": mv["S1_concentration"]["top20_share"], "se": mse20,
                        "se_source": "(c) bootstrap on numVotes vector", "model_stat": "top20_capital_share"},
        "top1_share": {"value": mv["S1_concentration"]["top1_share"], "se": mse01,
                       "se_source": "(c) bootstrap on numVotes vector", "model_stat": "top1_capital_share"},
        "winner_skill_pct": {"value": s2["winner_skill_pct"],
                             "se": se_from_ci(*s2["winner_skill_pct_CI"]),
                             "se_source": "(a) 001 bootstrap CI", "model_stat": "winner_pct_emp"},
        "P_top_decile": {"value": s2["P_top_decile_cond"],
                         "se": binom_prop_se(s2["P_top_decile_cond"], nmov),
                         "se_source": "(d) binomial-proportion SE sqrt(p(1-p)/k), k=decile size",
                         "model_stat": "P_winner_top_decile"},
    }

    # ---------------- BASEBALL (player) ----------------
    bb = dj["baseball"]
    sv = baseball_salary_vector()
    b20, bse20 = boot_share_se(sv, 0.20)
    b01, bse01 = boot_share_se(sv, 0.01)
    assert abs(b20 - bb["salary_concentration_1985_2016"]["top20_share"]) < 1e-6, f"bb top20 mismatch {b20}"
    assert abs(b01 - bb["salary_concentration_1985_2016"]["top1_share"]) < 1e-6, f"bb top1 mismatch {b01}"
    ev = bb["player_P2"]["exit_velocity"]
    ops_rhos = [p["rho"] for p in bb["player_OPS_persistence_LADDER"]["pairs"].values()]
    om, ose = boot_pairs_se(ops_rhos)
    targets["baseball"] = {
        "top20_share": {"value": bb["salary_concentration_1985_2016"]["top20_share"], "se": bse20,
                        "se_source": "(c) bootstrap on career-salary vector", "model_stat": "top20_capital_share"},
        "top1_share": {"value": bb["salary_concentration_1985_2016"]["top1_share"], "se": bse01,
                       "se_source": "(c) bootstrap on career-salary vector", "model_stat": "top1_capital_share"},
        "winner_skill_pct": {"value": ev["winner_skill_pct"],
                             "se": se_from_ci(*ev["winner_skill_pct_CI"]),
                             "se_source": "(a) 001 bootstrap CI (exit-velocity skill)", "model_stat": "winner_pct_emp"},
        "P_top_decile": {"value": ev["P_top_decile_cond"],
                         "se": binom_prop_se(ev["P_top_decile_cond"], ev["n"]),
                         "se_source": "(d) binomial-proportion SE sqrt(p(1-p)/k), k=decile size",
                         "model_stat": "P_winner_top_decile"},
        "OPS_persist": {"value": om, "se": ose,
                        "se_source": "(b) bootstrap over 23 OPS year-pair rhos",
                        "model_stat": "persist_y2y_top100"},
    }

    with open(os.path.join(OUT, "domain_targets.json"), "w") as f:
        json.dump(targets, f, indent=2)
    print(json.dumps({d: {k: {"value": round(v["value"], 4), "se": round(v["se"], 5)}
                          for k, v in sd.items()} for d, sd in targets.items()}, indent=2))


if __name__ == "__main__":
    main()
