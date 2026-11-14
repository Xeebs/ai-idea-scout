# Runtime Rosetta: An Independent Benchmark and Interop Layer for Fragmented Agent Sandboxing Runtimes

Four teams just shipped four different answers to "how do you sandbox a fleet of autonomous AI agents" — in the same 30-day window, with no comparison between them and no way to move your policy files if the one you pick stalls out. One of the four has NVIDIA's name on it and 508 Hacker News points behind it. The other three have a combined 23. If you're picking a runtime today, you're choosing between "loudest" and "unknown," because nobody has actually run them against the same test.

## The Gap

Within a single 30-day window, Hacker News saw four distinct, independently-maintained launches all solving overlapping slices of the same problem — execution isolation, policy enforcement, and zero-trust syscall filtering for AI agents: "OpenShell" (NVIDIA-backed, 508 points / 217 comments), "AegisKernel" (zero-trust POSIX runtime, 14 points / 4 comments), "Rigorix" (execution-governance engine, 4 points), and "Traccia" (runtime governance, 5 points). No comparison, benchmark, or interoperability layer surfaced anywhere between them.

A follow-up check on OpenShell found it's the real deal — an Apache-2.0 Rust runtime built on Landlock LSM and seccomp BPF, with declarative YAML policy, independently described in multiple write-ups as "a complementary layer, not a complete solution." The other three turned up nothing beyond their original launch posts — no adoption signal, no follow-up coverage, nothing to confirm they're more than a weekend project with a Show HN thread. That's not a knock on them; it's just the honest state of the evidence. The risk this project has to own upfront: NVIDIA's backing and marketing weight could simply out-resource the other three before they mature enough to be worth comparing at all, making a chunk of this effort moot within months. The gap being chased isn't "which runtime is best" — it's narrower and more durable than that: nobody has verified any of these claims against each other, and nobody can move a declarative policy set from one runtime to another if their bet stops being maintained.

## The Project

An independently-run benchmark harness installs each contender runtime in a disposable container and runs the identical declarative-policy test suite against all of them: syscall-filtering correctness, policy-violation catch rate against a standard adversarial action set (file exfiltration attempts, unauthorized syscalls, policy-violating tool calls), and invocation/startup latency overhead. The result is a published, re-runnable comparison matrix — not a one-time blog post, but something anyone can re-execute as the runtimes evolve.

On top of the benchmark sits a thin policy-translation layer that converts one runtime's declarative policy format into another's, so a team that bets on a project that later stalls isn't stuck re-deriving its security policy from scratch. Running continuously alongside both is a GitHub-API-driven maintenance-health tracker — commit cadence, issue response time, star growth — because three of the four contenders are unproven solo or small-team launches of genuinely unknown durability, and "still maintained in six months" is exactly the kind of claim nobody currently verifies before a team commits to one of these.

## Tangible Impact

**Population**: platform engineering teams deploying fleets of autonomous agents who must pick a sandboxing/runtime-governance layer today — the same audience OpenShell/AegisKernel/Rigorix/Traccia are each targeting; a proxy for the audience's size is OpenShell's 508-point, 217-comment HN launch, signaling a large population actively evaluating this exact category right now.
**Mechanism**: today a team either bets on the best-marketed option without verifying the other three's claims, or spends weeks building its own comparison from scratch; an independent, re-runnable benchmark plus a migration layer removes both the evaluation cost and the lock-in risk, letting a team switch runtimes later without re-deriving policies if its chosen project stalls.
**Measure**: (1) time for a team to pick a runtime using the benchmark vs. building its own bake-off (target: days, not weeks); (2) policy-translation fidelity — the % of a declarative policy set that migrates correctly between two runtimes without manual rewrite; (3) correlation between the benchmark's maintenance-health score and which of the four (or later entrants) are still actively maintained six months out, validating the health signal's predictive value.

## Try It

No companion skill has been written for this one yet — it's a benchmark-and-interop infrastructure project, not a prompt-driven task, so there's nothing to drop into `~/.claude/skills/` or paste into a chat tool today. If a `skills/agent-sandbox-runtime-benchmark-interop/` directory gets synthesized in a future cycle, this section will be updated to point at it.

---

Surfaced from `research/2026-11-13-ai-safety-and-guardrails-in-production.md`, pattern `P3`.
