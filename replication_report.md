# Replication Report

**Generated:** 2026-10-23 05:08:42

---

## Executive Summary

**Mode:** full

**Replication Score: 81.9%** (45/45 claims counted)

**Score decomposition** (substantive vs benign):

| Bucket | Claims | Ids | In score |
|---|---|---|---|
| Reproduced | 29 | C3, C4, C5, C6, C7, C8, C11, C13, C14, C15, C16, C18, C20, C21, C23, C25, C26, C27, C28, C29, C30, C32, C34, C36, C38, C39, C40, C44, C45 | counted |
| Diverged (substantive) | 16 | C1, C2, C9, C10, C12, C17, C19, C22, C24, C31, C33, C35, C37, C41, C42, C43 | counted |
| Not attempted: not shipped by the authors | 0 | — | counted as 0 |
| Not attempted: environment / toolchain | 0 | — | excluded |

## Evaluation & Synthesis

*Authored by the post-replication evaluator; advisory narrative, not part of the Replication Score.*

### Important Claims

The paper's thesis is that luck, not talent, drives extreme success, and that egalitarian funding beats meritocratic funding. The four headline claims carry this. C7 (the most successful agent has near-mean talent while the most talented agent stays poor) reproduces: match, with the paper's values inside a 300-run ensemble band and the run's own draw showing the same pattern. C23 (over 10000 runs the best-performer talent is Gaussian with mean 0.667, std 0.09) reproduces almost exactly: the run gave mean 0.670, std 0.093. C17 (the pooled 100-run capital distribution is a power law with slope -1.33) is partial: the shape is a clear heavy tail but the exponent came out shallower (-1.08). C31 (the Figure 10 funding table, egalitarian 'ALL EQUAL 1u' is the single most efficient strategy) is partial: egalitarian and random strategies do occupy the top and every elitarian 'BEST' strategy sits at the bottom, but 'ALL EQUAL 1u' lands second (E_norm 0.986) behind '10% RANDOM 5u'. The central message of each headline claim is reproduced; only two exact anchor numbers diverge.

### Replication Summary

This is a solid, honest replication of a model whose qualitative conclusions are robust. Score 0.82. Of 45 claims, 29 reproduced fully and 16 are partial, with zero no-match and zero blocked or out-of-scope, so the score reflects degree of numeric agreement, not coverage gaps. The score captures that the big-picture findings all hold while many exact scalars drift. It does not capture that most of the drift is inherent to the paper's own method: the paper illustrates a stochastic model with single-run anecdotes (sections 2.1 and the Figure 7/8 illustrative runs), and the replication showed, with generated ensembles, that the paper's printed numbers are often one atypical draw rather than the model's typical value. Attribution splits three ways. Some partials are the paper's anecdotal numbers sitting in the tail of the model's own distribution (paper-side, and inherent to the presentation). Some trace to a reimplementation the agent had to build because the authors never released the multi-run, funding, or environment code. One recurring partial (the power-law exponent) traces to a fit-window choice in the replication's analysis script. The run's own values diverge from the paper in the honest direction (more extreme, not tuned toward the paper), which supports the ensemble-based grading.

### What Did Not Replicate

No claim failed outright; the 16 partials cluster into three causes. Power-law exponents (C1 single-run -0.87 vs -1.27; C17 pooled -1.08 vs -1.33): the replication's analysis script fits the whole upper support C>=10, including the mode, rather than the far tail the paper fits, which biases the slope shallower (code audit A3, assurance 'rerun'); for the single run the audit's tail-only refit is even shallower, so that gap is also a more-unequal random draw, while the 100-run offset is a systematic ~3.5 sigma below the replication's own ensemble band. Single-run fine statistics (C9 lucky-event fit, C10 average event counts, C12 share experiencing one event type): the paper's illustrated run sits just outside the model's central-95% band for these quantities, so the paper's anecdote is atypical rather than the replication being wrong. Reconstructed multi-run, funding, and environment quantities (C19, C22, C24, C31, C33, C35, C37, C41, C42, C43): the egalitarian and random funding strategies run about 2 to 5 points higher in P_T than the paper, exceeding the paper's own stated 2% run-to-run stability, which is most likely a reconstruction-fidelity difference in code the authors never shipped. In every case the regime and ranking match; only the exact numbers drift.

### Whole-Paper Consistency

The produced results are consistent with what the paper describes overall. The capital distribution is heavy-tailed and Pareto-like (top 20% hold ~83%, C6 match). A tiny handful of agents reach very high capital while most stay below the starting level (C3, C5 match). The most successful agents cluster at medium-high talent near 0.667 rather than at the top of the talent range (C23 match, the paper's core 'luck beats talent' point). Egalitarian and random funding dominate meritocratic funding across both the variable-budget and fixed-budget tables (C31, C37). Where numbers differ they differ in magnitude within the same regime, not in direction, so the paper's narrative is supported end to end.

### Repository Divergence

Section 2.1 ran the authors' shipped NetLogo model essentially as-is; the only changes were logging and a seed, so that path is faithful to the repo. For sections 2.2 to 3.2 there is no shipped implementation, so the agent wrote a Python/torch reimplementation (reimpl/tvl.py and its drivers) instead of running the authors' code, because none exists. That reimplementation makes choices the demo does not: it uses an explicit toroidal world with period 201 (reimpl/tvl.py:34, W=201) following the paper's stated periodic boundary, and it defaults to clamping talent to [0,1] (reimpl/tvl.py:93) which the demo does not, toggled off for the section 3.2 runs to match the paper. The fidelity self-test (outputs/fidelity/compare.json) shows the reimplementation matches the NetLogo demo closely on event dynamics (mean lucky 1.49 vs 1.61, frac_neutral 0.174 vs 0.164) but under-produces the capital tail on a single matched draw (reimpl C_max 640 vs NetLogo 10240). That thinner tail is consistent with the reimplementation-based power-law slopes coming out shallower than the paper's, and is the clearest code-path divergence to flag.

## Tier Breakdown

| Tier | Match | Partial | No match | Not attempted | n/a | Missing | Total |
|---|---|---|---|---|---|---|---|
| Headline | 2 | 2 | 0 | 0 | 0 | 0 | 4 |
| Supporting | 27 | 14 | 0 | 0 | 0 | 0 | 41 |

## Per-Claim Verdicts

| ID | Tier | Type | Status | Rationale | Evidence |
|---|---|---|---|---|---|
| C1 | supporting | scalar | partial | The run produced a single-run power-law slope of -0.8658 (outputs/single_run/single_run_metrics.json, field 'powerlaw_slope'; figure outputs/single_run/fig3_distribution.pdf pan... | 9 file(s) |
| C2 | supporting | figure | partial | The run produced the Figure-3 plot at outputs/single_run/fig3_distribution.pdf (mtime 2026-10-22 15:16:50, postdating the replication start; emitted by analysis/analyze_single_r... | 5 file(s) |
| C3 | supporting | scalar | match | The run produced n_above_500=8 (outputs/single_run/single_run_metrics.json, field 'n_above_500'; stdout of plan step 3). I independently recomputed from the run-produced outputs... | 8 file(s) |
| C4 | supporting | scalar | match | The run produced top20_capital_share = 0.5688692957763831 = 56.89% (outputs/single_run/single_run_metrics.json, field 'top20_capital_share'; plan step 3 stdout 'top20_capital_sh... | 9 file(s) |
| C5 | supporting | scalar | match | The run produced frac_below_10 = 0.403 = 40.3% (outputs/single_run/single_run_metrics.json, field 'frac_below_10'; plan step 3 stdout 'frac_below_10=0.403'). analysis/analyze_si... | 10 file(s) |
| C6 | supporting | qualitative | match | The run produced this claim's quantity directly. analysis/analyze_single_run.py (lines 73-77) sorts the final-tick capital array ascending, takes k80=floor(0.8*N)=800, and repor... | 7 file(s) |
| C7 | headline | scalar | match | This is a single-run anecdote (seed-dependent draw). The replication's own single run (seed 12345, outputs/single_run/single_run_metrics.json) produced C_max=10240 with talent_a... | 3 file(s) |
| C8 | supporting | scalar | match | Single-run anecdote (seed-dependent draw), so the paper's printed numbers are themselves one draw and are graded against the model's run distribution, not by point equality. The... | 4 file(s) |
| C9 | supporting | scalar | partial | This is a single-run stochastic anecdote (Fig 5c,d). The replication reproduced both event-count distributions as decaying exponentials: the analysis script (analysis/analyze_si... | 6 file(s) |
| C10 | supporting | scalar | partial | The claim is a single-run anecdote (paper p.8, confirmed via pdftotext: 'averages 1.35 and 1.66, respectively' for lucky/unlucky — paper_value is accurate, no extraction error).... | 6 file(s) |
| C11 | supporting | scalar | match | Single-run anecdote (stochastic). The paper's printed values were confirmed verbatim via pdftotext of p.8: 'the maximum numbers of lucky or unlucky events occurred were, respect... | 4 file(s) |
| C12 | supporting | scalar | partial | Single-run anecdote (paper p.8). The printed values were confirmed verbatim via pdftotext of page 8: 'about 16% of people had a ”neutral” life, without lucky or unlucky events a... | 4 file(s) |
| C13 | supporting | scalar | match | This is a single-run anecdote (seed-dependent draw), so the paper's printed numbers are themselves one draw on trial against the model's run distribution; point equality is not ... | 3 file(s) |
| C14 | supporting | scalar | match | This is a single-run stochastic anecdote. The replication ran the authors' NetLogo model as shipped at the paper's section-2.1 settings (seed 12345) and the single_run_metrics.j... | 6 file(s) |
| C15 | supporting | figure | match | The run produced outputs/single_run/fig5_events.pdf (mtime Oct 22 15:16, postdating the replication phase and listed as a step-3 output) rather than the expected figures/figure5... | 2 file(s) |
| C16 | supporting | figure | match | The figure claimed by C16 was produced at outputs/single_run/fig6_trajectories.pdf (mtime 2026-10-22 15:16, within the replication phase; the file is not the expected path figur... | 5 file(s) |
| C17 | headline | scalar | partial | The run produced outputs/multi_100/multi_metrics.json (mtime 2026-10-22 15:22, step-5 output) with powerlaw_slope = -1.0764 over n_runs=100 (pooled 100,000 final-capital values,... | 5 file(s) |
| C18 | supporting | scalar | match | The claim is a lower-bound/threshold assertion: across 100 runs the maximum final capital of the most successful agent surpasses ~40000 units. The run-produced step-5 output out... | 6 file(s) |
| C19 | supporting | scalar | partial | This is a single-run anecdote: the paper (file1_paper.pdf p.12, confirmed verbatim: 'The best score was realized by an agent with a talent Tbest = 0.6048, practically coinciding... | 8 file(s) |
| C20 | supporting | scalar | match | This is a single-run anecdote read off one illustrated 100-run batch, so each paper value is a stochastic draw and the test is against the model's run distribution. The run's ow... | 7 file(s) |
| C21 | supporting | scalar | match | Step 5 (reimpl multi-run baseline, 100 runs x N=1000, mT=0.6, sigmaT=0.1) produced outputs/multi_100/multi_metrics.json (run-produced, mtime 2026-10-22 15:22, under the run's ou... | 5 file(s) |
| C22 | supporting | scalar | partial | Step 5 (reimpl multi-run baseline, 100 runs x N=1000, mT=0.6, sigmaT=0.1, I=80, NE=500, pL=50, C0=10, truncate_talent=True per reimpl/run_multi.py:63) produced outputs/multi_100... | 6 file(s) |
| C23 | headline | scalar | match | Step 6 ran the full-scale 10000-run experiment with the replication's own byte-unmodified engine (reimpl/run_multi.py + reimpl/tvl.py, GPU device 2) and produced outputs/multi_1... | 6 file(s) |
| C24 | supporting | scalar | partial | The run produced C_mt=61.65 and C_at=23.87 (outputs/multi_100/multi_metrics.json, written 2026-10-22 during the replication phase), and a sibling verifier generated a batch-leve... | 3 file(s) |
| C25 | supporting | scalar | match | The authors shipped only a single-run NetLogo visualization demo, so P_T0 was produced by the run's own faithful reimplementation. Step 5's run-produced output outputs/multi_100... | 5 file(s) |
| C26 | supporting | scalar | match | This is a single-run anecdote shared with C19 (C_best) and C24 (C_mt): the paper (p.13, provenance quote 'Cbest = 40960 which is 650 times greater than Cmt and more than 4000 ti... | 7 file(s) |
| C27 | supporting | figure | match | The run produced outputs/multi_100/fig7_distribution_and_scatter.pdf (mtime 2026-10-22 15:22, matching step-5 of the replication log; the expected path figures/figure7.pdf does ... | 4 file(s) |
| C28 | supporting | figure | match | The two panels of Figure 8 were produced as separate run-produced files (not the exact expected_output_file figures/figure8.pdf, which does not exist). outputs/multi_100/fig8a_b... | 7 file(s) |
| C29 | supporting | figure | match | The run produced outputs/multi_100/fig9_best_trajectory.pdf (mtime 2026-10-22 15:22, postdating the replication phase; generated by plan step 5 which emits fig9_best_trajectory.... | 4 file(s) |
| C30 | supporting | scalar | match | C30 is the no-funding multiple-run baseline P_T0 (same computation as sibling C25 and the Fig 10 NO FUNDING row, C31). The run-produced output outputs/multi_100/multi_metrics.js... | 5 file(s) |
| C31 | headline | table | partial | The funding experiments were reimplemented (authors shipped only a single-run NetLogo demo; fix_severity.json) and produced outputs/funding_fig10/funding_table.csv and funding_m... | 10 file(s) |
| C32 | supporting | scalar | match | The funding pipeline was reimplemented (authors shipped only a single-run NetLogo demo; see fix_severity.json) and produced outputs/funding_fig10/funding_table.csv and funding_m... | 4 file(s) |
| C33 | supporting | scalar | partial | The funding pipeline was reimplemented (authors shipped only a single-run NetLogo demo; see fix_severity.json) and produced outputs/funding_fig10/funding_table.csv (run-produced... | 5 file(s) |
| C34 | supporting | scalar | match | The run reimplemented the Fig.10 funding pipeline (authors shipped only a single-run NetLogo demo) and produced outputs/funding_fig10/funding_table.csv and funding_metrics.json ... | 4 file(s) |
| C35 | supporting | scalar | partial | The run reimplemented the funding pipeline (authors shipped only a single-run NetLogo demo; see fix_severity.json / C31) and produced outputs/funding_fig10/funding_table.csv (mt... | 6 file(s) |
| C36 | supporting | figure | match | The expected file name differs but the figure was produced at outputs/funding_fig10/fig11_efficiency_hist.pdf (titled 'Fig 11: normalized efficiency index by funding strategy'),... | 4 file(s) |
| C37 | supporting | table | partial | The run reimplemented the funding pipeline (authors shipped only a single-run NetLogo demo; see assess/fix_severity.json) and produced outputs/funding_fig12/funding_table_fixed.... | 5 file(s) |
| C38 | supporting | scalar | match | This is a stochastic single_run_anecdote: the paper's C_best=655360 and T=0.97 are one draw of the best-performer-over-100-runs for config (a) m_T=0.6, sigma_T=0.2. The run's ow... | 4 file(s) |
| C39 | supporting | scalar | match | This is a stochastic single_run_anecdote for config (b) m_T=0.7, sigma_T=0.1: the paper's printed top-three (C_best=327680 at T=0.8, then two at C=163840 with T=0.85 and T=0.92)... | 6 file(s) |
| C40 | supporting | scalar | match | Ensemble statistic graded under rule 3 (generated_ensemble). The run's step-9 output (output/replication/codebase/outputs/env_talent/env_talent_metrics.json) gave a single 100-r... | 7 file(s) |
| C41 | supporting | scalar | partial | The run's step 9 output outputs/env_talent/env_talent_metrics.json gives P_T = 34.98% for panel (a) (mT=0.6,sigmaT=0.2) and P_T = 33.98% for panel (b) (mT=0.7,sigmaT=0.1), each ... | 3 file(s) |
| C42 | supporting | scalar | partial | Step 10 (plan id 10, verifies C42/C43/C45) ran reimpl/run_env.py at the pL=80 config (baseline otherwise, un-truncated, 100 runs) and wrote output/replication/codebase/outputs/e... | 5 file(s) |
| C43 | supporting | scalar | partial | Step 10 (plan id 10, verifies C42/C43/C45) ran reimpl/run_env.py at the pL=20 config (baseline otherwise, un-truncated, 100 runs) and wrote outputs/env_pL/env_pL_metrics.json (r... | 6 file(s) |
| C44 | supporting | figure | match | The run produced outputs/env_talent/fig13_best_vs_talent.pdf (mtime 2026-10-22 15:32, a step-9 output per replication_plan.json, postdating the replication phase) rather than th... | 5 file(s) |
| C45 | supporting | figure | match | Step 10 (plan id 10, verifies C42/C43/C45) produced outputs/env_pL/fig14_best_vs_talent.pdf (mtime 2026-10-22 15:32, postdating the replication start at 15:11, so it is run-prod... | 5 file(s) |

## Flags

- Decomposition: 29 reproduced, 16 substantive divergence(s) (no_match / partial / not shipped by the authors), 0 benign/infrastructure-blocked or out of scope (excluded from the score, not charged to the paper).

## Code Audit

*Does the code compute what the paper defines? Advisory; independent of the Replication Score. A `match` above means the number came out of the shipped code, not that the code is right.*

Three findings. The most consequential is a model-definition conformance gap: the paper states talent is 'truncated in the interval [0,1]', but the authors' released NetLogo SETUP (TvLmodel.nlogo:32) draws talent from an unclipped normal, and the paper's own section 3.2 results were run un-truncated (the Fig-13 C_mt metric is defined on T>mT+2sigmaT=1.0 for the sigmaT=0.2 config, which is empty under truncation yet the paper reports a value). Second, the Figure 10 funding table prints F_T=70000 for the '25% BEST 10u, OTHERS 5u' strategy whose own definition totals 50000 over 8 injections, an internal arithmetic inconsistency in a headline table. Third, the power-law fits (single and 100-run) regress over the whole support C>=10 including the mode, not the far tail the paper fits; this is a real window deviation but a scratch refit shows it does not explain the -0.87-vs--1.27 single-run gap (the tail is even shallower), which is a more-unequal random draw. The core model rules (lucky doubles with prob=talent, unlucky halves, radius-1 one-event-per-step, toroidal world) in both the NetLogo demo and the Python reimplementation match the paper; the multi-run/funding/environment code is a faithful reconstruction (authors never released it), so most partial grades are stochastic draw or reconstruction-fidelity effects, not conformance defects.

Claims traced to code: 21 (5 deviate from the paper's definition).

| ID | Severity | Claims | Code | What the code does | What the text says | Assurance |
|---|---|---|---|---|---|---|
| A1 | moderate | C7, C23, C38, C40, C19, C21 | `official_comses_tvl_v1.0.0/code/TvLmodel.nlogo:32` | From reading the code: SETUP assigns `set talent random-normal mean-talent stdev-talent` with no clip or resample, so talents below 0 or above 1 are kept. The Python reimplementation env runs ran with truncate_talent=False (env_talent_metrics.json reports C_mt computed over agents with T>mT+2sigmaT=1.00 and C_mt_n_per_run=21.9, i.e. ~22 agents per run with talent above 1.0), matching the unclipped NetLogo and the paper's results. | The paper states twice that the talent distribution is truncated to the interval [0,1]. | text_only |
| A2 | moderate | C31 | `reimpl/run_funding.py:39` | The reimplementation defines '25% BEST 10u + OTHERS 5u' as best_frac=0.25, best_units=10, others_units=5 and computes invested = 10*250 + 5*750 = 6250 per injection, times 8 injections = 50000, which is written to funding_table.csv. | The paper's Figure 10 table lists F_T=70000 for the '25% BEST 10u, OTHERS 5u' row. | text_only |
| A3 | minor | C1, C2, C17, C27 | `analysis/analyze_single_run.py:17` | powerlaw_slope regresses log10(pdf) on log10(C) over the entire support C>=cmin=10.0, i.e. starting at the distribution's mode (C=10 holds 306 of 1000 agents in this run) and extending to C_max. run_multi.py:16 does the same for the 100-run pooled distribution. | The paper fits only the tail of the distribution. | rerun |

- **A1** numbers: as_shipped: talent unclipped (NetLogo); env reimpl truncate_talent=False, ~21.9 agents/run with T>1.0 at sigmaT=0.2, corrected: under true [0,1] truncation the T>1.0 set is empty and C_mt(panel a) is undefined
- **A2** numbers: as_shipped: paper F_T = 70000, corrected: 50000 (= (10*250 + 5*750)*8)
- **A3** numbers: as_shipped: C>=10 slope = -0.866 (matches shipped single_run_metrics.json -0.8658), corrected: tail-only: C>=40 -0.790, C>=160 -0.644, C>=320 -0.571

## Replication Attempt

**Environment:** Python 3.12.8, GPU: NVIDIA RTX A6000, Packages: torch 2.14.1+cu130, numpy 2.5.4, scipy 1.18.1, pandas 3.1.0, matplotlib 3.11.2
**Duration:** 419s
**Steps completed:** 10/10

| Step | Description | Result | Duration |
|------|-------------|--------|----------|
| 1 | Set up toolchain: JDK 17 + headless NetLogo 6.4.0, copy authors' model, Python venv (numpy/scipy/pandas/matplotlib/torch). | Success | 240s |
| 2 | Run authors' single-run demo headless at paper's section 2.1 settings (N=1000, N_E=500, m_T=0.6, sigma_T=0.1, p_L=50%, C0=10, I=80). Overrode released slider defaults (2000/1000) via BehaviorSpace enumeratedValueSet. Patched GO+SETUP to append per-(time,who) CSV. Fixed random-seed 12345. | Success | 8s |
| 3 | Analyze the single-run CSV (pure post-processing, no re-sim): power-law tail slope, inequality metrics, talent/capital misalignment, event-count exponential fits, trajectories, and Figs 3-6. | Success | 3s |
| 4 | Faithful vectorized (torch, GPU-batched) reimplementation mirroring the NetLogo rules (toroidal 201-period world, fixed integer agent positions, events fd 2 with random integer heading, one-of events in-radius 1, double-with-prob-talent / halve). Fidelity self-test vs the step-2 NetLogo run. | Success | 15s |
| 5 | Multiple-run baseline (section 2.2): 100 runs, N=1000, mT=0.6, sigmaT=0.1, I=80, NE=500, pL=50, C0=10. Pooled 100000 final capitals + best-performer metrics + Figs 7,8a,9. | Success | 8s |
| 6 | 10000-run experiment (section 2.2 / Fig 8b) at full scale, baseline params. Best-performer talent PDF (normalized) + Gaussian fit. GPU (torch) batched in chunks of 400. | Success | 90s |
| 7 | Figure 10/11 funding-strategy table: 20 funding strategies + NO FUNDING, 8 injections (t=10..80) over 100 runs, baseline params. PT, PT*=PT-PT0, FT, E=PT*/FT, E_norm=E/Emax; sorted desc; Fig 11 histogram. | Success | 24s |
| 8 | Figure 12 fixed-budget funding table: total FT=80000 for every strategy (10000 units/injection). 8 strategies + NO FUNDING, 100 runs. | Success | 12s |
| 9 | Section 3.2 environment: talent-distribution variants (Fig 13). Two 100-run batches: (a) mT=0.6 sigmaT=0.2, (b) mT=0.7 sigmaT=0.1. Per config: C_best, T_at_C_best, next_best, C_mt (most talented = T>mT+2sigmaT), P_T (T>mT+sigmaT=0.8). Fig 13 scatter. | Success | 10s |
| 10 | Section 3.2 environment: stimulation level p_L (Fig 14). Two 100-run batches: (a) pL=80%, (b) pL=20%, baseline otherwise. Per config: C_best, C_mt, P_T (T>0.7). Fig 14 scatter. | Success | 9s |


## Limitations & Code Quality

The shipped code did not run the paper's experiments as-is, and this is the main finding about the artifact. The authors released a single-run visualization demo only (its own PROVENANCE.md says so). It does not export per-agent trajectory data, so the agent had to add CSV logging and a fixed seed to the NetLogo model to recover section 2.1 (fix_severity.json fix 2, major). Everything behind sections 2.2 to 3.2, which is the multi-run power law, the 10000-run Gaussian, the Figure 10 and 12 funding tables, and the Figure 13/14 environment sweeps, was never released and had to be reimplemented in Python from the paper text. Two confirmed audit findings bear on the paper itself. A1 (assurance text_only, moderate): the paper says talent is 'truncated in [0,1]', but the released NetLogo setup draws talent unclipped, and the paper's own Figure 13 C_mt for the sigma_T=0.2 config is defined on T>1.0, which is empty under truncation yet the paper reports ~319, so the paper is internally inconsistent and only reproducible un-truncated (fix 5, major). A2 (assurance text_only, moderate): the Figure 10 row '25% BEST 10u, OTHERS 5u' prints F_T=70000, but its own definition totals 50000 over 8 injections, an arithmetic error in a headline table. The remaining fixes are housekeeping (rotted NetLogo download links, a numpy JSON-serialization shim, pinning to a free GPU) with no bearing on the science. A future reproducer must reimplement most of the paper and resolve the truncation contradiction before trusting section 3.2 numbers.

**Fixes the replication agent applied to make the work run:** 5 (3 minor, 2 major, 0 critical). These are evidence about the provided code/paper, not the replication.

Five fixes, and they cleanly separate into noise versus signal. Three are inconsequential: Fix 1 (Java/NetLogo provisioning around rotted download links and no root), Fix 3 (a one-line numpy JSON-serialization shim), and Fix 4 (pinning to a free GPU on a shared box) are all environment/toolchain housekeeping with zero bearing on the paper's science. The two consequential fixes both trace to the same root cause: the authors released only a single-run visualization DEMO, not the pipeline that produced the paper's quantitative results. Fix 2 had to add data-export instrumentation (and a fixed seed) because the demo emits only plots, and the entire multi-run / funding / environment apparatus (sections 3.1-3.2) was never released and had to be reimplemented from the paper text. Fix 5 then surfaced an actual internal inconsistency in the paper: its stated [0,1] talent truncation makes the reported section-3.2 C_mt value mathematically impossible, resolvable only by running un-truncated (as the authors' own demo in fact does). The overall fix burden is light in effort but informative in substance: the environment fixes are trivial, but the two model-level fixes show the published artifact is an incomplete demo and that the paper's written spec contains at least one result-breaking discrepancy that a replicator must catch and reconcile. The core model is reproducible and the qualitative findings hold, but reproducing the exact published numbers requires reimplementation plus interpretive judgment that the paper and repo do not fully supply.

| # | Description | Severity | Impact |
|---|-------------|----------|--------|
| 1 | Provisioned a standalone Temurin JDK 17 tarball and downloaded NetLogo 6.4.0 from GitHub (apt/root unavailable; the paper's ccl.northwestern.edu download URLs 404), then ran the authors' 6.0.3 demo model under NetLogo 6.4.0 with JAVA_HOME pointed at the Temurin JDK. | minor | Reflects ordinary toolchain/link rot and sandbox constraints rather than any defect in the paper's methodology. The only mild concern is engine-version drift (6.4.0 vs 6.0.3); worth noting for exactness but not expected to change results for this model. Does not reflect on the paper's science. |
| 2 | Added instrumentation to the NetLogo demo (TvLmodel_single.nlogo): a fixed random-seed (12345) after setup, a LOG-STATE procedure and logfile reporter, and header + per-step CSV logging of time/who/talent/success/lucky/unlucky counts. No model rules were changed; the model runs as shipped. | major | Confirms (as the repo's own PROVENANCE notes) that the authors released only a single-run demo, not the data-generation/analysis pipeline behind the paper's figures. The published code is incomplete for reproducing the paper's quantitative results: the per-agent data and the multi-run machinery were never shipped and must be instrumented or reimplemented. This is a meaningful gap in the artifact, though it reflects an incomplete release rather than a wrong method. |
| 3 | Added a numpy-to-native JSON default converter (default=_np) in analysis/analyze_single_run.py so numpy int64/float64 values serialize. | minor | Routine library-interaction boilerplate, almost certainly a NumPy version-drift artifact (newer NumPy no longer auto-coerces its scalar types in json.dump). Says nothing about the paper's methodology. |
| 4 | Set CUDA_VISIBLE_DEVICES=2 to pin the job to the one free GPU after GPUs 0/1 were occupied (~42GB held) by unrelated processes, which caused a CUDA OOM. | minor | Entirely an environment/shared-hardware concern. No implication for the repository or the paper's correctness. (Notable only in that a GPU is being used at all for what is a lightweight agent-based model, but that is this replication harness's setup, not the paper's.) |
| 5 | In the section-3.2 reimplementation (reimpl/run_env.py) disabled talent truncation (--no-truncate) and switched the 'most talented' capital metric C_mt to the paper's RELATIVE cut T>mT+2sigmaT, because for config (a) mT+2sigmaT=1.0 yields an EMPTY set under [0,1] truncation, whereas the paper reports C_mt~319. Ran 3.2 un-truncated to match the released demo and the paper's numbers. | major | Reveals a genuine contradiction between the paper's written methodology ('talent truncated in [0,1]') and its reported results: section 3.2's headline C_mt value is only reproducible if the truncation statement is ignored. The authors' released demo corroborates the no-truncation behavior, so the shipped text is the unreliable part. This is a real specification defect in the paper that a replicator must detect and work around; it modestly undermines confidence in the precision of the paper's section-3.2 description, though the qualitative conclusions survive. |


---
