"""Per-frame evidence and Viterbi decoding of the possession state (H, A, D).

Why Viterbi rather than a majority vote: spellF1 matches whole possessions by temporal IoU, so a
single spurious flicker splits one true possession into two predicted ones and can lose both
matches. A switch penalty makes every change of state pay for itself with sustained evidence.

Evidence model (log-scores, larger = more likely), per frame:
  * ball visible, on the pitch:  H = -min(d_home, clip) / radius
                                 A = -min(d_away, clip) / radius
                                 D = -dead_cost
    d_team is the distance in metres from the ball to the nearest tracked player of that team.
  * ball outside the pitch by more than out_margin metres: H = A = -out_cost, D = 0.
  * ball not tracked: 0 for every state -- no evidence, so the decoder keeps its current state
    unless a switch is worth its penalty. This is the "propagate through occlusions" rule.

Switch penalties are given in seconds of evidence and multiplied by fps, so the same parameters
mean the same thing at any frame rate.
"""

from dataclasses import asdict, dataclass

import numpy as np

H, A, D = 0, 1, 2
STATE_LABELS = np.array(["H", "A", "D"])


@dataclass(frozen=True)
class Params:
    radius: float = 2.0          # metres; distance scale of the evidence
    dead_cost: float = 3.0       # evidence cost of D on a visible, in-play ball
    switch_team_s: float = 1.0   # penalty of an H<->A change, in seconds of evidence
    switch_dead_s: float = 1.0   # penalty of entering or leaving D, in seconds of evidence
    dist_clip: float = 15.0      # metres; distances beyond this carry no extra information
    out_margin: float = 1.0      # metres beyond the lines before the ball counts as out
    out_cost: float = 3.0        # evidence against H and A while the ball is out
    sp_dead_before_s: float = 6.0  # seconds of dead ball assumed before each tagged restart
    sp_dead_bonus: float = 0.0     # per-frame D bonus in that window (0 = restart prior off)
    sp_team_after_s: float = 2.0   # seconds after a restart favouring the restarting team
    sp_team_bonus: float = 0.0     # per-frame bonus for that team (0 = off)
    fast_speed: float = 1e9        # m/s; above it the ball is in flight (pass, shot)
    fast_weight: float = 1.0       # weight of the distance evidence on an in-flight ball
    phase_team_bonus: float = 0.0  # per-frame bonus for the team of a Smart Tagging phase

    def as_dict(self):
        return asdict(self)


def evidence(d_home, d_away, ball_visible, ball_out, params, speed=None):
    """(T, 3) float array of per-frame log-scores for H, A, D.

    If `speed` (m/s) is given, frames where the ball moves faster than params.fast_speed have
    their in-play evidence scaled by params.fast_weight: the player nearest to a ball in flight
    is often not the one who has it."""
    d_home = np.asarray(d_home, dtype=float)
    d_away = np.asarray(d_away, dtype=float)
    visible = np.asarray(ball_visible, dtype=bool)
    out = np.asarray(ball_out, dtype=bool) & visible

    clip = params.dist_clip
    home = np.where(np.isnan(d_home), clip, np.minimum(d_home, clip))
    away = np.where(np.isnan(d_away), clip, np.minimum(d_away, clip))

    scores = np.zeros((len(d_home), 3), dtype=float)
    in_play = visible & ~out
    scores[in_play, H] = -home[in_play] / params.radius
    scores[in_play, A] = -away[in_play] / params.radius
    scores[in_play, D] = -params.dead_cost
    if speed is not None and params.fast_weight != 1.0:
        speed = np.asarray(speed, dtype=float)
        with np.errstate(invalid="ignore"):
            fast = in_play & (speed > params.fast_speed)
        scores[fast] *= params.fast_weight
    scores[out, H] = -params.out_cost
    scores[out, A] = -params.out_cost
    scores[out, D] = 0.0
    return scores


def transition_costs(params, fps):
    """3x3 cost of moving from state i (row) to state j (column)."""
    team = params.switch_team_s * fps
    dead = params.switch_dead_s * fps
    return [[0.0, team, dead],
            [team, 0.0, dead],
            [dead, dead, 0.0]]


def viterbi(scores, costs):
    """Most likely state path for a (T, 3) score array. Plain Python loop: 3 states is tiny."""
    n = len(scores)
    if n == 0:
        return np.zeros(0, dtype=np.int8)
    back = np.zeros((n, 3), dtype=np.int8)
    rows = scores.tolist()
    prev = list(rows[0])
    for t in range(1, n):
        row = rows[t]
        cur = [0.0, 0.0, 0.0]
        bt = back[t]
        for j in range(3):
            best_i, best_v = 0, prev[0] - costs[0][j]
            for i in (1, 2):
                v = prev[i] - costs[i][j]
                if v > best_v:
                    best_i, best_v = i, v
            cur[j] = best_v + row[j]
            bt[j] = best_i
        prev = cur
    path = np.zeros(n, dtype=np.int8)
    path[-1] = int(np.argmax(prev))
    for t in range(n - 1, 0, -1):
        path[t - 1] = back[t, path[t]]
    return path


def decode(d_home, d_away, ball_visible, ball_out, runs, n_frames, params, fps, prior=None,
           speed=None):
    """Label array of length n_frames: H/A/D inside each graded run, X everywhere else.

    Each run (half) is decoded on its own so that no state is carried across halftime.
    `prior` is an optional (T, 3) array added to the evidence (see priors.py).
    """
    scores = evidence(d_home, d_away, ball_visible, ball_out, params, speed)
    if prior is not None:
        scores = scores + prior
    costs = transition_costs(params, fps)
    labels = np.full(n_frames, "X", dtype="<U1")
    for start, stop in runs:
        path = viterbi(scores[start:stop], costs)
        labels[start:stop] = STATE_LABELS[path]
    return labels
