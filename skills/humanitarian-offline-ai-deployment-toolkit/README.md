# Offline Humanitarian AI Deployment Planner

A self-contained prompt template for drafting a concrete offline/intermittent-connectivity deployment plan for a humanitarian or low-resource AI project — the packaging format, sync approach, inference runtime, and field-condition test checklist a team needs before they build anything. Paste the block below into any AI chat tool (Claude, ChatGPT, Copilot Chat, etc.) along with your project details.

## When to use this

Use this the moment you're planning how to get an AI model running in a crisis zone or low-connectivity setting — a clinic, a disaster-response team, a field survey, a crop-advisory deployment — and need a kickoff-stage plan before committing engineering time to building packaging, sync, and runtime infrastructure from scratch. This is a one-time planning exercise, not a tool that deploys, monitors, or syncs anything itself.

## Data source

**Manual.** You describe your project in text when you use this — there is no API or connector involved. This skill never reads live device telemetry, a Mobile Device Management system, or real sync logs on its own. If you have that data and want it factored into the plan, paste the relevant numbers or summary into the conversation yourself.

## What to hand over

Before running this, gather:

1. **Domain and task** — what the model does (e.g., "mosquito-species classifier from phone photos," "symptom-triage checker for a clinic laptop," "crop-disease advisory from a tablet camera").
2. **Model** — architecture/size and current format if you've chosen one (e.g., "a 7B quantized Llama variant," "a MobileNet CNN already exported to TFLite"). If you haven't chosen a model yet, say so — the plan will recommend a size/format class instead of naming a specific model.
3. **Target device profile** — RAM, storage, and whether it's a phone, tablet, laptop, or single-board computer (e.g. Raspberry Pi-class device). If you genuinely don't know yet, say so.
4. **Connectivity tier** — pick the closest match: never connects again after the initial install, occasional Wi-Fi/cell window (hours to days apart), satellite burst (short scheduled windows), SMS-triggered pull, or "not sure yet."
5. *(Optional)* **Update/log cadence need** — do you need to push model updates to the field, pull usage logs back, both, or neither? A fully static one-way deployment with no sync need at all is a legitimate, simpler answer.

## The prompt

```
You are helping me plan an offline/intermittent-connectivity deployment for a
humanitarian or low-resource AI project. Here are my project details:

- Domain/task: <fill in>
- Model: <fill in, or "not chosen yet">
- Target device: <RAM, storage, device type — or "unknown">
- Connectivity tier: <never connects again / occasional Wi-Fi-cell window /
  satellite burst / SMS-triggered pull / not sure yet>
- Update/log sync need: <push updates / pull logs / both / neither>

Using only this information (ask me directly for anything critical that's
missing or ambiguous — device class and connectivity tier especially, don't
guess silently), produce a deployment plan with exactly these sections:

1. Profile — restate device class and connectivity tier, flagging anything
   you assumed rather than were told.
2. Packaging Recommendation — what format to package the model and runtime
   config in, whether quantization is needed, and why, based on how the
   model size compares to the device's RAM (model under ~40% of RAM is
   comfortable; 40-70% is tight and needs a real-hardware memory test before
   field deployment; over ~70% means this device class is a mismatch — say
   so plainly instead of papering over it).
3. Inference Runtime Recommendation — which runtime wrapper fits (e.g.
   llama.cpp-family for quantized LLMs on laptop/SBC-class hardware; a
   mobile-native runtime like MediaPipe/TFLite/ONNX Runtime Mobile for
   phone-class vision models; ONNX Runtime for cross-platform laptop/SBC
   work), framed as a starting recommendation to validate on real target
   hardware, not a guarantee.
4. Sync Recommendation — matched to my stated connectivity tier: no sync
   layer at all if I said "never connects again" (recommend a manual
   re-flash procedure instead); a queue-and-reconcile protocol (local
   write-ahead log, idempotent writes, push/pull on any detected
   connection) for an occasional window; the same approach sized to a
   bandwidth-constrained burst, with critical data prioritized over bulk
   data, if I said satellite burst or SMS-triggered pull.
5. Field-Condition Test Checklist — concrete, checkable items including at
   minimum: cold-start load time on real target hardware, behavior under a
   fully dropped connection for my worst-case expected outage duration,
   partial/out-of-order sync delivery, low-battery/low-storage degradation,
   and one real end-user usability pass in the actual field language and
   literacy context.
6. Out of Scope / Open Risks — state plainly that this is a plan, not a
   build: someone still has to implement the packaging, sync queue, and
   runtime integration, and run every checklist item on real hardware, not
   a simulator. Flag if my domain likely has data-sovereignty or regulatory
   constraints (e.g. health data staying in-country) that need separate
   legal review this plan doesn't cover.

Guardrails: never invent a specific benchmark number, exact RAM footprint, or
quantization behavior that isn't something you actually know — say "validate
on real hardware" instead of presenting a guess as fact. Never silently
assume my device class or connectivity tier if I didn't state it clearly —
ask me first. Never recommend a sync protocol if I said I have no
update/log need at all. Never claim this plan is field-tested or validated —
it's a starting design. Don't weigh in on whether my domain model itself
(e.g. a triage classifier's clinical accuracy) is safe or correct — that's a
separate evaluation I own, not something this plan covers.
```

## What you get back

A plan broken into exactly the six sections above: Profile, Packaging Recommendation, Inference Runtime Recommendation, Sync Recommendation, a checkbox-style Field-Condition Test Checklist, and an Out of Scope / Open Risks section naming what still needs building and testing on real hardware. It is a kickoff-stage design document, not working code and not a validated deployment.

## Guardrails (built into the prompt above)

- Never invents specific benchmark numbers, RAM footprints, or quantization behavior — flags uncertainty and recommends real-hardware validation instead.
- Never silently assumes device class or connectivity tier — asks directly when either is missing or ambiguous.
- Never recommends a sync protocol for a project that has no update/log cadence need — a static one-way deployment is a valid, simpler answer.
- Never presents the plan as field-tested — it is always framed as a starting design a team still has to build and test.
- Never evaluates the domain model's own correctness or safety (clinical, agricultural, legal judgment) — scoped strictly to deployment plumbing.
