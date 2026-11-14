# Agent Sandbox Covert-Channel Exposure Audit

A self-contained prompt template for auditing a multi-agent or multi-tenant sandbox architecture for covert/side-channel exposure — the gap between "we believe these workloads are isolated" and "they could still exchange information through shared physical or kernel resources." Paste the block below into any AI chat tool, fill in your architecture details, and send it.

## When to use this

Use this before trusting a sandbox's isolation claims for adversarial, red-team, multi-tenant, or untrusted-code agent workloads — e.g. you're running two agents that are supposed to have no shared network and no shared writable files, but they both run on the same physical hardware, and you need to know whether that's actually safe. Also use it right after reading about a specific covert-channel exploit (a CPU cache-timing channel, a DNS-tunneling sandbox bypass, etc.) to check whether your own setup has the same exposure.

Don't use this for a routine security review of a single-tenant service where co-residency with another untrusted workload isn't even a question — this skill is specifically about shared-resource leakage between workloads that are supposed to be isolated from each other.

## What you need to provide

**Data source: Manual.** You describe your own architecture in the prompt below — this does not connect to any live infrastructure, cloud account, or monitoring tool. (A future always-on monitoring version of this idea would read live hardware performance counters, but that's a different, runtime tool — this is a one-time design review you run by describing your setup.)

Gather before you start:

1. **Isolation boundary** — what actually separates the workloads: separate VMs, containers on a shared kernel, separate processes, a microVM technology (gVisor, Firecracker, Kata), or a named sandbox platform/vendor (E2B, Daytona, Modal, Fly Machines, AWS Bedrock AgentCore, etc.).
2. **What's explicitly blocked** — e.g. "no shared network," "no shared writable filesystem."
3. **What's shared, even if you think it's harmless** — physical host/CPU, hypervisor, DNS resolver, NTP, scheduler, storage backend, logging/metrics pipeline, egress proxy, any shared cache. If you haven't audited this, say "unknown."
4. **Threat model** — are the co-resident workloads assumed non-colluding (you're worried about accidental leakage) or actively adversarial/colluding (you're worried about deliberate exfiltration)?
5. (Optional) Any specific exploit or advisory you're worried about.

## The prompt

```
You are auditing my AI agent sandbox architecture for covert/side-channel
exposure: ways that workloads believed to be isolated from each other could
still exchange information through shared physical or kernel resources.

My architecture:
- Isolation boundary: <separate VMs / containers on shared kernel / separate
  processes / microVM tech (gVisor, Firecracker, Kata) / named platform>
- Explicitly blocked: <e.g. no shared network, no shared writable filesystem>
- Shared resources (even if you think they're harmless): <physical
  host/CPU, hypervisor, DNS resolver, NTP, scheduler, storage backend,
  logging/metrics pipeline, egress proxy, shared caches — or "unknown">
- Threat model: <non-colluding/accidental leakage OR adversarial/colluding>
- (Optional) Specific exploit or advisory I'm worried about: <describe>

Please:

1. Classify my isolation boundary's strength on this hierarchy (weakest to
   strongest): shared OS process/namespace < shared-kernel containers <
   microVMs < full separate VMs on shared hypervisor < separate physical
   hosts. State where I sit.

2. Screen my shared resources against these known covert/side-channel
   families, and flag which apply:
   - Microarchitectural/hardware timing (shared CPU cache, memory bus, GPU,
     co-residency on the same physical core/socket)
   - Network-protocol side channels (DNS, NTP, ICMP, or any control-plane
     protocol reachable even when app-layer traffic is blocked)
   - Shared storage/cache channels (page cache, build cache, predictable
     object storage names, shared temp directories)
   - Scheduler/resource-contention channels (CPU/IO latency one workload can
     observe to infer another's activity)
   - Shared logging/metrics/observability pipeline readable across tenants
   - Output/content-layer channels (steganography or encoding tricks in
     model-generated text reviewed by a shared downstream process) — treat
     this as a separate category from the infrastructure channels above,
     with a different owner and fix.

3. For each flagged channel, assign a risk tier:
   - HIGH: exploitable by a motivated colluding adversary with documented
     techniques, and my boundary doesn't already mitigate it.
   - MEDIUM: theoretically exploitable but needs unusual conditions, or only
     matters under the adversarial/colluding threat model.
   - LOW/MITIGATED: my stated boundary or controls already close this.

4. For every HIGH and MEDIUM finding, give one concrete, specific
   mitigation (not "add monitoring") — e.g. cache partitioning or core
   pinning for hardware-timing, strict DNS resolver allowlisting for DNS
   channels, per-tenant cache/temp isolation for storage channels,
   per-tenant log/metrics separation for observability channels, output
   content scanning for content-layer channels.

5. Give each finding a one-line verdict: accept the risk (and why), mitigate
   before adversarial/untrusted use, or monitor (only for MEDIUM findings,
   or HIGH findings where I say monitoring is already in place).

6. If anything about my shared resources is genuinely ambiguous from what
   I've told you, mark it "UNKNOWN — verify" and tell me who to ask (vendor
   docs, infra team) rather than guessing either way.

Output as:
- Boundary summary (one line: isolation tier + threat model)
- Findings table: Channel | Applies? (Y/N/UNKNOWN) | Risk tier | Basis
- Mitigations: one subsection per HIGH/MEDIUM finding with technique + verdict
- Open questions: any UNKNOWN items and who to verify them with
- Bottom line: one sentence — safe for adversarial/untrusted co-resident
  workloads today or not, and the single highest-priority fix.

Guardrails:
- Don't claim a channel is closed just because a boundary type "usually"
  mitigates it — hardware-timing channels have been demonstrated across VM
  boundaries on shared physical hosts. Only separate physical hosts or
  vendor-confirmed partitioning actually closes that row.
- Don't invent a specific CVE, paper, or incident citation — only name one
  if you're confident it's real, otherwise describe the channel generically.
- Don't recommend "monitor" as the fix for a HIGH finding when a structural
  mitigation is available and my threat model is adversarial — monitoring
  detects a channel in use, it doesn't close it.
- Don't flag a channel family I gave you no basis for (e.g. a GPU side
  channel when I didn't mention a shared GPU) — mark it not applicable.
- Don't conflate infrastructure-layer channels with output/content-layer
  channels — keep them separate, they have different owners and fixes.
```

## What you get back

A structured markdown audit: a one-line boundary/threat-model summary, a findings table screening six known covert/side-channel families against your specific shared resources, a risk tier and concrete mitigation for every finding that applies, an explicit "verify this" list for anything ambiguous, and a one-sentence bottom-line verdict on whether your architecture is actually safe for adversarial or untrusted co-resident workloads today.

## What this is not

This is a one-shot architecture design/review tool, not a runtime detector. It tells you where your paper design has exposure and what to fix; it does not watch live traffic or hardware counters for an attack actually happening. If you need always-on detection (e.g. watching for a cache-timing exfiltration attempt in progress), that's a separate monitoring sidecar built on tools like `perf_event`/eBPF — a different project, not this prompt.
