---
name: humanitarian-offline-ai-deployment-toolkit
description: Drafts a concrete offline/intermittent-connectivity AI deployment plan (packaging format, sync cadence, inference runtime, field-condition test checklist) for a humanitarian or low-resource project, given its domain, model, and device/connectivity profile. Use at project kickoff, before any packaging/sync infrastructure gets built.
---

# Offline Humanitarian AI Deployment Planner

## When to use this
Use this the moment someone describes a humanitarian, NGO, or low-resource AI project (health triage, disease-vector ID, crop advisory, disaster logistics, education, etc.) that must run in a crisis zone or low-connectivity setting, and asks something shaped like: "how should we deploy this model in the field," "what's our offline strategy," "help us plan sync for intermittent connectivity," or "what do we need to test before we ship this to the field." This is a one-time planning task run at or near kickoff, before engineering commits to a packaging/sync/runtime stack — not a tool that runs the deployment, monitors devices, or executes syncs itself.

## Inputs
**Data source**: Manual — the user describes their project in text; there is no connector. This skill never reads live device telemetry, a Mobile Device Management API, or production sync logs — if the user has that data and wants it factored in, they paste the relevant numbers/summary as text.

Ask for, if not already given:
1. **Domain and task** — what the model does (e.g. "mosquito-species classifier from phone photos," "triage symptom checker for a clinic laptop," "crop disease advisory from a tablet camera").
2. **Model** — architecture/size and current format if known (e.g. "7B quantized Llama variant," "a MobileNet-based CNN already exported to TFLite," or "not chosen yet" — if unchosen, the plan recommends a size/format class rather than a specific model).
3. **Target device profile** — RAM, storage, and whether it's a phone, laptop, tablet, or single-board computer. If unknown, ask directly; do not assume a smartphone by default — humanitarian deployments split meaningfully between phone, laptop, and SBC classes with different packaging implications.
4. **Connectivity tier** — one of: never connects after initial load, occasional Wi-Fi/cell window (hours to days), satellite burst (short scheduled windows), SMS-triggered pull, or "don't know yet." If "don't know," the plan defaults to the most conservative tier (never connects after initial load) and states this explicitly.
5. *(Optional)* **Update/log cadence need** — does the project need to push model updates to the field, pull usage logs back, both, or neither (a static one-way deployment with no sync need at all is valid and simplifies the plan significantly).

## Procedure
1. **Classify the device class** (phone / laptop-or-tablet / single-board-computer) and **connectivity tier** (per the five options above) from the inputs. If either is ambiguous or missing after one round of asking, state the assumption made and flag it as unverified in the output — never silently pick one.
2. **Recommend a packaging format** based on model size and device class:
   - Model fits comfortably in device RAM with room for the runtime (roughly model size < 40% of device RAM) → a single versioned bundle (weights + runtime config + a manifest listing exact runtime version) is sufficient.
   - Model is tight against device RAM (40-70%) → recommend the smallest viable quantization tier for the chosen runtime and flag that a load-time memory test on real hardware (not a simulator) is mandatory before field deployment.
   - Model exceeds ~70% of device RAM → recommend against that device class entirely; name the gap explicitly rather than proposing a packaging workaround that papers over a hardware mismatch.
3. **Recommend an inference runtime wrapper** matching the model format and device class (llama.cpp-family for quantized LLMs on laptop/SBC; a mobile-native runtime such as MediaPipe/TFLite/ONNX Runtime Mobile for phone-class CNN/vision models; ONNX Runtime for cross-platform laptop/SBC vision or tabular models). State this as a starting recommendation the team validates on their actual target hardware, not a guarantee.
4. **Recommend a sync cadence and protocol matched to the connectivity tier**:
   - Never connects after initial load → no sync protocol needed; recommend a manual re-flash/re-deploy procedure instead and say so plainly rather than inventing an unnecessary sync layer.
   - Occasional Wi-Fi/cell window → a queue-and-reconcile protocol (local write-ahead log, push/pull on any detected connection, idempotent writes so a partial sync never corrupts state).
   - Satellite burst or SMS-triggered pull → the same queue-and-reconcile approach, sized to fit the burst window (recommend batching and prioritizing: critical logs/updates first, bulk data last) and explicitly flag that burst-window bandwidth must be measured on the real link before committing to a batch size.
5. **Draft a field-condition test checklist** — concrete, falsifiable items tailored to the stated device/connectivity profile, always including at minimum: cold-start load time on target hardware, behavior under a fully-dropped connection for the expected worst-case outage duration, partial/out-of-order sync delivery, low-battery/low-storage degradation behavior, and one real end-user usability pass in the actual field language/literacy context (not just a lab test).
6. **Name what this plan does NOT cover**: it is a plan, not a build — someone still has to implement the packaging CLI, the sync queue, and the runtime integration, and still has to run the checklist on real hardware, not simulated conditions. If the user's own humanitarian domain has known regulatory/data-sovereignty constraints (e.g. health data must stay in-country), flag that this plan does not address those and the team needs separate legal/compliance review.

## Output format
```
## Offline Deployment Plan: <project name/domain>

### Profile
- Device class: <phone/laptop-or-tablet/SBC> (assumed/stated)
- Connectivity tier: <tier> (assumed/stated)
- Model: <description, size, format if known>

### Packaging Recommendation
<format, quantization tier if relevant, manifest contents, and the RAM-fit reasoning>

### Inference Runtime Recommendation
<runtime wrapper choice and why, flagged as needing validation on real hardware>

### Sync Recommendation
<protocol matched to connectivity tier, or "no sync layer needed" with reasoning>

### Field-Condition Test Checklist
- [ ] <item 1>
- [ ] <item 2>
...

### Out of Scope / Open Risks
<what this plan doesn't cover: implementation, real-hardware validation, legal/compliance>
```

## Guardrails
- Never invent a specific model's exact RAM footprint, benchmark latency, or quantization behavior that wasn't stated or is not well-established public knowledge — flag anything uncertain as "validate on real hardware" rather than presenting a guess as measured fact.
- Never skip asking about device class or connectivity tier when unstated — defaulting silently produces a plan for the wrong deployment target, which is worse than no plan.
- Never recommend a sync protocol for a project that explicitly has no update/log cadence need — a static one-way deployment with no sync layer is a valid, simpler answer and should be given when it fits.
- Never present this plan as validated or field-tested — it is a starting design for a team to build and then test on real hardware; say so explicitly every time.
- Never fold in domain-specific clinical, agricultural, or legal judgment (e.g. whether a triage model's accuracy is acceptable) — this skill plans deployment plumbing only, not the domain model's correctness or safety, which is a separate evaluation the project owns.
