# SMS-AI Segment Cost Auditor

A self-contained prompt template. Paste everything below the line into any AI chat tool (ChatGPT, Claude, Gemini, etc.), then provide your message batch as instructed inside it.

## What this does

If you run (or are planning to run) an AI chatbot over SMS — common for reaching users who don't have mobile internet access — your biggest hidden cost isn't the LLM call, it's the SMS gateway bill. SMS is billed in "segments": up to 160 characters (plain text) or 70 characters (if the message has emoji or certain non-Latin scripts) per segment, and a message that's even 1 character over that limit gets billed as 2 segments, not 1.5. An AI model has no idea where that boundary is, so it routinely writes a 161-character answer that costs double what a 159-character answer would, for no gain in content.

This tool audits a batch of AI responses you've already sent (or are about to send) and tells you exactly how many of them crossed a segment boundary they didn't need to, gives you a rewritten version of each one that fits back under the boundary without dropping any factual content, and — if you give it your per-segment rate — estimates what that's costing you per month. It does not run live in production; it's a one-time (or periodic) audit to decide whether building or buying a real-time compression layer is worth the engineering time.

It will NOT touch or rewrite anything involving numbers, dates, dosages, units, or warning language without flagging it separately for your own review — segment savings are never worth silently dropping a safety-relevant detail.

## What you need to provide

**Option A — paste a log (works anywhere, no setup):**
A plain list, one message per line, of the actual text your AI chatbot sent via SMS. A timestamp per line is nice to have but not required. Minimum ~10 messages; realistically paste a day's or week's worth (50-500 messages) so the percentages mean something.

**Option B — if you have API access (Twilio or Africa's Talking):**
Tell the AI chat tool you have Twilio/Africa's Talking API credentials and a date range; if the chat tool you're using can make API calls (e.g. Claude Code with Bash/curl), it can fetch the message log directly instead of you pasting it. Otherwise, paste the export.

**Also tell it, if you know:**
- Whether your messages are mostly English/Latin-script (GSM-7 encoding, 160/153 chars per segment) or contain emoji/non-Latin scripts like Swahili diacritics, Hindi, Amharic, etc. (UCS-2 encoding, 70/67 chars per segment). If you're not sure, say so — it will ask per message.
- Your per-segment billing rate and roughly how many active users/messages per month, if you want a dollar estimate instead of just a segment-count estimate.
- Any categories of content that must never be shortened (e.g. "dosage instructions", "appointment times", "account balances"). If you skip this, it defaults to protecting any number, date, unit, or warning phrase it finds.

## The prompt

```
You are auditing a batch of AI-chatbot responses sent over SMS for billed-segment
waste. SMS is billed in segments: 160 chars/segment for GSM-7 (plain Latin text),
70 chars/segment for UCS-2 (emoji or many non-Latin scripts); once a message needs
more than one segment, the per-segment budget drops to 153 (GSM-7) or 67 (UCS-2)
because of the concatenation header. A message that's 1 character over the
single-segment limit is billed as 2 full segments.

Here is my batch of messages:
[PASTE YOUR LOG HERE — one message per line, or describe your Twilio/Africa's
Talking API access and date range if you want it fetched directly]

Encoding: [GSM-7 / UCS-2 / not sure, check per message]
Per-segment rate (optional): [e.g. $0.012/segment]
Active users or monthly message volume (optional): [number]
Content I must never shorten (optional): [e.g. dosages, dates, account numbers —
otherwise default to protecting any number, date, unit, or warning phrase you find]

For each message:
1. Determine its encoding and compute its actual billed segment count using the
   budgets above.
2. Classify it as Clean (already minimal for its content), Boundary waste (trimming
   <=20 characters or <=15% of its length, whichever is larger, would pull it back
   under the previous segment boundary), or too short to ever cross a boundary.
3. For every "Boundary waste" message: first check it for safety-critical content
   (numbers, dates, units, dosages, warning phrases, or anything I listed above).
   If found, DO NOT rewrite it — mark it "cannot safely compress" and name exactly
   what content blocks the trim. Otherwise, draft a rewrite that cuts filler or
   redundant phrasing to land at or under the previous segment's budget while
   keeping every fact in the original.

Then give me:
- A summary table: total messages audited, average segments per message before vs.
  after, count/percent that were boundary waste, count that were flagged
  "cannot safely compress."
- Each boundary-waste message with its original text, segment count, the rewrite,
  its new segment count, and segments saved.
- Each "cannot safely compress" message with the specific content that blocked it.
- If I gave you a rate and volume: a cost-savings estimate, with the formula and
  every assumption shown explicitly — don't invent a rate if I didn't give you one,
  just report segment counts in that case.
- A one-paragraph recommendation on whether this batch's waste rate (rule of thumb:
  above ~15% of messages) justifies building or adopting real-time segment-
  compression middleware, or whether it's already close to optimal.

Never alter a number, date, unit, dosage, or warning phrase to save a segment —
flag it instead, even if it's the single biggest savings opportunity in the batch.
Never assume the encoding without checking each message. This is a one-time audit
to support a build/buy decision, not a live production tool.
```

## What you'll get back

A structured report: a before/after summary table, a list of flagged messages with concrete rewrites and the segment count each saves, a separate list of messages it refused to touch (with the reason), a cost estimate if you supplied a rate, and a one-paragraph recommendation on whether the waste rate you're seeing is big enough to justify building real segment-compression middleware.

## Limits — read before relying on this

- This is an audit of a batch you already have, not a live filter — it won't stop the next AI response from crossing a boundary. For that you need a real-time middleware layer sitting between your LLM call and your SMS gateway send (a separate, bigger build).
- It will refuse to rewrite anything it flags as safety-critical. That's intentional — review those manually yourself rather than asking it to loosen the rule.
- Segment math assumes standard GSM-7/UCS-2 rules; a few carriers have minor non-standard variations (e.g. different toll-free multipart limits) — treat the segment counts as very close estimates, not a guaranteed match to your exact invoice.
- Without a real per-segment rate, you only get segment counts, not a dollar figure — don't ask it to guess a rate "just to see a number."
