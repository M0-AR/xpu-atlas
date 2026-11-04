"""Publication-quality figures generated from frozen data snapshots."""

from __future__ import annotations

from datetime import datetime

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from .io_utils import FIGURES, RESULTS, SNAPSHOTS, ensure_dirs, read_json

OPENALEX_PATH = SNAPSHOTS / "openalex_counts.json"
WIKIMEDIA_PATH = SNAPSHOTS / "wikimedia_pageviews.json"
YAHOO_PATH = SNAPSHOTS / "yahoo_prices.json"

plt.rcParams.update(
    {
        "figure.dpi": 200,
        "savefig.dpi": 200,
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linewidth": 0.6,
        "legend.frameon": False,
        "legend.fontsize": 8,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)

PALETTE = {
    "cpu": "#2c3e50",
    "gpu": "#16a085",
    "tpu": "#d35400",
    "npu": "#8e44ad",
    "dpu": "#c0392b",
    "ppu": "#7f8c8d",
    "wse": "#34495e",
    "neuromorphic": "#e67e22",
    "quantum": "#2980b9",
    "photonic": "#27ae60",
    "fpga": "#95a5a6",
    "asic": "#bdc3c7",
    "mcu": "#7f8c8d",
    "isp": "#e74c3c",
}

COMPANY_COLORS = {
    "NVDA": "#76b900",
    "AMD": "#ed1c24",
    "GOOGL": "#4285f4",
    "INTC": "#0068b5",
    "QCOM": "#3253dc",
    "TSM": "#b03a2e",
    "ARM": "#0091bd",
    "CBRS": "#f39c12",
}


def _month_to_datetime(month: str) -> datetime:
    return datetime.strptime(month + "-01", "%Y-%m-%d")


def _save(fig, name: str) -> str:
    path = FIGURES / name
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {path.relative_to(FIGURES.parent)}")
    return str(path)


def figure_inflation(analysis: dict, openalex: dict) -> str:
    terms = analysis["bibliometrics"]["terms"]
    ordered = sorted(terms.items(), key=lambda item: item[1]["inflation_factor"])
    labels = [f"{record['label']} ({record['total_quoted']:,})" for _, record in ordered]
    values = [record["inflation_factor"] for _, record in ordered]
    colors = ["#c0392b" if value >= 10 else "#95a5a6" for value in values]

    fig, (left, right) = plt.subplots(1, 2, figsize=(11.5, 4.6))
    left.barh(labels, values, color=colors, edgecolor="white", height=0.72)
    left.set_xscale("log")
    left.axvline(1.0, color="#34495e", linewidth=0.8)
    left.axvline(10.0, color="#c0392b", linewidth=0.8, linestyle="--")
    for index, value in enumerate(values):
        left.text(value * 1.09, index, f"{value:.0f}x", va="center", fontsize=7)
    left.set_xlabel("Unquoted / exact-phrase OpenAlex count (log scale)")
    left.set_title("(a) Lexical inflation, 2000-2025")
    left.set_xlim(0.8, max(values) * 2.4)

    xs = [record["total_quoted"] for _, record in ordered]
    right.scatter(xs, values, s=34, c=colors, edgecolors="white", linewidths=0.5, zorder=3)
    for term_id in ("ppu", "dpu", "isp", "npu", "tpu", "photonic"):
        record = terms[term_id]
        right.annotate(
            record["label"],
            (record["total_quoted"], record["inflation_factor"]),
            textcoords="offset points",
            xytext=(4, 4),
            fontsize=7,
        )
    right.set_xscale("log")
    right.set_yscale("log")
    right.set_xlabel("Exact-phrase papers, 2000-2025 (log scale)")
    right.set_ylabel("Inflation factor (log scale)")
    right.set_title("(b) Ambiguity is worst for small, acronym-heavy fields")

    fig.suptitle(
        "Unquoted OpenAlex searches conflate acronyms with unrelated phrases",
        fontsize=11,
        y=1.02,
    )
    return _save(fig, "fig1_lexical_inflation.png")


def figure_publication(analysis: dict, openalex: dict) -> str:
    terms = analysis["bibliometrics"]["terms"]
    selected = ["gpu", "cpu", "tpu", "npu", "neuromorphic", "photonic"]
    fig, (left, right) = plt.subplots(1, 2, figsize=(11.5, 4.6))

    for term_id in selected:
        record = openalex["terms"][term_id]
        years = sorted(int(year) for year in record["counts"] if int(year) >= 2015)
        base_year = next(year for year in years if record["counts"][str(year)] > 0)
        base = record["counts"][str(base_year)]
        values = [100.0 * record["counts"][str(year)] / base for year in years]
        left.plot(
            years,
            values,
            marker="o",
            markersize=2.6,
            linewidth=1.5,
            color=PALETTE[term_id],
            label=f"{terms[term_id]['label']} ({base_year}=100)",
        )
    left.set_yscale("log")
    left.set_xlabel("Publication year")
    left.set_ylabel("Exact-phrase papers, indexed (log scale)")
    left.set_title("(a) Publication trajectories since 2015")
    left.legend(ncol=2, loc="upper left")

    fitted = [
        (record["label"], record["doubling_years"], record["r_squared"], term_id)
        for term_id, record in terms.items()
        if record["doubling_years"] is not None
        and record["r_squared"] is not None
        and record["r_squared"] >= 0.6
    ]
    fitted.sort(key=lambda item: item[1])
    right.barh(
        [item[0] for item in fitted],
        [item[1] for item in fitted],
        color=[PALETTE[item[3]] for item in fitted],
        edgecolor="white",
        height=0.68,
    )
    for index, (_, doubling, r_squared, _) in enumerate(fitted):
        right.text(doubling + 0.12, index, f"{doubling:.1f} y (R2={r_squared:.2f})", va="center", fontsize=7)
    right.set_xlabel("Exponential doubling time (years)")
    right.set_title("(b) Doubling time, exponential fits with R2 >= 0.6")
    right.set_xlim(0, max(item[1] for item in fitted) * 1.55)

    fig.suptitle(
        "Exact-phrase bibliometrics separate durable growth from acronym noise",
        fontsize=11,
        y=1.02,
    )
    return _save(fig, "fig2_publication_trajectories.png")


def figure_attention(analysis: dict, wikimedia: dict) -> str:
    articles = analysis["attention"]["articles"]
    selected = ["cpu", "gpu", "tpu", "npu", "neuromorphic", "quantum"]
    fig, (left, right) = plt.subplots(1, 2, figsize=(11.5, 4.6))

    for term_id in selected:
        means = articles[term_id]["annual_means"]
        years = sorted(int(year) for year in means if 2021 <= int(year) <= 2025)
        base = means[str(years[0])]
        values = [100.0 * means[str(year)] / base for year in years]
        left.plot(
            years,
            values,
            marker="o",
            markersize=3.2,
            linewidth=1.5,
            color=PALETTE[term_id],
            label=articles[term_id]["label"],
        )
    left.set_yscale("log")
    left.set_xlabel("Year")
    left.set_ylabel("Mean monthly pageviews, 2021 = 100 (log scale)")
    left.set_title("(a) Public attention, 2021-2025")
    left.legend(ncol=2, loc="upper left")
    left.set_xticks([2021, 2022, 2023, 2024, 2025])

    changes = [
        (record["label"], record["mean_2021"], record["mean_2025"], term_id)
        for term_id, record in articles.items()
        if record["mean_2021"] and record["mean_2025"]
    ]
    changes.sort(key=lambda item: item[2] / item[1])
    for index, (label, start_value, end_value, _) in enumerate(changes):
        ratio = end_value / start_value
        color = "#27ae60" if ratio >= 1 else "#c0392b"
        right.plot([start_value, end_value], [index, index], color=color, linewidth=2.0, alpha=0.55)
        right.scatter([start_value], [index], color="#7f8c8d", s=22, zorder=3, label="2021" if index == 0 else None)
        right.scatter([end_value], [index], color=color, s=30, zorder=3, label="2025" if index == 0 else None)
        right.text(
            max(start_value, end_value) * 1.12,
            index,
            f"{100.0 * (ratio - 1.0):+.0f}%",
            va="center",
            fontsize=7,
            color=color,
        )
    right.set_yticks(range(len(changes)), [item[0] for item in changes])
    right.set_xscale("log")
    right.set_xlabel("Mean monthly pageviews (log scale)")
    right.set_title("(b) Absolute attention levels, 2021 vs. 2025")
    right.legend(loc="lower right", fontsize=7)
    right.set_xlim(
        min(item[1] for item in changes) * 0.55,
        max(item[2] for item in changes) * 4.5,
    )

    fig.suptitle(
        "Wikipedia attention polarizes: legacy terms decay while NPU and neuromorphic surge",
        fontsize=11,
        y=1.02,
    )
    return _save(fig, "fig3_attention_reallocation.png")


def figure_economics(analysis: dict, yahoo: dict) -> str:
    tickers = analysis["markets"]["tickers"]
    selected = ["NVDA", "AMD", "GOOGL", "INTC", "QCOM", "TSM", "ARM"]
    fig, (left, right) = plt.subplots(1, 2, figsize=(11.5, 4.6))

    for ticker in selected:
        prices = yahoo["tickers"][ticker]["prices"]
        months = sorted(prices)
        base = float(prices[months[0]])
        xs = [_month_to_datetime(month) for month in months]
        ys = [100.0 * float(prices[month]) / base for month in months]
        left.plot(
            xs,
            ys,
            linewidth=1.5,
            color=COMPANY_COLORS.get(ticker, "#7f8c8d"),
            label=f"{tickers[ticker]['label']} ({months[0]})",
        )
    left.set_yscale("log")
    left.set_xlabel("Month")
    left.set_ylabel("Adjusted close, first observation = 100 (log scale)")
    left.set_title("(a) Cumulative total return, Dec 2021-Nov 2026")
    left.legend(ncol=2, loc="upper left", fontsize=7)
    left.tick_params(axis="x", rotation=30)

    ranked = sorted(
        (
            (ticker, record["cagr"])
            for ticker, record in tickers.items()
            if record["cagr"] is not None and record["n_months"] >= 24
        ),
        key=lambda item: item[1],
    )
    right.barh(
        [f"{tickers[ticker]['label']} ({ticker})" for ticker, _ in ranked],
        [100.0 * cagr for _, cagr in ranked],
        color=[COMPANY_COLORS.get(ticker, "#7f8c8d") for ticker, _ in ranked],
        edgecolor="white",
        height=0.68,
    )
    for index, (ticker, cagr) in enumerate(ranked):
        right.text(100.0 * cagr + 1.0, index, f"{100.0 * cagr:+.2f}%", va="center", fontsize=7)
    for label, value, color in (
        ("Integrators", analysis["markets"]["group_cagr"]["integrators_cpu_gpu_tpu"], "#16a085"),
        ("Foundry", analysis["markets"]["group_cagr"]["foundry"], "#b03a2e"),
        ("Legacy CPU", analysis["markets"]["group_cagr"]["legacy_cpu"], "#0068b5"),
    ):
        right.axvline(100.0 * value, color=color, linestyle="--", linewidth=1.0, label=label)
    right.axvline(0, color="#34495e", linewidth=0.8)
    right.set_xlabel("Monthly-price CAGR (%)")
    right.set_title("(b) Value accrues to integrators and foundry")
    right.legend(loc="lower right", fontsize=7)
    right.set_xlim(0, 65)

    fig.suptitle(
        "The market rewards integration and manufacturing, not legacy CPU or mobile SoC exposure",
        fontsize=11,
        y=1.02,
    )
    return _save(fig, "fig4_market_economics.png")


def figure_evidence(analysis: dict) -> str:
    evidence = analysis["evidence"]
    eras = ["pre-2015", "2015-2020", "2021-2026"]
    primary = [evidence["by_era"][era]["primary"] for era in eras]
    claims = [evidence["by_era"][era]["claims"] for era in eras]
    non_primary = [claims[i] - primary[i] for i in range(len(eras))]
    shares = [primary[i] / claims[i] for i in range(len(eras))]

    fig, (left, right) = plt.subplots(1, 2, figsize=(11.5, 4.6))
    positions = np.arange(len(eras))
    left.bar(positions, primary, color="#16a085", label="Primary source (E1)", width=0.62)
    left.bar(
        positions,
        non_primary,
        bottom=primary,
        color="#d5d8dc",
        label="Secondary, tertiary or unverified (E2/E3/E0)",
        width=0.62,
    )
    for index, share in enumerate(shares):
        left.text(index, claims[index] + 0.8, f"{100 * share:.1f}% primary", ha="center", fontsize=8)
    left.set_xticks(positions, eras)
    left.set_ylabel("Claims")
    left.set_title("(a) Primary-evidence share by era")
    left.legend(loc="upper left")
    left.set_ylim(0, max(claims) * 1.25)
    left.text(
        0.98,
        0.98,
        f"Yates chi2 = {evidence['era_test']['chi2_yates']:.2f}\n"
        f"p = {evidence['era_test']['p_value']:.3f}\n"
        f"Cramer's V = {evidence['era_test']['cramers_v']:.2f}",
        transform=left.transAxes,
        fontsize=7.5,
        ha="right",
        va="top",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#bdc3c7"},
    )

    status_order = ["supported", "unverified", "conflicting", "refuted"]
    status_counts = [evidence["status_counts"].get(status, 0) for status in status_order]
    status_colors = ["#16a085", "#f39c12", "#e67e22", "#c0392b"]
    bars = right.bar(status_order, status_counts, color=status_colors, width=0.62)
    for bar, count in zip(bars, status_counts):
        right.text(bar.get_x() + bar.get_width() / 2, count + 0.7, str(count), ha="center", fontsize=8)
    right.set_ylabel("Claims")
    right.set_title("(b) Verification status across 64 claims")
    right.set_ylim(0, max(status_counts) * 1.2)
    right.text(
        0.98,
        0.95,
        f"E1 (primary): {evidence['grade_counts'].get('E1', 0)}/64\n"
        f"E2 (secondary): {evidence['grade_counts'].get('E2', 0)}/64\n"
        f"E3 (tertiary): {evidence['grade_counts'].get('E3', 0)}/64\n"
        f"E0 (unverified): {evidence['grade_counts'].get('E0', 0)}/64",
        transform=right.transAxes,
        ha="right",
        va="top",
        fontsize=7.5,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#bdc3c7"},
    )

    fig.suptitle(
        "Evidence quality improves sharply after 2015 but nearly one quarter of claims remain unverified",
        fontsize=11,
        y=1.02,
    )
    return _save(fig, "fig5_evidence_gradient.png")


def figure_bench(analysis: dict) -> str | None:
    bench = analysis.get("bench")
    if not bench:
        return None
    raw = bench["raw"]
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2))

    left, middle, right = axes
    labels = ["Serial Python chain", "NumPy vectorized", "BLAS matmul"]
    values = [
        bench["serial_ops_per_s"],
        bench["vector_throughput_ops_per_s"],
        bench["matmul_peak_gflops"] * 1e9,
    ]
    colors = ["#7f8c8d", "#2980b9", "#c0392b"]
    left.bar(labels, values, color=colors, width=0.62)
    left.set_yscale("log")
    left.set_ylabel("Operations or FLOPs per second (log scale)")
    left.set_title("(a) Throughput hierarchy on one CPU")
    for index, value in enumerate(values):
        ratio = value / values[0]
        left.text(index, value * 1.35, f"{ratio:.0f}x" if index else "1x", ha="center", fontsize=8)
    left.set_ylim(1e6, max(values) * 5)
    left.tick_params(axis="x", rotation=12)

    thread_rows = raw["threads"]
    workers = [row["threads"] for row in thread_rows]
    speedups = [row["speedup_vs_1"] for row in thread_rows]
    middle.plot(workers, speedups, marker="o", color="#8e44ad", label="Measured")
    middle.plot(workers, workers, linestyle="--", color="#95a5a6", label="Ideal linear")
    for worker, speedup in zip(workers, speedups):
        middle.annotate(f"{speedup:.2f}x", (worker, speedup), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=7)
    middle.set_xlabel("Worker threads")
    middle.set_ylabel("Speedup vs. one thread")
    middle.set_title("(b) Parallel scaling hits the memory wall")
    middle.legend(loc="upper left")
    middle.set_xticks(workers)
    middle.set_ylim(0, max(workers) * 1.05)
    middle.text(
        0.98,
        0.06,
        f"8-thread efficiency: {100 * bench['thread_efficiency_8']:.1f}%",
        transform=middle.transAxes,
        ha="right",
        fontsize=7.5,
    )

    matmul_rows = sorted(raw["matmul"], key=lambda row: row["n"])
    sizes = [row["n"] for row in matmul_rows]
    gflops = [row["gflops"] for row in matmul_rows]
    right.plot(sizes, gflops, marker="o", color="#c0392b")
    for size, value in zip(sizes, gflops):
        right.annotate(f"{value:.0f}", (size, value), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=7)
    right.set_xscale("log", base=2)
    right.set_xticks(sizes, [str(size) for size in sizes])
    right.set_xlabel("Matrix dimension n")
    right.set_ylabel("GFLOPS")
    right.set_title("(c) Matmul throughput rises with working-set size")
    right.set_ylim(0, max(gflops) * 1.2)

    fig.suptitle(
        "Latency-optimized serial code is 12,000x slower than a dense linear-algebra engine",
        fontsize=11,
        y=1.02,
    )
    return _save(fig, "fig6_latency_throughput.png")


def main() -> int:
    ensure_dirs()
    analysis = read_json(RESULTS / "analysis.json")
    openalex = read_json(OPENALEX_PATH)
    wikimedia = read_json(WIKIMEDIA_PATH)
    yahoo = read_json(YAHOO_PATH)
    figure_inflation(analysis, openalex)
    figure_publication(analysis, openalex)
    figure_attention(analysis, wikimedia)
    figure_economics(analysis, yahoo)
    figure_evidence(analysis)
    figure_bench(analysis)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
