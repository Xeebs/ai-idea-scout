# Idle Compute, Honest Numbers: An Independent Benchmark for Volunteer-GPU Training Networks

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Small & local models
- **Source**: research/2026-11-12-small-local-models.md · P9
- **Maturity verdict**: PARTIAL — multiple 2026 projects (Dispersed, CrowdGPT, Gensyn, SynonAI, AIyield, Neurolov) already attempt idle-consumer-GPU distributed training with incentive layers, but coverage is almost entirely project marketing with no independent evaluation of throughput, payout fairness, or latency tolerance.
- **Format**: PROJECT

## The Gap
Reddit r/LocalLLaMA, "Microsoft files a patent application to train AI models on idle consumer GPUs" (2026-11-11), drew a pointed community reaction: no advertised payout rate, and "home internet latency feels like the bigger problem" than the compute itself. That same complaint applies to every existing commercial attempt at this pattern — each project (Dispersed, Gensyn, CrowdGPT, and others named in the gap-analyst's search) publishes its own throughput and payout claims with no third party checking whether real home-network latency actually lets the economics work, leaving both prospective GPU-sharers and ML teams evaluating these networks to take marketing at face value.

## The Project
An open, reproducible benchmark harness for volunteer-compute distributed training: simulate realistic home-network conditions (variable latency, asymmetric bandwidth, intermittent dropout, using network emulation tools like `tc`/`netem` across geographically distributed cloud nodes standing in for volunteer machines) and run real open distributed-training protocols (Hivemind-style gradient averaging, DiLoCo-style infrequent synchronization) across them, measuring actual achieved throughput versus datacenter-equivalent compute, and translating that into a "latency tolerance calculator" — given your real upload/download speed and a target model size, how much of your advertised GPU-credit payout would you actually realize versus the platform's headline rate. The benchmark publishes its methodology and raw data openly, unlike every current platform's self-reported numbers.
## Tangible Impact
**Population**: Owners of idle high-end consumer GPUs (gaming/workstation desktops, a population numbering in the tens of millions based on Steam's own hardware survey of RTX 30/40-series ownership) weighing whether to join a volunteer-compute credit network, plus smaller ML teams evaluating whether networks like Gensyn or Dispersed are a viable alternative to renting datacenter compute.
**Mechanism**: Replaces platform-authored throughput/payout marketing with independently measured numbers tied to real network conditions, so a prospective participant can estimate actual earnings before dedicating bandwidth and electricity, and an ML team can estimate real training wall-clock time before committing a job to a volunteer network instead of a cloud provider.
**Measure**: (1) gap between a platform's advertised throughput/payout and the benchmark's measured value under realistic latency/bandwidth conditions; (2) training-job completion time and final-model quality achieved via the emulated volunteer network versus an equivalent datacenter-cluster baseline; (3) adoption — number of distinct platforms the benchmark has evaluated and how many update their public claims after being cited.

## Why Now
Microsoft's own patent filing landing in the same 30-day window as a cluster of existing commercial attempts (Gensyn, Dispersed, CrowdGPT, SynonAI, AIyield, Neurolov) signals the category is consolidating fast enough that unverified claims will shape real participant and investor decisions soon — and the open protocols needed to build the benchmark (Hivemind, DiLoCo-style infrequent-sync training) are already mature, stable, and don't require inventing new distributed-training algorithms.

## MVP Sketch
Scope: benchmark one open protocol (Hivemind) across a small emulated network (4–8 geographically distributed cloud VMs with `netem`-injected latency profiles drawn from real residential-ISP measurements) training a small model (under 1B params) to a fixed quality target, and compare wall-clock time/final loss against a single-datacenter baseline at the same total GPU-hours. Stack: Python, Hivemind or an equivalent open framework, cloud VMs (a mix of regions for realistic latency), `tc`/`netem` for network shaping. Single validating experiment: does the emulated volunteer-network run reach the datacenter baseline's quality within a tolerable time multiplier (e.g., under 3x), or does latency sensitivity degrade it so badly that the entire category's economics are suspect — either result is a publishable, useful finding.

## Risks & Open Questions
- Cloud-VM network emulation is an approximation of real residential conditions (NAT traversal, ISP throttling, home router flakiness) and may understate the real-world latency problem the Reddit commenters flagged.
- This is explicitly an evaluation project, not a competing platform — its impact depends on being cited/trusted by the population it serves, which requires genuine neutrality and may be harder to achieve if any existing platform sponsors or disputes the methodology.
- If a major platform (Gensyn, given its reported scale) publishes its own independently-audited numbers first, this project's differentiation narrows to "covers more platforms" rather than "first honest numbers."
- Fair payout evaluation requires real electricity-cost and depreciation assumptions that vary by region/hardware — the benchmark's economic conclusions are sensitive to these assumptions in ways the throughput numbers are not.
