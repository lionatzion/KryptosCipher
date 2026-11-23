"""Finite anchor-constrained searches with explicit enumeration budgets."""
from dataclasses import asdict, dataclass
from itertools import islice, product

from .constants import ANCHORS, STD
from .primitives import implied_shift, inverse_permutation, transform, transpose, validate_alphabet


@dataclass(frozen=True)
class Model:
    name: str
    period: int
    permutation: tuple
    alphabet: str = STD
    mode: str = "vigenere"
    order: str = "S_T"

    def __post_init__(self):
        if type(self.period) is not int or self.period < 1:
            raise ValueError("Period must be a positive integer")
        if self.order not in ("S_T", "T_S"):
            raise ValueError("Order must be S_T or T_S")
        validate_alphabet(self.alphabet)
        inverse_permutation(self.permutation)
        implied_shift(0, 0, self.mode)


def encrypt(plaintext, key, model):
    if len(key) != model.period:
        raise ValueError("Key length differs from model period")
    if model.order == "S_T":
        return transpose(transform(plaintext, key, model.alphabet, model.mode), model.permutation)
    return transform(transpose(plaintext, model.permutation), key, model.alphabet, model.mode)


def decrypt(ciphertext, key, model):
    if len(key) != model.period:
        raise ValueError("Key length differs from model period")
    inverse = inverse_permutation(model.permutation)
    if model.order == "S_T":
        return transform(transpose(ciphertext, inverse), key, model.alphabet, model.mode, True)
    return transpose(transform(ciphertext, key, model.alphabet, model.mode, True), inverse)


def infer_key(ciphertext, model, anchors=ANCHORS):
    """Prune with O(number of anchors) work after building the inverse route.

    Gather definition: T(x)[j] = x[permutation[j]]. Anchor i pairs with C[inv[i]].
    S_T key residue is i % p; T_S residue is inv[i] % p. Collisions annotate
    evidence strength only. A consistent zero-collision fit is retained.
    """
    if len(ciphertext) != len(model.permutation) or any(c not in STD for c in ciphertext):
        raise ValueError("Ciphertext and route must have matching uppercase-letter lengths")
    if any(type(i) is not int or not 0 <= i < len(ciphertext) or p not in STD or len(p) != 1
           for i, p in anchors.items()):
        raise ValueError("Invalid anchor")
    inverse = inverse_permutation(model.permutation)
    key = [None] * model.period
    conflicts = []
    used = set()
    for i, p in sorted(anchors.items()):
        j = inverse[i]
        r = (i if model.order == "S_T" else j) % model.period
        used.add(r)
        required = implied_shift(model.alphabet.index(p), model.alphabet.index(ciphertext[j]), model.mode)
        if key[r] is not None and key[r] != required:
            conflicts.append({"plaintext_position_0": i, "residue": r,
                              "previous_shift": key[r], "required_shift": required})
        else:
            key[r] = required
    free = [i for i, k in enumerate(key) if k is None]
    return {"compatible": not conflicts, "key": key, "free_residues": free,
            "completion_count": 26 ** len(free), "distinct_anchor_residues": len(used),
            "consistency_checks": len(anchors) - len(used), "conflicts": conflicts}


def completions(partial_key, limit):
    if type(limit) is not int or limit < 0:
        raise ValueError("Completion limit must be nonnegative")
    free = [i for i, k in enumerate(partial_key) if k is None]
    for fill in islice(product(range(26), repeat=len(free)), limit):
        key = list(partial_key)
        for i, k in zip(free, fill):
            key[i] = k
        yield tuple(key)


def search(ciphertext, models, scorer=None, *, fit_anchors=ANCHORS, holdout_anchors=None,
           max_per_model=100000, max_total=500000, top=10):
    """Rank only complete enumerated keys. Never manufacture a single unknown fill.

    Models are visited in input order and completions lexicographically. A cap
    produces incomplete evidence, never an elimination. Holdout letters neither
    infer keys nor filter rankings; their exact match count is reported afterward.
    """
    if min(max_per_model, max_total) < 0 or top < 1:
        raise ValueError("Invalid search budget")
    holdout_anchors = holdout_anchors or {}
    if set(fit_anchors) & set(holdout_anchors):
        raise ValueError("Fit and evaluation holdout positions must be disjoint")
    score_mask = dict(fit_anchors) | dict(holdout_anchors)
    evaluations, rows, candidates = 0, [], []
    best_score = None
    compatible = 0
    for model in models:
        fit = infer_key(ciphertext, model, fit_anchors)
        # Validate holdout positions even when the model is inconsistent.
        if holdout_anchors:
            infer_key(ciphertext, model, holdout_anchors)
        row = {"model": asdict(model), **fit, "evaluated_completions": 0,
               "completion_search_complete": not fit["compatible"]}
        if fit["compatible"]:
            compatible += 1
            budget = min(fit["completion_count"], max_per_model, max_total - evaluations)
            for key in completions(fit["key"], budget):
                plaintext = decrypt(ciphertext, key, model)
                if any(plaintext[i] != p for i, p in fit_anchors.items()):
                    raise RuntimeError("Internal anchor propagation failure")
                if encrypt(plaintext, key, model) != ciphertext:
                    raise RuntimeError("Internal round-trip failure")
                scores = scorer.score(plaintext, score_mask) if scorer else None
                rank = scores["unknown_only"]["mean_log10"] if scores else None
                candidate = {"model": model.name, "key": key, "plaintext": plaintext,
                             "scores": scores, "holdout_matches": sum(plaintext[i] == p for i, p in holdout_anchors.items()),
                             "holdout_total": len(holdout_anchors), "roundtrip_exact": True,
                             "is_solution": False}
                # Bound stored output while retaining the global maximum.
                if len(candidates) < top or (rank is not None and rank > candidates[-1][0]):
                    candidates.append((rank if rank is not None else float("-inf"), candidate))
                    candidates.sort(key=lambda x: x[0], reverse=True)
                    del candidates[top:]
                if rank is not None and (best_score is None or rank > best_score):
                    best_score = rank
                evaluations += 1
                row["evaluated_completions"] += 1
            row["completion_search_complete"] = budget == fit["completion_count"]
        rows.append(row)
    return {"models_tested": len(rows), "compatible_models": compatible,
            "evaluated_completions": evaluations,
            "complete": all(r["completion_search_complete"] for r in rows),
            "best_unknown_only_score": best_score, "model_results": rows,
            "candidates": [c for _, c in candidates],
            "ranking": "unknown_only mean_log10" if scorer else "unscored, enumeration order only",
            "scorer": scorer.metadata if scorer else None,
            "budgets": {"max_per_model": max_per_model, "max_total": max_total, "top": top},
            "fit_positions": sorted(fit_anchors), "holdout_positions": sorted(holdout_anchors),
            "holdout_caveat": "Evaluation holdout only; both public cribs influenced prior research"}


def clock_schedules():
    """Three numeric 24-facet hypotheses, not historical city-ring reconstructions.

    UTC values, phase, direction and sign are explicit model choices. Deduplication
    prevents counting identical shift sequences as independent evidence.
    """
    bases = {"hours0": tuple(range(24)), "hours1": tuple(range(1, 25)),
             "signed_utc": tuple(h % 26 for h in range(-11, 13))}
    seen = set()
    for name, base in bases.items():
        for phase, direction, sign in product(range(24), (1, -1), (1, -1)):
            key = tuple(sign * base[(phase + direction * i) % 24] % 26 for i in range(24))
            if key not in seen:
                seen.add(key)
                yield f"{name}:phase={phase}:direction={direction}:sign={sign}", key


def fixed_key_matches(ciphertext, model, key, anchors=ANCHORS):
    """Check an independently specified key without fitting any of its values."""
    if len(key) != model.period or any(type(k) is not int or not 0 <= k < 26 for k in key):
        raise ValueError("Invalid fixed key")
    fit = infer_key(ciphertext, model, anchors)
    return fit["compatible"] and all(k is None or k == key[i] for i, k in enumerate(fit["key"]))
