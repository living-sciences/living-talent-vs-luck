#!/usr/bin/env python3
"""Figures for study 002: fit map, funding frontier, structural-gap summary."""
import os, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = "/workspace/eval/followup/002-002-theory-update/results"
OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"]
plt.rcParams.update({
    "figure.figsize": (7.5, 4.5), "figure.dpi": 150, "savefig.dpi": 150, "savefig.bbox": "tight",
    "font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "axes.prop_cycle": plt.cycler(color=OKABE_ITO),
})

grid = pd.read_csv(os.path.join(OUT, "calibration_grid.csv"))
fits = json.load(open(os.path.join(OUT, "domain_fits.json")))
fund = pd.read_csv(os.path.join(OUT, "funding_comparison.csv"))
targets = json.load(open(os.path.join(OUT, "domain_targets.json")))

DOM_COLOR = {"tennis": "#0072B2", "movies": "#E69F00", "chess": "#009E73", "baseball": "#D55E00"}

# ---------- Fig 1: fit map (alpha x p_L plane) ----------
fig, ax = plt.subplots(figsize=(8, 5.2))
# Zappala tennis a=0.20-0.30 band (vertical span on the alpha axis)
ax.axvspan(0.20, 0.30, color="#E69F00", alpha=0.18, zorder=0)
ax.text(0.25, 46, "Zappalà 2023\ntennis a=0.20–0.30\n(per-point weight;\ndifferent construct)",
        color="#9a6a00", fontsize=8, ha="center", va="center")
markers = {"tennis": "o", "movies": "s", "chess": "^", "baseball": "D"}
# small horizontal offsets so coincident markers (tennis & movies at 1.0,65) both show
offset = {"tennis": -0.018, "movies": 0.018, "chess": 0.0, "baseball": 0.0}
for dom, f in fits.items():
    a0, p0 = f["fitted_alpha"], f["fitted_pL"]
    neigh = np.array(f["neighbourhood_1SE"]) if f["neighbourhood_1SE"] else np.array([[a0, p0]])
    amin, amax = neigh[:, 0].min(), neigh[:, 0].max()
    pmin, pmax = neigh[:, 1].min(), neigh[:, 1].max()
    whole_grid = (len(neigh) >= 50)
    ax.add_patch(Rectangle((amin - 0.015, pmin - 2), (amax - amin) + 0.03, (pmax - pmin) + 4,
                           facecolor="none", edgecolor=DOM_COLOR[dom],
                           lw=1.2, ls="--", alpha=0.55, zorder=1))
    lab = f"{dom} (α={a0}, p_L={p0}) — fit FAILS" + ("  [1-SE nbhd = whole grid]" if whole_grid else "")
    ax.scatter([a0 + offset[dom]], [p0], s=150, marker=markers[dom], color=DOM_COLOR[dom],
               edgecolor="black", lw=0.9, zorder=3, label=lab)
ax.set_xlabel("talent-leverage dial  α   (0 = pure luck, 1 = paper's TvL model)")
ax.set_ylabel("lucky-event density  p_L  (%)")
ax.set_xlim(-0.06, 1.08); ax.set_ylim(12, 88)
ax.set_xticks([round(0.1 * i, 1) for i in range(11)]); ax.set_yticks([20, 35, 50, 65, 80])
ax.legend(loc="upper left", fontsize=8.3, framealpha=0.92)
ax.set_title("T1 fit map: nearest grid cell per domain — every joint 3-SE fit FAILS", pad=12)
fig.savefig(os.path.join(OUT, "fig_fit_map.png"), facecolor="white"); plt.close(fig)

# ---------- Fig 2: funding frontier ----------
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.plot(fund.alpha, fund.egal_E, "-o", color="#0072B2", label="egalitarian (ALL EQUAL 1u) — efficiency E")
ax.plot(fund.alpha, fund.elit_E, "-s", color="#D55E00", label="elitarian (25% BEST 10u) — efficiency E")
ax.fill_between(fund.alpha, fund.elit_E, fund.egal_E, color="#0072B2", alpha=0.08)
ax.set_xlabel("talent-leverage dial  α")
ax.set_ylabel("funding efficiency  E = ΔP_T / F_T")
ax.set_title("T3 funding frontier: egalitarian beats elitarian at EVERY α (no flip in [0,1])")
ax.set_xticks([round(0.1 * i, 1) for i in range(11)])
# annotate fitted career alphas
for dom in ("tennis", "movies"):
    ax.axvline(fits[dom]["fitted_alpha"], color="#009E73", ls=":", lw=1, alpha=0.6)
ax.text(1.0, fund.egal_E.iloc[-1], "  fitted tennis & movies α=1.0", color="#007a59",
        fontsize=8, va="bottom", ha="right", rotation=90)
ax.legend(loc="center right", fontsize=9)
ax.set_ylim(0, fund.egal_E.max() * 1.15)
fig.savefig(os.path.join(OUT, "fig_funding_frontier.png"), facecolor="white"); plt.close(fig)

# ---------- Fig 3: structural gap on the two breaking statistics ----------
fig, axes = plt.subplots(1, 2, figsize=(10, 4.6))
# (a) winner-skill percentile: model reachable range vs domain targets
mn, mx = grid.winner_pct_emp.min(), grid.winner_pct_emp.max()
ax = axes[0]
ax.axhspan(mn, mx, color="#0072B2", alpha=0.18, zorder=0)
ax.text(0.5, (mn + mx) / 2, f"model reachable\n[{mn:.2f}, {mx:.2f}]\n(all α, all p_L)",
        color="#004c77", ha="center", va="center", fontsize=9)
doms = ["tennis", "movies", "baseball"]
xs = [1, 2, 3]
for x, d in zip(xs, doms):
    t = targets[d]["winner_skill_pct"]
    ax.errorbar([x], [t["value"]], yerr=[[2 * t["se"]], [2 * t["se"]]], fmt="o",
                color=DOM_COLOR[d], ms=9, capsize=4, lw=1.5)
ax.set_xticks([0.5] + xs); ax.set_xticklabels(["model", "tennis", "movies", "baseball"])
ax.set_xlim(0, 3.6); ax.set_ylim(0.4, 1.03)
ax.set_ylabel("winner skill percentile"); ax.set_title("(a) top success ≠ top skill?")
# (b) persistence
mnp, mxp = grid.persist_y2y_top100.min(), grid.persist_y2y_top100.max()
ax = axes[1]
ax.axhspan(mnp, mxp, color="#0072B2", alpha=0.18, zorder=0)
ax.text(0.5, 0.90, f"model reachable\n[{mnp:.2f}, {mxp:.2f}]", color="#004c77",
        ha="center", va="center", fontsize=9)
pers = {"chess": targets["chess"]["y2y_persist"], "tennis": targets["tennis"]["y2y_persist"],
        "baseball": targets["baseball"]["OPS_persist"]}
for x, d in zip([1, 2, 3], ["chess", "tennis", "baseball"]):
    t = pers[d]
    ax.errorbar([x], [t["value"]], yerr=[[2 * t["se"]], [2 * t["se"]]], fmt="o",
                color=DOM_COLOR[d], ms=9, capsize=4, lw=1.5)
ax.set_xticks([0.5, 1, 2, 3]); ax.set_xticklabels(["model", "chess", "tennis", "baseball"])
ax.set_xlim(0, 3.6); ax.set_ylim(0.4, 1.0)
ax.set_ylabel("year-over-year persistence (Spearman)"); ax.set_title("(b) elite persistence")
fig.suptitle("Two structural failures: the model's winner is too mediocre and its ranks too sticky",
             fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig_structural_gap.png"), facecolor="white"); plt.close(fig)

print("wrote fig_fit_map.png, fig_funding_frontier.png, fig_structural_gap.png")
print("winner_pct model range:", round(mn, 3), round(mx, 3))
print("persist model range:", round(mnp, 3), round(mxp, 3))
