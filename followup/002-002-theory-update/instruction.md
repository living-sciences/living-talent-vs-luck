<!-- LAUNCH FILE: study 002-theory-update ONLY. The sibling study 001 is referenced for context; where this spec says to reuse 001 outputs, read them from this run's followup/ directory. -->

# Extension specs: Pluchino, Biondo & Rapisarda (2018), "Talent versus Luck", Adv. Complex Systems 21:1850014

**Status:** DRAFT for the Phase 2b judge, prepared 2026-10-22 by the Phase 2a recency-research agent. Every source was verified live on 2026-10-22 (`recency-research.md`; hashes in `extension-assets/*/DATA_MANIFEST.md`); Phase 2a preview code outputs are in `extension-assets/prep-diagnostics/` (embargoed for 001, see §0).

**What this pair is, in one sentence.** Study 001 tests, in five-plus real domains with pre-declared independent skill proxies, whether the model's four falsifiable signatures (fat-tail transformation; top-success ≠ top-skill; cross-domain luck ordering; funding-allocation claim) actually appear in the newest open data; Study 002 fits the TvL engine itself to each domain's measured signature triple, reconciles the fitted luck shares with the 2018-2026 literature, and confronts the Section-3 funding table with the real funding-lottery record.

**Reader question (a reader, through the site, anonymous):** do the model's findings corroborate with real-world data in different domains, e.g. sports, entertainment, poker?

This file holds the standard pair. At launch, each part is copied to its own instruction file:
- **Part I → `001-living-update`** (`--name living-update`): the multi-domain empirical test.
- **Part II → `002-theory-update`** (`--name theory-update`): the model fit, reconciliation, funding confrontation, and next-tick predictions.

---


# PART II: Follow-up study 002, theory update

- Measured expectation ≈ 1-2 core-hours (the calibration grid is ~7,000 engine runs; each run is ~1000 agents × 80 steps).
- Checkpoints: each T-block writes to `results/` with a `.done` marker; a cut-short session continues as `theory-update-cont`, reusing outputs and finishing `remaining`.

## Workspace staging

Same `shared-data/` as 001, plus read-only `followup/001-living-update/results/` (especially `signatures.csv`, `tvl_reference.csv`, `gates.json`). **Fetch nothing.** If 001's `result_card.json` is not `completed`, stop.

## 1. The question

001 measures whether the signatures appear; 002 asks what the 2018-2026 evidence — 001's measurements plus the literature — implies **for the model**: can one TvL parameterization per domain jointly reproduce each domain's measured triple (concentration, decoupling, persistence)? Do the fitted luck weights agree with the independent estimates (Zappalà's tennis a ≈ 0.20-0.30; Janosov's cross-domain luck decomposition; Levitt-Miles poker ROI; Sobkowicz's sprint lower bound)? And does the Section-3 funding claim survive contact with the post-2018 funding-lottery record?

## 2. Pre-declared analysis

**T1. Generalized TvL calibration (the model, written as a model).** Extend the engine minimally with one pre-declared talent-leverage dial (exact form fixed now, to forbid mid-run invention): a lucky hit succeeds with probability **q_i = (1−α)·q̄ + α·T_i**, where q̄ = 0.6 (the population mean talent), α ∈ {0, 0.1, …, 1.0}; α = 1 is the paper's model, α = 0 is pure luck (this mirrors Zappalà's a and nests the original). Second dial: p_L ∈ {20, 35, 50, 65, 80}. Grid: 11 α × 5 p_L × 100 runs (seeds 1..100) = 5,500 runs + the G2 anchor re-run at (α=1, p_L=50), which must reproduce 001's `tvl_reference.csv` within Monte-Carlo CI (gate).
- For each grid cell compute the model's triple: success top-20% share; winner-talent percentile mean and P(top-decile); **persistence as the y2y analogue — top-100 capital-rank Spearman between consecutive one-year windows (2 steps) in the back half of the run (t > 40), averaged — matching the domains' year-over-year construct; the split-half statistic (ranks at t=40 vs t=80) is computed and reported as a secondary, not used in the distance.** A binding construct note travels in `results/model.md`, exactly as T2 carries one for Zappalà's aggregation level: the model's persistence entry is the y2y analogue because every domain series is year-over-year; the split-half (20-year-gap) statistic is a different construct and never enters the fit.
- **Fit per domain:** nearest grid cell minimizing the standardized L2 distance on the domain's statistic list below, from 001's `signatures.csv` (standardized by 001's bootstrap SEs). **The per-domain statistic lists are fixed NOW (TvL-B1):**
  - tennis: {success top-20% share, winner-skill percentile, P(top-decile), y2y top-100 persistence};
  - chess: {y2y top-100 persistence} (S2 degenerate, declared in 001 §4.2);
  - movies: {success top-20% share, top-1% share, winner-skill percentile, P(top-decile)} (no persistence series);
  - baseball-player: {success top-20% share, top-1% share (salary-era concentration), winner-skill percentile, P(top-decile)} + the persistence entry = player OPS y2y Spearman (the ladder entry named in 001 §2 P3 / §4.3);
  - poker: **excluded from the T1 fit** — under the TvL-A5 demotion its only staged outputs are the Main-Event power statement (a power statement, not a signature statistic) and a selection-biased descriptive concentration row; stated as excluded in `domain_fits.csv`;
  - MusicLab: {per-world success top-20% share, winner-quality percentile, P(top-decile)} iff 001 ran the FULL branch; excluded (gated branch) otherwise.
  A statistic may drop from a domain's distance only when 001's own pre-declared rules withheld it (measurement-limited by its §4 numeric validity rule, or a gated branch), and every drop is stated per domain in `domain_fits.csv`. Report the fitted (α, p_L) with a 1-SE neighbourhood set.
- **Pre-declared falsification within T1:** if for some domain NO grid cell fits all its available statistics within 3 SE jointly, report "the TvL family cannot jointly reproduce this domain's signature triple" and show which statistic breaks — this is a finding against the model's sufficiency, not a failure of the study.

**T2. Reconciliation table (same-construct-family comparisons only).** `results/reconciliation.csv`: our fitted α per domain beside — Zappalà et al. 2023 tennis a = 0.20-0.30 (tagged "point-level weight in a tournament-structured ABM — different aggregation level; see T2 note"); Janosov et al. 2020 luck shares in creative careers (tagged "impact-decomposition, no ex-ante skill"); Levitt-Miles ROI gap (tagged "returns-based skill evidence, not a model weight"); Sobkowicz et al. 2020 sprint lower bound; Csurilla et al. 2023 (3×3 vs 5v5 direction only). One binding note: tennis's fitted α aggregates career-level outcomes while Zappalà's a weighs single points — the two agree or disagree only after the T1 model's point-free structure is acknowledged; never present them as the same parameter.

**T3. The funding claim (C5) vs the real world.**
- Model side: re-run the funding comparison on the fitted-α engines (not only α=1): egalitarian 1u vs elitarian top-25%×10u at fixed budget (8 injections, the paper's design; the briefing's §5.3 reading: re-rank at each injection; funds compound), 200 runs each, for α ∈ {fitted tennis, fitted movies, 1.0}. Question: does the egalitarian-beats-elitarian ordering survive when talent matters more than in the baseline model? (Pre-declared: report the α at which the ordering flips, if any — the "funding-claim robustness frontier".)
- **Binding (TvL-B3): no §3 printed P_T or F_T value from the paper is used as a quantitative reference band anywhere in 002** — T3 is engine-vs-engine throughout (the QA audit found the paper's §3 P_T family systematically 1-5 points off the faithful engine, 5-20σ on paired-seed bands, and one F_T cell arithmetically wrong). Wherever the paper's funding table is cited (in any 002 output: report, model.md, tables, card), this caveat travels with it verbatim: "the paper's unreleased experiment code evidently differed from the released demo; one F_T cell is an arithmetic error (70000→50000)".
- Real side (literature numbers from `literature/PROVENANCE.md`, each traced): Bol et al. 2018 (the real system is elitarian and causally Matthew — consistent with the model's premise); HRC NZ and SNSF lotteries (existence + acceptability + process evidence; **no outcome RCT of lottery-vs-panel on later research success exists in the staged record through 2026**).
- **Pre-declared verdict vocabulary for P4 (closed; M5's verdict word comes from this list only, TvL-B4):**
  - "untested but consistent" (default, if the model ordering is robust across fitted α and no real outcome evidence contradicts);
  - "contradicted" only if a staged-source outcome study shows merit-selected cohorts outperforming lottery cohorts at equal budget on later success;
  - "model-fragile" **iff flip-α < max(fitted α over the career domains used in T3, i.e. tennis and movies)**;
  - "robust (no flip in [0,1])" if no flip exists on α ∈ [0, 1] — and card metric M3 then reports "no flip" explicitly;
  - "domain-dependent" if the fitted tennis and movies α disagree on which side of the flip-α they sit — both values stated in the verdict row.
  Plus one sentence stating what future evidence would falsify C5 (a lottery-vs-panel outcome comparison, e.g. a future HRC NZ/SNSF cohort study).
**T4. Answer the reader, in one plain-language section**, domain by domain (sports, entertainment, poker, science/funding), each answer one or two sentences citing 001's verdict rows and T1's fitted weights — flowing text, no table dump.

**T5. Falsifiable predictions for the next tick (≥3, each with sign, magnitude, interval, and the data that will test it):** (1) tennis year-end top-100 persistence for 2026 (full season) within [fitted-model band]; (2) chess jan27 top-100 persistence exceeds tennis's by ≥ [x] (from the T1 fits); (3) the 2027 WSOP Main-Event repeat-champion count stays within the no-skill-null band E_0 ± [its binomial interval] computed by 001's power-statement machinery extended one year (field size assumed within ±20% of the 2025 entrants) — this replaces the previously planned bracelet permutation-null prediction, which inherits the TvL-A5 demotion (no permutation null is computable from the staged data; bracelet concentration is descriptive-only until Hendon-Mob-grade data is licensed); (4, if MusicLab staged) the winner-quality percentile band for any future multiple-worlds replication.

## 3. Validation gates
1. 001 `completed`; its `gates.json` G1-G3 passed.
2. T1's (α=1, p_L=50) cell reproduces `tvl_reference.csv` within Monte-Carlo CI.
3. Every literature number traces to `literature/PROVENANCE.md` (with its verification level: staged-PDF vs abstract-verified); abstract-verified numbers carry a dagger in every table.
4. The engine extension (α-dial) is implemented as a wrapper around the staged `tvl.py` with a diff shown in the report; the α=1 path must be bit-identical in expectation (same RNG draws) to the unmodified engine — assert on one seed.

## 4. Deliverables
- `report.md`, `followup_summary.json`, `result_card.json`.
- `results/model.md`: the generalized model (equation, grid, fitted (α, p_L) per domain with neighbourhoods, the T1 falsification outcomes, the T3 funding frontier, T5 predictions) — written as a model, not a number dump.
- `results/{calibration_grid.csv, domain_fits.csv, reconciliation.csv, funding_comparison.csv}`.
- Figures: `fig_fit_map.png` (α × p_L plane, domains placed with neighbourhoods; Zappalà's tennis band overlaid); `fig_funding_frontier.png` (egalitarian-vs-elitarian gap vs α).
- **Card (≤5 metrics):** headline = the T4 one-sentence answer to the reader; M1 fitted α per domain (with the tennis-vs-Zappalà pair); M2 the T1 joint-fit pass/fail per domain; M3 the funding flip-α vs fitted αs; M4 the strongest T5 prediction; M5 the P4 verdict word.

## 5. Out of scope
- New fetches; new domains; WTA; any model extension beyond the single pre-declared α-dial (no networks, no tournament structure — Zappalà's model is cited, not ported).
- Converting Janosov's Q/R decomposition into α (different construct; comparison stays qualitative).
- Any real-world funding outcome analysis beyond the staged literature record.

## 6. Environment
Same as 001. **FOREGROUND RULE** as in Part I. Chunk the 5,500-run grid into ≤8-minute calls (e.g. one α value per call), checkpointing each.

---