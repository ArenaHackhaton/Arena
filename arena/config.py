"""Parameters used for the submission. Chosen on EXTERNAL data only (scripts/tune_external.py,
results in tuning/results.json, rationale in docs/TUNING.md). Never tuned on the provided game,
its public ground truth or its video.
"""

from .decode import Params

PARAMS = Params()
