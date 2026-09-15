#!/usr/bin/env python3
"""
Cahen's Constant Calculator (OEIS Edition)
==========================================
Calculates Cahen's constant C to exactly N significant digits using
Sylvester's doubly-exponential series expansion, C-accelerated gmpy2 math,
and strict OEIS truncation formatting.

Mathematics
-----------
C = sum_{k=0}^{inf} (-1)^k / (s_k - 1)

where s_0 = 2 and s_{k+1} = s_k^2 - s_k + 1 (Sylvester's sequence).
Consecutive denominators d_k = s_k - 1 satisfy d_{k+1} = s_k * d_k, so each
d_k divides all later ones. The partial series therefore collapses to a
single exact integer fraction with denominator D = d_m:

    C_m = ( sum_k (-1)^k * (D // d_k) ) / D

The whole series is summed in exact integer arithmetic — no rounding error
accumulates — and only ONE high-precision division is performed at the
end. Because the sequence grows doubly exponentially, only ~log2(N) terms
are needed for N digits.
"""

from __future__ import annotations

import argparse
import os
import time

os.environ.setdefault("MPMATH_GMPY2", "1")

import mpmath
from gmpy2 import mpz

GUARD_DIGITS = 50


def sylvester_denominators(working_digits: int) -> tuple[list[mpz], mpz]:
    """Generate Cahen series denominators d_k = s_k - 1 up to 10**working_digits.

    Sylvester's sequence: s_0 = 2, s_{k+1} = s_k**2 - s_k + 1.

    Returns:
        (collected_denominators, next_d) where next_d is the first
        denominator exceeding 10**working_digits. next_d is divisible by
        every collected denominator (d_{k+1} = s_k * d_k).
    """
    threshold = mpz(10) ** working_digits
    denoms: list[mpz] = []
    s = mpz(2)
    while (s - 1) <= threshold:
        denoms.append(s - 1)
        s = s * s - s + 1
    return denoms, s - 1


def cahen_series_fraction(working_digits: int) -> tuple[int, int]:
    """Return the Cahen series as an exact fraction (numerator, denominator).

    Uses the divisibility property of Sylvester denominators (d_k divides
    every later d_j) to express the alternating series as a single integer
    fraction. The omitted tail is bounded by 1/D < 10**-working_digits.
    """
    denoms, D = sylvester_denominators(working_digits)

    numerator = 0
    for k, d in enumerate(denoms):
        sign = -1 if k % 2 else 1
        numerator += sign * (D // d)
    return numerator, D


def compute_cahen(target_digits: int) -> str:
    """Compute the first `target_digits` digits of Cahen's constant.

    The digits are returned as a string with the decimal point removed and
    the leading integer-part zero retained (matching OEIS b-file convention).

    Args:
        target_digits: number of decimal digits to produce (>= 1).

    Returns:
        Digit string of length `target_digits`.

    Raises:
        ValueError: if target_digits is not a positive integer.
    """
    if target_digits < 1:
        raise ValueError("target_digits must be a positive integer")

    working = target_digits + GUARD_DIGITS
    numerator, denominator = cahen_series_fraction(working)

    mpmath.mp.dps = working
    value = mpmath.mpf(numerator) / mpmath.mpf(denominator)
    return mpmath.nstr(value, working).replace(".", "")[:target_digits]


def save_oeis_files(constant_name: str, digits_str: str, target_digits: int) -> None:
    """Write the raw digit string and an OEIS b-file to the current directory.

    Args:
        constant_name: name used in output filenames.
        digits_str: decimal digit string (leading integer-part digit included).
        target_digits: expected number of digits (extra digits are truncated).
    """
    clean_digits = digits_str.replace(".", "")[:target_digits]

    raw_filename = f"{constant_name}_{target_digits}_digits.txt"
    with open(raw_filename, "w", encoding="utf-8") as f:
        f.write(clean_digits)
    print(f"Saved raw digit output to {raw_filename}")

    b_filename = f"b_file_{constant_name}_{target_digits}.txt"
    with open(b_filename, "w", encoding="utf-8") as f:
        # writelines consumes the generator lazily — O(1) memory even for
        # millions of digits, unlike building the b-file in a list first.
        f.writelines(f"{idx} {digit}\n" for idx, digit in enumerate(clean_digits, start=1))
    print(f"Saved OEIS b-file output to {b_filename}")


def main() -> None:
    """Entry point: parse arguments, compute, and save OEIS output files."""
    parser = argparse.ArgumentParser(description="Cahen OEIS Calculator")
    parser.add_argument(
        "-n", "--digits", type=int, default=1000,
        help="Target digits (default: 1000)")
    args = parser.parse_args()

    if args.digits < 1:
        parser.error("--digits must be a positive integer")

    t0 = time.time()
    digits = compute_cahen(args.digits)
    t1 = time.time()

    save_oeis_files("Cahen", digits, args.digits)
    print(f"Execution finished in {t1 - t0:.4f} seconds.")


if __name__ == "__main__":
    main()
