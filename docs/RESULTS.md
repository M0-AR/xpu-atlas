# Results

Generated from frozen snapshots by `python -m xpu_atlas.report`. Snapshot timestamp: 2026-11-04T11:07:25+00:00.

## Headline

| Metric | Value |
|---|---|
| `absorption_share` | 40% |
| `claims_conflicting` | 1 |
| `claims_refuted` | 1 |
| `claims_supported` | 47 |
| `claims_total` | 64 |
| `claims_unverified` | 15 |
| `coupling_spearman` | 0.38 |
| `era_chi2_p` | 0.009 |
| `foundry_cagr` | 30.0% |
| `gpu_attention_change` | -18.8% |
| `gpu_publication_cagr` | 5.4% |
| `inflation_terms_10x` | 5 |
| `integrators_cagr` | 33.4% |
| `legacy_cpu_cagr` | 4.9% |
| `matmul_peak_gflops` | 214.8 |
| `matmul_to_serial_ratio` | 11918x |
| `max_inflation` | 579x (PPU) |
| `mobile_cagr` | -0.03% |
| `paradigms_total` | 20 |
| `primary_share` | 20.3% |
| `serial_ops_per_s` | 18.0M |
| `sources_total` | 58 |
| `thread_efficiency_8` | 28.7% |
| `top_attention_decliners` | CPU -48%, MCU -42%, ASIC -38% |
| `top_attention_gainers` | Neuromorphic +2506%, NPU +2196%, DPU +76% |
| `vector_speedup_max` | 25.1x |
| `vector_to_serial_ratio` | 65.6x |
| `verification_ci` | 61.5-82.7% |
| `verification_rate` | 73.4% |

## Bibliometrics (OpenAlex, exact phrase)

`inflation` is the ratio of an unquoted keyword search to an exact-phrase search over 2000-2025. Doubling times are fitted only when the exponential R2 is at least 0.6.

| Term | Quoted | Unquoted | Inflation | CAGR 2021-25 | Doubling (y) | R2 | Fit |
|---|---:|---:|---:|---:|---:|---:|---|
| MCU (`mcu`) | 96,743 | 96,743 | 1.0x | 21.0% | 5.58 | 0.93 | good |
| Quantum (`quantum`) | 43,700 | 93,935 | 2.1x | 43.1% | 5.53 | 0.87 | good |
| FPGA (`fpga`) | 41,418 | 42,103 | 1.0x | 4.2% | 9.28 | 0.69 | moderate |
| GPU (`gpu`) | 21,736 | 23,750 | 1.1x | 5.4% | n/a | 0.59 | poor |
| Neuromorphic (`neuromorphic`) | 10,593 | 14,563 | 1.4x | 34.7% | 1.86 | 0.96 | good |
| CPU (`cpu`) | 9,231 | 45,365 | 4.9x | 13.7% | 6.52 | 0.96 | good |
| ASIC (`asic`) | 6,673 | 10,623 | 1.6x | 4.7% | n/a | 0.55 | poor |
| ISP (`isp`) | 1,175 | 152,202 | 129.5x | 18.7% | 7.77 | 0.82 | good |
| DPU (`dpu`) | 1,169 | 219,566 | 187.8x | 20.7% | 8.39 | 0.81 | good |
| Photonic (`photonic`) | 688 | 10,588 | 15.4x | 71.2% | 3.29 | 0.85 | good |
| NPU (`npu`) | 539 | 27,795 | 51.6x | 59.9% | 4.10 | 0.71 | moderate |
| TPU (`tpu`) | 537 | 2,484 | 4.6x | 4.0% | 1.56 | 0.77 | moderate |
| WSE (`wse`) | 513 | 4,864 | 9.5x | 29.6% | n/a | 0.09 | poor |
| PPU (`ppu`) | 11 | 6,369 | 579.0x | n/a | n/a | 0.19 | poor |

Median inflation across 14 terms: 4.8x. Terms with at least 10x inflation: dpu, isp, npu, photonic, ppu.

## Public attention (Wikimedia pageviews)

Mean monthly pageviews; 2026 is excluded because the snapshot ends in October 2026.

| Term | Article | 2021 mean | 2025 mean | Change |
|---|---|---:|---:|---:|
| Neuromorphic | Neuromorphic_computing | 422 | 10,990 | +2505.8% |
| NPU | Neural_processing_unit | 595 | 13,659 | +2196.0% |
| DPU | Data_processing_unit | 1,754 | 3,089 | +76.1% |
| TPU | Tensor_Processing_Unit | 17,463 | 29,376 | +68.2% |
| Quantum | Quantum_computing | 97,170 | 133,858 | +37.8% |
| WSE | Wafer-scale_integration | 1,024 | 1,191 | +16.3% |
| Photonic | Optical_computing | 6,775 | 7,109 | +4.9% |
| GPU | Graphics_processing_unit | 58,050 | 47,134 | -18.8% |
| FPGA | Field-programmable_gate_array | 38,445 | 30,872 | -19.7% |
| ASIC | Application-specific_integrated_circuit | 27,330 | 16,835 | -38.4% |
| MCU | Microcontroller | 32,760 | 19,033 | -41.9% |
| CPU | Central_processing_unit | 122,371 | 64,046 | -47.7% |

Median change: +10.6%. 7 articles grew and 5 declined between 2021 and 2025.

## Market snapshot (Yahoo Finance, monthly adjusted close)

| Ticker | Months | First | Last | CAGR | Annualized vol | Max drawdown |
|---|---:|---:|---:|---:|---:|---:|
| Arm (`ARM`) | 38 | 49.29 | 202.49 | 58.1% | 78.8% | -42.9% |
| NVIDIA (`NVDA`) | 60 | 29.29 | 206.69 | 48.8% | 47.8% | -58.7% |
| TSMC (`TSM`) | 60 | 111.52 | 404.80 | 30.0% | 36.4% | -49.0% |
| AMD (`AMD`) | 60 | 143.90 | 483.90 | 28.0% | 62.4% | -58.3% |
| Alphabet (`GOOGL`) | 60 | 143.49 | 280.03 | 14.6% | 32.0% | -39.1% |
| Intel (`INTC`) | 60 | 47.76 | 60.55 | 4.9% | 68.4% | -60.8% |
| Qualcomm (`QCOM`) | 60 | 164.65 | 164.43 | -0.0% | 40.9% | -41.0% |
| Cerebras (`CBRS`) | 6 | 221.00 | 97.82 | -85.9% | 63.5% | -55.7% |

| Group | Equal-weight CAGR |
|---|---:|
| foundry | 30.0% |
| integrators_cpu_gpu_tpu | 33.4% |
| legacy_cpu | 4.9% |
| mobile_soc | -0.0% |

Cerebras (`CBRS`) has only six monthly observations; its annualized CAGR is unstable. From the first post-IPO monthly close ($221 in June 2026) to $97.82 in November 2026 it fell 55.7%, and it is 47.1% below the $185 IPO price.

## Publication-attention coupling

| Term | Publication CAGR 2021-25 | Attention CAGR 2021-25 |
|---|---:|---:|
| ASIC | +4.7% | -11.4% |
| CPU | +13.7% | -14.9% |
| DPU | +20.7% | +15.2% |
| FPGA | +4.2% | -5.3% |
| GPU | +5.4% | -5.1% |
| MCU | +21.0% | -12.7% |
| Neuromorphic | +34.7% | +125.9% |
| NPU | +59.9% | +118.9% |
| Photonic | +71.2% | +1.2% |
| Quantum | +43.1% | +8.3% |
| TPU | +4.0% | +13.9% |
| WSE | +29.6% | +3.9% |

Pearson r = 0.46, Spearman rho = 0.38, n = 12. This is exploratory: the terms are not independent samples.

## Local microbenchmarks

Platform: Intel(R) Core(TM) i7-14700F, 28 logical cores, Python 3.12.13, NumPy 2.2.6, Linux.

| Metric | Value |
|---|---:|
| Serial Python chain | 18.0M ops/s |
| NumPy vectorized throughput | 1.18B ops/s |
| Vectorized / serial | 65.6x |
| Peak matmul | 214.8 GFLOPS |
| Matmul / serial | 11918x |
| 8-thread speedup | 2.29x |
| 8-thread efficiency | 28.7% |

These are single-machine microbenchmarks, not accelerator measurements. They quantify the latency-versus-throughput gap only.

## Notes

- OpenAlex counts are title-and-abstract phrase matches; the API does not expose a field-weighted count.
- Unquoted searches are retained only to quantify lexical ambiguity; all trend claims use exact phrases.
- Market data are adjusted monthly closes and are descriptive, not investment advice.
- Wikipedia pageviews measure public attention, not technical adoption.
