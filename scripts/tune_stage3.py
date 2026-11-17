"""Stage 3 of the external tuning: ball-speed gating and Smart Tagging phase prior, on top of the
submitted parameters (arena/config.py). EXTERNAL data only (Metrica sample games 1 and 2).

Each addition is kept only if it improves spellF1 on game 1 without hurting game 2.
Writes tuning/stage3.json; prints aggregates only.

    python scripts/tune_stage3.py
"""

import dataclasses
import itertools
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from arena import config, external_metrica, official, pipeline, priors  # noqa: E402
from tune_external import SEED, score  # noqa: E402

GRID = {
    "fast_speed": [1e9, 10.0, 15.0, 20.0],
    "fast_weight": [0.0, 0.25, 0.5],
    "phase_team_bonus": [0.0, 0.05, 0.1, 0.2],
}


def main():
    pm = official.metrics()
    games = {}
    for g in (1, 2):
        data = external_metrica.load_game(g)
        data["ball_occluded"] = external_metrica.simulate_occlusion(
            data["ball"], np.isin(data["gt"], ["H", "A"]), seed=SEED + g)
        data["restarts"] = priors.degrade(data["restarts_clean"], data["fps"], seed=SEED + g)
        data["phases"] = priors.emulate_phases(data["gt"], data["runs"], data["fps"], seed=SEED + g)
        games[g] = data
        print("game {}: {} emulated phases".format(g, len(data["phases"])))

    rows, seen = [], set()
    for values in itertools.product(*GRID.values()):
        params = dataclasses.replace(config.PARAMS, **dict(zip(GRID, values)))
        key = (params.fast_speed if params.fast_weight != 1.0 else None, params.fast_weight,
               params.phase_team_bonus)
        if params.fast_speed >= 1e9 and params.fast_weight != 0.0:
            continue  # gating off: one row is enough
        if key in seen:
            continue
        seen.add(key)
        row = {"params": dict(zip(GRID, values))}
        for g, data in games.items():
            row[g] = score(pm, data["gt"], pipeline.predict(data, params, data["ball_occluded"]))
        rows.append(row)
    rows.sort(key=lambda r: -r[1]["spell_f1"])
    reference = next(r for r in rows if r["params"]["fast_speed"] >= 1e9
                     and r["params"]["phase_team_bonus"] == 0.0)
    print("reference (submitted params):", reference[1], reference[2])
    for row in rows[:10]:
        print(row["params"], "| tune", row[1], "| check", row[2])
    with open(os.path.join(ROOT, "tuning", "stage3.json"), "w") as handle:
        json.dump({"grid": GRID, "reference": reference, "results": rows}, handle, indent=1)


if __name__ == "__main__":
    main()
