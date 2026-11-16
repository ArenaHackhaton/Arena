"""Per-frame features from positions in metres: nearest player of each team to the ball.

Shared by the provided match and the external tuning data, so both go through identical code.
"""

import warnings

import numpy as np


def nearest_distances(ball_xy, players_xy, team_of_slot):
    """(d_home, d_away): distance in metres from the ball to the nearest player of each team.

    ball_xy     (T, 2) metres, NaN where the ball is not tracked
    players_xy  (T, N, 2) metres, NaN where a slot is empty
    team_of_slot (N,) 0 = home, 1 = away
    NaN where the ball or every player of that team is missing.
    """
    ball_xy = np.asarray(ball_xy, dtype=np.float32)
    players_xy = np.asarray(players_xy, dtype=np.float32)
    team_of_slot = np.asarray(team_of_slot)
    out = []
    for team in (0, 1):
        slots = players_xy[:, team_of_slot == team, :]
        diff = slots - ball_xy[:, None, :]
        dist = np.sqrt((diff ** 2).sum(axis=2))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)  # all-NaN rows -> NaN, expected
            out.append(np.nanmin(dist, axis=1) if dist.shape[1] else
                       np.full(len(ball_xy), np.nan))
    return out[0], out[1]


def ball_flags(ball_xy, pitch, margin):
    """(visible, out_of_pitch) booleans. Coordinates have their origin at a corner of the pitch."""
    ball_xy = np.asarray(ball_xy, dtype=float)
    length, width = pitch
    visible = ~np.isnan(ball_xy).any(axis=1)
    x, y = ball_xy[:, 0], ball_xy[:, 1]
    with np.errstate(invalid="ignore"):
        out = visible & ((x < -margin) | (x > length + margin) |
                         (y < -margin) | (y > width + margin))
    return visible, out
