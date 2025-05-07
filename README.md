# Visibility Compression Evaluation - EoR test case

This repository contains scripts and tools to evaluate the performance of visibility compression algorithms on a test case relevant to **Epoch of Reionization (EoR)** science with SKA-like data.

**Feature page:**  
[Compression of visibsilities on SKA Confluence](https://confluence.skatelescope.org/display/SRCSC/Compression+of+visibilities)

---

## Overview

This test benchmarks several compression configurations, following the strategy outlined in **Chege et al. 2024**. It quantifies both the **compression ratio** and the **impact of compression noise** on power spectrum analysis, using a representative EoR dataset from the SKA Data Challenge 3a (SDC3a).

---

## Key Evaluation Criteria

- **Low compression noise per dataset**, ideally below the thermal noise level.
- **Uncorrelated compression noise across datasets**, so it averages down like thermal noise when stacking observations.

---

## Dataset

- Input: **SDC3a Measurement Set**
- Frequency range: **750–900 MHz**
- The dataset is concatenated into a single MS to reduce metadata overhead.

---

## Software Versions

- **DP3**: v6.0 (2023-08-11)  
- **WSClean**: v3.4 (2023-10-11)  
- **pspipe**: v0.5.1  
- **ps_eor**: v0.30  

---

## Procedure

The full pipeline consists of the following steps, each executed via dedicated scripts in this repository:

1. **Compress the Measurement Set**  
   - Script: [`compress_ms_dysco.py`](./compress_ms_dysco.py)  
   - Applies Dysco compression with specified `norm` and optional `databitrate`.

2. **Generate image cubes**  
   - Script: [`run_pspipe.py`](./run_pspipe.py)  
   - Calls `pspipe` to create image cubes from both original and compressed MS.

3. **Compute power spectra**  
   - Script: [`make_ps.py`](./make_ps.py)  
   - Uses `ps_eor` to derive 2D power spectra for comparison.
   - Calculates:
     - Compression noise in cylindrically averaged power spectra
     - Correlation of compression noise between independent subsets
     - Impact on 21-cm signal detectability

4. **Evaluate compression performance**  
   - Script: [`compare_ms_sizes.py`](./compare_ms_sizes.py)  
   - Calculates:
     - Compression ratio (total size, `DATA`, and `WEIGHT_SPECTRUM`)
     - Visibility statistics (standard deviation, time-difference std)
---

## Results

- All test outputs are stored in the `results/` directory.
- Detailed logs are available in the `logs/` folders.

