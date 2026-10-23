# Provenance — tennis leg

- **Source:** `Aneeshers/tennis-sackmann-archive` (GitHub, default branch `main`), an archival mirror of Jeff Sackmann's public tennis datasets. Downloaded file-by-file from `https://raw.githubusercontent.com/Aneeshers/tennis-sackmann-archive/main/atp/<file>` on 2026-10-22.
- **Why a mirror:** the canonical upstream `github.com/JeffSackmann/tennis_atp` returned HTTP 404 on 2026-10-22 (the repo is no longer public; of Sackmann's repos only `tennis_MatchChartingProject` remains). The mirror's README states its `atp` snapshot was taken from upstream commits of June 2026; the mirror is also published on Hugging Face (`Aneeshers/tennis-sackmann-archive`).
- **License:** CC BY-NC-SA 4.0 (the upstream license; mirror's LICENSE file staged alongside). Attribution: Jeff Sackmann / Tennis Abstract. Non-commercial use only; do not redistribute in the public living-paper repo beyond derived aggregates with attribution.
- **Contents staged:** `atp_matches_1968..2026.csv` (main-tour singles results; match stats from 1991), `atp_players.csv`, `atp_rankings_{90s,00s,10s,20s,current}.csv` (weekly rankings incl. points), the upstream data dictionary and README.
- **Coverage check (2026-10-22):** `atp_matches_2025.csv` has a full season; `atp_matches_2026.csv` is a partial season (snapshot June 2026) — the studies use seasons 1991-2025 and must not treat 2026 as complete.
- **Known limitation:** no prize-money field; success measures are titles, finals, Grand Slam wins, ranking points, weeks in top ranks.
