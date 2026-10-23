#!/usr/bin/env python3
"""Faithful, vectorized (torch, GPU-batched) reimplementation of the Pluchino-
Biondo-Rapisarda "Talent vs Luck" NetLogo model (arXiv 1802.07068).

Mirrors the shipped NetLogo rules (official_comses_tvl_v1.0.0/code/TvLmodel.nlogo):
  * World: 201x201 patches, coords 0..200, TOROIDAL / wrapping (empirically
    confirmed via BehaviorSpace: [distance patch 199 199] of patch 1 1 = 4.2426,
    i.e. torus period 201 -- see suspicions S1; the paper's periodic boundary).
  * Agents sprout on interior patch centres (integer coords 1..199); they never
    move.  N_E event-points also start on interior patch centres; each is tagged
    "lucky" with prob %-lucky/100, else "unlucky".
  * Each of I steps: every event sets heading = (random 360) deg and does fd 2
    (continuous move, wrapped mod 201).  Then every agent that has >=1 event
    within radius 1 picks ONE such event uniformly at random (NetLogo
    `one-of events in-radius 1`, suspicion S3) and:
        lucky   -> n-lucky +1 ;  if random-float 1 < talent: success *= 2
        unlucky -> n-unlucky+1 ;  success /= 2
  * C(0) = initial-success = 10.

Deviations from the shipped demo, documented:
  * truncate_talent (default True) clips talent to [0,1] as the PAPER states
    ("talent ... truncated in the interval [0,1]").  The shipped demo does NOT
    clip (suspicion S2); the self-test uses truncate_talent=False to match the
    demo and isolate structural/RNG differences.
  * Initial positions are sampled i.i.d. uniform on interior integer coords
    (1..199) WITH replacement; NetLogo's n-of draws DISTINCT patches.  With
    N=1000 / N_E=500 over 199*199=39601 patches, collisions are rare and agents
    are dynamically independent, so the effect is negligible (recorded here).
"""
import argparse, json, os
import numpy as np
import torch

W = 201.0  # torus period (patches 0..200)


def apply_funding(success, talent, funding, step, g, device):
    """Inject capital at an injection step. `funding` is a dict:
        kind: 'equal' | 'random' | 'best' | 'best_others'
        units: units per selected agent (for equal/random/best)
        frac: fraction selected (for random/best)
        best_units, others_units: for 'best_others'
        best_frac: fraction for 'best_others'
    Capital/success units are ADDED to success.  Returns new success and the
    total units injected this step (per run, scalar tensor shape (R,))."""
    R, N = success.shape
    kind = funding['kind']
    if kind == 'equal':
        u = funding['units']
        success = success + u
        invested = torch.full((R,), float(u * N), device=device)
    elif kind == 'random':
        u = funding['units']; frac = funding['frac']
        k = int(round(frac * N))
        key = torch.rand(R, N, generator=g, device=device)
        idx = key.argsort(dim=1)[:, :k]
        add = torch.zeros(R, N, device=device)
        add.scatter_(1, idx, u)
        success = success + add
        invested = torch.full((R,), float(u * k), device=device)
    elif kind == 'best':
        u = funding['units']; frac = funding['frac']
        k = int(round(frac * N))
        idx = success.argsort(dim=1, descending=True)[:, :k]
        add = torch.zeros(R, N, device=device)
        add.scatter_(1, idx, u)
        success = success + add
        invested = torch.full((R,), float(u * k), device=device)
    elif kind == 'best_others':
        bu = funding['best_units']; ou = funding['others_units']; bf = funding['best_frac']
        k = int(round(bf * N))
        order = success.argsort(dim=1, descending=True)
        best_idx = order[:, :k]; other_idx = order[:, k:]
        add = torch.zeros(R, N, device=device)
        add.scatter_(1, best_idx, bu)
        add.scatter_(1, other_idx, ou)
        success = success + add
        invested = torch.full((R,), float(bu * k + ou * (N - k)), device=device)
    else:
        raise ValueError(kind)
    return success, invested


def simulate_batch(R, N, NE, I, mT, sigmaT, pL, C0=10.0, device="cpu", seed=0,
                   truncate_talent=True, funding=None, record_traj=False):
    """Run R independent replicates in parallel on `device`. Returns dict of
    tensors: talent,success,nlucky,nunlucky each (R,N); traj (R,N,I+1) or None;
    invested (R,) total funding units injected."""
    device = torch.device(device)
    g = torch.Generator(device=device); g.manual_seed(int(seed))

    talent = mT + sigmaT * torch.randn(R, N, generator=g, device=device)
    if truncate_talent:
        talent = talent.clamp(0.0, 1.0)
    success = torch.full((R, N), float(C0), device=device)
    nlucky = torch.zeros(R, N, device=device)
    nunlucky = torch.zeros(R, N, device=device)
    invested = torch.zeros(R, device=device)

    ax = torch.randint(1, 200, (R, N), generator=g, device=device).float()
    ay = torch.randint(1, 200, (R, N), generator=g, device=device).float()
    ex = torch.randint(1, 200, (R, NE), generator=g, device=device).float()
    ey = torch.randint(1, 200, (R, NE), generator=g, device=device).float()
    lucky = torch.rand(R, NE, generator=g, device=device) < (pL / 100.0)

    traj = None
    if record_traj:
        traj = torch.empty(R, N, I + 1, device=device)
        traj[:, :, 0] = success

    fund_steps = set(funding['steps']) if funding is not None else set()

    for step in range(1, I + 1):
        heading = torch.randint(0, 360, (R, NE), generator=g, device=device).float() * (np.pi / 180.0)
        ex = torch.remainder(ex + 2.0 * torch.sin(heading), W)
        ey = torch.remainder(ey + 2.0 * torch.cos(heading), W)

        dx = ax[:, :, None] - ex[:, None, :]
        dy = ay[:, :, None] - ey[:, None, :]
        dx = dx - W * torch.round(dx / W)
        dy = dy - W * torch.round(dy / W)
        d2 = dx * dx + dy * dy
        within = d2 <= 1.0 + 1e-9                     # (R,N,NE)
        has = within.any(dim=2)                       # (R,N)

        key = torch.rand(R, N, NE, generator=g, device=device)
        key = torch.where(within, key, torch.full_like(key, float("inf")))
        sel = key.argmin(dim=2)                        # (R,N) index of chosen event
        sel_lucky = torch.gather(lucky, 1, sel)        # (R,N) bool

        lucky_hit = has & sel_lucky
        unlucky_hit = has & (~sel_lucky)
        nlucky += lucky_hit.float()
        nunlucky += unlucky_hit.float()

        r = torch.rand(R, N, generator=g, device=device)
        double_mask = lucky_hit & (r < talent)
        success = torch.where(double_mask, success * 2.0, success)
        success = torch.where(unlucky_hit, success * 0.5, success)

        if step in fund_steps:
            success, inv = apply_funding(success, talent, funding, step, g, device)
            invested = invested + inv

        if record_traj:
            traj[:, :, step] = success

    return dict(talent=talent, success=success, nlucky=nlucky, nunlucky=nunlucky,
                traj=traj, invested=invested)


def run(N, N_E, I, m_T, sigma_T, p_L, C0=10.0, seed=0, funding=None,
        device="cpu", truncate_talent=True, record_traj=False):
    """Single run; returns numpy arrays (and trajectory if requested)."""
    out = simulate_batch(1, N, N_E, I, m_T, sigma_T, p_L, C0=C0, device=device,
                          seed=seed, truncate_talent=truncate_talent,
                          funding=funding, record_traj=record_traj)
    res = dict(talent=out["talent"][0].cpu().numpy(),
               success=out["success"][0].cpu().numpy(),
               nlucky=out["nlucky"][0].cpu().numpy().astype(int),
               nunlucky=out["nunlucky"][0].cpu().numpy().astype(int))
    if record_traj:
        res["traj"] = out["traj"][0].cpu().numpy()
    return res


def _selftest(compare_csv, device):
    import pandas as pd
    cfg = dict(N=1000, N_E=500, I=80, m_T=0.6, sigma_T=0.1, p_L=50)
    # Match the shipped demo exactly: no talent truncation.
    r1 = run(cfg["N"], cfg["N_E"], cfg["I"], cfg["m_T"], cfg["sigma_T"], cfg["p_L"],
             seed=1, device=device, truncate_talent=False)
    # Ensemble for stable means.
    ens = simulate_batch(40, cfg["N"], cfg["N_E"], cfg["I"], cfg["m_T"], cfg["sigma_T"],
                         cfg["p_L"], device=device, seed=7, truncate_talent=False)
    ens_nl = ens["nlucky"].mean().item(); ens_nu = ens["nunlucky"].mean().item()
    ens_maxl = ens["nlucky"].max().item(); ens_maxu = ens["nunlucky"].max().item()

    nl = pd.read_csv(compare_csv)
    nl = nl.rename(columns={"n-lucky-events": "nlucky", "n-unlucky-events": "nunlucky"})
    nlf = nl[nl.time == nl.time.max()]

    def qsummary(c):
        lg = np.log2(np.asarray(c) / 10.0)
        qs = np.percentile(lg, [0, 10, 25, 50, 75, 90, 100])
        return qs

    cmp = {
        "config": cfg,
        "netlogo": {
            "mean_lucky": float(nlf.nlucky.mean()), "mean_unlucky": float(nlf.nunlucky.mean()),
            "max_lucky": int(nlf.nlucky.max()), "max_unlucky": int(nlf.nunlucky.max()),
            "success_log2_quantiles": qsummary(nlf.success).tolist(),
            "frac_neutral": float(((nlf.nlucky == 0) & (nlf.nunlucky == 0)).mean()),
            "C_max": float(nlf.success.max()), "C_min": float(nlf.success.min()),
        },
        "reimpl_single": {
            "mean_lucky": float(r1["nlucky"].mean()), "mean_unlucky": float(r1["nunlucky"].mean()),
            "max_lucky": int(r1["nlucky"].max()), "max_unlucky": int(r1["nunlucky"].max()),
            "success_log2_quantiles": qsummary(r1["success"]).tolist(),
            "frac_neutral": float(((r1["nlucky"] == 0) & (r1["nunlucky"] == 0)).mean()),
            "C_max": float(r1["success"].max()), "C_min": float(r1["success"].min()),
        },
        "reimpl_ensemble40": {
            "mean_lucky": ens_nl, "mean_unlucky": ens_nu,
            "max_lucky": ens_maxl, "max_unlucky": ens_maxu,
        },
    }
    os.makedirs("outputs/fidelity", exist_ok=True)
    with open("outputs/fidelity/compare.json", "w") as f:
        json.dump(cmp, f, indent=2)

    print("=== FIDELITY: reimpl vs NetLogo (single-run config N=1000 NE=500 I=80 mT=0.6 sT=0.1 pL=50) ===")
    print(f"{'metric':28s} {'NetLogo':>12s} {'reimpl(1run)':>14s} {'reimpl(40-ens)':>16s}")
    n, s, e = cmp["netlogo"], cmp["reimpl_single"], cmp["reimpl_ensemble40"]
    for k, ek in [("mean_lucky", "mean_lucky"), ("mean_unlucky", "mean_unlucky"),
                  ("max_lucky", "max_lucky"), ("max_unlucky", "max_unlucky")]:
        print(f"{k:28s} {n[k]:>12.3f} {s[k]:>14.3f} {e[ek]:>16.3f}")
    print(f"{'frac_neutral':28s} {n['frac_neutral']:>12.3f} {s['frac_neutral']:>14.3f} {'-':>16s}")
    print(f"{'C_max':28s} {n['C_max']:>12.1f} {s['C_max']:>14.1f}")
    print(f"{'C_min':28s} {n['C_min']:>12.5f} {s['C_min']:>14.5f}")
    print("success log2(C/10) quantiles [0,10,25,50,75,90,100]:")
    print("  NetLogo:", [round(x, 2) for x in n["success_log2_quantiles"]])
    print("  reimpl :", [round(x, 2) for x in s["success_log2_quantiles"]])
    print("wrote outputs/fidelity/compare.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--compare", default=None)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()
    if args.selftest:
        _selftest(args.compare, args.device)
