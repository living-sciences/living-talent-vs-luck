# Living paper: Talent versus Luck (Pluchino, Biondo & Rapisarda 2018)

This repository holds the working files behind the living-paper page
**https://livingscience.ai/econ/living-talent-vs-luck**: an AI-agent replication of the
paper's agent-based model, plus three follow-up studies that confront the model's
falsifiable signatures with the newest open data in sports, entertainment, poker and
science.

**Paper.** Pluchino, Alessandro, Alessio Emanuele Biondo, and Andrea Rapisarda. 2018.
"Talent versus Luck: The Role of Randomness in Success and Failure." *Advances in
Complex Systems* 21 (3-4): 1850014.
DOI: [10.1142/S0219525918500145](https://doi.org/10.1142/S0219525918500145).
Open-access version: [arXiv:1802.07068](https://arxiv.org/abs/1802.07068).

## What is in the repository

| Path | What it is |
|---|---|
| `replication/` | The replication run: the authors' GPL-2.0 ComSES NetLogo demo (re-hosted under its own license in `codebase/official_comses_tvl_v1.0.0/`, with provenance in `codebase/PROVENANCE.md`), the instrumented single-run NetLogo files, the Python reimplementation of the unreleased multi-run, funding and environment machinery (`codebase/reimpl/`), every output the run produced (`codebase/outputs/`), and the run's step log, evidence summary and package list. See `replication/README.md` for how to re-run. |
| `followup/001-001-living-update/` | Extension study (living update): tests the model's four pre-declared signatures against the newest open data in tennis, chess, baseball, movies, science and poker, with independent ex-ante skill proxies and the replication's own engine as the model-side reference. |
| `followup/002-002-theory-update/` | Extension study (theory update): adds a single talent-leverage dial to the engine, fits each domain's measured signature triple over an 11 x 5 calibration grid, reconciles the fits with the 2018-2026 literature, and confronts the Section 3 funding claim with the funding-lottery record. |
| `followup/003-003-corrections/` | Corrective study: applies the seven bounded labelling and reporting corrections logged by a provenance audit of 001 and 002. No verdict or estimate changed; two missing pre-declared quantities (the baseball decoupling MDE and the long-window tennis persistence) were computed and filed. Every old-to-new change is in its `results/card_corrections.csv`. |
| `specs/` | The studies' registered designs (`spec-001-launch.md`, `spec-002-launch.md`, `spec-003-corrections.md`), written and gated before the studies ran. Each study's `instruction.md` is the copy it executed under. |
| `extension-assets/` | The staged input data the extension studies read, included where the license allows (see Data below). Per-folder `DATA_MANIFEST.md` and `PROVENANCE.md` files record every URL, byte count, sha256 and fetch date (all fetches keyless, 2026-10-22), including for the files that could not be re-hosted. |
| `replication_report.md` | The replication report: claim-by-claim verdicts, score decomposition, and what did and did not replicate. |
| `referee_report.md` | A referee-style assessment of the paper informed by the replication and the follow-up studies. |
| `recency-research.md` | The recency research that scoped the extensions: the paper's 128-work citation graph triaged, the four falsifiable signatures derived, and every data source live-checked. |
| `LARGE_FILES_OMITTED.md` | Everything left out of this repository for license or copyright reasons, with exact provenance for re-fetching it. |

## Replication summary

The weighted replication score is **0.82**, with all 45 extracted claims counted: 29
reproduced, 16 diverged partially, and no claim failed outright. The authors released
only a single-run NetLogo demo; it ran essentially as shipped (logging and a seed were
the only additions), and the single-run anecdotes fall inside the model's ensemble
bands. Everything behind the 100- and 10,000-run ensembles, the funding tables and the
environment sweeps was never released and was rebuilt in Python from the text
(`replication/codebase/reimpl/`); that rebuild matched the demo's event dynamics
closely and reproduced the paper's central result, the 10,000-run best-performer talent
Gaussian (0.670 / 0.093 against the printed 0.667 / 0.09).

The fine print, stated honestly:

- **Funding and environment table offsets.** In the rebuilt Figure 10, egalitarian and
  random strategies run 2 to 5 points of P_T above the printed values, beyond the
  paper's own stated 2% run-to-run stability, and "ALL EQUAL 1u" places second behind
  "10% RANDOM 5u" rather than first. Section 3.2 values drift similarly. The ranking
  regime (egalitarian and random on top, every elitarian rule at the bottom) matches
  exactly. The likely cause is unreleased implementation details; releasing the
  authors' scripts would settle it.
- **The truncation contradiction.** The paper says talent is "truncated in the interval
  [0,1]", but the authors' released demo draws talent from an unclipped normal, and the
  paper's own Section 3.2 headline (C_mt for the sigma_T = 0.2 run) is only reproducible
  if the truncation statement is ignored.
- **The F_T arithmetic error.** The Figure 10 row "25% BEST 10u, OTHERS 5u" prints a
  total budget of 70000, but its own allocation rule gives 50000 over 8 injections.
- The power-law tail exponents did not reproduce at the printed values (pooled -1.08
  against -1.33; single run -0.87 against -1.27); part of that gap is a fit-window
  choice in the replication's own analysis script, documented in the report.

Details and per-claim rationales are in `replication_report.md`.

## Extension studies

- **001 living update.** The model's concentration signature (P1) is present in every
  domain measured, but it is consistent with any multiplicative process. The sharp
  signature, that the most successful are almost never the most skilled (P2), is
  **contradicted** where an independent ex-ante skill proxy exists: the tennis number
  one sits at the 0.994 skill percentile and the top-rated movies at 0.999, against a
  model ceiling near 0.70, configurations the baseline model produces in at most 1.3%
  and 0% of runs. The pre-declared persistence ladder (chess 0.870 > tennis 0.678 >
  baseball 0.493) reproduces exactly, but decoupling does not order with luck. The
  study also showed the paper's printed "3%" (winners with T > 0.8) is inconsistent
  with the paper's own engine, which gives about 8%.
- **002 theory update.** No member of the one-dial model family jointly fits any
  domain's measured triple: model winners top out near the 0.73 skill percentile while
  real winners sit at 0.99+, and model rank persistence is pinned near 0.96 while real
  values run 0.49 to 0.87. The funding claim, by contrast, is **robust** inside the
  model: egalitarian allocation beats elitarian on efficiency at every value of the
  talent-leverage dial, with no flip, and the real-world funding-lottery record is
  consistent with it, though no experiment yet measures the model's outcome variable.
- **003 corrections.** The provenance audit passed both studies (every audited number
  recomputed independently); this study applied its seven bounded labelling and
  reporting corrections, changed no verdict or estimate, and filed the two
  missing pre-declared quantities it computed.

## Reproducing

**The model runs in seconds.** The reimplemented engine
(`replication/codebase/reimpl/tvl.py`, Python with torch) runs batched: the 10,000-run
ensemble takes seconds on a GPU and minutes on CPU. Drivers for the multi-run, funding
and environment experiments are alongside it; exact package versions are in
`replication/installed_packages.txt`. The authors' NetLogo demo re-runs under NetLogo
6.4.0 headless (see `replication/README.md`).

**Extensions.** Python 3 with numpy, pandas, scipy, matplotlib, torch and pyreadr. The
study code is under `followup/*/workspace/code/` and reads a `shared-data/` staging
directory laid out exactly like `extension-assets/`. The shipped assets (Lahman,
OpenAlex sample, Wikipedia wikitext) cover the baseball success panel, the science and
poker legs; for tennis, chess, movies and Statcast, re-fetch the inputs per the exact
URLs and hashes in `extension-assets/*/DATA_MANIFEST.md` before re-running those blocks.
Study 002 re-runs entirely from 001's shipped `results/` plus the engine.

## Data

Everything the studies read is inventoried, with URL, vintage, sha256 and fetch date,
in `extension-assets/*/DATA_MANIFEST.md` and `PROVENANCE.md`. What ships here follows
each source's license:

- **Authors' NetLogo model** (ComSES codebase 199a298b, release 1.0.0): GPL-2.0,
  re-hosted in full with its LICENSE and citation files.
- **Lahman Baseball Database** (R package v14.0-0): CC BY-SA 3.0, shipped
  (`extension-assets/baseball/lahman_rda/`).
- **OpenAlex** 2015 article sample (seed-pinned query): CC0, shipped.
- **Wikipedia WSOP wikitext**: CC BY-SA 4.0, shipped with the four pinned revision ids
  (1368075126, 1362552102, 1379271818, 1377366948) in `wikipedia_revids.json`.
- **ATP tennis** (Jeff Sackmann / Tennis Abstract, CC BY-NC-SA 4.0, via the
  `Aneeshers/tennis-sackmann-archive` mirror because the canonical upstream returned
  404 on 2026-10-22): raw CSVs not re-hosted; derived aggregates only, manifests kept.
- **IMDb Non-Commercial Datasets**: raw TSVs not re-hosted per license; derived
  aggregates only. Information courtesy of IMDb (https://www.imdb.com). Used with
  permission.
- **FIDE rating lists and MLB Statcast leaderboards**: public records and leaderboard
  pages; raw downloads not re-hosted, derived aggregates with attribution.
- **Literature PDFs**: not re-hosted; every item's provenance and verification level is
  in `extension-assets/literature/`.

See `LARGE_FILES_OMITTED.md` for the full list of omissions with re-fetch instructions.

## Terms

The ComSES package and the NetLogo files derived from it remain under GPL-2.0. Files
derived from the Lahman database are CC BY-SA 3.0; the poker tables derived from
Wikipedia are CC BY-SA 4.0. Derived tennis aggregates carry the Jeff Sackmann / Tennis
Abstract attribution and the CC BY-NC-SA 4.0 terms of their source. Movie-side
aggregates: information courtesy of IMDb (https://www.imdb.com), used with permission.
Nothing in this repository is person-level beyond what the public sources themselves
publish (match results, rating lists, tournament tables).
