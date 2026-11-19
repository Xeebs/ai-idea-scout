# Voice-Native Core: A Reference Agent Architecture That Treats Speech as the Primary Interaction Mode, Not a Bolted-On Output Layer

Almost every voice agent shipping today was born as a text chatbot. The reasoning loop was written, tested, and tuned entirely in text, and only afterward did someone wire a text-to-speech engine onto the end of it. That ordering is invisible to users until the moment it isn't — the beat of silence after you stop talking, the "thinking" pause before the agent answers, the slightly-too-late interruption handling that makes a call-center bot feel like a call-center bot. The plumbing for *fast* voice output has gotten very good. The reasoning loop driving that plumbing mostly hasn't caught up.

## The Gap

Two independently-dated practitioner essays, surfaced in the same research pass, name this blind spot from different angles. One is titled, bluntly, "Voice feels like the underrated output layer for AI agents" (bittide.aicompass.dev). The other, "Building for Voice In, Visuals Out" (allenpike.com, also discussed on Hacker News), makes the stronger claim: for a two-way voice conversation to feel fluid, "the latency bar is about 200ms" — and the implication is that most systems, designed output-last, simply don't hit it.

That's not for lack of infrastructure. A look at what's actually shipped — AgentScope's three-layer voice design, Telnyx's Agent SDK voice mixin, the streaming-synthesis-before-full-text patterns in LiveKit and Pipecat — confirms the audio transport problem is solved. But every one of those frameworks makes the same architectural choice on purpose: the agent's core reasoning stays ignorant of the fact that it's talking at all. Voice is a mixin, a swappable layer, an adapter clipped onto a text-first core. That's precisely the bolted-on pattern both essays are calling out, not a counterexample to it. No framework found inverts the assumption and builds turn-taking and incremental response generation into the reasoning loop itself, as a first-class concern from the start.

## The Project

The fix isn't a faster TTS engine — that part is already fast. It's restructuring what the reasoning loop treats as its unit of output. Instead of "generate the full text response, then hand it to TTS," the model is driven to emit committable partial utterances: short, semantically self-contained chunks it's confident enough won't need revision, synced directly into a streaming synthesizer as they're produced. Turn-taking itself becomes a first-class abstraction the reasoning loop consults directly — an explicit state machine (listening / thinking / committing / speaking / interrupted) — rather than a boolean flag some app-layer code checks after the fact.

Concretely, that's three pieces: a chunked-commit reasoning wrapper that decides when a partial thought is safe to start speaking, a turn-state machine library the reasoning loop treats as ground truth, and transport adapters for LiveKit and Pipecat so a team migrating doesn't have to rebuild audio plumbing that already works — only the boundary between reasoning and speech.

## Tangible Impact

**Population**: small teams building latency-sensitive, voice-first consumer products — AI phone triage/support lines, in-car voice assistants, voice-dictation copilots for drivers — currently shipping on a text-first core with a TTS adapter glued on; and, downstream, the much larger population of phone callers and voice-assistant end users (per Edison Research's long-running Smart Audio Report, roughly a third of U.S. adults own a smart speaker and regularly interact by voice) who experience the perceptible "thinking pause" and unnatural turn-taking these bolted-on architectures produce.

**Mechanism**: a reasoning loop that can start speaking a confident partial thought while still reasoning about the rest cuts the gap between "user stops talking" and "agent starts talking" below the ~200ms naturalness threshold the essays cite, instead of waiting for a full text response to finish generating before TTS even starts; end users get a conversation that feels responsive instead of a call-center-hold-music cadence.

**Measure**: median time-to-first-audio from end of user utterance (hook on vs. a cascaded text-first baseline); correct barge-in resumption rate on a benchmark call set with scripted interruptions; blind-listener naturalness rating (MOS-style A/B) comparing the voice-native core against the same model wired through a conventional TTS-adapter pipeline.

Both essays naming this gap landed within the same 30-day research window — this is a live, current complaint, not a stale one, and it's arriving at exactly the moment streaming LLM output and streaming TTS have both gotten fast and cheap enough that "wait for the full response, then speak" is no longer a hardware necessity. It persists mostly as architectural inertia inherited from text-first chat frameworks — which is exactly why a reference implementation that inverts the assumption is buildable now rather than blocked on new model capability.

Worth saying plainly: this isn't a slam dunk. LiveKit's own `MultimodalAgent` and Pipecat already hand teams a lot, and some will reasonably judge a from-scratch reasoning core an unnecessary rebuild rather than a new abstraction worth adopting — any serious version of this needs a benchmark that shows a measurable naturalness/latency win, not just an architectural purity argument. The chunked-commit idea also carries its own risk: a model gated on "am I confident enough to start speaking this chunk" can still misjudge and have to awkwardly walk back something it's already said out loud, and getting that confidence threshold right is the actual hard problem here, not a solved implementation detail. And if frontier full-duplex voice models simply swallow the cascaded-reasoning-then-speak question for well-resourced teams, this project's natural audience narrows to teams who still want or need a modular, swappable-model stack rather than a single end-to-end model.

## Try It

A companion Claude Code skill is available at `skills/voice-native-agent-core-architecture/` — a one-time design-review aid, not the reference library itself. Its one-line description, from its `SKILL.md`:

> Audits an existing voice-agent pipeline description/code for the "bolted-on voice" anti-pattern (full-text-before-TTS, turn-state as a boolean flag, no commit-confidence gating, exception-style barge-in) and drafts a prioritized migration plan toward a chunked-commit, state-machine-native core. Use when a team is deciding whether to invest engineering time in redesigning their voice agent's reasoning-to-speech boundary.

To use it: either paste the contents of `skills/voice-native-agent-core-architecture/README.md` into any AI chat tool along with a description (or code) of your own voice pipeline, or drop the whole `voice-native-agent-core-architecture/` folder into `~/.claude/skills/` if you're using Claude Code. It's a static design review, not a live monitor — it works from how your pipeline is structured, not from latency traces, and it's meant to be rerun manually after a migration, not wired in as ongoing instrumentation.

---

Surfaced from `research/2026-11-19-voice-multimodal-agents.md`, pattern `P7`.
