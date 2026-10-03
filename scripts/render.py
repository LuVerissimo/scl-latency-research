# SPDX-License-Identifier: Apache-2.0
"""Render plots from exported CSV + manifest pairs. Deterministic: same inputs and
pinned library versions give byte-identical PNG and SVG output.

Usage: python render.py --data data --out plots
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

SEED = 0
RC = {
    "svg.hashsalt": "0",
    "svg.fonttype": "none",
    "font.family": "DejaVu Sans",
    "figure.dpi": 100,
    "savefig.dpi": 150,
}
PNG_META = {"Software": None}
SVG_META = {"Date": None, "Creator": None}


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path}: no data rows")
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


def label(col, units):
    return f"{col} [{units[col]}]" if units.get(col) else col


def title(manifest):
    t = manifest["description"]
    return t + " (synthetic)" if manifest["synthetic"] else t


def plot_polar_bler(cols, manifest, ax):
    units = manifest["units"]
    group = "list_size" if "list_size" in cols else None
    keys = sorted(set(cols[group])) if group else [None]
    for k in keys:
        m = cols[group] == k if group else np.ones_like(cols["snr_db"], dtype=bool)
        order = np.argsort(cols["snr_db"][m])
        name = f"L={int(k)}" if group else "BLER"
        ax.semilogy(cols["snr_db"][m][order], cols["bler"][m][order], marker="o", label=name)
    ax.set_xlabel(label("snr_db", units))
    ax.set_ylabel(label("bler", units))
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.5)
    ax.legend(loc="lower left")


def plot_latency(cols, manifest, axes):
    units = manifest["units"]
    x = np.sort(cols["latency_us"])
    hist_ax, ccdf_ax = axes
    hist_ax.hist(x, bins=60, log=True, edgecolor="black", linewidth=0.3)
    hist_ax.set_xlabel(label("latency_us", units))
    hist_ax.set_ylabel("count (log)")
    ccdf = 1.0 - np.arange(len(x)) / len(x)
    ccdf_ax.semilogy(x, ccdf, drawstyle="steps-post")
    ccdf_ax.set_xlabel(label("latency_us", units))
    ccdf_ax.set_ylabel("P(X >= x)")
    stats = [f"n = {len(x)}"] + [
        f"p{p:g} = {np.percentile(x, p):.2f}" for p in (50, 99, 99.9, 99.99)
    ]
    ccdf_ax.text(
        0.98,
        0.98,
        "\n".join(stats),
        transform=ccdf_ax.transAxes,
        ha="right",
        va="top",
        fontsize=8,
        family="monospace",
    )
    for ax in axes:
        ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.5)


def render(csv_path, manifest, out_dir):
    np.random.seed(SEED)
    cols = read_csv(csv_path)
    with plt.rc_context(RC):
        if manifest["kind"] == "polar_bler":
            fig, ax = plt.subplots(figsize=(7, 5))
            plot_polar_bler(cols, manifest, ax)
        elif manifest["kind"] == "latency":
            fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
            plot_latency(cols, manifest, axes)
        else:
            raise ValueError(f"unknown kind {manifest['kind']!r}")
        fig.suptitle(title(manifest), fontsize=11)
        fig.tight_layout()
        stem = Path(out_dir) / manifest["dataset_id"]
        fig.savefig(stem.with_suffix(".png"), metadata=PNG_META)
        fig.savefig(stem.with_suffix(".svg"), metadata=SVG_META)
        plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    manifests = sorted(args.data.glob("*.manifest.json"))
    if not manifests:
        print(f"render: no manifests in {args.data}", file=sys.stderr)
        return 1
    for mpath in manifests:
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
        render(args.data / f"{manifest['dataset_id']}.csv", manifest, args.out)
        print(f"render: {manifest['dataset_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
