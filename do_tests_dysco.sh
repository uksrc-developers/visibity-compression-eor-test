#!/bin/bash


# Dysco compression
./compress_ms_dysco.py --norm RF ZW3_IFRQ_0750-0900.ms
./compress_ms_dysco.py --norm AF ZW3_IFRQ_0750-0900.ms
./compress_ms_dysco.py --norm RF --databitrate 12 ZW3_IFRQ_0750-0900.ms
./compress_ms_dysco.py --norm AF --databitrate 12 ZW3_IFRQ_0750-0900.ms
./compress_ms_dysco.py --norm RF ZW3_IFRQ_0750-0900_N.ms
./compress_ms_dysco.py --norm AF ZW3_IFRQ_0750-0900_N.ms

# Generate power-spectra with pspipe
./run_pspipe.py ZW3_IFRQ_0750-0900.ms ZW3_IFRQ_0750-0900_10bit_AF.ms ZW3_IFRQ_0750-0900_10bit_RF.ms ZW3_IFRQ_0750-0900_12bit_AF.ms ZW3_IFRQ_0750-0900_12bit_RF.ms
./run_pspipe.py ZW3_IFRQ_0750-0900_N.ms ZW3_IFRQ_0750-0900_N_10bit_AF.ms ZW3_IFRQ_0750-0900_N_10bit_RF.ms

# Generate results

# --- For ZW3_IFRQ_0750-0900_10bit_AF ---
mkdir -p results/ZW3_IFRQ_0750-0900_10bit_AF
./compare_ms_sizes.py ZW3_IFRQ_0750-0900.ms ZW3_IFRQ_0750-0900_10bit_AF.ms > results/ZW3_IFRQ_0750-0900_10bit_AF/size_comparison.txt
./make_ps.py ZW3_IFRQ_0750-0900 ZW3_IFRQ_0750-0900_10bit_AF

# --- For ZW3_IFRQ_0750-0900_10bit_RF ---
mkdir -p results/ZW3_IFRQ_0750-0900_10bit_RF
./compare_ms_sizes.py ZW3_IFRQ_0750-0900.ms ZW3_IFRQ_0750-0900_10bit_RF.ms > results/ZW3_IFRQ_0750-0900_10bit_RF/size_comparison.txt
./make_ps.py ZW3_IFRQ_0750-0900 ZW3_IFRQ_0750-0900_10bit_RF

# --- For ZW3_IFRQ_0750-0900_12bit_AF ---
mkdir -p results/ZW3_IFRQ_0750-0900_12bit_AF
./compare_ms_sizes.py ZW3_IFRQ_0750-0900.ms ZW3_IFRQ_0750-0900_12bit_AF.ms > results/ZW3_IFRQ_0750-0900_12bit_AF/size_comparison.txt
./make_ps.py ZW3_IFRQ_0750-0900 ZW3_IFRQ_0750-0900_12bit_AF

# --- For ZW3_IFRQ_0750-0900_12bit_RF ---
mkdir -p results/ZW3_IFRQ_0750-0900_12bit_RF
./compare_ms_sizes.py ZW3_IFRQ_0750-0900.ms ZW3_IFRQ_0750-0900_12bit_RF.ms > results/ZW3_IFRQ_0750-0900_12bit_RF/size_comparison.txt
./make_ps.py ZW3_IFRQ_0750-0900 ZW3_IFRQ_0750-0900_12bit_RF

# --- For ZW3_IFRQ_0750-0900_N_10bit_AF ---
mkdir -p results/ZW3_IFRQ_0750-0900_N_10bit_AF
./compare_ms_sizes.py ZW3_IFRQ_0750-0900_N.ms ZW3_IFRQ_0750-0900_N_10bit_AF.ms > results/ZW3_IFRQ_0750-0900_N_10bit_AF/size_comparison.txt
./make_ps.py ZW3_IFRQ_0750-0900_N ZW3_IFRQ_0750-0900_N_10bit_AF

# --- For ZW3_IFRQ_0750-0900_N_10bit_RF ---
mkdir -p results/ZW3_IFRQ_0750-0900_N_10bit_RF
./compare_ms_sizes.py ZW3_IFRQ_0750-0900_N.ms ZW3_IFRQ_0750-0900_N_10bit_RF.ms > results/ZW3_IFRQ_0750-0900_N_10bit_RF/size_comparison.txt
./make_ps.py ZW3_IFRQ_0750-0900_N ZW3_IFRQ_0750-0900_N_10bit_RF
