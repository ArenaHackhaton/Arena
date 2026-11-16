"""External tuning data: Metrica Sports public sample games, with possession labels derived from
their human-annotated event data.

Source: https://github.com/metrica-sports/sample-data (commit e706dd5), anonymised games, 25 fps,
pitch 105 x 68 m, coordinates normalised 0-1. Terms (README "Legal stuff"): use responsibly and
acknowledge the source for any public use. None of it is the provided game (BAR-ATH, 2024-25).
The data is never committed: it is cloned into a gitignored folder (see scripts/get_external.py).

Possession labels H / A / D derived from the events (rules documented in docs/TUNING.md):
  * PASS, SHOT, SET PIECE, RECOVERY, BALL LOST: the acting team has the ball from the event's
    start frame until the next labelled change.
  * BALL OUT: dead ball from its end frame (ball crosses the line) until the next team event.
  * FAULT RECEIVED: dead ball from its start frame until the next team event (the free kick).
  * SHOT ending in a goal: dead ball from its end frame until the kick-off.
  * CHALLENGE, CARD: no change.
  * Graded window per period: first event start .. last event end. Everything else is X.

Ball occlusion: the provided match loses the ball on ~41% of graded frames. The sample games lose
it on nearly every dead-ball frame but rarely in play. simulate_occlusion() removes the ball on
random contiguous blocks (seeded) of in-play frames until ~41% of them have no ball, so the
decoder is tuned under comparable blindness during play.
"""

import os

import numpy as np
import pandas as pd

PITCH = (105.0, 68.0)
FPS = 25
TEAM_STATES = {"Home": "H", "Away": "A"}
POSSESSION_TYPES = {"PASS", "SHOT", "SET PIECE", "RECOVERY", "BALL LOST"}
DEFAULT_DIR = os.environ.get("ARENA_EXTERNAL_DIR") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "external", "sample-data")


def _read_tracking(path):
    table = pd.read_csv(path, skiprows=2, low_memory=False)
    frames = table["Frame"].to_numpy(dtype=np.int64)
    coords = table.iloc[:, 3:].to_numpy(dtype=np.float32)
    if coords.shape[1] % 2:
        raise ValueError("odd number of coordinate columns in {}".format(os.path.basename(path)))
    pairs = coords.reshape(len(table), -1, 2)
    return frames, pairs[:, :-1, :], pairs[:, -1, :]  # players, ball (last pair)


def derive_labels(events, n_frames):
    """Possession label per tracking frame (index = Frame - 1) from the event table."""
    changes = []  # (frame, order, state)
    order = 0
    ordered = events.sort_values(["Start Frame", "End Frame"], kind="mergesort")
    for team_name, kind, sub, start_f, end_f in zip(
            ordered["Team"], ordered["Type"], ordered["Subtype"],
            ordered["Start Frame"], ordered["End Frame"]):
        kind = str(kind).upper()
        sub = str(sub).upper()
        start = int(start_f) - 1
        end = int(end_f) - 1 if not pd.isna(end_f) else start
        team = TEAM_STATES.get(str(team_name))
        if kind in POSSESSION_TYPES and team:
            changes.append((start, order, team)); order += 1
            if kind == "SHOT" and "GOAL" in sub and "OUT" not in sub:
                changes.append((end, order, "D")); order += 1
        elif kind == "BALL OUT":
            changes.append((end, order, "D")); order += 1
        elif kind == "FAULT RECEIVED":
            changes.append((start, order, "D")); order += 1
    changes.sort()

    labels = np.full(n_frames, "X", dtype="<U1")
    runs = []
    for _, period in events.groupby("Period"):
        first = int(period["Start Frame"].min()) - 1
        last = int(np.nanmax(period[["Start Frame", "End Frame"]].to_numpy())) - 1
        first, last = max(first, 0), min(last, n_frames - 1)
        state = None
        span = [c for c in changes if first <= c[0] <= last]
        # state at the head of the period: first change inside it
        state = span[0][2] if span else "D"
        idx = 0
        for frame in range(first, last + 1):
            while idx < len(span) and span[idx][0] <= frame:
                state = span[idx][2]
                idx += 1
            labels[frame] = state
        runs.append((first, last + 1))
    return labels, runs


def load_game(game, root=DEFAULT_DIR):
    folder = os.path.join(root, "data", "Sample_Game_{}".format(game))
    stem = os.path.join(folder, "Sample_Game_{}_".format(game))
    frames_h, home, ball = _read_tracking(stem + "RawTrackingData_Home_Team.csv")
    frames_a, away, _ = _read_tracking(stem + "RawTrackingData_Away_Team.csv")
    if not np.array_equal(frames_h, frames_a):
        raise ValueError("home and away tracking frames differ")
    n_frames = int(frames_h.max())
    index = frames_h - 1

    players = np.full((n_frames, home.shape[1] + away.shape[1], 2), np.nan, dtype=np.float32)
    ball_xy = np.full((n_frames, 2), np.nan, dtype=np.float32)
    scale = np.array(PITCH, dtype=np.float32)
    players[index] = np.concatenate([home, away], axis=1) * scale
    ball_xy[index] = ball * scale
    team = np.array([0] * home.shape[1] + [1] * away.shape[1])

    events = pd.read_csv(stem + "RawEventsData.csv")
    labels, runs = derive_labels(events, n_frames)
    return {"ball": ball_xy, "players": players, "team": team, "pitch": PITCH, "fps": FPS,
            "n_frames": n_frames, "runs": runs, "gt": labels, "n_events": int(len(events)),
            "restarts_clean": restarts_from_events(events)}


def restarts_from_events(events):
    """Restarts as the Smart Tagging would report them: set pieces and goal kicks, with the team
    removed on throw-ins (the provided tagging tags every throw-in N/A)."""
    out, seen_periods = [], set()
    ordered = events.sort_values("Start Frame", kind="mergesort")
    for team_name, kind, sub, period, start_f in zip(
            ordered["Team"], ordered["Type"], ordered["Subtype"], ordered["Period"],
            ordered["Start Frame"]):
        kind, sub = str(kind).upper(), str(sub).upper()
        if kind == "SET PIECE" or (kind == "PASS" and "GOAL KICK" in sub):
            team = TEAM_STATES.get(str(team_name))
            if "THROW IN" in sub:
                team = None
            first_kickoff = "KICK OFF" in sub and period not in seen_periods
            if "KICK OFF" in sub:
                seen_periods.add(period)
            out.append({"frame": int(start_f) - 1, "team": team, "kickoff_start": first_kickoff})
    return out


def simulate_occlusion(ball_xy, eligible, target=0.41, mean_block_s=2.0, fps=FPS, seed=0):
    """Copy of ball_xy with the ball removed on random blocks until `target` of the eligible
    frames have no ball. Natural gaps count towards the target.

    In the sample games the ball is already missing on almost every dead-ball frame (it is not
    tracked out of play) but on only 10-23% of in-play frames, so `eligible` is the in-play (H/A)
    frames: occlusion is raised where the provided match loses the ball, during play."""
    rng = np.random.default_rng(seed)
    ball = ball_xy.copy()
    graded = np.asarray(eligible, dtype=bool)
    graded_idx = np.flatnonzero(graded)
    missing = np.isnan(ball).any(axis=1)
    need = int(target * len(graded_idx)) - int(missing[graded].sum())
    while need > 0:
        length = max(1, int(rng.geometric(1.0 / (mean_block_s * fps))))
        start = int(rng.choice(graded_idx))
        block = slice(start, min(start + length, len(ball)))
        newly = int((~np.isnan(ball[block]).any(axis=1) & graded[block]).sum())
        ball[block] = np.nan
        need -= newly
    return ball
