"""The bounded design-space axes used by the simulator.

The full Cartesian product is reported for scale. Only a small, physically
plausible set of candidates is simulated in this sprint.
"""

from __future__ import annotations

from itertools import product
from math import prod

AXES = {
    "execution_model": (
        "SIMD",
        "SIMT",
        "spatial",
        "event-driven",
        "stochastic",
        "near-memory",
        "photonic",
    ),
    "memory_hierarchy": (
        "cache+HBM",
        "HBM+SRAM",
        "SRAM-only",
        "compute-in-memory",
        "optical",
    ),
    "dataflow": (
        "control",
        "weight-stationary",
        "output-stationary",
        "event",
        "sampling",
    ),
    "interconnect": (
        "mesh",
        "NoC",
        "all-to-all",
        "optical",
    ),
    "numeric_format": (
        "int8",
        "fp8",
        "mixed",
        "analog",
    ),
    "programming_model": (
        "threads",
        "graph",
        "dataflow",
        "event-graph",
        "probabilistic",
    ),
}

AXIS_ORDER = tuple(AXES)


def cartesian_size() -> int:
    return prod(len(values) for values in AXES.values())


def enumerate_designs():
    return product(*(AXES[axis] for axis in AXIS_ORDER))
