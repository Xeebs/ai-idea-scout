---
name: agent-sandbox-covert-channel-detector
description: Audits a multi-agent or multi-tenant sandbox architecture description for covert/side-channel exposure — shared hardware, shared kernel resources, and shared network paths that could let "fully isolated" workloads exchange information anyway — and recommends concrete mitigations. Use before trusting a sandbox's isolation claims for adversarial, untrusted, or co-resident agent workloads, or when standing up a new agent-sandboxing platform.
---

# Agent Sandbox Covert-Channel Exposure Audit

## When to use this
A team is designing, operating, or evaluating a sandbox/isolation boundary meant to keep two or more agent workloads (or an agent and its operator, or an agent and another tenant) from exchanging information outside an intended channel — e.g. "these two agent VMs have no shared network and no shared writable files" — and wants to know whether that isolation claim actually holds, or whether shared physical/kernel resources leave a covert or side channel open. Reach for this before signing off on a sandbox's isolation guarantees for adversarial, red-team, multi-tenant, or untrusted-code use cases — not for routine application security review of a single-tenant service with no co-residency question at all.

Also reach for this immediately after any report (internal incident, vendor disclosure, research paper) describing a specific covert-channel exploit against a sandbox similar to yours, to check whether your own architecture has the same exposure.

## Inputs
**Data source**: Manual — the user describes or pastes their sandbox architecture (what's isolated, what's shared, and how workloads are scheduled/placed) directly into the conversation; this skill does not connect to any live infrastructure, cloud API, or monitoring system. A future "always-on monitoring sidecar" version of this idea would be Connected (reading host `perf_event`/eBPF data), but that is explicitly out of scope for this skill — this is a one-shot design/architecture review, not a runtime detector.

To run this skill, provide:
1. **Isolation boundary**: what layer separates the workloads — separate VMs, separate containers on shared kernel, separate processes, gVisor/Firecracker/Kata-style microVMs, or a named sandbox vendor/product (e.g. E2B, Daytona, Modal, Fly Machines, AWS Bedrock AgentCore).
2. **What's explicitly blocked**: e.g. "no shared network," "no shared writable filesystem," "no shared process namespace."
3. **What's shared, even if believed harmless**: physical host/CPU, hypervisor, DNS resolver, NTP server, scheduler, storage backend, logging/metrics pipeline, egress proxy, any shared cache (page cache, build cache, model/KV cache) — list whatever applies, or say "unknown" if the user hasn't audited this yet.
4. **Threat model**: are the co-resident workloads assumed non-colluding (accidental leakage) or actively adversarial/colluding (deliberate exfiltration)? This changes which channels matter.
5. Optional: any known exploit or advisory the user is specifically worried about (e.g. a CPU cache-timing channel, a DNS-tunneling bypass) — anchor the audit around it if given.

## Procedure
1. **Classify the isolation boundary's strength** against a known hierarchy, weakest to strongest: shared OS process/namespace < shared-kernel containers < microVMs (gVisor/Firecracker/Kata) < full separate VMs on shared hypervisor < separate physical hosts. State where the user's setup sits, because every channel type below is more or less exploitable depending on this.
2. **Walk the shared-resource list the user provided (or infer the defaults for their named platform/boundary type if they said "unknown") and screen each one against these known channel families**, flagging any that apply:
   - **Microarchitectural/hardware timing** — shared CPU cache, shared memory bus, shared GPU, co-resident on the same physical core/socket. Applies whenever two workloads share a physical host, regardless of VM/container boundary.
   - **Network-protocol side channels** — DNS (record type, query timing, subdomain encoding), NTP, ICMP, any "control-plane" protocol left reachable when application-layer egress is blocked. Applies whenever a workload has any network reachability at all, even if HTTP/app traffic is filtered.
   - **Shared storage/cache channels** — shared page cache, shared build/dependency cache, shared object storage with predictable naming, shared temp directories — presence/absence or timing of a cache hit can leak a bit.
   - **Scheduler/resource-contention channels** — CPU/IO scheduling latency that one workload can observe to infer another's activity (a coarser, lower-bandwidth cousin of the cache-timing channel).
   - **Shared logging/metrics/observability pipeline** — if both workloads' events land in one log store or metrics backend a workload can read back (directly or via a dashboard it can query), that pipeline itself is an exfiltration path.
   - **Output/content-layer channels** (distinct from infrastructure side channels) — if the only thing crossing the boundary is model-generated text/output reviewed by a shared downstream process, flag that encoding tricks (steganography, formatting, zero-width characters) can carry a channel even with a hard infrastructure boundary; name this as a separate owner/remediation path from the infra channels above, don't conflate them.
3. **For each flagged channel, assign a risk tier** based on the threat model given in input 4:
   - **HIGH** — exploitable by a motivated, colluding adversary with today's documented techniques (cite the closest known public exploit/paper if one matches), and the user's boundary tier (step 1) does not already mitigate it.
   - **MEDIUM** — theoretically exploitable but requires either unusual conditions (sustained co-residency guarantee, high channel-capacity tolerance) or is only a risk under the colluding threat model, not accidental leakage.
   - **LOW/MITIGATED** — the user's stated boundary or existing control already closes this (e.g. separate physical hosts eliminates the hardware-timing row entirely; a strict DNS allowlist with no wildcard resolution mitigates the DNS row).
4. **Write one concrete mitigation per HIGH and MEDIUM finding**, each naming a specific, real technique — not a vague "add monitoring": cache partitioning or scheduler-level isolation (e.g. core pinning, cache-way partitioning) for hardware-timing; DNS resolver allowlisting restricted to exact domains and record types for DNS channels; disabling or per-tenant-isolating shared caches/temp storage for storage channels; separating logging/metrics backends per tenant or stripping cross-tenant-readable detail for observability channels; output content scanning (distinct tooling) for content-layer channels.
5. **Close with a one-line verdict per finding**: "accept the risk" (name why — e.g. non-adversarial threat model, low channel capacity), "mitigate before adversarial/untrusted use" (HIGH findings with no existing control), or "monitor" (MEDIUM findings, or any HIGH finding where the user says a monitoring sidecar is already planned or in place).
6. If the user's description leaves a shared-resource category genuinely ambiguous (e.g. they don't know whether the sandbox vendor shares a page cache across tenants), say so explicitly and name it as an open question to verify with the vendor/platform docs — never assume a channel is absent just because the user didn't mention it, and never assume it's present without basis either; mark it `UNKNOWN — verify` rather than guessing.

## Output format
A markdown audit with:
1. **Boundary summary** — one line stating the isolation tier (step 1) and the stated threat model.
2. **Findings table** — one row per screened channel family: `Channel | Applies? (Y/N/UNKNOWN) | Risk tier | Basis (what in the input triggered this)`.
3. **Mitigations**, one subsection per HIGH/MEDIUM finding: the specific technique, and the one-line verdict (accept/mitigate/monitor).
4. **Open questions** — any `UNKNOWN` items the user should verify, and with whom (vendor docs, infra team, etc.).
5. **Bottom line** — one sentence: is this architecture safe to run adversarial/untrusted co-resident workloads on today, or not, and what's the single highest-priority fix.

## Guardrails
- Never claim a channel is closed just because a boundary type "usually" mitigates it (e.g. separate VMs) — hardware-timing channels have been demonstrated across VM boundaries on shared physical hosts; only separate physical hosts or vendor-confirmed cache/scheduler partitioning closes that row.
- Never invent a specific CVE, paper, or incident to cite — only reference a known exploit if the user supplied it or it's one you can actually name and are confident about (e.g. the publicly documented CPU-cache-timing channel between isolated agent VMs, or documented DNS-tunneling sandbox bypasses); if unsure, describe the channel family generically without a fabricated citation.
- Never recommend "add a monitoring sidecar" as the fix for a HIGH finding when a structural mitigation (partitioning, allowlisting, physical separation) is available and the threat model is adversarial/colluding — monitoring detects a channel in use, it doesn't close it; reserve "monitor" as the verdict only for MEDIUM findings or HIGH findings the user says already have monitoring in place.
- Never produce a finding for a channel family the input gives no basis for (e.g. flagging a GPU side channel when no GPU is shared and the user didn't mention one) — mark it not applicable rather than padding the report.
- Never conflate infrastructure-layer covert channels (hardware, network, storage, scheduler) with content-layer/output channels (steganography in model output) — they have different owners and different fixes; keep them in separate rows/sections.
