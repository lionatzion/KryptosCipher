"""Observed statistics and matched full-search random controls."""
from collections import Counter, defaultdict
from itertools import combinations
import hashlib
import random

from .constants import ANCHORS, K4_CIPHERTEXT, STD
from .solver import search


def ciphertext_hash(text):
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def crib_parity(ciphertext=K4_CIPHERTEXT):
    groups = defaultdict(list)
    for i, p in ANCHORS.items():
        groups[p].append((i + 1 + STD.index(ciphertext[i])) % 2)
    return {"groups": {p: sorted(set(v)) for p, v in sorted(groups.items())},
            "pair_matches": sum(a == b for v in groups.values() for a, b in combinations(v, 2)),
            "pair_count": sum(len(v) * (len(v) - 1) // 2 for v in groups.values()),
            "independent_equalities": sum(len(v) - 1 for v in groups.values()),
            "scope": "Repeated plaintext letter parity, not proof of globally alternating key parity"}


def width_bigrams(ciphertext=K4_CIPHERTEXT, width=21):
    if not 1 <= width < len(ciphertext):
        raise ValueError("Width must be inside ciphertext bounds")
    counts = Counter(ciphertext[i] + ciphertext[i + width] for i in range(len(ciphertext) - width))
    return {"width": width, "bigrams": len(ciphertext) - width,
            "repeated_types": sorted(g for g, n in counts.items() if n > 1),
            "duplicate_excess": sum(n - 1 for n in counts.values()),
            "scope": "Descriptive statistic; width selection must enter any significance calibration"}


def matched_controls(ciphertext, models, scorer, *, repetitions, seed, **search_options):
    """Repeat the exact fitting, completion, ranking and budget policy on each null.

    Record controls with no candidate as score=None (below any finite maximum).
    No comparison of a searched K4 maximum to individual random strings.
    Empirical ranks are conditional diagnostics, not discovery p-values.
    """
    if repetitions < 1:
        raise ValueError("At least one control per family is required")
    models = tuple(models)
    observed = search(ciphertext, models, scorer, **search_options)
    rng = random.Random(seed)
    controls = []
    for kind in ("histogram_shuffle", "uniform"):
        for trial in range(repetitions):
            if kind == "histogram_shuffle":
                letters = list(ciphertext)
                rng.shuffle(letters)
                text = "".join(letters)
            else:
                text = "".join(rng.choice(STD) for _ in ciphertext)
            result = search(text, models, scorer, **search_options)
            controls.append({"kind": kind, "trial": trial, "ciphertext": text,
                             "ciphertext_sha256": ciphertext_hash(text),
                             **{k: result[k] for k in ("best_unknown_only_score", "complete", "models_tested",
                                                      "compatible_models", "evaluated_completions")}})
    score = observed["best_unknown_only_score"]
    ranks = {}
    if score is not None:
        for kind in ("histogram_shuffle", "uniform"):
            exceed = sum(c["best_unknown_only_score"] is not None and c["best_unknown_only_score"] >= score
                         for c in controls if c["kind"] == kind)
            ranks[kind] = {"at_least_observed": exceed, "trials": repetitions,
                           "add_one_upper_tail_rank": (exceed + 1) / (repetitions + 1)}
    return {"observed": observed, "controls": controls, "seed": seed, "ranks": ranks,
            "scope": "Matched registered finite pipeline; does not correct earlier hypothesis selection",
            "all_searches_complete": observed["complete"] and all(c["complete"] for c in controls)}
