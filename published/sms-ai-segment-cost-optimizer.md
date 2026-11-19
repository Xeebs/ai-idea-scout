# SegmentWise: A Per-Message-Cost-Aware Response Compressor for SMS-Based AI Access

Three startups have shipped AI chatbot access over SMS to feature phones in the last year, each one proudly solving the "3.45 billion people without mobile internet" problem. None of them noticed they were still charging those same people by the segment for every word the model wastes.

## The Gap

teks, ChatMtaani, and textgpt have all built AI-over-SMS products aimed squarely at the population without mobile internet — tech.eu puts the global number at "3.45B people lacking mobile internet access"; Citizen Digital covers ChatMtaani bringing AI to "kabambe" feature phones in Kenya. The channel problem is solved: these tools genuinely get an LLM's output onto a feature phone with nothing more than SMS. But the Center for Global Development and NextBillion both independently zero in on a different, unsolved blocker — "high markups on text messages" that, in their framing, "will prevent the world's poorest from making use of the technology" even once the channel exists.

Look at what these three tools actually do with a model's response, and the gap becomes obvious: they're thin wrappers that pass the LLM's full, unoptimized output straight to the SMS gateway. None of them treats the number of billed SMS segments a response consumes as a design constraint. A search turned up exactly one implementation of the core mechanic anywhere — SMS Works' "AI SMS Message Optimiser," which demonstrably shrinks an outbound message from 162 characters and 2 billed credits down to 142 characters and 1 credit. But it's a generic SMS-marketing feature sold by one UK vendor, built for marketing blasts, not for an AI chatbot's response protocol, and not aimed anywhere near the ultra-low-income population CGD and NextBillion are describing. No second implementation, and nothing framing this as a first-class constraint for underserved-population AI access, turned up in any channel.

## The Project

SegmentWise is middleware, not another chatbot — it sits between an existing SMS-AI deployment's LLM call and its SMS gateway send (Africa's Talking, Twilio: both already the mature transport layer in the teks and ChatMtaani deployments cited above), and does one job: rewrite the model's answer to cost as few billed SMS segments as possible without losing what a low-literacy, low-bandwidth user actually needs from it.

The key move is that this isn't generic shortening. SMS billing runs on hard segment boundaries — 160 characters per segment for GSM-7 encoding, far fewer for Unicode scripts — so the content that matters most to cut isn't the longest sentence, it's whatever handful of characters pushes a response one segment past where it needed to stop. Trimming two characters that keep a reply inside a single billed segment is worth more than trimming twenty that don't cross any boundary at all. SegmentWise does segment-boundary-aware rewriting: encoding-aware math to find exactly where the next boundary falls, then a rewrite pass — rule-based trimming first, a constrained cheap-LLM call where that's not enough — that holds the line on factual content while closing the gap to the boundary. None of it requires touching the underlying chatbot's own logic.

## Tangible Impact

**Population**: The ~3.45 billion people globally lacking mobile internet access who are the explicit target market of teks, ChatMtaani, and textgpt's SMS-AI products (tech.eu, 2025).
**Mechanism**: Every SMS segment a user is billed for either comes directly out of their own airtime budget or constrains how often a cash-strapped aid or health program can afford to message them in the first place. A chatbot reply that silently spans two or three segments instead of one is a tax on exactly the population these tools exist to serve. Compressing at the segment boundary — not just trimming characters in general — turns a 2-3-segment interaction into a 1-segment one wherever the content allows it.
**Measure**: Average billed segments per AI response, before and after (the target is pulling the majority of responses that cross 1→2 segments back under the boundary); total monthly SMS cost per active user in a pilot deployment; comprehension and satisfaction ratings on compressed versus uncompressed responses, to confirm the savings aren't coming at the cost of clarity.

## Try It

A companion skill, `skills/sms-ai-segment-cost-optimizer/`, is a decision aid, not the middleware itself. Per its `SKILL.md`: it "audits a batch of already-sent AI-chatbot SMS responses and reports what fraction crossed a billed segment boundary unnecessarily (161 chars costing 2 segments instead of 1), with concrete before/after rewrites that preserve safety-critical content, plus a cost-savings estimate." Use it before committing engineering time to actually build or buy the compression middleware — hand it a pasted log of real sent messages and get back a number, not a guess, on how much is being wasted.

To use it: paste `skills/sms-ai-segment-cost-optimizer/README.md` into any AI chat tool and follow the prompt, or drop the `sms-ai-segment-cost-optimizer` folder into `~/.claude/skills/` if you're working in Claude Code.

## Worth Knowing Before You Build

This might already be solved and simply undocumented — teks, ChatMtaani, or textgpt's internal stack could already do some of this quietly, and a direct outreach to any of them costs little compared to building from scratch. Aggressive compression carries a real safety risk: a health chatbot trimming a dosage caveat to save one segment is a different kind of failure than a slightly longer bill, so any real implementation needs a content-criticality flag that overrides compression rather than treats every character as fair game. The encoding math also cuts against the populations this is meant to help — languages that force UCS-2 encoding get segments a fraction the size of GSM-7's 160 characters, so the harder-to-reach the language, the harder this problem gets. And carrier markup structures vary enough by country that the savings here could be substantial in one market and marginal in the next.

---

Surfaced from `research/2026-11-18-applied-ai-for-underserved-domains.md`, pattern `P3`.
