"""Corpus-specific quadgram scores with intact positional windows."""
import hashlib
import math
from pathlib import Path

from .constants import ANCHORS, STD


def window_groups(length=97, anchors=ANCHORS):
    if length < 4 or any(type(i) is not int or not 0 <= i < length for i in anchors):
        raise ValueError("Invalid text length or anchor positions")
    groups = {"unknown_only": [], "boundary": [], "anchor_internal": [], "full": list(range(length - 3))}
    for start in groups["full"]:
        known = sum(i in anchors for i in range(start, start + 4))
        groups["anchor_internal" if known == 4 else "unknown_only" if known == 0 else "boundary"].append(start)
    return groups


class QuadgramScorer:
    """Load an explicit count corpus; no silent fallback or universal threshold.

    File lines are QUADGRAM POSITIVE_INTEGER_COUNT; comments start with #.
    Log10(count/total), unseen floor log10(0.01/total). Source bytes are hashed.
    These conventional fitness values are not calibrated plaintext probabilities.
    """
    def __init__(self, path):
        data = Path(path).read_bytes()
        counts = {}
        for line_number, line in enumerate(data.decode("utf-8").splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            if len(fields) != 2:
                raise ValueError(f"Invalid count line {line_number}")
            gram, value = fields
            if len(gram) != 4 or any(c not in STD for c in gram) or gram in counts:
                raise ValueError(f"Invalid or duplicate quadgram at line {line_number}")
            try:
                count = int(value)
            except ValueError as exc:
                raise ValueError(f"Invalid count at line {line_number}") from exc
            if count < 1:
                raise ValueError("Quadgram counts must be positive")
            counts[gram] = count
        if not counts:
            raise ValueError("Empty quadgram table")
        total = sum(counts.values())
        self.logp = {g: math.log10(n) - math.log10(total) for g, n in counts.items()}
        self.floor = math.log10(0.01) - math.log10(total)
        self.metadata = {"name": Path(path).name, "sha256": hashlib.sha256(data).hexdigest(),
                         "entries": len(counts), "total_count": total,
                         "formula": "log10(count/total); unseen log10(0.01/total)",
                         "calibration": "Requires matched controls for the complete search"}

    def score(self, plaintext, anchors=ANCHORS):
        if any(c not in STD for c in plaintext):
            raise ValueError("Only complete uppercase ASCII plaintexts may be scored")
        return {name: {"windows": len(starts),
                       "mean_log10": sum(self.logp.get(plaintext[i:i + 4], self.floor) for i in starts) / len(starts) if starts else None}
                for name, starts in window_groups(len(plaintext), anchors).items()}
