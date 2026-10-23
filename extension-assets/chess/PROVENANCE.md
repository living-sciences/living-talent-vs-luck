# Provenance — chess leg (skill-dominated control)

- **Source:** FIDE rating-list download service, `http://ratings.fide.com/download/standard_jan{YY}frl.zip` for YY = 15..26, downloaded keyless 2026-10-22. January standard-rating full lists, fixed-width TXT inside each zip (header row gives column offsets; rating column label JAN{YY}).
- **Terms:** FIDE rating lists are publicly downloadable from FIDE's own download page (no key, no click-wrap encountered on the direct URLs). Ratings are facts/public records; staging for research is unproblematic. Do not re-host the raw lists publicly; derived aggregates with attribution to FIDE are fine.
- **Verified 2026-10-22:** jan25 list has 486,934 rated players, jan26 has 531,422; format parses on the header offsets (ID at col 0, rating under the JANxx column).
- **Caveat:** the K-factor/rating floor and the inclusion threshold changed over the years (notably the 2024 rating-floor compression for ratings below 2000); cross-year comparisons should be restricted to the elite segment (e.g. top 100-1000), where rules are stable.
