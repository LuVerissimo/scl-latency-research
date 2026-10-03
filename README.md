# SCL Decoding and GPU Latency Measurements

This repository contains measurement results only: CSV data, a manifest per dataset, and the plots rendered from them. It contains no system designs, source code for the measured systems, or product information.

## What the data is

| Kind | Content |
| :--- | :--- |
| `polar_bler` | Block error rate (BLER) vs SNR for successive cancellation list (SCL) decoding of polar codes, optionally per list size. |
| `latency` | Latency samples from ring-buffer and GPU persistent-kernel processing loops, reported as histogram and CCDF with p50, p99, p99.9, p99.99. |

The work targets deterministic, low-latency signal processing for civil uses such as industrial automation and research instrumentation.

## How it was measured

Each `data/<id>.manifest.json` records how its dataset was produced: commit of the producing code, host CPU, OS and kernel, GPU model, driver and CUDA versions, clock source, UTC timestamp, and units per column. Datasets with `"synthetic": true` are pipeline tests, not results. See [DATA_SCHEMA.md](DATA_SCHEMA.md).

## Reproduce the plots

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/render.py --data data --out /tmp/plots
.venv/bin/python scripts/validate.py
```

`validate.py` checks every manifest against the schema and confirms each committed plot is byte-identical to a fresh render from its CSV. Byte-identical output requires the pinned versions in `requirements.txt`; CI runs it on every pull request.

## Layout

| Path | Content |
| :--- | :--- |
| `data/` | `<id>.csv` and `<id>.manifest.json` |
| `plots/` | `<id>.png` and `<id>.svg` |
| `schema/` | Manifest JSON Schema |
| `scripts/` | `render.py`, `validate.py` |

## License

- Code (`scripts/`, `.github/`): Apache-2.0, see [LICENSE](LICENSE).
- Data and plots (`data/`, `plots/`): CC-BY-4.0, see [LICENSE-DATA](LICENSE-DATA).

Cite using [CITATION.cff](CITATION.cff).
