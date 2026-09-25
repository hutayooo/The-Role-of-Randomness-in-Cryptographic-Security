# The-Role-of-Randomness-in-Cryptographic-Security
# The Role of Randomness in Cryptographic Security

> **Comparative Performance and Statistical Evaluation of CSPRNGs vs. Non-Cryptographic PRNGs**

[![License: MIT](https://img.shields.io/badge/Code_License-MIT-yellow.svg)](LICENSE)
[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/Paper_License-CC_BY--NC--ND_4.0-lightgrey.svg)](LICENSE_PAPER.md)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)

---

## 📌 Research Overview

This repository contains the experimental framework, data analysis scripts, and paper for an Extended Essay investigating the trade-offs between **Cryptographically Secure Pseudo-Random Number Generators (CSPRNGs)** and **standard PRNGs**.

### Research Question
> *"How do Cryptographically Secure Pseudo-Random Number Generators (CSPRNGs) compare to Non-Cryptographically Secure PRNGs in terms of statistical randomness, computational efficiency, and suitability for cryptographic applications?"*

---

## 🎯 Key Findings & Empirical Results

Benchmarked across datasets ranging from **1 Million to 10 Million bits** on an **Intel® Core™ Ultra 9 285H** testbed:

| Generator | Type | NIST SP 800-22 Score | Shannon Entropy ($H$) | Chi-Square ($\chi^2$) | Pearson Correlation ($r$) | Speed (10M bits) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **LCG** | Non-Crypto PRNG | 5/15 (FAIL) | 8.0000 | 0.01 (FAIL) | 0.825102 (FAIL) | 0.266s |
| **Mersenne Twister** | Standard PRNG | 14/15 (PASS) | 7.9998 | 274.42 (PASS) | 0.000155 (PASS) | 0.524s |
| **ChaCha20RNG** | CSPRNG | **15/15 (PASS)** | 7.9998 | 275.04 (PASS) | **-0.000087 (PASS)** | **0.099s** |
| **SecretsRNG** | CSPRNG | **15/15 (PASS)** | 7.9998 | 261.49 (PASS) | 0.000211 (PASS) | 0.115s |

### Core Takeaways
1. **Entropy Fallacy:** A perfect Shannon Entropy score ($H = 8.0000$) does not guarantee randomness (e.g., LCG scored perfect entropy but completely failed uniformity and correlation tests).
2. **Speed Advantage:** Modern CSPRNGs using stream ciphers (**ChaCha20**) were **~5.29× faster** than non-crypto generators like the Mersenne Twister while maintaining full cryptographic security.
3. **State Recoverability:** While the Mersenne Twister passed statistical randomness, its internal state (624 32-bit integers) can be fully reverse-engineered after observing 624 outputs, rendering it unsuitable for cryptographic operations.

---

<Image alt="Diagram illustrating the cryptographically secure pseudorandom number generator evaluation concept" caption="Cryptographically Secure PRNG Evaluation Overview" src="image_agent_tag_16111113388906728758"/>

---

## 📁 Repository Structure

```text
.
├── README.md                 # Main project summary and documentation
├── LICENSE                   # Software code license (MIT)
├── LICENSE_PAPER.md          # Research document license (CC BY-NC-ND 4.0)
├── paper/
│   └── CS_Extended_Essay.pdf # Complete anonymized research document
├── src/
│   ├── rng_testing_suite.py  # RNG generators and statistical testing harness
│   └── requirements.txt      # Dependency configurations
└── bitstreams/               # Generated binary streams (git-ignored by default)
