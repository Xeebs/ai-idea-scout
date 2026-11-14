# Session-Degradation Risk Reviewer

A self-contained prompt template for reviewing a voice+vision agent's architecture and getting a concrete recommendation for when and how to "re-anchor" its visual grounding during long sessions — before you build the live re-anchoring loop itself.

## What this is for

Voice-driven agents that watch a screen share, a video feed, or a live camera continuously — rather than processing one uploaded image — tend to degrade in visual accuracy as a session runs on. Practitioner reports in production put the start of noticeable degradation at roughly the 30-second mark of continuous visual engagement: the agent starts giving instructions based on stale on-screen state (telling someone to click a button that's already gone, describing a screen that's since changed). The fix pattern — periodically re-sampling a fresh frame and re-injecting a short "what's changed" summary into the model's context — is proven in offline research benchmarks, but deciding how often to do it, and with what payload, for *your specific agent* is a design decision nobody has made for you yet.

This skill is that design decision. It is **not** the live middleware that actually watches your video stream in production — it's the step before that: you describe your agent's architecture in plain text, and it gives you back a concrete cadence, payload, and cost tradeoff to implement.

**Data source: manual.** You paste or type a short description of your agent's architecture into the chat. This skill never connects to a live video feed, API, or data source — everything it reasons about comes from what you tell it in the conversation.

## When to use it

- You're building a voice+vision agent (screen-share support, live tutoring/walkthrough, voice-first screen reading for blind/low-vision users) that holds a session open past roughly 30 seconds of continuous visual engagement, and you want to know upfront how aggressively to re-anchor its visual context.
- You already have one live and you're seeing it reference stale screen state — telling users to interact with elements that have moved or disappeared, or describing a screen that's already changed — and want a concrete remediation plan instead of guessing at a fixed timer.

## What to hand over

Before asking for a recommendation, give the assistant these six things (if you don't know one, say so — it will ask a follow-up rather than guess):

1. **Typical session length** — median and max duration of a real session.
2. **What the agent is watching** — a static document, a slowly scrolling page, an actively edited IDE/spreadsheet, a live camera, a multi-step UI workflow.
3. **How often the visual content changes** — roughly how many meaningfully different screen/scene states happen per minute in a typical session.
4. **The underlying multimodal model**, and any known context-window or session-length caveats for it.
5. **Per-turn latency budget** — how much added delay a re-anchoring event can afford before it breaks the real-time feel of the voice interaction.
6. **Any symptoms you've already seen**, if the agent is live (specific examples of stale-state references).

## The prompt

Paste the following into any AI chat tool, filling in your own details for the six inputs above:

```
You are reviewing the architecture of a voice+vision agent for visual-grounding
degradation risk. Here is my agent's architecture:

1. Typical session length: <your answer>
2. What it watches: <your answer>
3. Visual change frequency: <your answer>
4. Underlying multimodal model: <your answer>
5. Per-turn latency budget: <your answer>
6. Known symptoms (if any): <your answer>

Using this information, produce a structured brief with these exact sections,
in this order:

1. Inputs used — restate what I gave you, and flag anything you're assuming
   because I didn't specify it.
2. Risk profile — one paragraph: is my session type high, medium, or low risk
   for mid-session visual-grounding degradation, and why? Reason explicitly
   against a ~30-second degradation reference point reported by practitioners
   running continuous voice+vision sessions in production (name this
   explicitly as one practitioner's measured observation, not a universal
   constant) and against my stated change frequency.
3. Recommended cadence — give me both a fixed-timer fallback (a concrete
   number of seconds) and an adaptive rule (a plain-language trigger
   condition based on detected visual change) for how often to re-anchor
   the model's visual context.
4. Recommended anchor payload — for each cadence tier, tell me whether the
   re-anchor should be a full fresh frame re-sample, a lightweight
   diff/summary of what's changed since the last anchor, or both, and why,
   weighed against my stated latency budget.
5. Cost/latency tradeoff — one short paragraph on what my recommended
   cadence costs me in added latency and vision-token spend versus a more
   conservative cadence.
6. Evaluation plan — 3 to 5 concrete steps for how I could validate this
   recommendation using real recordings of my own sessions (what to record,
   what to label, what "correct" means).
7. Caveats — at minimum, flag that the 30-second figure comes from one
   practitioner's testing and that my own evaluation data should be the
   final word, not this brief.

If I didn't give you one of the six inputs, ask me for it specifically
before producing the brief — do not guess a cadence without it. Do not
recommend the most aggressive possible cadence by default; always weigh it
against my stated latency budget. Do not claim this brief alone validates
anything — only real session data can do that.
```

## What you get back

A single structured brief in the seven sections above: what inputs were used, a risk-level call with reasoning, a concrete fixed-cadence number plus an adaptive rule, a payload recommendation per cadence tier, a plain-language cost tradeoff, a short evaluation plan you can actually run, and explicit caveats about the limits of the recommendation.

## What this does not do

- It does not read your live video or screen-share stream — you describe your architecture in text; it never connects to anything.
- It does not implement the re-anchoring scheduler itself — that's a separate build (a LiveKit Agents or Pipecat plugin that actually watches frames and injects anchors in real time).
- It does not replace running your own evaluation on real session recordings — treat its cadence number as a starting hypothesis, not a final answer.
