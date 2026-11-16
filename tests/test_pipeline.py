"""Unit tests on SYNTHETIC data only. Never on the provided match."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from arena import decode, features, pipeline, priors  # noqa: E402

FPS = 25


def synthetic_game(n=1000):
    """Home has the ball for the first half of the frames, away for the second, ball always near."""
    players = np.full((n, 2, 2), np.nan, dtype=np.float32)
    ball = np.zeros((n, 2), dtype=np.float32) + 50.0
    players[:, 0, :] = 80.0
    players[:, 1, :] = 80.0
    players[: n // 2, 0, :] = 50.5  # home player next to the ball
    players[n // 2:, 1, :] = 50.5   # away player next to the ball
    return {"ball": ball, "players": players, "team": np.array([0, 1]), "pitch": (105.0, 68.0),
            "fps": FPS, "n_frames": n, "runs": [(100, 900)]}


def test_nearest_distances_handles_missing_ball():
    data = synthetic_game()
    ball = data["ball"].copy()
    ball[10] = np.nan
    d_home, d_away = features.nearest_distances(ball, data["players"], data["team"])
    assert np.isnan(d_home[10]) and np.isnan(d_away[10])
    assert d_home[0] < 1.0 and d_away[0] > 10.0


def test_two_clean_possessions_and_x_outside_runs():
    data = synthetic_game()
    labels = pipeline.predict(data, decode.Params())
    assert (labels[:100] == "X").all() and (labels[900:] == "X").all()
    assert (labels[100:490] == "H").all() and (labels[510:900] == "A").all()
    assert pipeline.summary(labels, data["runs"], FPS)["n_possessions"] == 2


def test_short_flicker_does_not_split_a_possession():
    data = synthetic_game()
    data["players"][300:305, 1, :] = 50.2  # away player closer for 5 frames only
    data["players"][300:305, 0, :] = 60.0
    labels = pipeline.predict(data, decode.Params(switch_team_s=1.0))
    assert (labels[100:490] == "H").all()


def test_missing_ball_keeps_current_state():
    data = synthetic_game()
    data["ball"][200:400] = np.nan
    labels = pipeline.predict(data, decode.Params())
    assert (labels[200:400] == "H").all()


def test_ball_out_of_pitch_gives_dead_ball():
    data = synthetic_game()
    data["ball"][300:500] = [-10.0, 30.0]
    labels = pipeline.predict(data, decode.Params(switch_dead_s=0.5))
    assert (labels[320:480] == "D").all()


def test_restart_prior_marks_dead_before_restart():
    data = synthetic_game()
    data["ball"][200:400] = np.nan
    restarts = [{"frame": 400, "team": "H", "kickoff_start": False}]
    params = decode.Params(sp_dead_before_s=6.0, sp_dead_bonus=4.0, switch_dead_s=0.5)
    labels = pipeline.predict(data, params, restarts=restarts)
    assert (labels[260:400] == "D").all()


def test_ball_speed_and_in_flight_gating():
    ball = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [np.nan, np.nan]])
    speed = features.ball_speed(ball, FPS)
    assert np.isnan(speed[0]) and abs(speed[1] - 25.0) < 1e-9 and np.isnan(speed[2])
    data = synthetic_game()
    # away player nearest for 20 frames, but the ball is "in flight" there: no switch
    data["players"][300:320, 1, :] = 50.2
    data["players"][300:320, 0, :] = 60.0
    data["ball"][300:320, 0] = 50.0 + np.arange(20) * 1.0  # 25 m/s
    data["players"][300:320, 1, 0] = data["ball"][300:320, 0] + 0.2
    params = decode.Params(switch_team_s=0.4, fast_speed=15.0, fast_weight=0.0)
    labels = pipeline.predict(data, params)
    assert (labels[100:490] == "H").all()


def test_phase_prior_adds_team_bonus():
    params = decode.Params(phase_team_bonus=0.5)
    prior = priors.phase_prior([{"start": 10, "stop": 20, "team": "A"}], 30, params)
    assert prior[15, decode.A] == 0.5 and prior[25, decode.A] == 0.0 and prior[15, decode.H] == 0


def test_deterministic():
    data = synthetic_game()
    a = pipeline.predict(data, decode.Params())
    b = pipeline.predict(data, decode.Params())
    assert np.array_equal(a, b)


def test_smart_tagging_mapping():
    items = [{"code": "SET PIECES", "start_s": 10.0, "end_s": 14.0,
              "tags": {"Team": "Barcelona", "Type": "Corner Kick"}},
             {"code": "SET PIECES", "start_s": 20.0, "end_s": 24.0,
              "tags": {"Team": "N/A", "Type": "Throw-in"}},
             {"code": "BUILD UP", "start_s": 30.0, "end_s": 40.0, "tags": {"Team": "Atletic Club"}}]
    out = priors.smart_tagging_restarts(items, FPS)
    assert [r["team"] for r in out] == ["H", None]
    assert out[0]["frame"] == 300
