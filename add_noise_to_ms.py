#!/usr/bin/env python3
import os
import shutil
import numpy as np
import argparse
from casacore.tables import table


def add_noise_to_ms(ms_in, ms_out, sefd, chunk_size=10000):
    if os.path.exists(ms_out):
        shutil.rmtree(ms_out)
    shutil.copytree(ms_in, ms_out)

    with table(ms_out, readonly=False) as t:
        n_rows = t.nrows()
        interval = t.getcell('INTERVAL', 0)  # seconds

        with table(os.path.join(ms_out, 'SPECTRAL_WINDOW')) as spw:
            chan_widths = spw.getcol('CHAN_WIDTH')[0]
            delta_nu = np.mean(np.abs(chan_widths))  # Hz

        sigma = sefd / np.sqrt(2 * delta_nu * interval)
        print(f"Injecting noise (σ = {sigma:.2e}) into {ms_out} in chunks of {chunk_size} rows...")

        for start_row in range(0, n_rows, chunk_size):
            end_row = min(start_row + chunk_size, n_rows)
            data_chunk = t.getcol('DATA', startrow=start_row, nrow=end_row - start_row)

            noise_chunk = (
                np.random.normal(0, sigma, data_chunk.shape) +
                1j * np.random.normal(0, sigma, data_chunk.shape)
            ).astype(np.complex64)

            t.putcol('DATA', data_chunk + noise_chunk, startrow=start_row, nrow=end_row - start_row)

    print("Noise injection completed.")


def parse_args():
    parser = argparse.ArgumentParser(description="Inject thermal noise into a Measurement Set.")
    parser.add_argument("input_ms", help="Input Measurement Set")
    parser.add_argument("output_ms", help="Output Measurement Set with noise")
    parser.add_argument("sefd", type=float, help="System Equivalent Flux Density (SEFD) in Jy")
    parser.add_argument("--chunk-size", type=int, default=10000,
                        help="Number of rows to process at a time (default: 10000)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    add_noise_to_ms(args.input_ms, args.output_ms, args.sefd, args.chunk_size)

