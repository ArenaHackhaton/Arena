"""Access to the organisers' repository (scorer, games table, baseline helpers).

The official repository is read-only for us and is NOT vendored: we import it from disk.
Its location defaults to a sibling folder `../more-than-a-hack-2027` next to this repository and
can be overridden with the MTAH_OFFICIAL_DIR environment variable.

Source of the imported code: https://github.com/metrica-sports/more-than-a-hack-2027
(MIT licence for code and documentation).
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFICIAL_DIR = os.environ.get("MTAH_OFFICIAL_DIR") or os.path.join(
    os.path.dirname(REPO_ROOT), "more-than-a-hack-2027")


def _ensure_path():
    if not os.path.isdir(OFFICIAL_DIR):
        raise FileNotFoundError(
            "official repository not found at {} (set MTAH_OFFICIAL_DIR)".format(OFFICIAL_DIR))
    for folder in (OFFICIAL_DIR, os.path.join(OFFICIAL_DIR, "evaluation")):
        if folder not in sys.path:
            sys.path.insert(0, folder)


def metrics():
    """The official scorer module, evaluation/possession_metrics.py."""
    _ensure_path()
    import possession_metrics
    return possession_metrics


def games():
    """The official games table, games.py."""
    _ensure_path()
    import games as games_module
    return games_module


def _starter(name):
    _ensure_path()
    starter = os.path.join(OFFICIAL_DIR, "starter")
    if starter not in sys.path:
        sys.path.insert(0, starter)
    return __import__(name)


def baseline():
    """The official baseline module, starter/baseline.py."""
    return _starter("baseline")


def smart_tagging():
    """The official Smart Tagging loader, starter/load_smart_tagging.py."""
    return _starter("load_smart_tagging")
