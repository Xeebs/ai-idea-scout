# Tone Match: A Continuous Affect-Conditioned Response Engine for Voice Agents

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-12-voice-multimodal-agents-ii.md · P2
- **Maturity verdict**: PARTIAL (real, runnable research implementations exist — Sympatheia, EmoSteer-TTS (has code), CoCoEmo, a PAD-based TTS framework — but every one is a research artifact with its own author-built evaluation; the only production-facing claim found, VoiceGenie.ai, is unverified marketing copy, not a documented adopted implementation)
- **Format**: PROJECT

## The Gap
Most voice agents still classify user speech into a fixed emotion taxonomy (happy/sad/angry/etc.) and template a response, which a CallSphere practitioner blog calls "unreliable on phone audio." The research direction that actually works better — conditioning the reply and TTS prosody on a continuous valence-arousal signal inferred turn-by-turn — is proven in papers (Sympatheia, AffAdapt, a VR study where 93.3% of 30 participants preferred the affect-aware agent) but has not crossed into a reusable, production-grade component. Every working implementation is a bespoke research pipeline evaluated on its own benchmark; nothing adopted or shipped combines continuous affect inference with response conditioning as a drop-in module.

## The Project
A middleware layer for voice-agent stacks that infers a continuous valence-arousal estimate from the user's speech each turn (using open, runnable approaches like activation-steering TTS or lightweight prosody feature extraction, building on EmoSteer-TTS-style techniques rather than starting from scratch) and feeds that signal into both response content (adjusting phrasing, pacing, de-escalation cues) and TTS prosody, updated continuously rather than per-session. It targets low-acuity, high-emotional-stakes voice interactions where mismatched tone is the actual failure mode, not generic chit-chat.

Components: a per-turn affect estimator, a response-conditioning adapter that nudges an LLM's reply style via the affect signal, a TTS prosody adapter, and an evaluation harness comparing affect-conditioned vs. discrete-taxonomy baselines on a labeled call set.

## Tangible Impact
**Population**: callers to non-clinical check-in and support voice lines that already use AI — e.g., employee-assistance-program wellness check-ins, post-discharge follow-up calls, and benefits/claims support lines where people are reluctant to state distress directly and a mismatched chipper tone increases call abandonment.
**Mechanism**: a continuous affect signal lets the agent detect rising distress or frustration from prosody even when the words themselves are neutral, and adjust tone and pacing (or trigger escalation to a human) before the caller disengages — the gap the discrete-taxonomy approach misses because it only reacts to labeled categories, not a changing trajectory.
**Measure**: caller-reported rapport/comfort score vs. discrete-taxonomy baseline; call abandonment rate; escalation-accuracy (does the system flag genuine distress trajectories that a human reviewer agrees warranted escalation) on a held-out labeled call set.

## Why Now
Activation-steering and LoRA-based continuous affect conditioning for TTS now have open, runnable implementations (EmoSteer-TTS ships code) rather than requiring proprietary training infrastructure, making a production-adjacent middleware buildable on top of existing open models for the first time this year.

## MVP Sketch
Build a per-turn affect estimator using an open prosody-feature or activation-steering approach; wire it into a small response-conditioning layer on top of an existing voice-agent reference stack; run a comparison on a labeled call-recording set (affect-conditioned vs. discrete-emotion-label baseline) scored by human raters for perceived tone-match and by an escalation-accuracy metric. The single experiment: does continuous affect conditioning produce measurably better tone-match and escalation accuracy than discrete-label templating on the same call set.

## Risks & Open Questions
- Affect inference from phone-quality audio is noisy; the MVP's accuracy ceiling may be set by audio quality, not the conditioning approach.
- No validated production eval exists for this exact use case — the project has to build its own labeled call set, which is resource-intensive and could introduce its own biases.
- Over-reacting to a continuous affect signal risks making the agent feel presumptuous or wrong about the user's state, which could be worse than the discrete-taxonomy baseline if not carefully bounded.
- VoiceGenie.ai's unverified marketing claim suggests a vendor may already be close to shipping this, which would shrink the window before this becomes SATURATED.
