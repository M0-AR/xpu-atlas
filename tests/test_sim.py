import csv
import math

from sim.architectures import ARCHITECTURES, ARCHITECTURE_BY_ID
from sim.design_space import AXES, cartesian_size
from sim.engine import build_payload, simulate
from sim.pareto import pareto_frontier
from sim.workloads import WORKLOADS
from xpu_atlas.io_utils import DOCS, FIGURES, RESULTS, read_json


def test_design_space_and_candidate_shape():
    assert len(WORKLOADS) == 3
    assert len(ARCHITECTURES) == 13
    assert cartesian_size() == 14_000
    assert len(ARCHITECTURE_BY_ID) == len(ARCHITECTURES)
    for architecture in ARCHITECTURES:
        assert architecture.execution in AXES["execution_model"]
        assert architecture.memory in AXES["memory_hierarchy"]
        assert architecture.dataflow in AXES["dataflow"]
        assert architecture.interconnect in AXES["interconnect"]
        assert architecture.numeric in AXES["numeric_format"]
        assert architecture.programming in AXES["programming_model"]
        assert set(architecture.utilization) == {workload.id for workload in WORKLOADS}


def test_simulation_is_deterministic_and_finite():
    workload = WORKLOADS[0]
    architecture = ARCHITECTURES[0]
    first = simulate(workload, architecture)
    second = simulate(workload, architecture)
    assert first == second
    for value in (
        first.latency_ms,
        first.throughput_tops,
        first.energy_j,
        first.average_power_w,
        first.cost_usd,
        first.perf_per_w_tops,
        first.perf_per_dollar_tops,
    ):
        assert math.isfinite(value)
        assert value > 0
    assert first.bottleneck in {"compute", "memory", "interconnect"}


def test_payload_has_frontier_per_workload():
    payload = build_payload()
    assert payload["metadata"]["experiments"] == 39
    assert payload["metadata"]["design_space_size"] == 14_000
    assert len(payload["results"]) == 39
    for workload in WORKLOADS:
        frontier = payload["frontier"][workload.id]
        assert frontier
        assert all(item in ARCHITECTURE_BY_ID for item in frontier)
        rows = [
            result
            for result in payload["results"]
            if result["workload_id"] == workload.id
        ]
        assert sum(result["pareto"] for result in rows) == len(frontier)
    assert "sparse_near_memory" in payload["frontier"]["sparse_event_inference"]
    assert "attention_near_memory" in payload["frontier"]["memory_bound_attention"]
    assert "npu_systolic" in payload["frontier"]["memory_bound_attention"]


def test_pareto_helper_removes_dominated_point():
    from sim.model import Metrics, Result

    def result(architecture_id, latency, energy):
        return Result(
            workload_id="test",
            architecture_id=architecture_id,
            metrics=Metrics(
                compute_ms=latency,
                memory_ms=1.0,
                interconnect_ms=1.0,
                dependency_ms=0.0,
                latency_ms=latency,
                throughput_tops=1.0,
                energy_j=energy,
                average_power_w=1.0,
                area_mm2=1.0,
                cost_usd=1.0,
                perf_per_w_tops=1.0,
                perf_per_dollar_tops=1.0,
                peak_utilization=1.0,
                bottleneck="compute",
            ),
        )

    frontier = pareto_frontier(
        [result("good", 1.0, 1.0), result("dominated", 2.0, 2.0)]
    )
    assert [item.architecture_id for item in frontier] == ["good"]


def test_generated_simulation_outputs_are_present():
    payload = read_json(RESULTS / "simulation.json")
    assert payload["metadata"]["experiments"] == 39

    with (RESULTS / "simulation.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 39
    assert {"workload_id", "architecture_id", "latency_ms", "energy_j"} <= set(rows[0])

    report = (DOCS / "SIMULATION.md").read_text(encoding="utf-8")
    assert "Design-Space Simulation" in report
    assert "does not measure silicon" in report
    assert "Pareto" in report
    for phrase in ("proves that", "guarantees", "always outperforms", "never fails"):
        assert phrase not in report.lower()

    figure = FIGURES / "fig7_design_space.png"
    assert figure.exists()
    assert figure.stat().st_size > 10_000
