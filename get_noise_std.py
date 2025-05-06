#!/usr/bin/env python3
import sys
import numpy as np
from casacore.tables import table

def main(ms_path):
    t = table(ms_path, readonly=True)

    # Determine number of baselines from unique ANTENNA1/2 pairs
    ant1 = t.getcol('ANTENNA1')
    ant2 = t.getcol('ANTENNA2')
    baselines = sorted(set(zip(ant1, ant2)))
    nbl = len(baselines)

    # Read the first 10 time steps = first 10 × nbl rows
    ntime = 10
    data = t.getcol('DATA', startrow=0, nrow=ntime * nbl)  # shape: (ntime * nbl, nchan, npol)
    t.close()

    # Reshape to (ntime, nbl, nchan, npol)
    data = data.reshape((ntime, nbl, data.shape[1], data.shape[2]))

    # Flatten all dimensions except time
    vis_flat = data.reshape(ntime, -1)  # shape: (ntime, nbl*nchan*npol)

    std_all = np.std(vis_flat)
    diff = np.diff(vis_flat, axis=0)
    std_diff = 1 / 2 * np.std(diff)

    print(f"STD over first 10 timesteps: {std_all}")
    print(f"STD of diff between successive timesteps: {std_diff}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: compute_std_vis.py <measurement_set.ms>")
        sys.exit(1)

    main(sys.argv[1])

