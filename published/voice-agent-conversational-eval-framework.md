# Full Call: A Consolidated End-to-End Conversational Eval Framework for Voice Agents

Five different teams quietly built five different answers to the same question in the last few months — and none of them agree. ServiceNow, Ultravox, Cekura, DeepEval, and a scattering of solo GitHub maintainers all shipped their own voice-agent evaluation tooling in 2026, independently, because none of them trusted — or had even seen — anyone else's. That's not a crowded market. That's five teams who each concluded the market had nothing worth adopting.

## The Gap

ServiceNow's EVA paper puts the core problem plainly: "most existing efforts test components in isolation" — ASR transcription accuracy scored on its own, LLM response quality scored on its own, TTS naturalness scored on its own. A voice agent can ace every one of those component scores and still fail the only test that matters to the person on the other end of the call: did the conversation actually work. Context dropped three turns back, a correction mistaken for a hang-up, a goal quietly abandoned mid-call — these are full-conversation failure modes, and per-component metrics are structurally blind to them.

The telling evidence isn't a single missing tool, it's the pile of almost-tools. Ultravox's own engineering blog admits that none of the existing benchmarks "perfectly addresses our users' specific needs" — so they built a bespoke one. ServiceNow built EVA-Bench and said outright that "no existing benchmark jointly addresses" realistic simulated conversation generation and full-scope failure measurement. A search for independently maintained eval repos turned up at least eight more, built in 2026 alone (ArtemisVoice, VoiceAgentsEval, EVA-Bench's own GitHub cousins, and others), none with meaningful adoption beyond their own authors. Five-plus teams converging on "we have to roll our own" in the same few months is the signature of a real gap, not a solved problem with too many options.

It gets worse once you look at the judge doing the scoring. Most of these efforts lean on an LLM (or audio-native LLM) as the arbiter of whether a call "went well." A Sprinklr paper on judge reliability for voice agents found that reliability is "metric- and configuration-dependent rather than uniform" — in plain terms, the thing teams are using to decide whether their voice agent is good enough to ship is itself unvalidated and inconsistent depending on how you configure it. Nobody has a converged *tool*, and the component most of them share isn't trustworthy to begin with.

## The Project

The fix isn't another bespoke benchmark — that's the failure mode already playing out five times over. It's a consolidation: one open framework that scores full multi-turn spoken conversations end-to-end, using an audio-native LLM-judge whose reliability has actually been checked against human ratings rather than taken on faith. Following the Sprinklr paper's own recommendation, the judge isn't a frozen black box — it ships with a documented reliability interval, calibrated against a human-gold set, so a team knows exactly how much to trust the score instead of treating it as gospel.

Practically, that means a conversation-simulation harness that generates realistic multi-turn test calls rather than scripted happy-path turns; an audio-native judge pipeline anchored to a human-rated calibration set; a failure-mode taxonomy built specifically for full-call voice interactions — context loss across turns, mishandled interruptions, goals that quietly go unresolved — rather than borrowed from text-chat eval; and an adapter layer so a team can point the framework at their own real call recordings instead of starting from zero. The point isn't to out-build EVA-Bench or Ultravox's internal tool from scratch — it's to take the pieces that already exist publicly and bolt them into something teams actually converge on, before one vendor's unvalidated internal tool calcifies into the de facto standard by default.

## Tangible Impact

**Population**: callers interacting with production voice agents built by small and mid-size engineering teams — companies too small to build bespoke eval infrastructure the way ServiceNow or Ultravox did, who currently ship on per-component metrics that miss conversation-level failures.
**Mechanism**: catching multi-turn failure modes (context loss, goal non-resolution, mishandled interruptions) before launch, using a calibrated rather than ad hoc judge, reduces the rate at which these failures reach real callers as a bad call experience or an unresolved issue requiring a callback.
**Measure**: correlation between the framework's calibrated score and real-world call outcomes (CSAT, resolution rate) on a held-out set of real calls; reduction in post-launch incident count for teams adopting the framework vs. a matched baseline; judge-score agreement with human raters on the calibration set.

## Try It

No companion skill has been built for this idea yet — it's tagged for one (`Format: BOTH` in the idea file), but the runtime harness and the Claude Code skill version haven't been written. When it lands, it'll live at `skills/voice-agent-conversational-eval-framework/` and the idea file describes its intended shape: a one-shot audit skill that, given a description of a team's existing voice-agent eval setup, checks it against an audio-native-plus-validated-judge checklist and drafts a gap report and starter failure-mode taxonomy — useful before a team commits to building or adopting the full framework. Check back on this repo's `skills/` directory for its arrival.

## A Reason This Might Already Be Solved (and Why It Probably Isn't Yet)

Worth saying plainly: the fragmentation itself is a double-edged signal. It's evidence of unmet need, but it's also evidence the market might not actually want consolidation — teams may simply prefer bespoke benchmarks tied to their own call types and never converge on a shared tool no matter how good it is. There's also a real platform risk: if LiveKit, Vapi, or another voice infrastructure vendor ships this as a built-in feature first, an independent framework loses most of its reason to exist. And a validated judge needs real human-rated calibration data — expensive to collect, and not guaranteed to generalize across call domains (a customer-support call and a medical intake call fail in different ways). None of that erases the gap documented above; it's just the honest list of ways this could still not work.

---

Surfaced from `research/2026-11-12-voice-multimodal-agents-ii.md`, pattern `P3`.
