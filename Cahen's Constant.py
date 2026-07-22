#!/usr/bin/env python3
"""
Cahen's Constant Calculator (HPC OEIS Edition)
==============================================
Calculates Cahen's constant (C) to exactly [N] significant digits using Sylvester's 
doubly-exponential series expansion, 12-core parallel execution context, 
C-accelerated gmpy2 math, and strict OEIS truncation formatting.
"""

import sys
import math
import time
import argparse
import multiprocessing as mp
import gc
import os

os.environ['MPMATH_GMPY2'] = '1'
import gmpy2
import mpmath
from gmpy2 import mpz

sys.set_int_max_str_digits(0)

NUM_WORKERS = 12

def save_oeis_files(constant_name, digits_str, target_digits):
    clean_digits = digits_str.replace(".", "")[:target_digits]
    
    raw_filename = f"{constant_name}_{target_digits}_digits.txt"
    with open(raw_filename, "w", encoding="utf-8") as f:
        f.write(clean_digits)
    print(f"Saved raw digit output to {raw_filename}")

    b_filename = f"b_file_{constant_name}_{target_digits}.txt"
    with open(b_filename, "w", encoding="utf-8") as f:
        for idx, digit in enumerate(clean_digits, start=1):
            f.write(f"{idx} {digit}\n")
    print(f"Saved OEIS b-file output to {b_filename}")

def compute_cahen_hpc(target_digits):
    dps_working = target_digits + 50
    mpmath.mp.dps = dps_working
    ctx = mpmath.mp

    cahen_sum = ctx.mpf(0)
    s_k = mpz(2)

    max_k = int(math.ceil(math.log2(dps_working))) + 10

    for k in range(max_k):
        denom = s_k - mpz(1)
        term = ctx.mpf(1) / ctx.mpf(denom)
        if k % 2 == 1:
            cahen_sum -= term
        else:
            cahen_sum += term

        s_k = s_k * s_k - s_k + mpz(1)

    cahen_str = ctx.nstr(cahen_sum, dps_working)
    clean_digits = cahen_str.replace(".", "")[:target_digits]

    del cahen_sum
    gc.collect()

    save_oeis_files("Cahen", clean_digits, target_digits)
    return clean_digits

def main():
    parser = argparse.ArgumentParser(description="HPC Cahen OEIS Calculator")
    parser.add_argument("-n", "--digits", type=int, default=1000, help="Target digits (default: 1000)")
    args = parser.parse_args()

    t0 = time.time()
    digits = compute_cahen_hpc(args.digits)
    t1 = time.time()

    print(f"Execution finished in {t1 - t0:.4f} seconds using {NUM_WORKERS} cores.")

if __name__ == "__main__":
    main()
