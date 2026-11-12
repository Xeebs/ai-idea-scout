# ArchPick: A Shared Benchmark Harness for the Cascaded-vs-Speech-to-Speech Decision

Every team that sets out to build a voice agent in 2026 eventually hits the same fork in the road — and right now, almost every one of them is navigating it blind, with a spreadsheet and a few weeks they didn't budget for.

## The Gap

The fork is this: do you build a cascaded pipeline — separate speech-to-text, LLM, and text-to-speech models, independently swappable and easy to debug — or a unified speech-to-speech model, where recognition, reasoning, and synthesis are trained together for lower theoretical latency but at the cost of vendor lock-in and much harder observability? There's no shortage of opinions on which is better. There's just no agreement, and no shared way to even ask the question for your own use case.

Two GitHub issues from unrelated small repos make the gap concrete. In `changtimwu/elevenlabs-exp#1`, a team evaluating ElevenLabs Realtime against their existing setup noted flatly: "Do our samples use it today? No. Both agents use the cascaded pipeline." In `thomaseude/t3code-voice#7`, titled simply "Voice engine choice," another team independently listed out the exact criteria they'd need to compare — French-language quality including technical vocabulary, end-to-end latency, barge-in handling, tool-calling reliability — to decide between OpenAI Realtime and a Whisper-plus-LLM-plus-TTS pipeline. Neither team found an existing rubric to reuse. Both built their own from scratch.

Worse, the published guidance actively disagrees with itself. Coval's comparison says speech-to-speech wins on latency. Inworld says a well-engineered cascade can beat it. An AssemblyAI panel found that both of its surveyed teams run cascaded pipelines for roughly 99% of their agents — specifically to avoid vendor lock-in, a factor that has nothing to do with the latency numbers everyone keeps quoting. There is one academic benchmark in this space, EVA-Bench (arXiv 2605.13841), which runs live multi-turn simulations across both architectures — but it's a fixed leaderboard, not something a team can point at their own call scripts and their own compliance constraints. When the generic published numbers don't answer "does this handle our technical French vocabulary," teams are left re-deriving the whole evaluation themselves.

## The Project

ArchPick is a benchmark harness a team points at their own problem, not someone else's. You hand it the thing that actually matters — representative call scripts, the languages and vocabulary your domain demands, your latency and cost budget — and it runs those exact scenarios through a reference cascaded stack (Whisper or Deepgram plus an LLM plus a TTS provider) and a reference unified speech-to-speech stack (OpenAI Realtime, Gemini Live, or similar), scoring both on latency percentiles, barge-in handling, tool-calling reliability, and per-minute cost.

The output isn't a leaderboard entry — it's a decision report built from your domain, with your numbers. That's the whole point: the two GitHub issues that motivated this didn't fail because no comparison existed anywhere, they failed because every comparison that existed was generic. A harness that scores both architectures against a team's own scenarios turns "does OpenAI Realtime handle our technical insurance-claims vocabulary as well as our cascaded pipeline does" from a multi-week bake-off into a question with a number attached.

## Tangible Impact

**Population**: small (2-8 person) engineering teams building vertical voice agents for a specific domain — healthcare intake, insurance claims, multilingual customer support, recruiting screening — who currently must choose a voice architecture with no shared tooling, evidenced by two independent small-repo GitHub issues each re-deriving comparison criteria from scratch rather than reusing an existing rubric or harness.

**Mechanism**: a runnable harness that scores both architectures against a team's own representative scenarios collapses what is currently a multi-week, ad hoc bake-off (standing up both stacks, writing eval scripts, manually scoring transcripts) into a day-long, repeatable run with domain-specific numbers — and reduces the downstream cost of picking wrong, since migrating a shipped voice agent from one architecture to the other mid-production is expensive (new integration, new observability, re-validated compliance for regulated domains like healthcare intake).

**Measure**: time from "we need to decide" to a documented architecture decision, compared against the multi-week ad hoc baseline implied by the two GitHub issues; rate of teams who re-platform (regret rate) within 6 months of their original choice; correlation between the harness's predicted latency/cost numbers and the team's actual production numbers post-launch.

## Try It

No companion skill has been built for this idea yet. The idea file sketches a quick-triage skill angle ("voice architecture triage" — a same-day structured recommendation for teams who need a direction before investing in full benchmarking) as a future companion to the harness, but it hasn't been synthesized or tested yet. Check back on `skills/voice-architecture-decision-benchmark-harness/` in a future cycle, or build the MVP harness described above yourself: two reference stacks, one scenario format, one comparison table.

Worth naming up front: EVA-Bench already exists as an academic benchmark, so this only earns its keep if it's a practically runnable, team-pointable harness rather than another fixed leaderboard — and the reference implementations will need a real update cadence, since both the cascaded-component APIs and the speech-to-speech model versions ship frequently enough that a stale harness becomes useless within months.

---

Surfaced from `research/2026-11-12-voice-multimodal-agents.md`, pattern `P2`.
