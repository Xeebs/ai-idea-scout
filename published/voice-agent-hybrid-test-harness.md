# Full Coverage: A Combined Replay + Adversarial-Synthetic + Auto-Regression Test Harness for Voice Agents

A team replayed 312 recorded production calls through their voice agent as a regression suite and still shipped a code-switching bug straight to real callers. Why? Because the failure happened exactly once per caller — it had never appeared in any of the 312 recordings in the first place. Real-call replay can only catch what real calls have already produced. The moment a failure mode is rare enough to never show up twice in your recorded history, replay-only testing is structurally blind to it.

## The Gap

Across the current voice-agent tooling landscape, three distinct ways of testing an agent have each been built — separately, by separate people, solving separate slices of the same problem. A DEV Community post makes the replay-only failure mode concrete: a code-switching bug that "never appeared in the recordings" because it only happens once per caller slipped straight through a 312-call regression suite. Vapi's own documentation draws a sharp line between "Evals" (did the agent make the right next decision from a given state) and "Simulations" (did the whole conversation land on the right outcome), and explicitly recommends promoting real production failures into permanent regression tests — as guidance for teams to implement themselves, not as a built tool.

Meanwhile, each individual layer already has a real implementation. `voicetest` (Apache 2.0, published on PyPI) does real-call replay against Retell, Vapi, Bland, and LiveKit transcripts. `xray-eval/xray` does something similar for LiveKit specifically, but sits behind the Elastic License — a telling signal that at least one team saw commercial value worth protecting here. On the synthetic side, academic benchmarks EVA-Bench and VAmoS-Bench generate adversarial simulated callers with acoustic perturbation, but as research artifacts, not shipped products a team can drop into CI. And Eve Legal's engineering blog describes exactly the auto-promotion pattern — flag a real failure, turn it into a permanent test — but only as a proprietary in-house harness nobody else gets to use.

Three real pieces, three different authors, zero teams putting them together. Every engineering team running a voice agent in production is currently choosing which one or two of the three they'll hand-roll, and living with the blind spot the missing piece leaves behind.

## The Project

The fix isn't inventing a fourth approach — it's wiring the three that already exist into one harness with a shared test-case store, so none of them has to run alone:

1. **Replay** imports real call transcripts and audio straight from a connected voice platform's export API and re-runs them against the current agent graph — built directly on `voicetest`'s existing, proven import coverage rather than reinventing that plumbing.
2. **Adversarial synthesis** uses an LLM-driven simulated caller to generate inputs targeting known failure classes — code-switching, DTMF confusion, backchannel noise — that real recordings simply haven't produced yet. This is the exact blind spot the 312-call example exposes, closed directly.
3. **Auto-promotion** takes any flagged production failure — a thumbs-down event, a human-reviewed bad call — and converts it automatically into a permanent, versioned regression case, generalizing Eve Legal's proprietary pattern into something any team can run.

All three write into one shared test-case store, so a single CI gate runs replay cases, synthetic adversarial cases, and auto-promoted real-failure cases together instead of three disconnected pipelines nobody fully trusts.

## Tangible Impact

**Population**: Engineering teams running production voice agents — a population the digest's own evidence sizes concretely: an AssemblyAI 2026 Insights Report found 87% of respondents have already deployed a voice agent to production, yet only 25% are satisfied with real-call quality. That gap scales with a 2026 voice-AI-agent software market estimated at $3.5–5.1B (Grand View Research, Meticulous Research) — a lot of teams sitting in that 62-point satisfaction gap with no structural way to close it.

**Mechanism**: Instead of manually re-deriving replay, adversarial-synthesis, and promotion tooling from scratch — or just skipping one layer entirely, which the digest shows is what most builders currently do — a team gets regression coverage that compounds automatically every time a real failure is caught in production. That's the specific mechanism the 312-call example shows a replay-only suite cannot deliver on its own.

**Measure**: the number of previously-unseen failure classes the adversarial layer catches that the replay-only set missed; time from a flagged production failure to a committed regression test (minutes via auto-promotion, versus the multi-day manual process most teams currently report); and regression-suite catch rate against a held-out set of real incidents over a 90-day window.

## Why Now

The raw ingredients all landed independently within the last few months and are mature enough to integrate rather than build from zero: `voicetest`'s PyPI release gave replay a real, Apache-licensed foundation; Vapi's docs formalized the Evals/Simulations distinction and named auto-promotion as a best practice; and the academic adversarial-caller benchmarks (EVA-Bench, VAmoS-Bench) proved out the synthetic-caller approach in public. Nobody has yet connected the three dots — the pieces are sitting there, unassembled.

## Try It

No companion skill exists yet for this idea — it's tagged `Format: BOTH`, and the intended skill is a "test gap triage" tool: given a pasted transcript of a voice-agent failure and a brief description of a team's current test coverage, it would classify which of the three layers would have caught it, draft the specific regression test case, and flag whether the failure class suggests the adversarial-synthesis layer needs expanding. When it's written, it'll land at `skills/voice-agent-hybrid-test-harness/`.

## The Honest Risk List

Building directly on `voicetest`'s Apache 2.0 code is favorable licensing, but it also means the differentiation here has to be the integration — auto-promotion feeding the adversarial layer, all three sharing one test-case store — not the replay mechanics themselves, which aren't new. Adversarial synthesis quality is entirely dependent on how well the generator models real failure distributions; a poorly tuned generator produces noise, not signal, and needs validation against a real dataset's failure shape before anyone should trust it on a new agent. Auto-promotion, left undisciplined, risks flooding a regression suite with one-off noise rather than durable signal — human confirmation before permanent promotion isn't optional. And `xray-eval/xray`'s choice of the non-OSI Elastic License is itself a signal worth taking seriously: at least one team already decided this space was worth protecting commercially, which may mean open tooling here faces a harder monetization path than it looks like at first glance.

---

Surfaced from `research/2026-11-20-voice-multimodal-agents.md`, pattern `P4`.
