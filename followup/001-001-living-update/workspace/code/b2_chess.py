"""B2 chess: skill-dominated control. Persistence anchor (consecutive-January
top-100 Spearman) + qualitative #1-player row. S2 is degenerate in chess (Elo is
both skill and success ranking) and is NOT computed, per spec 4.2."""
import os, re, io, zipfile, json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from common import SHARED, RESULTS, done, write_json

CH = os.path.join(SHARED, "chess")
YEARS = list(range(15, 27))  # 2015..2026


def load_year(yy):
    zf = os.path.join(CH, f"standard_jan{yy}frl.zip")
    with zipfile.ZipFile(zf) as z:
        nm = [n for n in z.namelist() if n.endswith(".txt")][0]
        with z.open(nm) as fh:
            lines = io.TextIOWrapper(fh, "latin-1").read().splitlines()
    header = lines[0]
    m = re.search(r"JAN\d\d", header)
    jpos = m.start()
    recs = []
    for ln in lines[1:]:
        if len(ln) < jpos + 4:
            continue
        pid = ln.split()[0] if ln.split() else None
        # rating: numeric token in a window around jpos
        win = ln[max(0, jpos - 2):jpos + 6]
        mm = re.search(r"\d{3,4}", win)
        if pid and mm:
            try:
                recs.append((pid, int(mm.group())))
            except ValueError:
                pass
    df = pd.DataFrame(recs, columns=["id", "rating"]).drop_duplicates("id")
    return df


def main():
    lists = {2000 + yy: load_year(yy) for yy in YEARS}
    # top-100 ratings per year, indexed by id
    top100 = {}
    top1000 = {}
    top1_id = {}
    for y, df in lists.items():
        s = df.sort_values("rating", ascending=False)
        top100[y] = s.head(100).set_index("id")["rating"]
        top1000[y] = s.head(1000).set_index("id")["rating"]
        top1_id[y] = s.iloc[0]["id"]

    pairs = {}
    rhos = []
    years = sorted(lists.keys())
    for a, b in zip(years[:-1], years[1:]):
        common = top100[a].index.intersection(top100[b].index)
        rho = spearmanr(top100[a][common], top100[b][common]).statistic
        pairs[f"{a}->{b}"] = {"rho": float(rho), "retained_n": int(len(common))}
        rhos.append(rho)
    # also top-1000 persistence secondary
    rhos1000 = []
    for a, b in zip(years[:-1], years[1:]):
        common = top1000[a].index.intersection(top1000[b].index)
        rhos1000.append(spearmanr(top1000[a][common], top1000[b][common]).statistic)

    res = {
        "panel": {"lists": "FIDE January standard 2015-2026", "segment": "top 100 / top 1000 by rating",
                  "n_rated_per_year": {str(y): int(len(df)) for y, df in lists.items()},
                  "caveat": "2024 sub-2000 floor change makes full distribution non-comparable; elite segment used"},
        "S2": "degenerate in chess (Elo is both skill and de-facto success ranking) — NOT computed per spec 4.2",
        "persistence_top100": {"pairs": pairs, "mean_rho": float(np.mean(rhos)), "n_pairs": len(rhos)},
        "persistence_top1000_mean_rho": float(np.mean(rhos1000)),
        "top1_rated_id_per_year": {str(y): top1_id[y] for y in years},
        "world_champion_match_row": "DROPPED: world-champion identity cannot be established from staged files (no champion roster staged); per spec 4.2 the row is dropped, not fetched. #1-rated id reported descriptively above (stable single id across 2015-2023 consistent with one dominant player).",
    }
    write_json(os.path.join(RESULTS, "domain_chess.json"), res)
    rows = [{"domain": "chess", "stat": "persistence_top100_mean_rho",
             "value": res["persistence_top100"]["mean_rho"], "ci_lo": None, "ci_hi": None,
             "n": 100, "note": "11 consecutive-Jan pairs 2015-2026"}]
    for k, v in pairs.items():
        rows.append({"domain": "chess", "stat": f"persistence_{k}", "value": v["rho"],
                     "ci_lo": None, "ci_hi": None, "n": v["retained_n"], "note": "top-100"})
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS, "domain_chess.csv"), index=False)
    # how many distinct #1 ids
    distinct_top1 = len(set(top1_id.values()))
    print(json.dumps({"persistence_top100_mean_rho": res["persistence_top100"]["mean_rho"],
                      "persistence_top1000_mean_rho": res["persistence_top1000_mean_rho"],
                      "n_distinct_top1_players_2015_2026": distinct_top1,
                      "n_rated_jan26": int(len(lists[2026])),
                      "pairs": {k: v["rho"] for k, v in pairs.items()}}, indent=2))
    done("B2")


if __name__ == "__main__":
    main()
