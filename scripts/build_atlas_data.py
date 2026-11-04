#!/usr/bin/env python3
"""Build the browser data bundle for preview.html from the frozen ledger and results."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def main() -> None:
    ledger = yaml.safe_load((ROOT / "data" / "claims.yaml").read_text(encoding="utf-8"))
    summary = json.loads((ROOT / "results" / "summary.json").read_text(encoding="utf-8"))
    analysis = json.loads((ROOT / "results" / "analysis.json").read_text(encoding="utf-8"))

    sources = {
        s["id"]: {
            "title": s["title"],
            "publisher": s["publisher"],
            "grade": s["grade"],
            "type": s["type"],
        }
        for s in ledger["sources"]
    }

    paradigms = []
    claims = []
    for p in ledger["paradigms"]:
        grades: dict[str, int] = {}
        for c in p["claims"]:
            grades[c["grade"]] = grades.get(c["grade"], 0) + 1
            claims.append(
                {
                    "id": c["id"],
                    "paradigm": p["name"],
                    "abbr": p["abbreviation"],
                    "year": p["year"],
                    "lifecycle": p["lifecycle"],
                    "statement": c["statement"],
                    "status": c["status"],
                    "grade": c["grade"],
                    "sources": c["sources"],
                    "note": c.get("note", ""),
                }
            )
        supported = sum(1 for c in p["claims"] if c["status"] == "supported")
        primary = sum(1 for c in p["claims"] if c["grade"] == "E1")
        paradigms.append(
            {
                "id": p["id"],
                "abbr": p["abbreviation"],
                "name": p["name"],
                "year": p["year"],
                "lifecycle": p["lifecycle"],
                "claims": len(p["claims"]),
                "supported": supported,
                "primary": primary,
                "grades": grades,
                "support_rate": supported / len(p["claims"]),
            }
        )

    terms = []
    for key, t in analysis["bibliometrics"]["terms"].items():
        terms.append(
            {
                "key": key,
                "label": t["label"],
                "quoted": t["total_quoted"],
                "unquoted": t["total_unquoted"],
                "inflation": t["inflation_factor"],
                "cagr": t.get("cagr_2021_2025"),
                "r2": t.get("r_squared"),
                "doubling": t.get("doubling_years"),
                "fit": t.get("fit_quality"),
                "reliable": t.get("reliable", False),
            }
        )
    terms.sort(key=lambda row: row["inflation"], reverse=True)

    attention = []
    for key, a in analysis["attention"]["articles"].items():
        attention.append(
            {
                "key": key,
                "label": a["label"],
                "mean2021": a["mean_2021"],
                "mean2025": a["mean_2025"],
                "change": a["change_2021_2025"],
                "cagr": a["cagr_2021_2025"],
                "peak": a["peak_views"],
            }
        )
    attention.sort(key=lambda row: row["change"], reverse=True)

    markets = []
    for ticker, m in analysis["markets"]["tickers"].items():
        markets.append(
            {
                "ticker": ticker,
                "label": m["label"],
                "cagr": m["cagr"],
                "total": m["total_return"],
                "vol": m["annualized_volatility"],
                "drawdown": m["max_drawdown"],
                "months": m["n_months"],
                "first": m["first_price"],
                "last": m["last_price"],
                "first_month": m["first_month"],
                "last_month": m["last_month"],
            }
        )
    markets.sort(key=lambda row: row["cagr"], reverse=True)

    bench = analysis["bench"]
    data = {
        "meta": {
            "title": "XPU-Atlas",
            "version": ledger["metadata"]["version"],
            "compiled": ledger["metadata"]["compiled"],
            "snapshot": summary.get("generated_at"),
        },
        "headline": summary["headline"],
        "evidence": {
            "claims": analysis["evidence"]["totals"]["claims"],
            "paradigms": analysis["evidence"]["totals"]["paradigms"],
            "sources": analysis["evidence"]["totals"]["sources"],
            "supported": sum(1 for c in claims if c["status"] == "supported"),
            "by_era": analysis["evidence"]["by_era"],
        },
        "paradigms": paradigms,
        "claims": claims,
        "sources": sources,
        "terms": terms,
        "attention": attention,
        "markets": markets,
        "market_groups": analysis["markets"]["group_cagr"],
        "bench": {
            "platform": bench["platform"],
            "serial_ops": bench["serial_ops_per_s"],
            "vector_ratio": bench["vector_to_serial_ratio"],
            "matmul_gflops": bench["matmul_peak_gflops"],
            "matmul_ratio": bench["matmul_to_serial_ratio"],
            "thread_efficiency": bench["thread_efficiency_8"],
            "vector_speedup": bench["vector_speedup_max"],
            "serial": bench["raw"]["serial"],
            "vector": bench["raw"]["vector"],
            "threads": bench["raw"]["threads"],
            "matmul": bench["raw"]["matmul"],
        },
    }

    ASSETS.mkdir(exist_ok=True)
    out = ASSETS / "atlas-data.js"
    out.write_text(
        "/* Generated from data/claims.yaml and results/. Do not edit by hand. */\n"
        + "window.XPU_DATA = "
        + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
