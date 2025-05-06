#!/usr/bin/env python3

import argparse
import subprocess
import os
import re

COLUMNS = ['DATA', 'WEIGHT_SPECTRUM']  # Exclude WEIGHTS

def get_dir_size(path):
    try:
        result = subprocess.run(['du', '-sb', path], capture_output=True, text=True, check=True)
        return int(result.stdout.split()[0])
    except Exception as e:
        print(f"Error getting directory size for {path}: {e}")
        return None

def get_column_size(ms_path, column):
    try:
        result = subprocess.run(['./ms_col_size.py', ms_path, column], capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        match = re.search(rf"{column}:\s*([\d.]+)\s*MB", output)
        if match:
            mb = float(match.group(1))
            return int(mb * 1024 * 1024)
        else:
            raise ValueError(f"Could not parse size from output: {output}")
    except Exception as e:
        print(f"Error getting column '{column}' size for {ms_path}: {e}")
        return None

def get_noise_std(path):
    try:
        result = subprocess.run(['./get_noise_std.py', path], capture_output=True, text=True, check=True)
        output = result.stdout

        std_first = None
        std_diff = None

        for line in output.splitlines():
            if "STD over first 10 timesteps" in line:
                std_first = float(line.strip().split(":")[-1])
            elif "STD of diff between successive timesteps" in line:
                std_diff = float(line.strip().split(":")[-1])

        return std_first, std_diff
    except Exception as e:
        print(f"Error running get_noise_std.py on {path}: {e}")
        return None, None

def format_size(bytes):
    for unit in ['B','KB','MB','GB','TB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} PB"

def format_number(x):
    return f"{x:.6f}" if x is not None else "N/A"

def compute_ratio(orig, comp, is_bytes):
    if orig is None or comp is None or comp == 0:
        return "N/A"
    if is_bytes:
        return f"{(orig / comp):.2f}x"
    else:
        return f"{((comp / orig - 1) * 100):.5f}%"  # Higher precision for small diffs

def print_row(label, orig, comp, is_bytes=True):
    if is_bytes:
        o_val = format_size(orig) if orig is not None else "N/A"
        c_val = format_size(comp) if comp is not None else "N/A"
    else:
        o_val = format_number(orig)
        c_val = format_number(comp)

    ratio = compute_ratio(orig, comp, is_bytes)

    print(f"{label:<25} | {o_val:>12} | {c_val:>12} | {ratio:>9}")

def main():
    parser = argparse.ArgumentParser(description="Compare size and noise stats of MS files")
    parser.add_argument("original", help="Path to original Measurement Set")
    parser.add_argument("compressed", help="Path to compressed Measurement Set")
    args = parser.parse_args()

    print(f"{'Metric':<25} | {'Original':>12} | {'Compressed':>12} | {'Ratio':>9}")
    print("-" * 67)

    # Total MS size
    orig_total = get_dir_size(args.original)
    comp_total = get_dir_size(args.compressed)
    print_row("Total MS size", orig_total, comp_total)

    # Column sizes
    for col in COLUMNS:
        orig_size = get_column_size(args.original, col)
        comp_size = get_column_size(args.compressed, col)
        print_row(f"{col} size", orig_size, comp_size)

    # Noise stats
    std_orig, diff_orig = get_noise_std(args.original)
    std_comp, diff_comp = get_noise_std(args.compressed)
    print_row("STD (first 10)", std_orig, std_comp, is_bytes=False)
    print_row("Noise STD (Δt)", diff_orig, diff_comp, is_bytes=False)

if __name__ == "__main__":
    main()

