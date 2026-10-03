# SPDX-License-Identifier: Apache-2.0
"""Validate every dataset in data/ and confirm plots/ re-renders byte-identical from CSV."""

import csv
import filecmp
import json
import sys
import tempfile
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import render  # noqa: E402

DATA, PLOTS = ROOT / "data", ROOT / "plots"
PLOT_EXTS = (".png", ".svg")


def main():
    schema = json.loads((ROOT / "schema" / "manifest.schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = []

    manifests = {p.name.removesuffix(".manifest.json"): p for p in DATA.glob("*.manifest.json")}
    csvs = {p.stem: p for p in DATA.glob("*.csv")}
    other = [p.name for p in DATA.iterdir() if p.name != ".gitkeep"]
    other = [n for n in other if not (n.endswith(".manifest.json") or n.endswith(".csv"))]
    errors += [f"data/{n}: unexpected file" for n in sorted(other)]
    errors += [f"data/{k}.csv: missing manifest" for k in sorted(csvs.keys() - manifests.keys())]
    errors += [
        f"data/{k}.manifest.json: missing CSV" for k in sorted(manifests.keys() - csvs.keys())
    ]

    expected_plots = {f"{k}{ext}" for k in manifests for ext in PLOT_EXTS}
    actual_plots = {p.name for p in PLOTS.iterdir() if p.name != ".gitkeep"}
    errors += [f"plots/{n}: missing" for n in sorted(expected_plots - actual_plots)]
    errors += [f"plots/{n}: no matching dataset" for n in sorted(actual_plots - expected_plots)]

    with tempfile.TemporaryDirectory() as tmp:
        for ds_id, mpath in sorted(manifests.items()):
            manifest = json.loads(mpath.read_text(encoding="utf-8"))
            errs = [e.message for e in validator.iter_errors(manifest)]
            if errs:
                errors += [f"{mpath.name}: {m}" for m in errs]
                continue
            if manifest["dataset_id"] != ds_id:
                errors.append(f"{mpath.name}: dataset_id does not match file name")
                continue
            if ds_id not in csvs:
                continue
            with open(csvs[ds_id], newline="", encoding="utf-8") as f:
                header = next(csv.reader(f), [])
            if header != list(manifest["units"]):
                errors.append(f"data/{ds_id}.csv: header does not match manifest units")
                continue
            render.render(csvs[ds_id], manifest, tmp)
            for ext in PLOT_EXTS:
                committed = PLOTS / f"{ds_id}{ext}"
                if committed.exists() and not filecmp.cmp(
                    committed, Path(tmp) / f"{ds_id}{ext}", shallow=False
                ):
                    errors.append(f"plots/{ds_id}{ext}: does not match re-render from CSV")

    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    print(f"validate: {len(manifests)} datasets, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
