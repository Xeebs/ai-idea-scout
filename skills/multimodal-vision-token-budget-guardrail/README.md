# Vision-Token Cost Auditor

A self-contained prompt for auditing how much a multimodal (vision-enabled) agent will actually cost in tokens and dollars once it's handling real traffic — especially an agent that streams continuous video or screen-share frames, where cost can balloon far past what a handful of manual test calls suggested. Paste the prompt block below into any AI chat tool (ChatGPT, Claude, Gemini, etc.), then answer the setup questions it asks.

## When to use this
Use this before shipping a new vision-enabled agent feature, before scaling one to more traffic, or when a vision-agent bill came in higher than expected and you want to know exactly where the spend is coming from. This is a one-time pre-launch/pre-scale audit — it produces a report, not a running system. It is not a general "explain vision tokens" tutorial, and it does not replace actually checking your provider's bill.

## What you need before you start
1. **The code (or a precise description) of every place your agent sends an image, video frame, or screen-share frame to a vision model.** For each one, you'll want to know: which provider/model (OpenAI, Anthropic, Gemini, etc.), the resolution/dimensions of the image being sent, the detail/fidelity setting if there is one (e.g., OpenAI's `low`/`high`/`auto`), and whether it fires once per upload or repeatedly in a loop (continuous video or screen-share capture).
2. **Your traffic assumptions** — how many sessions or requests per day/month, and for any continuous/looping call site, how many frames get sent per session (e.g., "500 sessions/day, one frame every 2 seconds, average 6-minute session").
3. **Which call sites, if any, are doing a precision task** — OCR, detecting small UI elements, fine-grained visual diagnosis — where shrinking the image or lowering fidelity could break correctness, as opposed to call sites that would tolerate resolution loss just fine.
4. **The current price per token (or per image) for your exact model**, pulled fresh from the provider's own pricing page. Token costs for vision drift across model updates, so don't rely on a number from memory — paste the current rate.

If you're running this inside a tool that can read your own files (like Claude Code), you can instead just give it the repository path and let it find the call sites itself — skip re-pasting code it can already read.

## The prompt

```
You are auditing my multimodal agent's vision-token cost before I ship/scale it.

Here is what I'm sending you:
1. Code/call sites: [paste the code for each place that sends an image/frame to a vision
   model, OR describe each one precisely: provider/model, resolution, detail/fidelity
   mode, and whether it's a one-off upload or a repeating loop]
2. Traffic assumptions: [e.g., "500 sessions/day, 1 frame every 2 seconds, 6-minute
   average session" for any looping call site; request volume for one-off sites]
3. Precision-sensitive call sites: [name any that do OCR, UI-element detection, or
   fine visual diagnosis where downscaling would risk correctness — or say "none"]
4. Current pricing: [paste the current per-token or per-image rate from the provider's
   pricing page for the exact model(s) in use]

Do this:
1. For each call site, state the tokenization formula you're using to estimate cost
   (cite which provider's documented rule — tile-based, resolution-based, etc.) and
   flag explicitly if you're not fully certain it's current.
2. Estimate tokens per single call for each call site from its resolution/detail mode.
3. Scale each estimate to a per-session and per-month dollar figure using my traffic
   assumptions. For looping/continuous call sites, this must multiply by frames per
   session, not just treat it as one call.
4. Rank all call sites by total monthly cost, highest first.
5. For the top cost drivers, propose concrete fixes (lower frame-sampling rate, lower
   detail mode, dedupe near-identical consecutive frames, route to a cheaper specialist
   model for a narrow sub-task, or reduce resolution to what the task actually needs).
   For any call site I flagged as precision-sensitive, do NOT default to suggesting
   downscaling — instead suggest alternatives, and if downscaling is the only lever,
   state the accuracy tradeoff explicitly rather than presenting it as free savings.
6. Total my current estimated monthly cost and the estimated cost after your suggested
   fixes, and show the gap.
7. End with a short note on how confident this estimate is, what it's based on, and
   recommend I validate it against 10-20 real billed API calls before trusting it for
   a budget decision.

Give me the full report in this structure:
- Assumptions used (provider/model, pricing source & date, traffic assumption,
  precision-sensitive sites)
- Call-site cost breakdown table, ranked by monthly cost
- Top cost drivers & mitigations, with estimated % savings and any accuracy tradeoff
- Totals: current estimated $/month vs. after mitigations, and the delta
- Confidence & validation note
```

## What you'll get back
A single structured report with five parts, in this order:
1. **Assumptions used** — the model/provider, where the pricing came from and whether it's confirmed current, your traffic numbers, and which sites you flagged as precision-sensitive.
2. **Call-site cost breakdown** — a table of every vision call site, ranked by estimated monthly cost (highest first), showing resolution/detail mode, frequency pattern, tokens per call, and dollars per session and per month.
3. **Top cost drivers & mitigations** — for each of the biggest spenders, a concrete fix with an estimated savings percentage, and — critically — an explicit accuracy tradeoff warning for anything precision-sensitive rather than a blind "just downscale it."
4. **Totals** — your current estimated monthly spend, the estimated spend after applying the suggested fixes, and the gap between them.
5. **Confidence & validation note** — what the estimate is and isn't trustworthy for, and a reminder to check it against real billed calls before gating a production budget decision on it.

## Guardrails this prompt enforces
- Every dollar figure is labeled an estimate, never presented as the actual bill.
- It will not suggest downscaling or dropping frames on anything you've flagged (or that looks like) a precision task without spelling out exactly what accuracy you'd be trading away.
- It will not silently assume a remembered price is still current — it will ask you to confirm pricing rather than guess.
- It will not invent traffic numbers — if you don't give it session/frequency data, it asks for it instead of making one up.
- It produces a one-time audit report, not a live cost guardrail. If you need something that actually blocks or downscales calls in a running production agent, that's a separate piece of middleware infrastructure, not something a single prompt can do — this report is the pre-launch homework that tells you whether you need to build one.
