#!/usr/bin/env python3

import argparse
import subprocess
import datetime
import os
import shlex

def build_output_name(msin, bitrate, norm):
    # Ensure .ms or .MS
    if not msin.lower().endswith('.ms'):
        raise ValueError("Input file must end with '.ms' or '.MS'")
    base, ext = os.path.splitext(msin)
    return f"{base}_{bitrate}bit_{norm}{ext}"

def build_log_name(msin, bitrate, norm):
    base = os.path.basename(msin)
    if base.lower().endswith('.ms'):
        base = base[:-3]  # Remove .ms or .MS
    return f"logs/{base}_{bitrate}bit_{norm}.log"

def main():
    parser = argparse.ArgumentParser(description="Compress a Measurement Set using DP3 and log performance.")
    parser.add_argument("msin", help="Input Measurement Set (.ms or .MS)")
    parser.add_argument("--norm", choices=['AF', 'RF'], default='AF', help="Normalization method (default: AF)")
    parser.add_argument("--databitrate", type=int, default=10, help="Bits per float for visibility columns (default: 10)")
    
    args = parser.parse_args()
    msin = args.msin
    norm = args.norm
    bitrate = args.databitrate

    msout = build_output_name(msin, bitrate, norm)
    log_file = build_log_name(msin, bitrate, norm)

    start_time = datetime.datetime.now()

    cmd = (
        f"/usr/bin/time -v DP3 steps=[] numthreads=20 "
        f"msin={shlex.quote(msin)} "
        f"msout={shlex.quote(msout)} "
        f"msout.overwrite=true "
        f"msout.storagemanager='dysco' "
        f"msout.storagemanager.databitrate={bitrate} "
        f"msout.storagemanager.normalization={norm}"
        ""
    )

    with open(log_file, 'w') as log:
        log.write(f"# Compression log\n")
        log.write(f"Start time: {start_time.isoformat()}\n")
        log.write(f"Command: {cmd}\n\n")
        log.flush()

        process = subprocess.run(cmd, shell=True, stdout=log, stderr=subprocess.STDOUT)

        end_time = datetime.datetime.now()
        duration = end_time - start_time

        log.write(f"\nEnd time: {end_time.isoformat()}\n")
        log.write(f"Duration: {duration}\n")
        log.write(f"Exit code: {process.returncode}\n")

    print(f"Compression finished. Log written to {log_file}")

if __name__ == "__main__":
    main()

