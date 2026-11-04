"""Three bounded workloads used by the first design-space sprint.

The numbers are deliberately round, documented assumptions. They are not
benchmark traces. The point is to compare architectural structures under a
shared workload, not to claim a measured speedup.
"""

from __future__ import annotations

from .model import Workload

WORKLOADS = (
    Workload(
        id="sparse_event_inference",
        name="Sparse event-driven inference",
        description=(
            "100M events, 64 fan-out, 16 timesteps, 2% active. The cost is "
            "dominated by state movement and event delivery, not dense MACs."
        ),
        ops=2_048_000_000.0,
        bytes_moved=1_200_000_000.0,
        communication_bytes=200_000_000.0,
        sequential_steps=16,
        parallelism=100_000_000,
        sparsity=0.98,
        precision_bits=8,
        bottleneck="memory and event interconnect",
    ),
    Workload(
        id="stochastic_sampling",
        name="Stochastic sampling",
        description=(
            "4,096 variables, 1,024 samples, 128 sweeps. The cost is dominated "
            "by repeated state exchange and sampling, not matrix multiplication."
        ),
        ops=536_870_912.0,
        bytes_moved=16_777_216.0,
        communication_bytes=16_777_216.0,
        sequential_steps=128,
        parallelism=4_096,
        sparsity=0.0,
        precision_bits=8,
        bottleneck="interconnect and sampling",
    ),
    Workload(
        id="memory_bound_attention",
        name="Memory-bound attention",
        description=(
            "4 batches, 16 heads, 2,048 tokens, 64 head width. The cost is "
            "dominated by the score matrix and tensor movement."
        ),
        ops=34_359_738_368.0,
        bytes_moved=603_979_776.0,
        communication_bytes=67_108_864.0,
        sequential_steps=32,
        parallelism=8_388_608,
        sparsity=0.0,
        precision_bits=8,
        bottleneck="memory bandwidth",
    ),
)

WORKLOAD_BY_ID = {workload.id: workload for workload in WORKLOADS}
