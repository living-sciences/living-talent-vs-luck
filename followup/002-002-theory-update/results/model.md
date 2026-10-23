# The generalized Talent-vs-Luck model, written as a model (study 002)

## 1. The engine, with one pre-declared dial

The faithful TvL engine (replication `reimpl/tvl.py`) is extended by a **single
pre-declared talent-leverage dial** α. A lucky encounter now doubles capital with
probability

> **q_i = (1 − α)·q̄ + α·T_i**,  q̄ = 0.6 (= m_T, the population mean talent).

- **α = 1** → q_i = T_i → the paper's original model (nested exactly; the α=1 code
  path is **bit-identical** to the staged engine — gate 4, max abs diff 0.0).
- **α = 0** → q_i = 0.6 constant → pure luck, talent irrelevant.
- α mirrors Zappalà's per-point weight *a* in spirit (a=1 ⇒ only talent), but is a
  **career-level** leverage in the point-free TvL world (T2 binding note).

Everything else is unchanged: 201×201 toroidal world, N=1000 agents, N_E=500
events, I=80 steps, C0=10, truncated talent ~N(0.6,0.1). The only functional diff
vs the staged engine is the two lines computing `q` and `double_mask`
(`workspace/code/tvl_alpha.py`).

## 2. The calibration grid

11 α ∈ {0,0.1,…,1.0} × 5 p_L ∈ {20,35,50,65,80} × 100 runs = **5,500 runs**
(common random numbers: one seed per p_L shared across α, isolating the α effect),
plus the (α=1, p_L=50) anchor, which reproduces 001's `tvl_reference.csv`
**exactly** (gate 2: winner-pct 0.69642, P(top-decile) 0.269, top-20% share
0.77066, y2y persistence 0.95902 — all diff 0.00e+00 on the bit-identical
reproduction). Full grid: `results/calibration_grid.csv`.

**What the dial moves, and what it cannot.** Across the whole grid:

| model statistic | range over all 55 cells | moved by |
|---|---|---|
| winner skill percentile | **0.485 → 0.727** | α (talent leverage) |
| P(winner in top-talent decile) | 0.07 → 0.36 | α |
| success top-20% share | 0.647 → 0.832 | p_L (luck density) |
| success top-1% share | 0.217 → 0.425 | p_L |
| y2y top-100 persistence (PRIMARY) | **0.957 → 0.964** (essentially pinned) | ~nothing |

**Binding construct note (persistence).** The model's persistence entry is the
**y2y analogue** — top-100 capital-rank Spearman between consecutive one-year
(2-step) windows in the back half (t>40), averaged — because every domain series is
year-over-year. The split-half (t=40 vs t=80, 20-year-gap) statistic is computed
and reported as a **secondary** (`persist_splithalf_top100` in the grid) and never
enters the fit.

## 3. Per-domain fit (nearest grid cell, standardized L2) and the T1 falsification

Distance = standardized L2 over each domain's pre-declared (TvL-B1) statistic list,
standardized by 001's bootstrap SEs (`results/domain_targets.json`; share SEs
bootstrapped on reconstructed 001 success vectors — reconstructions match 001 to
<1e-6; persistence SEs bootstrapped over year-pair rhos; P(top-decile) without a
001 CI uses the binomial-proportion SE). Poker is **excluded** (TvL-A5: only a power
*statement* and a selection-biased descriptive row); MusicLab is **excluded**
(001's gated ELSE branch). Full table: `results/domain_fits.csv`.

| domain | fitted (α, p_L) | 1-SE neighbourhood | joint 3-SE fit | statistics that break in **every** grid cell |
|---|---|---|---|---|
| tennis | (1.0, 65) | {(1.0,65)} | **FAILS** | winner-skill pct (0.73 vs 0.994, −63σ); P(top-decile) (0.33 vs 0.667, −4σ); y2y persistence (0.96 vs 0.678, +11σ) |
| chess | (0.4, 50) | whole grid | **FAILS** | y2y persistence (0.96 vs 0.870, +10σ) |
| movies | (1.0, 65) | {(1.0,65)} | **FAILS** | top-20% share (0.83 vs 0.883, −37σ); winner-skill pct (0.73 vs 0.999, −458σ) |
| baseball | (0.3, 20) | {(0.3,20),(0.3,35)…} | **FAILS** | top-1% salary share (0.22 vs 0.082, +26σ); OPS y2y persistence (0.96 vs 0.493, +27σ) |

Fitted α's are **nearest cells of failed fits** — not calibrated parameters. The
pre-declared falsification clause fires for **all four** fitted domains: no (α,p_L)
in the family reproduces the domain's full signature list within 3 SE jointly.

**Two structural failures of the TvL family** (robust to the entire α×p_L grid):

1. **The model's winner is too mediocre.** Even at maximum talent leverage (α=1),
   the top-capital agent sits at only the ~0.49–0.73 talent percentile. Real top
   performers sit at the 0.99+ skill percentile (tennis 0.994, movies 0.999). The
   model's own signature — *top success ≠ top skill* — is the very thing the data
   contradict in tennis and movies; the dial cannot close the gap.
2. **The model's ranks are too sticky.** y2y top-100 persistence is pinned at ~0.96
   regardless of α or p_L, far above every real domain (chess 0.87 > tennis 0.68 >
   baseball 0.49). The model cannot produce the churn — nor the cross-domain
   ordering — seen in real year-over-year data.

Domain-specific breaks add detail: movies are **more** concentrated than the model's
ceiling (top-20% 0.883 > 0.832), while baseball salaries are **less** top-heavy than
the model's floor (top-1% 0.082 < 0.217).

## 4. The funding claim (C5) vs the real world — engine-vs-engine (TvL-B3)

Re-running the paper's 8-injection design on the α-engine (egalitarian ALL-EQUAL-1u
vs elitarian 25%-BEST-10u, 200 runs each, efficiency E = ΔP_T/F_T), the
egalitarian-beats-elitarian ordering holds at **every** α ∈ [0,1]
(`results/funding_comparison.csv`): egalitarian efficiency ≈ 9× elitarian, the gap
narrowing from +0.00466 (α=0) to +0.00435 (α=1) but **never flipping**.

- **Funding-claim robustness frontier: no flip-α in [0,1]** → model-internal verdict
  **"robust (no flip in [0,1])"**; card M3 reports **"no flip"**. fitted career α's
  (tennis 1.0, movies 1.0) both sit on the egalitarian-wins side.
- **Real side** (traced, `literature/PROVENANCE.md`): Bol et al. 2018† — real
  early-career funding is elitarian and causally Matthew (winners accrue >2× funding,
  ≈€180k, over 8 years), *consistent with the model's premise*; HRC NZ (Liu 2020) and
  SNSF (Heyard 2022) lotteries exist and are process-acceptable, but **no outcome RCT
  of lottery-vs-panel on later research success exists in the staged record through
  2026**.
- **P4 verdict word (M5): "untested but consistent"** — the ordering is robust across
  the fitted career α's and no staged outcome study contradicts it. What would
  falsify C5: a lottery-vs-panel outcome comparison at equal budget (e.g. a future
  HRC NZ / SNSF cohort study) showing merit-selected cohorts outperforming lottery
  cohorts on later success.

> **Caveat travelling with every citation of the paper's §3 funding table:** *the
> paper's unreleased experiment code evidently differed from the released demo; one
> F_T cell is an arithmetic error (70000→50000).* No §3 printed P_T/F_T value is used
> as a quantitative reference band anywhere in 002 — T3 is engine-vs-engine
> throughout.

## 5. Falsifiable predictions for the next tick (`results/predictions.json`)

1. **Tennis year-end-2026 top-100 persistence.** Model (fitted cell) band
   **[0.962, 0.964]**; the empirical series predicts ~**0.68** (2011–2025 range
   [0.49, 0.83]). Sign: the model over-predicts by ~0.28. Test: ATP year-end-2026
   top-100 rankings. The model is falsified if 2026 lands near 0.68, as the trend
   implies.
2. **Chess Jan-2027 minus tennis year-end-2026 top-100 persistence ≥ 0.10**
   (observed 2015–2026 gap 0.19). The model predicts ≈0 (both pinned at 0.96), so a
   persistent gap further falsifies the model's persistence channel. Test: FIDE Jan
   2027 top-100 vs ATP year-end 2026.
3. **2027 WSOP Main-Event repeat-champion count** within the no-skill null
   **E_0 = 0.0038** (= D=37 distinct prior champions / n≈9,735, 2025 field ±20% ⇒
   [7,788, 11,682]); 95% binomial null interval on the count = **{0}**. Predict **0**
   repeats. At ~9.7k-entrant fields the test has essentially no power (001's finding),
   so recurrence would only carry weight if the field shrank materially. (Replaces the
   bracelet permutation-null prediction — TvL-A5 demotion: no permutation null is
   computable from the staged data.)
4. **MusicLab winner-quality band — NOT issued:** 001 took the honest-exclusion ELSE
   branch (no staged MusicLab data), so the FULL branch condition is unmet.
