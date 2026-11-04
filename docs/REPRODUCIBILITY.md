# Reproducibility

## Environment

- Python 3.12 (the Docker image pins `python:3.12-slim`)
- NumPy, Matplotlib, PyYAML and pytest, pinned in `requirements.txt`
- No network access is required for the default pipeline

The reference machine for the committed benchmark is an Intel Core i7-14700F
with 28 logical cores, Linux, Python 3.12.13 and NumPy 2.2.6. Benchmark numbers
will vary on other hardware; the analysis pipeline will not.

## Commands

```bash
make install     # install dependencies and the package
make all         # claims + analyze + figures + report + paper-check, then tests
make bench       # refresh host CPU benchmarks (changes committed results)
make test        # pytest only
make paper-check # README/result consistency only
make fetch       # refresh live snapshots (network required)
```

The default `make all` is offline and deterministic. `make fetch` changes the
snapshots; `make bench` changes the committed benchmark results. Neither is part
of the default pipeline.

## Docker

```bash
docker compose build
docker compose up --abort-on-container-exit
```

The `pipeline` service runs `make all`. The `test` service runs `pytest -q`.
Both mount `results/`, `figures/` and `docs/` so generated artifacts are visible
on the host.

## Frozen inputs

`data/snapshots/capture_manifest.json` records the SHA256 of each snapshot. The
test suite recomputes the hashes and fails if a file changes without a manifest
update.

| File | SHA256 |
|---|---|
| `openalex_counts.json` | `7512dfd09dfc97195cfdb8dbeae3e59a01c541e3c915d50ebbb52df52931ff95` |
| `wikimedia_pageviews.json` | `e45e5c6dca17c0adc983b15bb539a4eab2fe4fcc13b3df8cdc7e5ffa25bd051c` |
| `yahoo_prices.json` | `c641f5623c8382056826c77961ce304cb6922e96caef5b69ef05d56054121d12` |

## Deterministic outputs

| Output | Producer |
|---|---|
| `results/evidence_audit.json` | `python -m xpu_atlas.claims` |
| `results/analysis.json` | `python -m xpu_atlas.analyze` |
| `results/summary.json` | `python -m xpu_atlas.analyze` |
| `results/bench.json`, `bench.csv` | `make bench` (explicit; hardware-dependent) |
| `figures/fig1..fig6` | `python -m xpu_atlas.figures` |
| `docs/EVIDENCE.md`, `docs/RESULTS.md` | `python -m xpu_atlas.report` |

## Failure modes

- **Missing `results/evidence_audit.json`:** run `make claims` before
  `make analyze`.
- **Missing figures or docs:** run `make figures report`.
- **Paper check fails:** a headline number changed without a README update.
  Regenerate the results and update the README, or investigate the change.
- **Benchmark variance:** the benchmark is host-dependent. The paper reports the
  committed run; reruns are expected to differ by a few percent.
- **Live fetch rate limits:** OpenAlex and Wikimedia may return HTTP 429. The
  fetcher backs off and retries; if it still fails, use the committed snapshots.
