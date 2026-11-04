"""CLI entry point for the analytical design-space simulator."""

from __future__ import annotations

import argparse
from pathlib import Path

from xpu_atlas.io_utils import DOCS, FIGURES, RESULTS, ensure_dirs, write_csv, write_json, write_text

from .engine import build_payload
from .report import CSV_FIELDS, plot_design_space, render_markdown, result_rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Screen hypothetical XPU architectures under explicit assumptions."
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=RESULTS / "simulation.json",
        help="path for the full simulation payload",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=RESULTS / "simulation.csv",
        help="path for the per-experiment table",
    )
    parser.add_argument(
        "--md",
        type=Path,
        default=DOCS / "SIMULATION.md",
        help="path for the generated report",
    )
    parser.add_argument(
        "--figure",
        type=Path,
        default=FIGURES / "fig7_design_space.png",
        help="path for the Pareto figure",
    )
    args = parser.parse_args(argv)

    ensure_dirs()
    payload = build_payload()
    write_json(args.json, payload)
    write_csv(args.csv, result_rows(payload), CSV_FIELDS)
    write_text(args.md, render_markdown(payload))
    plot_design_space(payload, args.figure)

    metadata = payload["metadata"]
    print(
        f"sim: {metadata['experiments']} experiments "
        f"({metadata['evaluated_candidates']} candidates x {metadata['workloads']} workloads)"
    )
    print(f"sim: wrote {args.json}, {args.csv}, {args.md}, {args.figure}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
