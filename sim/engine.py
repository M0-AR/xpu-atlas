"""Analytical simulator and design-space payload builder."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, replace
from math import isfinite

from .architectures import ARCHITECTURES
from .design_space import AXES, AXIS_ORDER, cartesian_size
from .model import (
    COST_PER_MM2_USD,
    PACKAGE_COST_USD,
    REFERENCE_CLOCK_GHZ,
    REFERENCE_NODE_NM,
    Architecture,
    Metrics,
    Result,
    Workload,
)
from .pareto import pareto_frontier
from .workloads import WORKLOADS


def simulate(workload: Workload, architecture: Architecture) -> Metrics:
    """Return analytical metrics for one workload/architecture pair.

    The model is intentionally transparent:

    * compute time = effective ops / (peak ops * workload utilization)
    * memory time = bytes moved / peak bandwidth
    * interconnect time = communication bytes / peak interconnect bandwidth
    * latency = max(stage times) * mapping overhead + fixed latency + dependency
    * energy = ops * energy/op + bytes * energy/byte + comm * energy/comm-byte
    """

    utilization = architecture.utilization[workload.id]
    compute_s = workload.ops / (architecture.peak_ops_s * utilization)
    memory_s = workload.bytes_moved / architecture.bandwidth_bytes_s
    interconnect_s = workload.communication_bytes / architecture.interconnect_bytes_s
    dependency_s = workload.sequential_steps / (architecture.clock_ghz * 1e9)

    stage_s = max(compute_s, memory_s, interconnect_s)
    latency_s = (
        stage_s * architecture.overhead[workload.id]
        + dependency_s
        + architecture.fixed_latency_us * 1e-6
    )

    throughput_ops_s = workload.ops / latency_s
    energy_pj = (
        workload.ops * architecture.energy_per_op_pj
        + workload.bytes_moved * architecture.energy_per_byte_pj
        + workload.communication_bytes * architecture.energy_per_comm_byte_pj
    )
    energy_j = energy_pj * 1e-12
    average_power_w = energy_j / latency_s
    cost_usd = architecture.area_mm2 * COST_PER_MM2_USD + PACKAGE_COST_USD

    throughput_tops = throughput_ops_s / 1e12
    bottleneck = max(
        (("compute", compute_s), ("memory", memory_s), ("interconnect", interconnect_s)),
        key=lambda item: item[1],
    )[0]

    metrics = Metrics(
        compute_ms=compute_s * 1e3,
        memory_ms=memory_s * 1e3,
        interconnect_ms=interconnect_s * 1e3,
        dependency_ms=dependency_s * 1e3,
        latency_ms=latency_s * 1e3,
        throughput_tops=throughput_tops,
        energy_j=energy_j,
        average_power_w=average_power_w,
        area_mm2=architecture.area_mm2,
        cost_usd=cost_usd,
        perf_per_w_tops=throughput_tops / average_power_w,
        perf_per_dollar_tops=throughput_tops / cost_usd,
        peak_utilization=throughput_ops_s / architecture.peak_ops_s,
        bottleneck=bottleneck,
    )
    if not all(
        isfinite(value)
        for value in (
            metrics.compute_ms,
            metrics.memory_ms,
            metrics.interconnect_ms,
            metrics.dependency_ms,
            metrics.latency_ms,
            metrics.throughput_tops,
            metrics.energy_j,
            metrics.average_power_w,
            metrics.cost_usd,
            metrics.perf_per_w_tops,
            metrics.perf_per_dollar_tops,
            metrics.peak_utilization,
        )
    ):
        raise ValueError(f"non-finite metric for {workload.id}/{architecture.id}")
    return metrics


def build_payload() -> dict:
    results: list[Result] = []
    frontier: dict[str, list[str]] = {}

    for workload in WORKLOADS:
        workload_results = [
            Result(
                workload_id=workload.id,
                architecture_id=architecture.id,
                metrics=simulate(workload, architecture),
            )
            for architecture in ARCHITECTURES
        ]
        frontier_results = pareto_frontier(workload_results)
        frontier_ids = {result.architecture_id for result in frontier_results}
        frontier[workload.id] = sorted(frontier_ids)
        results.extend(
            replace(result, pareto=result.architecture_id in frontier_ids)
            for result in workload_results
        )

    appearances = Counter(
        result.architecture_id for result in results if result.pareto
    )
    multi_workload = sorted(
        architecture_id for architecture_id, count in appearances.items() if count >= 2
    )
    baseline_frontier = sorted(
        architecture_id
        for architecture_id in appearances
        if architecture_id.startswith(("cpu_", "gpu_", "npu_"))
    )

    best_by_workload: dict[str, dict[str, str]] = {}
    for workload in WORKLOADS:
        subset = [result for result in results if result.workload_id == workload.id]
        best_by_workload[workload.id] = {
            "latency": min(subset, key=lambda result: result.metrics.latency_ms).architecture_id,
            "energy": min(subset, key=lambda result: result.metrics.energy_j).architecture_id,
            "cost": min(subset, key=lambda result: result.metrics.cost_usd).architecture_id,
            "perf_per_w": max(
                subset, key=lambda result: result.metrics.perf_per_w_tops
            ).architecture_id,
            "perf_per_dollar": max(
                subset, key=lambda result: result.metrics.perf_per_dollar_tops
            ).architecture_id,
        }

    return {
        "metadata": {
            "model": "analytical roofline + mapping overhead",
            "model_version": "0.1.0",
            "reference_node_nm": REFERENCE_NODE_NM,
            "reference_clock_ghz": REFERENCE_CLOCK_GHZ,
            "cost_per_mm2_usd": COST_PER_MM2_USD,
            "package_cost_usd": PACKAGE_COST_USD,
            "design_space_size": cartesian_size(),
            "evaluated_candidates": len(ARCHITECTURES),
            "workloads": len(WORKLOADS),
            "experiments": len(results),
            "disclaimer": (
                "Analytical screening only. These are assumptions, not silicon "
                "measurements; iso-accuracy, RTL, and FPGA validation are required "
                "before any architecture claim."
            ),
        },
        "axes": {axis: list(AXES[axis]) for axis in AXIS_ORDER},
        "workloads": [asdict(workload) for workload in WORKLOADS],
        "architectures": [asdict(architecture) for architecture in ARCHITECTURES],
        "results": [
            {
                "workload_id": result.workload_id,
                "architecture_id": result.architecture_id,
                "family": next(
                    architecture.family
                    for architecture in ARCHITECTURES
                    if architecture.id == result.architecture_id
                ),
                "pareto": result.pareto,
                "metrics": asdict(result.metrics),
            }
            for result in results
        ],
        "frontier": frontier,
        "summary": {
            "pareto_appearances": dict(sorted(appearances.items())),
            "multi_workload_frontier": multi_workload,
            "baseline_frontier": baseline_frontier,
            "best_by_workload": best_by_workload,
        },
    }
