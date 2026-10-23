# Extension assets — index (staged 2026-10-22, Phase 2a)

Reader question (a reader, through the site, anonymous): do the model's findings corroborate with real-world data in different domains, e.g. sports, entertainment, poker?

| Folder | Leg | Size | Key contents | Gate |
|---|---|---|---|---|
| `tennis/` | sports, luck-mid domain | ~107 MB | ATP matches 1968-2026 (stats 1991+), players, weekly rankings 1990-2026 (CC BY-NC-SA 4.0, Sackmann via archival mirror — upstream repo is gone) | none |
| `chess/` | skill-dominated control | ~96 MB | FIDE January standard rating lists 2015-2026 (fixed-width TXT in zips) | none |
| `baseball/` | sports, team + salary | ~13 MB | Lahman v14.0 RData (1871-2025; salaries 1985-2016), Databank CSV zip (to 2019), Statcast exit-velo + sprint-speed leaderboards 2015-2026 (2026 staged in the 2b revision, TvL-A7) | none |
| `entertainment/` | movies (+ MusicLab gate) | ~227 MB | IMDb non-commercial title.ratings + title.basics (2026-10-22 vintage) | MusicLab raw data: HUMAN GATE (OPR archive 403s keyless) |
| `poker/` | luck-heavy end | ~0.3 MB | Wikipedia wikitext (WSOP, Main Event champions, bracelet, Poker HoF) with pinned revids, CC BY-SA | Hendon Mob bulk: HUMAN GATE (ToS) |
| `science/` | citations + funding | ~0.1 MB | OpenAlex seeded 2015-cohort citation sample (5,000 works, CC0) | none |
| `literature/` | prior art + funding lotteries | ~22 MB | 6 open PDFs (Janosov 2020, Zappalà 2023, Sobkowicz 2020, HRC-NZ, SNSF, hot streaks) + verified-by-abstract list in PROVENANCE | Bol/Denrell-Liu/Levitt-Miles/SSRN-2026 PDFs: human pull optional |
| `prep-diagnostics/` | Phase 2a previews | tiny | previews.json + prep notes — **EMBARGOED for 001 until its own estimates are written** | — |

Total ≈ 465 MB apparent. Nothing over 1 GB. Every folder has `DATA_MANIFEST.md` (sha256 per file) and `PROVENANCE.md` (URL, vintage, license, caveats).
