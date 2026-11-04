"""Statistical analyses over committed live-data snapshots.

All inputs are frozen JSON snapshots captured from public APIs, so the
analysis is deterministic and offline-reproducible. `make fetch` refreshes
the snapshots; `make analyze` recomputes every table and headline number.
"""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any, Iterable

from .io_utils import RESULTS, SNAPSHOTS, ensure_dirs, read_json, write_json

EVIDENCE_PATH = RESULTS / "evidence_audit.json"
OPENALEX_PATH = SNAPSHOTS / "openalex_counts.json"
WIKIMEDIA_PATH = SNAPSHOTS / "wikimedia_pageviews.json"
YAHOO_PATH = SNAPSHOTS / "yahoo_prices.json"
BENCH_PATH = RESULTS / "bench.json"
ANALYSIS_PATH = RESULTS / "analysis.json"
SUMMARY_PATH = RESULTS / "summary.json"

TERM_LABELS = {
    "cpu": "CPU",
    "gpu": "GPU",
    "tpu": "TPU",
    "npu": "NPU",
    "dpu": "DPU",
    "ppu": "PPU",
    "wse": "WSE",
    "neuromorphic": "Neuromorphic",
    "quantum": "Quantum",
    "photonic": "Photonic",
    "fpga": "FPGA",
    "asic": "ASIC",
    "mcu": "MCU",
    "isp": "ISP",
}

TICKER_LABELS = {
    "NVDA": "NVIDIA",
    "AMD": "AMD",
    "GOOGL": "Alphabet",
    "INTC": "Intel",
    "QCOM": "Qualcomm",
    "TSM": "TSMC",
    "ARM": "Arm",
    "CBRS": "Cerebras",
}

ATTENTION_MARKET_PAIRS = [
    ("gpu", "NVDA"),
    ("cpu", "INTC"),
    ("cpu", "AMD"),
    ("tpu", "GOOGL"),
    ("npu", "QCOM"),
]


def cagr(start: float, end: float, years: float) -> float:
    if start <= 0 or years <= 0:
        return float("nan")
    return (end / start) ** (1.0 / years) - 1.0


def max_drawdown(values: Iterable[float]) -> float:
    peak = -math.inf
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1.0)
    return worst


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return float("nan")
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = math.sqrt(
        sum((x - mean_x) ** 2 for x in xs) * sum((y - mean_y) ** 2 for y in ys)
    )
    return numerator / denominator if denominator else float("nan")


def rankdata(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    position = 0
    while position < len(order):
        end = position
        while end + 1 < len(order) and values[order[end + 1]] == values[order[position]]:
            end += 1
        average_rank = (position + end) / 2.0 + 1.0
        for index in order[position : end + 1]:
            ranks[index] = average_rank
        position = end + 1
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float:
    return pearson(rankdata(xs), rankdata(ys))


def linear_fit(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    sxx = sum((x - mean_x) ** 2 for x in xs)
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    slope = sxy / sxx if sxx else float("nan")
    intercept = mean_y - slope * mean_x
    ss_total = sum((y - mean_y) ** 2 for y in ys)
    ss_residual = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r_squared = 1.0 - ss_residual / ss_total if ss_total else float("nan")
    return slope, intercept, r_squared


def exponential_fit(counts: dict[str, int]) -> dict[str, Any]:
    points = [(int(year), count) for year, count in counts.items() if count > 0]
    points.sort()
    if len(points) < 5:
        return {
            "doubling_years": None,
            "r_squared": None,
            "fit_quality": "insufficient",
            "annual_growth_rate": None,
            "n_years": len(points),
        }
    xs = [float(year) for year, _ in points]
    ys = [math.log(count) for _, count in points]
    slope, _, r_squared = linear_fit(xs, ys)
    doubling = math.log(2) / slope if slope > 0 else None
    if r_squared >= 0.8:
        quality = "good"
    elif r_squared >= 0.6:
        quality = "moderate"
    else:
        quality = "poor"
    return {
        "doubling_years": doubling,
        "r_squared": r_squared,
        "fit_quality": quality,
        "annual_growth_rate": math.exp(slope) - 1.0,
        "n_years": len(points),
    }


def analyze_bibliometrics() -> dict[str, Any]:
    snapshot = read_json(OPENALEX_PATH)
    terms: dict[str, Any] = {}
    for term_id, record in snapshot["terms"].items():
        counts = {int(year): int(count) for year, count in record["counts"].items()}
        unquoted = record.get("counts_unquoted", {})
        first_year = min(counts) if counts else None
        last_year = max(counts) if counts else None
        peak_year = max(counts, key=counts.get) if counts else None
        peak_count = counts.get(peak_year, 0) if peak_year else 0
        c2021 = counts.get(2021)
        c2025 = counts.get(2025)
        recent_share = (
            sum(count for year, count in counts.items() if year >= 2021)
            / sum(counts.values())
            if counts and sum(counts.values())
            else 0.0
        )
        fit = exponential_fit({str(year): count for year, count in counts.items()})
        total = int(record["total"])
        terms[term_id] = {
            "label": TERM_LABELS.get(term_id, term_id),
            "query": record["query"],
            "total_quoted": total,
            "total_unquoted": int(record.get("total_unquoted", total)),
            "inflation_factor": float(record.get("inflation_factor", 1.0)),
            "first_year": first_year,
            "last_year": last_year,
            "peak_year": peak_year,
            "peak_count": peak_count,
            "fit_quality": fit.get("fit_quality"),
            "cagr_2015_2025": (
                cagr(counts[2015], c2025, 10) if counts.get(2015) and c2025 else None
            ),
            "cagr_2021_2025": (
                cagr(c2021, c2025, 4) if c2021 and c2025 else None
            ),
            "recent_5y_share": recent_share,
            "reliable": total >= 100 and len(counts) >= 8,
            **fit,
        }
    reliable = {k: v for k, v in terms.items() if v["reliable"]}
    growth_values = [v["cagr_2021_2025"] for v in reliable.values() if v["cagr_2021_2025"] is not None]
    inflation_values = [v["inflation_factor"] for v in terms.values()]
    return {
        "source": snapshot.get("source"),
        "retrieved_at": snapshot.get("retrieved_at"),
        "terms": terms,
        "summary": {
            "n_terms": len(terms),
            "n_reliable": len(reliable),
            "median_cagr_2021_2025": statistics.median(growth_values) if growth_values else None,
            "max_cagr_2021_2025": max(growth_values) if growth_values else None,
            "median_inflation": statistics.median(inflation_values),
            "max_inflation": max(inflation_values),
            "terms_with_10x_inflation": sorted(
                [k for k, v in terms.items() if v["inflation_factor"] >= 10.0]
            ),
            "terms_with_100x_inflation": sorted(
                [k for k, v in terms.items() if v["inflation_factor"] >= 100.0]
            ),
        },
    }


def annual_means(values: dict[str, int]) -> dict[str, float]:
    buckets: dict[str, list[int]] = defaultdict(list)
    for timestamp, views in values.items():
        buckets[timestamp[:4]].append(int(views))
    return {year: sum(monthly) / len(monthly) for year, monthly in sorted(buckets.items())}


def analyze_attention() -> dict[str, Any]:
    snapshot = read_json(WIKIMEDIA_PATH)
    articles: dict[str, Any] = {}
    for term_id, record in snapshot["articles"].items():
        views = {str(ts): int(value) for ts, value in record["views"].items()}
        means = annual_means(views)
        peak_month = max(views, key=views.get) if views else None
        articles[term_id] = {
            "label": TERM_LABELS.get(term_id, term_id),
            "article": record["article"],
            "n_months": len(views),
            "first_month": min(views) if views else None,
            "last_month": max(views) if views else None,
            "mean_2021": means.get("2021"),
            "mean_2025": means.get("2025"),
            "change_2021_2025": (
                (means["2025"] / means["2021"] - 1.0)
                if means.get("2021") and means.get("2025")
                else None
            ),
            "cagr_2021_2025": (
                cagr(means["2021"], means["2025"], 4)
                if means.get("2021") and means.get("2025")
                else None
            ),
            "peak_month": peak_month,
            "peak_views": views.get(peak_month) if peak_month else None,
            "annual_means": means,
        }
    changes = [
        record["change_2021_2025"]
        for record in articles.values()
        if record["change_2021_2025"] is not None
    ]
    return {
        "source": snapshot.get("source"),
        "retrieved_at": snapshot.get("retrieved_at"),
        "articles": articles,
        "summary": {
            "n_articles": len(articles),
            "median_change_2021_2025": statistics.median(changes) if changes else None,
            "n_declining": sum(1 for value in changes if value < 0),
            "n_growing": sum(1 for value in changes if value > 0),
        },
    }


def log_returns(prices: dict[str, float]) -> list[float]:
    ordered = [prices[key] for key in sorted(prices)]
    return [math.log(b / a) for a, b in zip(ordered, ordered[1:]) if a > 0 and b > 0]


def analyze_markets() -> dict[str, Any]:
    snapshot = read_json(YAHOO_PATH)
    tickers: dict[str, Any] = {}
    monthly_returns: dict[str, list[float]] = {}
    for ticker, record in snapshot["tickers"].items():
        prices = {str(month): float(value) for month, value in record["prices"].items()}
        ordered = [prices[key] for key in sorted(prices)]
        months = len(prices)
        years = (months - 1) / 12.0
        returns = log_returns(prices)
        tickers[ticker] = {
            "label": TICKER_LABELS.get(ticker, ticker),
            "currency": record.get("currency"),
            "exchange": record.get("exchange"),
            "n_months": months,
            "first_month": min(prices) if prices else None,
            "last_month": max(prices) if prices else None,
            "first_price": ordered[0] if ordered else None,
            "last_price": ordered[-1] if ordered else None,
            "total_return": ordered[-1] / ordered[0] - 1.0 if ordered else None,
            "cagr": cagr(ordered[0], ordered[-1], years) if ordered and years > 0 else None,
            "annualized_volatility": (
                statistics.stdev(returns) * math.sqrt(12) if len(returns) >= 2 else None
            ),
            "max_drawdown": max_drawdown(ordered) if ordered else None,
        }
        monthly_returns[ticker] = returns

    long_tickers = [ticker for ticker, record in tickers.items() if record["n_months"] >= 48]
    correlation_matrix = {}
    for left in long_tickers:
        correlation_matrix[left] = {}
        for right in long_tickers:
            n = min(len(monthly_returns[left]), len(monthly_returns[right]))
            correlation_matrix[left][right] = pearson(
                monthly_returns[left][-n:], monthly_returns[right][-n:]
            )

    def basket_cagr(members: list[str]) -> float | None:
        if any(member not in tickers for member in members):
            return None
        common_months = min(tickers[member]["n_months"] for member in members)
        values = []
        for member in members:
            prices = read_json(YAHOO_PATH)["tickers"][member]["prices"]
            ordered = [float(prices[key]) for key in sorted(prices)][-common_months:]
            values.append([value / ordered[0] for value in ordered])
        average = [sum(series[i] for series in values) / len(values) for i in range(common_months)]
        return cagr(average[0], average[-1], (common_months - 1) / 12.0)

    groups = {
        "integrators_cpu_gpu_tpu": ["NVDA", "AMD", "GOOGL"],
        "legacy_cpu": ["INTC"],
        "mobile_soc": ["QCOM"],
        "foundry": ["TSM"],
    }
    group_cagr = {name: basket_cagr(members) for name, members in groups.items()}

    pairs = []
    for term_id, ticker in ATTENTION_MARKET_PAIRS:
        if ticker in tickers and tickers[ticker]["cagr"] is not None:
            pairs.append(
                {
                    "term": term_id,
                    "ticker": ticker,
                    "company": TICKER_LABELS.get(ticker, ticker),
                    "price_cagr": tickers[ticker]["cagr"],
                }
            )
    return {
        "source": snapshot.get("source"),
        "retrieved_at": snapshot.get("retrieved_at"),
        "tickers": tickers,
        "correlation_matrix": correlation_matrix,
        "group_cagr": group_cagr,
        "attention_market_pairs": pairs,
    }


def analyze_bench() -> dict[str, Any] | None:
    if not BENCH_PATH.exists():
        return None
    payload = read_json(BENCH_PATH)
    serial_rates = [row["ops_per_s"] for row in payload["serial"]]
    serial_rate = statistics.median(serial_rates) if serial_rates else 0.0
    vector_rows = payload["vector"]
    vector_speedups = [row["speedup"] for row in vector_rows if "speedup" in row]
    vector_throughput = max(row["numpy_ops_per_s"] for row in vector_rows)
    matmul_peak = max(row["gflops"] for row in payload["matmul"])
    thread_rows = payload["threads"]
    eight = next((row for row in thread_rows if row["threads"] == 8), None)
    crossover = next(
        (
            row["n"]
            for row in sorted(vector_rows, key=lambda item: item["n"])
            if row.get("speedup", 0) >= 2.0
        ),
        None,
    )
    return {
        "platform": payload["platform"],
        "serial_ops_per_s": serial_rate,
        "vector_speedup_min": min(vector_speedups) if vector_speedups else None,
        "vector_speedup_max": max(vector_speedups) if vector_speedups else None,
        "vector_throughput_ops_per_s": vector_throughput,
        "vector_to_serial_ratio": vector_throughput / serial_rate if serial_rate else None,
        "matmul_peak_gflops": matmul_peak,
        "matmul_to_serial_ratio": matmul_peak * 1e9 / serial_rate if serial_rate else None,
        "thread_speedup_8": eight["speedup_vs_1"] if eight else None,
        "thread_efficiency_8": eight["parallel_efficiency"] if eight else None,
        "vector_crossover_n": crossover,
        "energy": payload.get("energy"),
        "raw": payload,
    }


def attention_publication_coupling(
    bibliometrics: dict[str, Any], attention: dict[str, Any]
) -> dict[str, Any]:
    rows = []
    for term_id, article in attention["articles"].items():
        publication = bibliometrics["terms"].get(term_id)
        if not publication or not publication.get("cagr_2021_2025"):
            continue
        attention_cagr = article.get("cagr_2021_2025")
        if attention_cagr is None:
            continue
        rows.append(
            {
                "term": term_id,
                "label": TERM_LABELS.get(term_id, term_id),
                "publication_cagr": publication["cagr_2021_2025"],
                "attention_cagr": attention_cagr,
            }
        )
    xs = [row["publication_cagr"] for row in rows]
    ys = [row["attention_cagr"] for row in rows]
    return {
        "n_terms": len(rows),
        "rows": rows,
        "pearson": pearson(xs, ys) if len(rows) >= 2 else None,
        "spearman": spearman(xs, ys) if len(rows) >= 2 else None,
    }


def build_summary(
    evidence: dict[str, Any],
    bibliometrics: dict[str, Any],
    attention: dict[str, Any],
    markets: dict[str, Any],
    bench: dict[str, Any] | None,
    coupling: dict[str, Any],
) -> dict[str, Any]:
    claims = evidence["totals"]["claims"]
    verification = evidence["verification_rate"]
    ci_low, ci_high = evidence["verification_rate_ci95"]
    inflation_terms = bibliometrics["summary"]["terms_with_10x_inflation"]
    max_inflation_term = max(
        bibliometrics["terms"].items(), key=lambda item: item[1]["inflation_factor"]
    )
    lifecycle = evidence["lifecycle_counts"]
    absorption = lifecycle.get("absorbed", 0) + lifecycle.get("integrated", 0)

    gpu_publication = bibliometrics["terms"]["gpu"]
    gpu_attention = attention["articles"]["gpu"]
    attention_change = gpu_attention.get("change_2021_2025")
    publication_change = gpu_publication.get("cagr_2021_2025")

    top_gainers = sorted(
        (
            (article["label"], article["change_2021_2025"])
            for article in attention["articles"].values()
            if article["change_2021_2025"] is not None
        ),
        key=lambda item: item[1],
        reverse=True,
    )[:3]
    top_decliners = sorted(
        (
            (article["label"], article["change_2021_2025"])
            for article in attention["articles"].values()
            if article["change_2021_2025"] is not None
        ),
        key=lambda item: item[1],
    )[:3]
    headline = {
        "claims_total": str(claims),
        "claims_supported": str(evidence["status_counts"].get("supported", 0)),
        "claims_unverified": str(evidence["status_counts"].get("unverified", 0)),
        "claims_conflicting": str(evidence["status_counts"].get("conflicting", 0)),
        "claims_refuted": str(evidence["status_counts"].get("refuted", 0)),
        "top_attention_gainers": ", ".join(
            f"{label} {100 * change:+.0f}%" for label, change in top_gainers
        ),
        "top_attention_decliners": ", ".join(
            f"{label} {100 * change:+.0f}%" for label, change in top_decliners
        ),
        "integrators_cagr": (
            f"{100 * markets['group_cagr']['integrators_cpu_gpu_tpu']:.1f}%"
            if markets["group_cagr"]["integrators_cpu_gpu_tpu"] is not None
            else "n/a"
        ),
        "legacy_cpu_cagr": (
            f"{100 * markets['group_cagr']['legacy_cpu']:.1f}%"
            if markets["group_cagr"]["legacy_cpu"] is not None
            else "n/a"
        ),
        "foundry_cagr": (
            f"{100 * markets['group_cagr']['foundry']:.1f}%"
            if markets["group_cagr"]["foundry"] is not None
            else "n/a"
        ),
        "mobile_cagr": (
            f"{100 * markets['group_cagr']['mobile_soc']:.2f}%"
            if markets["group_cagr"]["mobile_soc"] is not None
            else "n/a"
        ),
        "paradigms_total": str(evidence["totals"]["paradigms"]),
        "sources_total": str(evidence["totals"]["sources"]),
        "verification_rate": f"{100 * verification:.1f}%",
        "verification_ci": f"{100 * ci_low:.1f}-{100 * ci_high:.1f}%",
        "primary_share": f"{100 * evidence['primary_share']:.1f}%",
        "era_chi2_p": f"{evidence['era_test']['p_value']:.3f}",
        "max_inflation": f"{max_inflation_term[1]['inflation_factor']:.0f}x ({max_inflation_term[1]['label']})",
        "inflation_terms_10x": str(len(inflation_terms)),
        "absorption_share": f"{100 * absorption / evidence['totals']['paradigms']:.0f}%",
        "gpu_publication_cagr": (
            f"{100 * publication_change:.1f}%" if publication_change is not None else "n/a"
        ),
        "gpu_attention_change": (
            f"{100 * attention_change:.1f}%" if attention_change is not None else "n/a"
        ),
        "coupling_spearman": (
            f"{coupling['spearman']:.2f}" if coupling.get("spearman") is not None else "n/a"
        ),
    }
    if bench:
        headline.update(
            {
                "serial_ops_per_s": f"{bench['serial_ops_per_s'] / 1e6:.1f}M",
                "vector_speedup_max": f"{bench['vector_speedup_max']:.1f}x",
                "vector_to_serial_ratio": f"{bench['vector_to_serial_ratio']:.1f}x",
                "matmul_peak_gflops": f"{bench['matmul_peak_gflops']:.1f}",
                "matmul_to_serial_ratio": f"{bench['matmul_to_serial_ratio']:.0f}x",
                "thread_efficiency_8": f"{100 * bench['thread_efficiency_8']:.1f}%",
            }
        )
    return {
        "generated_at": read_json(SNAPSHOTS / "capture_manifest.json").get("created_at"),
        "headline": headline,
        "checks": [
            headline["claims_total"],
            headline["verification_rate"],
            headline["primary_share"],
            headline["max_inflation"],
            headline["absorption_share"],
        ],
        "evidence": evidence["totals"],
        "bibliometrics": bibliometrics["summary"],
        "attention": attention["summary"],
        "markets": markets["group_cagr"],
        "coupling": {
            "n_terms": coupling["n_terms"],
            "pearson": coupling.get("pearson"),
            "spearman": coupling.get("spearman"),
        },
        "bench": {
            key: bench[key]
            for key in (
                "serial_ops_per_s",
                "vector_speedup_max",
                "vector_to_serial_ratio",
                "matmul_peak_gflops",
                "matmul_to_serial_ratio",
                "thread_efficiency_8",
            )
        }
        if bench
        else None,
    }


def main() -> int:
    ensure_dirs()
    if not EVIDENCE_PATH.exists():
        raise SystemExit("run `python -m xpu_atlas.claims` first")
    evidence = read_json(EVIDENCE_PATH)
    bibliometrics = analyze_bibliometrics()
    attention = analyze_attention()
    markets = analyze_markets()
    bench = analyze_bench()
    coupling = attention_publication_coupling(bibliometrics, attention)
    analysis = {
        "evidence": evidence,
        "bibliometrics": bibliometrics,
        "attention": attention,
        "markets": markets,
        "coupling": coupling,
        "bench": bench,
    }
    write_json(ANALYSIS_PATH, analysis)
    summary = build_summary(evidence, bibliometrics, attention, markets, bench, coupling)
    write_json(SUMMARY_PATH, summary)
    print(
        f"analysis: claims={summary['headline']['claims_total']} "
        f"verification={summary['headline']['verification_rate']} "
        f"max_inflation={summary['headline']['max_inflation']} "
        f"gpu_pub_cagr={summary['headline']['gpu_publication_cagr']} "
        f"gpu_attention={summary['headline']['gpu_attention_change']}"
    )
    if bench:
        print(
            f"bench: serial={summary['headline']['serial_ops_per_s']} ops/s "
            f"vector_speedup={summary['headline']['vector_speedup_max']} "
            f"matmul={summary['headline']['matmul_peak_gflops']} GFLOPS "
            f"thread_eff={summary['headline']['thread_efficiency_8']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
