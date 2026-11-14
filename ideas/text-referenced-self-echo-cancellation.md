# Hear Myself Not: A Vendor-Agnostic Text-Referenced Self-Echo Filter for Voice Agent STT

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-14-voice-multimodal-agents.md · P7
- **Maturity verdict**: PARTIAL — confirmed shipped as Soniox STT v6 (`stt-rt-v6`/`stt-async-v6`, Nov 3 2026), streaming the agent's own outgoing TTS text into the STT model to filter it from the transcript (Soniox blog, marktechpost, voiceaispace.com). But it's a single vendor's proprietary feature under two weeks old; the only independent test found used synthetic audio only with no real-device testing noted, and no second vendor or open-source implementation surfaced.
- **Format**: PROJECT
- **Data Sources**: CONNECTED — the middleware hooks directly into the voice-agent runtime's own TTS output stream (the text and timing of what the agent is currently generating/speaking) via the agent framework's existing event hooks (LiveKit Agents and Pipecat both already expose TTS-generation and STT-input hooks maturely); no third-party API or user-pasted data is involved, since both signals it fuses already live inside the agent's own running pipeline.

## The Gap
Soniox just shipped a proprietary technique — feeding an agent's own generated text into the STT step to filter the agent's voice out of the transcript, instead of relying purely on acoustic echo cancellation (AEC) — but it's locked to one vendor's STT product, tested only on synthetic audio, and has no second implementation anywhere. Every team using a different STT engine (Whisper-based, Deepgram, open-source) is stuck with acoustic-only AEC, which fails on cheap hardware (speakerphones, low-end headsets, robotics platforms) where echo cancellation hardware/software is weak — causing the agent to transcribe and react to its own voice.

## The Project
A standalone, STT-engine-agnostic middleware that sits between a voice agent's TTS output and its STT input: it tracks what text the agent is currently speaking (with word-level timing estimated from TTS phoneme/duration output), and post-filters the STT transcript by aligning and subtracting segments that match the expected self-speech, semantically and temporally — not just acoustically. Unlike Soniox's built-in version, this is a drop-in layer any STT engine can sit behind, open-sourced and benchmarked on real recorded hardware (not just synthetic audio), closing the exact gap the one independent test flagged.

## Tangible Impact
**Population**: teams building voice agents on open or non-Soniox STT stacks (Whisper.cpp, Deepgram, local models) deployed on hardware with weak acoustic echo cancellation — robotics/kiosk voice interfaces, cheap speakerphone-based call setups, and full-duplex agents where the agent may be speaking while still listening for barge-in. This specifically targets builders who can't just switch STT vendors to get Soniox's fix.
**Mechanism**: the middleware removes self-transcribed segments that acoustic AEC alone missed, preventing the agent from interpreting its own speech as user input — the failure mode that causes an agent to respond to itself in a loop or falsely register a "barge-in" that was just the agent's own voice bleeding back into the mic.
**Measure**: self-transcription false-positive rate (fraction of self-speech incorrectly transcribed as user speech) on a real-hardware test set, before/after the middleware, specifically on weak-AEC hardware; false barge-in rate attributable to self-echo in a live pilot; latency overhead added per utterance (must stay under ~50ms to not itself become a barge-in problem).

## Why Now
Soniox's Nov 3, 2026 release proves the core technique works and is commercially viable just weeks ago — the gap now is purely about generalizing it past one vendor's closed STT, which is squarely an engineering integration problem, not a research one, since TTS timing/text and STT transcript streams are both already exposed by mature agent frameworks.

## MVP Sketch
Scope: a Python middleware package hooking into LiveKit Agents' TTS-output and STT-input event streams, implementing text/timing alignment (Levenshtein-style fuzzy match between expected self-speech text and STT output within the expected time window) to strip matched segments before the transcript reaches the agent's reasoning step. Validate on a 50-utterance real-hardware test (a cheap USB speakerphone with known weak AEC) comparing self-transcription false-positive rate with AEC-only vs. AEC+this middleware. Target: 2-3 weeks for one audio-ML engineer, since the TTS/STT hooks already exist in the chosen framework and the novel work is the alignment logic.

## Risks & Open Questions
- Word-level TTS timing estimates are inherently approximate (they come from the TTS model's own duration prediction, not ground truth), so the alignment window must be generous enough to catch drift without accidentally stripping real overlapping user speech — this tradeoff needs real tuning, not a guess.
- If Soniox's technique generalizes poorly even for Soniox on real hardware (the thing the one independent test couldn't confirm), that's a signal this entire pattern might not work as well as the vendor claims — worth testing against Soniox's own output on the same real-hardware set as a sanity check before building further.
- A team willing to just switch to Soniox gets this for free without building anything — the project's value is specifically for teams locked into a different STT stack for other reasons (cost, self-hosting, language coverage), which narrows but doesn't eliminate the addressable population.
- Full-duplex models (P6 in the same digest) sidestep this problem architecturally rather than patching it — if full-duplex adoption accelerates faster than expected, this middleware's relevance window could be shorter than it looks today.
