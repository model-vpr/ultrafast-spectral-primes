# Copyright (c) 2026 Stefka Georgieva
# Licensed under CC BY-NC-ND 4.0
# Commercial use requires a separate license. 
# Contact: georgieva@vpr-research.eu; vpr.model@gmail.com

import numpy as np
from sympy import isprime
from tqdm import tqdm
import time
import math
from mpmath import mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import sys
sys.set_int_max_str_digits(20000)  # Increase limit (e.g., to 20,000 digits)
import gmpy2
from sympy import primerange

# Generate the first ~1000 primes (up to 20000)
# This takes microseconds and is done only once
SMALL_PRIMES_EXTENDED = list(primerange(7, 20000))

# Precision setup
mp.dps = 500

class SpectralPrimeConfig:
    def __init__(self):
        self.spectral_params = {
            'A': 11.379, 'B': 3.220, 'C': -0.0141,
            'D': 0.000053, 'E': -9e-8, 'F': 1e-10, 'A_log': 5.0
        }

def quinitic_with_log_law(x, A, B, C, D, E, F, A_log):
    poly_term = A + B*x + C*x**2 + D*x**3 + E*x**4 + F*x**5
    log_correction = A_log * np.log(x)
    return poly_term + log_correction

def spectral_law_relative(num_eigenvalues, spectral_params):
    n_indices = np.arange(1, num_eigenvalues + 1)
    levels = quinitic_with_log_law(n_indices, **spectral_params)
    levels = (levels - levels.min()) / (levels.max() - levels.min())
    return levels

# --- PARALLEL CHECK FUNCTION ---
def check_candidate_batch(candidate, search_offset, base_exponent):
    local_found = []
    start_num = candidate - search_offset
    end_num = candidate + search_offset

    current_6n = ((start_num + 5) // 6) * 6

    while current_6n - 1 <= end_num:
        for test in [current_6n - 1, current_6n + 1]:
            if start_num <= test <= end_num and test > 5:
                # 1. Fast division by 5
                if test % 5 == 0: continue

                # 2. Filter with extended prime list
                is_composite = False
                for p in SMALL_PRIMES_EXTENDED:
                    if test % p == 0:
                        is_composite = True
                        break
                if is_composite: continue

                # 3. HEAVY CHECK (only for ~10–15% survivors)
                if gmpy2.is_prime(gmpy2.mpz(test)):
                    local_found.append(test)

        current_6n += 6

    return local_found

def parallel_spectral_scan(base_exponent, num_points=8, start_index=0, num_eigenvalues=50, search_offset=10):
    """
    Parallel scan with sliding window capability.

    Args:
        start_index: Starting index of "hot" candidates (0 = beginning).
    """
    log_base = base_exponent * math.log(10)

    print(f"\n🚀 SCAN: 10^{base_exponent} | Window: {start_index} to {start_index + num_points}")
    start_time = time.time()

    # 1. Generate spectral levels
    config = SpectralPrimeConfig()
    spectral_levels = spectral_law_relative(num_eigenvalues, config.spectral_params)

    # 2. Find all points above 90th percentile
    threshold = np.percentile(spectral_levels, 90)
    hot_indices = np.where(spectral_levels > threshold)[0]

    # Sort indices by spectral strength (highest first)
    sorted_hot_indices = hot_indices[np.argsort(spectral_levels[hot_indices])][::-1]

    # 3. Select window
    target_indices = sorted_hot_indices[start_index : start_index + num_points]

    if len(target_indices) == 0:
        print("❌ No more hot points in this range!")
        return []

    # 4. Prepare candidate numbers
    tasks = []
    print(f"Preparing {len(target_indices)} candidates...")

    log_step = 1.0 / num_eigenvalues
    for idx in target_indices:
        lp = log_base + (idx * log_step)
        try:
            candidate = int(mp.exp(lp))
            tasks.append(candidate)
        except:
            continue

    # 5. Parallel execution
    primes_found = []
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(check_candidate_batch, c, search_offset, base_exponent): c for c in tasks}

        for future in tqdm(as_completed(futures), total=len(tasks), desc="Checking"):
            result = future.result()
            if result:
                primes_found.extend(result)

    primes_found = sorted(set(primes_found))

    # === NEW: automatic min / max report ===
    if primes_found:
        min_p = min(primes_found)
        max_p = max(primes_found)
        print(f"\n📊 SPECTRAL RESULT (b={base_exponent}, offset={search_offset:,})")
        print(f" Smallest prime → {min_p}")
        print(f" Largest prime → {max_p}")
        print(f" Delta → {max_p - search_offset}")
        print(f" First digit of max → {str(max_p)[0]}")

    elapsed = time.time() - start_time
    print(f"✅ Completed in {elapsed:.2f}s. Found: {len(primes_found)}")

    return primes_found

def save_primes(primes, exponent):
    if primes:
        filename = f"spectral_primes_10_{exponent}.txt"
        with open(filename, 'w') as f:
            f.write(f"Spectral Primes at 10^{exponent}\nTotal: {len(primes)}\n\n")
            for p in primes:
                f.write(f"{p}\n")
        print(f"Saved to: {filename}")

if __name__ == "__main__":
    # SESSION 1: first 8 best points
    primes_batch_1 = parallel_spectral_scan(
        base_exponent=309,
        num_points=8,
        start_index=0,  # start from the highest-ranked candidates
        search_offset=20000
    )

    save_primes(primes_batch_1, "40_part1")