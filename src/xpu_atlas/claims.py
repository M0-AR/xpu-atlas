"""Validate the claim ledger and compute evidence-audit statistics."""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

import yaml

from .io_utils import DATA, RESULTS, ensure_dirs, read_json, write_json

CLAIMS_PATH = DATA / "claims.yaml"
OUTPUT_PATH = RESULTS / "evidence_audit.json"

VALID_GRADES = {"E1", "E2", "E3", "E0"}
VALID_STATUS = {"supported", "conflicting", "unverified", "refuted"}
VALID_LIFECYCLE = {
    "general-purpose",
    "absorbed",
    "integrated",
    "commercial",
    "research",
    "emerging",
    "embedded",
}
VALID_SOURCE_TYPES = {
    "primary",
    "peer_reviewed",
    "press",
    "encyclopedia",
    "dataset",
    "standard",
}


class LedgerError(ValueError):
    """Raised when the claim ledger violates its schema."""


def load_ledger(path=CLAIMS_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        ledger = yaml.safe_load(handle)
    validate_ledger(ledger)
    return ledger


def validate_ledger(ledger: dict[str, Any]) -> None:
    if not isinstance(ledger, dict):
        raise LedgerError("ledger root must be a mapping")
    for key in ("metadata", "sources", "paradigms"):
        if key not in ledger:
            raise LedgerError(f"missing top-level key: {key}")

    sources = ledger["sources"]
    if not isinstance(sources, list) or len(sources) < 10:
        raise LedgerError("at least 10 sources are required")
    source_ids: set[str] = set()
    for source in sources:
        for field in ("id", "title", "publisher", "url", "type", "retrieved", "grade"):
            if field not in source:
                raise LedgerError(f"source missing {field}: {source}")
        if source["id"] in source_ids:
            raise LedgerError(f"duplicate source id: {source['id']}")
        if source["type"] not in VALID_SOURCE_TYPES:
            raise LedgerError(f"invalid source type: {source['type']}")
        if source["grade"] not in VALID_GRADES:
            raise LedgerError(f"invalid source grade: {source['grade']}")
        if not str(source["url"]).startswith("http"):
            raise LedgerError(f"source URL must be absolute: {source['url']}")
        source_ids.add(source["id"])

    paradigms = ledger["paradigms"]
    if not isinstance(paradigms, list) or len(paradigms) < 20:
        raise LedgerError("at least 20 paradigms are required")
    paradigm_ids: set[str] = set()
    claim_ids: set[str] = set()
    for paradigm in paradigms:
        for field in ("id", "name", "abbreviation", "year", "lifecycle", "claims"):
            if field not in paradigm:
                raise LedgerError(f"paradigm missing {field}: {paradigm}")
        if paradigm["id"] in paradigm_ids:
            raise LedgerError(f"duplicate paradigm id: {paradigm['id']}")
        paradigm_ids.add(paradigm["id"])
        if paradigm["lifecycle"] not in VALID_LIFECYCLE:
            raise LedgerError(f"invalid lifecycle: {paradigm['lifecycle']}")
        if not paradigm["claims"]:
            raise LedgerError(f"paradigm {paradigm['id']} has no claims")
        for claim in paradigm["claims"]:
            for field in ("id", "statement", "status", "grade", "sources"):
                if field not in claim:
                    raise LedgerError(f"claim missing {field}: {claim}")
            if claim["id"] in claim_ids:
                raise LedgerError(f"duplicate claim id: {claim['id']}")
            claim_ids.add(claim["id"])
            if claim["status"] not in VALID_STATUS:
                raise LedgerError(f"invalid status: {claim['status']}")
            if claim["grade"] not in VALID_GRADES:
                raise LedgerError(f"invalid grade: {claim['grade']}")
            if not claim["sources"]:
                raise LedgerError(f"claim {claim['id']} has no sources")
            missing = [ref for ref in claim["sources"] if ref not in source_ids]
            if missing:
                raise LedgerError(f"claim {claim['id']} references unknown sources: {missing}")


def _era(year: int) -> str:
    if year < 2015:
        return "pre-2015"
    if year <= 2020:
        return "2015-2020"
    return "2021-2026"


def chi2_2x2(a: int, b: int, c: int, d: int) -> tuple[float, float]:
    """Yates-corrected chi-square and p-value for a 2x2 table."""
    n = a + b + c + d
    denominator = (a + b) * (c + d) * (a + c) * (b + d)
    if denominator == 0 or n == 0:
        return 0.0, 1.0
    numerator = n * (abs(a * d - b * c) - n / 2.0) ** 2
    statistic = max(numerator / denominator, 0.0)
    p_value = math.erfc(math.sqrt(statistic / 2.0))
    return statistic, p_value


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return 0.0, 0.0
    p = successes / total
    denominator = 1.0 + z * z / total
    centre = (p + z * z / (2.0 * total)) / denominator
    half = z * math.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total)) / denominator
    return max(0.0, centre - half), min(1.0, centre + half)


def compute_audit(ledger: dict[str, Any]) -> dict[str, Any]:
    claims = [claim for paradigm in ledger["paradigms"] for claim in paradigm["claims"]]
    status_counts = Counter(claim["status"] for claim in claims)
    grade_counts = Counter(claim["grade"] for claim in claims)
    total = len(claims)
    supported = status_counts.get("supported", 0)
    low, high = wilson_interval(supported, total)

    by_era: dict[str, dict[str, Any]] = {}
    for era in ("pre-2015", "2015-2020", "2021-2026"):
        era_claims = [
            claim
            for paradigm in ledger["paradigms"]
            if _era(int(paradigm["year"])) == era
            for claim in paradigm["claims"]
        ]
        by_era[era] = {
            "claims": len(era_claims),
            "supported": sum(claim["status"] == "supported" for claim in era_claims),
            "primary": sum(claim["grade"] == "E1" for claim in era_claims),
            "primary_share": (
                sum(claim["grade"] == "E1" for claim in era_claims) / len(era_claims)
                if era_claims
                else 0.0
            ),
        }

    old = [
        claim
        for paradigm in ledger["paradigms"]
        if _era(int(paradigm["year"])) == "pre-2015"
        for claim in paradigm["claims"]
    ]
    new = [
        claim
        for paradigm in ledger["paradigms"]
        if _era(int(paradigm["year"])) != "pre-2015"
        for claim in paradigm["claims"]
    ]
    a = sum(claim["grade"] == "E1" for claim in old)
    b = len(old) - a
    c = sum(claim["grade"] == "E1" for claim in new)
    d = len(new) - c
    chi2, p_value = chi2_2x2(a, b, c, d)
    cramers_v = math.sqrt(chi2 / total) if total else 0.0

    by_paradigm = {}
    for paradigm in ledger["paradigms"]:
        paradigm_claims = paradigm["claims"]
        by_paradigm[paradigm["id"]] = {
            "name": paradigm["name"],
            "abbreviation": paradigm["abbreviation"],
            "year": int(paradigm["year"]),
            "lifecycle": paradigm["lifecycle"],
            "claims": len(paradigm_claims),
            "supported": sum(claim["status"] == "supported" for claim in paradigm_claims),
            "grades": dict(Counter(claim["grade"] for claim in paradigm_claims)),
        }

    conflict_register = [
        {
            "claim_id": claim["id"],
            "statement": claim["statement"],
            "status": claim["status"],
            "grade": claim["grade"],
            "note": claim.get("note", ""),
            "sources": claim["sources"],
        }
        for claim in claims
        if claim["status"] in {"conflicting", "refuted"}
    ]

    lifecycle_counts = Counter(paradigm["lifecycle"] for paradigm in ledger["paradigms"])
    return {
        "metadata": ledger["metadata"],
        "totals": {
            "paradigms": len(ledger["paradigms"]),
            "claims": total,
            "sources": len(ledger["sources"]),
        },
        "status_counts": dict(status_counts),
        "grade_counts": dict(grade_counts),
        "verification_rate": supported / total if total else 0.0,
        "verification_rate_ci95": [low, high],
        "primary_share": grade_counts.get("E1", 0) / total if total else 0.0,
        "conflict_rate": (
            (status_counts.get("conflicting", 0) + status_counts.get("refuted", 0)) / total
            if total
            else 0.0
        ),
        "unverified_rate": status_counts.get("unverified", 0) / total if total else 0.0,
        "by_era": by_era,
        "era_test": {
            "comparison": "pre-2015 vs 2015+ primary-evidence share",
            "table": {"old_primary": a, "old_non_primary": b, "new_primary": c, "new_non_primary": d},
            "chi2_yates": chi2,
            "p_value": p_value,
            "cramers_v": cramers_v,
        },
        "by_paradigm": by_paradigm,
        "lifecycle_counts": dict(lifecycle_counts),
        "conflict_register": conflict_register,
    }


def main() -> int:
    ensure_dirs()
    ledger = load_ledger()
    audit = compute_audit(ledger)
    write_json(OUTPUT_PATH, audit)
    print(
        f"claims: {audit['totals']['claims']} across {audit['totals']['paradigms']} paradigms; "
        f"supported={audit['status_counts'].get('supported', 0)} "
        f"({audit['verification_rate']:.1%}); "
        f"conflicts={len(audit['conflict_register'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
