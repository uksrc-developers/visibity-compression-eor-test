#!/usr/bin/env python3

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from ps_eor import datacube, pspec
from pspipe import database, settings

import matplotlib as mpl
mpl.rcParams['image.cmap'] = 'Spectral_r'
mpl.rcParams['image.origin'] = 'lower'
mpl.rcParams['image.interpolation'] = 'nearest'
mpl.rcParams['axes.grid'] = True

TRUTH_CUBE_PATH = "sdc3a_truth_eor_f181.h5"


def load_revision(ps_dir, obs_name):
    settings_file = Path(ps_dir) / "main.toml"
    rev = database.VisRevision(settings.Settings.load_with_defaults(str(settings_file)))
    return rev.get_data(obs_name)


def plot_ps2d_comparison(data, data_d1, outdir):
    ps_gen = data.get_ps_gen(window_fct='blackmanharris', umin=30, umax=500, primary_beam='ska_low', rmean_freqs=False)

    fig, axes = plt.subplots(1, 4, figsize=(14, 5), sharey=True)

    ps2d_uncompressed = ps_gen.get_ps2d(data.i)
    ps2d_compressed = ps_gen.get_ps2d(data_d1.i)
    ps2d_diff = ps_gen.get_ps2d(data.i - data_d1.i)
    ps2d_ratio = ps2d_diff / ps_gen.get_ps2d(data.i_dt)

    ps2d_uncompressed.plot(ax=axes[0], vmin=1e-6, vmax=1e3, norm='log', colorbar=False)
    axes[0].set_title("Uncompressed")

    ps2d_compressed.plot(ax=axes[1], vmin=1e-6, vmax=1e3, norm='log', colorbar=False)
    axes[1].set_title("Compressed")
    axes[1].set_ylabel('')

    ps2d_diff.plot(ax=axes[2], vmin=1e-6, vmax=1e3, norm='log', colorbar=True)
    axes[2].set_title("Difference (compression noise)")
    axes[2].set_ylabel('')

    ps2d_ratio.plot(ax=axes[3], vmin=1e-6, vmax=1, norm='log', colorbar=True)
    axes[3].set_title("Ratio (Comp. noise / Thermal noise)")
    axes[3].set_ylabel('')

    ratio_median = np.median(ps2d_ratio.data)
    ratio_mean = np.mean(ps2d_ratio.data)
    axes[3].text(0.05, 0.95, f"Median = {ratio_median:.3e}\nMean = {ratio_mean:.3e}", transform=axes[3].transAxes,
                 fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    fig.savefig(outdir / f"{os.path.basename(outdir)}_ps2d_comparison.png")
    plt.close(fig)


def plot_coherence(data, data_d1, outdir):
    ps_gen_box = data.get_ps_gen(window_fct='boxcar', umin=30, umax=500, primary_beam='ska_low')

    ps2d = ps_gen_box.get_coherence_ps2d(data_d1.i_even - data.i_even,
                                         data_d1.i_odd - data.i_odd,
                                         cross_square=False)

    d = ps2d.data.flatten()
    d_mean = d.mean()
    d_std = d.std()
    d_med = np.median(d)

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    ps2d.plot(ax=axes[0], vmin=-1, vmax=1, norm='linear', cmap='seismic')
    axes[0].set_title("2D Cross-Coherence")

    axes[1].hist(d, bins=25, color='teal', alpha=0.75)
    axes[1].axvline(d_mean, color='red', linestyle='--', label=f'Mean = {d_mean:.3f}')
    axes[1].axvline(d_med, color='green', linestyle='-.', label=f'Median = {d_med:.3f}')
    axes[1].axvline(d_mean + d_std, color='orange', linestyle=':', label=f'Std = {d_std:.3f}')
    axes[1].axvline(d_mean - d_std, color='orange', linestyle=':')

    axes[1].set_xlabel("Cross-Coherence")
    axes[1].set_ylabel("Frequency")
    axes[1].set_title("Histogram of Cross-Coherence")
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()
    fig.savefig(outdir / f"{os.path.basename(outdir)}_coherence_plot.png")
    plt.close(fig)


def plot_ps3d(data, data_d1, ps_dir, outdir):
    fmin = 181  # MHz
    ref_freq = 106
    
    data_truth = datacube.CartDataCube.load(TRUTH_CUBE_PATH)
    ps_gen_truth = pspec.PowerSpectraBuilder().get(data_truth, window_fct='hann', primary_beam='no_pb', rmean_freqs=False, du=8, umin=30, umax=550)

    ps_gen_avoid = data.get_ps_gen(window_fct='blackmanharris', filter_wedge_theta=12, filter_kpar_min=0.1, umin=30, umax=500, primary_beam='ska_low')
    kbins = np.logspace(np.log10(ps_gen_avoid.kmin), np.log10(2.5), 10)

    ps3d_truth = ps_gen_truth.get_ps3d(kbins, data_truth)

    fig, ax = plt.subplots(figsize=(8, 6))

    ps3d_truth.plot(ax=ax, label='21-cm truth', nsigma=0, marker='', color='teal', lw=3)
    (ps_gen_avoid.get_ps3d(kbins, data.i) - ps_gen_avoid.get_ps3d(kbins, data.i_dt)).plot(ax=ax, label='Recovered - uncompressed', fill_std=False, color='crimson', marker='', lw=2)
    (ps_gen_avoid.get_ps3d(kbins, data_d1.i) - ps_gen_avoid.get_ps3d(kbins, data_d1.i_dt)).plot(ax=ax, label='Recovered - compressed', fill_std=False, color='gold', marker='', lw=2)
    ps_gen_avoid.get_ps3d(kbins, data_d1.i - data.i).plot(ax=ax, label='Compression noise', lw=2, nsigma=0, marker='', color='springgreen')
    ps_gen_avoid.get_ps3d(kbins, data.i_dt).plot(ax=ax, label='Thermal noise (uncompressed)', color='dimgrey', nsigma=0, lw=3, ls='--', marker='')

    ax.set_title("3D Power Spectrum Comparison")
    ax.set_ylim(ymin=1e-2)
    ax.legend()
    plt.tight_layout()
    fig.savefig(outdir / f"{os.path.basename(outdir)}_ps3d_comparison.png")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Plot power spectra and coherence from uncompressed and compressed MS observations.")
    parser.add_argument("uncompressed", help="ObsID for the uncompressed data (e.g. RAW)")
    parser.add_argument("compressed", help="ObsID for the compressed data (e.g. DYSCO_DEFAULT)")
    parser.add_argument("--psdir", default="ps", help="Path to the ps directory containing main.toml (default: ps/)")
    args = parser.parse_args()

    data = load_revision(args.psdir, args.uncompressed)
    data_d1 = load_revision(args.psdir, args.compressed)

    outdir = Path("results") / args.compressed
    outdir.mkdir(parents=True, exist_ok=True)

    plot_ps2d_comparison(data, data_d1, outdir)
    plot_coherence(data, data_d1, outdir)
    plot_ps3d(data, data_d1, args.psdir, outdir)


if __name__ == "__main__":
    main()

