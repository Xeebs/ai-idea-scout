# Phone Line Tuned: An Open Narrowband Augmentation Pipeline for Turn-Detection Models

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-14-voice-multimodal-agents.md · P2
- **Maturity verdict**: OPEN — GitHub search of open turn-detection checkpoints (`pipecat-ai/smart-turn`, `TurnWave`, `vogent/Vogent-Turn-80M`, `miuda-ai/smart-turn-rs`) found fine-tunable models but none documenting training or evaluation on narrowband (8kHz) phone audio; LiveKit's own docs only suggest VAD-threshold tweaks, not a turn-detection fine-tune. The only evidence of this actually being solved is one contributor's own unpublished measurement (`timbal-ai/timbal#242`): 18.05% caller cutoffs on simulated phone audio vs. 9.86% wideband, improved to 8.64% with a one-off phone-audio-augmented fine-tune. No published dataset, augmentation pipeline, or benchmark surfaced.
- **Format**: PROJECT
- **Data Sources**: CONNECTED — the base augmentation pipeline uses publicly downloadable open speech corpora (LibriTTS, Mozilla Common Voice, VoxPopuli), which already exist and are mature, degraded synthetically through standard telephony codec simulation (G.711/G.729 + bandpass filtering); teams wanting to further fine-tune on their own real call traffic can optionally connect their own Twilio or Telnyx call-recording API (both mature, already-existing APIs) to supply real narrowband audio instead of only simulated.

## The Gap
General-purpose turn-detection models trained on wideband audio mis-fire far more often on real phone-channel (narrowband) audio, cutting callers off roughly 1.8x as often — a measured, cited number from one contributor's roadmap issue, not a published study. Every open turn-detection checkpoint found in this run is fine-tunable in principle, but none ships training or evaluation data for the narrowband case, so every team deploying a voice agent over PSTN is silently inheriting a worse interruption-handling model than they'd get on WebRTC, with no way to know it without running their own measurement first.

## The Project
A standalone, open-source data augmentation pipeline that takes any wideband turn-detection training/eval set and degrades it realistically to match real phone-channel conditions — codec compression (G.711 µ-law/a-law, G.729), bandpass filtering to the narrowband envelope, and injected line noise/jitter profiles sourced from real carrier characteristics — plus a published, reusable benchmark corpus so any team can evaluate their chosen turn-detection model's false-cutoff rate on realistic phone audio before deploying, not after a complaint. The pipeline also ships reference fine-tuned checkpoints for the popular open models (Smart Turn, Vogent-Turn-80M) so most teams can just swap a checkpoint rather than run their own training.

## Tangible Impact
**Population**: teams running AI voice agents over real telephone lines (PSTN/SIP trunking) rather than WebRTC-only web calls — call centers, appointment-booking IVR replacements, and voice-agent platform vendors (LiveKit, Pipecat, Vogent integrators) whose downstream customers all inherit this gap. Telephony-based voice-agent deployment is the dominant production use case (phone support lines, outbound sales/collections calls), far larger than browser-based voice demos.
**Mechanism**: a team adopting the augmented checkpoint or running their own fine-tune through the published pipeline measurably reduces false caller-cutoffs — the single most visible, complaint-generating failure mode in production voice agents (a caller who gets cut off mid-sentence assumes the system is broken, not that it's a tuning gap).
**Measure**: false-cutoff rate on a held-out real-phone-audio benchmark, before/after adopting the augmented checkpoint (target: matching or beating the cited 8.64% improved rate); caller complaint/escalation rate in a pilot deployment; number of independent teams adopting the published checkpoint vs. their own ad hoc fine-tune within 90 days.

## Why Now
Turn-detection models (Smart Turn, Vogent-Turn) only reached open, fine-tunable maturity in the last several months, and the one documented phone-audio measurement surfaced in this digest cycle is brand new (Nov 4, 2026) — the gap is concrete, recent, and the base models to fine-tune already exist, so this is a data-engineering project, not a research bet.

## MVP Sketch
Scope: build the codec-degradation augmentation script (Python, `sox`/`ffmpeg` + a G.711/G.729 codec library), apply it to a 5,000-utterance slice of an existing open turn-detection training set, fine-tune Vogent-Turn-80M on the augmented set, and publish a 200-call held-out benchmark (half simulated-narrowband, half real recorded phone audio if obtainable via a volunteer SIP trunk) with false-cutoff-rate as the headline metric. Target: 2-3 weeks for one person with telephony/audio-ML experience, since the augmentation logic and fine-tuning loop are both well-understood, mechanical work once the degradation profile is right.
- The validating experiment: does the augmented-fine-tuned checkpoint cut the false-cutoff rate on real (not just simulated) phone audio by a comparable margin to the cited 18.05%→8.64% result — if it doesn't generalize past synthetic degradation, that's the project's central risk, worth testing first.

## Risks & Open Questions
- The one data point behind this gap is a single contributor's self-reported measurement on simulated phone audio — the project's first job is independently reproducing it before building further, since it could be noisier or less generalizable than it looks.
- Real carrier audio varies more than any synthetic codec simulation captures (jitter, packet loss patterns differ by carrier and geography); a pipeline tuned only on synthetic degradation may not transfer to real SIP trunk audio from actual telecom providers.
- Obtaining real phone-channel benchmark audio at volume requires either a volunteer SIP trunk partnership or paying for call minutes — a nontrivial logistics cost for a small team, separate from the ML work itself.
- If one of the open turn-detection projects (Smart Turn, Vogent) ships its own narrowband fine-tune first, this project's value shifts from "only option" to "independent benchmark," which is still useful but less differentiated.
