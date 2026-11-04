"""Render the evidence ledger and results tables as Markdown."""

from __future__ import annotations

from typing import Any

import yaml

from .io_utils import DATA, DOCS, RESULTS, ensure_dirs, read_json, write_text

CLAIMS_PATH = DATA / "claims.yaml"
ANALYSIS_PATH = RESULTS / "analysis.json"
SUMMARY_PATH = RESULTS / "summary.json"
EVIDENCE_PATH = DOCS / "EVIDENCE.md"
RESULTS_PATH = DOCS / "RESULTS.md"


def fmt_pct(value: float | None, digits: int = 1) -> str:
    return "n/a" if value is None else f"{100.0 * value:.{digits}f}%"


def fmt_num(value: float | None, digits: int = 2) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def escape(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def render_evidence(ledger: dict[str, Any], evidence: dict[str, Any]) -> str:
    claims = [claim for paradigm in ledger["paradigms"] for claim in paradigm["claims"]]
    lines = [
        "# Evidence Ledger",
        "",
        f"Generated from `data/claims.yaml` on {evidence['metadata']['compiled']}. "
        f"The ledger contains **{len(claims)} claims**, "
        f"**{len(ledger['paradigms'])} paradigms** and **{len(ledger['sources'])} sources**.",
        "",
        "## Grading rubric",
        "",
        "| Grade | Meaning |",
        "|---|---|",
        "| E1 | Primary source: official release, filing, peer-reviewed paper, standard or API dataset. |",
        "| E2 | Reputable secondary source: major news wire, trade press or expert analysis. |",
        "| E3 | Tertiary source: encyclopedia or general reference. |",
        "| E0 | Unverified, conflicting or refuted; retained for transparency. |",
        "",
        "`supported` means at least one cited source directly supports the statement; "
        "`unverified` means plausible but not confirmed by a captured source; "
        "`conflicting` means credible sources disagree; `refuted` means a captured source contradicts the statement.",
        "",
        "## Summary",
        "",
        f"- Supported: **{evidence['status_counts'].get('supported', 0)}/{len(claims)}** "
        f"({100 * evidence['verification_rate']:.1f}%, 95% Wilson CI "
        f"{100 * evidence['verification_rate_ci95'][0]:.1f}-{100 * evidence['verification_rate_ci95'][1]:.1f}%).",
        f"- Primary evidence (E1): **{evidence['grade_counts'].get('E1', 0)}/{len(claims)}** "
        f"({100 * evidence['primary_share']:.1f}%).",
        f"- Unverified or conflicting: **{evidence['status_counts'].get('unverified', 0)} unverified, "
        f"{evidence['status_counts'].get('conflicting', 0)} conflicting, "
        f"{evidence['status_counts'].get('refuted', 0)} refuted**.",
        f"- Grade distribution: E1={evidence['grade_counts'].get('E1', 0)}, "
        f"E2={evidence['grade_counts'].get('E2', 0)}, E3={evidence['grade_counts'].get('E3', 0)}, "
        f"E0={evidence['grade_counts'].get('E0', 0)}.",
        f"- Era test: Yates chi-square = {evidence['era_test']['chi2_yates']:.2f}, "
        f"p = {evidence['era_test']['p_value']:.4f}, Cramer's V = {evidence['era_test']['cramers_v']:.3f}.",
        "",
        "### Primary-evidence share by era",
        "",
        "| Era | Claims | Primary (E1) | Share | Supported |",
        "|---|---:|---:|---:|---:|",
    ]
    for era in ("pre-2015", "2015-2020", "2021-2026"):
        record = evidence["by_era"][era]
        lines.append(
            f"| {era} | {record['claims']} | {record['primary']} | "
            f"{100 * record['primary_share']:.1f}% | {record['supported']} |"
        )
    lines += [
        "",
        "## Conflict register",
        "",
        "| Claim | Status | Grade | Statement | Note |",
        "|---|---|---|---|---|",
    ]
    for item in evidence["conflict_register"]:
        lines.append(
            f"| `{item['claim_id']}` | {item['status']} | {item['grade']} | "
            f"{escape(item['statement'])} | {escape(item.get('note', ''))} |"
        )
    lines += ["", "## Claims by paradigm", ""]
    for paradigm in ledger["paradigms"]:
        lines += [
            f"### {paradigm['abbreviation']} - {paradigm['name']} "
            f"({paradigm['year']}, {paradigm['lifecycle']})",
            "",
            "| Claim | Status | Grade | Statement | Sources | Note |",
            "|---|---|---|---|---|---|",
        ]
        for claim in paradigm["claims"]:
            sources = ", ".join(f"`{source}`" for source in claim["sources"])
            lines.append(
                f"| `{claim['id']}` | {claim['status']} | {claim['grade']} | "
                f"{escape(claim['statement'])} | {sources} | {escape(claim.get('note', ''))} |"
            )
        lines.append("")
    lines += [
        "## Sources",
        "",
        "| ID | Title | Publisher | Type | Grade | Retrieved | URL |",
        "|---|---|---|---|---|---|---|",
    ]
    for source in ledger["sources"]:
        lines.append(
            f"| `{source['id']}` | {escape(source['title'])} | {escape(source['publisher'])} | "
            f"{source['type']} | {source['grade']} | {source['retrieved']} | {source['url']} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_results(analysis: dict[str, Any], summary: dict[str, Any]) -> str:
    headline = summary["headline"]
    bibliometrics = analysis["bibliometrics"]
    attention = analysis["attention"]
    markets = analysis["markets"]
    bench = analysis.get("bench")
    coupling = analysis["coupling"]

    lines = [
        "# Results",
        "",
        f"Generated from frozen snapshots by `python -m xpu_atlas.report`. "
        f"Snapshot timestamp: {summary.get('generated_at', 'n/a')}.",
        "",
        "## Headline",
        "",
        "| Metric | Value |",
        "|---|---|",
    ]
    for key, value in headline.items():
        lines.append(f"| `{key}` | {value} |")
    lines += [
        "",
        "## Bibliometrics (OpenAlex, exact phrase)",
        "",
        "`inflation` is the ratio of an unquoted keyword search to an exact-phrase search over 2000-2025. "
        "Doubling times are fitted only when the exponential R2 is at least 0.6.",
        "",
        "| Term | Quoted | Unquoted | Inflation | CAGR 2021-25 | Doubling (y) | R2 | Fit |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for term_id, record in sorted(
        bibliometrics["terms"].items(), key=lambda item: item[1]["total_quoted"], reverse=True
    ):
        lines.append(
            f"| {record['label']} (`{term_id}`) | {record['total_quoted']:,} | "
            f"{record['total_unquoted']:,} | {record['inflation_factor']:.1f}x | "
            f"{fmt_pct(record['cagr_2021_2025'])} | "
            f"{fmt_num(record['doubling_years']) if record['r_squared'] is not None and record['r_squared'] >= 0.6 else 'n/a'} | "
            f"{fmt_num(record['r_squared'])} | {record['fit_quality']} |"
        )
    lines += [
        "",
        f"Median inflation across {bibliometrics['summary']['n_terms']} terms: "
        f"{bibliometrics['summary']['median_inflation']:.1f}x. "
        f"Terms with at least 10x inflation: {', '.join(bibliometrics['summary']['terms_with_10x_inflation'])}.",
        "",
        "## Public attention (Wikimedia pageviews)",
        "",
        "Mean monthly pageviews; 2026 is excluded because the snapshot ends in October 2026.",
        "",
        "| Term | Article | 2021 mean | 2025 mean | Change |",
        "|---|---|---:|---:|---:|",
    ]
    for term_id, record in sorted(
        attention["articles"].items(), key=lambda item: item[1]["change_2021_2025"] or 0, reverse=True
    ):
        lines.append(
            f"| {record['label']} | {escape(record['article'])} | "
            f"{record['mean_2021']:,.0f} | {record['mean_2025']:,.0f} | "
            f"{100 * record['change_2021_2025']:+.1f}% |"
        )
    lines += [
        "",
        f"Median change: {100 * attention['summary']['median_change_2021_2025']:+.1f}%. "
        f"{attention['summary']['n_growing']} articles grew and "
        f"{attention['summary']['n_declining']} declined between 2021 and 2025.",
        "",
        "## Market snapshot (Yahoo Finance, monthly adjusted close)",
        "",
        "| Ticker | Months | First | Last | CAGR | Annualized vol | Max drawdown |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for ticker, record in sorted(
        markets["tickers"].items(), key=lambda item: item[1]["cagr"] or -1, reverse=True
    ):
        lines.append(
            f"| {record['label']} (`{ticker}`) | {record['n_months']} | "
            f"{record['first_price']:.2f} | {record['last_price']:.2f} | "
            f"{fmt_pct(record['cagr'])} | {fmt_pct(record['annualized_volatility'])} | "
            f"{fmt_pct(record['max_drawdown'])} |"
        )
    lines += [
        "",
        "| Group | Equal-weight CAGR |",
        "|---|---:|",
    ]
    for group, value in markets["group_cagr"].items():
        lines.append(f"| {group} | {fmt_pct(value)} |")
    lines += [
        "",
        "Cerebras (`CBRS`) has only six monthly observations; its annualized CAGR is unstable. "
        "From the first post-IPO monthly close ($221 in June 2026) to $97.82 in November 2026 it fell 55.7%, "
        "and it is 47.1% below the $185 IPO price.",
        "",
        "## Publication-attention coupling",
        "",
        "| Term | Publication CAGR 2021-25 | Attention CAGR 2021-25 |",
        "|---|---:|---:|",
    ]
    for row in coupling["rows"]:
        lines.append(
            f"| {row['label']} | {100 * row['publication_cagr']:+.1f}% | "
            f"{100 * row['attention_cagr']:+.1f}% |"
        )
    lines += [
        "",
        f"Pearson r = {fmt_num(coupling['pearson'])}, Spearman rho = {fmt_num(coupling['spearman'])}, "
        f"n = {coupling['n_terms']}. This is exploratory: the terms are not independent samples.",
        "",
    ]
    if bench:
        platform = bench["platform"]
        lines += [
            "## Local microbenchmarks",
            "",
            f"Platform: {platform['cpu_model']}, {platform['logical_cores']} logical cores, "
            f"Python {platform['python']}, NumPy {platform['numpy']}, {platform['system']}.",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Serial Python chain | {bench['serial_ops_per_s'] / 1e6:.1f}M ops/s |",
            f"| NumPy vectorized throughput | {bench['vector_throughput_ops_per_s'] / 1e9:.2f}B ops/s |",
            f"| Vectorized / serial | {bench['vector_to_serial_ratio']:.1f}x |",
            f"| Peak matmul | {bench['matmul_peak_gflops']:.1f} GFLOPS |",
            f"| Matmul / serial | {bench['matmul_to_serial_ratio']:.0f}x |",
            f"| 8-thread speedup | {bench['thread_speedup_8']:.2f}x |",
            f"| 8-thread efficiency | {100 * bench['thread_efficiency_8']:.1f}% |",
            "",
            "These are single-machine microbenchmarks, not accelerator measurements. "
            "They quantify the latency-versus-throughput gap only.",
            "",
        ]
    lines += [
        "## Notes",
        "",
        "- OpenAlex counts are title-and-abstract phrase matches; the API does not expose a field-weighted count.",
        "- Unquoted searches are retained only to quantify lexical ambiguity; all trend claims use exact phrases.",
        "- Market data are adjusted monthly closes and are descriptive, not investment advice.",
        "- Wikipedia pageviews measure public attention, not technical adoption.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ensure_dirs()
    ledger = yaml.safe_load(CLAIMS_PATH.read_text(encoding="utf-8"))
    evidence = read_json(RESULTS / "evidence_audit.json")
    analysis = read_json(ANALYSIS_PATH)
    summary = read_json(SUMMARY_PATH)
    write_text(EVIDENCE_PATH, render_evidence(ledger, evidence))
    write_text(RESULTS_PATH, render_results(analysis, summary))
    print(f"wrote {EVIDENCE_PATH.relative_to(DOCS.parent)}")
    print(f"wrote {RESULTS_PATH.relative_to(DOCS.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
