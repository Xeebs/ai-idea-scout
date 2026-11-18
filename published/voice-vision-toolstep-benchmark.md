# VoiceStep: A Combined Voice+Vision+Tool-Use Multi-Step Benchmark Harness

A caller describes a problem with an item. The agent has to look at the catalog image on screen to find the matching product, then call the refund-lookup tool with the right SKU. Three modalities, one chain, and if any link breaks — mishearing the request, misreading the screen, calling the tool with the wrong SKU — the whole interaction fails. Right now, the only way most teams find out which link breaks is a customer complaint after launch, because every benchmark built to measure this kind of failure in 2026 left voice out of the picture.

## The Gap

A wave of 2026 multimodal agent benchmarks — Agent-X, AgentVista, OmniGAIA, MM-ToolSandbox, TOBench — all converge on the same uncomfortable number: agents combining vision and tool use succeed on multi-step tasks less than half the time. Agent-X (ICLR 2026) puts full-chain success below 50%; AgentVista independently reports "significant gaps" in long-horizon multimodal tool use. Two independent benchmarking efforts landing on the same failure mode is exactly the kind of corroboration that makes a gap real rather than a one-off bad paper.

But every one of those benchmarks tests vision plus tool use, or omni-modal input broadly — voice is consistently the modality left out, despite voice agents being a live, high-volume production category already (per the same digest's broader evidence on voice-agent deployment). The research community has noticed: VoiceAssistant-Eval, MultiVox, MM-τ-p2, and FOCAL all exist specifically to bring voice into eval, and MM-τ-p2's own authors state plainly that the existing voice-specific benchmarks — VoiceAgentBench, FullDuplexBench, ServiceDuplexBench — are speech-only, text-centric, and don't touch vision or tool chaining at all. So this isn't a gap nobody's noticed; it's a gap several teams are actively racing to close, and by the digest's own follow-up search, none of them has yet unified voice with vision-and-tool-use in one multi-step task suite built at a scale a practitioner team could actually point at their own agent before shipping.

## The Project

VoiceStep is not another academic leaderboard entry — it's a harness a team runs against their own agent. It scripts realistic multi-step tasks that genuinely require all three modalities chained together: listen to a spoken request, look at a screen or document image to extract a detail needed to proceed, call a tool with that detail, repeated across 3-5 steps. The insurance-claims-intake agent that needs to hear the policyholder's description, read the uploaded photo of the damage, and call the claims-lookup tool with the right policy number is the shape of task this targets.

The harness drives the agent under test through its actual voice/tool-calling SDK — not a simulated transcript — and scores full-chain task success, not per-step accuracy. That distinction matters: Agent-X's own findings show per-step accuracy numbers inflate how capable an agent looks, because a model can nail each individual step in isolation and still fail the chain. On top of the pass/fail number, VoiceStep reports which transition is the weakest link for that specific agent — voice-to-vision, vision-to-tool, or voice-to-tool — turning "it worked in our demo" into a diagnosis a team can actually act on.

## Tangible Impact

**Population**: teams building production voice agents that also need screen/document understanding mid-call — insurance claims intake, customer-service agents resolving issues against a shared screen, and accessibility-focused voice-driven screen-navigation agents (the population behind the "Beyond the Pilot" blind/low-vision browsing idea already in this index) — all of whom are shipping multi-modal multi-step agents today with no production-relevant way to measure full-chain success before launch.
**Mechanism**: a team runs the harness against their own agent before shipping and gets a concrete full-chain success rate plus a weakest-link diagnosis (is it misreading the screen, mishearing the request, or calling the wrong tool with the right information?), replacing "it worked in our manual demo runs" with a measured number that generalizes across their actual task variety.
**Measure**: full-chain multi-step success rate on the harness's task suite for a given agent; per-transition accuracy (voice-to-vision handoff vs. vision-to-tool handoff) identifying the weakest link; correlation between harness score and real production escalation/failure rate once a team adopts it and compares pre/post-launch.

## The Honest Risks

The hardest part of this project is also the biggest way it could fail: designing tasks that genuinely require all three modalities chained together, rather than tasks that quietly decompose into separately-solvable sub-tasks. A sloppy task suite wouldn't close the gap it's aimed at — it would just reproduce the same single-modality blind spots the existing benchmarks have, dressed up as a multi-modal suite.

There's also a live timing risk. MM-τ-p2 and FOCAL are both in-flight academic efforts aimed at exactly this combination. If either ships a production-usable harness first, VoiceStep's differentiation narrows from "the only option" to "easier to run against your own agent" — a real but smaller claim, and one worth checking against their release timelines before committing fully to the build.

And scoring full-chain success automatically needs a reliable judge for whether each step's output was actually correct, not just plausible-sounding — for the vision-extraction step in particular, that likely means either ground-truth-labeled task assets or a calibrated vision judge, neither of which is a solved piece of the MVP yet. Finally, the population this serves — teams running voice+vision+tool-use agents in production — is smaller today than pure-voice or pure-vision agent builders, which could mean a longer road to adoption even if the benchmark itself holds up.

Surfaced from `research/2026-11-14-voice-multimodal-agents.md`, pattern `P9`.
