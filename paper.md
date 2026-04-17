---
title: 'SpectralPrimes: A High-Performance Prime Number Generator Based on Riemann Zeta Zeros'
tags:
  - Python
  - Number Theory
  - Riemann Hypothesis
  - Spectral Analysis
  - Cryptography
authors:
  - name: Stefka Georgieva
    orcid: https://orcid.org/0009-0005-9158-0016
    affiliation: Independent Researcher
date: 17 April 2026
bibliography: paper.bib
---

# Summary

`SpectralPrimes` is a Python-based computational tool designed for the ultra-fast generation of large prime numbers. Unlike traditional probabilistic primality tests (e.g., Miller-Rabin), this software leverages the spectral distribution of the non-trivial zeros of the Riemann zeta function. By applying a "Spectral Law" derived from the Hilbert-Pólya conjecture, the algorithm identifies high-probability candidates for primality with significantly reduced computational overhead.

This implementation is based on the theoretical framework established in @SpectralPrimesTheory2026 and further validated through numerical analysis in @EmpiricalValidation2026.

# Statement of Need

The generation of large prime numbers is a cornerstone of modern asymmetric cryptography, particularly for RSA-based systems. As cryptographic requirements shift towards larger key sizes, the demand for more efficient generation algorithms increases. 

`SpectralPrimes` fills a gap in existing mathematical software by providing an implementation that bridges analytical number theory and practical computational efficiency. It is intended for use by researchers in number theory and developers looking for alternative methods in cryptographic entropy generation. The inclusion of numerical verification scripts for the Riemann Explicit Formula allows users to validate the underlying mathematical framework.

# Mentions

This work builds upon the theoretical foundations of the Riemann Hypothesis and the connection between quantum chaos and prime distribution as suggested by the Hilbert-Pólya conjecture.

# References