# Data schema

Every dataset is a pair of files in `data/`:

- `<dataset_id>.csv`: header row, then numeric rows. Columns match `units` in the manifest, in order.
- `<dataset_id>.manifest.json`: metadata, validated against `schema/manifest.schema.json` (JSON Schema 2020-12, no extra fields allowed).

Each dataset has two plots in `plots/`: `<dataset_id>.png` and `<dataset_id>.svg`.

## Manifest fields (all required)

| Field | Type | Meaning |
| :--- | :--- | :--- |
| `dataset_id` | string | Lowercase ID, 3 to 64 chars. Matches the file names data/<id>.csv, data/<id>.manifest.json, plots/<id>.{png,svg}. |
| `kind` | enum: `polar_bler`, `latency` | `polar_bler` (BLER vs SNR) or `latency` (latency samples). |
| `description` | string | One-line description, used as the plot title. |
| `units` | object | Map of CSV column name to unit, in CSV column order. `polar_bler` requires `snr_db` and `bler`; optional `list_size` groups curves. `latency` requires `latency_us`. |
| `git_sha` | string | Commit of the code that produced the data (7 to 40 hex chars). |
| `host_cpu` | string | CPU model of the measurement host. |
| `os_kernel` | string | OS and kernel version. |
| `gpu_model` | string or null | GPU model, or null for CPU-only runs. |
| `driver_version` | string or null | GPU driver version, or null. |
| `cuda_version` | string or null | CUDA version, or null. |
| `clock_source` | enum: `CLOCK_MONOTONIC`, `CLOCK_MONOTONIC_RAW`, `TSC`, `cudaEvent`, `globaltimer`, `none` | Timer used for measurements. `none` for simulations without timing. |
| `timestamp_utc` | string | Capture time, `YYYY-MM-DDTHH:MM:SSZ`. |
| `synthetic` | boolean | `true` if the data is synthetic (pipeline test), `false` if measured or simulated by the producing code. |

## Example

```json
{
  "dataset_id": "example_latency",
  "kind": "latency",
  "description": "Example latency distribution",
  "units": {"latency_us": "us"},
  "git_sha": "0123abc",
  "host_cpu": "x86_64",
  "os_kernel": "Linux 6.8",
  "gpu_model": null,
  "driver_version": null,
  "cuda_version": null,
  "clock_source": "CLOCK_MONOTONIC",
  "timestamp_utc": "2026-01-01T00:00:00Z",
  "synthetic": true
}
```
