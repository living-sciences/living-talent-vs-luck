"""B6 poker (luck-end leg, bounded). Parse champions wikitext row-by-row
(position-based, no bulk regex over markup). Write poker_events.csv.
Compute the pre-declared power statement. Bracelet concentration DESCRIPTIVE ONLY."""
import os, re, json
import numpy as np
import pandas as pd
from common import SHARED, RESULTS, done, write_json

PK = os.path.join(SHARED, "poker")


def split_cells(row_lines):
    """Each data cell is a line starting with '|' (not '|-' or '|}'). Strip a
    leading style prefix (segment containing '=' before the first interior '|')."""
    cells = []
    for ln in row_lines:
        s = ln.rstrip("\n")
        if not s.startswith("|"):
            continue
        if s.startswith("|-") or s.startswith("|}") or s.startswith("|+"):
            continue
        body = s[1:]
        # style prefix?  "align=... bgcolor=...| content"
        if "|" in body:
            head, rest = body.split("|", 1)
            if ("=" in head) or re.search(r"\b(align|bgcolor|colspan|rowspan|style|width|scope)\b", head):
                cells.append(rest.strip())
                continue
        cells.append(body.strip())
    return cells


def sortname(cell):
    m = re.search(r"\{\{sortname\|([^|}]+)\|([^|}]+)", cell)
    if m:
        return f"{m.group(1).strip()} {m.group(2).strip()}"
    # plain text: strip wiki links, refs, templates, dagger
    t = re.sub(r"<ref.*?(/>|</ref>)", "", cell, flags=re.S)
    t = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", t)
    t = re.sub(r"\{\{[^}]*\}\}", "", t)
    t = t.replace("†", "").replace("'", "").strip()
    return t if t and t.lower() not in ("n/a", "{{n/a}}", "") else None


def num(cell):
    m = re.search(r"\{\{nts\|(\d+)\}\}", cell)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d[\d,]{2,})", cell.replace(",", ""))
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


def parse_champions():
    text = open(os.path.join(PK, "wsop_main_event_champions.wikitext")).read()
    lines = text.splitlines()
    # locate the main champions table (the col6right sortable one)
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("{|") and "col6right" in ln:
            start = i
            break
    # collect until table close
    end = start
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("|}"):
            end = i
            break
    tbl = lines[start:end]
    # split into rows on '|-'
    rows, cur = [], []
    for ln in tbl[1:]:
        if ln.startswith("|-"):
            if cur:
                rows.append(cur); cur = []
        elif ln.startswith("!"):
            continue
        else:
            cur.append(ln)
    if cur:
        rows.append(cur)

    events = []
    for r in rows:
        cells = split_cells(r)
        # find year cell
        yr = None
        yr_idx = None
        for j, c in enumerate(cells):
            m = re.search(r"\[\[(\d{4}) World Series of Poker\|(\d{4})\]\]", c)
            if m:
                yr = int(m.group(2)); yr_idx = j; break
        if yr is None:
            continue
        # position-based relative to year cell: winner=+1, prize=+4, entrants=+5, runnerup=+8
        def get(off):
            k = yr_idx + off
            return cells[k] if 0 <= k < len(cells) else ""
        winner = sortname(get(1))
        prize = num(get(4))
        entrants = num(get(5))
        runner = sortname(get(8))
        events.append({"year": yr, "champion": winner, "runner_up": runner,
                       "entrants": entrants, "prize": prize})
    df = pd.DataFrame(events).drop_duplicates("year").sort_values("year").reset_index(drop=True)
    return df


def power_statement(df):
    w = df[(df.year >= 1990) & (df.year <= 2025)].copy()
    w = w.dropna(subset=["entrants"])
    years = w.year.tolist()
    champs = w.champion.tolist()
    ent = dict(zip(w.year, w.entrants))
    # observed repeat champions within window
    seen = {}
    observed = 0
    for y, c in zip(years, champs):
        if c in seen:
            observed += 1
        seen[c] = seen.get(c, 0) + 1
    # E_0: sum over years of (distinct prior winners)/n_t  (uniform no-skill null)
    # E_5: skilled stratum 10%, 5x weight -> per-skilled-player prob = 5/(1.4 n_t); prior winners assumed skilled
    seen_set = set()
    E0 = 0.0
    E5 = 0.0
    for y, c in zip(years, champs):
        D = len(seen_set)
        n = ent[y]
        if n and n > 0:
            E0 += D / n
            E5 += D * 5.0 / (1.4 * n)
        seen_set.add(c)
    d = E5 - E0
    can = "cannot" if abs(d) < 1.0 else "can"
    stmt = (f"Under a no-skill null with field sizes n_t, the expected number of repeat "
            f"Main-Event champions 1990-2025 is E_0 = {E0:.3f}; under a uniform 5x skill "
            f"multiple for a 10% skilled stratum it is E_5 = {E5:.3f}. The observed count is "
            f"{observed}. With E_5 - E_0 = {d:.3f} expected events, this comparison {can} "
            f"distinguish the hypotheses.")
    return {"statement": stmt, "E0": E0, "E5": E5, "observed": observed,
            "E5_minus_E0": d, "n_years": len(years),
            "field_range": [int(w.entrants.min()), int(w.entrants.max())],
            "model_detail": "E0=sum_t D_{t-1}/n_t; E5=sum_t D_{t-1}*5/(1.4 n_t); D=distinct prior in-window winners; prior winners assumed in skilled stratum"}


def bracelet_descriptive():
    text = open(os.path.join(PK, "wsop_bracelet.wikitext")).read()
    lines = text.splitlines()
    # find the "top bracelet winners" wikitable
    start = None
    for i, ln in enumerate(lines):
        if "top bracelet winners" in ln.lower():
            for j in range(i, min(i + 5, len(lines))):
                if lines[j].startswith("{|"):
                    start = j; break
            break
    counts = []
    if start:
        # gather rows between |- markers
        rows, cur = [], []
        i = start + 1
        while i < len(lines) and not lines[i].startswith("|}"):
            ln = lines[i]
            if ln.startswith("|-"):
                if cur:
                    rows.append(cur); cur = []
            elif not ln.startswith("!"):
                cur.append(ln)
            i += 1
        if cur:
            rows.append(cur)
        cur_count = None
        for r in rows:
            # a count cell: leading int, possibly with rowspan; carries over if absent
            cnt = None
            player = None
            for ln in r:
                mc = re.match(r"\|\s*(?:rowspan=\d+\s*)?align=center\s*\|\s*(\d+)\s*$", ln.strip())
                if mc and player is None and cnt is None:
                    cnt = int(mc.group(1))
                pm = re.search(r"\[\[([^\]|]+)", ln)
                if pm and "flagicon" in ln:
                    player = pm.group(1)
            if cnt is not None:
                cur_count = cnt
            if player:
                counts.append({"player": player, "bracelets": cur_count})
    return counts


def main():
    df = parse_champions()
    df.to_csv(os.path.join(RESULTS, "poker_events.csv"), index=False)

    # 5-row spot check (print rows for manual verification vs PROVENANCE)
    spot = df[df.year.isin([1972, 1988, 2003, 2006, 2019])].to_dict("records")

    power = power_statement(df)
    brac = bracelet_descriptive()

    res = {
        "n_events_parsed": int(len(df)),
        "year_range": [int(df.year.min()), int(df.year.max())],
        "spot_check_rows": spot,
        "power_statement": power,
        "bracelet_descriptive_ONLY": {
            "multi_bracelet_counts_truncated": brac[:25],
            "caveat": "top-truncated list (table starts at 17,11,10,9...); concentration on a top-truncated list is selection-biased and lower-bound-style descriptive only — NO verdict weight, NO null comparison (demoted at 2b revision, TvL-A5). A proper multi-event concentration test is a next-tick item behind the Hendon Mob human gate.",
        },
        "literature_anchor": "Levitt & Miles 2014 (WSOP 2010): a-priori high-skill players' ROI +30.5% vs -15.6% for others — the poker leg's informative weight rests on this labelled literature rung.",
        "P3_placement": "luck-end placement is LITERATURE-BASED only (Levitt-Miles 2014), reported as a labelled literature rung, NOT a measured/confirmed rung; staged poker data has no persistence series.",
    }
    write_json(os.path.join(RESULTS, "domain_poker.json"), res)

    rows = [
        {"domain": "poker", "stat": "power_E0", "value": power["E0"], "ci_lo": None, "ci_hi": None, "n": power["n_years"], "note": "no-skill null expected repeats"},
        {"domain": "poker", "stat": "power_E5", "value": power["E5"], "ci_lo": None, "ci_hi": None, "n": power["n_years"], "note": "5x skill 10% stratum"},
        {"domain": "poker", "stat": "power_observed_repeats", "value": power["observed"], "ci_lo": None, "ci_hi": None, "n": power["n_years"], "note": "1990-2025 in-window"},
    ]
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS, "domain_poker.csv"), index=False)
    print(json.dumps({"n_events": len(df), "year_range": res["year_range"],
                      "spot_check": spot, "power": power,
                      "n_bracelet_rows": len(brac), "top_bracelet": brac[:4]}, indent=2, default=str))
    done("B6")


if __name__ == "__main__":
    main()
