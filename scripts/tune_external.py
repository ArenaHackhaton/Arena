"""Grid search of the decoder parameters on EXTERNAL data only (Metrica sample games 1 and 2).

Tune on game 1, check on game 2 (held out), and report the official baseline (+/-50 majority vote)
on the same data for comparison. Scored with the official spellF1 (evaluation/possession_metrics.py).
Prints aggregates only; writes tuning/results.json.

Stage 1 tunes the tracking evidence and switch penalties with the restart prior off.
Stage 2 keeps the best stage-1 values and tunes the restart prior (degraded restarts).

    python scripts/tune_external.py
"""

import dataclasses
import itertools
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from arena import decode, external_metrica, official, pipeline, priors  # noqa: E402

STAGE1 = {
    "radius": [1.0, 2.0, 4.0],
    "dead_cost": [1.0, 2.0, 4.0],
    "switch_team_s": [0.25, 0.5, 1.0, 2.0],
    "switch_dead_s": [0.25, 0.5, 1.0, 2.0],
}
STAGE2 = {
    "sp_dead_before_s": [3.0, 6.0, 10.0, 15.0],
    "sp_dead_bonus": [0.0, 1.0, 2.0, 4.0],
    "sp_team_after_s": [1.0, 2.0],
    "sp_team_bonus": [0.0, 1.0, 2.0],
}
TUNE_GAME, CHECK_GAME = 1, 2
SEED = 0


def score(pm, gt, pred):
    gt_codes, pred_codes = pm.label_codes(gt), pm.label_codes(pred)
    runs = pm.valid_runs(gt_codes)
    filled = pm.fill_abstentions(pred_codes, runs)
    spells = pm.spell_scores(gt_codes, filled, runs)
    cm3 = pm.scored_confusion(pm.confusion(gt_codes, pred_codes))
    return {"spell_f1": round(spells["mean_f1"], 4), "macro_f1": round(pm.macro_f1(cm3), 4),
            "n_pred": spells["n_pred"], "n_gt": spells["n_gt"]}


def search(pm, games, base_params, grid):
    keys, rows = list(grid), []
    for values in itertools.product(*(grid[k] for k in keys)):
        params = dataclasses.replace(base_params, **dict(zip(keys, values)))
        row = {"params": dict(zip(keys, values))}
        for g, data in games.items():
            pred = pipeline.predict(data, params, data["ball_occluded"], data["restarts"])
            row[g] = score(pm, data["gt"], pred)
        rows.append(row)
    rows.sort(key=lambda r: -r[TUNE_GAME]["spell_f1"])
    return rows


def show(title, rows, n=8):
    print("\n" + title)
    for row in rows[:n]:
        print(row["params"], "| tune", row[TUNE_GAME], "| check", row[CHECK_GAME])


def main():
    t0 = time.time()
    pm, base = official.metrics(), official.baseline()
    games = {}
    for g in (TUNE_GAME, CHECK_GAME):
        data = external_metrica.load_game(g)
        data["ball_occluded"] = external_metrica.simulate_occlusion(
            data["ball"], np.isin(data["gt"], ["H", "A"]), seed=SEED + g)
        data["restarts"] = priors.degrade(data["restarts_clean"], data["fps"], seed=SEED + g)
        games[g] = data
        print("game {}: {} frames, {} events, {} graded, {} restarts ({} kept)".format(
            g, data["n_frames"], data["n_events"], sum(b - a for a, b in data["runs"]),
            len(data["restarts_clean"]), len(data["restarts"])))

    report = {"seed": SEED, "stage1": STAGE1, "stage2": STAGE2, "baseline_smooth50": {}}
    for g, data in games.items():
        labels = pipeline.baseline_labels(data, 50, base, data["ball_occluded"])
        report["baseline_smooth50"][g] = score(pm, data["gt"], labels)
    print("baseline smooth50:", report["baseline_smooth50"])

    rows1 = search(pm, games, decode.Params(), STAGE1)
    show("stage 1, top on game {} (tuning) with game {} (held out):".format(
        TUNE_GAME, CHECK_GAME), rows1)
    best1 = dataclasses.replace(decode.Params(), **rows1[0]["params"])

    rows2 = search(pm, games, best1, STAGE2)
    show("stage 2 (restart prior), on top of the best stage-1 values:", rows2)
    best = dataclasses.replace(best1, **rows2[0]["params"])

    report.update({"stage1_results": rows1, "stage2_results": rows2,
                   "best_params": best.as_dict(),
                   "best_scores": {g: rows2[0][g] for g in games}})
    print("\nbest params:", best.as_dict())
    os.makedirs(os.path.join(ROOT, "tuning"), exist_ok=True)
    with open(os.path.join(ROOT, "tuning", "results.json"), "w") as handle:
        json.dump(report, handle, indent=1, default=str)
    print("done in {:.0f} s".format(time.time() - t0))


if __name__ == "__main__":
    main()
