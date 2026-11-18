# Dispatch Shield: Real-Time Voice-Liveness Detection Tuned for Emergency/911 Call Audio

- **Status**: PROPOSED
- **Date**: 2026-11-17
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-17-voice-multimodal-agents.md · P9
- **Maturity verdict**: PARTIAL — Pindrop Pulse, ValidSoft, and Mitek sell mature voice-liveness/deepfake-detection products, but every one targets financial-services/contact-center fraud, none mentions 911 or public-safety deployment, and a third-party benchmark (DeepFake-Eval-2024) reports commercial detectors fall to ~45-50% accuracy on noisy phone-call audio — the exact channel this gap is about.
- **Format**: BOTH
- **Data Sources**: CONNECTED (project) — live call audio streamed from the PSAP's CPaaS/SIP trunk or NG911 i3 audio feed (mature streaming APIs exist, e.g. Twilio Voice Media Streams); no liveness model trained/evaluated for this specific noisy-telephony channel exists yet, which is the gap being built. MANUAL (skill companion) — a single recorded call (wav/mp3) a supervisor or investigator uploads after the fact.

## The Gap
A Hacker News thread (Nov 11 2026, 12pts/4cmt, linking NPR reporting) describes swatters using AI-cloned voices to deceive 911 dispatchers, framed as an ongoing, worsening, currently-unmitigated problem — no vendor or open-source countermeasure surfaced anywhere in search. The mature commercial liveness-detection market exists but is built and evaluated for a different channel (clean-ish contact-center/banking audio), and independently benchmarks poorly (~45-50% accuracy) on the noisy, compressed audio that defines actual phone-call conditions, let alone emergency-dispatch audio specifically.

## The Project
A real-time (first few seconds of a call) voice-liveness/synthetic-speech classifier purpose-tuned and evaluated specifically on noisy, compressed, emergency-dispatch-grade telephony audio — the acoustic conditions that make existing commercial detectors fail — delivered as a non-blocking risk score to the dispatcher's call-handling console alongside ANI/caller-ID cross-checks, with a published accuracy benchmark on that noisy-channel audio so the tool's real performance is known rather than marketed.

## Tangible Impact
**Population**: U.S. 911 dispatch centers/PSAPs — there are roughly 6,000 PSAPs nationwide per federal 911 program data — and, downstream, people subjected to an armed police response triggered by an AI-voice-spoofed "swatting" call, a problem the HN thread and underlying NPR reporting describe as actively worsening through 2026. Dispatchers themselves currently have zero tooling for this specific threat.
**Mechanism**: Giving dispatchers a liveness-risk score tuned for real 911-audio conditions — instead of nothing, as today — lets them apply extra verification (callback, address cross-check) before escalating to an armed response, reducing wrongful SWAT deployments triggered by spoofed calls.
**Measure**: (1) detection precision/recall on a noisy-911-audio benchmark vs. the ~45-50% DeepFake-Eval-2024 baseline for commercial detectors; (2) number of flagged-and-independently-verified spoofed calls in a pilot PSAP; (3) change in false armed-response dispatch rate for flagged vs. unflagged suspicious calls in a pilot study.

## Why Now
Swatting-via-AI-voice is reported as actively worsening right now (Nov 2026), and the exact reason existing commercial detectors don't help — they were built and evaluated on the wrong audio channel — is now independently documented (DeepFake-Eval-2024), giving a concrete, benchmarkable target to build against rather than a vague aspiration.

## Skill Angle
A **forensic audio-review skill**: given one uploaded recorded call, it runs the same liveness model against the file and produces a synthetic-voice-likelihood report with supporting evidence (spectral artifacts, prosody anomalies) — a genuinely separable after-the-fact investigative task a supervisor or investigator can use even without the live dispatch-console integration.

## MVP Sketch
Scope: a classifier fine-tuned on a noisy-telephony-audio dataset (synthetic + real spoofed-call samples, codec-degraded to match real PSAP audio quality), exposed as a streaming inference endpoint plus a benchmark report comparing it against at least one commercial detector on the same noisy test set. Stack: Python/PyTorch model, a lightweight gRPC/WebSocket scoring service, Twilio Media Streams as the reference audio input. Validating experiment: build a 200-clip noisy-911-grade benchmark set (synthetic spoofed + real human calls, codec-matched) and report precision/recall against the DeepFake-Eval-2024 commercial baseline.

## Risks & Open Questions
- Getting realistic, legally usable emergency-dispatch audio for training/eval (vs. synthetic approximations) is a genuine data-access hurdle — PSAP recordings are sensitive and often not public.
- A non-blocking risk score could be ignored under dispatcher time pressure if not integrated carefully into existing CAD workflows — the UX of "flag, don't block" needs real dispatcher-workflow validation, not just model accuracy.
- False positives at 911 scale carry real cost (delayed response to a genuine emergency), so the acceptable false-positive rate is much stricter than in financial fraud use cases.
- An established vendor (Pindrop etc.) could extend into public-safety at any time, given they already have the base liveness technology — the differentiator here is strictly audio-channel tuning and benchmarking, not new detection theory.
