# Limitations

The paper's claims are bounded by the corpus, the sources and the proxies. This
file lists the main threats to validity.

## Corpus

1. **One transcript.** The 64 claims are a forensic sample of one narrative, not
   a systematic review. A different transcript would produce a different claim
   set and a different base rate.
2. **Claim granularity.** Decomposing a sentence into claims involves judgment.
   A broader claim may be marked unverified while a narrower version would pass.
3. **Taxonomy boundaries.** The twenty paradigms are the transcript's categories.
   Real product lines blur the boundaries (for example, an APU contains a CPU and
   a GPU; an NPU is often part of a SoC).

## Evidence

4. **Selection and access bias.** Paywalls, language barriers and archival gaps
   mean that some true claims remain unverified. The ledger records captured
   evidence, not all evidence.
5. **Tertiary dominance.** 28 of 64 claims rest on tertiary sources. Support by an
   encyclopedia is not primary support, even when the statement is correct.
6. **Conflict resolution.** The PS3 node count remains conflicting because the
   captured sources disagree. The ledger does not force a resolution.
7. **Search backend fragility.** Rate limits and backend failures can reduce
   recall. The audit used sequential queries and direct fetches as fallbacks, but
   no search process is exhaustive.

## Bibliometrics

8. **Title-and-abstract only.** OpenAlex counts do not cover full text and are not
   field-weighted. A paper that mentions a term once counts the same as a paper
   that is about the term.
9. **Exact phrases are imperfect.** Quoted search reduces homonym inflation but
   does not eliminate it. The WSE series contains a 2002 spike that is almost
   certainly unrelated to wafer-scale engines.
10. **Small denominators.** PPU has only 11 exact-phrase papers; its 579x
    inflation factor is illustrative, not a stable estimate.
11. **No quality weighting.** Counts treat a Nature paper and a workshop abstract
    alike. The analysis is about volume, not scientific quality.

## Attention

12. **Pageviews are a proxy.** Wikipedia traffic measures public curiosity, not
    adoption, purchasing or technical understanding.
13. **Bots and seasonality.** Pageview series can be affected by bots, article
    merges, redirects, news cycles and viral events.
14. **Article choice.** Each term maps to one canonical article. A different
    article or a redirect would change the series.
15. **Partial 2026.** The snapshot ends in October 2026; 2026 is excluded from
    annual comparisons.

## Markets

16. **Short window.** The long series covers 60 months, which includes an AI capex
    cycle and a concentrated bull market. Cerebras has only six monthly closes.
17. **Descriptive only.** The market analysis is not a factor model and not
    investment advice. Correlation with architecture is not causation.
18. **Universe selection.** The eight tickers are illustrative, not a market
    index. Survivorship and selection effects are present.

## Benchmarks

19. **Single machine.** The measurements come from one Intel CPU. They do not
    generalize to accelerators or to other memory hierarchies.
20. **Kernel choice.** The affine kernel is memory-bound; matmul is compute-bound.
    The 11,918x ratio depends on both the kernel and the BLAS implementation.
21. **No accelerator access.** TPU, GPU, QPU, photonic and neuromorphic hardware
    were not measured. Claims about those units rely on the literature, not on
    this benchmark.

## Statistics

22. **Non-independence.** Claims within a paradigm are correlated. The era
    chi-square treats them as independent and should be read as descriptive.
23. **Exploratory coupling.** The publication-attention correlation has n = 12 and
    no pre-registration. It is a hypothesis, not a confirmed effect.
24. **Multiple comparisons.** No family-wise correction is applied across the
    tables. Individual p-values should be interpreted accordingly.

## Time

25. **Snapshot date.** The version of record is 4 November 2026. Live data will
    differ. Replications should report the snapshot they used and the differences
    they observed.
