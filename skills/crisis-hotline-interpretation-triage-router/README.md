# Crisis Hotline MT Triage Audit

A paste-in prompt template for auditing whether machine translation (MT) is safe to deploy — unsupervised or with human-interpreter escalation — on a crisis or volunteer hotline, for one specific language pair. Use this with any AI chat tool (ChatGPT, Claude, Gemini, etc.) by pasting the whole template below, filling in your data, and sending it.

This is a **one-time or periodic pre-deployment audit** of a sample batch, not a live call-routing system. It does not process real-time calls — it evaluates a batch of examples you provide and gives you a report and an operating rule.

## When to use this

You run a crisis-response hotline, volunteer interpreter network, humanitarian NGO, or disaster-response service, and you're deciding whether MT can handle a specific language pair unsupervised, or how to split traffic between MT and scarce human interpreters. You have, or can collect, a batch of real or representative MT outputs for that pair and want a structured, evidence-based go/no-go answer and a concrete escalation rule — before committing interpreter time or risking a silently wrong translation reaching someone in crisis.

## What you need before you start

1. **Language pair** — e.g., "Haitian Creole → English" or "Dari → English."
2. **Crisis domain** — pick one: medical/health triage, logistics/shelter/evacuation, missing-persons/family reunification, emotional support/mental health, or general information. The domain changes how severely each failure gets scored.
3. **A sample batch of at least 20-30 message pairs.** For each message, you need:
   - The original source-language message (or a close gloss if you can't paste native script)
   - The MT output as actually produced
   - Ideally one of: a back-translation of the MT output back into the source language, a bilingual reviewer's one-line accuracy note, or a known ground-truth urgency label (e.g., "this is a life-threatening emergency" vs. "routine request")
4. **Optional**: which MT system/model produced the output (Google Translate API, NLLB, a commercial vendor, a local LLM, etc.) — this helps contextualize likely failure modes but isn't required.

If you have fewer than 20 pairs, say so up front — the audit will still run but the verdict will be marked low-confidence. If you only have MT outputs with no source text or accuracy signal at all, collect at least a few back-translations or a bilingual reviewer's notes first — accuracy can't be assessed from output alone.

## The prompt to paste

```
You are auditing whether machine translation is reliable enough to deploy
on a crisis/volunteer hotline for one specific language pair, before any
live traffic goes through it. Treat false negatives (missing a real
emergency) as far more costly than false positives (an unnecessary human
review) throughout.

LANGUAGE PAIR: <source language> -> <target language>
DOMAIN: <medical/health | logistics/shelter/evacuation | missing-persons |
emotional support/mental health | general information>
MT SYSTEM (if known): <name, or "unspecified">

SAMPLE MESSAGES (source | MT output | back-translation or reviewer note,
one per line or block):
<paste your batch here - minimum 20-30 pairs>

Do the following:

1. For each message, check it against this failure taxonomy and flag any
   that match:
   - Script degradation: garbled characters, incomplete target-script
     rendering, mixed scripts, repetition/truncation, or output not
     actually in the stated target language.
   - Urgency distortion: the MT output's perceived urgency differs from
     the source - hedging added or removed, dropped time-critical words
     ("immediately," a deadline), an emergency reframed as routine or
     vice versa.
   - Meaning drop / content error: negation flips, numeric or quantity
     errors (dosage, headcounts, addresses), dropped named entities
     (locations, medications, names), or a swapped subject/object that
     reverses who needs help.
   - Confidence calibration gap: if a confidence score was supplied,
     note whether low-confidence outputs correlate with the failures
     above; if none was supplied, say so as a visibility gap.

2. Assign each flagged message a risk level - HIGH, MEDIUM, or LOW -
   weighted by domain: in medical/health and emotional-support domains,
   any urgency distortion or meaning drop is at least MEDIUM, and
   anything that could delay or misdirect emergency response is HIGH.
   In logistics/shelter, numeric/address errors are at least MEDIUM;
   wording ambiguity alone is LOW. In general information, most issues
   are LOW unless meaning is inverted.

3. Aggregate: what percentage of the batch is HIGH/MEDIUM/LOW, what are
   the 1-3 most common failure types for this specific pair, and do
   failures cluster around a particular message type?

4. Recommend a specific, operable escalation rule (not "use judgment") -
   e.g., "escalate all medical-domain messages, plus anything matching
   [these cues], to a human interpreter."

5. Give a go/no-go verdict for letting MT run unsupervised, with an
   explicit confidence level (HIGH/MEDIUM/LOW) tied to sample size and
   whether accuracy signals (back-translation/reviewer notes) were
   actually provided. Never call it HIGH confidence on fewer than 20
   validated pairs. Never recommend a full "go" with no escalation path
   for the medical/health or emotional-support domains, regardless of
   how clean the sample looks.

Output format:

# MT Reliability Audit - <language pair> / <domain>
Sample size: <n> | MT system: <name or "unspecified">
Confidence in this verdict: <HIGH/MEDIUM/LOW>

## Flagged Messages
A table: # | Source (excerpt) | MT Output (excerpt) | Failure Type(s) | Risk
(list only flagged messages, not the whole batch)

## Summary
- Risk distribution (% HIGH/MEDIUM/LOW)
- Most common failure type(s) for this pair
- Any pattern noticed

## Recommendation
- Go/No-Go for unsupervised MT
- Specific escalation rule
- What would raise confidence in this verdict (bigger sample, bilingual
  review, a field pilot, etc.)

Do not invent failure examples, percentages, or linguistic claims not
grounded in the messages actually pasted above. If no source text or
accuracy signal was provided for a message, say you cannot assess it
rather than guessing.
```

## What you get back

A structured audit report (format above): a table of specifically flagged messages tied to the actual batch you pasted, an aggregate risk breakdown, the most common failure pattern for your language pair, a concrete escalation rule you could hand to hotline staff today, and a go/no-go verdict with an honest confidence qualifier.

## Guardrails (built into the prompt, worth knowing)

- It will never tell you MT is safe to run fully unsupervised in medical or emotional-support/mental-health domains, no matter how clean your sample looks — it will always recommend an escalation path for the highest-risk message types there.
- It will not assess accuracy from MT output alone — if you paste outputs with no source text or validation signal, it will ask for one instead of guessing.
- It will not give you a high-confidence verdict from a small sample (under 20 pairs) — it caps confidence and tells you why.
- It will not accept automatic metrics (BLEU, etc.) alone as proof of safety — it flags the absence of human/bilingual validation as a limitation.
- This is not a live routing system. If you need real-time call/message routing with this logic running continuously, that's a larger engineering build (middleware wired to your MT pipeline and an actual interpreter on-call queue) — this skill is the audit you run before building or trusting that.
