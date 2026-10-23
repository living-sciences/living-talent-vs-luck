"""B7 MusicLab branch. Raw data NOT staged (OPR archive human gate) -> honest-
exclusion branch: one labelled literature row (Salganik-Dodds-Watts 2006). No
invented numbers."""
import os, json
from common import SHARED, RESULTS, done, write_json

exists = os.path.isdir(os.path.join(SHARED, "entertainment", "musiclab"))
res = {
    "branch": "ELSE (honest-exclusion): shared-data/entertainment/musiclab/ does not exist",
    "musiclab_raw_available": exists,
    "literature_row": {
        "source": "Salganik, Dodds & Watts, Science 311:854-856 (2006) — MusicLab",
        "qualitative_findings": "Inequality and unpredictability of success both rise with social influence. 'The best songs rarely did poorly, and the worst rarely did well, but any other result was possible.' Quality (independent-condition market share) sets only loose bounds on success; luck (early social signal) governs the middle.",
        "relation_to_P2": "Qualitative support for P2's DIRECTION in few-trial reward markets: top success is only weakly pinned by ex-ante quality. Labelled literature-based, not a measured rung.",
        "gate": "raw data human-gated (OPR archive 403s keyless); see entertainment/PROVENANCE.md",
    },
}
write_json(os.path.join(RESULTS, "domain_musiclab.json"), res)
print(json.dumps(res, indent=2))
done("B7")
