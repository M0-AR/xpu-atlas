"""Check that the paper's headline numbers match generated results."""

from __future__ import annotations

import re
import sys
from .claims import load_ledger
from .io_utils import ROOT, RESULTS, read_json

README_PATH = ROOT / "README.md"
FIGURES = ROOT / "figures"
DOCS = ROOT / "docs"

FORBIDDEN = [
    "100% supported",
    "all 64 claims are supported",
    "proves that",
    "guarantees",
    "risk-free",
    "always outperforms",
    "never fails",
]


def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace(",", "")
    text = re.sub(r"\s+", " ", text)
    return text


def main() -> int:
    if not README_PATH.exists():
        print("paper-check: README.md missing", file=sys.stderr)
        return 1
    paper = normalize(README_PATH.read_text(encoding="utf-8"))
    summary = read_json(RESULTS / "summary.json")
    headline = summary["headline"]

    required = {
        "claims_total": headline["claims_total"],
        "paradigms_total": headline["paradigms_total"],
        "sources_total": headline["sources_total"],
        "verification_rate": headline["verification_rate"],
        "verification_ci": headline["verification_ci"],
        "primary_share": headline["primary_share"],
        "era_p": headline["era_chi2_p"],
        "max_inflation": headline["max_inflation"],
        "absorption_share": headline["absorption_share"],
        "serial_ops": headline["serial_ops_per_s"],
        "vector_ratio": headline["vector_to_serial_ratio"],
        "matmul_gflops": headline["matmul_peak_gflops"],
        "matmul_ratio": headline["matmul_to_serial_ratio"],
        "thread_efficiency": headline["thread_efficiency_8"],
        "integrators": headline["integrators_cagr"],
        "foundry": headline["foundry_cagr"],
        "legacy": headline["legacy_cpu_cagr"],
        "mobile": headline["mobile_cagr"],
    }
    extra = [
        "187.8x",
        "129.5x",
        "51.6x",
        "1.18b",
        "4.1",
        "30.5",
        "111.7",
        "214.8",
        "2.29x",
        "0.97x",
        "-55.7%",
        "-47.1%",
        "$185",
        "1,760",
        "1,716",
        "8 of 20",
    ]

    missing = []
    for label, value in required.items():
        token = normalize(str(value))
        if token not in paper:
            missing.append(f"{label}={value}")
    for value in extra:
        if normalize(value) not in paper:
            missing.append(value)

    forbidden_hits = [phrase for phrase in FORBIDDEN if normalize(phrase) in paper]

    figure_refs = re.findall(r"!\[[^\]]*\]\((figures/[^)]+)\)", README_PATH.read_text(encoding="utf-8"))
    missing_figures = [ref for ref in figure_refs if not (ROOT / ref).exists()]
    if len(figure_refs) < 5:
        missing_figures.append(f"only {len(figure_refs)} figure references")

    docs_missing = [
        str(path.relative_to(ROOT))
        for path in (DOCS / "EVIDENCE.md", DOCS / "RESULTS.md")
        if not path.exists()
    ]

    try:
        ledger = load_ledger()
    except Exception as exc:  # noqa: BLE001 - surface schema failures to the caller
        print(f"paper-check: ledger invalid: {exc}", file=sys.stderr)
        return 1

    claim_count = sum(len(paradigm["claims"]) for paradigm in ledger["paradigms"])
    if claim_count != int(headline["claims_total"]):
        missing.append(
            f"ledger claim count {claim_count} != headline {headline['claims_total']}"
        )

    if missing or forbidden_hits or missing_figures or docs_missing:
        if missing:
            print("paper-check: missing or stale tokens:", file=sys.stderr)
            for item in missing:
                print(f"  - {item}", file=sys.stderr)
        if forbidden_hits:
            print("paper-check: forbidden overclaims:", file=sys.stderr)
            for item in forbidden_hits:
                print(f"  - {item}", file=sys.stderr)
        if missing_figures:
            print("paper-check: missing figures:", file=sys.stderr)
            for item in missing_figures:
                print(f"  - {item}", file=sys.stderr)
        if docs_missing:
            print("paper-check: missing generated docs:", file=sys.stderr)
            for item in docs_missing:
                print(f"  - {item}", file=sys.stderr)
        return 1

    print(
        f"paper-check: OK ({claim_count} claims, {len(figure_refs)} figures, "
        f"{len(required) + len(extra)} numeric tokens)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
