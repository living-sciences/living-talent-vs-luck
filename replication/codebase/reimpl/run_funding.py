#!/usr/bin/env python3
"""Steps 7 & 8: funding-strategy experiments (section 3.1, Figs 10/11 and 12).

Injects capital at 8 time points (every 5 years = every 10 steps: t=10,20,...,80)
over I=80, baseline params (N=1000, mT=0.6, sigmaT=0.1, NE=500, pL=50, C0=10),
100 runs per strategy (paired seeds across strategies for low-variance PT*).

PT  = avg over runs of [% of agents with T>mT+sigmaT (=0.7) and final C>C0(=10)]
PT0 = PT of the NO FUNDING strategy
PT* = PT - PT0 ;  E = PT*/FT ;  Enorm = E/Emax (NO FUNDING := 0)
"""
import argparse, json, os
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tvl import simulate_batch

INJECT_STEPS = [10, 20, 30, 40, 50, 60, 70, 80]
N = 1000


def fig10_strategies():
    S = {}
    S["NO FUNDING"] = None
    for u in (1, 2, 5):
        S[f"ALL EQUAL {u}u"] = dict(kind="equal", units=u, steps=INJECT_STEPS)
    for frac, tag in ((0.10, "10%"), (0.25, "25%"), (0.50, "50%")):
        for u in (5, 20):
            S[f"{tag} RANDOM {u}u"] = dict(kind="random", frac=frac, units=u, steps=INJECT_STEPS)
    for u in (5, 10, 15, 20):
        S[f"25% BEST {u}u"] = dict(kind="best", frac=0.25, units=u, steps=INJECT_STEPS)
    for u in (5, 10, 20):
        S[f"10% BEST {u}u"] = dict(kind="best", frac=0.10, units=u, steps=INJECT_STEPS)
    S["50% BEST 5u"] = dict(kind="best", frac=0.50, units=5, steps=INJECT_STEPS)
    S["25% BEST 5u + OTHERS 1u"] = dict(kind="best_others", best_frac=0.25, best_units=5, others_units=1, steps=INJECT_STEPS)
    S["25% BEST 10u + OTHERS 1u"] = dict(kind="best_others", best_frac=0.25, best_units=10, others_units=1, steps=INJECT_STEPS)
    S["25% BEST 10u + OTHERS 5u"] = dict(kind="best_others", best_frac=0.25, best_units=10, others_units=5, steps=INJECT_STEPS)
    return S


def fig12_strategies():
    """Fixed total FT=80000 -> 10000 units per injection distributed."""
    per = 80000.0 / 8.0  # 10000 per injection
    S = {}
    S["NO FUNDING"] = None
    S["ALL EQUAL"] = dict(kind="equal", units=per / N, steps=INJECT_STEPS)
    for frac, tag in ((0.10, "10%"), (0.25, "25%"), (0.50, "50%")):
        k = round(frac * N)
        S[f"{tag} RANDOM"] = dict(kind="random", frac=frac, units=per / k, steps=INJECT_STEPS)
    for frac, tag in ((0.10, "10%"), (0.25, "25%"), (0.50, "50%")):
        k = round(frac * N)
        S[f"{tag} BEST"] = dict(kind="best", frac=frac, units=per / k, steps=INJECT_STEPS)
    kb = round(0.25 * N)
    S["HALF 25% BEST + HALF OTHERS"] = dict(kind="best_others", best_frac=0.25,
                                            best_units=(per / 2) / kb,
                                            others_units=(per / 2) / (N - kb), steps=INJECT_STEPS)
    return S


def run_strategy(funding, runs, mT, sT, pL, NE, I, C0, device, base_seed):
    """Return (PT, FT) with PT averaged over runs and FT the mean invested."""
    thr = mT + sT
    pts, fts = [], []
    remaining = runs; chunk = 200; cid = 0
    while remaining > 0:
        R = min(chunk, remaining)
        out = simulate_batch(R, N, NE, I, mT, sT, pL, C0=C0, device=device,
                             seed=base_seed + cid, truncate_talent=True, funding=funding)
        tal = out["talent"]; succ = out["success"]; inv = out["invested"]
        mask = tal > thr                                   # (R,N)
        succ_gt = (succ > C0) & mask
        denom = mask.sum(dim=1).clamp(min=1).float()
        pt = 100.0 * succ_gt.sum(dim=1).float() / denom    # (R,)
        pts.append(pt.cpu().numpy()); fts.append(inv.cpu().numpy())
        remaining -= R; cid += 1
    pts = np.concatenate(pts); fts = np.concatenate(fts)
    return float(pts.mean()), float(fts.mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategies", choices=["fig10", "fig12"], required=True)
    ap.add_argument("--runs", type=int, default=100)
    ap.add_argument("--fixed-FT", type=float, default=None)
    ap.add_argument("--mT", type=float, default=0.6)
    ap.add_argument("--sigmaT", type=float, default=0.1)
    ap.add_argument("--pL", type=float, default=50)
    ap.add_argument("--NE", type=int, default=500)
    ap.add_argument("--I", type=int, default=80)
    ap.add_argument("--C0", type=float, default=10)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--gpu", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    device = "cuda" if (args.gpu and torch.cuda.is_available()) else "cpu"

    S = fig10_strategies() if args.strategies == "fig10" else fig12_strategies()

    # Pass 1: PT and FT for every strategy (paired seeds)
    results = {}
    for name, fund in S.items():
        PT, FT = run_strategy(fund, args.runs, args.mT, args.sigmaT, args.pL,
                              args.NE, args.I, args.C0, device, args.seed)
        results[name] = {"PT": PT, "FT": FT}
        print(f"{name:34s} PT={PT:6.2f}%  FT={FT:8.0f}")

    PT0 = results["NO FUNDING"]["PT"]
    for name, r in results.items():
        r["PT_star"] = r["PT"] - PT0
        r["E"] = (r["PT_star"] / r["FT"]) if r["FT"] > 0 else 0.0
    Emax = max(r["E"] for r in results.values())
    for name, r in results.items():
        r["E_norm"] = (r["E"] / Emax) if Emax > 0 else 0.0
    results["NO FUNDING"]["E_norm"] = 0.0   # by definition

    # Build sorted table (NO FUNDING placed by its E_norm=0)
    rows = sorted(results.items(), key=lambda kv: kv[1]["E_norm"], reverse=True)
    import csv
    csv_name = "funding_table.csv" if args.strategies == "fig10" else "funding_table_fixed.csv"
    with open(os.path.join(args.out, csv_name), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["strategy", "E_norm", "P_T", "P_T_star", "F_T"])
        for name, r in rows:
            w.writerow([name, f"{r['E_norm']:.4f}", f"{r['PT']:.2f}", f"{r['PT_star']:.2f}", f"{r['FT']:.0f}"])
    with open(os.path.join(args.out, "funding_metrics.json"), "w") as f:
        json.dump({"PT0": PT0, "Emax": Emax, "n_runs": args.runs,
                   "inject_steps": INJECT_STEPS, "strategies": results}, f, indent=2)

    print(f"\nPT0 (no funding) = {PT0:.2f}%   Emax = {Emax:.3e}")
    print(f"{'strategy':34s} {'E_norm':>7s} {'PT':>7s} {'PT*':>7s} {'FT':>8s}")
    for name, r in rows:
        print(f"{name:34s} {r['E_norm']:7.3f} {r['PT']:7.2f} {r['PT_star']:7.2f} {r['FT']:8.0f}")

    # Fig 11 histogram (fig10 only)
    if args.strategies == "fig10":
        names = [n for n, _ in rows]
        enorms = [r["E_norm"] for _, r in rows]
        fig, ax = plt.subplots(figsize=(11, 6))
        ax.bar(range(len(names)), enorms, color="#4C72B0")
        ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=90, fontsize=7)
        ax.set_ylabel("E_norm"); ax.set_title("Fig 11: normalized efficiency index by funding strategy")
        fig.tight_layout(); fig.savefig(os.path.join(args.out, "fig11_efficiency_hist.pdf")); plt.close(fig)


if __name__ == "__main__":
    main()
