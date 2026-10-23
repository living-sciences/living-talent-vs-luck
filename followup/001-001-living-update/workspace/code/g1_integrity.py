"""Block A / G1 integrity: verify sha256 manifests + coverage sanity per PROVENANCE."""
import os, re, sys, json, gzip, io
import pandas as pd
from common import SHARED, RESULTS, done, write_json, sha256

report = {"sha256": {}, "coverage": {}, "status": "PASS", "notes": []}


def parse_manifest(path):
    """Return {filename: sha256} from a DATA_MANIFEST.md table."""
    out = {}
    for line in open(path):
        m = re.match(r"\|\s*([^\s|][^|]*?)\s*\|\s*(\d+)\s*\|\s*([0-9a-f]{64})\s*\|", line)
        if m:
            out[m.group(1).strip()] = m.group(3)
    return out


# ---- sha256 verification per leg ----
legs = ["tennis", "chess", "baseball", "entertainment", "poker", "science", "literature"]
n_ok = n_bad = n_missing = 0
for leg in legs:
    mpath = os.path.join(SHARED, leg, "DATA_MANIFEST.md")
    man = parse_manifest(mpath)
    leg_res = {}
    for fname, expect in man.items():
        if fname in (".hashes.tmp",):
            continue
        fpath = os.path.join(SHARED, leg, fname)
        if not os.path.exists(fpath):
            leg_res[fname] = "MISSING"
            n_missing += 1
            continue
        got = sha256(fpath)
        ok = (got == expect)
        leg_res[fname] = "OK" if ok else f"MISMATCH got={got[:12]}"
        n_ok += ok
        n_bad += (not ok)
    report["sha256"][leg] = leg_res
report["sha256_summary"] = {"ok": n_ok, "mismatch": n_bad, "missing": n_missing}
if n_bad:
    report["status"] = "FAIL"
    report["notes"].append(f"{n_bad} sha256 mismatches")

# ---- coverage sanity ----
cov = report["coverage"]
# tennis 2025 complete; 2026 partial
t25 = pd.read_csv(os.path.join(SHARED, "tennis", "atp_matches_2025.csv"))
t26 = pd.read_csv(os.path.join(SHARED, "tennis", "atp_matches_2026.csv"))
cov["tennis_2025_matches"] = int(len(t25))
cov["tennis_2026_matches"] = int(len(t26))
cov["tennis_2025_complete"] = bool(len(t25) > 2000)

# chess jan26 >= 500k rated
import zipfile
with zipfile.ZipFile(os.path.join(SHARED, "chess", "standard_jan26frl.zip")) as z:
    nm = z.namelist()[0]
    with z.open(nm) as fh:
        n = sum(1 for _ in io.TextIOWrapper(fh, "latin-1")) - 1
cov["chess_jan26_rows"] = int(n)
cov["chess_jan26_ge_500k"] = bool(n >= 500000)

# Lahman Teams max year 2025
import pyreadr
teams = list(pyreadr.read_r(os.path.join(SHARED, "baseball", "lahman_rda", "Teams.RData")).values())[0]
cov["lahman_teams_max_year"] = int(teams["yearID"].max())
cov["lahman_teams_max_year_2025"] = bool(teams["yearID"].max() == 2025)

# IMDb movies >= 45k at votes cut
rat = pd.read_csv(os.path.join(SHARED, "entertainment", "imdb", "title.ratings.tsv.gz"),
                  sep="\t", compression="gzip")
bas = pd.read_csv(os.path.join(SHARED, "entertainment", "imdb", "title.basics.tsv.gz"),
                  sep="\t", compression="gzip", low_memory=False,
                  usecols=["tconst", "titleType"], dtype=str)
mov = bas[bas.titleType == "movie"].merge(rat, on="tconst")
mov1k = mov[mov.numVotes >= 1000]
cov["imdb_movies_ge1000votes"] = int(len(mov1k))
cov["imdb_movies_ge_45k"] = bool(len(mov1k) >= 45000)

# poker champions table rows ~ 1970s-2025
champ = open(os.path.join(SHARED, "poker", "wsop_main_event_champions.wikitext")).read()
years = sorted(set(int(y) for y in re.findall(r"\[\[(\d{4}) World Series of Poker\|\d{4}\]\]", champ)))
cov["poker_champ_year_min"] = years[0] if years else None
cov["poker_champ_year_max"] = years[-1] if years else None
cov["poker_champ_n_years"] = len(years)

for k in ["tennis_2025_complete", "chess_jan26_ge_500k", "lahman_teams_max_year_2025", "imdb_movies_ge_45k"]:
    if not cov.get(k):
        report["status"] = "FAIL"
        report["notes"].append(f"coverage fail: {k}")

write_json(os.path.join(RESULTS, "g1_integrity.json"), report)
print(json.dumps({"status": report["status"], "sha256_summary": report["sha256_summary"],
                  "coverage": cov, "notes": report["notes"]}, indent=2, default=str))
if report["status"] == "PASS":
    done("G1")
else:
    sys.exit(1)
