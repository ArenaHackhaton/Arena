"""Regenerate the submission CSV from the provided data, then validate it.

    python scripts/make_submission.py                  # -> submissions/CulersFromSN.csv

Deterministic: no randomness on the match path, so the same code and data give the same file
byte for byte. Prints aggregates only (counts, possessions, timing) -- never frame-level data.
"""

import argparse
import hashlib
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from arena import config, loader, official, pipeline, priors  # noqa: E402


def log(tag, message):
    print("[{}] {}".format(tag, message), flush=True)


def write_csv(path, labels):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as handle:
        handle.write("frame,label\n")
        handle.writelines("{},{}\n".format(i, label) for i, label in enumerate(labels))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--name", default="CulersFromSN", help="file stem (the team name)")
    parser.add_argument("--out", default=os.path.join(ROOT, "submissions"))
    args = parser.parse_args()
    t0 = time.time()

    log("START", "loading tactical ATD")
    try:
        data = loader.load_match()
    except Exception as error:  # report the kind of failure only, never data
        log("RESULT", "load failed: {} {}".format(type(error).__name__,
                                                  getattr(error, "args", [""])[0]
                                                  if isinstance(error, loader.TrackingFormatError)
                                                  else ""))
        sys.exit(1)
    log("RESULT", "{} records, contiguous={}, ball visible on {:.1f}% of graded frames".format(
        data["n_records"], data["contiguous"], 100.0 * sum(
            (~(data["ball"][a:b] != data["ball"][a:b]).any(axis=1)).sum()
            for a, b in data["runs"]) / sum(b - a for a, b in data["runs"])))

    log("CALL", "homography input check")
    try:
        log("RESULT", "homography {}".format(loader.check_homography()))
    except Exception as error:  # informative only: the decoder does not use the matrices
        log("RESULT", "homography check skipped: {}".format(type(error).__name__))

    log("CALL", "smart tagging restarts")
    st = official.smart_tagging()
    data["restarts"] = priors.smart_tagging_restarts(st.load(), data["fps"])
    log("RESULT", "{} restarts ({} with a team)".format(
        len(data["restarts"]), sum(r["team"] is not None for r in data["restarts"])))

    log("CALL", "decode with params {}".format(config.PARAMS.as_dict()))
    labels = pipeline.predict(data, config.PARAMS)
    path = os.path.join(args.out, "{}.csv".format(args.name))
    write_csv(path, labels)
    with open(path, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()[:16]
    log("RESULT", "summary {}".format(pipeline.summary(labels, data["runs"], data["fps"])))
    log("RESULT", "wrote {} (sha256 {}) in {:.0f} s".format(
        os.path.relpath(path, ROOT), digest, time.time() - t0))

    log("CALL", "official validator")
    validator = os.path.join(official.OFFICIAL_DIR, "evaluation", "validate_submission.py")
    result = subprocess.run([sys.executable, validator, path])
    log("STATE", "validator exit code {}".format(result.returncode))
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
