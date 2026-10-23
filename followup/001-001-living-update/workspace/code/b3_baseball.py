"""B3 baseball: team series (secondary), player P2 (Statcast skill vs success),
salary-era concentration, player OPS persistence (P3 LADDER ENTRY), G3 validity row."""
import os, re, json, unicodedata
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from common import SHARED, RESULTS, done, write_json

BB = os.path.join(SHARED, "baseball")
rng = np.random.default_rng(2018)


def lah(t):
    import pyreadr
    return list(pyreadr.read_r(os.path.join(BB, "lahman_rda", f"{t}.RData")).values())[0]


def norm_name(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z ]", "", s.lower()).strip()
    return re.sub(r"\s+", " ", s)


def gini(x):
    x = np.sort(np.asarray(x, float)); n = len(x); cum = np.cumsum(x)
    return float((n + 1 - 2 * (cum / cum[-1]).sum()) / n)


def concentration(x):
    s = np.sort(np.asarray(x, float))[::-1]; tot = s.sum(); n = len(s)
    return {"top20_share": float(s[:max(1, int(.2 * n))].sum() / tot),
            "top1_share": float(s[:max(1, int(.01 * n))].sum() / tot),
            "gini": gini(x), "n": n}


def main():
    res = {}

    # ---- Team series: y2y win% correlation 1961-2025 + Mauboussin luck share ----
    teams = lah("Teams")
    t = teams[(teams.yearID >= 1961) & (teams.yearID <= 2025)].copy()
    t["winpct"] = t.W / (t.W + t.L)
    piv = t.pivot_table(index="franchID", columns="yearID", values="winpct")
    yrs = sorted(t.yearID.unique())
    y2y = []
    for a, b in zip(yrs[:-1], yrs[1:]):
        if a in piv.columns and b in piv.columns:
            d = piv[[a, b]].dropna()
            if len(d) >= 10:
                y2y.append(spearmanr(d[a], d[b]).statistic)
    # Mauboussin season luck share averaged 2015-2025
    mboss = []
    for y in range(2015, 2026):
        wp = t[t.yearID == y]["winpct"]
        if len(wp) > 1:
            mboss.append((0.25 / 162) / wp.var(ddof=1))
    res["team_series"] = {"winpct_y2y_mean_spearman": float(np.mean(y2y)),
                          "n_pairs": len(y2y),
                          "mauboussin_luck_share_2015_2025_mean": float(np.mean(mboss)),
                          "note": "reported SECONDARY, not the P3 ladder entry"}

    # ---- Player OPS persistence (P3 ladder entry) ----
    bat = lah("Batting")
    b = bat[(bat.yearID >= 2000) & (bat.yearID <= 2025)].copy()
    for c in ["AB", "H", "X2B", "X3B", "HR", "BB", "HBP", "SF", "SH", "IBB"]:
        b[c] = pd.to_numeric(b[c], errors="coerce").fillna(0)
    agg = b.groupby(["playerID", "yearID"]).agg(
        AB=("AB", "sum"), H=("H", "sum"), X2B=("X2B", "sum"), X3B=("X3B", "sum"),
        HR=("HR", "sum"), BB=("BB", "sum"), HBP=("HBP", "sum"), SF=("SF", "sum"),
        SH=("SH", "sum")).reset_index()
    agg["PA"] = agg.AB + agg.BB + agg.HBP + agg.SF + agg.SH
    agg["X1B"] = agg.H - agg.X2B - agg.X3B - agg.HR
    agg["TB"] = agg.X1B + 2 * agg.X2B + 3 * agg.X3B + 4 * agg.HR
    denom_obp = (agg.AB + agg.BB + agg.HBP + agg.SF).replace(0, np.nan)
    agg["OBP"] = (agg.H + agg.BB + agg.HBP) / denom_obp
    agg["SLG"] = agg.TB / agg.AB.replace(0, np.nan)
    agg["OPS"] = agg.OBP + agg.SLG
    q = agg[(agg.PA >= 300) & agg.OPS.notna()]
    opiv = q.pivot_table(index="playerID", columns="yearID", values="OPS")
    ops_pairs = {}
    ops_rhos = []
    for a, bb in zip(range(2000, 2025), range(2001, 2026)):
        if a in opiv.columns and bb in opiv.columns:
            d = opiv[[a, bb]].dropna()
            if len(d) >= 20:
                r = spearmanr(d[a], d[bb]).statistic
                ops_pairs[f"{a}->{bb}"] = {"rho": float(r), "n": int(len(d))}
                ops_rhos.append(r)
    ops_persistence = float(np.mean(ops_rhos))
    res["player_OPS_persistence_LADDER"] = {"mean_spearman": ops_persistence,
                                            "n_pairs": len(ops_rhos), "pairs": ops_pairs}

    # ---- Statcast skill panels + G3 validity (y2y reliability) ----
    def load_statcast(kind, col):
        frames = []
        for y in range(2015, 2027):
            f = os.path.join(BB, "statcast", f"{kind}_{y}.csv")
            d = pd.read_csv(f)
            d.columns = [c.strip().strip('"').replace("﻿", "") for c in d.columns]
            namecol = [c for c in d.columns if "last_name" in c][0]
            d = d.rename(columns={namecol: "name_raw", col: "val"})
            d = d[["player_id", "name_raw", "val"]].copy()
            d["year"] = y
            frames.append(d)
        return pd.concat(frames, ignore_index=True)

    ev = load_statcast("exitvelo", "avg_hit_speed")
    sp = load_statcast("sprint", "sprint_speed")

    def y2y_reliability(df):
        piv = df.pivot_table(index="player_id", columns="year", values="val")
        rr = []
        for a, b in zip(range(2015, 2026), range(2016, 2027)):
            if a in piv.columns and b in piv.columns:
                d = piv[[a, b]].dropna()
                if len(d) >= 20:
                    rr.append(spearmanr(d[a], d[b]).statistic)
        return float(np.mean(rr)), len(rr)

    ev_rel, ev_np = y2y_reliability(ev)
    sp_rel, sp_np = y2y_reliability(sp)
    validity_pass = bool((ev_rel >= ops_persistence) and (sp_rel >= ops_persistence))
    res["G3_validity"] = {"exitvelo_y2y_spearman": ev_rel, "sprint_y2y_spearman": sp_rel,
                          "n_pairs_ev": ev_np, "n_pairs_sp": sp_np,
                          "success_persistence_OPS": ops_persistence,
                          "PASS": validity_pass,
                          "rule": "PASS iff both exitvelo & sprint y2y r >= OPS y2y Spearman"}

    # ---- Player P2: career-avg skill vs success (All-Star + awards 2015-2025) ----
    ev_career = ev.groupby(["player_id", "name_raw"]).agg(skill=("val", "mean"),
                                                          nssn=("val", "size")).reset_index()
    sp_career = sp.groupby("player_id").agg(sprint=("val", "mean")).reset_index()
    skill_df = ev_career.merge(sp_career, on="player_id", how="left")
    skill_df = skill_df[skill_df.nssn >= 3].copy()  # >=3 Statcast seasons
    skill_df["nkey"] = skill_df.name_raw.map(norm_name)

    # success: All-Star + awards counts 2015-2025 per Lahman playerID
    allstar = lah("AllstarFull")
    awards = lah("AwardsPlayers")
    asc = allstar[(allstar.yearID >= 2015) & (allstar.yearID <= 2025)].groupby("playerID").size()
    awc = awards[(awards.yearID >= 2015) & (awards.yearID <= 2025)].groupby("playerID").size()
    success = asc.add(awc, fill_value=0).rename("success")
    people = lah("People")
    people["nkey"] = (people.nameLast.map(norm_name) + " " + people.nameFirst.map(norm_name)).map(lambda s: s.strip())
    # statcast "Last, First" -> normalized "last first"
    def sc_key(raw):
        raw = str(raw)
        if "," in raw:
            last, first = raw.split(",", 1)
            return (norm_name(last) + " " + norm_name(first)).strip()
        return norm_name(raw)
    skill_df["mkey"] = skill_df.name_raw.map(sc_key)
    pmap = people.set_index("playerID")
    name2pid = {}
    for pid, row in people.iterrows():
        k = (norm_name(row.nameLast) + " " + norm_name(row.nameFirst)).strip()
        name2pid.setdefault(k, []).append(row.playerID)
    def lookup(mkey):
        lst = name2pid.get(mkey, [])
        return lst[0] if len(lst) == 1 else (lst[0] if lst else None)
    skill_df["playerID"] = skill_df.mkey.map(lookup)
    matched = skill_df.dropna(subset=["playerID"]).copy()
    matched["success"] = matched.playerID.map(success).fillna(0)
    match_rate = float(len(matched) / len(skill_df))

    def p2_from(skill_series, succ_series, label):
        df = pd.DataFrame({"skill": skill_series, "success": succ_series}).dropna()
        df["skill_pct"] = df.skill.rank(pct=True)
        win = df.loc[df.success.idxmax()]
        top10 = df.nlargest(10, "success")
        n = len(df); k = max(1, int(round(.1 * n)))
        ts = set(df.nlargest(k, "skill").index); tc = set(df.nlargest(k, "success").index)
        # bootstrap
        idx = df.index.to_numpy(); ws = []
        for _ in range(1000):
            s = df.loc[rng.choice(idx, len(idx), replace=True)].reset_index(drop=True)
            s["skill_pct"] = s.skill.rank(pct=True)
            ws.append(s.loc[s.success.idxmax()].skill_pct)
        return {"skill_measure": label, "n": n,
                "winner_skill_pct": float(win.skill_pct),
                "winner_skill_pct_CI": [float(np.percentile(ws, 2.5)), float(np.percentile(ws, 97.5))],
                "top10_median_skill_pct": float(top10.skill_pct.median()),
                "P_top_decile_cond": len(ts & tc) / len(ts)}

    matched_ev = matched.set_index("playerID")
    p2_ev = p2_from(matched_ev.skill, matched_ev.success, "avg_exit_velocity")
    p2_sp = p2_from(matched_ev.sprint, matched_ev.success, "sprint_speed")
    res["player_P2"] = {"match_rate_statcast_to_lahman": match_rate,
                        "n_skill_panel": int(len(skill_df)),
                        "exit_velocity": p2_ev, "sprint_speed": p2_sp,
                        "success_measure": "All-Star selections + AwardsPlayers rows 2015-2025",
                        "model_ref_winner_pct": 0.696, "model_P_top_decile": 0.269}

    # ---- Salary-era concentration 1985-2016, players >=5 salary years ----
    sal = lah("Salaries")
    sc = sal.groupby("playerID").agg(tot=("salary", "sum"), nyr=("yearID", "nunique"))
    sc5 = sc[sc.nyr >= 5]
    res["salary_concentration_1985_2016"] = concentration(sc5.tot.values)
    res["salary_concentration_1985_2016"]["note"] = "career summed salary, players >=5 salary years"

    write_json(os.path.join(RESULTS, "domain_baseball.json"), res)
    rows = [
        {"domain": "baseball", "stat": "OPS_persistence_y2y", "value": ops_persistence,
         "ci_lo": None, "ci_hi": None, "n": len(ops_rhos), "note": "P3 LADDER ENTRY 2000-2025"},
        {"domain": "baseball", "stat": "team_winpct_y2y", "value": res["team_series"]["winpct_y2y_mean_spearman"],
         "ci_lo": None, "ci_hi": None, "n": res["team_series"]["n_pairs"], "note": "secondary"},
        {"domain": "baseball", "stat": "winner_skill_pct_exitvelo", "value": p2_ev["winner_skill_pct"],
         "ci_lo": p2_ev["winner_skill_pct_CI"][0], "ci_hi": p2_ev["winner_skill_pct_CI"][1], "n": p2_ev["n"], "note": "success=AS+awards"},
        {"domain": "baseball", "stat": "winner_skill_pct_sprint", "value": p2_sp["winner_skill_pct"],
         "ci_lo": p2_sp["winner_skill_pct_CI"][0], "ci_hi": p2_sp["winner_skill_pct_CI"][1], "n": p2_sp["n"], "note": ""},
        {"domain": "baseball", "stat": "salary_top20_share", "value": res["salary_concentration_1985_2016"]["top20_share"],
         "ci_lo": None, "ci_hi": None, "n": res["salary_concentration_1985_2016"]["n"], "note": "1985-2016"},
    ]
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS, "domain_baseball.csv"), index=False)
    print(json.dumps({"OPS_persistence_LADDER": ops_persistence,
                      "team_winpct_y2y": res["team_series"]["winpct_y2y_mean_spearman"],
                      "mauboussin_luck_share": res["team_series"]["mauboussin_luck_share_2015_2025_mean"],
                      "exitvelo_y2y_rel": ev_rel, "sprint_y2y_rel": sp_rel,
                      "validity_PASS": validity_pass,
                      "p2_exitvelo_winner_pct": p2_ev["winner_skill_pct"], "CI": p2_ev["winner_skill_pct_CI"],
                      "p2_exitvelo_top10_med": p2_ev["top10_median_skill_pct"],
                      "p2_exitvelo_P_top_decile": p2_ev["P_top_decile_cond"],
                      "p2_sprint_winner_pct": p2_sp["winner_skill_pct"],
                      "match_rate": match_rate, "n_skill_panel": len(skill_df),
                      "salary_top20": res["salary_concentration_1985_2016"]["top20_share"],
                      "salary_gini": res["salary_concentration_1985_2016"]["gini"]}, indent=2))
    done("B3")


if __name__ == "__main__":
    main()
