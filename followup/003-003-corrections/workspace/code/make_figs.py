"""003 figures: (1) baseball winner-pct bootstrap vs the two bands (the MDE/power
finding, item 001-3); (2) tennis long persistence series with the declared NaN gap
and the two window means (item 001-4)."""
import os, re, json, unicodedata
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#D55E00",
             "#CC79A7", "#56B4E9", "#F0E442", "#000000"]
plt.rcParams.update({
    "figure.figsize": (7.5, 4.5), "figure.dpi": 150,
    "savefig.dpi": 150, "savefig.bbox": "tight",
    "font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25,
    "axes.prop_cycle": plt.cycler(color=OKABE_ITO),
})

SHARED = "/workspace/eval/followup_staging/shared-data"
BB = os.path.join(SHARED, "baseball")
OUT = "/workspace/eval/followup/003-003-corrections/results"
rng = np.random.default_rng(2018)


def norm_name(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z ]", "", s.lower()).strip()
    return re.sub(r"\s+", " ", s)


def lah(t):
    import pyreadr
    return list(pyreadr.read_r(os.path.join(BB, "lahman_rda", f"{t}.RData")).values())[0]


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


def baseball_bootstrap():
    ev = load_statcast("exitvelo", "avg_hit_speed")
    ev_career = ev.groupby(["player_id", "name_raw"]).agg(skill=("val", "mean"),
                                                          nssn=("val", "size")).reset_index()
    skill_df = ev_career[ev_career.nssn >= 3].copy()
    allstar = lah("AllstarFull"); awards = lah("AwardsPlayers")
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
    skill_df["playerID"] = skill_df.mkey.map(lambda m: (name2pid.get(m) or [None])[0])
    matched = skill_df.dropna(subset=["playerID"]).copy()
    matched["success"] = matched.playerID.map(success).fillna(0)
    df = pd.DataFrame({"skill": matched.set_index("playerID").skill,
                       "success": matched.set_index("playerID").success}).dropna()
    df["skill_pct"] = df.skill.rank(pct=True)
    win_pct = float(df.loc[df.success.idxmax()].skill_pct)
    idx = df.index.to_numpy(); ws = []
    for _ in range(1000):
        s = df.loc[rng.choice(idx, len(idx), replace=True)].reset_index(drop=True)
        s["skill_pct"] = s.skill.rank(pct=True)
        ws.append(float(s.loc[s.success.idxmax()].skill_pct))
    return np.array(ws), win_pct


def fig1_baseball():
    ws, win_pct = baseball_bootstrap()
    ci = (np.percentile(ws, 2.5), np.percentile(ws, 97.5))
    fig, ax = plt.subplots()
    # band shading
    ax.axvspan(0.55, 0.95, color=OKABE_ITO[0], alpha=0.12, label="model band [0.55, 0.95]")
    ax.axvspan(0.95, 1.001, color=OKABE_ITO[3], alpha=0.12, label="talent-dominated band (≥0.95)")
    ax.hist(ws, bins=np.linspace(0, 1, 41), color=OKABE_ITO[1], alpha=0.85,
            edgecolor="white", linewidth=0.3, label="winner-pct bootstrap (1000)")
    ax.axvline(0.696, color=OKABE_ITO[0], ls="--", lw=1.8, label="model baseline 0.696")
    ax.axvline(0.95, color="black", ls=":", lw=1.4, label="band boundary 0.95")
    ax.axvline(win_pct, color=OKABE_ITO[3], lw=2.0, label=f"point estimate {win_pct:.2f}")
    # MDE / CI annotation
    ax.annotate(f"95% CI [{ci[0]:.2f}, {ci[1]:.2f}] spans both bands\n→ uninformative; "
                f"MDE ≈ 0.33 > 0.25-pt gap",
                xy=(0.16, ax.get_ylim()[1]*0.45), fontsize=10.5,
                bbox=dict(boxstyle="round", fc="white", ec=OKABE_ITO[3], alpha=0.95))
    ax.set_xlabel("winner (top-success player) skill percentile")
    ax.set_ylabel("bootstrap resamples")
    ax.set_xlim(0, 1.02)
    ax.legend(fontsize=8.5, loc="upper left", framealpha=0.9)
    fig.savefig(os.path.join(OUT, "fig1_baseball_mde.png"), facecolor="white")
    plt.close(fig)
    print("fig1 done; CI", ci)


def fig2_tennis():
    j = json.load(open("/workspace/eval/followup/001-001-living-update/results/domain_tennis.json"))
    pairs = j["persistence_1992_2025"]["pairs"]
    years = []; rhos = []
    for k, v in pairs.items():
        y0 = int(k.split("->")[0]); years.append(y0); rhos.append(v["rho"])
    years = np.array(years); rhos = np.array(rhos)
    nan_mask = np.isnan(rhos)
    fig, ax = plt.subplots()
    # valid points
    ax.plot(years[~nan_mask], rhos[~nan_mask], "o-", color=OKABE_ITO[0], lw=1.5,
            ms=5, label="y2y Spearman (valid pairs)")
    # NaN gap marker band
    ax.axvspan(1991.5, 1996.0, color=OKABE_ITO[3], alpha=0.12,
               label="no point data (1992–1996): 4 NaN pairs excluded")
    nonnan_mean = float(np.nanmean(rhos))
    ax.axhline(nonnan_mean, color=OKABE_ITO[1], ls="--", lw=2.0,
               label=f"1992–2025 non-NaN mean {nonnan_mean:.3f} (29 pairs)")
    ax.axhline(j["persistence_2011_2025"]["mean_rho"], color=OKABE_ITO[2], ls=":", lw=2.0,
               label=f"2011–2025 mean {j['persistence_2011_2025']['mean_rho']:.3f} (headline)")
    ax.set_xlabel("season (start of year-pair)")
    ax.set_ylabel("top-100 points-rank y2y Spearman ρ")
    ax.set_ylim(0, 1)
    ax.legend(fontsize=9, loc="lower right", framealpha=0.9)
    fig.savefig(os.path.join(OUT, "fig2_tennis_long_persistence.png"), facecolor="white")
    plt.close(fig)
    print("fig2 done; non-NaN mean", nonnan_mean)


if __name__ == "__main__":
    fig1_baseball()
    fig2_tennis()
