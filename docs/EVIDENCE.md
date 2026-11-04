# Evidence Ledger

Generated from `data/claims.yaml` on 2026-11-04. The ledger contains **64 claims**, **20 paradigms** and **58 sources**.

## Grading rubric

| Grade | Meaning |
|---|---|
| E1 | Primary source: official release, filing, peer-reviewed paper, standard or API dataset. |
| E2 | Reputable secondary source: major news wire, trade press or expert analysis. |
| E3 | Tertiary source: encyclopedia or general reference. |
| E0 | Unverified, conflicting or refuted; retained for transparency. |

`supported` means at least one cited source directly supports the statement; `unverified` means plausible but not confirmed by a captured source; `conflicting` means credible sources disagree; `refuted` means a captured source contradicts the statement.

## Summary

- Supported: **47/64** (73.4%, 95% Wilson CI 61.5-82.7%).
- Primary evidence (E1): **13/64** (20.3%).
- Unverified or conflicting: **15 unverified, 1 conflicting, 1 refuted**.
- Grade distribution: E1=13, E2=7, E3=28, E0=16.
- Era test: Yates chi-square = 6.83, p = 0.0090, Cramer's V = 0.327.

### Primary-evidence share by era

| Era | Claims | Primary (E1) | Share | Supported |
|---|---:|---:|---:|---:|
| pre-2015 | 33 | 2 | 6.1% | 22 |
| 2015-2020 | 21 | 7 | 33.3% | 17 |
| 2021-2026 | 10 | 4 | 40.0% | 8 |

## Conflict register

| Claim | Status | Grade | Statement | Note |
|---|---|---|---|---|
| `spu-003` | conflicting | E0 | The US Air Force built a supercomputer from 1,760 PlayStation 3 consoles. | Secondary reports differ between 1,760 and 1,716 nodes; the fetched Cell extract does not resolve the count. |
| `lpu-003` | refuted | E2 | The transcript's statement that Nvidia paid 'about $20' for Groq's technology is off by roughly three orders of magnitude; the reported figure is about $20 billion. | Unit/scale error in popular narration; retained as a conflict-register entry. |

## Claims by paradigm

### CPU - Central Processing Unit (1971, general-purpose)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `cpu-001` | supported | E3 | The CPU executes the instructions of a computer program, including arithmetic, logic, control and input/output operations. | `S001` | Definition-level claim; encyclopedic source. |
| `cpu-002` | supported | E3 | The CPU is the primary, general-purpose processor and is contrasted with specialized coprocessors such as GPUs. | `S001` |  |
| `cpu-003` | unverified | E0 | Consumer desktop CPUs in 2026 span roughly 4 to 24 cores. | `S001` | Product-stack generalization; not sampled from vendor SKUs in this audit. |

### GPU - Graphics Processing Unit (1999, general-purpose)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `gpu-001` | supported | E3 | Nvidia announced the GeForce 256 on 31 August 1999 and marketed it as the world's first GPU. | `S003` | 'World's first GPU' is a marketing claim, not a neutral architectural priority claim. |
| `gpu-002` | supported | E3 | A GPU is a specialized circuit for digital image processing and graphics acceleration, present on discrete cards and integrated into systems-on-chip. | `S002` |  |
| `gpu-003` | supported | E3 | GPUs are increasingly used for AI processing and model training because of linear-algebra acceleration. | `S002` |  |

### PPU - Physics Processing Unit (2006, absorbed)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `ppu-001` | supported | E3 | A PPU is a dedicated microprocessor for physics calculations, especially game physics engines. | `S004` |  |
| `ppu-002` | supported | E3 | Ageia acquired NovodeX/PhysX in 2004 and produced a PhysX physics-processing chip. | `S005` |  |
| `ppu-003` | unverified | E0 | The PhysX card launched at roughly $250-300 in 2006 and Nvidia acquired Ageia in 2008, moving PhysX onto GPUs. | `S005` | The absorption narrative is consistent across secondary reports, but price and dates were not captured from a primary source in this snapshot. |

### APU - Accelerated Processing Unit (2011, integrated)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `apu-001` | supported | E3 | AMD's APU combines a general-purpose AMD64 CPU and a 3D integrated GPU on a single die. | `S006` |  |
| `apu-002` | unverified | E0 | AMD launched its first APUs in 2011. | `S006` | Launch year is widely reported but not present in the fetched extract. |
| `apu-003` | supported | E3 | The Steam Deck integrates a custom AMD APU. | `S007` |  |

### SPU - Synergistic Processing Unit (2006, absorbed)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `spu-001` | supported | E3 | The Cell Broadband Engine combines a general-purpose PowerPC PPE with multiple Synergistic Processing Elements. | `S008` |  |
| `spu-002` | unverified | E0 | Cell contains eight SPEs; one was disabled for yields and one reserved for the system, leaving six usable by games. | `S008` | Widely reported; the fetched extract does not contain the yield and reservation details. |
| `spu-003` | conflicting | E0 | The US Air Force built a supercomputer from 1,760 PlayStation 3 consoles. | `S008` | Secondary reports differ between 1,760 and 1,716 nodes; the fetched Cell extract does not resolve the count. |

### NPU - Neural Processing Unit (2017, integrated)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `npu-001` | supported | E3 | An NPU is a specialized accelerator for AI and machine learning, and may be standalone or integrated into a CPU or GPU. | `S009` |  |
| `npu-002` | supported | E3 | Apple introduced the A11 Bionic in the iPhone 8/8 Plus and iPhone X on 12 September 2017. | `S010` |  |
| `npu-003` | unverified | E0 | Apple branded the A11's AI accelerator as the Neural Engine. | `S010` | Device and date are verified; the Neural Engine branding is not in the fetched extract. |
| `npu-004` | supported | E1 | Microsoft requires an NPU capable of 40+ TOPS for Copilot+ PC certification. | `S011`, `S012` |  |

### TPU - Tensor Processing Unit (2015, commercial)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `tpu-001` | supported | E3 | Google's TPU is an NPU/ASIC designed for neural-network machine learning; internal use began in 2015. | `S013` |  |
| `tpu-002` | supported | E1 | Google announced its eighth-generation TPUs, TPU 8t for training and TPU 8i for inference, on 22 April 2026. | `S014`, `S015` |  |
| `tpu-003` | supported | E1 | TPUs are offered to Google Cloud customers rather than sold as standalone PC components. | `S014` | Cloud availability; no retail component channel was announced. |

### LPU - Language Processing Unit (2016, absorbed)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `lpu-001` | supported | E2 | Groq's LPU is an inference accelerator that emphasizes deterministic execution and on-chip SRAM. | `S019` | Architecture details are vendor claims reported by trade press. |
| `lpu-002` | supported | E2 | Nvidia licensed Groq's inference technology non-exclusively on 24 December 2025, hired Jonathan Ross and Sunny Madra, and reportedly paid about $20 billion. | `S016`, `S017`, `S018` | The parties disclosed the license and hiring; the price is press-reported, not disclosed. |
| `lpu-003` | refuted | E2 | The transcript's statement that Nvidia paid 'about $20' for Groq's technology is off by roughly three orders of magnitude; the reported figure is about $20 billion. | `S018` | Unit/scale error in popular narration; retained as a conflict-register entry. |

### MCU - Microcontroller Unit (1971, embedded)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `mcu-001` | supported | E3 | An MCU integrates one or more processor cores, memory, and programmable I/O peripherals on a single integrated circuit. | `S020` |  |
| `mcu-002` | supported | E3 | MCUs target embedded applications, in contrast to general-purpose microprocessors. | `S020` |  |
| `mcu-003` | unverified | E0 | A modern car can contain dozens of MCUs. | `S020` | Industry estimate; not sampled from teardown data. |

### ISP - Image Signal Processor (1990, integrated)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `isp-001` | supported | E3 | An ISP/image processor is a specialized DSP or media processor for image processing in cameras and other devices. | `S021` |  |
| `isp-002` | supported | E3 | Image processors often use SIMD or MIMD parallelism. | `S021` |  |
| `isp-003` | unverified | E0 | Two phones with the same camera sensor can produce different photos because of ISP and software differences. | `S021` | Plausible and widely reported, but not tested with a controlled image dataset in this audit. |

### TPM / Secure Enclave - Security Processor (2001, integrated)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `sec-001` | supported | E3 | A TPM is a secure cryptoprocessor implementing ISO/IEC 11889, used for boot integrity and disk-encryption keys. | `S022` |  |
| `sec-002` | supported | E1 | Windows 11 requires TPM 2.0. | `S012` |  |
| `sec-003` | unverified | E0 | Apple's Secure Enclave first appeared in the iPhone 5S in 2013. | `S058` | Widely reported; the fetched trusted-execution-environment extract does not confirm the device and date. |

### ASIC - Application-Specific Integrated Circuit (1980, commercial)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `asic-001` | supported | E3 | An ASIC is an integrated circuit customized for a particular use rather than general-purpose use. | `S023` |  |
| `asic-002` | unverified | E0 | Bitcoin mining migrated from CPUs to GPUs to ASICs, with ASIC miners appearing around 2013. | `S056` | The fetched Bitcoin extract does not contain mining-hardware history. |
| `asic-003` | unverified | E0 | Modern leading-edge ASIC design can cost tens to hundreds of millions of dollars. | `S023` | Industry cost estimate; no primary cost breakdown was captured. |

### FPGA - Field-Programmable Gate Array (1985, commercial)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `fpga-001` | supported | E3 | An FPGA is a configurable integrated circuit that can be repeatedly programmed after manufacturing. | `S024` |  |
| `fpga-002` | supported | E3 | Xilinx is renowned for inventing the first commercially viable FPGA. | `S025` |  |
| `fpga-003` | supported | E3 | FPGAs are used in telecommunications, automotive, aerospace, industrial and R&D applications. | `S024` |  |

### DPU - Data Processing Unit (2019, integrated)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `dpu-001` | supported | E3 | A DPU tightly integrates a general-purpose CPU with network-interface hardware; the category overlaps with SmartNICs and IPUs. | `S026` |  |
| `dpu-002` | supported | E3 | Nvidia acquired Mellanox for $6.9 billion in March 2019; the BlueField DPU line originated at Mellanox. | `S027` |  |
| `dpu-003` | unverified | E0 | Amazon uses Nitro chips for a similar infrastructure-offload role. | `S026` | Not verified against AWS primary documentation in this snapshot. |

### WSE - Wafer-Scale Engine (2019, commercial)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `wse-001` | supported | E1 | Cerebras WSE-3 has 4 trillion transistors, 900,000 AI cores, 44 GB of on-chip memory, and 21 PB/s memory bandwidth. | `S029`, `S033` |  |
| `wse-002` | supported | E1 | Cerebras uses the entire wafer as one chip instead of cutting it into individual dies. | `S047`, `S029` |  |
| `wse-003` | supported | E2 | OpenAI signed a multi-year deal valued at more than $20 billion for Cerebras compute in January 2026. | `S030`, `S029` |  |
| `wse-004` | supported | E1 | Cerebras priced its IPO at $185 per share on 13 May 2026 and began trading as CBRS on 14 May 2026. | `S028`, `S032` |  |

### NPU (neuromorphic) - Neuromorphic Processor (2014, research)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `nm-001` | supported | E3 | Neuromorphic computing uses artificial neurons and brain-inspired, event-driven computation. | `S035` |  |
| `nm-002` | unverified | E0 | IBM's TrueNorth chip (2014) contained 1 million artificial neurons. | `S035` | Widely cited; not captured from a primary IBM source in this snapshot. |
| `nm-003` | supported | E1 | Intel's Hala Point (17 April 2024) packages 1,152 Loihi 2 processors with 1.15 billion neurons, 20 petaops, and a 2,600 W maximum. | `S034` |  |

### Photonic - Photonic Processor (2025, research)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `ph-001` | supported | E3 | Photonic or optical computing uses light waves for data processing, storage, or communication. | `S036` |  |
| `ph-002` | supported | E1 | Lightmatter published a Nature paper in April 2025 demonstrating a photonic processor running AI models, including Atari games. | `S037` |  |
| `ph-003` | unverified | E0 | Photons are strong at transport and multiplication but weak at storage, so photonic systems remain hybrid. | `S036` | Analytical claim; not directly tested. |

### QPU - Quantum Processing Unit (2019, research)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `q-001` | supported | E3 | Quantum computers process information using quantum states, exploiting superposition, interference, and entanglement. | `S039` |  |
| `q-002` | supported | E1 | Google's 105-qubit Willow chip completed a benchmark in under five minutes that would take a classical supercomputer an estimated 10^25 years. | `S038` | Benchmark-specific claim; it does not imply general-purpose speedup. |
| `q-003` | supported | E3 | Quantum hardware is largely experimental and suitable only for specialized tasks. | `S039` |  |
| `q-004` | unverified | E0 | IBM and Google target reliable error-corrected quantum computers around 2029. | `S039` | Roadmap claim; not captured from a primary source in this snapshot. |

### TSU - Thermodynamic Sampling Unit (2026, emerging)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `tsu-001` | supported | E1 | Extropic's Z1 has 269,568 probabilistic bits across eight cores, >50 MHz sampling, <1 W, and a die under 12 mm per side. | `S040` |  |
| `tsu-002` | supported | E2 | Extropic's ~10,000x energy-efficiency claim derives from simulations and system-level modeling of small benchmarks, not production Z1 measurements. | `S040`, `S041` | The company's own page describes simulating a small piece of Z1; the independent analysis calls for production measurements. |
| `tsu-003` | supported | E1 | Z1 systems (M.2 sticks, PCIe cards, clusters) are planned for early access in 2027; the chip taped out in 2026. | `S040` |  |

### Wetware - Biological Processing Unit (2022, research)

| Claim | Status | Grade | Statement | Sources | Note |
|---|---|---|---|---|---|
| `bio-001` | supported | E1 | Cortical Labs demonstrated that neurons on microelectrode arrays can learn to play Pong (Neuron, 2022). | `S042` |  |
| `bio-002` | supported | E2 | The CL1 costs about $35,000; each unit can house about 800,000 neurons; the 2026 Doom demo used about 200,000 neurons. | `S043`, `S044`, `S045`, `S046` | The 200,000 figure refers to the Doom demo, not the CL1's full capacity. |
| `bio-003` | supported | E2 | CL1 neurons require life support and can remain viable for up to about six months under ideal conditions. | `S043`, `S045` |  |
| `bio-004` | unverified | E0 | Biological computing raises ethical questions about awareness and consent. | `S046` | Normative and ethical claim; not empirically testable in this audit. |

## Sources

| ID | Title | Publisher | Type | Grade | Retrieved | URL |
|---|---|---|---|---|---|---|
| `S001` | Central processing unit | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Central_processing_unit |
| `S002` | Graphics processing unit | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Graphics_processing_unit |
| `S003` | GeForce 256 | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/GeForce_256 |
| `S004` | Physics processing unit | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Physics_processing_unit |
| `S005` | Ageia | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Ageia |
| `S006` | AMD APU | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/AMD_APU |
| `S007` | Steam Deck | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Steam_Deck |
| `S008` | Cell (processor) | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Cell_(processor) |
| `S009` | Neural processing unit | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Neural_processing_unit |
| `S010` | Apple A11 | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Apple_A11 |
| `S011` | Introducing Copilot+ PCs | Microsoft | primary | E1 | 2026-11-04 | https://blogs.microsoft.com/blog/2024/05/20/introducing-copilot-pcs/ |
| `S012` | Windows 11 specifications and system requirements | Microsoft | primary | E1 | 2026-11-04 | https://www.microsoft.com/en-us/windows/windows-11-specifications |
| `S013` | Tensor Processing Unit | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Tensor_Processing_Unit |
| `S014` | Our eighth generation TPUs: two chips for the agentic era | Google | primary | E1 | 2026-11-04 | https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/eighth-generation-tpu-agentic-era/ |
| `S015` | AI infrastructure at Next '26 | Google Cloud | primary | E1 | 2026-11-04 | https://cloud.google.com/blog/products/compute/ai-infrastructure-at-next26 |
| `S016` | Groq and Nvidia enter non-exclusive inference technology licensing agreement | Groq | primary | E1 | 2026-11-04 | https://groq.com/newsroom/groq-and-nvidia-enter-non-exclusive-inference-technology-licensing-agreement-to-accelerate-ai-inference-at-global-scale |
| `S017` | Nvidia to license Groq technology, hire executives | Reuters | press | E2 | 2026-11-04 | https://www.reuters.com/business/nvidia-buy-ai-chip-startup-groq-about-20-billion-cnbc-reports-2025-12-24/ |
| `S018` | Nvidia buying AI chip startup Groq for about $20 billion | CNBC | press | E2 | 2026-11-04 | https://www.cnbc.com/2025/12/24/nvidia-buying-ai-chip-startup-groq-for-about-20-billion-biggest-deal.html |
| `S019` | Nvidia to license technology from inference chip startup Groq in reported $20B deal | SiliconANGLE | press | E2 | 2026-11-04 | https://siliconangle.com/2025/12/24/nvidia-license-technology-inference-chip-startup-groq-reported-20b-deal/ |
| `S020` | Microcontroller | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Microcontroller |
| `S021` | Image processor | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Image_processor |
| `S022` | Trusted Platform Module | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Trusted_Platform_Module |
| `S023` | Application-specific integrated circuit | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Application-specific_integrated_circuit |
| `S024` | Field-programmable gate array | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Field-programmable_gate_array |
| `S025` | Xilinx | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Xilinx |
| `S026` | Data processing unit | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Data_processing_unit |
| `S027` | Nvidia BlueField | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Nvidia_BlueField |
| `S028` | Cerebras Systems announces pricing of initial public offering | Cerebras | primary | E1 | 2026-11-04 | https://www.cerebras.ai/press-release/cerebras-systems-announces-pricing-of-initial-public-offering |
| `S029` | Cerebras Systems 424B4 prospectus | U.S. Securities and Exchange Commission | primary | E1 | 2026-11-04 | https://www.sec.gov/Archives/edgar/data/2021728/000162828026035214/cerebras-424b4.htm |
| `S030` | Cerebras scores OpenAI deal worth over $10 billion | CNBC | press | E2 | 2026-11-04 | https://www.cnbc.com/2026/01/14/cerebras-scores-openai-deal-worth-over-10-billion.html |
| `S031` | AI chipmaker Cerebras files for IPO after scrapping paperwork in 2025 | CNBC | press | E2 | 2026-11-04 | https://www.cnbc.com/2026/04/17/cerebras-new-ipo-ai-chips.html |
| `S032` | Cerebras prices IPO above expected range | CNBC | press | E2 | 2026-11-04 | https://www.cnbc.com/amp/2026/05/13/cerebras-prices-ipo-above-expected-range-wall-street-expects-ai-flood.html |
| `S033` | Cerebras Systems | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Cerebras_Systems |
| `S034` | Intel builds world's largest neuromorphic system | Intel | primary | E1 | 2026-11-04 | https://www.intel.com/content/www/us/en/newsroom/news/intel-builds-worlds-largest-neuromorphic-system.html |
| `S035` | Neuromorphic computing | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Neuromorphic_computing |
| `S036` | Optical computing | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Optical_computing |
| `S037` | Photonic processor running AI models (Nature) | Nature | peer_reviewed | E1 | 2026-11-04 | https://www.nature.com/articles/s41586-025-08854-x |
| `S038` | Quantum supremacy using a programmable superconducting processor (Willow) | Nature | peer_reviewed | E1 | 2026-11-04 | https://doi.org/10.1038/s41586-024-08449-y |
| `S039` | Quantum computing | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Quantum_computing |
| `S040` | From one to one billion: Torx, Thermalizers, and Z1 | Extropic | primary | E1 | 2026-11-04 | https://extropic.ai/writing/from-one-to-one-billion/ |
| `S041` | The transistor's intriguing second act | Kindred Ventures | press | E2 | 2026-11-04 | https://kindredventures.com/research/the-transistors-intriguing-second-act/ |
| `S042` | In vitro neurons learn and exhibit sentience when embodied in a simulated game-world (Neuron) | Cell Press | peer_reviewed | E1 | 2026-11-04 | https://doi.org/10.1016/j.neuron.2022.09.001 |
| `S043` | Biological computer: human brain cells on a chip | IEEE Spectrum | press | E2 | 2026-11-04 | https://spectrum.ieee.org/biological-computer-for-sale |
| `S044` | 200,000 living human neurons on a microchip demonstrated playing Doom | Tom's Hardware | press | E2 | 2026-11-04 | https://www.tomshardware.com/tech-industry/artificial-intelligence/200-000-living-human-neurons-on-a-microchip-demonstrated-playing-doom-cortical-labs-cl1-video-shows-the-gameplay-and-explains-how-the-neurons-learn-the-game |
| `S045` | This $35,000 computer made of living human neurons can run Doom | TechSpot | press | E2 | 2026-11-04 | https://www.techspot.com/news/111506-35000-computer-made-living-human-neurons-can-run.html |
| `S046` | How human neurons on a chip learned to play Doom | Scientific American | press | E2 | 2026-11-04 | https://www.scientificamerican.com/article/how-human-neurons-on-a-chip-learned-to-play-doom/ |
| `S047` | Wafer-scale integration | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Wafer-scale_integration |
| `S048` | The PRISMA 2020 statement: an updated guideline for reporting systematic reviews | BMJ | peer_reviewed | E1 | 2026-11-04 | https://www.bmj.com/content/372/bmj.n71 |
| `S049` | PRISMA 2020 statement | PRISMA | standard | E1 | 2026-11-04 | https://www.prisma-statement.org/ |
| `S050` | MLPerf Inference rules | MLCommons | standard | E1 | 2026-11-04 | https://raw.githubusercontent.com/mlcommons/inference_policies/master/inference_rules.adoc |
| `S051` | Artifact review and badging | ACM | standard | E1 | 2026-11-04 | https://www.acm.org/publications/policies/artifact-review-and-badging-current/ |
| `S052` | NeurIPS paper checklist | NeurIPS | standard | E1 | 2026-11-04 | https://neurips.cc/public/guides/PaperChecklist |
| `S053` | OpenAlex works API | OpenAlex | dataset | E1 | 2026-11-04 | https://api.openalex.org/ |
| `S054` | Wikimedia Pageviews API | Wikimedia Foundation | dataset | E1 | 2026-11-04 | https://wikimedia.org/api/rest_v1/ |
| `S055` | Yahoo Finance chart API | Yahoo Finance | dataset | E1 | 2026-11-04 | https://query1.finance.yahoo.com/v8/finance/chart/NVDA |
| `S056` | Bitcoin | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Bitcoin |
| `S057` | PlayStation 5 | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/PlayStation_5 |
| `S058` | Trusted execution environment | Wikipedia | encyclopedia | E3 | 2026-11-04 | https://en.wikipedia.org/wiki/Trusted_execution_environment |
