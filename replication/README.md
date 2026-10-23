# Replication run

The authors released only a single-run NetLogo demo of the TvL model (GPL-2.0, via
ComSES); everything behind the paper's 100- and 10,000-run ensembles, funding tables
(Figures 10-12) and environment sweeps (Figures 13-14) was never published and was
rebuilt from the paper text. The claim-by-claim verdicts are in the top-level
`replication_report.md`; the step-by-step execution record is `replication_log.json`,
the environment and key results are in `evidence_summary.json`, and the exact package
versions are in `installed_packages.txt`.

## Layout

- `codebase/official_comses_tvl_v1.0.0/`: the authors' ComSES release 1.0.0 as
  downloaded (GPL-2.0; LICENSE, CITATION.cff and codemeta.json included). Only
  `docs/Talent_vs_Luck.pdf`, a copy of the arXiv paper, is omitted; see
  `../LARGE_FILES_OMITTED.md`. Provenance and the download hash are in `PROVENANCE.md`.
- `codebase/netlogo/`: `TvLmodel_orig.nlogo` (the demo as shipped) and
  `TvLmodel_single.nlogo` (the instrumented copy: a fixed seed and CSV state logging
  were added; no model rule changed), plus the BehaviorSpace experiment XML. These
  remain GPL-2.0 as derivatives of the authors' model.
- `codebase/reimpl/`: the Python reimplementation of the unreleased machinery.
  `tvl.py` is the batched engine (torch); `run_multi.py`, `run_funding.py` and
  `run_env.py` drive the ensemble, funding and environment experiments. Its fidelity
  to the NetLogo demo is checked in `outputs/fidelity/`.
- `codebase/analysis/`: the single-run analysis script.
- `codebase/outputs/`: everything the run produced, one folder per experiment
  (`single_run`, `multi_100`, `multi_10000`, `funding_fig10`, `funding_fig12`,
  `env_pL`, `env_talent`, `fidelity`).
- `codebase/PROVENANCE.md`: where the package and the paper artifacts came from, with
  hashes, plus the pointer to the unlicensed third-party Python port that is
  deliberately not included here.

## How to re-run

The NetLogo leg: install NetLogo 6.4.0 (headless) and a JDK 17, set `JAVA_HOME` and
`NL_HOME` as in `codebase/env.sh`, and run `TvLmodel_single.nlogo` with the
BehaviorSpace experiment in `codebase/netlogo/single_run_experiment.xml`. The demo is
written for NetLogo 6.0.3 and runs unchanged under 6.4.0.

The Python leg runs in seconds: `python reimpl/run_multi.py` reproduces the ensembles
(the 10,000-run ensemble takes seconds on a GPU, minutes on CPU), `run_funding.py` the
Figure 10/12 tables, and `run_env.py` the Section 3.2 sweeps. Package versions are in
`../installed_packages.txt`; numpy, torch and matplotlib are the substantive
dependencies.

Two conventions matter and are documented in the report: talent truncation to [0,1] is
a flag (the paper text says truncated, the authors' demo draws unclipped, and the
Section 3.2 results are only reproducible untruncated), and the power-law fits in the
analysis script regress over the whole support rather than the far tail.
