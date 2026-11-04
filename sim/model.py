"""Data model for the analytical design-space simulator."""

from __future__ import annotations

from dataclasses import dataclass

REFERENCE_NODE_NM = 5
REFERENCE_CLOCK_GHZ = 1.0
COST_PER_MM2_USD = 0.35
PACKAGE_COST_USD = 8.0


@dataclass(frozen=True)
class Workload:
    id: str
    name: str
    description: str
    ops: float
    bytes_moved: float
    communication_bytes: float
    sequential_steps: int
    parallelism: int
    sparsity: float
    precision_bits: int
    bottleneck: str


@dataclass(frozen=True)
class Architecture:
    id: str
    name: str
    family: str
    execution: str
    memory: str
    dataflow: str
    interconnect: str
    numeric: str
    programming: str
    peak_ops_s: float
    bandwidth_bytes_s: float
    interconnect_bytes_s: float
    energy_per_op_pj: float
    energy_per_byte_pj: float
    energy_per_comm_byte_pj: float
    area_mm2: float
    fixed_latency_us: float
    clock_ghz: float
    utilization: dict[str, float]
    overhead: dict[str, float]
    note: str = ""


@dataclass(frozen=True)
class Metrics:
    compute_ms: float
    memory_ms: float
    interconnect_ms: float
    dependency_ms: float
    latency_ms: float
    throughput_tops: float
    energy_j: float
    average_power_w: float
    area_mm2: float
    cost_usd: float
    perf_per_w_tops: float
    perf_per_dollar_tops: float
    peak_utilization: float
    bottleneck: str


@dataclass(frozen=True)
class Result:
    workload_id: str
    architecture_id: str
    metrics: Metrics
    pareto: bool = False
