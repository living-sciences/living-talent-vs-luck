# Corrective study: 003-corrections — audit conformance fixes for 001 and 002

The provenance audit passed both studies (every audited number recomputed independently;
no fabrication, no gate fudging) with five bounded labeling/reporting corrections on 001
and two cosmetic notes on 002. This study applies exactly those corrections and nothing
else. No verdict row changes; no estimate changes. Record every old → new change in this
study's `results/card_corrections.csv` (file, item, old, new, reason).

Framing rules (binding): nothing is relabelled as better than it is; a missing
pre-declared element is computed and the TRUE value filed (or the pre-declared
ill-defined branch stated); an undeclared deviation is declared, never erased.

## Corrections — study 001 (`followup/001-001-living-update/`)

1. **001-1 (the judge's round-2 condition).** In results/findings.md, the P2 movies
   validity row quotes the 0.2 constant ("median within-decile |ρ| 0.023 ≤ 0.2") without
   the provenance sentence. Add the exact sentence "[SET AT 2b REVISION: this constant
   was fixed before the within-decile statistic was ever computed; the only related
   preview quantity was the bulk Spearman(rating, votes) = 0.205, a different statistic,
   stated here for transparency.]" (or an explicit pointer to the gates.json copy) to
   that findings row.
2. **001-2 (declare the truncation deviation).** Spec §5 Block A G2 says "no truncation";
   the run used truncate_talent=True, consistent with the QA distcheck anchor bands
   (themselves computed with truncation ON; clips ~3e-5 of draws, numerically
   immaterial). Add one line to 001's deviations list naming the spec-text conflict and
   the resolution chosen (construct-consistency with the anchor).
3. **001-3 (baseball MDE).** The baseball "uninformative" P2 verdict omits the
   §6-required "(power: [MDE])" clause. Compute and state the MDE, or state precisely
   why an MDE is ill-defined for a rank statistic at n_success≈10 — whichever the data
   genuinely supports; file any computation in results/.
4. **001-4 (long tennis secondary).** domain_tennis.json's 1992-2025 persistence mean is
   NaN (1992-1996 pairs have no points data) and unreported. Report the non-NaN-pair
   mean with the gap declared (or state the exclusion rule), in findings.md and the JSON.
5. **001-5 (reporting-gap bundle; one sentence each in a findings erratum/appendix):**
   (a) M2 reports per-domain conditional overlaps rather than the spec's pooled
   statistic — state the deviation (keep the per-domain numbers); (b) the headline shape
   clause "4 of 4 domains" is off the k=3 template — state it; (c) baseball OPS y2y
   lacks the 2019→2020 and 2020→2021 pairs (COVID ≥300-PA emptiness) — declare;
   (d) fix domain_chess.json prose "2015-2023" → "2015-2026" (its own table's range);
   (e) S4 tested raw concentration ordering, not "per unit of skill spread" — state it.

## Corrections — study 002 (`followup/002-002-theory-update/`)

6. **002-1a.** Inherit the 001-2 truncation note into 002's deviations list.
7. **002-1b.** Clean the two `np.float64(…)` repr strings leaked into predictions.json
   prediction-text fields (values unchanged, repr formatting only).

## Where things live

001 outputs: `followup/001-001-living-update/`; 002 outputs:
`followup/002-002-theory-update/`. Staged data (read-only):
`followup_staging/shared-data/`. Edit files in place.

## Deliverables

report.md (one short section per item, including the true baseball MDE outcome and the
long-tennis value); results/card_corrections.csv; corrected files in place;
result_card.json for THIS study (status completed when all seven are done).

## Rules

Foreground only; no fetches; no new packages; `--timeout 7200`.
