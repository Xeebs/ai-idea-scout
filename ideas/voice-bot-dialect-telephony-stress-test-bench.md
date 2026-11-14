# Pareeksha Open: A Combined Dialect x Telephony-Condition Stress-Test Bench for Voice Bots

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-13-voice-multimodal-agents-ii.md · P5
- **Maturity verdict**: PARTIAL — component pieces exist (Sierra's open μ-Bench: 4,270 annotated utterances from real 8kHz phone calls across 5 locales; Maqsam's Arabic call-domain WER/CER benchmark; a Gnani.ai "KathBath Noisy" codec/noise/call-drop dataset, Hindi-only; Cekura's accent-specific scoring tool) but none combines multi-dialect corpora with configurable line-condition simulation into one general-purpose WER/CER-heatmap test bench — the poster's own from-scratch "Pareeksha" tool is a solo build, not a shared standard.
- **Format**: BOTH
- **Data Sources**: MANUAL — the user uploads their own labeled audio + reference transcripts (or points the tool at their own ASR/voice-bot API endpoint) for the dialects/conditions they care about; the tool ships bundled with existing open datasets (μ-Bench, KathBath Noisy) as default reference corpora so a team isn't starting from zero. **Upgrade path (CONNECTED, not in MVP)**: pull real degraded production call audio automatically via a telephony platform's call-recording API (e.g. Twilio Voice Insights) or a team's ASR vendor's own low-confidence-transcript logs, instead of requiring manual curation of a regression set — noted as a roadmap item since no mature cross-vendor "give me your worst transcripts" API exists yet.

## The Gap
r/speechtech's "Pareeksha" poster (2026-11-11) built a from-scratch open-source tool to measure ASR accuracy on Indian dialects under simulated phone-line conditions (WER/CER heatmaps by region x line-condition) after apparently finding nothing off-the-shelf, reporting WER jumping "from 5% on a clean line to [much higher]" once realistic degradation was applied. The gap-analyst confirmed real benchmark fragments exist (μ-Bench, KathBath Noisy, Maqsam, Cekura) but none unify multi-dialect speech with a configurable telephony-degradation simulator into one tool teams can point at their own bot before launch.

## The Project
An open-source CLI/library that takes (a) a labeled multi-dialect/accent speech corpus and (b) a target ASR/voice-bot endpoint, applies a configurable pipeline of telephony-degradation transforms (8kHz A-law/mu-law codec simulation, additive noise at a set SNR, simulated packet loss/jitter) across every dialect in the corpus, runs the bot against each dialect x condition cell, and renders a WER/CER heatmap report (HTML + CSV) showing exactly where a deployment will fail before it goes live on real lines. The novel centerpiece is the cross product itself — dialect x condition, not either axis alone — which is the exact combination no existing component tool performs.

Component list: codec/noise/packet-loss transform library (ffmpeg/sox-based), a pluggable ASR-adapter layer (so any vendor API or self-hosted model can be scored), a bundled starter corpus assembled from the open datasets the gap-analyst found, and a heatmap report generator.

## Tangible Impact
**Population**: Voice-bot engineering and QA teams deploying IVR/call-center/banking-helpline bots into markets with heavy dialect variation and degraded telephony — most acutely in South Asia, the Middle East, and Africa, where the majority of inbound calls arrive over compressed 8kHz mobile/PSTN lines. Downstream, this reaches the hundreds of millions of regional-language and accented speakers in those markets (e.g. India's mobile subscriber base, per TRAI's own public subscriber reporting, runs well over a billion connections, a large share interacting with banking/telecom/government IVR in a regional dialect) who are currently served by bots validated only on clean, standard-accent studio audio.
**Mechanism**: Teams run their own corpus/dialects through the bench pre-launch instead of discovering accent- or line-condition-specific failure only after go-live complaints; the heatmap turns "it sort of worked in testing" into a concrete, fixable pre-deploy checklist.
**Measure**: (1) number of dialect x condition failure cells caught in the bench vs. discovered later via production complaint tickets for the same bot; (2) WER/CER delta between clean-line and worst-simulated-condition scores per dialect, tracked release over release; (3) time to assemble a team's first dialect/line regression suite (target: hours using the bundled starter corpus, vs. the multi-week from-scratch build the Pareeksha poster did).

## Why Now
Open starter corpora (μ-Bench, KathBath Noisy) and mature audio-degradation libraries (ffmpeg/sox codec and noise simulation) already exist as free, usable building blocks — the only missing piece is the integration layer and heatmap tooling, which is squarely buildable with current technology; no model-capability wait is required.

## Skill Angle
A companion skill takes a team's existing production failure logs or support-ticket excerpts (pasted in) and drafts a prioritized dialect x condition test matrix — which combinations to run first, based on where the pasted failures cluster — before anyone commits to running the full bench. This is a one-shot judgment/prioritization task, independently useful even for a team not yet ready to stand up the full tool.

## MVP Sketch
2-4 week MVP: a Python CLI that (1) bundles a small slice of μ-Bench + KathBath Noisy as the default corpus, (2) implements three degradation transforms (clean passthrough, 8kHz codec simulation, additive noise at a configurable SNR), (3) accepts a user-supplied ASR endpoint (API key/URL) or a local whisper-class model, (4) outputs a WER/CER heatmap as a static HTML report. Single experiment: run one real IVR bot's ASR endpoint against the bundled corpus and confirm the heatmap surfaces at least one dialect/condition combination with meaningfully worse WER than the bot's own reported baseline.

## Risks & Open Questions
- Licensing/access terms for the cited open datasets (μ-Bench, KathBath Noisy) need verifying before bundling them directly rather than linking to them.
- Degradation simulation (codec/noise/packet-loss) is a reasonable proxy for real line conditions but won't perfectly replicate every carrier's actual signal path — the tool should be positioned as a pre-launch filter, not a certification.
- If a well-resourced voice-AI eval vendor (Coval, Hamming, Cekura) ships this exact combined capability before launch, the differentiation collapses to "open-source and self-hostable" alone — still valuable, but a narrower pitch.
- Scope creep risk: resist the urge to support every language/dialect in v1; a working 3-5-dialect proof beats a half-working universal claim.
