"""Parameters used for the submission. Chosen on EXTERNAL data only (scripts/tune_external.py,
results in tuning/results.json, rationale in docs/TUNING.md). Never tuned on the provided game,
its public ground truth or its video.

Grid search best on Metrica sample game 1, checked on game 2; sp_dead_before_s set to 10 s
rather than the 15 s grid optimum because it was at least as good on 15 of 18 robustness runs
with a noisier tagger (more dropped restarts, larger timing error) -- see
scripts/robustness_external.py, tuning/robustness.json and docs/TUNING.md.
"""

from .decode import Params

PARAMS = Params(
    radius=2.0,
    dead_cost=2.0,
    switch_team_s=1.0,
    switch_dead_s=2.0,
    dist_clip=15.0,
    out_margin=1.0,
    out_cost=3.0,
    sp_dead_before_s=10.0,
    sp_dead_bonus=1.0,
    sp_team_after_s=2.0,
    sp_team_bonus=2.0,
    # Stage 3 (scripts/tune_stage3.py, tuning/stage3.json): ignore the nearest-player evidence
    # when the ball moves faster than 15 m/s (in flight). +0.007 / +0.002 spellF1 on Metrica
    # games 1 / 2: within noise but never worse, and physically motivated.
    fast_speed=15.0,
    fast_weight=0.0,
    # Smart Tagging phase prior tested and NOT used (phase_team_bonus = 0): mixed results
    # (-0.002 / +0.01 to +0.02) on an emulation that is optimistic by construction.
    phase_team_bonus=0.0,
)
