"""B4 movies: IMDb. quality=averageRating (weakest proxy), success=numVotes.
S1 concentration + S2 (measurement-limited if validity row fails).
Validity: within each numVotes-decile Spearman(rating,votes); PASS iff median |rho|<=0.2."""
import os, json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, skew, kurtosis
from common import SHARED, RESULTS, done, write_json

IM = os.path.join(SHARED, "entertainment", "imdb")
rng = np.random.default_rng(2018)


def gini(x):
    x = np.sort(np.asarray(x, float)); n = len(x); cum = np.cumsum(x)
    return float((n + 1 - 2 * (cum / cum[-1]).sum()) / n)


def concentration(x):
    s = np.sort(np.asarray(x, float))[::-1]; tot = s.sum(); n = len(s)
    return {"top20_share": float(s[:max(1, int(.2 * n))].sum() / tot),
            "top1_share": float(s[:max(1, int(.01 * n))].sum() / tot),
            "gini": gini(x), "n": n}


def main():
    rat = pd.read_csv(os.path.join(IM, "title.ratings.tsv.gz"), sep="\t")
    bas = pd.read_csv(os.path.join(IM, "title.basics.tsv.gz"), sep="\t",
                      usecols=["tconst", "titleType", "primaryTitle"], dtype=str, low_memory=False)
    mov = bas[bas.titleType == "movie"].merge(rat, on="tconst")
    mov["numVotes"] = pd.to_numeric(mov.numVotes, errors="coerce")
    mov["averageRating"] = pd.to_numeric(mov.averageRating, errors="coerce")
    mov = mov[(mov.numVotes >= 1000) & mov.averageRating.notna()].copy()
    n = len(mov)

    # ---- validity: within-decile Spearman(rating, votes) ----
    mov["vdec"] = pd.qcut(mov.numVotes, 10, labels=False, duplicates="drop")
    decile_rows = []
    for d, g in mov.groupby("vdec"):
        rho = spearmanr(g.averageRating, g.numVotes).statistic
        decile_rows.append({"votes_decile": int(d), "n": int(len(g)),
                            "spearman_rating_votes": float(rho), "abs_rho": float(abs(rho))})
    med_abs = float(np.median([r["abs_rho"] for r in decile_rows]))
    bulk_sp = float(spearmanr(mov.averageRating, mov.numVotes).statistic)
    validity_pass = bool(med_abs <= 0.2)
    thr_sensitive = bool(abs(med_abs - 0.2) < 0.05)

    # ---- S1 concentration (success=numVotes) ----
    conc = concentration(mov.numVotes.values)
    quality_shape = {"skew": float(skew(mov.averageRating)),
                     "kurtosis_excess": float(kurtosis(mov.averageRating)),
                     "mean": float(mov.averageRating.mean()), "sd": float(mov.averageRating.std())}

    # ---- S2 (reported, labelled measurement-limited if validity fails) ----
    mov2 = mov.reset_index(drop=True)
    mov2["skill_pct"] = mov2.averageRating.rank(pct=True)
    win = mov2.loc[mov2.numVotes.idxmax()]
    top10 = mov2.nlargest(10, "numVotes")
    k = max(1, int(round(.1 * n)))
    ts = set(mov2.nlargest(k, "averageRating").index)
    tc = set(mov2.nlargest(k, "numVotes").index)
    # bootstrap winner pct
    idx = mov2.index.to_numpy(); ws = []
    for _ in range(1000):
        s = mov2.loc[rng.choice(idx, len(idx), replace=True)].reset_index(drop=True)
        s["skill_pct"] = s.averageRating.rank(pct=True)
        ws.append(s.loc[s.numVotes.idxmax()].skill_pct)
    p2 = {"n": n, "winner_skill_pct": float(win.skill_pct),
          "winner_skill_pct_CI": [float(np.percentile(ws, 2.5)), float(np.percentile(ws, 97.5))],
          "top10_median_skill_pct": float(top10.skill_pct.median()),
          "P_top_decile_cond": len(ts & tc) / len(ts),
          "top_success_title": str(win.primaryTitle),
          "verdict_label": "VALID" if validity_pass else "measurement-limited: no P2 verdict"}

    res = {"panel": {"filter": "titleType==movie & numVotes>=1000", "n": n,
                     "quality_proxy": "averageRating (declared weakest proxy)",
                     "success": "numVotes"},
           "G3_validity": {"within_decile_spearman": decile_rows, "median_abs_rho": med_abs,
                           "bulk_spearman_rating_votes": bulk_sp,
                           "PASS": validity_pass, "threshold_sensitive": thr_sensitive,
                           "rule": "PASS iff median within-decile |rho| <= 0.2 [SET AT 2b REVISION]",
                           "note_2b": "0.2 fixed before this statistic computed; only related preview was bulk Spearman(rating,votes)=0.205"},
           "S1_concentration": conc, "quality_distribution": quality_shape,
           "S2": p2, "model_ref_winner_pct": 0.696, "model_P_top_decile": 0.269}
    write_json(os.path.join(RESULTS, "domain_movies.json"), res)

    rows = [{"domain": "movies", "stat": "votes_decile_%d_spearman" % r["votes_decile"],
             "value": r["spearman_rating_votes"], "ci_lo": None, "ci_hi": None,
             "n": r["n"], "note": "validity"} for r in decile_rows]
    rows += [
        {"domain": "movies", "stat": "median_abs_rho_validity", "value": med_abs, "ci_lo": None, "ci_hi": None, "n": n, "note": "PASS<=0.2"},
        {"domain": "movies", "stat": "winner_skill_pct", "value": p2["winner_skill_pct"],
         "ci_lo": p2["winner_skill_pct_CI"][0], "ci_hi": p2["winner_skill_pct_CI"][1], "n": n, "note": p2["verdict_label"]},
        {"domain": "movies", "stat": "top10_median_skill_pct", "value": p2["top10_median_skill_pct"], "ci_lo": None, "ci_hi": None, "n": n, "note": ""},
        {"domain": "movies", "stat": "P_top_decile_cond", "value": p2["P_top_decile_cond"], "ci_lo": None, "ci_hi": None, "n": n, "note": ""},
        {"domain": "movies", "stat": "votes_top20_share", "value": conc["top20_share"], "ci_lo": None, "ci_hi": None, "n": n, "note": ""},
        {"domain": "movies", "stat": "votes_top1_share", "value": conc["top1_share"], "ci_lo": None, "ci_hi": None, "n": n, "note": ""},
    ]
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS, "domain_movies.csv"), index=False)
    print(json.dumps({"n": n, "median_abs_rho": med_abs, "bulk_spearman": bulk_sp,
                      "validity_PASS": validity_pass, "threshold_sensitive": thr_sensitive,
                      "winner_skill_pct": p2["winner_skill_pct"], "CI": p2["winner_skill_pct_CI"],
                      "top10_median": p2["top10_median_skill_pct"], "P_top_decile": p2["P_top_decile_cond"],
                      "top_success_title": p2["top_success_title"],
                      "votes_top20_share": conc["top20_share"], "votes_top1_share": conc["top1_share"],
                      "rating_kurtosis": quality_shape["kurtosis_excess"]}, indent=2))
    done("B4")


if __name__ == "__main__":
    main()
