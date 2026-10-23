#!/usr/bin/env python3
"""Steps 9 & 10: environment experiments (section 3.2, Figs 13 & 14).

Each config = baseline (N=1000, I=80, NE=500, C0=10) with overrides. 100 runs.
Per config record: best performer per run (talent, capital); C_best (max over
runs) and its talent; the next-best performers; C_mt (avg capital of the "most
talented"); P_T (% of talented agents with final C>C0).

"most talented" cutoff: primary = absolute T>0.8 (the paper's canonical
mT+2sigmaT cutoff for the baseline; for mT=0.6,sigmaT=0.2 the relative
mT+2sigmaT=1.0 is empty under truncation, so absolute 0.8 is used and the
relative value, where defined, is also recorded).
P_T threshold = mT+sigmaT (per config).
"""
import argparse, json, os
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tvl import simulate_batch

N = 1000


def parse_cfg(s):
    base = dict(mT=0.6, sigmaT=0.1, pL=50.0)
    for part in s.split(","):
        k, v = part.split("=")
        base[k.strip()] = float(v)
    return base


def run_config(cfg, runs, NE, I, C0, device, seed, truncate=True):
    mT, sT, pL = cfg["mT"], cfg["sigmaT"], cfg["pL"]
    best_t, best_c = [], []
    pt_runs = []
    cmt_abs_vals = []        # capitals of agents with T>0.8 (absolute), pooled
    cmt_rel_vals = []        # capitals of agents with T>mT+2sigmaT (where non-empty)
    thr_pt = mT + sT
    thr_rel = mT + 2 * sT
    remaining = runs; chunk = 200; cid = 0
    while remaining > 0:
        R = min(chunk, remaining)
        out = simulate_batch(R, N, NE, I, mT, sT, pL, C0=C0, device=device,
                             seed=seed + cid, truncate_talent=truncate)
        tal = out["talent"]; succ = out["success"]
        bc, bi = succ.max(dim=1)
        bt = tal.gather(1, bi[:, None]).squeeze(1)
        best_t.append(bt.cpu().numpy()); best_c.append(bc.cpu().numpy())
        # PT per run
        m = tal > thr_pt
        num = ((succ > C0) & m).sum(dim=1).float()
        den = m.sum(dim=1).clamp(min=1).float()
        pt_runs.append((100.0 * num / den).cpu().numpy())
        # Cmt pools
        tflat = tal.reshape(-1).cpu().numpy(); cflat = succ.reshape(-1).cpu().numpy()
        cmt_abs_vals.append(cflat[tflat > 0.8])
        cmt_rel_vals.append(cflat[tflat > thr_rel])
        remaining -= R; cid += 1
    best_t = np.concatenate(best_t); best_c = np.concatenate(best_c)
    pt = float(np.concatenate(pt_runs).mean())
    cmt_abs = np.concatenate(cmt_abs_vals)
    cmt_rel = np.concatenate(cmt_rel_vals)
    order = np.argsort(best_c)[::-1]
    nb = [{"talent": float(best_t[i]), "capital": float(best_c[i])} for i in order[:5]]
    res = {
        "C_best": float(best_c.max()),
        "T_at_C_best": float(best_t[int(np.argmax(best_c))]),
        "next_best": nb[1:5],
        "C_mt": (float(cmt_rel.mean()) if cmt_rel.size else float("nan")),
        "C_mt_def": f"mean final capital of 'most talented' = agents with T>mT+2sigmaT={thr_rel:.2f} (paper's relative cut)",
        "C_mt_n_per_run": float(cmt_rel.size / runs),
        "C_mt_absolute_gt_0p8": (float(cmt_abs.mean()) if cmt_abs.size else None),
        "P_T": pt,
        "P_T_threshold": thr_pt,
        "_best_t": best_t, "_best_c": best_c,
    }
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", nargs="+", required=True)
    ap.add_argument("--runs", type=int, default=100)
    ap.add_argument("--NE", type=int, default=500)
    ap.add_argument("--I", type=int, default=80)
    ap.add_argument("--C0", type=float, default=10)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2000)
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--no-truncate", dest="truncate", action="store_false",
                    help="match the shipped demo / paper RESULTS (talent not clipped to [0,1]); needed so the 'most talented' T>mT+2sigmaT cut is non-empty for sigmaT=0.2")
    ap.set_defaults(truncate=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    device = "cuda" if (args.gpu and torch.cuda.is_available()) else "cpu"

    cfgs = [parse_cfg(s) for s in args.configs]
    is_pL = any(c["pL"] != 50.0 for c in cfgs)
    metrics = {}
    panels = []
    for i, cfg in enumerate(cfgs):
        res = run_config(cfg, args.runs, args.NE, args.I, args.C0, device, args.seed + 1000 * i, truncate=args.truncate)
        label = ",".join(f"{k}={cfg[k]}" for k in ("mT", "sigmaT", "pL"))
        bt = res.pop("_best_t"); bc = res.pop("_best_c")
        panels.append((cfg, bt, bc, label))
        metrics[args.configs[i]] = res
        print(f"[{args.configs[i]}] C_best={res['C_best']:.0f} T={res['T_at_C_best']:.3f} "
              f"C_mt={res['C_mt']:.1f} P_T={res['P_T']:.2f}%")

    name = "env_pL_metrics.json" if is_pL else "env_talent_metrics.json"
    with open(os.path.join(args.out, name), "w") as f:
        json.dump(metrics, f, indent=2)
    print(json.dumps(metrics, indent=2))

    fig_name = "fig14_best_vs_talent.pdf" if is_pL else "fig13_best_vs_talent.pdf"
    fig, axes = plt.subplots(1, len(panels), figsize=(6 * len(panels), 5), squeeze=False)
    for ax, (cfg, bt, bc, label) in zip(axes[0], panels):
        ax.scatter(bt, bc, s=22, color="#55A868")
        ax.set_yscale("log"); ax.set_xlabel("talent of best performer"); ax.set_ylabel("final capital")
        mT, sT = cfg["mT"], cfg["sigmaT"]
        for v, st in [(mT, "--"), (mT - sT, ":"), (mT + sT, ":")]:
            ax.axvline(v, color="k", ls=st, lw=0.8)
        ax.set_title(label)
    fig.tight_layout(); fig.savefig(os.path.join(args.out, fig_name)); plt.close(fig)
    print("wrote", os.path.join(args.out, fig_name))


if __name__ == "__main__":
    main()
