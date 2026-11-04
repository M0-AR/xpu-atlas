"""Host microbenchmarks instantiating the generality/efficiency frontier.

Three workloads separate latency-optimised serial execution from
throughput-optimised parallel execution:

1. serial_chain   : a dependent integer recurrence (one lane, latency-bound).
2. vector_elementwise : sin(x)cos(x) + x^2 over N elements, scalar Python vs
   NumPy SIMD, plus thread-pool chunking.
3. matmul         : dense square matrix multiplication, reported in GFLOPS.

The study is deliberately hardware-local and small. It does not benchmark any
commercial accelerator; it measures the *shape* of the trade-off on the host
CPU so that the CPU/GPU analogy can be quantified rather than asserted.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable

import numpy as np

from .io_utils import RESULTS, ensure_dirs, utc_now_iso, write_csv, write_json

RAPL_PATH = Path("/sys/class/powercap/intel-rapl:0/energy_uj")
SERIAL_SIZES = [1_000_000, 3_000_000, 10_000_000]
VECTOR_SIZES = [1_000, 10_000, 100_000, 1_000_000, 10_000_000]
THREAD_SIZE = 8_000_000
THREAD_COUNTS = [1, 2, 4, 8]
MATMUL_SIZES = [256, 512, 1024, 2048]


def median_time(fn: Callable[[], object], repeats: int = 4, warmup: int = 1) -> tuple[float, float]:
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    ordered = sorted(samples)
    median = statistics.median(ordered)
    q1 = ordered[len(ordered) // 4]
    q3 = ordered[(3 * len(ordered)) // 4]
    return median, q3 - q1


def serial_chain(n: int) -> int:
    x = 123456789
    for _ in range(n):
        x = (x * 1664525 + 1013904223) & 0xFFFFFFFF
    return x


def python_elementwise(values: list[float]) -> list[float]:
    return [v * v + 3.0 * v + 1.0 for v in values]


def run_serial() -> list[dict[str, float]]:
    rows = []
    for n in SERIAL_SIZES:
        elapsed, iqr = median_time(lambda n=n: serial_chain(n))
        rows.append(
            {
                "n": n,
                "median_s": elapsed,
                "iqr_s": iqr,
                "ops_per_s": n / elapsed,
            }
        )
        print(f"[serial] n={n:>10,} t={elapsed:.4f}s ops/s={n / elapsed:,.0f}", file=sys.stderr)
    return rows


def run_vector() -> list[dict[str, float]]:
    rng = np.random.default_rng(20261104)
    rows = []
    for n in VECTOR_SIZES:
        array = rng.standard_normal(n)
        numpy_time, numpy_iqr = median_time(lambda a=array: a * a + 3.0 * a + 1.0)
        row: dict[str, float] = {
            "n": n,
            "numpy_median_s": numpy_time,
            "numpy_iqr_s": numpy_iqr,
            "numpy_ops_per_s": n / numpy_time,
        }
        if n <= 1_000_000:
            values = array.tolist()
            python_time, python_iqr = median_time(lambda v=values: python_elementwise(v), repeats=3)
            row.update(
                {
                    "python_median_s": python_time,
                    "python_iqr_s": python_iqr,
                    "python_ops_per_s": n / python_time,
                    "speedup": python_time / numpy_time,
                }
            )
        rows.append(row)
        print(
            f"[vector] n={n:>10,} numpy={numpy_time:.5f}s "
            f"speedup={row.get('speedup', float('nan')):.1f}x",
            file=sys.stderr,
        )
    return rows


def _chunk_apply(array: np.ndarray, workers: int) -> None:
    edges = np.linspace(0, array.size, workers + 1, dtype=int)
    chunks = [array[edges[i] : edges[i + 1]] for i in range(workers)]

    def work(chunk: np.ndarray) -> None:
        chunk * chunk + 3.0 * chunk + 1.0

    if workers == 1:
        work(chunks[0])
        return
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(work, chunks))


def run_threads() -> list[dict[str, float]]:
    rng = np.random.default_rng(7)
    array = rng.standard_normal(THREAD_SIZE)
    rows = []
    baseline = None
    for workers in THREAD_COUNTS:
        elapsed, iqr = median_time(lambda w=workers: _chunk_apply(array, w), repeats=4)
        if baseline is None:
            baseline = elapsed
        rows.append(
            {
                "threads": workers,
                "median_s": elapsed,
                "iqr_s": iqr,
                "ops_per_s": THREAD_SIZE / elapsed,
                "speedup_vs_1": baseline / elapsed,
                "parallel_efficiency": (baseline / elapsed) / workers,
            }
        )
        print(
            f"[threads] workers={workers} t={elapsed:.5f}s "
            f"speedup={baseline / elapsed:.2f}x",
            file=sys.stderr,
        )
    return rows


def run_matmul() -> list[dict[str, float]]:
    rng = np.random.default_rng(11)
    rows = []
    batches = {256: 50, 512: 20, 1024: 5, 2048: 2}
    for n in MATMUL_SIZES:
        a = rng.standard_normal((n, n))
        b = rng.standard_normal((n, n))
        batch = batches.get(n, 1)

        def work(a=a, b=b, batch=batch) -> None:
            for _ in range(batch):
                a @ b

        elapsed, iqr = median_time(work, repeats=5, warmup=1)
        per_call = elapsed / batch
        flops = 2.0 * n**3
        rows.append(
            {
                "n": n,
                "batch": batch,
                "median_s": per_call,
                "iqr_s": iqr / batch,
                "gflops": flops / per_call / 1e9,
            }
        )
        print(f"[matmul] n={n} t={per_call:.4f}s {flops / per_call / 1e9:.1f} GFLOPS", file=sys.stderr)
    return rows


def read_energy_uj() -> int | None:
    try:
        return int(RAPL_PATH.read_text(encoding="ascii").strip())
    except (OSError, ValueError):
        return None


def measure_energy() -> dict[str, float | None]:
    start_energy = read_energy_uj()
    if start_energy is None:
        return {"joules": None, "gflops_per_watt": None, "note": "RAPL energy counter unavailable"}
    rng = np.random.default_rng(13)
    n = 512
    a = rng.standard_normal((n, n))
    b = rng.standard_normal((n, n))
    start = time.perf_counter()
    operations = 0
    while time.perf_counter() - start < 1.0:
        a @ b
        operations += 2.0 * n**3
    elapsed = time.perf_counter() - start
    end_energy = read_energy_uj()
    if end_energy is None or end_energy <= start_energy:
        return {"joules": None, "gflops_per_watt": None, "note": "RAPL counter not readable after run"}
    joules = (end_energy - start_energy) / 1e6
    return {
        "joules": joules,
        "gflops_per_watt": operations / elapsed / 1e9 / (joules / elapsed),
        "note": "package-level RAPL energy, one-second matmul loop",
    }


def cpu_model() -> str:
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true", help="run reduced sizes for CI")
    args = parser.parse_args()
    ensure_dirs()
    started = utc_now_iso()

    platform_info = {
        "cpu_model": cpu_model(),
        "logical_cores": os.cpu_count(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "machine": platform.machine(),
        "system": platform.system(),
        "started_at": started,
    }

    payload = {
        "platform": platform_info,
        "serial": run_serial(),
        "vector": run_vector(),
        "threads": run_threads(),
        "matmul": run_matmul(),
        "energy": measure_energy(),
    }
    payload["finished_at"] = utc_now_iso()

    write_json(RESULTS / "bench.json", payload)
    rows = []
    for row in payload["serial"]:
        rows.append({"workload": "serial", **row})
    for row in payload["vector"]:
        rows.append({"workload": "vector", **row})
    for row in payload["threads"]:
        rows.append({"workload": "threads", **row})
    for row in payload["matmul"]:
        rows.append({"workload": "matmul", **row})
    fieldnames = sorted({key for row in rows for key in row})
    write_csv(RESULTS / "bench.csv", rows, fieldnames)
    print(json.dumps(platform_info, indent=2), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
