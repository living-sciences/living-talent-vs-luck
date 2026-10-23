# Study 002 — Theory update: fitting the Talent-vs-Luck engine to the measured signatures

## Question

Study 001 measured whether the Pluchino–Biondo–Rapisarda (2018) "Talent versus
Luck" model's four falsifiable signatures appear in the newest open data across
sports, entertainment, poker and science. This follow-up (002) asks what that
evidence implies **for the model itself**: (T1) can one TvL parameterization per
domain — the original engine plus a single pre-declared talent-leverage dial α —
jointly reproduce each domain's measured triple (concentration, winner-skill
decoupling, year-over-year persistence)? (T2) do the fitted luck/talent weights
agree with the 2018–2026 literature (Zappalà tennis *a*≈0.20–0.30; Janosov; Levitt–
Miles; Sobkowicz)? (T3) does the Section-3 funding claim (egalitarian beats
elitarian) survive contact with the post-2018 funding-lottery record and with
talent mattering more than in the baseline? (T4) a plain-language answer to the
reader's question, and (T5) ≥3 falsifiable next-tick predictions.

## Approach

**Reused from the completed replication and study 001 (fetched nothing):**
- the faithful TvL engine `reimpl/tvl.py` (fidelity established in the replication);
- 001's `signatures.csv`, `tvl_reference.csv`, `gates.json` and the per-domain JSONs
  for every target statistic and 001's bootstrap CIs;
- 001's b-block loaders (imported, not re-run) to reconstruct the per-entity success
  vectors needed for share-SE bootstraps; the reconstructed shares match 001 to
  <1e-6;
- 001's poker power-statement machinery, extended one year for prediction P3.

**Built for 002 (`workspace/code/`):**
- `tvl_alpha.py` — a thin wrapper around the staged engine adding the α-dial
  `q_i=(1−α)q̄+αT_i` (q̄=0.6). The **only** functional change vs the staged engine is
  the `q`/`double_mask` computation; all RNG draws keep their order, so α=1 is
  **bit-identical** to the unmodified engine (gate 4: max abs diff 0.0).
- `domain_targets.py` — assembles each domain's target statistics + standardization
  SEs (001 CI → SE; persistence → bootstrap over year-pair rhos; shares → bootstrap
  on reconstructed vectors; P(top-decile) without a CI → binomial-proportion SE).
- `t1_grid.py` — the 11×5×100 = 5,500-run calibration grid (CRN per p_L), +anchor.
- `t1_fit.py`, `t2_reconciliation.py`, `t3_funding.py`, `t5_predictions.py`,
  `gates.py`, `make_figs.py`.

All four **validation gates pass** (`results/gates_002.json`): (1) 001 completed &
G1–G3 passed; (2) the (α=1,p_L=50) anchor reproduces `tvl_reference.csv` exactly
(diff 0.00e+00 on the bit-identical 1000-run reproduction; the independent grid cell
agrees within Monte-Carlo CI); (3) every literature number traces to
`PROVENANCE.md` with its verification level (abstract-verified carry †); (4) α=1
bit-identical.

## Results

### T1 — the TvL family cannot jointly reproduce any domain's signature triple

The α-dial moves the winner's skill percentile (0.49→0.73) and P(top-decile)
(0.07→0.36); p_L moves concentration (top-20% 0.65→0.83); **y2y persistence is
pinned at ~0.96 across the entire grid**. Fitting each domain to its nearest cell
(standardized L2) and applying the pre-declared 3-SE joint test:

| domain | fitted (α, p_L) | joint 3-SE fit | structurally unreachable statistics (break in every cell) |
|---|---|---|---|
| tennis | (1.0, 65) | **FAILS** | winner-skill pct −63σ; P(top-decile) −4σ; y2y persistence +11σ |
| chess | (0.4, 50) | **FAILS** | y2y persistence +10σ |
| movies | (1.0, 65) | **FAILS** | winner-skill pct −458σ; top-20% share −37σ |
| baseball | (0.3, 20) | **FAILS** | top-1% salary share +26σ; OPS y2y persistence +27σ |

Two **structural failures** survive the whole α×p_L grid:
1. **Winners too mediocre.** Model winner ≤ 0.73 skill percentile even at α=1; real
   top performers ≥ 0.99 (tennis 0.994, movies 0.999). The model's own *top-success
   ≠ top-skill* signature is exactly what tennis and movies contradict.
2. **Ranks too sticky.** Model y2y persistence ~0.96 everywhere; real 0.49–0.87, and
   ordered chess > tennis > baseball — an ordering the flat model cannot produce.

Domain detail: movies are **more** concentrated than the model's ceiling (0.883 >
0.832); baseball salaries are **less** top-heavy than its floor (0.082 < 0.217).
`results/domain_fits.csv`, `results/calibration_grid.csv`,
`results/fig_fit_map.png`, `results/fig_structural_gap.png`.

#### Comparison to the study-001 / replication baseline

| quantity | model baseline (α=1, p_L=50) | 002 grid reachable range | real-domain measurement (001) | source of baseline |
|---|---|---|---|---|
| winner skill percentile | 0.696 | 0.485 – 0.727 | tennis 0.994, movies 0.999, baseball 1.0 | `tvl_reference.csv` / `signatures.csv` |
| P(winner in top decile) | 0.269 | 0.07 – 0.36 | tennis 0.667, movies 0.204, baseball 0.419 | `tvl_reference.csv` |
| success top-20% share | 0.771 | 0.647 – 0.832 | tennis 0.639, movies 0.883, baseball 0.637 | `tvl_reference.csv` |
| success top-1% share | 0.347 | 0.217 – 0.425 | movies 0.309, baseball 0.082 | 001 grid (anchor) |
| y2y top-100 persistence | 0.959 | 0.957 – 0.964 | chess 0.870, tennis 0.678, baseball 0.493 | `tvl_reference.csv` |

The baseline numbers reproduce 001 exactly (gate 2). The new content is the *range*
column: it shows the signatures are not reachable by **any** member of the α-dial
family, not just the baseline parameterization 001 already rejected.

### T2 — reconciliation (same-construct comparisons only)

`results/reconciliation.csv`. Our career-level fitted α (tennis 1.0, movies 1.0,
chess 0.4, baseball 0.3) sit beside Zappalà 2023 tennis *a*≈0.20–0.30 (per-point
weight in a tournament ABM), Janosov 2020 (impact-decomposition, no ex-ante skill —
qualitative only), Levitt–Miles 2014† (skilled ROI +30.5% vs −15.6%), Sobkowicz
2020 (a small non-zero sprint luck floor). **Binding note:** our tennis α is a
career-level leverage in the point-free engine; Zappalà's *a* is a per-point weight.
They are not the same parameter, and they disagree in the informative direction —
points are luck-dominated (low *a*) yet careers aggregate skill, pushing the
career-level leverage to its ceiling (α=1): the **aggregation paradox**, not a
contradiction. *(Deviation: Csurilla et al. 2023, named in the T2 spec, is absent
from the staged `PROVENANCE.md`; it is recorded direction-only with no cited number,
keeping gate 3 clean.)*

### T3 — the funding claim survives, but remains untested against reality

Engine-vs-engine (TvL-B3; **no §3 printed value used as a reference band**):
egalitarian (ALL-EQUAL-1u) beats elitarian (25%-BEST-10u) on efficiency at **every**
α ∈ [0,1] — efficiency ≈ 9× higher, gap +0.00466 (α=0) → +0.00435 (α=1), **no flip**
(`results/funding_comparison.csv`, `results/fig_funding_frontier.png`). So the
claim is **robust** to the talent-leverage dial (M3: no flip). Against reality: real
funding is elitarian and causally Matthew (Bol 2018†), and lotteries exist and are
acceptable (HRC NZ, SNSF) but have **no outcome RCT** through 2026 → **P4 verdict:
"untested but consistent"**. Falsifier of C5: a future equal-budget lottery-vs-panel
cohort study showing merit beats lottery on later success.

> Caveat travelling with the §3 table: *the paper's unreleased experiment code
> evidently differed from the released demo; one F_T cell is an arithmetic error
> (70000→50000).*

### T4 — answer to the reader (sports, entertainment, poker, science/funding)

**Sports.** The model's signature claim — the most successful are rarely the most
skilled — does **not** corroborate. Tennis's all-time title leader sits at the 99.4th
percentile of independently measured skill (001), and no setting of the generalized
engine, even maximum talent-leverage α=1, lifts its winner above the ~73rd
percentile; baseball's small skill panel is too noisy to decide, but its salary
top-1% share (0.082) is *less* top-heavy than any model cell. The real persistence
ladder chess > tennis > baseball is genuine, but the engine's capital ranks are far
too sticky (~0.96) to reproduce any of those three or their ordering.

**Entertainment.** Same verdict: the most-voted film sits at the 99.9th percentile of
its rating proxy and movie success is more concentrated (top-20% 0.883) than the
model can reach (≤0.832) — the engine's "lucky mediocrity wins" picture does not
match films either.

**Poker.** Undecided by design: at modern ~9.7k-entrant Main-Event fields the
no-skill null (E_0≈0.31 repeat champions) and a 5× skill multiple (E_5≈1.12) are
statistically indistinguishable (observed repeats 0); poker's luck weight rests on
Levitt–Miles 2014† (skilled ROI +30.5% vs −15.6%), consistent with α>0 but not a
fitted weight.

**Science / funding.** The model's egalitarian-beats-elitarian efficiency claim is
robust across the whole talent-leverage range (no flip) and is *untested but
consistent* with reality — real funding is Matthew-like (Bol 2018†) and funding
lotteries are deemed acceptable, but no study has yet compared lottery vs panel on
later research outcomes.

### T5 — three falsifiable next-tick predictions

1. **Tennis year-end-2026 top-100 persistence:** model band [0.962, 0.964] vs
   empirical ~0.68 (range [0.49, 0.83]); the model over-predicts by ~0.28. Test: ATP
   year-end-2026 rankings.
2. **Chess Jan-2027 − tennis year-end-2026 top-100 persistence ≥ 0.10** (observed
   gap 0.19; model predicts ≈0). Test: FIDE Jan 2027 vs ATP year-end 2026.
3. **2027 WSOP Main-Event repeat-champion count = 0**, within the no-skill null
   E_0=0.0038 (D=37, n≈9,735 ±20%), 95% binomial null interval {0}. Test: next
   poker_events row.
(4 — MusicLab — not issued: 001's gated ELSE branch.)

## Deviations & limitations

- **T1 falsification is the result, not a failure.** The pre-declared clause (no cell
  fits all stats within 3 SE) fires for all four fitted domains; this is a finding
  against the TvL family's *sufficiency*, reported as such.
- **Fitted α's are nearest cells of failed fits**, not calibrated parameters; T2/T3
  use them only where the spec directs (reconciliation rows; funding career-α's).
- **Standardization SEs** combine four pre-declared sources (001 CI; year-pair
  bootstrap; share bootstrap on reconstructed vectors; binomial-proportion SE for
  P(top-decile) without a CI). Large-n domains (movies) therefore have very small
  share SEs, making those statistics near-hard constraints — this is the intended
  pre-declared standardization, and the falsification verdicts for the *structural*
  breaks (winner-skill, persistence) hold by tens of SEs regardless of SE choice.
- **CRN grid:** 100 replicates/cell share one seed per p_L across α (variance
  reduction, isolates α); the anchor cell still reproduces 001 within MC CI, and the
  dedicated bit-identical 1000-run reproduction matches 001 exactly.
- **Csurilla et al. 2023** (T2) is absent from the staged `PROVENANCE.md`; included
  direction-only with no cited number (deviation, gate-3-clean).
- **Poker & MusicLab excluded from T1** per TvL-A5 and the gated-branch rule.
- Engine substitution (`shared-data/tvl-engine/` not staged → faithful replication
  engine) is inherited from 001 and recorded there; the α=1 bit-identity check
  confirms the substitution is sound.
- **Truncation deviation (inherited from 001-2, declared at 003 audit-conformance):**
  Spec §5 Block A G2 says "no truncation", but 001's G2 model-reference run used
  `truncate_talent=True`, chosen for construct-consistency with the staged QA
  distcheck anchor bands (computed with truncation ON; clips ~3e-5 of talent draws,
  numerically immaterial). 002's α-dial grid and anchor inherit this setting and are
  bit-identical to 001's baseline at α=1, so the deviation carries through unchanged.
- No new data fetched; no model extension beyond the single pre-declared α-dial.
