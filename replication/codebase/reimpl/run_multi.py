#!/usr/bin/env python3
"""Steps 5 & 6: multiple-run baseline (section 2.2) with the reimplementation.

Step 5: --runs 100  -> multi_metrics.json + fig7, fig8a, fig9.
Step 6: --runs 10000 --gaussian -> gaussian_fit.json + fig8b (GPU, chunked).
"""
import argparse, json, os
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tvl import simulate_batch


def powerlaw_slope(capital, cmin=10.0):
    vals, counts = np.unique(capital, return_counts=True)
    pdf = counts / counts.sum()
    mask = (vals >= cmin) & (counts > 0)
    x, y = np.log10(vals[mask]), np.log10(pdf[mask])
    slope, icept = np.polyfit(x, y, 1)
    return float(slope), icept, vals, pdf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, required=True)
    ap.add_argument("--N", type=int, default=1000)
    ap.add_argument("--mT", type=float, default=0.6)
    ap.add_argument("--sigmaT", type=float, default=0.1)
    ap.add_argument("--I", type=int, default=80)
    ap.add_argument("--NE", type=int, default=500)
    ap.add_argument("--pL", type=float, default=50)
    ap.add_argument("--C0", type=float, default=10)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=100)
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--gaussian", action="store_true", help="step-6 mode: fit Gaussian to best-talent PDF")
    ap.add_argument("--chunk", type=int, default=250)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    device = "cuda" if (args.gpu and torch.cuda.is_available()) else "cpu"
    mT, sT = args.mT, args.sigmaT
    thr_talented = mT + sT            # T>0.7 baseline
    thr_mosttal = mT + 2 * sT         # T>0.8 baseline ("most talented")
    near_lo, near_hi = mT - 0.5 * sT, mT + 0.5 * sT  # "very close to mean"

    best_talents = []   # per-run best-performer talent
    best_caps = []      # per-run best-performer capital
    full_mode = not args.gaussian     # step5 keeps all agents
    all_cap = [] if full_mode else None
    all_tal = [] if full_mode else None
    record_traj = full_mode and args.runs <= 500
    global_best = {"C": -1, "run": -1, "idx": -1, "T": None, "traj": None}

    remaining = args.runs
    chunk_id = 0
    done = 0
    while remaining > 0:
        R = min(args.chunk, remaining)
        out = simulate_batch(R, args.N, args.NE, args.I, mT, sT, args.pL,
                             C0=args.C0, device=device, seed=args.seed + chunk_id,
                             truncate_talent=True, record_traj=record_traj)
        succ = out["success"]; tal = out["talent"]
        bc, bi = succ.max(dim=1)       # best capital & index per run
        bt = tal.gather(1, bi[:, None]).squeeze(1)
        best_caps.append(bc.cpu().numpy()); best_talents.append(bt.cpu().numpy())
        # global best
        cmax_chunk = bc.max().item(); r_local = int(bc.argmax().item())
        if cmax_chunk > global_best["C"]:
            i_local = int(bi[r_local].item())
            global_best.update(C=cmax_chunk, run=done + r_local, idx=i_local,
                               T=float(tal[r_local, i_local].item()))
            if record_traj:
                global_best["traj"] = out["traj"][r_local, i_local].cpu().numpy()
        if full_mode:
            all_cap.append(succ.cpu().numpy()); all_tal.append(tal.cpu().numpy())
        done += R; remaining -= R; chunk_id += 1

    best_talents = np.concatenate(best_talents)
    best_caps = np.concatenate(best_caps)

    if args.gaussian:
        # Step 6: PDF of best-performer talent + Gaussian fit
        from scipy.optimize import curve_fit
        mu0, sd0 = best_talents.mean(), best_talents.std()
        counts, edges = np.histogram(best_talents, bins=60, density=True)
        centers = 0.5 * (edges[:-1] + edges[1:])
        def gauss(x, A, mu, sd):
            return A * np.exp(-(x - mu) ** 2 / (2 * sd ** 2))
        try:
            popt, _ = curve_fit(gauss, centers, counts, p0=[counts.max(), mu0, sd0])
            A_fit, mu_fit, sd_fit = popt
            sd_fit = abs(sd_fit)
        except Exception:
            A_fit, mu_fit, sd_fit = 1.0 / (sd0 * np.sqrt(2 * np.pi)), mu0, sd0
        res = {"gauss_mean": float(mu_fit), "gauss_std": float(sd_fit),
               "n_runs": int(args.runs),
               "best_talents_summary": {"mean": float(best_talents.mean()),
                                        "std": float(best_talents.std()),
                                        "min": float(best_talents.min()),
                                        "max": float(best_talents.max()),
                                        "median": float(np.median(best_talents))}}
        with open(os.path.join(args.out, "gaussian_fit.json"), "w") as f:
            json.dump(res, f, indent=2)
        print(json.dumps(res, indent=2))
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.hist(best_talents, bins=60, density=True, alpha=0.6, color="#4C72B0", label="best-performer talent PDF")
        xx = np.linspace(best_talents.min(), best_talents.max(), 300)
        ax.plot(xx, gauss(xx, A_fit, mu_fit, sd_fit), "r-", lw=2,
                label=f"Gaussian fit\nmean={mu_fit:.3f}, std={sd_fit:.3f}")
        ax.axvline(mT, color="k", ls="--", label=f"mT={mT}")
        ax.set_xlabel("talent of best performer"); ax.set_ylabel("PDF")
        ax.set_title(f"Fig 8b: best-performer talent PDF over {args.runs} runs"); ax.legend()
        fig.tight_layout(); fig.savefig(os.path.join(args.out, "fig8b_best_talent_pdf.pdf")); plt.close(fig)
        return

    # ---------------- Step 5 full metrics ----------------
    cap = np.concatenate(all_cap, axis=0).ravel()   # pooled final capitals
    tal = np.concatenate(all_tal, axis=0)            # (runs, N)
    capm = np.concatenate(all_cap, axis=0)           # (runs, N)
    slope, icept, vals, pdf = powerlaw_slope(cap, cmin=10.0)

    gi = global_best
    C_best = float(gi["C"]); T_best = float(gi["T"])
    # most talented among the 100 best performers
    j = int(np.argmax(best_talents))
    T_max_among_best = float(best_talents[j]); C_at_Tmax = float(best_caps[j])
    # fraction of runs whose best performer has talent>0.8
    mask08 = best_talents > thr_mosttal
    frac08 = float(mask08.mean())
    max_ratio08 = float(best_caps[mask08].max() / C_best) if mask08.any() else 0.0
    # group averages over all agents, all runs
    flat_t = tal.ravel(); flat_c = capm.ravel()
    C_mt = float(flat_c[flat_t > thr_mosttal].mean())
    C_at = float(flat_c[(flat_t >= near_lo) & (flat_t <= near_hi)].mean())
    # P_T0: per-run % of T>0.7 agents with capital>C0, averaged over runs
    pt0_per_run = []
    for r in range(tal.shape[0]):
        m = tal[r] > thr_talented
        if m.sum() > 0:
            pt0_per_run.append(100.0 * ((capm[r][m] > args.C0).mean()))
    P_T0 = float(np.mean(pt0_per_run))

    metrics = {
        "powerlaw_slope": slope,
        "global_max_capital": float(cap.max()),
        "T_best": T_best, "C_best": C_best,
        "T_max_among_best": T_max_among_best, "C_at_T_max_among_best": C_at_Tmax,
        "ratio_to_Cbest": float(C_at_Tmax / C_best),
        "T_av_best": float(best_talents.mean()),
        "frac_best_talent_gt_0p8": frac08,
        "max_capital_ratio_talent_gt_0p8": max_ratio08,
        "C_mt": C_mt, "C_at": C_at, "P_T0": P_T0,
        "_defs": {"most_talented": f"T>{thr_mosttal:.3f} (mT+2sigmaT)",
                  "near_mean": f"{near_lo:.3f}<=T<={near_hi:.3f} (mT+-0.5sigmaT)",
                  "talented_PT": f"T>{thr_talented:.3f} (mT+sigmaT)",
                  "powerlaw": "regress log10(pdf) on log10(C) for C>=C0=10 over pooled runs"},
        "n_runs": int(args.runs),
    }
    with open(os.path.join(args.out, "multi_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)
    print(json.dumps(metrics, indent=2))

    # Fig 7a: pooled log-log + fit ; 7b: best capital vs talent
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    mask = vals >= 10
    ax[0].scatter(np.log10(vals[mask]), np.log10(pdf[mask]), s=14, color="#4C72B0", label="pooled data")
    xx = np.linspace(np.log10(10), np.log10(vals.max()), 50)
    ax[0].plot(xx, icept + slope * xx, "r-", label=f"slope={slope:.2f}")
    ax[0].set_xlabel("log10(capital)"); ax[0].set_ylabel("log10(pdf)")
    ax[0].set_title("(a) pooled capital distribution"); ax[0].legend()
    ax[1].scatter(best_talents, best_caps, s=20, color="#55A868")
    ax[1].set_yscale("log"); ax[1].set_xlabel("talent of best performer"); ax[1].set_ylabel("final capital")
    for v, st in [(mT, "--"), (mT - sT, ":"), (mT + sT, ":")]:
        ax[1].axvline(v, color="k", ls=st, lw=0.8)
    ax[1].set_title("(b) best-performer capital vs talent")
    fig.tight_layout(); fig.savefig(os.path.join(args.out, "fig7_distribution_and_scatter.pdf")); plt.close(fig)

    # Fig 8a: histogram of best-performer talent
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(best_talents, bins=25, color="#4C72B0", alpha=0.8)
    ax.axvline(mT, color="k", ls="--", label=f"mT={mT}")
    ax.set_xlabel("talent of best performer"); ax.set_ylabel("# runs")
    ax.set_title(f"Fig 8a: best-performer talent over {args.runs} runs (Tav={best_talents.mean():.3f})"); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(args.out, "fig8a_best_talent_hist.pdf")); plt.close(fig)

    # Fig 9: trajectory + lucky-event sequence of the global best performer
    if gi["traj"] is not None:
        traj = gi["traj"]; t = np.arange(len(traj))
        spikes = []
        for i in range(1, len(traj)):
            if traj[i] > traj[i - 1]:
                spikes.append((t[i], +1))
            elif traj[i] < traj[i - 1]:
                spikes.append((t[i], -1))
        fig, ax = plt.subplots(2, 1, figsize=(8, 6), gridspec_kw={"height_ratios": [2, 1]})
        ax[0].plot(t, traj, "-o", ms=3, color="#333333")
        ax[0].set_yscale("log"); ax[0].set_ylabel("capital/success")
        ax[0].set_title(f"Fig 9: best performer (run {gi['run']}, T={T_best:.3f}, C_best={C_best:.0f})")
        for ts, sgn in spikes:
            ax[1].vlines(ts, 0, sgn, color=("#4C72B0" if sgn > 0 else "#C44E52"))
        ax[1].axhline(0, color="k", lw=0.5); ax[1].set_ylim(-1.3, 1.3)
        ax[1].set_xlabel("time step"); ax[1].set_ylabel("event (+luck/-unluck)")
        fig.tight_layout(); fig.savefig(os.path.join(args.out, "fig9_best_trajectory.pdf")); plt.close(fig)


if __name__ == "__main__":
    main()
