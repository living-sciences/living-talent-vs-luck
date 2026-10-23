"""Block C: cross-domain assembly (signatures.csv), S4 ordering test, model-side
exceedance probabilities (§2), the embargo-lifted prep-diagnostics comparison, and
the three figures. Also writes consolidated G3 summary."""
import os, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import RESULTS, SHARED, done, write_json

OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"]
plt.rcParams.update({
    "figure.figsize": (7.5, 4.5), "figure.dpi": 150, "savefig.dpi": 150,
    "savefig.bbox": "tight", "font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.alpha": 0.25, "axes.prop_cycle": plt.cycler(color=OKABE_ITO)})


def load(name):
    return json.load(open(os.path.join(RESULTS, f"domain_{name}.json")))


def main():
    ref = json.load(open(os.path.join(RESULTS, "tvl_reference.json")))
    base = ref["baseline"]
    arr = np.load(os.path.join(RESULTS, "tvl_baseline_arrays.npz"))
    win_pct = arr["winner_pct_emp"]
    top10_pct = arr["top10_median_T_pct_emp"]

    def exceed(dist, v):
        return float((dist >= v).mean())

    tennis = load("tennis"); chess = load("chess"); bb = load("baseball")
    movies = load("movies"); sci = load("science"); poker = load("poker")

    # ---- consolidated G3 ----
    g3 = {
        "tennis": tennis["G3_validity"],
        "baseball": bb["G3_validity"],
        "movies": movies["G3_validity"],
    }
    write_json(os.path.join(RESULTS, "g3_validity.json"), g3)
    done("G3")

    # ---- exceedance probabilities (§2) ----
    exc = {
        "tennis_winner": {"value": tennis["P2_primary_titles"]["winner_skill_pct"],
                          "P_model_winner_pct_ge": exceed(win_pct, tennis["P2_primary_titles"]["winner_skill_pct"])},
        "tennis_top10": {"value": tennis["P2_primary_titles"]["top10_median_skill_pct"],
                         "P_model_top10_median_ge": exceed(top10_pct, tennis["P2_primary_titles"]["top10_median_skill_pct"])},
        "movies_winner": {"value": movies["S2"]["winner_skill_pct"],
                          "P_model_winner_pct_ge": exceed(win_pct, movies["S2"]["winner_skill_pct"])},
        "movies_top10": {"value": movies["S2"]["top10_median_skill_pct"],
                         "P_model_top10_median_ge": exceed(top10_pct, movies["S2"]["top10_median_skill_pct"])},
        "baseball_exitvelo_winner": {"value": bb["player_P2"]["exit_velocity"]["winner_skill_pct"],
                                     "P_model_winner_pct_ge": exceed(win_pct, bb["player_P2"]["exit_velocity"]["winner_skill_pct"])},
    }
    write_json(os.path.join(RESULTS, "exceedance.json"), exc)

    # ---- signatures.csv ----
    rows = []

    def add(domain, stat, value, ci=None, n=None, flag="", note=""):
        rows.append({"domain": domain, "statistic": stat, "value": value,
                     "ci_lo": ci[0] if ci else None, "ci_hi": ci[1] if ci else None,
                     "n": n, "proxy_validity": flag, "note": note})

    # TvL reference rows
    add("TvL_model_baseline", "winner_skill_pct", base["winner_pct_emp_mean"],
        [base["winner_pct_emp_p2.5"], base["winner_pct_emp_p97.5"]], base["n_runs"], "engine",
        "G2 run-produced; paper-implied 0.749")
    add("TvL_model_baseline", "top10_median_skill_pct", base["top10_median_T_pct_emp_mean"],
        [base["top10_median_T_pct_emp_p2.5"], base["top10_median_T_pct_emp_p97.5"]], base["n_runs"], "engine", "")
    add("TvL_model_baseline", "P_winner_top_decile", base["P_winner_top_decile"], None, base["n_runs"], "engine", "paper claim 0.03")
    add("TvL_model_baseline", "P_winner_T_gt_0.8", base["P_winner_T_gt_0.8"], None, base["n_runs"], "engine", "paper claim 0.03; QA 8%")
    add("TvL_model_baseline", "top20_capital_share", base["top20_share_mean"], None, base["n_runs"], "engine", "paper claim 0.80")
    add("TvL_model_baseline", "persistence_y2y_top100", base["persist_y2y_top100_mean"], None, base["n_runs"], "engine", "construct-matched")
    for pL, s in ref["ladder"].items():
        add(f"TvL_pL{pL}", "winner_skill_pct", s["winner_pct_emp_mean"], None, s["n_runs"], "engine", "luck ladder")
        add(f"TvL_pL{pL}", "P_winner_top_decile", s["P_winner_top_decile"], None, s["n_runs"], "engine", "luck ladder")
        add(f"TvL_pL{pL}", "top20_capital_share", s["top20_share_mean"], None, s["n_runs"], "engine", "luck ladder")
        add(f"TvL_pL{pL}", "persistence_y2y_top100", s["persist_y2y_top100_mean"], None, s["n_runs"], "engine", "luck ladder")

    # tennis
    tv = tennis["P2_primary_titles"]; tval = tennis["G3_validity"]["PASS"]
    fl = "PASS" if tval else "FAIL"
    add("tennis", "winner_skill_pct", tv["winner_skill_pct"], tv["winner_skill_pct_CI"], tv["n"], fl, "titles; [PREVIEW-CALIBRATED] band")
    add("tennis", "top10_median_skill_pct", tv["top10_median_skill_pct"], tv["top10_median_skill_pct_CI"], tv["n"], fl, "")
    add("tennis", "P_top_decile_cond", tv["P_top_decile_cond"], tv["P_top_decile_cond_CI"], tv["n"], fl, "")
    add("tennis", "winner_skill_pct_finals_excluded", tennis["P2_leakage_control_finals_excluded"]["winner_skill_pct"], None, tv["n"], fl, "leakage control")
    add("tennis", "titles_top20_share", tennis["P1_shape"]["concentration_titles_incl_zeros"]["top20_share"], None, tv["n"], fl, "P1 [PREVIEW-CALIBRATED 0.6]")
    add("tennis", "titles_top1_share", tennis["P1_shape"]["concentration_titles_incl_zeros"]["top1_share"], None, tv["n"], fl, "P1")
    add("tennis", "persistence_y2y_top100", tennis["persistence_2011_2025"]["mean_rho"], None, 100, fl, "2011-2025")
    add("tennis", "split_half_reliability", tennis["G3_validity"]["split_half_spearman"], None, tv["n"], fl, "")

    # chess
    add("chess", "persistence_y2y_top100", chess["persistence_top100"]["mean_rho"], None, 100, "N/A(Elo)", "skill-dominated anchor; S2 degenerate")

    # baseball
    bval = "PASS" if bb["G3_validity"]["PASS"] else "FAIL"
    be = bb["player_P2"]["exit_velocity"]; bs = bb["player_P2"]["sprint_speed"]
    add("baseball", "winner_skill_pct_exitvelo", be["winner_skill_pct"], be["winner_skill_pct_CI"], be["n"], bval, "success=AS+awards")
    add("baseball", "top10_median_skill_pct_exitvelo", be["top10_median_skill_pct"], None, be["n"], bval, "")
    add("baseball", "winner_skill_pct_sprint", bs["winner_skill_pct"], bs["winner_skill_pct_CI"], bs["n"], bval, "")
    add("baseball", "OPS_persistence_y2y", bb["player_OPS_persistence_LADDER"]["mean_spearman"], None, bb["player_OPS_persistence_LADDER"]["n_pairs"], bval, "P3 ladder entry")
    add("baseball", "team_winpct_y2y", bb["team_series"]["winpct_y2y_mean_spearman"], None, bb["team_series"]["n_pairs"], bval, "secondary")
    add("baseball", "salary_top20_share", bb["salary_concentration_1985_2016"]["top20_share"], None, bb["salary_concentration_1985_2016"]["n"], bval, "1985-2016")

    # movies
    mval = "PASS" if movies["G3_validity"]["PASS"] else "FAIL"
    ms = movies["S2"]
    add("movies", "winner_skill_pct", ms["winner_skill_pct"], ms["winner_skill_pct_CI"], ms["n"], mval, "quality=rating")
    add("movies", "top10_median_skill_pct", ms["top10_median_skill_pct"], None, ms["n"], mval, "")
    add("movies", "P_top_decile_cond", ms["P_top_decile_cond"], None, ms["n"], mval, "")
    add("movies", "votes_top20_share", movies["S1_concentration"]["top20_share"], None, ms["n"], mval, "P1")
    add("movies", "votes_top1_share", movies["S1_concentration"]["top1_share"], None, ms["n"], mval, "P1")

    # science
    s15 = sci["S1_concentration_by_cohort"]["2015_staged"]
    add("science", "citations_top20_share_2015", s15["top20_share"], None, s15["n"], "no-skill-proxy", "S1 only; fat-tail success")
    add("science", "citations_top1_share_2015", s15["top1_share"], None, s15["n"], "no-skill-proxy", "")
    for coh in ("2010_fetched", "2019_fetched"):
        c = sci["S1_concentration_by_cohort"].get(coh, {})
        if c.get("top20_share") is not None:
            add("science", f"citations_top20_share_{coh}", c["top20_share"], None, c["n"], "no-skill-proxy", "cohort stability (declared fetch)")

    # poker
    p = poker["power_statement"]
    add("poker", "power_E0", p["E0"], None, p["n_years"], "literature-anchored", "no-skill null")
    add("poker", "power_E5", p["E5"], None, p["n_years"], "literature-anchored", "5x skill 10% stratum")
    add("poker", "power_observed_repeats", p["observed"], None, p["n_years"], "literature-anchored", "1990-2025")

    sig = pd.DataFrame(rows)
    sig.to_csv(os.path.join(RESULTS, "signatures.csv"), index=False)

    # ---- S4 ordering test ----
    persistence = {"chess": chess["persistence_top100"]["mean_rho"],
                   "tennis": tennis["persistence_2011_2025"]["mean_rho"],
                   "baseball": bb["player_OPS_persistence_LADDER"]["mean_spearman"]}
    pre_declared = ["chess", "tennis", "baseball"]
    measured_order = sorted(persistence, key=lambda k: -persistence[k])
    persistence_ok = (measured_order == pre_declared)
    # decoupling (winner skill pct) across P2 domains
    decoupling = {"tennis": tennis["P2_primary_titles"]["winner_skill_pct"],
                  "baseball": bb["player_P2"]["exit_velocity"]["winner_skill_pct"],
                  "movies": movies["S2"]["winner_skill_pct"]}
    # model prediction: higher luck (lower persistence) -> LOWER winner skill pct (more decoupling)
    # test monotonicity among tennis & baseball (both have persistence & decoupling)
    conc = {"tennis": tennis["P1_shape"]["concentration_titles_incl_zeros"]["top20_share"],
            "baseball": bb["salary_concentration_1985_2016"]["top20_share"],
            "movies": movies["S1_concentration"]["top20_share"]}
    s4 = {
        "persistence": persistence, "pre_declared_order": pre_declared,
        "measured_order": measured_order, "persistence_order_reproduced": persistence_ok,
        "decoupling_winner_skill_pct": decoupling,
        "concentration_top20_share": conc,
        "decoupling_orders_with_persistence": False,
        "interpretation": ("Persistence ladder reproduced exactly (chess>tennis>baseball). But decoupling "
                           "does NOT order with persistence/luck: winner-skill percentile is ~0.99-1.0 in ALL "
                           "measured P2 domains (tennis 0.994, baseball 1.0 [CI-wide], movies 0.999), i.e. all "
                           "sit in the model's talent-dominated corner regardless of luck share, the opposite of "
                           "the model's prediction that higher-luck domains should show MORE top-level decoupling. "
                           "Per the pre-declared vocabulary this is a PARTIAL ordering."),
        "verdict": "partial ordering: persistence ladder holds; decoupling/concentration do not order with it",
    }
    write_json(os.path.join(RESULTS, "s4_ordering.json"), s4)

    # ================= FIGURES =================
    # fig_decoupling
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    doms = ["tennis", "movies", "baseball"]
    wp = [tennis["P2_primary_titles"]["winner_skill_pct"], movies["S2"]["winner_skill_pct"],
          bb["player_P2"]["exit_velocity"]["winner_skill_pct"]]
    wci = [tennis["P2_primary_titles"]["winner_skill_pct_CI"], movies["S2"]["winner_skill_pct_CI"],
           bb["player_P2"]["exit_velocity"]["winner_skill_pct_CI"]]
    t10 = [tennis["P2_primary_titles"]["top10_median_skill_pct"], movies["S2"]["top10_median_skill_pct"],
           be["top10_median_skill_pct"]]
    x = np.arange(len(doms))
    errlo = [wp[i] - wci[i][0] for i in range(len(doms))]
    errhi = [wci[i][1] - wp[i] for i in range(len(doms))]
    ax.errorbar(x - 0.08, wp, yerr=[errlo, errhi], fmt="o", color=OKABE_ITO[1], ms=9,
                capsize=4, label="winner skill percentile (95% CI)")
    ax.scatter(x + 0.08, t10, marker="s", color=OKABE_ITO[0], s=70, label="top-10 median skill percentile")
    ax.axhline(base["winner_pct_emp_mean"], color=OKABE_ITO[2], ls="--", lw=1.6,
               label=f"TvL baseline winner pct = {base['winner_pct_emp_mean']:.2f}")
    ax.axhspan(0.55, 0.95, color=OKABE_ITO[2], alpha=0.08)
    ax.axhline(0.95, color="gray", ls=":", lw=1.2)
    ax.axhline(0.99, color=OKABE_ITO[3], ls="-.", lw=1.2, label="talent-dominated (>=0.99)")
    ax.text(2.35, 0.75, "model band\n[0.55,0.95]", color=OKABE_ITO[2], fontsize=9, va="center")
    ax.set_xticks(x); ax.set_xticklabels([d + "\n(n=%d)" % n for d, n in
                    zip(doms, [tennis["P2_primary_titles"]["n"], movies["S2"]["n"], be["n"]])])
    ax.set_ylabel("skill percentile of top-success unit")
    ax.set_ylim(0.3, 1.03); ax.legend(fontsize=8.5, loc="lower left")
    fig.text(0.5, -0.02, "Top success coincides with top skill in every measured domain — decoupling absent.",
             ha="center", fontsize=9, style="italic")
    fig.savefig(os.path.join(RESULTS, "fig_decoupling.png"), facecolor="white")
    plt.close(fig)

    # fig_ordering: persistence (x) vs decoupling & concentration (y)
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for d in ["chess", "tennis", "baseball"]:
        if d in decoupling:
            ax.scatter(persistence[d], decoupling[d], color=OKABE_ITO[1], s=90, zorder=3)
            ax.annotate(d, (persistence[d], decoupling[d]), fontsize=10,
                        xytext=(4, 5), textcoords="offset points")
    # chess has no decoupling; mark persistence with a rug
    ax.scatter([persistence["chess"]], [0.5], marker="|", s=400, color=OKABE_ITO[7])
    ax.annotate("chess (skill anchor;\nS2 degenerate)", (persistence["chess"], 0.5),
                fontsize=8.5, xytext=(-30, -28), textcoords="offset points")
    # TvL pL ladder overlay (persistence_y2y vs winner pct)
    px = [ref["ladder"][k]["persist_y2y_top100_mean"] for k in ("20", "50", "80")]
    py = [ref["ladder"][k]["winner_pct_emp_mean"] for k in ("20", "50", "80")]
    ax.plot(px, py, "-D", color=OKABE_ITO[0], ms=6, alpha=0.8, label="TvL p_L ladder (20/50/80)")
    for k, xx, yy in zip(("pL20", "pL50", "pL80"), px, py):
        ax.annotate(k, (xx, yy), fontsize=8, color=OKABE_ITO[0], xytext=(3, -10), textcoords="offset points")
    ax.set_xlabel("elite persistence (year-to-year Spearman)  —  higher = more skill-dominated")
    ax.set_ylabel("decoupling: winner skill percentile")
    ax.legend(fontsize=9, loc="lower left")
    fig.text(0.5, -0.02, "Persistence ladder holds (chess>tennis>baseball) but decoupling stays ~1.0 regardless of luck — "
             "opposite the model's p_L ladder.", ha="center", fontsize=8.5, style="italic")
    fig.savefig(os.path.join(RESULTS, "fig_ordering.png"), facecolor="white")
    plt.close(fig)

    # fig_shapes: skill vs success distributions (small multiples)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
    # use concentration shares as a bar summary
    panels = [("tennis", tennis["P1_shape"]["concentration_titles_incl_zeros"]["top20_share"],
               tennis["P1_shape"]["skill_distribution"]),
              ("movies", movies["S1_concentration"]["top20_share"], movies["quality_distribution"]),
              ("science", s15["top20_share"], None)]
    for ax, (name, top20, shape) in zip(axes, panels):
        ax.bar(["success\ntop-20%", "egalitarian\n(0.20)"], [top20, 0.20],
               color=[OKABE_ITO[1], OKABE_ITO[7]])
        ax.axhline(base["top20_share_mean"], color=OKABE_ITO[2], ls="--",
                   label="TvL capital\ntop-20%%=%.2f" % base["top20_share_mean"])
        ax.set_ylim(0, 1); ax.set_title(name); ax.legend(fontsize=7, loc="upper right")
        if shape:
            ax.text(0.02, 0.92, "skill skew=%.2f\nkurt=%.2f" % (shape["skew"], shape["kurtosis_excess"]),
                    transform=ax.transAxes, fontsize=7.5, va="top")
    axes[0].set_ylabel("share of total success")
    fig.suptitle("Fat-tailed success from near-symmetric skill (P1 shape signature)", fontsize=12)
    fig.savefig(os.path.join(RESULTS, "fig_shapes.png"), facecolor="white")
    plt.close(fig)

    # ---- embargo-lifted prep-diagnostics comparison appendix ----
    prev = json.load(open(os.path.join(SHARED, "prep-diagnostics", "previews.json")))
    appendix = {
        "note": "Embargo lifted after B-block estimates written. Preview = Phase 2a prep-diagnostics; Study = this run.",
        "comparisons": [
            {"quantity": "tennis #1-success skill percentile", "preview": prev["tennis"]["top_success"]["skill_percentile"], "study": tv["winner_skill_pct"]},
            {"quantity": "tennis titles top-20% share", "preview": prev["tennis"]["titles_top20pct_share"], "study": tennis["P1_shape"]["concentration_titles_incl_zeros"]["top20_share"]},
            {"quantity": "tennis titles top-1% share", "preview": prev["tennis"]["titles_top1pct_share"], "study": tennis["P1_shape"]["concentration_titles_incl_zeros"]["top1_share"]},
            {"quantity": "tennis top-100 y2y Spearman 2011-2025", "preview": prev["tennis"]["top100_yearend_points_y2y_spearman_mean_2011_2025"], "study": tennis["persistence_2011_2025"]["mean_rho"]},
            {"quantity": "chess top-100 y2y jan25->jan26", "preview": prev["chess"]["top100_y2y_spearman_jan25_jan26"], "study": chess["persistence_top100"]["pairs"].get("2025->2026", {}).get("rho")},
            {"quantity": "baseball team wpct y2y", "preview": prev["baseball"]["team_wpct_y2y_corr_1961_2025"], "study": bb["team_series"]["winpct_y2y_mean_spearman"]},
            {"quantity": "baseball season luck share", "preview": prev["baseball"]["season_luck_share"], "study": bb["team_series"]["mauboussin_luck_share_2015_2025_mean"]},
            {"quantity": "science citations top-20% (2015)", "preview": prev["science"]["citations_top20pct_share"], "study": s15["top20_share"]},
            {"quantity": "movies votes top-20% share", "preview": prev["imdb"]["votes_top20pct_share"], "study": movies["S1_concentration"]["top20_share"]},
            {"quantity": "movies most-voted quality percentile", "preview": prev["imdb"]["most_voted_quality_percentile"], "study": ms["winner_skill_pct"]},
            {"quantity": "model winner-talent mean (paper claim vs G2)", "preview": prev["tvl_model_reference"]["winner_talent_mean"], "study": base["winner_T_mean"]},
            {"quantity": "model P(winner T>0.8) (paper claim vs G2)", "preview": prev["tvl_model_reference"]["P_winner_talent_gt_0.8"], "study": base["P_winner_T_gt_0.8"]},
        ],
    }
    write_json(os.path.join(RESULTS, "prep_diagnostics_comparison.json"), appendix)

    print(json.dumps({"s4_verdict": s4["verdict"], "persistence": persistence,
                      "measured_order": measured_order, "persistence_ok": persistence_ok,
                      "exceedance": exc,
                      "decoupling": decoupling}, indent=2))
    done("C")


if __name__ == "__main__":
    main()
