"""Robustness of the tuned parameters to a noisier tagger, on EXTERNAL data only.

Compares the grid best (sp_dead_before_s = 15 s) with the submitted value (10 s, arena/config.py)
on Metrica sample games 1 and 2, with restarts degraded more than during tuning: dropped share
{0.15, 0.35, 0.5} x timing error {1 s, 2 s} x 3 seeds. Also scores the submitted parameters with
the tuning-time degradation. Writes tuning/robustness.json; prints aggregates only.

    python scripts/robustness_external.py
"""

import dataclasses
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from arena import config, external_metrica, official, pipeline, priors  # noqa: E402
from tune_external import SEED, score  # noqa: E402

SETTINGS = [(0.15, 1.0), (0.35, 2.0), (0.5, 2.0)]
SEEDS = [10, 11, 12]


def main():
    pm, base = official.metrics(), official.baseline()
    submitted = config.PARAMS
    grid_best = dataclasses.replace(submitted, sp_dead_before_s=15.0)
    report = {"settings": SETTINGS, "seeds": SEEDS, "runs": [], "submitted_tuning_degradation": {}}
    wins = 0
    for g in (1, 2):
        data = external_metrica.load_game(g)
        occluded = external_metrica.simulate_occlusion(
            data["ball"], np.isin(data["gt"], ["H", "A"]), seed=SEED + g)
        baseline = score(pm, data["gt"], pipeline.baseline_labels(data, 50, base, occluded))
        tuned_restarts = priors.degrade(data["restarts_clean"], data["fps"], seed=SEED + g)
        report["submitted_tuning_degradation"][g] = score(
            pm, data["gt"], pipeline.predict(data, submitted, occluded, tuned_restarts))
        for drop, jitter in SETTINGS:
            for seed in SEEDS:
                restarts = priors.degrade(data["restarts_clean"], data["fps"],
                                          jitter_s=jitter, drop=drop, seed=seed)
                s15 = score(pm, data["gt"], pipeline.predict(data, grid_best, occluded, restarts))
                s10 = score(pm, data["gt"], pipeline.predict(data, submitted, occluded, restarts))
                wins += s10["spell_f1"] >= s15["spell_f1"]
                report["runs"].append({"game": g, "drop": drop, "jitter_s": jitter, "seed": seed,
                                       "baseline": baseline["spell_f1"],
                                       "grid_best_15s": s15["spell_f1"],
                                       "submitted_10s": s10["spell_f1"]})
    gains = [r["submitted_10s"] - r["baseline"] for r in report["runs"]]
    report["summary"] = {"n_runs": len(gains), "submitted_beats_baseline": sum(x > 0 for x in gains),
                         "gain_min": round(min(gains), 4), "gain_max": round(max(gains), 4),
                         "10s_at_least_as_good_as_15s": int(wins)}
    print("submitted params, tuning degradation:", report["submitted_tuning_degradation"])
    print("summary:", report["summary"])
    with open(os.path.join(ROOT, "tuning", "robustness.json"), "w") as handle:
        json.dump(report, handle, indent=1)


if __name__ == "__main__":
    main()
