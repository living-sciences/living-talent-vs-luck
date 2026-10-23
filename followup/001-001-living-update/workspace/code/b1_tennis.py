"""B1 tennis: the powered P2 domain. Also produces G3 tennis validity row
(split-half reliability + finals-excluded leakage control)."""
import os, json, glob
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from common import SHARED, RESULTS, done, write_json

TEN = os.path.join(SHARED, "tennis")
SEASONS = range(1991, 2026)  # 1991-2025 stats era, exclude 2026 partial
LEVELS = {"G", "M", "A", "F"}
rng = np.random.default_rng(2018)


def load_matches():
    dfs = []
    cols = ["tourney_level", "tourney_date", "round", "winner_id", "loser_id",
            "winner_name", "loser_name", "tourney_name", "best_of",
            "w_svpt", "w_1stWon", "w_2ndWon", "l_svpt", "l_1stWon", "l_2ndWon"]
    for yr in SEASONS:
        f = os.path.join(TEN, f"atp_matches_{yr}.csv")
        d = pd.read_csv(f, usecols=lambda c: c in cols, low_memory=False)
        d["season"] = yr
        dfs.append(d)
    m = pd.concat(dfs, ignore_index=True)
    m = m[m.tourney_level.isin(LEVELS)].copy()
    return m


def points_won(m):
    """winner/loser points won & played per match (point stats present)."""
    need = ["w_svpt", "w_1stWon", "w_2ndWon", "l_svpt", "l_1stWon", "l_2ndWon"]
    valid = m.dropna(subset=need).copy()
    for c in need:
        valid[c] = valid[c].astype(float)
    # winner points won = own service points won + return points won (loser svpt not won)
    valid["w_pw"] = (valid.w_1stWon + valid.w_2ndWon) + (valid.l_svpt - valid.l_1stWon - valid.l_2ndWon)
    valid["l_pw"] = (valid.l_1stWon + valid.l_2ndWon) + (valid.w_svpt - valid.w_1stWon - valid.w_2ndWon)
    valid["tot"] = valid.w_svpt + valid.l_svpt
    return valid


def skill_panel(valid, exclude_finals=False):
    """career point-share per player; returns Series indexed by player_id, and match count."""
    v = valid
    if exclude_finals:
        v = v[v["round"] != "F"]
    # stack winner and loser rows
    w = pd.DataFrame({"pid": v.winner_id, "pw": v.w_pw, "tot": v.tot})
    l = pd.DataFrame({"pid": v.loser_id, "pw": v.l_pw, "tot": v.tot})
    allp = pd.concat([w, l], ignore_index=True)
    g = allp.groupby("pid").agg(pw=("pw", "sum"), tot=("tot", "sum"), n=("pw", "size"))
    g["skill"] = g.pw / g.tot
    return g


def career_match_counts(valid):
    w = valid.groupby("winner_id").size()
    l = valid.groupby("loser_id").size()
    return w.add(l, fill_value=0)


def success_measures(m):
    """career titles (round=='F' wins), GS titles."""
    finals = m[m["round"] == "F"]
    titles = finals.groupby("winner_id").size().rename("titles")
    gs = finals[finals.tourney_level == "G"]
    gs_titles = gs.groupby("winner_id").size().rename("gs_titles")
    names = pd.concat([m[["winner_id", "winner_name"]].rename(columns={"winner_id": "pid", "winner_name": "name"}),
                       m[["loser_id", "loser_name"]].rename(columns={"loser_id": "pid", "loser_name": "name"})])
    name_map = names.dropna().groupby("pid").name.first()
    return titles, gs_titles, name_map


def p2_stats(skill, success):
    """skill, success: Series on same player index. Returns dict of P2 stats."""
    df = pd.DataFrame({"skill": skill, "success": success}).dropna()
    n = len(df)
    df["skill_pct"] = df.skill.rank(pct=True)
    df["succ_pct"] = df.success.rank(pct=True, method="average")
    # #1 success unit
    win = df.loc[df.success.idxmax()]
    winner_skill_pct = float(win.skill_pct)
    # top-10 success
    top10 = df.nlargest(10, "success")
    top10_median_skill_pct = float(top10.skill_pct.median())
    # decile overlap: P(top-success-decile | top-skill-decile)
    k = max(1, int(round(0.1 * n)))
    top_skill = set(df.nlargest(k, "skill").index)
    top_succ = set(df.nlargest(k, "success").index)
    cond = len(top_skill & top_succ) / len(top_skill)
    # also binary: is #1 success in top-skill decile
    win_in_top_skill_decile = float(df.success.idxmax() in top_skill)
    return dict(n=n, winner_skill_pct=winner_skill_pct,
                top10_median_skill_pct=top10_median_skill_pct,
                P_top_decile_cond=cond, win_in_top_skill_decile=win_in_top_skill_decile)


def bootstrap_p2(skill, success, B=1000):
    df = pd.DataFrame({"skill": skill, "success": success}).dropna()
    idx = df.index.to_numpy()
    ws, t10, pc = [], [], []
    for _ in range(B):
        samp = rng.choice(idx, size=len(idx), replace=True)
        d = df.loc[samp].reset_index(drop=True)
        d["skill_pct"] = d.skill.rank(pct=True)
        win = d.loc[d.success.idxmax()]
        ws.append(win.skill_pct)
        top10 = d.nlargest(10, "success")
        t10.append(top10.skill_pct.median())
        k = max(1, int(round(0.1 * len(d))))
        ts = set(d.nlargest(k, "skill").index); tc = set(d.nlargest(k, "success").index)
        pc.append(len(ts & tc) / len(ts))
    def ci(a):
        return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
    return {"winner_skill_pct_CI": ci(ws), "top10_median_skill_pct_CI": ci(t10),
            "P_top_decile_cond_CI": ci(pc)}


def concentration(success):
    s = np.sort(np.asarray(success, dtype=float))[::-1]
    tot = s.sum(); n = len(s)
    top20 = s[:max(1, int(0.2 * n))].sum() / tot
    top1 = s[:max(1, int(0.01 * n))].sum() / tot
    ss = np.sort(s)
    cum = np.cumsum(ss)
    gini = float((n + 1 - 2 * (cum / cum[-1]).sum()) / n)
    return {"top20_share": float(top20), "top1_share": float(top1), "gini": gini}


def persistence_series(name="points", start=2011, end=2025):
    """year-end top-100 points-rank consecutive-year Spearman."""
    rk = []
    for f in ["atp_rankings_90s.csv", "atp_rankings_00s.csv", "atp_rankings_10s.csv",
              "atp_rankings_20s.csv", "atp_rankings_current.csv"]:
        p = os.path.join(TEN, f)
        if os.path.exists(p):
            rk.append(pd.read_csv(p))
    r = pd.concat(rk, ignore_index=True)
    r["year"] = (r.ranking_date // 10000).astype(int)
    # last ranking date per year
    ye = r.loc[r.groupby("year").ranking_date.idxmax().values]
    last_dates = dict(zip(ye.year, ye.ranking_date))
    out = {}
    for y in range(start, end + 1):
        if y in last_dates:
            d = r[(r.ranking_date == last_dates[y])][["player", "points", "rank"]]
            d = d[d["rank"] <= 100].set_index("player")["points"]
            out[y] = d
    pairs = {}
    years = sorted(out.keys())
    rhos = []
    for a, b in zip(years[:-1], years[1:]):
        if b - a != 1:
            continue
        common = out[a].index.intersection(out[b].index)
        if len(common) >= 10:
            rho = spearmanr(out[a][common], out[b][common]).statistic
            pairs[f"{a}->{b}"] = {"rho": float(rho), "n": int(len(common))}
            rhos.append(rho)
    return {"pairs": pairs, "mean_rho": float(np.mean(rhos)), "n_pairs": len(rhos)}


def main():
    m = load_matches()
    valid = points_won(m)
    counts = career_match_counts(valid)  # matches with point stats
    # panel: players with >=200 matches having complete point stats
    panel_ids = counts[counts >= 200].index
    g_full = skill_panel(valid)
    g_fe = skill_panel(valid, exclude_finals=True)
    titles, gs_titles, name_map = success_measures(m)

    def restrict(g):
        return g.loc[g.index.intersection(panel_ids)]

    gf = restrict(g_full)
    skill = gf.skill
    succ = titles.reindex(skill.index).fillna(0)
    gs = gs_titles.reindex(skill.index).fillna(0)

    # --- primary P2 (titles) ---
    p2 = p2_stats(skill, succ)
    p2_ci = bootstrap_p2(skill, succ)
    # GS secondary
    p2_gs = p2_stats(skill, gs)

    # --- leakage control: finals-excluded skill ---
    gfe = g_fe.loc[g_fe.index.intersection(panel_ids)]
    # check top-10 success units still meet >=200 after finals-excluded (match count w/o finals)
    skill_fe = gfe.skill
    common_fe = skill_fe.index.intersection(succ.index)
    p2_fe = p2_stats(skill_fe.loc[common_fe], succ.loc[common_fe])

    # --- G3 validity: split-half reliability (odd vs even career matches) ---
    # assign each match an index per player; split odd/even by chronological order
    valid_sorted = valid.sort_values(["tourney_date"]).reset_index(drop=True)
    w = pd.DataFrame({"pid": valid_sorted.winner_id, "pw": valid_sorted.w_pw, "tot": valid_sorted.tot})
    l = pd.DataFrame({"pid": valid_sorted.loser_id, "pw": valid_sorted.l_pw, "tot": valid_sorted.tot})
    allp = pd.concat([w, l], ignore_index=True)
    allp["occ"] = allp.groupby("pid").cumcount()
    odd = allp[allp.occ % 2 == 1].groupby("pid").apply(lambda d: d.pw.sum() / d.tot.sum(), include_groups=False)
    even = allp[allp.occ % 2 == 0].groupby("pid").apply(lambda d: d.pw.sum() / d.tot.sum(), include_groups=False)
    sh = pd.DataFrame({"odd": odd, "even": even}).reindex(panel_ids).dropna()
    split_half_r = float(spearmanr(sh.odd, sh.even).statistic)
    split_half_pearson = float(np.corrcoef(sh.odd, sh.even)[0, 1])

    # --- persistence series ---
    pers_short = persistence_series(start=2011, end=2025)
    pers_long = persistence_series(start=1992, end=2025)

    # validity rule: PASS iff split-half r >= success persistence (y2y top-100 points-rank Spearman)
    success_persistence = pers_short["mean_rho"]
    validity_pass = bool(split_half_r >= success_persistence)

    # --- P1 shape ---
    conc_titles = concentration(succ[succ > 0]) if (succ > 0).any() else None
    conc_all = concentration(np.maximum(succ.values, 0) + 1e-9)  # include zeros via +eps? use raw
    conc_raw = concentration(succ.values + 0.0) if succ.sum() > 0 else None
    # skill distribution shape (thin-tailed check): skewness, kurtosis
    from scipy.stats import skew, kurtosis
    skill_shape = {"skew": float(skew(skill)), "kurtosis_excess": float(kurtosis(skill)),
                   "mean": float(skill.mean()), "sd": float(skill.std())}

    # leakage agreement: do primary and finals-excluded land in same cell?
    def cell(ws_pct):
        if ws_pct >= 0.95:
            return "absent_talent_dominated"
        elif 0.55 <= ws_pct <= 0.95:
            return "present_band"
        else:
            return "other"
    leakage_agree = bool(cell(p2["winner_skill_pct"]) == cell(p2_fe["winner_skill_pct"]))

    res = {
        "panel": {"seasons": "1991-2025", "levels": sorted(LEVELS),
                  "min_matches": 200, "n_players": int(len(skill)),
                  "n_matches_with_pointstats": int(len(valid))},
        "skill_proxy": "career point-share = sum(points won)/sum(points played)",
        "P2_primary_titles": {**p2, **p2_ci,
                              "model_ref_winner_pct": 0.696,
                              "paper_implied_winner_pct": 0.749,
                              "model_P_top_decile": 0.269},
        "P2_secondary_gs_titles": p2_gs,
        "P2_leakage_control_finals_excluded": {**p2_fe, "agree_with_primary_cell": leakage_agree},
        "G3_validity": {"split_half_spearman": split_half_r, "split_half_pearson": split_half_pearson,
                        "n": int(len(sh)), "success_persistence_y2y": success_persistence,
                        "PASS": validity_pass,
                        "rule": "PASS iff split-half r >= y2y top-100 points-rank Spearman (2011-2025)"},
        "P1_shape": {"concentration_titles_winners_only": conc_titles,
                     "concentration_titles_incl_zeros": conc_raw,
                     "skill_distribution": skill_shape},
        "persistence_2011_2025": pers_short,
        "persistence_1992_2025": pers_long,
    }
    write_json(os.path.join(RESULTS, "domain_tennis.json"), res)

    # CSV: one row per statistic
    rows = []
    def add(stat, val, ci=None, extra=""):
        rows.append({"domain": "tennis", "stat": stat, "value": val,
                     "ci_lo": ci[0] if ci else None, "ci_hi": ci[1] if ci else None,
                     "n": p2["n"], "note": extra})
    add("winner_skill_pct", p2["winner_skill_pct"], p2_ci["winner_skill_pct_CI"], "primary=titles")
    add("top10_median_skill_pct", p2["top10_median_skill_pct"], p2_ci["top10_median_skill_pct_CI"])
    add("P_top_decile_cond", p2["P_top_decile_cond"], p2_ci["P_top_decile_cond_CI"])
    add("winner_skill_pct_finals_excluded", p2_fe["winner_skill_pct"], None, "leakage control")
    add("split_half_reliability", split_half_r, None, "G3 validity")
    add("success_persistence_y2y", success_persistence, None, "2011-2025")
    add("top20_success_share", conc_raw["top20_share"] if conc_raw else None, None, "titles incl zeros")
    add("top1_success_share", conc_raw["top1_share"] if conc_raw else None, None)
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS, "domain_tennis.csv"), index=False)

    print(json.dumps({
        "n_players": res["panel"]["n_players"],
        "winner_skill_pct": p2["winner_skill_pct"], "CI": p2_ci["winner_skill_pct_CI"],
        "top10_median_skill_pct": p2["top10_median_skill_pct"],
        "P_top_decile_cond": p2["P_top_decile_cond"],
        "winner_skill_pct_finals_excluded": p2_fe["winner_skill_pct"],
        "leakage_agree": leakage_agree,
        "split_half_r": split_half_r, "success_persistence": success_persistence,
        "validity_PASS": validity_pass,
        "top20_share_titles": conc_raw["top20_share"] if conc_raw else None,
        "top1_share_titles": conc_raw["top1_share"] if conc_raw else None,
        "skill_kurtosis": skill_shape["kurtosis_excess"],
        "#1 success player": name_map.get(succ.idxmax(), "?"),
        "persistence_short_mean": pers_short["mean_rho"],
    }, indent=2, default=str))
    done("B1")


if __name__ == "__main__":
    main()
