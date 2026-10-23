#!/usr/bin/env python3
"""Step 3: post-process the authors' single NetLogo run (no re-simulation).

Reads agents_timeseries.csv (columns: time,who,talent,success,n-lucky-events,
n-unlucky-events) and computes the scalars and figures of paper sections 2.1
(Figs 3-6). Capital/success is geometric: C = 10 * 2^(doublings - halvings), so
the natural histogram bins are the discrete values themselves (log/geometric).
"""
import argparse, json, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def powerlaw_slope(capital, cmin=10.0):
    """Slope of the final-capital tail from a log-binned (discrete geometric)
    histogram: regress log10(pdf) on log10(C) for C >= cmin."""
    vals, counts = np.unique(capital, return_counts=True)
    pdf = counts / counts.sum()
    mask = (vals >= cmin) & (counts > 0)
    x = np.log10(vals[mask])
    y = np.log10(pdf[mask])
    if len(x) < 2:
        return float("nan"), x, y
    slope, intercept = np.polyfit(x, y, 1)
    return float(slope), x, y, slope, intercept


def expfit(counts_per_agent, maxbin=None):
    """Fit y = A exp(-b x) to the histogram of an integer event-count series,
    via linear regression of ln(count) on x over non-empty bins."""
    if maxbin is None:
        maxbin = int(counts_per_agent.max())
    x = np.arange(0, maxbin + 1)
    hist = np.array([(counts_per_agent == k).sum() for k in x], dtype=float)
    nz = hist > 0
    xf, yf = x[nz], np.log(hist[nz])
    b_slope, lnA = np.polyfit(xf, yf, 1)
    A = float(np.exp(lnA))
    b = float(-b_slope)
    return A, b, x, hist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeseries", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    df = pd.read_csv(args.timeseries)
    df = df.rename(columns={"n-lucky-events": "nlucky", "n-unlucky-events": "nunlucky"})
    tmax = df.time.max()
    final = df[df.time == tmax].sort_values("who").reset_index(drop=True)
    N = len(final)
    C = final.success.values
    T = final.talent.values
    total = C.sum()

    m = {}
    # (a) power-law slope of tail
    slope, xpl, ypl, s2, icept = powerlaw_slope(C, cmin=10.0)
    m["powerlaw_slope"] = slope
    # (b)
    m["n_above_500"] = int((C > 500).sum())
    # (c) share of top 20 richest
    order = np.argsort(C)[::-1]
    m["top20_capital_share"] = float(C[order[:20]].sum() / total)
    # (d)
    m["frac_below_10"] = float((C < 10).mean())
    # (e) Pareto bottom80 / top20
    sorted_asc = np.sort(C)
    k80 = int(np.floor(0.8 * N))
    m["bottom80_share"] = float(sorted_asc[:k80].sum() / total)
    m["top20_share"] = float(sorted_asc[k80:].sum() / total)
    # (f) C_max/T_max
    imax = int(np.argmax(C))
    imaxT = int(np.argmax(T))
    m["C_max"] = float(C[imax]); m["talent_at_C_max"] = float(T[imax])
    m["T_max"] = float(T[imaxT]); m["capital_at_T_max"] = float(C[imaxT])
    # (g) T* = talent of most successful; avg capital of talent>T*
    Tstar = float(T[imax])
    m["T_star"] = Tstar
    mask_gt = T > Tstar
    avg_gt = float(C[mask_gt].mean()) if mask_gt.any() else float("nan")
    m["avg_capital_talent_gt_Tstar"] = avg_gt
    m["ratio_Cmax_over_avg"] = float(C[imax] / avg_gt) if avg_gt == avg_gt and avg_gt > 0 else float("nan")
    # (h) exponential fits
    lA, lb, lx, lh = expfit(final.nlucky)
    uA, ub, ux, uh = expfit(final.nunlucky)
    m["lucky_fit_A"] = lA; m["lucky_fit_b"] = lb
    m["unlucky_fit_A"] = uA; m["unlucky_fit_b"] = ub
    # (i)
    m["mean_lucky"] = float(final.nlucky.mean()); m["mean_unlucky"] = float(final.nunlucky.mean())
    # (j)
    m["max_lucky"] = int(final.nlucky.max()); m["max_unlucky"] = int(final.nunlucky.max())
    # (k)
    neutral = (final.nlucky == 0) & (final.nunlucky == 0)
    one_type = ((final.nlucky > 0) & (final.nunlucky == 0)) | ((final.nlucky == 0) & (final.nunlucky > 0))
    m["frac_neutral"] = float(neutral.mean())
    m["frac_one_type"] = float(one_type.mean())
    # (l) trajectories of final-max and final-min agents
    who_max = int(final.loc[imax, "who"]); who_min = int(final.loc[int(np.argmin(C)), "who"])
    traj_max = df[df.who == who_max].sort_values("time")
    traj_min = df[df.who == who_min].sort_values("time")
    cmax_series = traj_max.success.values.tolist()
    cmin_series = traj_min.success.values.tolist()
    # last-10-step rise of max agent: C at t=tmax-10 -> t=tmax
    c_at_70 = float(traj_max[traj_max.time == tmax - 10].success.values[0])
    c_at_80 = float(traj_max[traj_max.time == tmax].success.values[0])
    m["max_agent_traj_last10"] = {"t_start": tmax - 10, "C_start": c_at_70,
                                  "t_end": int(tmax), "C_end": c_at_80,
                                  "series_last10": traj_max[traj_max.time >= tmax - 10].success.values.tolist()}
    m["max_agent_who"] = who_max; m["min_agent_who"] = who_min
    m["max_agent_talent"] = float(traj_max.talent.iloc[0])
    # (m) least successful
    imin = int(np.argmin(C))
    m["min_agent_final_capital"] = float(C[imin]); m["min_agent_talent"] = float(T[imin])

    def _np(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(str(type(o)))
    with open(os.path.join(args.out, "single_run_metrics.json"), "w") as f:
        json.dump(m, f, indent=2, default=_np)
    print(json.dumps(m, indent=2, default=_np))

    # ---------------- Figures ----------------
    # Fig 3: log-lin (a) and log-log (b) of final capital distribution
    vals, counts = np.unique(C, return_counts=True)
    pdf = counts / counts.sum()
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    # log-lin: x linear capital, y log count  (paper panel a uses log-lin: y log)
    ax[0].bar(np.log10(vals), counts, width=0.08, color="#4C72B0")
    ax[0].set_xlabel("log10(capital/success)"); ax[0].set_ylabel("# individuals")
    ax[0].set_yscale("log"); ax[0].set_title("(a) distribution (log-lin)")
    # log-log with fitted slope
    ax[1].scatter(np.log10(vals), np.log10(pdf), s=18, color="#4C72B0", label="data")
    xx = np.linspace(xpl.min(), xpl.max(), 50)
    ax[1].plot(xx, icept + slope * xx, "r-", label=f"slope={slope:.2f}")
    ax[1].set_xlabel("log10(capital/success)"); ax[1].set_ylabel("log10(pdf)")
    ax[1].set_title("(b) distribution (log-log) + power-law fit"); ax[1].legend()
    fig.tight_layout(); fig.savefig(os.path.join(args.out, "fig3_distribution.pdf")); plt.close(fig)

    # Fig 4: (a) talent vs log(capital); (b) capital vs talent
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ax[0].scatter(np.log10(C), T, s=10, alpha=0.5, color="#55A868")
    ax[0].axhline(T.mean(), color="k", ls="--", lw=0.8)
    ax[0].set_xlabel("log10(capital/success)"); ax[0].set_ylabel("talent"); ax[0].set_title("(a) talent vs capital")
    ax[1].scatter(T, C, s=10, alpha=0.5, color="#55A868")
    ax[1].axvline(T.mean(), color="k", ls="--", lw=0.8)
    ax[1].set_yscale("log"); ax[1].set_xlabel("talent"); ax[1].set_ylabel("capital/success")
    ax[1].set_title("(b) capital vs talent")
    fig.tight_layout(); fig.savefig(os.path.join(args.out, "fig4_talent_vs_capital.pdf")); plt.close(fig)

    # Fig 5: (a) lucky vs success, (b) unlucky vs success, (c) lucky hist log-lin, (d) unlucky hist log-lin
    fig, ax = plt.subplots(2, 2, figsize=(11, 8))
    ax[0, 0].scatter(C, final.nlucky, s=10, alpha=0.5, color="#4C72B0")
    ax[0, 0].set_xscale("log"); ax[0, 0].set_xlabel("capital/success"); ax[0, 0].set_ylabel("# lucky events"); ax[0, 0].set_title("(a)")
    ax[0, 1].scatter(C, final.nunlucky, s=10, alpha=0.5, color="#C44E52")
    ax[0, 1].set_xscale("log"); ax[0, 1].set_xlabel("capital/success"); ax[0, 1].set_ylabel("# unlucky events"); ax[0, 1].set_title("(b)")
    ax[1, 0].scatter(lx, lh, color="#4C72B0"); ax[1, 0].plot(lx, lA * np.exp(-lb * lx), "r-", label=f"A={lA:.1f}, b={lb:.2f}")
    ax[1, 0].set_yscale("log"); ax[1, 0].set_xlabel("# lucky events"); ax[1, 0].set_ylabel("frequency"); ax[1, 0].set_title("(c) lucky-event pdf"); ax[1, 0].legend()
    ax[1, 1].scatter(ux, uh, color="#C44E52"); ax[1, 1].plot(ux, uA * np.exp(-ub * ux), "r-", label=f"A={uA:.1f}, b={ub:.2f}")
    ax[1, 1].set_yscale("log"); ax[1, 1].set_xlabel("# unlucky events"); ax[1, 1].set_ylabel("frequency"); ax[1, 1].set_title("(d) unlucky-event pdf"); ax[1, 1].legend()
    fig.tight_layout(); fig.savefig(os.path.join(args.out, "fig5_events.pdf")); plt.close(fig)

    # Fig 6: (a) max-agent trajectory + its event sequence; (b) min-agent
    def event_sequence(traj):
        s = traj.sort_values("time")
        t = s.time.values; c = s.success.values
        lu = s.nlucky.values; un = s.nunlucky.values
        spikes = []  # (time, +1 lucky-exploited / -1 unlucky)
        for i in range(1, len(c)):
            if c[i] > c[i - 1]:       # doubled -> lucky event exploited
                spikes.append((t[i], +1))
            elif c[i] < c[i - 1]:     # halved -> unlucky event
                spikes.append((t[i], -1))
        return t, c, spikes
    fig, ax = plt.subplots(2, 2, figsize=(11, 7), gridspec_kw={"height_ratios": [2, 1]})
    for col, traj, title in [(0, traj_max, f"(a) most successful (who={who_max}, T={m['max_agent_talent']:.2f})"),
                             (1, traj_min, f"(b) least successful (who={who_min}, T={m['min_agent_talent']:.2f})")]:
        t, c, spikes = event_sequence(traj)
        ax[0, col].plot(t, c, "-o", ms=3, color="#333333")
        ax[0, col].set_yscale("log"); ax[0, col].set_ylabel("capital/success"); ax[0, col].set_title(title)
        for (ts, sgn) in spikes:
            ax[1, col].vlines(ts, 0, sgn, color=("#4C72B0" if sgn > 0 else "#C44E52"))
        ax[1, col].axhline(0, color="k", lw=0.5); ax[1, col].set_ylim(-1.3, 1.3)
        ax[1, col].set_xlabel("time step"); ax[1, col].set_ylabel("event (+luck/-unluck)")
    fig.tight_layout(); fig.savefig(os.path.join(args.out, "fig6_trajectories.pdf")); plt.close(fig)
    print("Figures written to", args.out)


if __name__ == "__main__":
    main()
