"""Run the Opus review audit and pre-registered experiment; writes JSON evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from research.opus_review import audit
from research.opus_review.core import ROOT

AUDIT_TASKS = {
    "inputs": audit.input_audit,
    "period27": audit.p27_audit,
    "legacy_exports": audit.legacy_exports_audit,
    "period_ladder": audit.period_ladder,
    "progressive": audit.progressive_audit,
    "feedback": audit.feedback_audit,
    "recurrence": audit.recurrence_audit,
    "running_key": audit.running_key_audit,
    "planted": audit.planted_audit,
    "identifiability": audit.identifiability,
    "gromark_bean": audit.gromark_audit,
    "transcription_shift": audit.transcription_shift_audit,
    "english_running_key": audit.english_running_key_audit,
    "ic_period": audit.ic_period_audit,
    "width_bigrams": audit.width_bigram_audit,
}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")


def manifest(outdir):
    """Hashes of every review output and source, plus the environment that produced them."""
    import hashlib
    import platform
    import subprocess
    import numpy
    files = sorted(p for p in list(outdir.rglob("*")) + list((ROOT / "research/opus_review").glob("*.py"))
                   + [ROOT / "tests/test_opus_review.py", ROOT / "docs/OPUS_K4_EXPERIMENT_PREREG.md",
                      ROOT / "docs/OPUS_K4_REVIEW.md"]
                   if p.is_file() and p.name != "manifest.json" and "__pycache__" not in p.parts)
    git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {"base_commit": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
            "python": platform.python_version(), "numpy": numpy.__version__, "platform": platform.platform(),
            "files": {str(p.relative_to(ROOT)): {"bytes": p.stat().st_size,
                                                  "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                      for p in files}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=ROOT / "out/opus_review_20261007")
    parser.add_argument("--only", choices=tuple(AUDIT_TASKS) + ("experiment", "manifest"))
    args = parser.parse_args()
    if args.only == "manifest":
        write_json(args.outdir / "manifest.json", manifest(args.outdir))
        return
    tasks = dict(AUDIT_TASKS)
    tasks["experiment"] = None
    for name in tasks:
        if args.only and name != args.only:
            continue
        start = time.perf_counter()
        if name == "experiment":
            from research.opus_review.keyword_tableau import experiment
            result = experiment(log=lambda msg: print(json.dumps({"experiment": "keyword_tableau",
                                                                  "stage": msg}), flush=True))
            path = args.outdir / "experiment/keyword_tableau.json"
        else:
            result = tasks[name]()
            path = args.outdir / f"audit/{name}.json"
        write_json(path, result)
        print(json.dumps({"task": name, "seconds": round(time.perf_counter() - start, 2),
                          "output": str(path.relative_to(ROOT))}), flush=True)


if __name__ == "__main__":
    main()
