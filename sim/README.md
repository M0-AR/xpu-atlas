# sim/ — analytical design-space explorer

This directory screens hypothetical XPU architectures under explicit
assumptions. It is a search tool, not a silicon claim.

```bash
make sim
```

Outputs:

- `results/simulation.json` — full payload, assumptions, and per-experiment metrics
- `results/simulation.csv` — flat table for spreadsheets
- `docs/SIMULATION.md` — generated report and Pareto discussion
- `figures/fig7_design_space.png` — latency-versus-energy frontiers

The model is a roofline-style calculation with workload-to-structure
utilization and overhead multipliers. It does not model SRAM capacity, NoC
contention, thermal effects, yield, compiler quality, or numerical accuracy.
The next gate is iso-accuracy validation, then RTL or FPGA prototyping.
