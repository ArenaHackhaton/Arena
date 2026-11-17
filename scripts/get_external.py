"""Fetch the external tuning data (Metrica Sports public sample games) at a pinned commit.

    python scripts/get_external.py            # -> external/sample-data (gitignored)

Source: https://github.com/metrica-sports/sample-data, commit e706dd506b360d69d9d123d5b8026e7294b13996.
Terms (README, "Legal stuff"): use the data responsibly and acknowledge the source for any public
use. The data is never committed to this repository. Set ARENA_EXTERNAL_DIR to use another folder.
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "https://github.com/metrica-sports/sample-data.git"
COMMIT = "e706dd506b360d69d9d123d5b8026e7294b13996"


def main():
    target = os.environ.get("ARENA_EXTERNAL_DIR") or os.path.join(ROOT, "external", "sample-data")
    if not os.path.isdir(target):
        os.makedirs(os.path.dirname(target), exist_ok=True)
        subprocess.run(["git", "clone", "--quiet", URL, target], check=True)
    subprocess.run(["git", "-C", target, "checkout", "--quiet", COMMIT], check=True)
    print("external data at {} (commit {})".format(target, COMMIT[:7]))


if __name__ == "__main__":
    sys.exit(main())
