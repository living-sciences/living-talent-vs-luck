#!/usr/bin/env python3
"""Study 002 engine extension: the single pre-declared TALENT-LEVERAGE DIAL (alpha).

This is a thin WRAPPER around the staged faithful engine
    /workspace/eval/replication/codebase/reimpl/tvl.py
It reuses that module's `apply_funding` and world constant `W` verbatim, and
reimplements ONLY `simulate_batch` with one changed line so that a lucky hit now
succeeds with probability

    q_i = (1 - alpha) * qbar + alpha * T_i        (qbar = 0.6 = population mean talent)

  * alpha = 1.0  ->  q_i = T_i                 (the paper's original model; NESTED)
  * alpha = 0.0  ->  q_i = qbar = 0.6          (pure luck: talent irrelevant)

DIFF vs the staged tvl.simulate_batch (the ONLY functional change):

    - double_mask = lucky_hit & (r < talent)
    + q = (1.0 - alpha) * qbar + alpha * talent
    + double_mask = lucky_hit & (r < q)

Every RNG draw (talent, agent/event positions, headings, selection keys, the
Bernoulli draw r) is issued in the IDENTICAL order and shape as the staged
engine, so at alpha == 1.0 the stream and all outputs are BIT-IDENTICAL in
expectation to the unmodified engine.  `assert_alpha1_bit_identical` checks this
on one seed (validation gate 4).
"""
import os, sys
import numpy as np
import torch

# Import the staged faithful engine and reuse its primitives verbatim.
_STAGED = "/workspace/eval/replication/codebase/reimpl"
if _STAGED not in sys.path:
    sys.path.insert(0, _STAGED)
import tvl as _staged                      # noqa: E402
from tvl import apply_funding, W           # noqa: E402  (reused verbatim)

QBAR = 0.6  # population mean talent m_T (pre-declared leverage anchor)


def simulate_batch(R, N, NE, I, mT, sigmaT, pL, C0=10.0, device="cpu", seed=0,
                   truncate_talent=True, funding=None, record_traj=False,
                   alpha=1.0):
    """alpha-generalized copy of tvl.simulate_batch. alpha==1.0 reproduces the
    staged engine bit-for-bit (same RNG draw order)."""
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
        within = d2 <= 1.0 + 1e-9
        has = within.any(dim=2)

        key = torch.rand(R, N, NE, generator=g, device=device)
        key = torch.where(within, key, torch.full_like(key, float("inf")))
        sel = key.argmin(dim=2)
        sel_lucky = torch.gather(lucky, 1, sel)

        lucky_hit = has & sel_lucky
        unlucky_hit = has & (~sel_lucky)
        nlucky += lucky_hit.float()
        nunlucky += unlucky_hit.float()

        r = torch.rand(R, N, generator=g, device=device)
        # ---- THE ONLY FUNCTIONAL CHANGE vs staged tvl.simulate_batch ----
        q = (1.0 - alpha) * QBAR + alpha * talent
        double_mask = lucky_hit & (r < q)
        # -----------------------------------------------------------------
        success = torch.where(double_mask, success * 2.0, success)
        success = torch.where(unlucky_hit, success * 0.5, success)

        if step in fund_steps:
            success, inv = apply_funding(success, talent, funding, step, g, device)
            invested = invested + inv

        if record_traj:
            traj[:, :, step] = success

    return dict(talent=talent, success=success, nlucky=nlucky, nunlucky=nunlucky,
                traj=traj, invested=invested)


def assert_alpha1_bit_identical(device="cpu", seed=12345):
    """Validation gate 4: alpha==1.0 path reproduces the staged engine exactly."""
    cfg = dict(R=8, N=1000, NE=500, I=80, mT=0.6, sigmaT=0.1, pL=50)
    a = _staged.simulate_batch(cfg["R"], cfg["N"], cfg["NE"], cfg["I"], cfg["mT"],
                               cfg["sigmaT"], cfg["pL"], device=device, seed=seed,
                               truncate_talent=True)
    b = simulate_batch(cfg["R"], cfg["N"], cfg["NE"], cfg["I"], cfg["mT"],
                       cfg["sigmaT"], cfg["pL"], device=device, seed=seed,
                       truncate_talent=True, alpha=1.0)
    out = {}
    for k in ("talent", "success", "nlucky", "nunlucky"):
        eq = bool(torch.equal(a[k], b[k]))
        maxdiff = float((a[k] - b[k]).abs().max().item())
        out[k] = {"bit_identical": eq, "max_abs_diff": maxdiff}
    out["ALL_BIT_IDENTICAL"] = all(v["bit_identical"] for v in out.values()
                                   if isinstance(v, dict))
    return out


if __name__ == "__main__":
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    import json
    res = assert_alpha1_bit_identical(device=dev)
    print(json.dumps(res, indent=2))
    assert res["ALL_BIT_IDENTICAL"], "alpha=1 path is NOT bit-identical to staged engine"
    print("GATE 4 PASS: alpha=1.0 path bit-identical to staged tvl.simulate_batch")
