#!/usr/bin/env python3
"""T1 generalized-TvL calibration grid.

Grid: alpha in {0,0.1,...,1.0} (11) x p_L in {20,35,50,65,80} (5) x 100 runs.
For each cell compute the MODEL triple (+ extras), mirroring 001's g2_reference
construct definitions exactly:
  - top20_capital_share            (success top-20% share)
  - top1_capital_share             (success top-1% share)
  - winner_pct_emp                 (winner talent empirical percentile)
  - P_winner_top_decile            (winner talent > true top-decile cut 0.728)
  - persist_y2y_top100  (PRIMARY)  (back-half t>40, 2-step windows, top-100, averaged)
  - persist_splithalf_top100 (SECONDARY, reported not used in distance)

Common random numbers: all 11 alpha share one seed per p_L (seed=1000+pL), so the
alpha effect is isolated (talent/positions/events/Bernoulli draws identical across
alpha; only the q=(1-a)qbar+a*T threshold differs).  Runs one --alpha per call
(<=8 min), appends to results/calibration_grid.csv, checkpoints alpha_<i>.done.
"""
import os, sys, json, time, argparse
import numpy as np
from scipy.stats import norm, spearmanr
import torch

CODE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE)
from tvl_alpha import simulate_batch

OUT = "/workspace/eval/followup/002-002-theory-update/results"
CKPT = "/workspace/eval/followup/002-002-theory-update/workspace/checkpoints"
os.makedirs(OUT, exist_ok=True); os.makedirs(CKPT, exist_ok=True)
GRID_CSV = os.path.join(OUT, "calibration_grid.csv")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
mT, sT = 0.6, 0.1
N, NE, I, C0 = 1000, 500, 80, 10.0
ALPHAS = [round(0.1 * i, 1) for i in range(11)]
PLS = [20, 35, 50, 65, 80]
TOP_DECILE_CUT = mT + norm.ppf(0.9) * sT   # 0.72816 (true top-decile talent cut)


def cell_stats(alpha, pL, R=100, seed=None, chunk=50):
    """Run R replicates at (alpha,pL); return per-run arrays of model statistics."""
    if seed is None:
        seed = 1000 + pL
    acc = {k: [] for k in ["top20", "top1", "winner_pct", "win_decile",
                           "persist_y2y", "persist_splithalf", "winner_T"]}
    done = 0; cid = 0
    while done < R:
        r = min(chunk, R - done)
        res = simulate_batch(r, N, NE, I, mT, sT, pL, C0=C0, device=DEVICE,
                             seed=seed + cid, truncate_talent=True,
                             record_traj=True, alpha=alpha)
        succ = res["success"].cpu().numpy()
        tal = res["talent"].cpu().numpy()
        traj = res["traj"].cpu().numpy()
        for i in range(r):
            s = succ[i]; t = tal[i]
            tot = s.sum()
            ssort = np.sort(s)[::-1]
            acc["top20"].append(ssort[:int(0.2 * N)].sum() / tot)
            acc["top1"].append(ssort[:max(1, int(0.01 * N))].sum() / tot)
            wi = int(np.argmax(s)); wt = t[wi]
            acc["winner_T"].append(wt)
            acc["winner_pct"].append((t < wt).mean())
            acc["win_decile"].append(float(wt > TOP_DECILE_CUT))
            # split-half (secondary): ranks at t=40 vs t=80, top-100 by t=40
            c40 = traj[i, :, 40]; c80 = traj[i, :, 80]
            top100 = np.argsort(c40)[::-1][:100]
            acc["persist_splithalf"].append(spearmanr(c40[top100], c80[top100]).statistic)
            # y2y (primary): back-half t>40, 2-step windows, top-100 by earlier year
            ys = list(range(40, 81, 2))
            rhos = []
            for a_, b_ in zip(ys[:-1], ys[1:]):
                ca = traj[i, :, a_]; cb = traj[i, :, b_]
                tp = np.argsort(ca)[::-1][:100]
                rr = spearmanr(ca[tp], cb[tp]).statistic
                if np.isfinite(rr):
                    rhos.append(rr)
            acc["persist_y2y"].append(np.mean(rhos) if rhos else np.nan)
        done += r; cid += 1
    return {k: np.asarray(v, float) for k, v in acc.items()}


def summarize(a, alpha, pL):
    def ms(x):
        x = x[np.isfinite(x)]
        return float(np.mean(x)), float(np.std(x, ddof=1) / np.sqrt(len(x)))
    row = {"alpha": alpha, "p_L": pL, "n_runs": int(len(a["winner_pct"]))}
    for key, name in [("top20", "top20_capital_share"), ("top1", "top1_capital_share"),
                      ("winner_pct", "winner_pct_emp"), ("win_decile", "P_winner_top_decile"),
                      ("persist_y2y", "persist_y2y_top100"),
                      ("persist_splithalf", "persist_splithalf_top100"),
                      ("winner_T", "winner_T_mean")]:
        m, se = ms(a[key])
        row[name] = m
        row[name + "_mcse"] = se
    return row


def append_rows(rows):
    import pandas as pd
    df = pd.DataFrame(rows)
    if os.path.exists(GRID_CSV):
        old = pd.read_csv(GRID_CSV)
        old = old[~((old.alpha.isin(df.alpha)) & (old.p_L.isin(df.p_L))
                    & old.set_index(["alpha", "p_L"]).index.isin(df.set_index(["alpha", "p_L"]).index))]
        df = pd.concat([old, df], ignore_index=True)
    df = df.sort_values(["alpha", "p_L"]).reset_index(drop=True)
    df.to_csv(GRID_CSV, index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--alpha", type=float, required=True)
    ap.add_argument("--R", type=int, default=100)
    args = ap.parse_args()
    alpha = round(args.alpha, 1)
    t0 = time.time()
    rows = []
    for pL in PLS:
        a = cell_stats(alpha, pL, R=args.R)
        rows.append(summarize(a, alpha, pL))
        print(f"alpha={alpha} pL={pL} top20={rows[-1]['top20_capital_share']:.3f} "
              f"winnerpct={rows[-1]['winner_pct_emp']:.3f} "
              f"Pdec={rows[-1]['P_winner_top_decile']:.3f} "
              f"persist_y2y={rows[-1]['persist_y2y_top100']:.3f} "
              f"[{time.time()-t0:.0f}s]")
    append_rows(rows)
    open(os.path.join(CKPT, f"alpha_{alpha}.done"), "w").write(time.strftime("%F %T"))
    print(f"alpha={alpha} DONE in {time.time()-t0:.0f}s -> {GRID_CSV}")


if __name__ == "__main__":
    main()
