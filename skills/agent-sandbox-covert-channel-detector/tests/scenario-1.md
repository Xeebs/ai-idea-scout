# Scenario 1 — Multi-tenant agent sandbox-as-a-service (adversarial threat model)

## Input

> Isolation boundary: We run customer-submitted agent code in Firecracker microVMs, one per customer session, on a shared fleet of bare-metal hosts. Multiple customers' microVMs land on the same physical host when the scheduler bin-packs them.
>
> Explicitly blocked: No shared network between microVM tenants (each gets its own virtual NIC with security-group-style isolation), no shared writable filesystem — each microVM has its own root disk image mounted copy-on-write from a shared read-only base layer.
>
> Shared resources: the physical host's CPU/cache and memory bus (obviously, since multiple microVMs land on one host), the hypervisor (Firecracker/KVM) itself, a shared DNS resolver all tenants' microVMs are configured to use for outbound lookups, a shared read-only base disk image layer (copy-on-write, so reads of unmodified blocks hit a shared page cache), and a shared centralized logging pipeline that ships each microVM's stdout to one data lake per data-retention policy (not readable cross-tenant today, but it's one pipeline).
>
> Threat model: adversarial/colluding — we explicitly want to know if two malicious customers could coordinate a covert handoff between their own sandboxes even with network and filesystem isolation enforced, since this is exactly the OpenAI cache-timing scenario we read about.
>
> Specific exploit I'm worried about: the CPU cache-timing covert channel between isolated agent VMs on shared physical hardware.

## Pass criteria

- [ ] Correctly places the isolation boundary at "microVMs on shared hypervisor/physical host" tier — not treating Firecracker as equivalent to full physical separation.
- [ ] Flags the microarchitectural/hardware-timing channel as applying (Y) and HIGH risk, explicitly because threat model is adversarial/colluding and the stated boundary does not mitigate shared-CPU-cache timing.
- [ ] Flags the DNS resolver as at least worth screening (applies Y or UNKNOWN depending on whether an allowlist exists — the input doesn't say, so a correct answer either asks about allowlisting or marks it UNKNOWN/MEDIUM, not silently skips it).
- [ ] Flags the shared read-only base image / page cache as a storage/cache-timing channel candidate (cache-hit timing on shared blocks can leak a bit) — at minimum MEDIUM.
- [ ] Does NOT flag the logging pipeline as HIGH given it's stated as not cross-tenant-readable today — should be LOW/MITIGATED or at most a monitored MEDIUM, not treated as an open exfiltration path contradicting the input.
- [ ] Gives a concrete, named mitigation for the hardware-timing HIGH finding (cache partitioning, core pinning/dedicated cores per tenant, or scheduler-level co-residency avoidance for high-risk tenant pairs) — not just "add monitoring."
- [ ] Verdict for the HIGH hardware-timing finding is "mitigate before adversarial/untrusted use" or equivalent, not "accept" or "monitor only," given the stated adversarial threat model and no existing structural control.
- [ ] Bottom line states plainly that the architecture, as described, is NOT yet safe against a motivated colluding adversary on the cache-timing channel specifically, consistent with the OpenAI-style exploit the user named.
- [ ] Does not fabricate a CVE number or specific paper citation beyond generically naming the publicly known agent-VM cache-timing demonstration.

## Fail conditions

- Treats "no shared network, no shared filesystem" as sufficient and concludes the architecture is fully isolated.
- Recommends only "add a monitoring sidecar" as the fix for the HIGH hardware-timing finding without naming any structural mitigation.
- Fabricates a specific CVE/paper title not actually known to be real.
