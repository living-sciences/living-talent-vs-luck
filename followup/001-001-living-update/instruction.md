<!-- LAUNCH FILE: study 001-living-update ONLY. The sibling study 002 is referenced for context but is OUT OF SCOPE for this session; another session runs it from its own file. -->

# Extension specs: Pluchino, Biondo & Rapisarda (2018), "Talent versus Luck", Adv. Complex Systems 21:1850014

**Status:** DRAFT for the Phase 2b judge, prepared 2026-10-22 by the Phase 2a recency-research agent. Every source was verified live on 2026-10-22 (`recency-research.md`; hashes in `extension-assets/*/DATA_MANIFEST.md`); Phase 2a preview code outputs are in `extension-assets/prep-diagnostics/` (embargoed for 001, see §0).

**What this pair is, in one sentence.** Study 001 tests, in five-plus real domains with pre-declared independent skill proxies, whether the model's four falsifiable signatures (fat-tail transformation; top-success ≠ top-skill; cross-domain luck ordering; funding-allocation claim) actually appear in the newest open data; Study 002 fits the TvL engine itself to each domain's measured signature triple, reconciles the fitted luck shares with the 2018-2026 literature, and confronts the Section-3 funding table with the real funding-lottery record.

**Reader question (a reader, through the site, anonymous):** do the model's findings corroborate with real-world data in different domains, e.g. sports, entertainment, poker?

This file holds the standard pair. At launch, each part is copied to its own instruction file:
- **Part I → `001-living-update`** (`--name living-update`): the multi-domain empirical test.
- **Part II → `002-theory-update`** (`--name theory-update`): the model fit, reconciliation, funding confrontation, and next-tick predictions.

---


# PART I: Follow-up study 001, living update

**LAUNCH LINE:** `REPLICATION: COMPLETE; GRADING UNDER AUDIT` (fixed; see ORCH-1)

- Measured compute in Phase 2a: every domain block runs in seconds-to-minutes on one core; the heaviest items are the IMDb `title.basics` parse (~2 min) and gate G2's 1,000 engine runs (~minutes). Expect well under 1 core-hour total.

**Continuation study.** Every block (A-D) writes its CSVs to `results/` and a `workspace/checkpoints/<block>.done` marker, and updates `followup_summary.json` (with a `remaining` list), as soon as it finishes. If the session ends before `result_card.json` is completed, the orchestrator relaunches the same instruction as the next free number with `--name living-update-cont` and the header "continues 001-living-update"; the continuation reuses `workspace/` and `results/`, skips blocks with `.done` markers, and finishes everything in `remaining`. Every pre-declared block runs; nothing is dropped for time.

## 0. What this study is (binding framing)

- It answers the reader's question — do the model's findings corroborate with real-world data in sports, entertainment, poker (and science/funding, where the paper's Section 3 lives) — by testing the model's four pre-declared signatures P1-P4 (§2) against the newest open data (vintages: tennis through the full 2025 season, FIDE January 2015-2026, Lahman through 2025, Statcast 2015-2026, IMDb 2026-10-22, OpenAlex live, Wikipedia revids pinned).
- **The test must be able to fail, and Phase 2a previews suggest parts of it will:** the design treats "signature absent" as a first-class, reportable outcome with its own pre-declared wording (§6). No text may convert a failed signature into a win for the paper, or a confirmed amplification (P1) into evidence for the model's *mechanism*.
- **Skill is unobservable; every proxy is imperfect.** Each domain block carries a proxy-validity row (§4) and the pre-declared contamination caveat from `recency-research.md` §5. Verdicts in a domain where the proxy fails its validity row are labelled "measurement-limited", not "signature absent".
- **Prior-art positioning (binding):** the first results paragraph of `results/findings.md` must name Janosov-Battiston-Sinatra 2020 (the closest multi-domain decomposition), Zappalà et al. 2023 (the authors' own tennis calibration, a ≈ 0.20-0.30), and Biondo-Pluchino SSRN 6572147 (2026) as the authors' concurrent careers paper — stated as "concurrent and not yet read (metadata-verified; bot-blocked)" in findings.md and on the card (a human reads it before external publication; ORCH-2). No text may claim this is the first empirical test of talent-vs-luck, the first luck-vs-ability decomposition, or the first sports test. What IS new is stated in exactly these terms: independent ex-ante skill proxies against TvL's quantitative winner-percentile signature; the cross-domain ordering with a skill-dominated control; the funding confrontation.
- **Embargo.** Do NOT open `shared-data/prep-diagnostics/` until blocks B1-B6 have written their estimates to `results/`. Afterwards compare in an appendix and reconcile any differences.
- Do not read other studies under `followup/`. **Fetch nothing from the network**, with one declared exception: the OpenAlex API queries written in block B5 (keyless, CC0); log each query string + timestamp in `results/fetch_log.json`. If any other input is missing, stop that block and report; never substitute from memory.

## 1. The model-side reference values (paper claims, not replication grades)

| ID | Model claim (paper) | Reference value | Home |
|---|---|---|---|
| C1 | Gaussian talent + multiplicative luck ⇒ fat tail, 80/20 | top 20% of agents hold ~80% of capital; tail slope ≈ −1.3 | Sec 2.1-2.2 |
| C2/C4 | most successful ≠ most talented | winner talent ~ N(0.667, 0.09) ⇒ winner at the **74.9th percentile** of N(0.6,0.1); P(winner talent > 0.8, i.e. top ~2.3%) ≈ **3%**; most-talented agents' mean capital ≈ 63 vs 33 for average | Sec 2.2, Figs 8-9 |
| C5 | egalitarian/random funding > elitarian per unit invested | E_norm ranking; egalitarian 1u/agent best | Sec 3.1 |
| C6 | luck-richness moves outcomes: p_L 80/50/20 ⇒ P_T 62/32/9% | the model's own "luck share" dial | Sec 3.2 |

**The printed values in this table are paper CLAIMS, never gate references or comparison bands.** The QA audit (13,700 runs of the same engine; staged at `shared-data/qa-distcheck/distcheck_results.json`, see ORCH-3) proved the faithful engine does not produce some of them: P(winner T > 0.8) ≈ 8.0 ± 2.2% (not the printed 3%; QA claim C22), P(winner in the true top talent decile, T > ≈0.728) ≈ 25%, and mean top-20% capital share ≈ 0.774 (the printed 0.80 sits at the edge of the faithful distribution). These are paper-text-vs-code discrepancies, part of what this study teaches about the paper.

Gate G2 re-derives the C1/C2/C4 reference numbers from the staged engine (1,000 baseline runs, plus the p_L = {20,50,80} ladder at 250 runs each) so every comparison row cites a run-produced file, not a transcribed number. **G2's PASS/FAIL bands are restricted to audit-verified engine-integrity quantities only:** winner-talent mean within 0.6686 ± 0.01, winner-talent sd within 0.0932 ± 0.015, and mean top-20% capital share within 0.774 ± 0.02 — the centers come from the staged QA distcheck bands (`shared-data/qa-distcheck/distcheck_results.json`, keys `baseline_per_run.winner_T` and `baseline_per_run.top20pct_share`), and G2 must additionally print a side-by-side of its own run distribution against those staged bands. **G2 does NOT gate on any printed paper quantity** — not the 3% / not 0.80 ± 0.03. Instead, G2 *reports* P(winner in top talent decile), P(winner T > 0.8), and the top-20% capital share from its own runs, and these run-produced values become the model-side reference values for every S2 comparison and for card metric M2, with the paper's printed 3% / 80% cited beside them, labelled as the paper's claims. (The paper states T > 0.8 ≈ top 2.3%; G2 reports both that cut and the top-decile cut, and all S2 comparisons use the **top-decile** cut, declared now.) If G2 fails its integrity bands, stop and diagnose the engine copy before any domain block.

## 2. The four pre-declared signatures and their per-domain discriminating predictions

- **P1 (shape, weak):** skill-proxy distribution ~ thin-tailed/symmetric while success is fat-tailed (top-20% share ≥ 0.6 [PREVIEW-CALIBRATED; tennis preview 0.639], top-1% share ≥ 0.1 [PREVIEW-CALIBRATED]). *Pre-declared reading:* P1 can only count AGAINST the model if absent; its presence is consistent with any multiplicative mechanism and must be reported with that sentence attached.
- **P2 (decoupling at the top, the sharp test):** per domain, compute (a) the skill percentile of the #1-success unit, (b) the median skill percentile of the top-10 success units, (c) P(top-success decile | top-skill decile overlap). TvL baseline predicts (a) ≈ 0.75 on average, with P(top-decile) given by the G2-derived reference (the paper prints 3%, but that is its claim for the T > 0.8 cut; the QA audit measured ≈8% at T > 0.8 and ≈25% at the true top-decile cut — the run-produced G2 values are the reference, the printed 3% is cited only as the paper's claim); the skill-dominated limit predicts (a) ≥ 0.99. **Every P2 verdict row must also report the model-side exceedance probabilities computed from G2's run distributions: "under the model baseline, a winner at or above this skill percentile occurs in [x]% of runs; a top-10 median this high in [y]%"** — G2 produces the winner-talent-percentile and top-10-capital-median-talent-percentile distributions, so the band comparison is always accompanied by an honest tail statement quantifying the strength of a contradiction (a winner percentile of 0.994 is roughly a 2% tail event under the baseline).
- **P3 (ordering):** rank domains by elite persistence (year-to-year Spearman of the top-100 success ranking; for MLB teams, win% autocorrelation). Pre-declared expected ordering, most-skill-first, **on the measured ladder: chess > tennis > baseball** — these three are the only domains with a persistence series in the staged data, and every P3 verdict row is scoped to them. **Poker's luck-end placement is literature-based only (Levitt-Miles 2014)**: it is reported as a labelled literature rung, never counted as a confirmed/measured rung, and "cross-domain ordering signature present" may not be claimed as a 4-domain result (the staged poker data has no persistence series; the spec itself notes persistence needs the gated Hendon Mob). **The baseball ladder entry is the player OPS y2y Spearman (§4.3), declared now; the team win% y2y correlation is a reported secondary, not the ladder entry.** Movies/science unplaced a priori (no persistence series in the staged data — concentration and P2 only). Then test whether P2 decoupling decreases, and success concentration (per unit of skill spread) increases, monotonically in measured luck share.
- **P4 (funding, bounded):** handled in 002; 001 only produces the model-side funding ladder (G2's p_L runs + the paper's Table values) and ships no real-world funding verdict.

**What contradicts the model (pre-declared, verbatim in findings):** "A domain contradicts the model's baseline decoupling signature when the #1-success unit sits at or above the 95th percentile of independently measured skill AND the top-10 median sits at or above the 95th — both conditions binding, the pattern the model gives only in its talent-dominated corner. A domain supports it when winner-skill percentiles concentrate in the 60th-90th band with P(top-decile) below 25% [PREVIEW-CALIBRATED]. The cross-domain claim survives only if decoupling orders with measured persistence." (These are the same cuts as §6's P2 rows — one pair, 0.95/0.95, stated identically in both places; the top-10-median conjunct is binding, not parenthetical, because under the model's own baseline the single winner alone sits above the 95th skill percentile in roughly 15% of runs, so a one-draw winner-only verdict would over-reject.)

**Preview-calibration disclosure (binding; econ4 Dem-A1 standard).** The Phase 2a prep-diagnostics previews were used to calibrate this spec's gates and verdict bands (`prep-diagnostics/README.md` says so verbatim). Therefore:
- Every band constant set with previews in view — the P1 cutoffs 0.6 and 0.1, the P2 bands [0.55, 0.95] and ≥ 0.95, and P(top-decile) < 25% — is labelled **[PREVIEW-CALIBRATED]** wherever it appears: in this spec, in `gates.json`, in `results/findings.md`, and on the result card. The relevant preview values are stated next to the thresholds wherever they are used (tennis top-20% share preview 0.639 next to the 0.6 cutoff; tennis winner percentile preview 0.994 next to the 0.95 cut).
- The words "pre-registered" and "validated" are **banned** for these constants, everywhere.
- **Threshold-sensitivity rule:** any P1/P2 verdict whose statistic falls within 0.05 of its threshold is reported as "threshold-sensitive" with the raw value in the verdict row. By the previews, tennis P1 triggers this (0.639 vs the 0.6 cutoff — the P1 verdict must say so); tennis P2 does not (0.994 vs the 0.95 cut) and may headline.

## 3. Pre-verified sources (all staged; verify each folder's sha256 manifest before use; fetch nothing except B5's declared queries)

See `shared-data/<leg>/PROVENANCE.md` for URL, vintage, license and caveats per folder: tennis (ATP 1968-2026, stats 1991+, CC BY-NC-SA via archival mirror — upstream repo gone), chess (FIDE Jan 2015-2026), baseball (Lahman v14.0 to 2025 + Salaries 1985-2016 frozen + Statcast 2015-2026, the 2026 leaderboards staged in the 2b revision), entertainment (IMDb 2026-10-22; MusicLab human-gated), poker (Wikipedia wikitext, pinned revids), science (OpenAlex seeded sample), literature (6 staged PDFs + abstract-verified list).

## 4. Pre-declared constructions (per domain)

Common exclusion rule: a unit enters a domain's skill/success panel only if it meets that domain's pre-declared minimum-activity cut (below). Cuts are fixed now; changing one is a deviation.

### 4.1 Tennis (sports; the powered P2 domain)
- Panel: ATP main-tour singles (`tourney_level` ∈ {G, M, A, F}), seasons **1991-2025** (stats era; 2026 partial season excluded). Players with **≥200** matches having complete point stats.
- **Skill s_i:** career share of total points won = Σ(points won)/Σ(points played), from `w_svpt, w_1stWon, w_2ndWon, l_svpt, l_1stWon, l_2ndWon` (winner's points won include the loser's unwon service points, and vice versa).
- **Success:** primary = career titles (count of `round == 'F'` wins); secondary = Grand Slam titles; year-end ranking points (from the rankings files, last ranking date per year).
- Proxy-validity row: split-half reliability of s_i (odd vs even career matches); plus the structural-amplification caveat verbatim from `recency-research.md` §7.2. **Numeric pass/fail rule (binding, recency §7.1):** the row PASSES iff the split-half reliability r is at least the domain's success persistence (the y2y top-100 points-rank Spearman of §4.1's persistence series, averaged); if r falls below it, every tennis P2 verdict is labelled "measurement-limited", not "signature absent/present".
- **Leakage control (binding; the point-share proxy is independent in grain but not ex-ante — titles are won by winning those same points):** recompute the full set of P2 statistics with the skill measure s_i* computed **excluding all matches with `round == 'F'`** (finals, the title-deciding matches, removed from both players' point sums), reported beside the primary. The primary P2 verdict stands only if the leakage control lands in the same §6 cell; if the two disagree, the tennis P2 verdict row is "measurement-limited: leakage-sensitive", with both values shown. (Declared alternative, used only if the finals-excluded panel drops below the ≥200-match cut for the top-10 success units: an odd/even-year temporal split — skill from odd years, success over the whole career — same agreement rule.)
- Persistence series: year-end top-100 points rank, consecutive-year Spearman, 2011-2025 (and 1992-2025 as a long secondary run); dropouts excluded pairwise with the retained-n reported per pair.
### 4.2 Chess (skill-dominated control)
- Panel: FIDE January standard lists 2015-2026, elite segment (top 100 and top 1,000 by rating; the 2024 sub-2000 floor change makes the full distribution non-comparable across years — declared).
- Persistence: consecutive-January Spearman of top-100 ratings/ranks, 2015→2016 … 2025→2026 (11 pairs), with retention counts.
- P2 note (binding): Elo is both the skill measure and the de-facto success ranking, so S2 is **degenerate in chess and is not computed**; chess contributes the persistence anchor plus one qualitative row (is the #1-rated player the reigning/most-recent world champion, by January list, 2015-2026 — established from the FIDE lists plus the staged literature only; if world-champion identity cannot be established from staged files, the row is dropped, not fetched).
### 4.3 Baseball (sports)
- Team series: Lahman Teams 1961-2025: y2y win% correlation; Mauboussin-style season luck share = (0.25/162)/var(win%) per season, averaged 2015-2025. (Per §2 P3: the team series is a reported secondary, not the ladder entry.)
- Player P2 (Statcast era): skill = avg exit velocity (qualified batters) and sprint speed, per season **2015-2026** (the 2026 leaderboards are staged; the success-side series end 2025 at source, so the 2026 files enter the career skill averages and the G3 reliability series only — the skill-success pairing window is unchanged and this asymmetry is declared), career-averaged; success = (a) cumulative salary 2015-2016 (the frozen-salary overlap, declared thin), (b) All-Star selections + AwardsPlayers rows 2015-2025 from Lahman. Players with ≥3 Statcast seasons.
- Salary-era concentration: career summed salary 1985-2016, players with ≥5 salary years: top-20%/top-1% share, Gini.
- Player persistence: OPS (≥300 PA) y2y Spearman, 2000-2025. **This is the P3 ladder entry for baseball (declared per §2 P3).**
- **Numeric pass/fail rule for the baseball validity row (binding, recency §7.1):** PASSES iff the y2y reliability of the skill measurables (exit velo and sprint speed y2y r, 2015-2026, each) is at least the domain's success persistence (the OPS y2y Spearman above); below it, baseball P2 verdicts are labelled "measurement-limited".
### 4.4 Movies (entertainment, open branch)
- Panel: IMDb `titleType == movie`, `numVotes ≥ 1000` (≈49k titles at staging vintage).
- Quality proxy = averageRating (declared the weakest proxy); success = numVotes. S1, S2 (with the measurement-limited label if the validity row fails — validity row: rating-votes Spearman by votes-decile, showing the proxy is not just popularity), S4 contribution: concentration only. **Numeric pass/fail rule for the movies validity row (binding):** compute Spearman(averageRating, numVotes) within each of the 10 numVotes-deciles; the row PASSES iff the median within-decile |rho| across the 10 deciles is ≤ 0.2; otherwise every movies P2 verdict is "measurement-limited: no P2 verdict". [SET AT 2b REVISION: this constant was fixed before the within-decile statistic was ever computed; the only related preview quantity was the bulk Spearman(rating, votes) = 0.205, a different statistic, stated here for transparency.] If the realized median within-decile |rho| falls within 0.05 of 0.2, the movies validity verdict is reported as "threshold-sensitive" with the raw value stated. The full decile table ships in `results/domain_movies.csv` either way.
### 4.5 Poker (the luck-end leg, bounded by design)
- Extraction (binding, from `poker/PROVENANCE.md`): parse the staged wikitext tables by reading them row-by-row (no bulk regex over markup; a naive regex verifiably returns 0 rows). Write `results/poker_events.csv`: year, champion, runner-up where listed, entrants, prize; and from the bracelet/HoF pages: multi-bracelet counts. Spot-check 5 rows against the cited rendered revisions' values recorded in PROVENANCE (not fetched).
- **Pre-declared power statement, computed and written BEFORE any poker verdict, copied verbatim into findings:** "Under a no-skill null with field sizes n_t, the expected number of repeat Main-Event champions 1990-2025 is E_0 = [x]; under a uniform 5× skill multiple for a 10% skilled stratum it is E_5 = [y]. The observed count is [z]. With E_5 − E_0 = [d] expected events, this comparison [can/cannot] distinguish the hypotheses." Phase 2a expectation: it cannot (modern fields ≈ 8-10k). (The Main-Event power statement's Entrants inputs are verified on disk and it stays as specced.)
- **The bracelet-concentration block is DESCRIPTIVE ONLY (demoted in the 2b revision, TvL-A5).** The previously planned "multi-bracelet concentration vs a permutation null across all bracelet events" is **not computable from the staged data**: the staged bracelet article holds only a top-truncated multi-bracelet-winners table, prose-only event counts for four scattered years (14 in 1990, 24 in 2000, 58 in 2011, 74 in 2017), no per-event field sizes, and no full player population. No permutation null may be constructed or improvised mid-run. Instead, one labelled descriptive row ships: the multi-bracelet counts as read from the staged (truncated) table, with the binding caveat that concentration computed on a top-truncated list is selection-biased and lower-bound-style descriptive only — no verdict weight, no null comparison. **The poker leg's informative weight rests on the Levitt-Miles 2014 anchor** (a-priori skilled ROI +30.5% vs −15.6%), cited as literature; a proper multi-event concentration test is a next-tick item behind the Hendon Mob human gate.
### 4.6 Science
- From the staged OpenAlex 2015 sample: citation concentration (S1). Declared in-run fetch (the §0 exception): the same seeded sample query for cohorts 2010 and 2019 (two pulls, ≤25 pages each, query strings fixed to the PROVENANCE pattern with only `publication_year` changed), to show S1 stability across cohorts. No author-level analysis (Janosov/Sinatra turf; engaged in 002).
### 4.7 MusicLab (entertainment, gated branch — pre-declared)
- **IF** `shared-data/entertainment/musiclab/` exists: per social-influence world: success = downloads per song; quality = market share in the independent condition. Compute S1 per world, S2 with quality as the skill proxy (the one true ex-ante proxy in this study), and the winner-quality percentile distribution across worlds (the direct analogue of the model's Fig 8). This block then headlines P2.
- **ELSE (the honest-exclusion branch):** one labelled literature row: SDW 2006's published findings (inequality and unpredictability rise with social influence; "the best songs rarely did poorly, the worst rarely did well, but any other result was possible"), stated as qualitative support for P2's direction in few-trial reward markets, with "raw data human-gated (OPR archive); see PROVENANCE" in the findings and on the card. No invented numbers.

## 5. Pre-declared blocks

### Block A: gates (run first, in order)
1. **G1 integrity:** every staged file matches its `DATA_MANIFEST.md` sha256; row/coverage sanity per PROVENANCE (tennis 2025 complete; jan26 list ≥500k rated; Lahman Teams max year 2025; IMDb movies ≥45k at the votes cut; champions table rows ≈ 1970s-2025).
2. **G2 model reference (anchor):** run `shared-data/tvl-engine/` — 1,000 baseline runs (N=1000, m_T=0.6, σ_T=0.1, I=80, N_E=500, p_L=50, C0=10, no truncation, seeds 1..1000) → `results/tvl_reference.csv`: winner-talent mean/sd/percentile distribution, **the per-run top-10-capital median talent percentile distribution (needed for the P2 exceedance probabilities, §2)**, P(winner top-decile), P(winner T > 0.8), capital top-20% share, Gini, split-half capital-rank persistence (capital rank at t=40 vs t=80 — reported secondary, needed by 002's gate), **and the y2y persistence analogue: top-100 capital-rank Spearman between consecutive one-year windows (2 steps) in the back half of the run (t > 40), averaged — the construct-matched persistence entry for M3 and for 002's T1 distance (TvL-B2)**. PASS/FAIL per §1's audit-anchored integrity bands only (winner-talent mean/sd + top-20% share vs the staged `shared-data/qa-distcheck/distcheck_results.json` centers); the paper's printed 3% / 0.80 are never gated on; on failure stop and diagnose.
3. **G3 proxy validity:** the per-domain validity rows of §4 (tennis split-half reliability + the finals-excluded leakage control; movies decile table; Statcast y2y reliability of exit velo/sprint, 2015-2026). **Each row carries its §4 numeric pass/fail rule, so "fails its validity row" is decidable, not judgment**, and each must be reported next to its domain's verdicts.

### Block B: domains (any order after A; one `.done` per sub-block)
B1 tennis, B2 chess, B3 baseball, B4 movies, B5 science, B6 poker, B7 MusicLab branch — computing, per domain, the applicable S1/S2/S3 statistics of §2 with bootstrap 95% CIs (resample units, 1,000 draws, seed 2018) and writing `results/domain_<leg>.csv`.

### Block C: the cross-domain assembly (needs all B)
- `results/signatures.csv`: one row per domain × statistic × value × CI × n × proxy-validity flag, plus the TvL reference row from G2 and the TvL p_L={20,50,80} ladder rows.
- The ordering test (S4): persistence ranks vs P2-decoupling ranks vs concentration ranks across the domains that have each; verdict by the §6 vocabulary.
- Figures (at most 3 on the card):
  - `fig_decoupling.png`: per domain, winner-skill percentile (and top-10 median) with CIs, against the TvL baseline band (0.75) and the talent-dominated band (≥0.99);
  - `fig_ordering.png`: persistence (x) vs decoupling and vs concentration (y), domains labelled, TvL p_L ladder overlaid;
  - `fig_shapes.png`: skill vs success distributions per domain (small multiples, log scale on success).

### Block D: findings + card
`results/findings.md`: METHOD paragraph; the binding prior-art paragraph (§0); per-signature results with the §6 vocabulary; the poker power statement verbatim; the MusicLab branch label; the §2 contradiction paragraph verbatim; limitations (proxy table). Plus, binding:
- **The C22 model-side finding, one sentence:** "The paper's released engine, run faithfully, gives P(winner talent > 0.8) ≈ 8% (QA audit, 13,700 runs), not the paper's printed 3%, and the paper's printed value is distributionally inconsistent with its own released code — the printed quantities are treated throughout as the paper's claims, with the run-produced G2 values as the model-side references." This is part of what the study teaches about the paper.
- **The concurrent-work disclosure:** findings.md states that Biondo-Pluchino SSRN 6572147 (2026) is "concurrent and not yet read (metadata-verified; bot-blocked)".
- **Every [PREVIEW-CALIBRATED] constant that appears in findings.md carries its label and its neighbouring preview value (§2); every threshold-sensitive verdict says so in its row.** The same labels must appear in `gates.json` (on the G-gate band constants and the §6 band constants it records) and on the result card wherever those constants are quoted.

## 6. Pre-declared verdict vocabulary (per signature × domain; banned words outside their rows: "proves", "confirms the model", "no effect", "talent doesn't matter", "luck beats talent")

| Condition | Wording allowed |
|---|---|
| P1 present (success top-20% ≥ 0.6 and skill proxy thin-tailed) | "shape signature present (consistent with the model and with any multiplicative mechanism)" |
| P1 absent | "shape signature absent — counts against the model in this domain" |
| P2: winner-skill percentile CI within [0.55, 0.95] [PREVIEW-CALIBRATED] and P(top-decile) < 25% [PREVIEW-CALIBRATED] | "decoupling signature present at years-of-data [n]" + the §2 exceedance probabilities |
| P2: winner percentile CI ≥ 0.95 [PREVIEW-CALIBRATED; tennis preview 0.994] AND top-10 median ≥ 0.95 (both binding — the same cut pair as §2's contradiction paragraph) | "decoupling signature absent: top success coincides with top measured skill (the model's talent-dominated corner)" + the §2 exceedance probabilities |
| P2: proxy validity row failed (by its §4 numeric rule) or the tennis leakage control disagrees in cell | "measurement-limited: no P2 verdict" / "measurement-limited: leakage-sensitive" |
| P3: pre-declared ordering (chess > tennis > baseball on measured persistence; the 3-domain ladder only) exactly reproduced AND decoupling/concentration order with it | "cross-domain ordering signature present (3 measured domains; poker's luck-end placement literature-based, not counted)" |
| P3: persistence ordering holds but decoupling/concentration do not order with it (or vice versa) | "partial ordering: [state which]" |
| P3: orderings scrambled | "ordering signature absent — counts against the model's cross-domain claim" |
| any P1/P2 statistic within 0.05 of its threshold | the cell verdict + ", threshold-sensitive (raw value [v] vs threshold [t])" — mandatory per §2's rule |
| any statistic with CI spanning both bands | "uninformative: the data cannot distinguish the model band from the talent-dominated band (power: [MDE])" |

**Headline sentence template (fixed):** "Across [k] domains with independent skill measures, the model's decoupling signature is [present in …/absent in …]; the measured domains order on the skill-luck axis as [order], against the pre-declared measured ladder [chess > tennis > baseball] (poker's luck-end placement literature-based, not measured); the shape signature (fat-tailed success from thin-tailed skill) appears in [k'] of [k] — a pattern [consistent/partially consistent/inconsistent] with a talent-times-luck mechanism whose luck weight varies by domain, and [consistent/inconsistent] with the paper's baseline parameterization in which the most successful are almost never the most skilled."

## 7. Deliverables

- `report.md`, `followup_summary.json`, `result_card.json` (per the followup-studies handoff §5), `results/findings.md`, `results/fetch_log.json`.
- CSVs: `tvl_reference.csv`, `domain_{tennis,chess,baseball,movies,science,poker[,musiclab]}.csv`, `signatures.csv`, `poker_events.csv`, `gates.json`.
- Figures: the three §5-C files.

**Result card (at most 5 metrics; every metric pairs the new number with its model-side reference and cites both files; [PREVIEW-CALIBRATED] labels and threshold-sensitivity flags travel onto the card per §2; the card also carries the concurrent-unread disclosure of §0/Block D):**
- `headline`: the §6 template sentence, filled.
- **M1:** tennis winner-skill percentile (+CI) vs the G2-derived baseline winner percentile from `tvl_reference.csv` (the paper-implied 0.749 cited beside it as the paper's claim) — preview expectation: decoupling absent.
- **M2:** P(top-success ∈ top-skill decile) pooled over P2 domains vs **the G2-derived model value** P(winner top-decile) from `tvl_reference.csv` (the paper's printed 3% noted beside it as the paper's claim — the QA audit shows 3% is the paper's claim for its T > 0.8 cut and that the faithful engine gives ≈8% there and ≈25% at the true top-decile cut).
- **M3:** the persistence ladder (chess / tennis / baseball values) vs the TvL p_L ladder's **y2y persistence analogue** (G2/T1's construct-matched entry; split-half reported secondary).
- **M4:** success top-20% shares per domain vs **the G2-derived model share** from `tvl_reference.csv` (audit mean ≈ 0.774; the paper's printed 0.80 cited beside it as the paper's claim).
- **M5:** the poker power statement's E_0 / E_5 / observed triple (or, if B7-full ran, the MusicLab winner-quality percentile vs the G2-derived baseline — whichever branch is informative; pre-declared preference: MusicLab if un-gated).

## 8. Out of scope

- Prize-money/wealth series not in staged data (no scraping of ATP prize money, Hendon Mob, box office, Spotify/Billboard).
- Any new model development (002's job) and any funding-leg verdict (002's job).
- Author-level science careers (Janosov/Sinatra turf; engaged as literature in 002).
- Any fetch beyond B5's two declared OpenAlex pulls; any login; any outward message.
- WTA / women's tours this tick (the mirror has the data; a next-tick extension is noted, not run — keeping this tick lean).

## 9. Environment and compute

- CPU only, single core sufficient. Python 3 (pandas, numpy, scipy, matplotlib, pyreadr).
- **Tool-call limit:** a single shell call is capped at 10 minutes. Keep every call under ~8 minutes (the IMDb parse and the G2 engine runs both fit; if G2 threatens the cap, run it in 4 chunks of 250 seeds, checkpointing each).
- **FOREGROUND RULE:** run every command in the foreground and wait for it to finish. Never background a job (`&`, `nohup`, background-task tools), and never end the turn "to wait". Write `followup_summary.json` incrementally after each block.

---