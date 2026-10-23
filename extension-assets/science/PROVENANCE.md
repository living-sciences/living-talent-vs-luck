# Provenance — science leg

- `openalex_2015_article_sample_citations.csv` — OpenAlex API, seeded random sample of 2015 journal articles with citation counts: `api.openalex.org/works?filter=type:article,publication_year:2015&sample=10000&seed=42&per-page=200&page=1..25&select=id,cited_by_count`, fetched keyless 2026-10-22 (5,000 rows retrieved; seed pinned so the pull is reproducible/extendable). License CC0. Preview: top 20% of papers hold 92.8% of citations; 57.3% uncited.
- OpenAlex is also the sanctioned in-run source if a study block needs a further pull — keyless, CC0; pin any new query string + date in the study's deviations. (This is the single declared exception to "fetch nothing new", below, and only for OpenAlex API queries written into the spec.)
- Funding natural experiments / lotteries are engaged through the literature leg (Bol-de Vaan-van de Rijt 2018 PNAS; Liu et al. 2020 HRC NZ; Heyard et al. 2022 SNSF), see `literature/`.
