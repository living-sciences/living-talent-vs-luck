# Follow-up 001 — Living update: Talent-vs-Luck signatures vs the newest open data

## Question

Pluchino, Biondo & Rapisarda's *Talent versus Luck* (2018) argues that a Gaussian
spread of talent plus multiplicative luck produces a fat-tailed, 80/20
distribution of success in which **the most successful are almost never the most
talented**. A reader asked, through the site: *do the model's findings corroborate
with real-world data in different domains — e.g. sports, entertainment, poker?*
This study answers by testing the model's four pre-declared, falsifiable
signatures against the newest open data in **tennis, chess, baseball, movies,
science and poker** (plus a gated MusicLab branch), using **independent ex-ante
skill proxies** and the paper's own faithful engine as the model-side reference.
The test is designed to be able to fail, and "signature absent" is a first-class
reportable outcome.

## Approach

**Reused from the replication:** the faithful, GPU-batched TvL engine
(`/workspace/eval/replication/codebase/reimpl/tvl.py`), whose fidelity to the
shipped NetLogo model the replication established (10,000-run winner-talent mean
0.670, sd 0.093). Nothing from the original pipeline was re-run except the engine,
and only to produce the model-side reference distributions this study needs.

**New work.** Block A gates: **G1** sha256-verified all 126 staged files and
checked coverage; **G2** ran 1,000 baseline engine runs + a p_L={20,50,80} ladder
to derive the model-side reference distributions; **G3** computed each domain's
proxy-validity row. Block B computed the P1/P2/S1 statistics per domain with
bootstrap CIs. Block C assembled the cross-domain signature table, the ordering
test, the model-side exceedance probabilities, and three figures. All code is
under `workspace/code/`; all outputs under `results/`.

**Deviations (full list in `followup_summary.json`).** `shared-data/tvl-engine/`,
`qa-distcheck/distcheck_results.json`, and `recency-research.md` were not separately
staged; the faithful replication engine was used for G2 and the integrity-band /
pass-fail constants were taken from the centers quoted verbatim in the spec. "Seeds
1..1000" were realized as independent batched replicates under fixed master seeds.

## Results

### Gates
- **G1 PASS** — 126/126 sha256 match; tennis 2025 complete (2,944 matches), FIDE
  Jan-2026 531,422 rated, Lahman Teams max year 2025, 49,346 IMDb movies at the
  votes cut, poker champions 1970–2026.
- **G2 PASS** — integrity bands met (winner-talent mean 0.6696 ∈ 0.6686±0.01; sd
  0.0918 ∈ 0.0932±0.015; top-20% capital share 0.7707 ∈ 0.774±0.02). Run-produced
  references: winner **skill percentile 0.696** (paper-implied 0.749),
  **P(winner top-decile) 0.269**, **P(winner T>0.8) 0.078**, **top-20% capital
  share 0.771**, **y2y persistence 0.959**.
- **G3 PASS** in all three P2 domains (tennis split-half 0.959 ≥ persistence 0.678;
  baseball exit-velo y2y 0.756 & sprint 0.932 ≥ OPS 0.493; movies within-decile
  |ρ| 0.023 ≤ 0.2).

### Paper-text-vs-code (C22)
The released engine, run faithfully, gives **P(winner talent > 0.8) ≈ 7.8%** (QA
audit 8.0%; 13,700 runs), **not the paper's printed 3%** — the printed value is
distributionally inconsistent with the paper's own code. Throughout, the printed
3% / 0.80 / 0.749 are treated as the paper's *claims*; the G2 run-produced values
are the references.

### The four signatures

| Signature | Result |
|---|---|
| **P1 shape** | **present** in all 4 domains with a concentration measure (success top-20% share: tennis 0.639 *threshold-sensitive*, movies 0.883, science 0.928, baseball salary 0.637), from near-symmetric skill — but *consistent with any multiplicative mechanism*, not evidence for the model's mechanism. |
| **P2 decoupling** | **absent** in tennis (winner skill pct **0.994** [0.984,1.000], top-10 median 0.981) and movies (0.999 / 0.997): top success coincides with top measured skill — the model's *talent-dominated corner*. **Uninformative** in baseball (point estimate 1.0 but CI [0.40,1.00]). The tennis/movie configurations occur in **≤1.3% / 0%** of model baseline runs. |
| **P3 ordering** | **partial** — the persistence ladder reproduces the pre-declared **chess 0.870 > tennis 0.678 > baseball 0.493** exactly, but decoupling does *not* order with luck (winner-skill pct ~1.0 everywhere). Poker's luck-end placement is literature-based (Levitt-Miles 2014), not counted. |
| **P4 funding** | model-side ladder only; no real-world funding verdict (study 002). |

### Comparison to the model-side reference

| Quantity | Real data | Model (G2) | Paper claim |
|---|---|---|---|
| #1-success skill percentile (tennis) | 0.994 | 0.696 | 0.749 |
| top-success in top-skill decile | tennis 0.67 / movies 0.20 (conditional) | 0.269 | 0.03 |
| success top-20% share | 0.64–0.93 | 0.771 (capital) | 0.80 |
| elite persistence ladder | chess 0.870 > tennis 0.678 > baseball 0.493 | 0.959 (y2y) | — |
| P(winner T>0.8) | — | 0.078 | 0.03 |

### Poker power statement (verbatim)
> Under a no-skill null with field sizes n_t, the expected number of repeat
> Main-Event champions 1990-2025 is E_0 = 0.315; under a uniform 5× skill multiple
> for a 10% skilled stratum it is E_5 = 1.124. The observed count is 0. With
> E_5 − E_0 = 0.809 expected events, this comparison cannot distinguish the
> hypotheses.

### Figures
- `fig_decoupling.png` — winner & top-10 skill percentiles per domain vs the TvL
  baseline band; every measured domain sits in the talent-dominated corner.
- `fig_ordering.png` — persistence vs decoupling, with the TvL p_L ladder overlaid.
- `fig_shapes.png` — fat-tailed success concentration vs the egalitarian 0.20 line.

### Answer to the reader
The model's **shape** result corroborates broadly (a few win almost everything,
from modest skill spreads) — but that follows from almost any multiplicative
process and is not evidence for the model's mechanism. The model's **signature**
result — that the most successful are almost never the most skilled — does **not**
corroborate: in tennis and movies (and in the baseball point estimate) the top
performers sit at the very top of independently measured skill, a configuration the
faithful engine produces in ~1% or fewer of its baseline runs. The cross-domain
persistence ordering behaves as the skill-luck intuition predicts, but does not
translate into the top-level decoupling the model's baseline requires.

## Prior art (binding)
Not the first talent-vs-luck test, luck-vs-ability decomposition, or sports test.
Closest prior art: Janosov–Battiston–Sinatra (2020); the authors' own tennis
calibration Zappalà et al. (2023, talent weight a≈0.20–0.30); and **Biondo–Pluchino
SSRN 6572147 (2026), concurrent and not yet read (metadata-verified; bot-blocked)**
— a human should read it before external publication. New here: independent ex-ante
proxies against TvL's quantitative winner-percentile signature; the cross-domain
ordering with a skill-dominated control; the funding confrontation (in 002).

## Deviations & limitations
See `results/findings.md` for the full proxy-limitation table. Principal caveats:
the tennis point-share proxy is independent in grain but not ex-ante (controlled by
a finals-excluded leakage test, which agrees); the baseball Statcast-era success
panel is small (n≈430) giving wide P2 CIs; movie rating is the weakest proxy
(confound controlled within votes-decile); science and poker contribute
concentration/literature only. The three unstaged engine/QA/recency files were
substituted as described above. Everything pre-declared ran; nothing was dropped
for time (total compute well under one core-hour; G2 the heaviest at ~2 min/1000
runs on a shared GPU).
