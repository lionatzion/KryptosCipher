"""Canonical transcriptions; code indices are zero based."""
import json
from importlib.resources import files

STD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ALPHABETS = {"STD": STD, "KRYPTOS": KRYPTOS}
FIXTURES = json.loads(files(__package__).joinpath("fixtures.json").read_text())
K1_CIPHERTEXT = FIXTURES["K1_CIPHERTEXT"]
K2_CIPHERTEXT = FIXTURES["K2_CIPHERTEXT"]
K3_CIPHERTEXT = FIXTURES["K3_CIPHERTEXT"]
K4_CIPHERTEXT = FIXTURES["K4_CIPHERTEXT"]
ANCHORS = dict(zip(range(21, 34), "EASTNORTHEAST")) | dict(zip(range(63, 74), "BERLINCLOCK"))
FIT_ANCHORS = {i: p for i, p in ANCHORS.items() if i < 34}
HOLDOUT_ANCHORS = {i: p for i, p in ANCHORS.items() if i >= 63}
