---
name: multimodal-vision-token-budget-guardrail
description: Audits a multimodal agent's image/video-frame-sending code (or a described pattern) and produces a per-call-site, per-session, and per-month vision-token cost estimate, ranked by spend, with concrete downscale/routing fixes for the biggest drivers. Use before shipping or scaling a vision-enabled agent — especially one streaming continuous video or screen-share frames — not for a single-image chatbot that already fits comfortably in a known budget.
---

# Vision-Token Cost Auditor

## When to use this
A developer or team is about to ship, or is already scaling, a multimodal agent that sends images, video frames, or screen-share frames to a vision-capable model (OpenAI, Anthropic, or Gemini), and wants to know the real token/dollar cost *before* the bill arrives — not a generic "how do vision tokens work" question, and not a request to actually enforce a budget live in production (that's a separate runtime guardrail, out of scope for this one-shot audit). The clearest trigger phrases: "what will this cost us at scale," "why is our vision agent so expensive," "review this before we ship it," or "we're about to add continuous frame capture, what's the exposure."

## Inputs
**Data source**: Connected — when run inside Claude Code (or another tool with filesystem access), point this skill at the repository path containing the agent's vision-calling code; it reads the relevant files directly via Read/Grep rather than asking you to re-paste code that's already sitting in your repo. The provider SDKs it's inspecting (OpenAI, Anthropic, Gemini vision endpoints) are mature and already in use by any team this targets — there is no new connector to build. The portable, non-filesystem version (README) falls back to Manual: paste the actual code snippet(s) or a precise description of the pattern.

Either way, three things must come from you regardless of mode (no connector holds business/traffic assumptions):
1. **Call-site data** — Connected: a repo path to scan. Manual: the pasted code that constructs and sends the image/frame payload (provider SDK call, resolution/dimensions, detail/fidelity parameter, model name).
2. **Traffic assumptions** — sessions or requests per day/month, and frames-per-session for any continuous/streaming call site (e.g., "500 sessions/day, 1 frame every 2 seconds, avg 6-minute session").
3. **Precision-sensitivity flags** — which call sites, if any, are doing a precision task (OCR, UI element detection, fine-grained visual diagnosis) where downscaling would risk correctness, versus which are tolerant of resolution loss.
4. **Current provider pricing** — if this skill cannot verify today's per-token/per-tile rate for the exact model in use (training data goes stale, rates change), it must ask you to paste the current rate from the provider's pricing page rather than silently reusing a remembered number.

## Procedure
1. **Locate every vision call site.** Connected mode: grep/search the given path for calls into vision-capable endpoints (e.g., `images`, `image_url`, `media`, base64 image payload construction, frame-capture loops) across the provider SDKs in use. Manual mode: parse the pasted snippet(s). For each site, extract: provider/model, resolution or dimensions, detail/fidelity mode (e.g., OpenAI `low`/`high`/`auto`, or equivalent), and whether it fires once per upload or repeatedly in a loop (continuous video/screen-share).
2. **Confirm current pricing.** State the provider's documented tokenization rule being used for the estimate (e.g., OpenAI's tile-based formula, or Anthropic/Gemini's resolution-based formula) and its source. If unconfirmed or possibly stale, say so explicitly and ask the user to confirm/paste the current rate before producing dollar figures — token-count estimates can still be given, dollar figures cannot be trusted until pricing is confirmed.
3. **Estimate per-call token cost** for each call site using the confirmed formula and the extracted resolution/detail mode. Always state this as an estimate with an explicit uncertainty note (tokenization/tiling rules are provider-specific and can shift without notice).
4. **Scale to per-session and per-month** using the user-supplied traffic assumptions (frequency × sessions). For continuous/streaming call sites, this is frames-per-session × frames, not a single-call estimate — this is where unbounded cost usually hides.
5. **Rank call sites by total monthly cost contribution**, highest first.
6. **For each of the top cost drivers**, propose concrete mitigations matched to the call site's characteristics and its precision-sensitivity flag:
   - Continuous/streaming site, not precision-flagged → reduce frame-sampling rate, drop to a lower detail mode, or dedupe near-identical consecutive frames.
   - Continuous/streaming site, precision-flagged → do not default to downscaling; instead suggest routing to a cheaper specialist model for the narrow sub-task, or sampling at full fidelity only on detected state changes.
   - One-off upload site → usually lower-priority unless resolution is far higher than the task needs (e.g., a 4K image for OCR that only needs ~1500px on the long edge).
   For every mitigation, state the estimated percentage cost reduction and, if the site is precision-flagged, the explicit accuracy tradeoff being traded away.
7. **Total the current estimated monthly cost** and the **estimated cost after applying the suggested mitigations**, and state the gap between them.
8. **Recommend a validation step**: comparing the estimate against ~10-20 real billed API calls of varying sizes/detail modes before trusting this estimate to drive a budget decision — this audit is a pre-launch/pre-scale estimate, not a substitute for checking an actual bill.

## Output format
A single markdown report, in this order:
1. **Assumptions used** — table: `Provider/Model | Pricing source & confirmed-as-of date | Traffic assumption | Precision-sensitive sites flagged by user`.
2. **Call-site cost breakdown** — table, ranked by monthly cost descending: `Call site (file/location or snippet #) | Resolution/detail mode | Frequency pattern | Est. tokens/call | Est. $/session | Est. $/month | % of total`.
3. **Top cost drivers & mitigations** — one entry per top driver: the finding, the suggested fix, estimated % savings, and (if precision-flagged) the explicit tradeoff.
4. **Totals** — current estimated $/month, estimated $/month after mitigations, and the delta.
5. **Confidence & validation note** (fixed, always included) — states the tokenization formula's source, that provider pricing/tokenization can change without notice, and recommends validating against real billed calls before gating production traffic on this estimate.

## Guardrails
- Never present a dollar figure as the actual billed cost — always an estimate with a stated uncertainty basis and formula source.
- Never recommend downscaling, lowering detail mode, or dropping frames on a call site the user flagged as precision-sensitive without explicitly stating the accuracy tradeoff; when precision-sensitivity wasn't stated for a site that looks precision-shaped (OCR, UI/element detection, fine visual diagnosis), ask rather than assuming it's safe to downscale.
- Never fabricate or silently reuse a remembered provider price/tokenization rule without flagging that it may be stale — ask the user to confirm current pricing rather than guessing.
- Never invent traffic volume, frame rate, or session counts the user didn't supply — if traffic assumptions are missing, ask for them rather than estimating a monthly figure from a guess.
- This is a one-shot pre-launch/pre-scale audit, not a live runtime guardrail — never imply it enforces or blocks anything in production; recommend a persistent middleware wrapper (a separate, infrastructure-shaped build) for that.
