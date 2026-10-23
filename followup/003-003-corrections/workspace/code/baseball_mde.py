"""001-3: baseball P2 power/MDE analysis.

Reconstructs the exact study-001 baseball P2 exit-velocity panel (reusing b3's
loaders verbatim) to reproduce winner_skill_pct=1.0 and its bootstrap CI, then
characterises the success panel and determines whether an MDE is computable or
ill-defined for this rank statistic. File written to 003's results/.
"""
import os, re, json, unicodedata
import numpy as np
import pandas as pd
from scipy.stats import spearmanr  # noqa: F401 (parity with b3 imports)

SHARED = "/workspace/eval/followup_staging/shared-data"
BB = os.path.join(SHARED, "baseball")
OUT = "/workspace/eval/followup/003-003-corrections/results"
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(2018)  # same seed as b3_baseball.py


def lah(t):
    import pyreadr
    return list(pyreadr.read_r(os.path.join(BB, "lahman_rda", f"{t}.RData")).values())[0]


def norm_name(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z ]", "", s.lower()).strip()
    return re.sub(r"\s+", " ", s)


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


def main():
    ev = load_statcast("exitvelo", "avg_hit_speed")
    sp = load_statcast("sprint", "sprint_speed")
    ev_career = ev.groupby(["player_id", "name_raw"]).agg(skill=("val", "mean"),
                                                          nssn=("val", "size")).reset_index()
    sp_career = sp.groupby("player_id").agg(sprint=("val", "mean")).reset_index()
    skill_df = ev_career.merge(sp_career, on="player_id", how="left")
    skill_df = skill_df[skill_df.nssn >= 3].copy()

    allstar = lah("AllstarFull")
    awards = lah("AwardsPlayers")
    asc = allstar[(allstar.yearID >= 2015) & (allstar.yearID <= 2025)].groupby("playerID").size()
    awc = awards[(awards.yearID >= 2015) & (awards.yearID <= 2025)].groupby("playerID").size()
    success = asc.add(awc, fill_value=0).rename("success")
    people = lah("People")

    def sc_key(raw):
        raw = str(raw)
        if "," in raw:
            last, first = raw.split(",", 1)
            return (norm_name(last) + " " + norm_name(first)).strip()
        return norm_name(raw)
    skill_df["mkey"] = skill_df.name_raw.map(sc_key)
    name2pid = {}
    for _, row in people.iterrows():
        k = (norm_name(row.nameLast) + " " + norm_name(row.nameFirst)).strip()
        name2pid.setdefault(k, []).append(row.playerID)

    def lookup(mkey):
        lst = name2pid.get(mkey, [])
        return lst[0] if lst else None
    skill_df["playerID"] = skill_df.mkey.map(lookup)
    matched = skill_df.dropna(subset=["playerID"]).copy()
    matched["success"] = matched.playerID.map(success).fillna(0)

    # ---- exit-velocity P2 panel, exactly as b3 ----
    df = pd.DataFrame({"skill": matched.set_index("playerID").skill,
                       "success": matched.set_index("playerID").success}).dropna()
    df["skill_pct"] = df.skill.rank(pct=True)
    n = len(df)
    win_pct = float(df.loc[df.success.idxmax()].skill_pct)
    top10 = df.nlargest(10, "success")
    top10_med = float(top10.skill_pct.median())

    # bootstrap (reproduce b3's CI)
    idx = df.index.to_numpy(); ws = []
    for _ in range(1000):
        s = df.loc[rng.choice(idx, len(idx), replace=True)].reset_index(drop=True)
        s["skill_pct"] = s.skill.rank(pct=True)
        ws.append(float(s.loc[s.success.idxmax()].skill_pct))
    ws = np.array(ws)
    ci = [float(np.percentile(ws, 2.5)), float(np.percentile(ws, 97.5))]
    boot_sd = float(ws.std(ddof=1))

    # ---- success-panel characterisation (the "n_success" the verdict leans on) ----
    succ = df.success.values
    vmax = succ.max()
    succ_sorted = np.sort(succ)[::-1]
    n_at_max = int((succ == vmax).sum())
    n_pos = int((succ > 0).sum())
    # distinct high-success players: how many players carry essentially all the
    # success mass that determines the "winner" order statistic
    top_counts = pd.Series(succ).value_counts().sort_index(ascending=False)
    # effective number of success "events" distinguishing the leaders
    n_distinct_top = int((succ >= max(1, vmax - 2)).sum())  # within 2 of the max

    # ---- MDE attempt (band decision boundary = 0.95) ----
    BOUND = 0.95
    # Gaussian one-sided detection distance from the boundary (alpha=.05, power=.80)
    z_a, z_b = 1.6448536269514722, 0.8416212335729143
    gaussian_mde = float((z_a + z_b) * boot_sd)
    # fraction of bootstrap resamples placing winner in each band
    frac_ge_bound = float((ws >= BOUND).mean())
    frac_model_band = float(((ws >= 0.55) & (ws < BOUND)).mean())
    frac_below_model = float((ws < 0.55).mean())
    # how piled at the ceiling is the bootstrap statistic?
    frac_at_ceiling = float((ws >= 0.999).mean())

    out = {
        "item": "001-3 baseball P2 power/MDE",
        "panel": {"n_players": int(n), "skill_measure": "avg_exit_velocity",
                  "success_measure": "All-Star selections + AwardsPlayers rows 2015-2025"},
        "reproduced": {"winner_skill_pct": win_pct, "winner_skill_pct_CI": ci,
                       "top10_median_skill_pct": top10_med,
                       "bootstrap_sd": boot_sd},
        "success_panel": {
            "max_success_count": float(vmax),
            "n_players_at_max": n_at_max,
            "n_players_within_2_of_max": n_distinct_top,
            "n_players_success_gt_0": n_pos,
            "top_success_counts_desc": [float(x) for x in succ_sorted[:12]],
        },
        "band_boundary": BOUND,
        "bootstrap_band_placement": {
            "frac_talent_dominated_ge_0.95": frac_ge_bound,
            "frac_model_band_0.55_0.95": frac_model_band,
            "frac_below_model_band": frac_below_model,
            "frac_at_ceiling_1.0": frac_at_ceiling,
        },
        "gaussian_mde_from_boundary_pctpts": gaussian_mde,
        "model_baseline_winner_pct": 0.696,
        "gap_baseline_to_boundary": round(BOUND - 0.696, 3),
    }
    with open(os.path.join(OUT, "baseball_mde.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
