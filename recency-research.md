# Recency research: Pluchino, Biondo & Rapisarda (2018), "Talent versus Luck"

Phase 2a, econ5 living-papers batch. Prepared 2026-10-22. Every fact marked "verified" was checked against a live endpoint on 2026-10-22; URLs, byte sizes and sha256 are in `extension-assets/*/DATA_MANIFEST.md` and `extension-assets/*/PROVENANCE.md`. Anything not checked live is marked **UNVERIFIED**. Note: this session's web-search quota was exhausted before this task started; the sweep below was done through OpenAlex (the paper's full 128-work citation graph), Semantic Scholar, arXiv, the GitHub API, Dataverse/Zenodo/DataCite search APIs and direct endpoint checks — coverage of non-indexed grey literature is accordingly thinner than usual.

Companion files: `specs/spec-001-launch.md` and `specs/spec-002-launch.md` (001-living-update + 002-theory-update).

Reader question (a reader, through the site, anonymous): **do the model's findings corroborate with real-world data in different domains, e.g. sports, entertainment, poker?**

---

## 1. The replication as it finished (and why this spec does not lean on its grades)

Run: the AI-agent replication run (full mode), finished 2026-10-22. As this research was written the score stood at **0.612** (45/45 claims counted: 14 match, 27 partial, 4 no_match); the grading audit mentioned below subsequently revised the verdicts, and the final report (`replication_report.md`) carries **0.82** (45/45 counted: 29 match, 16 partial, 0 no_match).

- The evaluator's own narrative attributes essentially all partials/no_matches to single-draw stochastic scalars in a heavy-tailed process (capital lives on 10·2^k; this run's best agent drew 10·2^16 where the paper's example drew 10·2^12), not to method defects. Ensemble-stable quantities agree closely: winners' talent Normal fit **0.670/0.093 vs paper 0.667/0.09** (C23 match), P_T0 31.6% vs 32.05%, funding-table qualitative structure exact (all elitarian rows at the bottom).
- **A QA audit is re-examining the grading in parallel.** Therefore this spec anchors every model-side reference on the **paper's claims (briefing §3, C1-C6)** and on fresh runs of the replication's own engine (`replication/codebase/reimpl/tvl.py`, fidelity-checked against the authors' NetLogo), never on the 0.612 score or individual verdicts. If the audit revises verdicts, nothing in either study changes.
- Two audit findings matter for the extension: (A1) the shipped NetLogo draws talent **un-truncated**; (A2) one funding-table F_T cell (70000) is internally inconsistent (code computes 50000). The engine's `--no-truncate` convention is inherited where Section-3.2-like sweeps are run.

## 2. What the model actually predicts about real data — the four fingerprints

The TvL model is a toy; the reader's question is whether its *signatures* appear in real domains. Pre-declaring them, with what would count against the model (the specs must be able to fail):

- **P1 — shape transformation (weak test).** Gaussian-ish skill in, fat-tailed success out (C1: top 20% hold ~80%). *Weak* because any multiplicative process produces this; P1 alone can only fail the model, not confirm it. Contradiction: a domain where success is as thin-tailed as skill.
- **P2 — decoupling at the top (the sharp test).** The most successful are (almost) never the most skilled (C2/C4). Quantitatively, at baseline (p_L = 50%): the per-run winner's talent averages 0.667 — the **74.9th percentile** of N(0.6, 0.1) — and the winner comes from the top talent decile in only **~3%** of runs. This needs an *independent* skill proxy per domain or it is a tautology. Contradiction: a domain where the top-success units are systematically the top-skill units (winner's skill percentile ≈ 99+). **Phase 2a preview: tennis contradicts the strong form of P2** (see §6) — which is exactly what makes the test informative.
- **P3 — cross-domain ordering.** In the model, more luck (lower talent leverage / richer event randomness) ⇒ lower persistence of top performance, more decoupling, and (per unit of skill spread) more concentration driven by chance. Across domains, decoupling (P2) and elite persistence should order together along the skill-luck continuum, with chess as the skill-dominated control at one end and poker near the luck end. Contradiction: a luck-heavy domain (low persistence) showing *tight* top-coupling, or the ordering scrambling.
- **P4 — funding/allocation (C5).** Egalitarian or random allocation beats concentrating resources on the already-most-successful, per unit invested, at rewarding the talented. Real-world analogues: the NWO threshold natural experiment (a causal Matthew effect — the premise TvL's "naively meritocratic" scheme amplifies) and the real funding lotteries (HRC NZ, SNSF, Volkswagen). Honest status: no real-world experiment yet measures the model's outcome variable (fraction of talented ending above baseline per unit budget); P4 is testable today only as *consistency with lottery-evaluation evidence*, plus a statement of what future evidence would falsify it.

## 3. Prior art (all verified 2026-10-22; staged PDFs in `extension-assets/literature/`)

**The citation sweep:** all **128 works citing the paper** (OpenAlex W2788432705) were listed and triaged; abstracts of the empirically relevant ones were pulled. The ones that constrain novelty:

1. **Janosov, Battiston & Sinatra 2020** (EPJ Data Science 9:9; staged) — *the closest existing multi-domain test.* Film directors, music, books, science: decomposes career impact into luck (R-model, random-impact) vs individual ability (Q-model); finds luck's share comparable across creative domains and best-work timing random. **What it did NOT do:** no sports, no poker, no chess control; no independent *ex-ante* skill proxy (Q is inferred from the same impact data); no test of TvL's quantitative winner-percentile signature; no concentration-vs-persistence cross-domain ordering; no funding leg.
2. **Zappalà, Biondo, Pluchino & Rapisarda 2023** (Chaos Solitons & Fractals 176:114088; staged) — the TvL authors' own tennis study: ATP 2010-2019, an ABM where one parameter a weighs talent per point; best data-model agreement at **a ≈ 0.20-0.30** (luck dominates point outcomes). It calibrates a *different* model to match observed tournament/career stylized facts; it does **not** measure point-level skill directly from match statistics, does not test P2 (winner-skill percentile with an independent proxy), and covers one domain. A 2024 follow-up (Mathematical and Computational Applications, GA-calibrated) exists.
3. **Sobkowicz, Frank, Biondo, Pluchino & Rapisarda 2020** (Physica A 557:124899; staged) — 100-m dash: small but non-zero luck contribution among the best sprinters; the authors frame it as a *lower bound* for less-controlled domains. One domain, performance (not reward) outcome.
4. **Biondo & Pluchino 2026**, "When Talent Is Not Enough: Superstar Careers in the Arts", SSRN 6572147 — **concurrent work by the paper's own authors** (posted 2026; SSRN bot-blocked this session, metadata verified via OpenAlex; human pull recommended). Both studies must name it as concurrent and must not claim to be the first empirical confrontation of TvL with careers data.
5. Adjacent sports-luck estimates to engage in 002's reconciliation: **Csurilla et al. 2023** (3×3 basketball more luck-dependent than 5v5; IJERPH 20:2911), the **fencing ABM** (PLoS ONE 2022), **Delbianco et al. 2021** rugby Bayesian ability/luck/effort, and the authors' **APS interdisciplinarity** paper (PLoS ONE 2019: "the most talented authors are not necessarily the most successful", from publication-reputation ABM + APS data).
6. Background canon (cited by the paper or the briefing, verified): **Denrell & Liu 2012** (PNAS: top performers not the most able when extreme performance indicates unreliability — predicts our S2 statistic's direction in luck-heavy domains), **Sinatra et al. 2016** (random-impact rule, Q), **Liu et al. 2018** (hot streaks; staged), **Salganik-Dodds-Watts 2006** (MusicLab: "the best songs rarely did poorly, the worst rarely did well, but any other result was possible"), **Mauboussin 2012** (skill-luck continuum — concept engaged; his per-league luck-share numbers were NOT verified this session and must not be quoted as data; both studies compute their own persistence-based shares).
7. Funding leg: **Bol, de Vaan & van de Rijt 2018** (PNAS 115:4887: NWO near-threshold winners accumulate >2× funding, ≈ €180k more, over 8 years; "participation" dropout mechanism), **Liu et al. 2020** (HRC NZ Explorer lottery; staged), **Heyard et al. 2022** (SNSF middle-group lottery; staged), **De Peuter & Conix 2021** (modified lottery argument). These are the real-world benchmarks for C5. **UNVERIFIED this session:** the Volkswagen Experiment! lottery evaluation reports (not reachable through the APIs used); listed as an optional human pull, not load-bearing.

**The novelty argument, in one paragraph.** What exists through 2026 is: luck-vs-ability decompositions *within* creative domains from impact data alone (Janosov), single-domain ABM calibrations by the TvL group (tennis a≈0.2-0.3; sprint lower bound; arts concurrent), and single-sport luck indices. What does **not** exist, and what the spec adds: (i) a test of TvL's *specific, quantitative* winner-percentile signature (P2) using **ex-ante, independent skill proxies** (point-level dominance in tennis, physical measurables in baseball, Elo in chess, a-priori skill classes in poker via Levitt-Miles, appeal-vs-success in MusicLab if un-gated); (ii) the **cross-domain ordering test** (P3) tying concentration and top-decoupling to measured persistence on one axis with a skill-dominated control; (iii) a **like-for-like model fit** (002) that puts the TvL engine itself — not a bespoke ABM — against each domain's measured triple and reconciles the fitted luck shares with Zappalà/Janosov/Levitt-Miles; (iv) the first confrontation of the Section-3 funding table with the post-2018 lottery-evaluation record.

## 4. Data legs, verified (all 2026-10-22; hashes in per-folder manifests)

| Leg | Source and vintage | Size | License / gate | Verified how |
|---|---|---|---|---|
| Tennis (ATP) | `Aneeshers/tennis-sackmann-archive` (GitHub mirror of Jeff Sackmann's data; atp snapshot June 2026); matches 1968-2026, stats 1991+, weekly rankings 1990-2026 | 107 MB | CC BY-NC-SA 4.0 | downloaded; 2025 season complete, 2026 partial; 333 players with ≥200 stat matches |
| Chess (control) | FIDE January standard rating lists 2015-2026, `ratings.fide.com/download/standard_jan{YY}frl.zip` | 96 MB | public download | downloaded; jan26 = 531,422 rated players; fixed-width format parsed |
| Baseball | Lahman v14.0-0 RData (2026-02-11; Teams/Batting **1871-2025**, Salaries 1985-2016 frozen upstream) + Databank CSV zip (to 2019) + Baseball Savant Statcast leaderboards (exit velo, sprint speed) 2015-2025, keyless CSV endpoints | 13 MB | CC BY-SA 3.0; MLB public pages | downloaded; vintages checked in-session via pyreadr |
| Movies | IMDb non-commercial datasets `title.ratings` + `title.basics`, vintage 2026-10-22 (daily refresh) | 227 MB | IMDb non-commercial; **no public redistribution of raw TSVs** | downloaded; 49,346 movies with ≥1,000 votes |
| Poker | Wikipedia wikitext, revids pinned: WSOP main article (1379271818), Main Event champions list (1368075126), bracelet article (1362552102), Poker HoF (1377366948) | 0.3 MB | CC BY-SA 4.0 | downloaded via MediaWiki API |
| Science | OpenAlex seeded sample, 2015 journal-article cohort, 5,000 works with citation counts (query + seed pinned in PROVENANCE) | 0.1 MB | CC0 | pulled in-session |
| Literature | 6 open PDFs staged; 7 more verified by abstract/metadata (see §3) | 22 MB | various OA | downloaded / API-verified |

**A data-seam finding worth recording:** two canonical open sports-data repos are *gone* from GitHub as of 2026-10-22 — `JeffSackmann/tennis_atp` (404; only his MatchChartingProject remains) and `chadwickbureau/baseballdatabank` (404). Both survive through maintained mirrors (the archival tennis mirror, CC-licensed; the Lahman R package). The briefing's assumption "Sackmann's GitHub repos" is stale; PROVENANCE records the mirror chain. This also strengthens the case for staging everything now rather than fetching in-run.

**Gated / not staged (honest-exclusion branches in the spec):**
- **MusicLab raw data (HUMAN GATE):** the canonical release (4 experiments, 27,267 participants, 167 CSVs) lived at `opr.princeton.edu/archive/cm/`; the host 403s all keyless access, and the Internet Archive's CDX service was down during this session, so no verified mirror could be staged. A human with a browser can likely fetch it in minutes. Until then the MusicLab block runs on published summary numbers only, labelled literature-based.
- **The Hendon Mob (HUMAN GATE, standing):** ToS-gated; no scrape. Without it the poker leg is bounded to Main-Event/bracelet recurrence + Levitt-Miles.
- Box-office revenue (Box Office Mojo/The Numbers), Spotify/Billboard charts: scrape-gray, excluded; IMDb votes is the declared success measure for movies.
- Bol et al. / Denrell-Liu / Levitt-Miles / Biondo-Pluchino-2026 publisher PDFs: bot-blocked; key numbers verified from abstracts; optional human pulls.

## 5. Per-domain measurement design and its honest limits

| Domain | Skill proxy (ex-ante / independent?) | Success measure | Known contamination, declared |
|---|---|---|---|
| Tennis | career share of total points won, tour-level matches with stats, min 200 matches (fine-grained: ~10^4-10^5 points per player; a performance measure but far less luck-amplified than titles) | career titles (primary); Slam titles, peak year-end points (secondary) | point share is itself performance, not pure ability; amplification point-→match→title is partly *structural* (best-of-N), not TvL-style event luck — 002 addresses this with the Zappalà reconciliation |
| Chess | FIDE Elo (explicit, pooled over all games) | elite-rank persistence; world-champion-vs-top-rating concordance | Elo and success both derive from game results — declared; chess serves as the *persistence control*, not a P2 domain |
| Baseball | Statcast physical measurables: exit velocity, sprint speed (close to pure tools) | salary (1985-2016 career sums; 2015-2016 season overlap with Statcast), awards/All-Star (to 2025) | salary era and Statcast era barely overlap (2015-16) — declared; team-level win% luck share is the clean long series |
| Movies | IMDb averageRating (audience quality judgment) | numVotes (popularity/reach) | averageRating is post-hoc and socially influenced — the weakest proxy; labelled; MusicLab (if un-gated) is the clean version: appeal in the independent world = the only true ex-ante quality measure in any leg |
| Poker | Levitt-Miles a-priori skill classes (literature); none in staged data | Main-Event wins/final tables, multi-bracelet counts | power problem at modern field sizes (see §6); persistence analysis needs Hendon Mob (gated) |
| Science | none staged (Q-model is Janosov's turf) | citation concentration (sample) | P1-only leg + funding natural experiment via literature |

## 6. Phase 2a previews (embargoed for 001 until its own estimates are written; `extension-assets/prep-diagnostics/previews.json`)

Model-side reference (from the paper's claims; to be re-derived by 001's gate G2 with the replication engine): winner-talent mean 0.667 ⇒ **74.9th percentile** of the talent distribution; P(winner from top talent decile) ≈ **3%**; capital top-20% share ≈ **0.80**.

| Domain statistic | Preview value |
|---|---|
| Tennis: skill (point share) distribution | mean 0.502, sd 0.012, skew 0.75 — tight, near-symmetric: P1's "Gaussian input" confirmed |
| Tennis: titles top-20% share (among 333 qualifying players) | **0.639** (top 1% of players hold 12.6% of titles) — fat-tailed success: P1 holds |
| Tennis: #1-success (Federer, 103 titles) skill percentile | **0.994**; top-skill (Djokovic, point share .5447) has 101 titles; Spearman(skill, titles) = **0.79** |
| Chess: top-100 y2y rank persistence (jan25→jan26) | Spearman **0.886**, 100/100 retained |
| Tennis: top-100 year-end points persistence (2011-2025) | Spearman **0.645** |
| MLB: team win% y2y (1961-2025) | r **0.50**; binomial-variance luck share of a 162-game season ≈ **0.24** |
| MLB: 2016 salary top-20% share | 0.656 (852 players) |
| Science: 2015-cohort citations | top-20% share **0.928**; 57.3% uncited |
| Movies: votes top-20% share | 0.883; most-voted films sit at the **99.9th** rating percentile, yet bulk Spearman(rating, votes) = **0.205** |

**The sharpest preview finding — and the spec's honest centre:** tennis **contradicts the strong form of P2**. Success is wildly amplified relative to a near-Gaussian skill measure (P1 ✓), but the very top of success *is* the very top of skill (winner at the 99.4th skill percentile; TvL baseline predicts ~75th and only 3% chance of top-decile). Movies show the same pattern at the extreme top. This is exactly Denrell & Liu's boundary condition: where performance aggregates over very many trials (tennis careers ≈ 10^4-10^5 points), extreme success *is* informative about skill; TvL's winner-percentile signature should emerge only where luck per trial is large and trials are few (poker tournaments, single hits). So the spec's P2/P3 test is genuinely two-sided: domains will fall on both sides, and the cross-domain *gradient* — not a blanket "luck beats talent" — is the quantity the model must predict to survive. The funding and MusicLab legs test the model where it claims to live (multiplicative reward dynamics on few, large shocks).

**Power notes (pre-declared in the spec):**
- Poker Main Event: with modern fields (≈ 8,000-10,000 entrants) even a 5× skill multiple gives a repeat-champion probability near zero over 20 years; the pre-registered power statement will likely declare repeat-win counts uninformative, and the leg's informative outputs are the multi-bracelet concentration (smaller fields, many events) and the Levitt-Miles ROI anchor. This is stated up front so the judge does not get an "uninformative by design" surprise.
- Tennis S2 is powered: 333 qualifying players, winner-percentile sampling noise ≈ ±0.03 at worst (bootstrap in-spec).
- Chess-vs-tennis persistence difference (0.886 vs 0.645 preview, 14 + 1 year-pairs) is large relative to year-to-year scatter; the ordering test has real resolution across its 4-6 domains, but with ≤6 domains the S4 ordering verdict is pre-declared as exact-match / partial / scrambled rather than a p-value.

## 7. Biggest risks for the spec

1. **Proxy contamination** (§5 table). Mitigation: each domain carries a declared proxy-validity row (the proxy's own split-half/y2y reliability), and any P2 verdict where proxy reliability < success persistence is labelled "measurement-limited".
2. **Structural vs TvL amplification in tennis.** Best-of-N scoring amplifies small point-skill edges deterministically — concentration there is not evidence of TvL-style event luck. 002's calibration must separate the two (the TvL engine has no tournament structure; the reconciliation with Zappalà's point-level a handles this explicitly), and 001's P1 rows must not be sold as supporting the model's *mechanism*.
3. **Chess rating-floor changes** (2024 compression below 2000) — elite-segment analyses only; declared in PROVENANCE.
4. **IMDb redistribution limits** — results publishable, raw TSVs never pushed to a public repo.
5. **The Wikipedia-table extraction** in the poker leg must follow the agent-read rule in `poker/PROVENANCE.md` (a naive regex verifiably fails on this markup).
6. **Concurrent-author work** (Biondo-Pluchino 2026 SSRN, unread). Risk of overlap with our entertainment leg; mitigated by naming it, and by our legs (sports/chess/poker/funding/cross-domain ordering) being outside "superstar careers in the arts".

## 8. Open items for a human (none blocks launch)

1. **MusicLab zip** from `opr.princeton.edu/archive/cm/` (browser; minutes) → unlocks the clean P2 entertainment block (001 B7 full branch).
2. **Hendon Mob** licensed bulk (or an agreed export) → upgrades the poker leg to a real persistence analysis (next tick, not this one).
3. Publisher PDFs: Bol et al. 2018, Denrell & Liu 2012, Levitt & Miles 2014, and the **Biondo-Pluchino 2026 SSRN concurrent paper** (read before the extension report is published).
4. Optional: Volkswagen Experiment! lottery evaluation reports (grey literature, not API-reachable this session).
