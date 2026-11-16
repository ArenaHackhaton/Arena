"""Parameters used for the submission. Chosen on EXTERNAL data only (scripts/tune_external.py,
results in tuning/results.json, rationale in docs/TUNING.md). Never tuned on the provided game,
its public ground truth or its video.

Grid search best on Metrica sample game 1, checked on game 2; sp_dead_before_s set to 10 s
rather than the 15 s grid optimum because it was at least as good on 14 of 18 robustness runs
with a noisier tagger (more dropped restarts, larger timing error) -- see docs/TUNING.md.
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
)
