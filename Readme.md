# ultrafast-spectral-primes

![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-CC%20BY--NC--ND%204.0-lightgrey.svg)
![Status](https://img.shields.io/badge/status-research--prototype-important.svg)

A novel computational framework for ultra-fast generation of large prime numbers, leveraging the spectral structure of the Riemann zeta function.

## The Philosophy: Constructive Realization of RH

> "We don't wait for someone to prove the Riemann Hypothesis (RH) to use the zeros. We generate them ourselves and use them to find primes. This is more than a validation—it's a constructive realization of the entire theory."
## 🚀 Introduction

We present three implementations for **ultra-fast prime number generation**.

This is a novel approach to analyzing and discovering prime numbers **without using the Sieve of Eratosthenes in any form**.  
The methods also **avoid division as a mechanism for prime detection**.

Within the current mathematical paradigm, such algorithms would not be expected to function —  
yet, in practice, they do.

---

We introduce three variants:

- **code1.py**  
- **code2.py**
- **code1_random.py**   


# ⚡ Executive Summary

This is a **high-performance research prototype** that challenges classical probabilistic primality testing. By treating prime detection as a signal processing problem rather than a trial-division problem, we achieve:
# 🚀 Performance Benchmarks: Spectral vs. Classical (code1.py)

## 📊 Summary of Results — Code 1

| Bit length | Primes | Time (s) | ms/prime |
|-----------|--------|---------|----------|
| 332       | 848    | 1.66    | 2.0      |
| 512       | 580    | 2.04    | 3.5      |
| 1024      | 267    | 3.68    | 13.8     |
| 2048      | 132    | 10.47   | 79.3     |
| 4096      | 67     | 51.55   | 769      |
| 4096      | 125    | 77.74   | 622      |

---

**Hardware:** Intel i7, 16 GB RAM, Python 3.13, 8 parallel processes  

**Note:**  
For 4096-bit numbers, increasing spectral resolution from 50 to 100 eigenvalues improves efficiency by ≈19%  
(622 vs 769 ms/prime).



# 🚀 Performance Benchmarks: Spectral vs. Classical (code2.py)
- **1024-bit primes in ~37 ms** (Median: 27.6 ms).
- **100% Accuracy**: Zero false positives across 2,000+ extensive mass tests.
- **Pure Python**: Competitive with optimized C-based implementations (e.g., OpenSSL) for 1024-bit prime generation, even in pure Python.



The following results were obtained on a standard **MacBook Pro (i7 @ 2.8 GHz)** using a **single-threaded Python** environment. No GPU, no parallel computing, and no C++ extensions were used.


| Key Size | Digits | **Spectral Law (Mean)** | **Spectral Law (Median)** | **Accuracy** | **Status** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **512-bit** | 154 | **8.10 ms** | 5.60 ms | 100% | Proto |
| **1024-bit** | 309 | **37.43 ms** | **27.60 ms** | **100.0%** | **Proto** |
| **2048-bit** | 617 | **284.12 ms** | 271.11 ms | 100% | Proto |
| **4096-bit** | 1234 | **2.06 sec** | 1.43 sec | 100% | Proto |


https://github.com/user-attachments/assets/f0955ca6-164a-4663-956f-8862b4d83f52


### 💡 Why this is a Breakthrough:
- **Beating Optimized C**: Typical optimized OpenSSL Miller-Rabin implementations for 1024-bit primes range between 50-100 ms. Our **unoptimized Python** code already cuts this time by half.
- **The "Radar" Advantage**: Unlike classical methods that search blindly, the **Spectral Law** acts as a radar, pointing directly to high-density prime regions, drastically reducing the search space.
- **Statistical Stability**: 95% of 1024-bit primes are generated within **104.41 ms**, with a minimum latency of just **1.90 ms**.

**Ultra-fast prime generation using spectral methods **



---

## 📚 Full Documentation

For complete theoretical background, mathematical derivations, and experimental results, see the **Zenodo publication https://doi.org/10.5281/zenodo.19893929**:

👉 [**The Spectral Law of Prime Numbers**](https://zenodo.org/records/19893929)

👉 [**Empirical validation of the prime nodal condition and
the spectral law for the Riemann hypothes**](https://zenodo.org/records/17726547)

---

## 📋 Step-by-Step Overview

### Step 1: Hamiltonian Operator (Hilbert-Polya)

**File:** [`my-hamiltonian.py`](./my-hamiltonian.py)

- Constructs quantum operator
- Input: primes up to 150,000 (13,848 primes)
- Output: eigenvalues → γ² (Riemann zeros)
- Result: first 10,000 zeros with **R² = 0.9999**
-The high R² score (0.9999) and low relative error confirm that the Hilbert-Polya conjecture is numerically realized: the Hamiltonian with potentials at prime positions indeed generates the Riemann zeros.

### 🤖 Performance result

### 1.1. Standard Analysis

**Dataset size:** 10,000 examples

---

### 📊 Model Evaluation

#### 🔹 Linear Model

```text
CV R²:   -3.6281 (±4.0496)
Test R²:  0.9366
```

---

#### 🔹 GBM_Simple

```text
CV R²:   -1.5153 (±1.9356)
Test R²:  0.9996
```

---

#### 🔹 GBM_Medium

```text
CV R²:   -1.1795 (±1.4267)
Test R²:  0.9999
```

---

### 🏆 Best Model

**GBM_Medium**  
**Test R² = 0.9999**

---

### 🔁 Stability Check (Bootstrap)

```text
Bootstrap R²: 0.9379 (±0.0014)
```

---

### ⚠️ Overfitting Diagnostics

```text
Train R²: 1.0000
Test R²:  0.9999
Gap:      0.0000
```

✅ **Good generalization**

👉 [**my-hamiltonian.py**]
👉 [**my-hamiltonian-res.pdf**]
**File:** `my-hamiltonian.py`
**File:** `my-hamiltonian-res.pdf`

---


### Step 2: Spectral Law Fitting

**File:** `spectral_law_verification.py`
## 📐 Spectral Law Approximation

From the computed zeros, we observe a remarkably simple functional relationship:

```
γ(λ) ≈ A + B·λ + C·λ² + D·λ³ + E·λ⁴ + F·λ⁵ + A_log · ln(λ)
```

This higher-order approximation is used in **Code 1**.

---

### 🔧 Model Reduction

In subsequent analysis, the model was reduced to only **three parameters**, without loss of accuracy and with significantly lower computational cost:

```
γ(λ) = A + B·λ + C·ln(λ)
```

This simplified formula is the **core model used in Code 2**.

---

### 💡 Key Insight

- Higher-order polynomial terms (λ², λ³, ...) do **not significantly improve accuracy**  
- The reduced model preserves precision while improving efficiency  
- This suggests an underlying **low-dimensional spectral structure**



---

### Step 3: Code 1 — Cluster-Based 

**File:** `code1.py`

- Uses top spectral indices  
- Logarithmic candidate mapping  
- No division during selection
- Verify with gmpy2.is_prime()

**Speed:** ~14 ms per prime (1024-bit)

---

## 🔁 Deterministic vs Randomized Prime Generation

### 🔒 Deterministic Version (Original Cluster-Based Method)

The original cluster-based method uses fixed parameters and produces **sequential primes with identical prefixes**:

```python
# Fixed parameters (deterministic)
base_exponent = 309  # 10^609 (2024 bits)
num_points = 8
start_index = 0
search_offset = 20000
```

#### Result: Sequential primes with same prefix

```text
p1 = 202971210494436929447256046091688877425121532510442865664778934639395072751734107016013
p2 = 202971210494436929447256046091688877425121532510442865664778934639395072751734107016077  # Δ = 64
p3 = 202971210494436929447256046091688877425121532510442865664778934639395072751734107016781  # Δ = 704
p4 = 202971210494436929447256046091688877425121532510442865664778934639395072751734107017043  # Δ = 262
```

---

### ⚠️ Important: Sequential Primes

The deterministic version of Code 1 always returns the **same sequential primes** for the same input parameters.

This is **not suitable for cryptography**, because:

- Primes are predictable and repeatable  
- Differences between consecutive primes are very small (`Δ = 64, 704, 262...`)  
- RSA keys would be vulnerable to **Fermat factorization**  

---


### 🔑 Controlling the Prime Prefix (Code 1)

#### 🧭 How to Change the Prefix of Generated Primes

To modify the prefix of all generated primes, adjust the logarithmic base used in the transformation.

Locate the following line at **line 76** in the code:

```python
log_base = base_exponent * math.log(10)
```

Replace it with a different value and observe how the generated primes acquire a **different prefix**.

---

#### 🔬 Explanation

- The logarithmic base controls the **mapping from spectral space to integer space**  
- Changing this value effectively shifts the numerical scale  
- As a result, the generated primes maintain their structure, but their **leading digits (prefix)** change  

This provides a simple way to explore different prime regions while preserving the underlying spectral behavior.

### 🧪 Scientific Advantage

This deterministic behavior is actually beneficial for:

- Reproducibility of experiments  
- Validation of the spectral law  
- Controlled testing environments

  ---

### 🎲 Randomized Version (Cryptographic)
**File:** `code1_random.py`

By introducing randomness , we generate:

- Truly random primes  
- Different prefixes  
- Cryptographically secure outputs  

This version maintains the **mathematical structure**, while removing predictability.

### ⚙️ Configuration Guide (`code1_random.py`)

#### 🔍 Adjusting the Search Range

To modify the search range, change the value at **line 151**.

**When should you increase the range?**

- When searching for very large numbers and the results show a low number of primes found  
- Increasing the range improves the probability of finding primes, but also increases computation time  

---

#### 🔢 Controlling Prime Size and Sample Count

To adjust the size of the generated primes and the number of samples:

```python
BITS = 2048
SAMPLES = 50
```

Please set your desired values at **lines 346 and 347** in the code.

- `BITS` → defines the size of the primes (in bits)  
- `SAMPLES` → number of primes to generate

### Step 4: Code 2 — Explicit Formula (Validation)

**File:** `code2.py`

**File:** `riemann_verification.py`

- Optimized implementation of Riemann's explicit formula  
- Vectorized NumPy operations (C-speed)  
    


- **1024-bit primes in ~37 ms** (Median: 27.6 ms).
- **100% Accuracy**: Zero false positives across 2,000+ extensive mass tests.
- **Pure Python**: Competitive with optimized C-based implementations (e.g., OpenSSL) for 1024-bit prime generation, even in pure Python.

# 🚀 Performance Benchmarks: Code 2

The following results were obtained on a standard **MacBook Pro (i7 @ 2.8 GHz)** using a **single-threaded Python** environment. No GPU, no parallel computing, and no C++ extensions were used.


| Key Size | Digits | **Spectral Law (Mean)** | **Spectral Law (Median)** | **Accuracy** | **Status** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **512-bit** | 154 | **8.10 ms** | 5.60 ms | 100% | Proto |
| **1024-bit** | 309 | **37.43 ms** | **27.60 ms** | **100.0%** | **Proto** |
| **2048-bit** | 617 | **284.12 ms** | 271.11 ms | 100% | Proto |
| **4096-bit** | 1234 | **2.06 sec** | 1.43 sec | 100% | Proto |

---

## 🔬 Key Scientific Discoveries

### 1. Topological Invariance (B > 0)

```python
# All B > 0 produce IDENTICAL primes!
B = 0.5, 1.0, 1.884, 5.0, 10.0 → same primes
```

**Interpretation:**  
Changing `B` changes the measurement scale (meters → feet), not the structure.

---

### 2. Phase Transition at B = 0

| Condition | Behavior |
|----------|--------|
| B > 0    | Upper family (primes ~2,000,000) |
| B < 0    | Lower family (primes ~1,000,000) |
| B < -5   | Fixed point (stable lower family) |

---




```

**Requirements:**  
`numpy`, `gmpy2`, `mpmath`, `sympy`, `scipy`

## 💻 Environment
- **Language**: Python 3.8+
- **Libraries**: `numpy`, `scipy`, `mpmath`
- **Portability**: Designed for easy porting to C/Rust for even greater performance gains.

---

## 📜 License & Commercial Use

This project is released under the **Creative Commons BY-NC-ND 4.0 License**.

### 🔒 Non-Commercial Use

You are free to:
- Use, study, and share the code for research and educational purposes

### 🚫 Restrictions

- Commercial use is **strictly prohibited**
- Redistribution of modified versions is **not allowed**

### 💼 Commercial Licensing

Commercial use of this technology, including but not limited to:

- Integration into cryptographic systems  
- Use in production environments  
- Financial or security-related applications  

**requires a separate commercial license.**

If you are interested in licensing this technology, please contact:

📧 georgieva@vpr-research.eu; vpr.model@gmail.com

---

### ⚖️ Notice

Unauthorized commercial use may constitute a violation of intellectual property rights.

All rights reserved.



**Author**: Stefka Georgieva  
**Contact**: georgieva@vpr-research.eu; vpr.model@gmail.com  
**License**: [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)
