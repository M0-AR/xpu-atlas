# Methodology

This document records the protocol behind XPU-Atlas. The README states the
results; this file states how the results were produced and what would count as
a replication.

## 1. Unit of analysis

The corpus is one 2026 popular-technology transcript that describes twenty
processing-unit paradigms. A **claim** is a single factual assertion that can be
checked against a public source. Claims were extracted at the finest useful
granularity: a definition, a date, a product specification, a financial figure
or a causal statement is a separate claim when it can fail independently.

The twenty paradigms are the transcript's taxonomy, not a literature-derived
ontology. The ledger records the first public introduction or announcement year,
with a `year_confidence` field where the date is disputed.

## 2. Grading

| Grade | Definition | Typical examples |
|---|---|---|
| E1 | Primary source | vendor release, SEC filing, peer-reviewed paper, standard, API dataset |
| E2 | Reputable secondary source | Reuters, CNBC, trade press, expert analysis |
| E3 | Tertiary source | encyclopedia, general reference |
| E0 | Unverified, conflicting or refuted | no captured source, disagreement, contradiction |

Grade and status are orthogonal. A claim is `supported` when at least one cited
source directly supports it, regardless of grade. A claim is `unverified` when
the statement is plausible but no captured source confirms it. A claim is
`conflicting` when credible sources disagree on a material detail, and `refuted`
when a captured source contradicts it.

The primary-evidence share is the fraction of claims graded E1. It is
deliberately strict: an encyclopedia can support a definition, but it cannot
establish a product specification or a financial figure.

## 3. Source capture and search protocol

Sources were captured between 28 October and 4 November 2026. The search order
was: primary documents first, then major news wires, then trade press, then
encyclopedias. Each source record contains an identifier, title, publisher, URL,
type, retrieval date and grade.

The audit used a sequential search protocol. Parallel searches triggered rate
limits, so queries were issued one at a time with a short delay after an HTTP
429. When a search backend failed, the fallback was a direct fetch of a
DuckDuckGo HTML or lite results page, followed by the target document. Search
results were never treated as evidence by themselves; the cited document had to
be opened and read.

## 4. Data snapshots

### OpenAlex

- Endpoint: `https://api.openalex.org/works`
- Filter: `title_and_abstract.search`
- Window: 2000-2025
- Terms: ASIC, CPU, DPU, FPGA, GPU, ISP, MCU, neuromorphic, NPU, photonic, PPU,
  quantum, TPU, WSE
- Two series per term: the exact phrase (quoted) and the unquoted token search.

The quoted series is the primary measure. The unquoted series is a sensitivity
check for lexical ambiguity. Counts are not field-weighted and are not
deduplicated across terms.

### Wikimedia

- Endpoint: Wikimedia REST pageview API
- Window: January 2021-October 2026 (70 months)
- Articles: the canonical article for each of twelve terms, chosen once and
  recorded in the snapshot.

Pageviews measure public attention, not technical adoption. The annual means
used in the paper exclude the partial 2026 year.

### Yahoo Finance

- Endpoint: Yahoo Finance chart API
- Window: December 2021-November 2026 for long series; Arm begins October 2023;
  Cerebras begins June 2026.
- Field: monthly adjusted close, which includes splits and dividends.

The market analysis is descriptive. It does not model factor exposures, and it
is not investment advice.

## 5. Statistics

- **Verification rate:** supported / total, with a 95% Wilson score interval.
- **Era test:** a 2x2 table of pre-2015 vs 2015+ by E1 vs not-E1, with a
  Yates-corrected chi-square and Cramer's V.
- **CAGR:** `(end / start) ** (1 / years) - 1`, using `(months - 1) / 12` years
  for monthly series. The subtraction avoids counting the first observation as a
  full period.
- **Exponential fit:** ordinary least squares on `ln(count)` against year.
  Doubling time is `ln(2) / slope`; fits with R2 below 0.6 are marked poor and
  their doubling times are not interpreted.
- **Volatility:** standard deviation of monthly log returns times `sqrt(12)`.
- **Maximum drawdown:** the worst peak-to-trough decline along the price path.
- **Coupling:** Pearson and Spearman correlations between publication CAGR and
  attention CAGR across the twelve terms with both series. This is exploratory;
  the terms are not independent samples.

## 6. Benchmarks

The benchmark suite runs on the host CPU only:

1. A serial Python chain at 1M, 3M and 10M iterations.
2. An affine kernel (`v*v + 3*v + 1`) in a Python list comprehension versus
   NumPy, at 1K to 10M elements.
3. The affine kernel in a `ThreadPoolExecutor` at 1, 2, 4 and 8 workers.
4. Dense matmul at n = 256, 512, 1024 and 2048, batched so each timing sample is
   long enough to be stable.
5. Optional RAPL energy when `/sys/class/powercap` is readable.

Each measurement reports the median and IQR over repeated trials. The benchmark
does not measure accelerators and does not claim to.

## 7. What would count as a replication

A replication would (a) use the committed snapshots and reproduce every number
in `results/summary.json`, (b) rerun `make test` and `make paper-check`, and
(c) rebuild the Docker image and run the pipeline. A **live** replication would
refresh the snapshots with `make fetch` and report the differences rather than
expecting identical counts.
