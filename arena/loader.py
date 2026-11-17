"""Load the provided tactical ATD into arrays aligned on video frames (submission rows).

Alignment (DATA.md, games.py, starter/load_atd.py): video_frame = frame_id - 1.
Raw line format (starter/baseline.py): "<frame_id>:<slot>;<slot>;...:<ball>", each group
"x,y,speed[,...]" normalised 0-1, NaN where missing. Team of each slot comes from the metadata
XML via the official baseline's team_of_each_track (first team = home).

Nothing here prints data: only counts and shapes.
"""

import io

import numpy as np
import pandas as pd

from . import official


class TrackingFormatError(Exception):
    """Raised with a message that never contains data values."""


def _group_layout(raw_path):
    with open(raw_path) as handle:
        first = handle.readline().rstrip("\n")
    parts = first.split(":")
    if len(parts) != 3:
        raise TrackingFormatError("expected 3 ':'-separated fields per line, got {}".format(
            len(parts)))
    slots = parts[1].split(";")
    return len(slots), slots[0].count(",") + 1, parts[2].count(",") + 1


def check_homography(data_dir=None):
    """Input validation of the tactical homography (aggregates only).

    The decoder works in pitch metres and does not need the matrices, but the homography tells
    whether a pitch transform exists for each frame (`valid`) and how well it fits
    (`reprojection_error`). Returns the share of valid rows and the median reprojection error
    over the graded halves; raises TrackingFormatError on a malformed file.
    """
    games = official.games()
    path = games.require(["homography"], games.GAME, data_dir)[0]
    try:
        table = pd.read_csv(path, usecols=["frame", "reprojection_error", "valid"])
    except Exception as error:
        raise TrackingFormatError("homography unreadable ({})".format(type(error).__name__))
    n_frames = games.source_frames("tactical", games.GAME)
    if len(table) != n_frames:
        raise TrackingFormatError("homography rows {} != {}".format(len(table), n_frames))
    graded = np.zeros(n_frames, dtype=bool)
    for _, first, last in games.half_video_blocks(games.GAME):
        graded[first:last + 1] = True
    valid = table["valid"].to_numpy()[graded] == 1
    return {"valid_share_graded": round(float(valid.mean()), 4),
            "median_reproj_error_graded": round(float(
                np.nanmedian(table["reprojection_error"].to_numpy()[graded])), 3)}


def load_match(data_dir=None):
    """dict with ball (T,2) m, players (T,N,2) m, team (N,), pitch, fps, n_frames, runs."""
    games = official.games()
    base = official.baseline()
    game = games.GAME
    meta_path, raw_path = games.require(["atd_meta", "atd_raw"], game, data_dir)
    n_frames = games.source_frames("tactical", game)
    length, width = games.GAMES[game]["pitch"]
    fps = games.GAMES[game]["fps"]

    team = base.team_of_each_track(meta_path)
    n_slots, per_slot, per_ball = _group_layout(raw_path)
    if n_slots != len(team):
        raise TrackingFormatError("slot count {} != metadata players {}".format(
            n_slots, len(team)))

    with open(raw_path) as handle:
        text = handle.read()
    n_lines = text.count("\n") + (0 if text.endswith("\n") else 1)
    if text.count(";") != n_lines * (n_slots - 1):
        raise TrackingFormatError("inconsistent slot count across lines")
    text = text.replace(":", ",").replace(";", ",")
    n_cols = 1 + n_slots * per_slot + per_ball
    try:
        table = pd.read_csv(io.StringIO(text), header=None, dtype=np.float32,
                            na_values=["NaN", "nan"], engine="c").to_numpy()
    except Exception as error:  # never echo the parser message: it can quote a line
        raise TrackingFormatError("parse failed ({})".format(type(error).__name__))
    del text
    if table.shape[1] != n_cols:
        raise TrackingFormatError("expected {} columns, got {}".format(n_cols, table.shape[1]))

    frame_id = table[:, 0].astype(np.int64)
    video_frame = frame_id - 1
    if video_frame.min() < 0 or video_frame.max() >= n_frames:
        raise TrackingFormatError("frame ids outside 1..{}".format(n_frames))

    slots = table[:, 1:1 + n_slots * per_slot].reshape(len(table), n_slots, per_slot)[:, :, :2]
    ball = table[:, 1 + n_slots * per_slot:1 + n_slots * per_slot + 2]
    scale = np.array([length, width], dtype=np.float32)

    players_xy = np.full((n_frames, n_slots, 2), np.nan, dtype=np.float32)
    ball_xy = np.full((n_frames, 2), np.nan, dtype=np.float32)
    players_xy[video_frame] = slots * scale
    ball_xy[video_frame] = ball * scale

    runs = [(first, last + 1) for _, first, last in games.half_video_blocks(game)]
    return {
        "ball": ball_xy, "players": players_xy, "team": np.asarray(team),
        "pitch": (length, width), "fps": fps, "n_frames": n_frames, "runs": runs,
        "n_records": int(len(table)),
        "contiguous": bool(len(table) == n_frames and
                           np.array_equal(video_frame, np.arange(n_frames))),
    }
