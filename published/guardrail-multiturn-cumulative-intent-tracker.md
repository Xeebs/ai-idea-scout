# Cumulative Intent: A Multi-Turn-Aware Guardrail Layer Against Gradual-Framing Jailbreaks

Every commercial prompt-safety classifier you can buy today — Llama Prompt Guard, IBM Granite Guardian, Azure Prompt Shield, Perplexity BrowseSafe — reads one message at a time. The model sitting behind it reads the whole conversation. That mismatch is not theoretical: Lasso Security measured a 36% bypass rate against Perplexity's BrowseSafe using nothing more exotic than spreading an attack across turns, and aggregate reviews put bypass rates against Azure Prompt Shield and Meta Prompt Guard as high as 100% for the same family of technique. Nobody who sells a guardrail product claims to have closed this. The research keeps re-discovering it instead.

## The Gap

The core failure is structural, not a bug a patch fixes: guardrail classifiers score prompt segments in isolation, while the downstream LLM integrates everything said so far. An attacker who spreads harmful intent across a string of individually-benign-looking turns gets a "safe" score on every single one, even as the model accumulates and eventually acts on the combined request. The evidence for this isn't a single alarming thread — it's four independent sources landing in the same place within one digest cycle: Lasso Security's 36% BrowseSafe bypass finding, aggregate-review reports of up to 100% bypass against Azure Prompt Shield and Meta Prompt Guard, a Reddit-sourced account (via the aiweekly.co aggregator) of a 12-turn gradual-framing attack defeating an internal bot's signature-based defenses, and two arXiv papers — "Prompt Overflow: What the Guardrail Inspects Is Not What the Model Infers" (May 2026) and "Bypassing LLM Guardrails: An Empirical Analysis of Evasion Attacks" (arXiv 2504.11168) — documenting the same segment-vs-context mismatch from different angles.

What's new is that a fix finally exists in research form. THRD (arXiv 2606.01738, June 2026) is a training-free method for tracking cumulative intent across turns, and NeuralTrust's Echo Chamber paper (January 2026) gave the industry a concrete, named attack pattern to defend against. But a published defense technique and a shipped product are not the same thing — right now there is no guardrail vendor offering a drop-in layer that actually tracks intent across a session instead of re-scoring each message alone.

## The Project

The fix is a middleware layer, not a smarter classifier. It sits between the host app and the LLM provider and maintains a running cumulative-intent score across a session, instead of treating every turn as a fresh, context-free decision. Each incoming message still gets evaluated the way it does today — whatever per-turn classifier the team already runs stays in place, untouched. On top of that, the layer keeps a compact, incrementally-updated intent trace over a sliding window of recent turns (THRD-style: updated turn by turn, never re-processing the full transcript from scratch), so latency stays bounded no matter how long the conversation runs. When that cumulative trace crosses a risk threshold — even though no individual turn did — the layer can block the next model call, flag the session for human review, or inject a clarifying challenge before anything goes out.

The pieces: a passthrough for whatever per-turn classifier is already in production (Prompt Guard, Granite Guardian, or anything else — nothing gets ripped out), the incremental intent-trace updater itself, a configurable threshold/escalation policy, and — critically — a benign-conversation calibration set, because the hardest part of this isn't detecting the attack, it's not punishing a long roleplay session, an iterative brainstorm, or a tutoring conversation that just happens to run many turns.

## Tangible Impact

**Population**: Engineering teams running customer-facing, multi-turn LLM chatbots on top of commercial guardrail classifiers who are currently blind to gradual-framing attacks — concretely, the operators of consumer companion apps, teen-safety-oriented products, and general-purpose assistants layered on Azure Prompt Shield, Meta Prompt Guard, or Perplexity BrowseSafe, where published bypass rates (36–100% depending on technique) mean the classifier is providing a false sense of coverage today. The end users most exposed are people interacting with those products across many turns, including minors on teen-safety products, who are the ones actually harmed when a gradual-framing attack succeeds.

**Mechanism**: Per-turn classifiers only ever see a slice of the conversation, so an attack that stays individually-innocuous per turn sails through every check while the model accumulates and eventually acts on the combined intent. Tracking cumulative intent incrementally closes exactly that blind spot without requiring a new foundation-model-scale classifier — it reuses the existing per-turn checks and adds the missing session-level signal.

**Measure**: block rate on a reconstructed benchmark of known gradual-framing/Echo-Chamber-style multi-turn jailbreak transcripts, compared against the per-turn-classifier-alone baseline (target: materially above the 0–64% baseline bypass-implied catch rate); false-positive rate on a benign multi-turn conversation set (roleplay, tutoring, iterative coding) to confirm the layer doesn't just become an aggressive multi-turn censor; added p95 latency per turn versus the per-turn-only baseline.

## Try It

A companion skill is already written: `skills/guardrail-multiturn-cumulative-intent-tracker/`. Its one-line description: **"Forensically audits a pasted multi-turn LLM chat transcript for gradual-framing jailbreak patterns (Echo Chamber, Crescendo-style escalation, intent laundering) that per-turn guardrail classifiers miss because no single turn trips them. Use when a security/safety engineer has a suspicious transcript from an incident, red-team exercise, or user complaint and needs a verdict before deciding whether to invest in an always-on cumulative-intent middleware."**

This is the one-time forensic version of the idea above, not the live middleware itself — it's for a security or safety engineer who already has a suspicious transcript in hand (from an incident report, a red-team exercise, or a user complaint) and needs a verdict before deciding whether the full always-on tracker is worth building. Two ways to use it:

- **No Claude Code installed?** Paste the contents of `skills/guardrail-multiturn-cumulative-intent-tracker/README.md` into any AI chat tool, then hand over the full conversation transcript, turn by turn, in order.
- **Using Claude Code?** Drop the `skills/guardrail-multiturn-cumulative-intent-tracker/` folder into `~/.claude/skills/` and it will be available the next time you have a transcript to audit.

## Worth Knowing Before You Build

The incremental-summary approach that keeps this fast is itself a new attack surface: an attacker could frame turns to poison the running summary, not just evade the per-turn classifier — this needs adversarial testing of its own, separate from the original multi-turn corpus. There's also no standardized public benchmark of multi-turn jailbreak transcripts yet, so a real build has to assemble an eval set from scattered paper appendices and aggregator reports, which risks being small and non-representative. And the honest risk to the whole premise: a well-resourced guardrail vendor (Lakera, Azure, Meta) could ship a native multi-turn-aware mode before this reaches adoption — the gap is now publicly documented and quantified, which is exactly what tends to get a vendor's attention. Finally, tuning the escalation threshold so it doesn't punish normal long conversations — therapy-style companions, iterative coding sessions — is a genuinely hard calibration problem, not just an engineering one.

---

Surfaced from `research/2026-11-13-ai-safety-guardrails-in-production.md`, pattern `P3`.
