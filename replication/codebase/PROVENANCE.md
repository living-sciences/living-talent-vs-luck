# Provenance — pluchino-etal-2018-talent-vs-luck package

All fetches 2026-10-22, by the Phase 0 prep agent. No registration or license gate was
bypassed; every item below was served to an anonymous HTTP client.

## Paper

| Item | URL | Date | sha256 | Notes |
|---|---|---|---|---|
| `../paper.pdf` | https://arxiv.org/pdf/1802.07068v3 | 2026-10-22 | 0dec3daa3536c5f4e414d7c9d5e28e91c70f369928236ed6a48601c0f5dea20b | arXiv v3 (2018-07-09), the latest version. Open-access author version; the published version (Advances in Complex Systems 21(3-4) 1850014, doi:10.1142/S0219525918500145) is paywalled at World Scientific and was deliberately NOT fetched. |
| `../supplementary/arxiv_source_1802.07068v3.tar.gz` | https://arxiv.org/e-print/1802.07068v3 | 2026-10-22 | 00f364dd5c754b40b4f71d6b4f2964ad91ea83e40309c0eb07b414da3d34f774 | LaTeX source + the 14 figure PNGs; extracted to `../supplementary/arxiv_source_v3/`. The .tex is the authoritative source for every printed parameter and number. arXiv license: non-exclusive distribution (default arXiv license). |

## Official code (the authors')

| Item | URL | Date | sha256 | License |
|---|---|---|---|---|
| `tvl_comses_v1.0.0.zip` → `official_comses_tvl_v1.0.0/` | https://www.comses.net/codebases/199a298b-fe95-473e-ad39-0fd69b5ff61c/releases/1.0.0/download/ | 2026-10-22 | 987a57b276d666b6ece6b7e1e2a38a6a9c2c6ce3397d99ab1ed3587a20c2a0a5 | **GPL-2.0** (LICENSE in zip; confirmed on the ComSES landing page, saved at `../supplementary/provenance/comses_tvl_landing_2026-10-22.html`) |

- ComSES / CoMSES Net (Open ABM) codebase "Talent vs Luck: the role of randomness in
  success and failure", release 1.0.0, published 2018-07-15, authors Alessandro Pluchino,
  Alessio Emanuele Biondo, Andrea Rapisarda — the same authors as the paper, and the
  repository the paper's own footnote points to ("A demo version of the NetLogo code of
  the TvL model ... can be found on the Open ABM repository - https://www.comses.net/codebases/").
  Download required no login.
- Contents: `code/TvLmodel.nlogo` (NetLogo 6.0.3, 929 lines), `docs/Talent_vs_Luck.pdf`
  (a copy of the arXiv paper), LICENSE, CITATION.cff, codemeta.json.
- **Scope caveat:** this is the single-run DEMO the paper describes. It implements setup +
  the event random walk + the double/halve rules and the single-run plots. It does NOT
  contain the multiple-run machinery, the funding-strategy experiments (section 3.1) or
  the environment experiments (section 3.2) — those were never released and must be
  reimplemented from the paper text.
- **Code-vs-paper discrepancy to carry into replication:** the paper says talent is
  "truncated in the interval [0,1]"; the demo's SETUP uses a bare
  `random-normal mean-talent stdev-talent` with no clipping. Also, the demo's GO handles
  at most ONE event per agent per step (`one-of events in-radius 1`), a detail the paper
  text does not state. The replication should document which convention it follows and
  show sensitivity.
- Author personal site www.pluchino.it (which historically mirrored a TvL NetLogo file)
  was unreachable on 2026-10-22 (connection failure); not pursued further.

## Third-party reimplementations (cross-checks ONLY — not the authors' code)

| Item | URL | Date | sha256 | License |
|---|---|---|---|---|
| `third_party/hviidhenrik_master.tar.gz` → `third_party/hviidhenrik_talent_vs_luck_simulation/` | https://github.com/hviidhenrik/talent_vs_luck_simulation (tarball of master, last updated 2021-12-25) | 2026-10-22 | 5c18ee7b6c09a1ba2b51c033ac8145c8f506de7998efb553e29ccfe9c302939b | **NONE declared** → all rights reserved. Staged for INTERNAL cross-check reading only; must never be redistributed or copied into the public living-paper repo. |

Recorded but NOT staged (for the record only):
- https://github.com/Raphaaella/Computational-Modeling---Talent-vs.-Luck — university
  replication + critique notebooks, 75 MB, no license. Not pulled (size + no license).
- Assorted other small reimplementations found on GitHub (tr1v3r/simulation,
  CB2Moon/Talent-vs-Luck-Simulation, IUoH/TVL, sobabear/SuccessParadox, a Julia port by
  Zeki-Zhang) — all 0-star, unlicensed; URLs kept here in case a cross-check is wanted.

Primary verification target is the paper's printed numbers + the official GPL-2.0 NetLogo
demo, not any third-party port.

## Human-gated items

- **Publisher PDF (World Scientific)**: paywalled. Not needed — arXiv v3 is the open
  version and the batch note says never to re-host the publisher PDF. No action required
  unless a page-number-exact citation to the journal version is ever needed (library access).
- No other gates were encountered: the ComSES download is open, arXiv is open.
