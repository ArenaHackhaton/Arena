"""Restart prior: every set piece is the end of a dead-ball stretch, and often names the team that
restarts. Turned into additive per-frame scores for the decoder.

Restarts come from the Smart Tagging on the provided match (automatic output, used as input) and
from the set-piece events on the external tuning games, degraded with timing jitter and dropped
tags so that tuning does not assume a perfect tagger.

A restart is a dict: {"frame": restart instant (video frame), "team": "H" | "A" | None,
                      "kickoff_start": bool}
"""

import numpy as np

from .decode import A, D, H

TEAM_INDEX = {"H": H, "A": A}


def restart_prior(restarts, runs, n_frames, fps, params):
    """(T, 3) additive scores: D before each restart, the restarting team just after it."""
    prior = np.zeros((n_frames, 3), dtype=float)
    if params.sp_dead_bonus <= 0 and params.sp_team_bonus <= 0:
        return prior
    before = int(round(params.sp_dead_before_s * fps))
    after = int(round(params.sp_team_after_s * fps))
    for restart in restarts:
        frame = int(restart["frame"])
        run = next(((s, e) for s, e in runs if s <= frame < e), None)
        if run is None:
            continue
        start, stop = run
        head = start if restart.get("kickoff_start") else max(start, frame - before)
        prior[head:frame, D] += params.sp_dead_bonus
        team = TEAM_INDEX.get(restart.get("team"))
        if team is not None:
            prior[frame:min(stop, frame + after), team] += params.sp_team_bonus
    return prior


#: Smart Tagging phase codes in which the tagged team is the one with the ball (attacking phases).
#: Defending codes are left out: whether their Team tag names the defending side is not documented.
ATTACKING_CODES = {"build up", "progression", "ball in final third", "ball in the box",
                   "creating chances", "attacking transition", "long ball"}


def phase_prior(phases, n_frames, params):
    """(T, 3) additive scores: a small bonus for the team of each tagged attacking phase.

    A phase is {"start": frame, "stop": frame (exclusive), "team": "H" | "A"}."""
    prior = np.zeros((n_frames, 3), dtype=float)
    if params.phase_team_bonus <= 0:
        return prior
    for phase in phases:
        team = TEAM_INDEX.get(phase.get("team"))
        if team is None:
            continue
        start, stop = max(0, int(phase["start"])), min(n_frames, int(phase["stop"]))
        if stop > start:
            prior[start:stop, team] += params.phase_team_bonus
    return prior


def smart_tagging_phases(instances):
    """Attacking phases with a team, from the official Smart Tagging loader output."""
    out = []
    for item in instances:
        if (item["code"] or "").strip().lower() not in ATTACKING_CODES:
            continue
        team_tag = (item["tags"].get("Team") or "").strip().lower()
        team = "H" if "barcelona" in team_tag else ("A" if "tletic" in team_tag else None)
        if team:
            out.append({"start": item["start_frame"], "stop": item["end_frame"], "team": team})
    return out


def emulate_phases(gt_labels, runs, fps, min_s=5.0, shift_s=3.0, wrong=0.2, drop=0.4, seed=0):
    """External-data stand-in for tagged attacking phases: possessions of at least `min_s`
    seconds from the derived labels, degraded hard (boundary shift, wrong team, dropped) because
    those labels are also the scoring target -- so this tuning is optimistic by construction."""
    rng = np.random.default_rng(seed)
    out = []
    for start, stop in runs:
        window = gt_labels[start:stop]
        change = np.flatnonzero(window[1:] != window[:-1]) + 1
        bounds = np.concatenate(([0], change, [len(window)]))
        for a, b in zip(bounds[:-1], bounds[1:]):
            label = window[a]
            if label not in ("H", "A") or (b - a) < min_s * fps or rng.random() < drop:
                continue
            team = ("A" if label == "H" else "H") if rng.random() < wrong else label
            shift = rng.normal(0.0, shift_s, size=2) * fps
            out.append({"start": start + a + int(shift[0]), "stop": start + b + int(shift[1]),
                        "team": team})
    return out


def smart_tagging_restarts(instances, fps):
    """Restarts from the official Smart Tagging loader output (starter/load_smart_tagging.load).

    The tag marks a window of a few seconds around the restart, so its centre is taken as the
    restart instant. Team names are mapped to sides by club name (DATA.md: home = Barcelona);
    N/A (every throw-in) gives no team.
    """
    out = []
    for item in instances:
        if (item["code"] or "").strip().lower() != "set pieces":
            continue
        tags = item["tags"]
        team_tag = (tags.get("Team") or "").strip().lower()
        team = "H" if "barcelona" in team_tag else ("A" if "tletic" in team_tag else None)
        kind = (tags.get("Type") or "").strip().lower()
        out.append({"frame": int(round((item["start_s"] + item["end_s"]) / 2.0 * fps)),
                    "team": team, "kickoff_start": kind == "kick off (start)"})
    return out


def degrade(restarts, fps, jitter_s=1.0, drop=0.15, seed=0):
    """Imitate an automatic tagger on clean external restarts: Gaussian timing error and misses."""
    rng = np.random.default_rng(seed)
    out = []
    for restart in restarts:
        if rng.random() < drop:
            continue
        moved = dict(restart)
        moved["frame"] = int(round(restart["frame"] + rng.normal(0.0, jitter_s) * fps))
        out.append(moved)
    return out
