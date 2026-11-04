"""Capture reproducible live-data snapshots from public APIs.

Sources
-------
OpenAlex   : yearly publication counts for 14 processor concepts (2000-2025).
Wikimedia  : monthly English-Wikipedia pageviews for 12 articles (2021-2026).
Yahoo      : monthly adjusted close prices for 8 semiconductor tickers (5y).

The default `make all` pipeline runs *offline* against committed snapshots.
`make fetch` refreshes every snapshot and records source URLs, retrieval
timestamps and SHA-256 digests in data/snapshots/capture_manifest.json.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .io_utils import SNAPSHOTS, ensure_dirs, sha256_file, utc_now_iso, write_json

USER_AGENT = "XPU-Atlas/0.1 (academic reproducibility study)"

OPENALEX_TERMS: dict[str, str] = {
    "cpu": "central processing unit",
    "gpu": "graphics processing unit",
    "tpu": "tensor processing unit",
    "npu": "neural processing unit",
    "dpu": "data processing unit",
    "ppu": "physics processing unit",
    "wse": "wafer-scale integration",
    "neuromorphic": "neuromorphic computing",
    "quantum": "quantum computing",
    "photonic": "photonic computing",
    "fpga": "field-programmable gate array",
    "asic": "application-specific integrated circuit",
    "mcu": "microcontroller",
    "isp": "image signal processor",
}

WIKI_ARTICLES: dict[str, str] = {
    "cpu": "Central_processing_unit",
    "gpu": "Graphics_processing_unit",
    "tpu": "Tensor_Processing_Unit",
    "npu": "Neural_processing_unit",
    "dpu": "Data_processing_unit",
    "quantum": "Quantum_computing",
    "neuromorphic": "Neuromorphic_computing",
    "fpga": "Field-programmable_gate_array",
    "asic": "Application-specific_integrated_circuit",
    "mcu": "Microcontroller",
    "wse": "Wafer-scale_integration",
    "photonic": "Optical_computing",
}

TICKERS: list[str] = ["NVDA", "AMD", "GOOGL", "INTC", "QCOM", "TSM", "ARM", "CBRS"]

OPENALEX_START = "2000-01-01"
OPENALEX_END = "2025-12-31"
WIKI_START = "2021010100"
WIKI_END = "2026103100"
YAHOO_RANGE = "5y"
YAHOO_INTERVAL = "1mo"


class FetchError(RuntimeError):
    pass


def _http_json(url: str, retries: int = 3, timeout: int = 60) -> Any:
    """GET a JSON document with bounded exponential backoff."""
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
    raise FetchError(f"failed after {retries} attempts: {url} :: {last_error}")


def _openalex_query(query: str, quoted: bool) -> dict[str, Any]:
    search_term = f'"{query}"' if quoted else query
    filters = (
        f"title_and_abstract.search:{search_term},"
        f"from_publication_date:{OPENALEX_START},"
        f"to_publication_date:{OPENALEX_END}"
    )
    params = urllib.parse.urlencode({"filter": filters, "group_by": "publication_year"})
    url = f"https://api.openalex.org/works?{params.replace('+', '%20')}"
    raw = _http_json(url)
    counts = {
        str(group["key"]): int(group["count"])
        for group in raw.get("group_by", [])
        if str(group.get("key", "")).isdigit()
    }
    return {
        "url": url,
        "counts": dict(sorted(counts.items())),
        "total": int(raw.get("meta", {}).get("count", sum(counts.values()))),
    }


def fetch_openalex() -> dict[str, Any]:
    """Capture both phrase-quoted and unquoted counts.

    The unquoted `search` filter tokenises the query; the quoted form asks
    OpenAlex for the exact phrase. The ratio is a direct measure of lexical
    inflation caused by homonyms (ISP, MCU, TPU, NPU, DPU, ...).
    """
    payload: dict[str, Any] = {"source": "OpenAlex", "retrieved_at": utc_now_iso(), "terms": {}}
    for term_id, query in OPENALEX_TERMS.items():
        quoted = _openalex_query(query, quoted=True)
        time.sleep(0.25)
        unquoted = _openalex_query(query, quoted=False)
        payload["terms"][term_id] = {
            "query": query,
            "url": quoted["url"],
            "url_unquoted": unquoted["url"],
            "counts": quoted["counts"],
            "total": quoted["total"],
            "counts_unquoted": unquoted["counts"],
            "total_unquoted": unquoted["total"],
            "inflation_factor": round(unquoted["total"] / max(quoted["total"], 1), 3),
        }
        print(
            f"[openalex] {term_id:12s} quoted={quoted['total']:7d} "
            f"unquoted={unquoted['total']:8d} inflation={payload['terms'][term_id]['inflation_factor']:.1f}x",
            file=sys.stderr,
        )
        time.sleep(0.25)
    return payload


def fetch_wikimedia() -> dict[str, Any]:
    payload: dict[str, Any] = {"source": "Wikimedia Pageviews API", "retrieved_at": utc_now_iso(), "articles": {}}
    for term_id, article in WIKI_ARTICLES.items():
        url = (
            "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
            f"en.wikipedia/all-access/all-agents/{article}/monthly/{WIKI_START}/{WIKI_END}"
        )
        raw = _http_json(url)
        series = {
            str(item["timestamp"])[:6]: int(item["views"])
            for item in raw.get("items", [])
        }
        payload["articles"][term_id] = {
            "article": article,
            "url": url,
            "views": dict(sorted(series.items())),
        }
        print(f"[wikimedia] {term_id:12s} months={len(series)}", file=sys.stderr)
        time.sleep(0.15)
    return payload


def fetch_yahoo() -> dict[str, Any]:
    payload: dict[str, Any] = {"source": "Yahoo Finance chart API", "retrieved_at": utc_now_iso(), "tickers": {}}
    for ticker in TICKERS:
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            f"?range={YAHOO_RANGE}&interval={YAHOO_INTERVAL}"
        )
        raw = _http_json(url)
        result = (raw.get("chart", {}).get("result") or [None])[0]
        if not result:
            raise FetchError(f"empty Yahoo result for {ticker}")
        timestamps = result.get("timestamp", [])
        quote = (result.get("indicators", {}).get("quote") or [{}])[0]
        adjclose = (result.get("indicators", {}).get("adjclose") or [{}])[0].get("adjclose")
        closes = adjclose if adjclose else quote.get("close", [])
        series: dict[str, float] = {}
        for stamp, close in zip(timestamps, closes):
            if close is None:
                continue
            month = time.strftime("%Y-%m", time.gmtime(stamp))
            series[month] = float(close)
        payload["tickers"][ticker] = {
            "url": url,
            "currency": result.get("meta", {}).get("currency"),
            "exchange": result.get("meta", {}).get("exchangeName"),
            "prices": dict(sorted(series.items())),
        }
        print(f"[yahoo] {ticker:6s} months={len(series)}", file=sys.stderr)
        time.sleep(0.3)
    return payload


def build_manifest() -> dict[str, Any]:
    files = [
        "openalex_counts.json",
        "wikimedia_pageviews.json",
        "yahoo_prices.json",
    ]
    manifest: dict[str, Any] = {"created_at": utc_now_iso(), "files": {}}
    for name in files:
        path = SNAPSHOTS / name
        if path.exists():
            manifest["files"][name] = {
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="do not touch the network; verify committed snapshots instead",
    )
    parser.add_argument(
        "--only",
        choices=["openalex", "wikimedia", "yahoo"],
        help="refresh a single source",
    )
    args = parser.parse_args()

    ensure_dirs()
    expected = [
        SNAPSHOTS / "openalex_counts.json",
        SNAPSHOTS / "wikimedia_pageviews.json",
        SNAPSHOTS / "yahoo_prices.json",
    ]

    if args.offline:
        missing = [str(path) for path in expected if not path.exists()]
        if missing:
            print(f"offline mode: missing snapshots: {missing}", file=sys.stderr)
            return 1
        manifest = build_manifest()
        write_json(SNAPSHOTS / "capture_manifest.json", manifest)
        print("offline mode: committed snapshots present and hashed", file=sys.stderr)
        return 0

    jobs = {
        "openalex": (fetch_openalex, "openalex_counts.json"),
        "wikimedia": (fetch_wikimedia, "wikimedia_pageviews.json"),
        "yahoo": (fetch_yahoo, "yahoo_prices.json"),
    }
    selected = [args.only] if args.only else list(jobs)
    for name in selected:
        fetcher, filename = jobs[name]
        print(f"refreshing {name} ...", file=sys.stderr)
        write_json(SNAPSHOTS / filename, fetcher())

    manifest = build_manifest()
    write_json(SNAPSHOTS / "capture_manifest.json", manifest)
    print(json.dumps(manifest, indent=2), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
