"""Pareto helpers for multi-objective screening."""

from __future__ import annotations

from .model import Result

OBJECTIVES = ("latency_ms", "energy_j")


def dominates(left: Result, right: Result) -> bool:
    left_metrics = left.metrics
    right_metrics = right.metrics
    no_worse = all(
        getattr(left_metrics, objective) <= getattr(right_metrics, objective)
        for objective in OBJECTIVES
    )
    strictly_better = any(
        getattr(left_metrics, objective) < getattr(right_metrics, objective)
        for objective in OBJECTIVES
    )
    return no_worse and strictly_better


def pareto_frontier(results: list[Result]) -> list[Result]:
    return [
        candidate
        for candidate in results
        if not any(
            dominates(other, candidate) for other in results if other is not candidate
        )
    ]
