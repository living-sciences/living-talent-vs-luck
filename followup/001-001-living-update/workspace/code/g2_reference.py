"""Block A / G2 model reference anchor.
Runs the faithful TvL engine (replication reimpl) and derives the model-side
reference distributions used by every S2 comparison and by M2/M3/M4.

Engine note (deviation): the spec cites `shared-data/tvl-engine/`; that folder is
NOT staged. The faithful engine is the replication codebase reimpl/tvl.py, whose
fidelity to the NetLogo model is established in the replication (multi_10000:
winner-talent mean 0.670, sd 0.093). We use it and record the substitution.
Seeds "1..1000": the batched engine seeds the whole batch's RNG stream; we realize
1000 independent replicates per block under fixed master seeds (baseline seed=1,
ladder seeds 20/50/80), replicates independent draws. Recorded as a deviation.
"""
import os, sys, json, time
import numpy as np
from scipy.stats import norm, spearmanr
sys.path.insert(0, "/workspace/eval/replication/codebase/reimpl")
import torch
from tvl import simulate_batch
from common import RESULTS, done, write_json

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
mT, sT = 0.6, 0.1
N, NE, I, C0 = 1000, 500, 80, 10.0

# staged QA distcheck bands quoted verbatim in the spec (§1); file not separately staged.
QA_BANDS = {
    "winner_T_mean": {"center": 0.6686, "tol": 0.01},
    "winner_T_sd": {"center": 0.0932, "tol": 0.015},
    "top20pct_share": {"center": 0.774, "tol": 0.02},
}
TOP_DECILE_CUT = mT + norm.ppf(0.9) * sT  # T > 0.728 true top-decile cut
THR_08 = 0.8


def gini(x):
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    cum = np.cumsum(x)
    return float((n + 1 - 2 * (cum / cum[-1]).sum()) / n)


def run_block(R, seed, pL, record_traj=True):
    """Run R replicates; return per-run arrays of the needed statistics."""
    out = {"winner_T": [], "winner_pct_emp": [], "winner_pct_theo": [],
           "winner_top_decile": [], "winner_T_gt_08": [],
           "top10_median_T_pct_emp": [], "top20_share": [], "gini": [],
           "persist_splithalf_all": [], "persist_splithalf_top100": [],
           "persist_y2y_top100": []}
    chunk = int(os.environ.get("TVL_CHUNK", "100"))
    done_n = 0
    cid = 0
    while done_n < R:
        r = min(chunk, R - done_n)
        res = simulate_batch(r, N, NE, I, mT, sT, pL, C0=C0, device=DEVICE,
                             seed=seed + cid, truncate_talent=True,
                             record_traj=record_traj)
        succ = res["success"].cpu().numpy()      # (r,N)
        tal = res["talent"].cpu().numpy()         # (r,N)
        traj = res["traj"].cpu().numpy() if record_traj else None  # (r,N,I+1)
        for i in range(r):
            s = succ[i]; t = tal[i]
            wi = int(np.argmax(s))
            wt = t[wi]
            out["winner_T"].append(float(wt))
            out["winner_pct_emp"].append(float((t < wt).mean()))
            out["winner_pct_theo"].append(float(norm.cdf((wt - mT) / sT)))
            out["winner_top_decile"].append(float(wt > TOP_DECILE_CUT))
            out["winner_T_gt_08"].append(float(wt > THR_08))
            top10 = np.argsort(s)[::-1][:10]
            med_t = np.median(t[top10])
            out["top10_median_T_pct_emp"].append(float((t < med_t).mean()))
            ssort = np.sort(s)[::-1]
            out["top20_share"].append(float(ssort[:int(0.2 * N)].sum() / s.sum()))
            out["gini"].append(gini(s))
            if traj is not None:
                c40 = traj[i, :, 40]; c80 = traj[i, :, 80]
                out["persist_splithalf_all"].append(float(spearmanr(c40, c80).statistic))
                top100 = np.argsort(c40)[::-1][:100]
                out["persist_splithalf_top100"].append(
                    float(spearmanr(c40[top100], c80[top100]).statistic))
                # y2y: 1 year = 2 steps; back half t>40 -> years at t=40,42,...,80
                ys = list(range(40, 81, 2))
                rhos = []
                for a, b in zip(ys[:-1], ys[1:]):
                    ca = traj[i, :, a]; cb = traj[i, :, b]
                    tp = np.argsort(ca)[::-1][:100]
                    rr = spearmanr(ca[tp], cb[tp]).statistic
                    if np.isfinite(rr):
                        rhos.append(rr)
                out["persist_y2y_top100"].append(float(np.mean(rhos)) if rhos else np.nan)
        done_n += r; cid += 1
    return {k: np.array(v, dtype=float) for k, v in out.items()}


def summarize(a):
    def q(x, p):
        return float(np.nanpercentile(x, p))
    return {
        "winner_T_mean": float(np.mean(a["winner_T"])),
        "winner_T_sd": float(np.std(a["winner_T"])),
        "winner_pct_emp_mean": float(np.mean(a["winner_pct_emp"])),
        "winner_pct_emp_p2.5": q(a["winner_pct_emp"], 2.5),
        "winner_pct_emp_p97.5": q(a["winner_pct_emp"], 97.5),
        "winner_pct_theo_mean": float(np.mean(a["winner_pct_theo"])),
        "P_winner_top_decile": float(np.mean(a["winner_top_decile"])),
        "P_winner_T_gt_0.8": float(np.mean(a["winner_T_gt_08"])),
        "top10_median_T_pct_emp_mean": float(np.mean(a["top10_median_T_pct_emp"])),
        "top10_median_T_pct_emp_p2.5": q(a["top10_median_T_pct_emp"], 2.5),
        "top10_median_T_pct_emp_p97.5": q(a["top10_median_T_pct_emp"], 97.5),
        "top20_share_mean": float(np.mean(a["top20_share"])),
        "gini_mean": float(np.mean(a["gini"])),
        "persist_splithalf_all_mean": float(np.nanmean(a["persist_splithalf_all"])) if len(a["persist_splithalf_all"]) else None,
        "persist_splithalf_top100_mean": float(np.nanmean(a["persist_splithalf_top100"])) if len(a["persist_splithalf_top100"]) else None,
        "persist_y2y_top100_mean": float(np.nanmean(a["persist_y2y_top100"])) if len(a["persist_y2y_top100"]) else None,
        "n_runs": int(len(a["winner_T"])),
    }


def main():
    t0 = time.time()
    print(f"device={DEVICE}")
    baseline = run_block(1000, seed=1, pL=50, record_traj=True)
    bsum = summarize(baseline)
    # save full baseline per-run arrays for Block-C exceedance probabilities (§2)
    np.savez(os.path.join(RESULTS, "tvl_baseline_arrays.npz"),
             winner_pct_emp=baseline["winner_pct_emp"],
             winner_pct_theo=baseline["winner_pct_theo"],
             top10_median_T_pct_emp=baseline["top10_median_T_pct_emp"],
             winner_T=baseline["winner_T"], top20_share=baseline["top20_share"])
    print("baseline done", time.time() - t0)

    ladder = {}
    for pL in (20, 50, 80):
        a = run_block(250, seed=pL, pL=pL, record_traj=True)
        ladder[str(pL)] = summarize(a)
        print(f"ladder pL={pL} done", time.time() - t0)

    # integrity gate check
    gate = {}
    gate["winner_T_mean"] = (bsum["winner_T_mean"], QA_BANDS["winner_T_mean"],
                             abs(bsum["winner_T_mean"] - QA_BANDS["winner_T_mean"]["center"]) <= QA_BANDS["winner_T_mean"]["tol"])
    gate["winner_T_sd"] = (bsum["winner_T_sd"], QA_BANDS["winner_T_sd"],
                           abs(bsum["winner_T_sd"] - QA_BANDS["winner_T_sd"]["center"]) <= QA_BANDS["winner_T_sd"]["tol"])
    gate["top20pct_share"] = (bsum["top20_share_mean"], QA_BANDS["top20pct_share"],
                              abs(bsum["top20_share_mean"] - QA_BANDS["top20pct_share"]["center"]) <= QA_BANDS["top20pct_share"]["tol"])
    status = "PASS" if all(v[2] for v in gate.values()) else "FAIL"

    result = {
        "status": status,
        "engine": "/workspace/eval/replication/codebase/reimpl/tvl.py (faithful; shared-data/tvl-engine not staged)",
        "config": {"N": N, "NE": NE, "I": I, "C0": C0, "mT": mT, "sigmaT": sT,
                   "pL_baseline": 50, "top_decile_cut_T": TOP_DECILE_CUT},
        "baseline": bsum,
        "ladder": ladder,
        "integrity_gate_vs_staged_QA_bands": {k: {"value": v[0], "band": v[1], "pass": v[2]} for k, v in gate.items()},
        "paper_claims_for_reference": {"P_winner_T_gt_0.8_paper": 0.03,
                                       "winner_pct_paper_implied": 0.749,
                                       "top20_share_paper": 0.80},
        "runtime_sec": time.time() - t0,
    }
    write_json(os.path.join(RESULTS, "tvl_reference.json"), result)

    # also a flat CSV (tvl_reference.csv) with the reference rows
    import pandas as pd
    rows = [{"block": "baseline_pL50", **bsum}]
    for pL, s in ladder.items():
        rows.append({"block": f"pL{pL}", **s})
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS, "tvl_reference.csv"), index=False)

    print(json.dumps(result["integrity_gate_vs_staged_QA_bands"], indent=2))
    print("STATUS", status)
    print(json.dumps({"winner_pct_emp_mean": bsum["winner_pct_emp_mean"],
                      "P_winner_top_decile": bsum["P_winner_top_decile"],
                      "P_winner_T_gt_0.8": bsum["P_winner_T_gt_0.8"],
                      "top20_share_mean": bsum["top20_share_mean"],
                      "persist_y2y_top100_mean": bsum["persist_y2y_top100_mean"],
                      "persist_splithalf_all_mean": bsum["persist_splithalf_all_mean"]}, indent=2))
    if status == "PASS":
        done("G2")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
