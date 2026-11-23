"""Small reproducible command line interface; never contacts a verifier."""
import argparse
from datetime import datetime, timezone
import hashlib
from itertools import product
import json
from pathlib import Path
import shlex
import sys

from .constants import ALPHABETS, ANCHORS, FIT_ANCHORS, HOLDOUT_ANCHORS, K4_CIPHERTEXT
from .diagnostics import ciphertext_hash, crib_parity, matched_controls, width_bigrams
from .primitives import MODES, route_catalog, verify_baselines
from .scoring import QuadgramScorer, window_groups
from .solver import Model, clock_schedules, decrypt, fixed_key_matches, infer_key, search


def source_hash():
    root = Path(__file__).parent
    digest = hashlib.sha256()
    for path in sorted(root.iterdir()):
        if path.suffix in (".py", ".json"):
            digest.update(path.name.encode() + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def period_list(value):
    try:
        if ":" in value:
            a, b = map(int, value.split(":"))
            result = list(range(a, b + 1))
        else:
            result = list(dict.fromkeys(int(x) for x in value.split(",")))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use 1:30 or 24,27") from exc
    if not result or min(result) < 1 or max(result) > 97:
        raise argparse.ArgumentTypeError("Periods must be in 1..97")
    return result


def build_models(args):
    routes = [("identity", tuple(range(97)))] if args.routes == "identity" else list(route_catalog(max_column_width=args.max_column_width))
    alphabets = ALPHABETS if args.alphabet == "both" else {args.alphabet: ALPHABETS[args.alphabet]}
    modes = MODES if args.mode == "all" else [args.mode]
    orders = ("S_T", "T_S") if args.order == "both" else [args.order]
    # Identity has identical orders; Vigenere/variant-Beaufort equivalence is
    # documented, never interpreted as independent corroboration.
    seen = set()
    for (route, permutation), period, (name, alphabet), mode, order in product(routes, args.periods, alphabets.items(), modes, orders):
        effective_order = "S_T" if permutation == tuple(range(97)) else order
        signature = (permutation, period, alphabet, mode, effective_order)
        if signature not in seen:
            seen.add(signature)
            yield Model(f"{route}:{name}:{mode}:{effective_order}:p={period}", period, permutation, alphabet, mode, effective_order)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=("verify", "diagnostics", "search", "clock"))
    ap.add_argument("--output", type=Path)
    ap.add_argument("--periods", type=period_list, default=period_list("1:30"))
    ap.add_argument("--alphabet", choices=("STD", "KRYPTOS", "both"), default="both")
    ap.add_argument("--mode", choices=(*MODES, "all"), default="all")
    ap.add_argument("--order", choices=("S_T", "T_S", "both"), default="both")
    ap.add_argument("--routes", choices=("identity", "grids"), default="identity")
    ap.add_argument("--max-column-width", type=int, choices=range(1, 8), default=3)
    ap.add_argument("--quadgrams", type=Path)
    ap.add_argument("--max-per-model", type=int, default=100000)
    ap.add_argument("--max-total", type=int, default=500000)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--controls", type=int, default=0, help="Search controls per null family; requires a quadgram table")
    ap.add_argument("--seed", type=int, default=20261123)
    ap.add_argument("--evaluation-holdout", action="store_true", help="Fit EASTNORTHEAST only; report BERLINCLOCK afterward")
    args = ap.parse_args(argv)
    if min(args.max_per_model, args.max_total, args.controls) < 0 or args.top < 1:
        ap.error("Budgets must be nonnegative and --top positive")
    if args.controls and (args.command != "search" or not args.quadgrams):
        ap.error("--controls requires search and --quadgrams")
    if args.evaluation_holdout and args.command != "search":
        ap.error("--evaluation-holdout applies to search only")
    baselines = verify_baselines()
    if not all(baselines.values()):
        raise RuntimeError(f"Baseline known-answer failure: {baselines}")
    scorer = QuadgramScorer(args.quadgrams) if args.quadgrams else None
    if args.command == "verify":
        result = baselines
    elif args.command == "diagnostics":
        models = list(build_models(args))
        compatible = [{"model": m.name, **infer_key(K4_CIPHERTEXT, m)} for m in models
                      if infer_key(K4_CIPHERTEXT, m)["compatible"]]
        result = {"baselines": baselines, "parity": crib_parity(), "width21": width_bigrams(),
                  "quadgram_windows": {k: len(v) for k, v in window_groups().items()},
                  "models_checked": len(models), "compatible_models": compatible,
                  "scope": "Specified alphabets, routes, modes and periods only; no plaintext inference"}
    elif args.command == "clock":
        args.periods = [24]
        models, schedules = list(build_models(args)), list(clock_schedules())
        hits = []
        for model, (name, key) in product(models, schedules):
            if fixed_key_matches(K4_CIPHERTEXT, model, key):
                hits.append({"model": model.name, "schedule": name, "key": key,
                             "plaintext": decrypt(K4_CIPHERTEXT, key, model), "is_solution": False})
        result = {"models": len(models), "distinct_schedules": len(schedules),
                  "configurations": len(models) * len(schedules), "hits": hits,
                  "scope": "Three numeric facet hypotheses, all phases/directions/signs; no city names or historical clock reconstruction"}
    else:
        models = list(build_models(args))
        options = {"max_per_model": args.max_per_model, "max_total": args.max_total, "top": args.top,
                   "fit_anchors": FIT_ANCHORS if args.evaluation_holdout else ANCHORS,
                   "holdout_anchors": HOLDOUT_ANCHORS if args.evaluation_holdout else None}
        result = (matched_controls(K4_CIPHERTEXT, models, scorer, repetitions=args.controls, seed=args.seed, **options)
                  if args.controls else search(K4_CIPHERTEXT, models, scorer, **options))
    parameters = {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items() if k != "output"}
    # Published provenance records corpus identity, not a machine-specific path.
    if args.quadgrams:
        parameters["quadgrams"] = scorer.metadata
    report = {"schema_version": 1, "id": "k4-" + args.command,
              "recorded_at": datetime.now(timezone.utc).isoformat(),
              "command": "python -m kryptos " + shlex.join(argv),
              "code_sha256": source_hash(), "ciphertext_sha256": ciphertext_hash(K4_CIPHERTEXT),
              "parameters": parameters, "result": result, "is_solution": False}
    payload = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(json.dumps({"output": str(args.output), "command": args.command, "is_solution": False}))
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
