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
