# Living update (study 001): the Talent-vs-Luck signatures against the newest open data

**Reader question.** Do the model's findings corroborate with real-world data in
different domains — sports, entertainment, poker (and science/funding, where the
paper's Section 3 lives)? This study tests the model's four pre-declared
signatures P1–P4 against the newest open data (tennis through 2025, FIDE Jan
2015–2026, Lahman through 2025, Statcast 2015–2026, IMDb 2026-10-22, OpenAlex
live, Wikipedia pinned revids), using independent ex-ante skill proxies and the
faithful engine as the model-side reference.

## Prior art (binding positioning)

This is **not** the first empirical talent-vs-luck test, the first luck-vs-ability
decomposition, or the first sports test. The closest multi-domain decomposition is
**Janosov, Battiston & Sinatra (2020, EPJ Data Science 9:9)**; the authors' own
tennis calibration is **Zappalà, Biondo, Pluchino & Rapisarda (2023, Chaos
Solitons & Fractals 176:114088)**, which fits a per-point talent weight *a ≈
0.20–0.30*; and **Biondo & Pluchino, "When Talent Is Not Enough: Superstar
Careers in the Arts," SSRN 6572147 (2026)** is the authors' **concurrent and not
yet read (metadata-verified; bot-blocked)** careers paper (a human should read it
before any external publication). What **is** new here: independent ex-ante skill
proxies tested against TvL's *quantitative* winner-percentile signature; the
cross-domain ordering with a skill-dominated control (chess); and the funding
confrontation (the latter deferred to study 002).

## Method

The faithful TvL engine (the replication's `reimpl/tvl.py`; fidelity established
there — 10,000-run winner-talent mean 0.670, sd 0.093) was run as the model-side
reference (gate **G2**): 1,000 baseline runs (N=1000, m_T=0.6, σ_T=0.1, I=80,
N_E=500, p_L=50, C0=10, truncation on) plus a p_L={20,50,80} ladder (250 runs
each). Every staged file was sha256-verified (gate **G1**: 126/126 match). Each
domain carries its pre-declared skill/success construction and a proxy-validity
row (gate **G3**) with a numeric pass/fail rule. Bootstrap 95% CIs resample units
(1,000 draws, seed 2018). No value is tuned toward the paper or the Phase-2a
previews; the previews were used only to calibrate thresholds (labelled
**[PREVIEW-CALIBRATED]** throughout; the words "pre-registered"/"validated" are
not used for those constants).

## The model-side reference (G2) and a paper-text-vs-code finding

G2 passed its audit-anchored integrity bands (winner-talent mean 0.6696 ∈
0.6686±0.01; sd 0.0918 ∈ 0.0932±0.015; top-20% capital share 0.7707 ∈ 0.774±0.02).
The run-produced reference values (the references for every comparison below) are:
winner **skill percentile 0.696** (paper-implied 0.749), **P(winner in the true
top-talent decile) = 0.269**, **P(winner talent > 0.8) = 0.078**, **top-20%
capital share 0.771**, **y2y top-100 persistence 0.959**.

> **C22 model-side finding.** The paper's released engine, run faithfully, gives
> P(winner talent > 0.8) ≈ 8% (QA audit, 13,700 runs; reproduced here at 7.8%),
> not the paper's printed 3%, and the paper's printed value is distributionally
> inconsistent with its own released code — the printed quantities are treated
> throughout as the paper's claims, with the run-produced G2 values as the
> model-side references.

## P1 — shape signature (weak)

Success is fat-tailed and highly concentrated in every domain with a concentration
measure; the skill proxies are near-symmetric/thin-tailed (tennis point-share
skew 0.75, excess kurtosis 0.71; movie rating excess kurtosis 0.92):

| domain | success top-20% share | top-1% share | skill shape | verdict |
|---|---|---|---|---|
| tennis (titles) | **0.639** [PREVIEW-CALIBRATED cutoff 0.6; preview 0.639] | 0.126 [cutoff 0.1] | near-symmetric | **shape signature present (consistent with the model and with any multiplicative mechanism)**, *threshold-sensitive (raw 0.639 vs 0.6)* |
| movies (votes) | 0.883 | 0.309 | near-symmetric | shape signature present (consistent with the model and with any multiplicative mechanism) |
| science (citations 2015) | 0.928 | 0.278 | (no skill proxy) | fat-tailed success present; shape-on-success only |
| baseball (salary 1985–2016) | 0.637 | — (Gini 0.604) | — | fat-tailed success present |

Science citation concentration is stable across cohorts (top-20% share: 2010
**0.954**, 2015 **0.928**, 2019 **0.883**; declared OpenAlex in-run pulls, logged
in `fetch_log.json`). **Pre-declared reading:** P1 can only count *against* the
model if absent; its presence is consistent with any multiplicative mechanism and
is **not** evidence for the model's specific mechanism.

## P2 — decoupling at the top (the sharp test)

Model baseline: the #1-success unit sits near the **0.70** skill percentile
(paper-implied 0.749), P(top-decile) **0.269**. The skill-dominated limit predicts
≥ 0.99.

| domain (proxy) | #1-success skill pct (95% CI) | top-10 median skill pct | P(top-decile) | validity | verdict |
|---|---|---|---|---|---|
| **tennis** (point-share; titles) | **0.994** [0.984, 1.000] | **0.981** | 0.67 cond. | **PASS** (split-half 0.959 ≥ persistence 0.678); leakage-robust (finals-excluded 0.994, same cell) | **decoupling signature absent: top success coincides with top measured skill (the model's talent-dominated corner)** [cut pair 0.95/0.95, PREVIEW-CALIBRATED; tennis winner-pct preview 0.994] |
| tennis (Grand Slam titles, secondary) | 1.000 | 0.987 | — | PASS | decoupling absent (even sharper) |
| **movies** (rating; votes) | 0.999 [0.997, 1.000] | 0.997 | 0.20 cond. | PASS (median within-decile \|ρ\| 0.023 ≤ 0.2 **[SET AT 2b REVISION: this constant was fixed before the within-decile statistic was ever computed; the only related preview quantity was the bulk Spearman(rating, votes) = 0.205, a different statistic, stated here for transparency.]**; weakest proxy) | decoupling signature absent (talent-dominated corner) |
| **baseball** (exit velocity; All-Star+awards) | 1.000 [0.397, 1.000] | 0.867 | 0.42 cond. | PASS (exit-velo y2y 0.756, sprint 0.932 ≥ OPS 0.493) | **uninformative: the data cannot distinguish the model band from the talent-dominated band (power: MDE ≈ 0.33 skill-percentile points** at 80% power / α=0.05 one-sided, from the winner-pct bootstrap SD 0.134 — larger than the 0.25-point gap from the model baseline 0.696 to the 0.95 boundary, so the bands cannot be separated; the MDE is a lower bound because winner-pct is a single success-ranked order statistic whose bootstrap piles at the 1.0 ceiling in 37.5% of resamples. Computation filed in study 003's `results/baseball_mde.json`.**)** |
| baseball (sprint speed; secondary) | 0.501 | — | — | PASS | sprint is a weak success predictor; point estimate near the model band's lower edge |
| chess (Elo) | — | — | — | — | S2 degenerate (Elo is both skill and success ranking) — **not computed** |

**Model-side exceedance (§2, from G2's run distributions).** Under the model
baseline, a winner at or above tennis's skill percentile (0.994) occurs in **1.3%**
of runs; a top-10 median this high (0.981) in **0.0%** of runs. For movies (0.999 /
0.997) both exceedances are **0.0%**. The tennis and movie top-success cohorts are
therefore essentially *never* produced by the model's baseline parameterization:
the data sit far in the model's talent-dominated corner, not at its p_L=50
decoupling prediction.

**Pre-declared contradiction paragraph (verbatim).** "A domain contradicts the
model's baseline decoupling signature when the #1-success unit sits at or above the
95th percentile of independently measured skill AND the top-10 median sits at or
above the 95th — both conditions binding, the pattern the model gives only in its
talent-dominated corner. A domain supports it when winner-skill percentiles
concentrate in the 60th-90th band with P(top-decile) below 25% [PREVIEW-CALIBRATED].
The cross-domain claim survives only if decoupling orders with measured
persistence." Tennis and movies meet **both** binding conditions → the baseline
decoupling signature is **contradicted** in both. (Note: under the model's own
baseline the single winner alone sits above the 95th skill percentile in ~15% of
runs, which is why the top-10-median conjunct is binding — and here it too is ≥0.95,
so the contradiction is not a one-draw artifact.)

## P3 — cross-domain ordering

Elite persistence (year-to-year Spearman) reproduces the pre-declared measured
ladder **exactly**: **chess 0.870 > tennis 0.678 > baseball 0.493** (baseball's
ladder entry is player OPS y2y 2000–2025, as declared; team win% y2y 0.476 and
Mauboussin season luck share 0.248 are reported secondaries). **But decoupling
does not order with persistence/luck:** the #1-success skill percentile is ~0.99–1.0
in every measured P2 domain regardless of luck share, the opposite of the model's
prediction that higher-luck domains show *more* top-level decoupling (the model's
own p_L ladder moves winner-pct only within 0.67–0.73). 

**Verdict: partial ordering — the persistence ladder holds; decoupling and
concentration do not order with it.** **Poker's luck-end placement is
literature-based only (Levitt & Miles 2014)** and is reported as a labelled
literature rung, **not** a counted/measured rung; "cross-domain ordering signature
present" is **not** claimed as a 4-domain result (the staged poker data has no
persistence series).

## P4 — funding (bounded)

Study 001 ships only the model-side funding ladder (the p_L={20,50,80} runs, in
`tvl_reference.csv`) and **no real-world funding verdict**; the funding
confrontation is study 002's job.

## Poker (the luck-end leg, bounded by design)

Champions parsed row-by-row from the staged wikitext (`poker_events.csv`, 57
Main-Event years 1970–2026; 5-row spot-check against PROVENANCE passed:
e.g. Moneymaker 2003 / 839 entrants / $2.5M; Gold 2006 / 8,773 / $12M).

> **Power statement (verbatim).** Under a no-skill null with field sizes n_t, the
> expected number of repeat Main-Event champions 1990-2025 is E_0 = 0.315; under a
> uniform 5× skill multiple for a 10% skilled stratum it is E_5 = 1.124. The
> observed count is 0. With E_5 − E_0 = 0.809 expected events, this comparison
> cannot distinguish the hypotheses.

Modern fields (≈8–10k) make Main-Event recurrence uninformative, as anticipated.
The **bracelet-concentration block is descriptive only** (demoted at the 2b
revision): the staged bracelet article holds only a top-truncated multi-bracelet
table (Hellmuth 17, Ivey 11, Brunson/Chan/Seidel 10, then five at 9) with no
per-event field sizes and no full player population — concentration on a
top-truncated list is selection-biased and lower-bound-style descriptive only, with
no verdict weight and no null comparison. The poker leg's informative weight rests
on the **Levitt & Miles 2014** anchor (a-priori skilled ROI +30.5% vs −15.6%), cited
as literature; a proper multi-event concentration test is a next-tick item behind
the Hendon Mob human gate.

## MusicLab branch (entertainment, gated)

`shared-data/entertainment/musiclab/` does not exist (OPR archive 403s keyless) →
**honest-exclusion branch.** One labelled literature row: Salganik–Dodds–Watts
(2006) found that inequality and unpredictability both rise with social influence —
"the best songs rarely did poorly, and the worst rarely did well, but any other
result was possible" — qualitative support for P2's *direction* in few-trial reward
markets. Raw data human-gated; no invented numbers.

## Headline

Across 3 domains with independent skill measures (tennis, movies, baseball; chess
as a skill-dominated persistence control), the model's decoupling signature is
**absent in tennis and movies** (top success coincides with top measured skill) and
**uninformative in baseball**; the measured domains order on the skill-luck axis as
**chess > tennis > baseball**, reproducing the pre-declared measured ladder (poker's
luck-end placement literature-based, not measured); the shape signature (fat-tailed
success from near-symmetric skill) appears in **4 of 4** domains with a
concentration measure — a pattern **partially consistent** with a talent-times-luck
mechanism whose luck weight varies by domain, and **inconsistent** with the paper's
baseline parameterization in which the most successful are almost never the most
skilled.

**Answer to the reader.** The model's *shape* finding (a few win almost
everything, from modest spreads in underlying skill) corroborates broadly — but
that pattern follows from almost any multiplicative process and is not, by itself,
evidence for the model's mechanism. The model's *signature* finding — that the
most successful are almost never the most skilled — does **not** corroborate in
these domains: in tennis and movies (and in the baseball point estimate) the top
performers sit at the very top of independently measured skill, a configuration
the faithful engine produces in ~1% or fewer of its baseline runs. The persistence
ordering across domains behaves as the skill-luck intuition predicts, but it does
**not** translate into the top-level decoupling the model's baseline requires.

## Limitations (proxy table)

| domain | skill proxy | key limitation |
|---|---|---|
| tennis | career point-share | independent in grain but not ex-ante (titles won by winning those same points); addressed by the finals-excluded leakage control (robust) |
| chess | Elo | skill and success ranking are the same object → no P2; used only as the persistence anchor |
| baseball | exit velocity / sprint speed | physical measurables, genuinely ex-ante, but the Statcast-era success panel pairing All-Star/awards is small (n≈430) → wide P2 CIs; sprint is a weak success proxy |
| movies | IMDb averageRating | the weakest proxy; votes-vs-rating confound controlled within votes-decile (median \|ρ\|=0.023) |
| science | — | citations are success; no independent ex-ante quality proxy → S1/concentration only |
| poker | — | no persistence series in staged data; Main-Event recurrence has no power at modern field sizes; bracelet concentration descriptive only |

**Deviations.** `shared-data/tvl-engine/`, `qa-distcheck/distcheck_results.json`
and `recency-research.md` were not separately staged; the faithful replication
engine was used for G2 and the band/rule constants were taken from the centers
quoted verbatim in the spec. "Seeds 1..1000" were realized as independent batched
replicates under fixed master seeds. The tennis top-100 persistence (0.678,
2011–2025) differs slightly from the preview (0.645) due to last-ranking-date
handling; split-half reliability still clears the validity rule by a wide margin.
**Truncation deviation (declared at 003 audit-conformance):** Spec §5 Block A G2
specifies "no truncation" for the model-reference run, but the G2 run used
`truncate_talent=True`; this was chosen for construct-consistency with the staged
QA distcheck anchor bands, which were themselves computed with truncation ON — the
resolution is to keep the anchor-consistent setting (truncation clips ~3e-5 of
talent draws, numerically immaterial to every G2 integrity band and reference
value), and the spec-text conflict is named here rather than silently followed.

## Erratum / audit-conformance appendix (study 003 corrections)

The provenance audit recomputed every audited number independently and found no
fabrication and no gate fudging; it logged five bounded labelling/reporting
corrections, applied here (no verdict row and no estimate changes). Each old→new
change is recorded in study 003's `results/card_corrections.csv`.

- **001-4 (long tennis secondary).** The 1992–2025 top-100 points-rank persistence
  series has an unreported mean because the 1992→1993, 1993→1994, 1994→1995 and
  1995→1996 pairs carry no point-level data (ATP point statistics begin 1996 in the
  staged feed), so the raw 33-pair mean is NaN. **Exclusion rule declared:** pairs in
  which either season lacks point-level statistics are excluded; the non-NaN-pair
  mean over the 29 valid pairs (first valid pair 1996→1997) is **ρ̄ = 0.622**
  (range 0.354–0.831), consistent with the headline 2011–2025 mean 0.678. The gap
  (four pre-1996 pairs missing) is declared, not imputed. Filed in
  `domain_tennis.json` (`persistence_1992_2025.mean_rho_nonNaN`) and in 003's
  `results/tennis_long_persistence.json`.
- **001-5(a) (M2 pooled vs per-domain).** M2 reports per-domain conditional overlaps
  (P(top-decile): tennis 0.67, movies 0.20, baseball 0.42) rather than the spec's
  single pooled statistic; the per-domain numbers are kept and this is an undeclared
  deviation now declared — no pooled figure is substituted.
- **001-5(b) (shape "4 of 4" vs k=3 template).** The headline shape clause reports the
  signature present in "4 of 4" domains with a concentration measure, whereas the
  pre-declared §6 shape template was framed for k=3 (the three independent-proxy
  domains tennis/movies/baseball); science is the added fourth concentration-only
  domain. The "4 of 4" count is retained and the departure from the k=3 template is
  declared, not erased.
- **001-5(c) (baseball OPS y2y COVID gap).** The baseball OPS year-to-year persistence
  ladder entry (mean 0.493, 23 pairs) is missing the 2019→2020 and 2020→2021 pairs:
  the 60-game 2020 season leaves essentially no players at the ≥300-PA cut, so both
  adjacent pairs are empty. This gap is declared; the 23-pair mean is unchanged.
- **001-5(e) (S4 concentration rung).** The S4 cross-domain ordering test ranked **raw**
  top-20% concentration share (tennis 0.639, baseball 0.637, movies 0.883), not
  concentration "per unit of skill spread" (share normalised by the domain's skill
  dispersion) as the spec rung intended; the raw-share ranking is kept and the
  deviation is declared. (The verdict — decoupling/concentration do not order with
  persistence — is unaffected: it rests on the winner-skill-percentile ordering, not
  the concentration rung.)
- **001-5(d)** is a prose fix in `domain_chess.json` ("2015-2023" → "2015-2026", the
  range of that file's own #1-rated-id table); see `card_corrections.csv`.
