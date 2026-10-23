"""B5 science: OpenAlex citation concentration (S1) on staged 2015 sample, plus
the declared in-run fetch of cohorts 2010 & 2019 (<=25 pages each) to show S1
stability across cohorts. Logs each query string + timestamp to results/fetch_log.json."""
import os, json, time, urllib.request, urllib.error
import numpy as np
import pandas as pd
from common import SHARED, RESULTS, done, write_json

SCI = os.path.join(SHARED, "science")
FETCH_LOG = os.path.join(RESULTS, "fetch_log.json")


def gini(x):
    x = np.sort(np.asarray(x, float)); n = len(x); cum = np.cumsum(x)
    if cum[-1] == 0:
        return 0.0
    return float((n + 1 - 2 * (cum / cum[-1]).sum()) / n)


def concentration(cites):
    c = np.asarray(cites, float)
    s = np.sort(c)[::-1]; tot = s.sum(); n = len(s)
    return {"n": int(n), "total_citations": float(tot),
            "top20_share": float(s[:max(1, int(.2 * n))].sum() / tot) if tot else None,
            "top1_share": float(s[:max(1, int(.01 * n))].sum() / tot) if tot else None,
            "frac_uncited": float((c == 0).mean()), "gini": gini(c),
            "mean": float(c.mean()), "median": float(np.median(c))}


def fetch_cohort(year, max_pages=25, log=None):
    rows = []
    for page in range(1, max_pages + 1):
        url = (f"https://api.openalex.org/works?filter=type:article,"
               f"publication_year:{year}&sample=10000&seed=42&per-page=200"
               f"&page={page}&select=id,cited_by_count")
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        entry = {"query": url, "timestamp": ts, "year": year, "page": page}
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "living-talent-vs-luck-followup-001/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
            res = data.get("results", [])
            for w in res:
                rows.append(w.get("cited_by_count", 0))
            entry["status"] = "ok"; entry["n"] = len(res)
            if log is not None:
                log.append(entry)
            if len(res) < 200:
                break
        except Exception as e:
            entry["status"] = f"ERROR {type(e).__name__}: {e}"
            if log is not None:
                log.append(entry)
            return rows, str(e)
        time.sleep(0.2)
    return rows, None


def main():
    log = []
    # staged 2015 sample
    s15 = pd.read_csv(os.path.join(SCI, "openalex_2015_article_sample_citations.csv"))
    conc15 = concentration(s15.cited_by_count.values)

    cohorts = {"2015_staged": conc15}
    fetch_status = {"2010": None, "2019": None}
    for yr in (2010, 2019):
        cites, err = fetch_cohort(yr, 25, log)
        if err or len(cites) < 100:
            fetch_status[str(yr)] = f"fetch failed/thin: err={err} n={len(cites)}"
            cohorts[f"{yr}_fetched"] = {"n": len(cites), "status": "unavailable",
                                        "note": "in-run OpenAlex fetch failed; S1 stability shown only where available"}
        else:
            cohorts[f"{yr}_fetched"] = concentration(cites)
            fetch_status[str(yr)] = f"ok n={len(cites)}"

    res = {"source": "OpenAlex (staged 2015 sample + declared in-run 2010/2019 pulls)",
           "S1_concentration_by_cohort": cohorts,
           "fetch_status": fetch_status,
           "declared_fetch_exception": "spec section 0/4.6 permits OpenAlex keyless CC0 queries; logged to fetch_log.json",
           "preview_stated_in_provenance": "2015: top20=92.8%, uncited=57.3% (for cross-check)"}
    write_json(os.path.join(RESULTS, "domain_science.json"), res)
    write_json(FETCH_LOG, {"fetches": log, "note": "OpenAlex in-run pulls (declared exception, spec section 0)"})

    rows = []
    for coh, c in cohorts.items():
        if "top20_share" in c and c.get("top20_share") is not None:
            rows.append({"domain": "science", "stat": f"top20_share_{coh}", "value": c["top20_share"],
                         "ci_lo": None, "ci_hi": None, "n": c["n"], "note": "citation concentration"})
            rows.append({"domain": "science", "stat": f"frac_uncited_{coh}", "value": c["frac_uncited"],
                         "ci_lo": None, "ci_hi": None, "n": c["n"], "note": ""})
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS, "domain_science.csv"), index=False)
    print(json.dumps({"conc_2015_staged": conc15, "fetch_status": fetch_status,
                      "cohorts_summary": {k: {kk: v.get(kk) for kk in ("top20_share", "top1_share", "frac_uncited", "n")}
                                          for k, v in cohorts.items()}}, indent=2))
    done("B5")


if __name__ == "__main__":
    main()
