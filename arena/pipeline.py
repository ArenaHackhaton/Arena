"""One function from loaded tracking to labels, used identically on the match and on external data.

Parameters live in arena/config.py (the values used for the submission) and are passed in as a
decode.Params; nothing here is tuned.
"""

import numpy as np

from . import decode, features, priors


def predict(data, params, ball_xy=None, restarts=None):
    """Label array (H/A/D in graded runs, X elsewhere) for a loaded game dict.

    `restarts` (list of restart dicts, see priors.py) defaults to data["restarts"] if present.
    """
    ball = data["ball"] if ball_xy is None else ball_xy
    restarts = data.get("restarts", []) if restarts is None else restarts
    d_home, d_away = features.nearest_distances(ball, data["players"], data["team"])
    visible, out = features.ball_flags(ball, data["pitch"], params.out_margin)
    prior = priors.restart_prior(restarts, data["runs"], data["n_frames"], data["fps"], params)
    return decode.decode(d_home, d_away, visible, out, data["runs"], data["n_frames"],
                         params, data["fps"], prior)


def baseline_labels(data, window, baseline_module, ball_xy=None):
    """The official baseline (nearest tracked player, centred majority vote of +/- window frames),
    reproduced on any loaded game with the official smooth() function. X outside graded runs."""
    ball = data["ball"] if ball_xy is None else ball_xy
    d_home, d_away = features.nearest_distances(ball, data["players"], data["team"])
    codes = np.full(data["n_frames"], -1, dtype=np.int8)
    seen = ~np.isnan(d_home) | ~np.isnan(d_away)
    home_closer = np.nan_to_num(d_home, nan=np.inf) <= np.nan_to_num(d_away, nan=np.inf)
    codes[seen] = np.where(home_closer[seen], 0, 1)
    labels = np.asarray(baseline_module.smooth(codes, window), dtype="<U1")
    graded = np.zeros(data["n_frames"], dtype=bool)
    for start, stop in data["runs"]:
        graded[start:stop] = True
    labels[~graded] = "X"
    return labels


def summary(labels, runs, fps):
    """Aggregates only: label counts, number and mean duration of possessions (H/A runs)."""
    out = {name: int(np.sum(labels == name)) for name in ("H", "A", "D", "X")}
    n_spells, alive = 0, 0
    for start, stop in runs:
        window = labels[start:stop]
        if not len(window):
            continue
        change = np.flatnonzero(window[1:] != window[:-1]) + 1
        heads = np.concatenate(([0], change))
        n_spells += int(np.isin(window[heads], ["H", "A"]).sum())
        alive += int(np.isin(window, ["H", "A"]).sum())
    out["n_possessions"] = n_spells
    out["mean_possession_s"] = round(alive / float(fps) / n_spells, 2) if n_spells else 0.0
    return out
