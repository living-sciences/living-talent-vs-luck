# Study 003 — Corrective study: audit-conformance fixes for studies 001 and 002

## Question

A provenance audit of the two completed follow-up studies — **001** (living update:
TvL signatures vs the newest open data) and **002** (theory update: fitting the
TvL engine to the measured signatures) — passed both (every audited number was
recomputed independently; no fabrication, no gate fudging) but logged **five
bounded labelling/reporting corrections on 001** and **two cosmetic notes on 002**.
This study applies **exactly those seven corrections and nothing else**. No verdict
row changes and no estimate changes were made. Two pre-declared elements that were
missing or unreported were *computed* and their true values filed (the baseball P2
MDE, and the long-tennis persistence mean), per the binding framing rule that a
missing element is computed and the TRUE value filed, an undeclared deviation is
declared (never erased), and nothing is relabelled as better than it is. Every
old→new change is recorded in `results/card_corrections.csv`.

## Approach

All corrections edit files **in place** in `followup/001-001-living-update/` and
`followup/002-002-theory-update/`. The two computations reuse study 001's own code
and the read-only staged data (`followup_staging/shared-data/`); no engine run, no
fetch, no new package beyond the ones 001/002 already used. The baseball panel was
reconstructed with 001's exact `b3_baseball.py` loaders and bootstrap seed (2018),
which reproduced the stored `winner_skill_pct = 1.0` and CI `[0.397, 1.0]` bit-for-bit
before any MDE was derived. New computation artifacts are filed under 003's
`results/` (`baseball_mde.json`, `tennis_long_persistence.json`, two figures).

## Results

### Study 001 corrections

**001-1 — judge's round-2 provenance sentence (findings.md).** The P2 movies
validity row quoted the 0.2 within-decile cut (`median within-decile |ρ| 0.023 ≤ 0.2`)
without its provenance. Added the exact sentence *"[SET AT 2b REVISION: this
constant was fixed before the within-decile statistic was ever computed; the only
related preview quantity was the bulk Spearman(rating, votes) = 0.205, a different
statistic, stated here for transparency.]"* The 0.205 preview and the 0.2 cut are
now explicitly distinguished.

**001-2 — truncation deviation declared (findings.md + followup_summary.json).**
Spec §5 Block A G2 says "no truncation"; the G2 run used `truncate_talent=True`,
consistent with the staged QA distcheck anchor bands (themselves computed with
truncation ON). Added one deviation line naming the spec-text conflict and the
resolution (construct-consistency with the anchor; truncation clips ~3×10⁻⁵ of
talent draws, numerically immaterial to every G2 band and reference value).

**001-3 — baseball P2 MDE computed (findings.md + `results/baseball_mde.json`).**
The "uninformative" baseball P2 verdict omitted the §6-required `(power: [MDE])`
clause. **Computed outcome:** the test statistic is `winner_skill_pct`, the skill
percentile of the single highest-success player (exit velocity vs All-Star+awards,
n = 431). Reconstruction reproduces the point estimate **1.0** and bootstrap SD
**0.134**; the bootstrap distribution is heavily piled at the 1.0 ceiling (37.5% of
resamples) with 87.8% of mass in the talent-dominated band (≥0.95), yet its 2.5th
percentile reaches 0.397 — which is why the 95% CI `[0.40, 1.00]` spans both bands.
The Gaussian one-sided detection distance from the 0.95 boundary at 80% power / α=0.05
is **MDE ≈ 0.33 skill-percentile points**, *larger* than the 0.25-point gap from the
model baseline (0.696) to the boundary (0.95) — so the bands genuinely cannot be
separated. The MDE is a **lower bound**: `winner_skill_pct` is a single
success-ranked order statistic bounded at 1.0 with the estimate at the ceiling, so
the sampling distribution is boundary-piled and non-Gaussian and no tighter effect
is resolvable. This is the data-supported reading: a true, finite MDE that is simply
too large for the test to be informative (not a clean "undefined"), filed with its
caveat. The verdict text ("uninformative") is unchanged.

**001-4 — long-tennis persistence reported (findings.md + domain_tennis.json +
`results/tennis_long_persistence.json`).** `domain_tennis.json`'s 1992–2025 top-100
persistence mean was NaN (the four pairs 1992→1993 … 1995→1996 have no point-level
data; ATP point statistics begin 1996 in the staged feed) and unreported. **Exclusion
rule declared:** pairs where either season lacks point-level statistics are excluded.
The non-NaN-pair mean over the 29 valid pairs (first valid 1996→1997) is **ρ̄ = 0.622**
(range 0.354–0.831), consistent with the headline 2011–2025 mean 0.678. The four-pair
pre-1996 gap is declared, not imputed.

**001-5 — reporting-gap bundle (one sentence each, findings.md erratum appendix;
(d) is a chess prose fix).**
- (a) M2 reports **per-domain** conditional overlaps (0.67 / 0.20 / 0.42) rather than
  the spec's single pooled statistic — declared; per-domain numbers kept.
- (b) The headline shape clause "**4 of 4** domains" departs from the pre-declared
  **k=3** shape template (science is the added 4th concentration-only domain) —
  declared; count retained.
- (c) The baseball OPS y2y ladder entry (mean 0.493, 23 pairs) is **missing the
  2019→2020 and 2020→2021 pairs** — the 60-game 2020 season empties the ≥300-PA cut —
  declared; mean unchanged.
- (d) `domain_chess.json` prose "**2015-2023**" → "**2015-2026**" (the range of that
  file's own #1-rated-id table).
- (e) S4 ranked **raw** top-20% concentration, not concentration "**per unit of skill
  spread**" — declared; the raw ranking and the ordering verdict (which rests on the
  winner-skill ordering) are unchanged.

### Study 002 corrections

**002-1a — truncation note inherited (report.md + followup_summary.json).** Added
the 001-2 truncation deviation to 002's deviations list, noting 002's α-dial grid and
anchor inherit `truncate_talent=True` and remain bit-identical to 001's baseline at
α=1.

**002-1b — numpy repr cleaned (predictions.json).** The P1 tennis prediction's
`model_prediction` and `falsifies_model_if` text fields leaked
`[np.float64(0.962), np.float64(0.964)]`; cleaned to `[0.962, 0.964]` in both.
Formatting only — the numeric interval `[0.962, 0.964]` is unchanged (and the
structured `interval.model_band` field already held plain floats).

### Comparison table (nothing moved that was a verdict or estimate)

| Item | Quantity | Before | After | Nature |
|---|---|---|---|---|
| 001-3 | baseball P2 `winner_skill_pct` | 1.0, CI [0.40,1.00] | 1.0, CI [0.40,1.00] (unchanged) + MDE ≈ 0.33 | missing power clause **computed & filed** |
| 001-4 | tennis 1992–2025 persistence mean | NaN (unreported) | 0.622 over 29 non-NaN pairs | missing value **computed & filed**, gap declared |
| 001-1/2/5, 002-1a/1b | labels / deviations / prose / repr | — | declared / fixed | label & reporting only, **no estimate change** |

### Figures
- `fig1_baseball_mde.png` — the baseball `winner_skill_pct` bootstrap against the two
  bands: mass piles at the 1.0 ceiling but the 95% CI reaches 0.40, spanning both
  bands; MDE ≈ 0.33 > the 0.25-pt gap → uninformative (item 001-3).
- `fig2_tennis_long_persistence.png` — the 1992–2025 tennis persistence series with
  the declared 1992–1996 no-point-data gap, the non-NaN-pair mean 0.622, and the
  headline 2011–2025 mean 0.678 (item 001-4).

## Deviations & limitations

- **Scope is exactly the seven audited corrections.** No verdict row and no estimate
  was changed; the two computed numbers (MDE, long-tennis mean) fill pre-declared
  elements that were missing/unreported, consistent with the binding framing rules.
- **Baseball MDE is reported as a finite lower bound, not a clean "ill-defined".** The
  data support a concrete Gaussian-approximation MDE (≈0.33 pct-pts) that already
  exceeds the resolvable gap; the deeper reason the test is uninformative — a single
  boundary-piled order statistic — is stated as the caveat that makes 0.33 a lower
  bound rather than claiming the quantity is undefined. The instruction's "n_success≈10"
  cue refers to the small effective leader panel; here the top success magnitudes run
  70/59/46/… with a unique max, but the single-order-statistic logic is the same.
- **New computation files live under 003's `results/`** (not 001's), per the
  write-scope rule; 001's findings.md points to them. Edits to 001/002 files are in
  place, as the corrective instruction directs.
- No engine run, no fetch, no new package; foreground only.
