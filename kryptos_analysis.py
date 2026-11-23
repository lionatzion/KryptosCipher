"""Compatibility entry point for the verified workbench (pip install -e .)."""
from kryptos.cli import main
from kryptos.constants import K1_CIPHERTEXT, K2_CIPHERTEXT, K3_CIPHERTEXT, K4_CIPHERTEXT
from kryptos.primitives import decode_k1, decode_k2, decode_k3

if __name__ == "__main__":
    main()
