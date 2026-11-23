"""Replay repository export phases and the five period-24 collision witnesses.

This inspects the explicitly named GitHub files, not similarly named project
uploads. It validates stored plaintext/key consistency, not English or a solution.
"""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path

from kryptos.constants import ALPHABETS, ANCHORS, K4_CIPHERTEXT, STD
from kryptos.primitives import MODES, implied_shift

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = (
    "k4_top10_summary.json", "k4_top100_candidates_light.csv",
    "kryptos_k4_top50_period27.csv",
    "kryptos_k4_top100_period27_quadgram_composite.csv",
    "Top_5_K4_candidates_with_highlighted_phrases.csv",
    "data/exports/k4_top10_summary.json",
    "data/exports/k4_top100_candidates_light.csv",
)


def classify_row(raw, ciphertext=K4_CIPHERTEXT):
    row = {k.lower(): v for k, v in raw.items()}
    plain = row.get("plaintext", row.get("plaintext_highlighted"))
    key = row.get("keystream_27")
    result = {"plaintext_length": len(plain) if isinstance(plain, str) else None,
              "key_length": len(key) if isinstance(key, str) else None,
              "matching_phases": []}
    if not isinstance(plain, str) or not isinstance(key, str) or not plain or not key:
        return {**result, "status": "missing_plaintext_or_key"}
    if len(plain) != len(ciphertext) or len(key) != 27 or set(plain + key) - set(STD):
        return {**result, "status": "invalid_length_or_characters"}
    for phase in range(27):
        recovered = "".join(STD[(STD.index(c) - STD.index(key[(i + phase) % 27])) % 26]
                            for i, c in enumerate(ciphertext))
        if recovered == plain:
            result["matching_phases"].append(phase)
    phases = result["matching_phases"]
    return {**result, "status": "exact_phase0" if 0 in phases else
            "requires_unrecorded_phase" if phases else "does_not_reproduce"}


def export_audit(root=ROOT):
    results = []
    for name in EXPORTS:
        data = (root / name).read_bytes()
        text = data.decode("utf-8")
        rows = json.loads(text) if name.endswith(".json") else list(csv.DictReader(io.StringIO(text)))
        details = [{"row": i, **classify_row(row)} for i, row in enumerate(rows, 1)]
        results.append({"file": name, "sha256": hashlib.sha256(data).hexdigest(),
                        "rows": len(rows), "classifications": dict(Counter(r["status"] for r in details)),
                        "matching_phase_counts": dict(Counter(str(r["matching_phases"]) for r in details)),
                        "row_results": details})
    return results


def period24_witnesses():
    results = []
    for name, alphabet in ALPHABETS.items():
        for mode in MODES:
            pairs = []
            for first in range(21, 26):
                second = first + 48
                values = [implied_shift(alphabet.index(ANCHORS[i]), alphabet.index(K4_CIPHERTEXT[i]), mode)
                          for i in (first, second)]
                pairs.append({"positions_1_based": [first + 1, second + 1],
                              "required_numeric_shifts": values,
                              "same_residue_mod_24": first % 24 == second % 24,
                              "conflict": values[0] != values[1]})
            results.append({"alphabet": name, "mode": mode, "pairs": pairs})
    return results


def run_audit(root=ROOT):
    files = export_audit(root)
    duplicates = ["out/astra_20261007/feedback.json", "out/opus_review_20261007/reproduction/feedback.json"]
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in duplicates}
    return {"script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "scope": "Only named repository exports; no other uploaded versions. Historical scores not validated.",
            "phase_convention": "P[i] = STD[(STD.index(C[i]) - STD.index(key[(i + phase) % 27])) % 26]",
            "files": files,
            "summary": {"rows": sum(f["rows"] for f in files),
                        "phase_26_rows": sum(f["matching_phase_counts"].get("[26]", 0) for f in files),
                        "phase_0_rows": sum(f["matching_phase_counts"].get("[0]", 0) for f in files),
                        "invalid_or_incomplete_rows": sum(f["classifications"].get(s, 0) for f in files
                                                          for s in ("missing_plaintext_or_key", "invalid_length_or_characters"))},
            "period24_witnesses": period24_witnesses(),
            "duplicated_reproduction_artifacts": {"sha256": hashes, "byte_identical": len(set(hashes.values())) == 1,
                                                 "purpose": "Retained original and independent-reproduction records; not additional independent search evidence"},
            "is_solution": False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=ROOT / "out/local/review_checks.json")
    args = ap.parse_args()
    result = run_audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), **result["summary"]}))


if __name__ == "__main__":
    main()
