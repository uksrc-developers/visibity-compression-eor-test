#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
from pathlib import Path

def exit_with_error(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)

def run_command(command, **kwargs):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, **kwargs)
    if result.returncode != 0:
        exit_with_error(f"Command failed: {command}")

def main():
    parser = argparse.ArgumentParser(description="Run pspipe power spectrum pipeline for one or more MS.")
    parser.add_argument("ms_paths", nargs='+', help="Path(s) to input Measurement Sets (.ms or .MS)")
    parser.add_argument("--psdir", default="ps", help="Path to the directory containing main.toml and ms_lists/ (default: ps)")
    args = parser.parse_args()

    # Resolve all input MS paths BEFORE changing directory
    resolved_ms_paths = []
    for p in args.ms_paths:
        abs_path = Path(p).resolve()
        if abs_path.is_dir() and abs_path.name.lower().endswith(".ms"):
            resolved_ms_paths.append(abs_path)
        else:
            print(f"Skipping invalid MS path: {p}", file=sys.stderr)

    if not resolved_ms_paths:
        exit_with_error("No valid Measurement Set paths provided.")

    ps_dir = Path(args.psdir).resolve()
    ms_list_dir = ps_dir / "ms_lists"

    if not ps_dir.is_dir():
        exit_with_error(f"PS directory not found: {ps_dir}")
    if not (ps_dir / "main.toml").exists():
        exit_with_error(f"main.toml not found in {ps_dir}")
    if not ms_list_dir.exists():
        ms_list_dir.mkdir()

    # Change to the ps directory AFTER resolving paths
    os.chdir(ps_dir)
    print(f"Changed working directory to {ps_dir}")

    obs_names = []
    for ms_path in resolved_ms_paths:
        obs_name = ms_path.stem
        obs_names.append(obs_name)

        ms_list_file = ms_list_dir / obs_name
        with open(ms_list_file, 'w') as f:
            f.write(str(ms_path) + '\n')
        print(f"Created ms_lists entry: {ms_list_file.name}")

    # Add all observations to the database
    add_obs_cmd = f"psdb add_all_obs main.toml " + " ".join(f"ms_lists/{obs}" for obs in obs_names)
    run_command(add_obs_cmd)

    # Run the power spectrum pipeline
    obs_str = ",".join(obs_names)
    pipeline_cmd = f"pspipe image,gen_vis_cube main.toml {obs_str}"
    run_command(pipeline_cmd)

    print("Power spectrum pipeline completed successfully.")

if __name__ == "__main__":
    main()

