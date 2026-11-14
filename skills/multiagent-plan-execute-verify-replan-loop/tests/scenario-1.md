# Scenario 1: Competitive analysis run with a real gap and an unsupported claim

## Setup

A team ran a 3-worker multi-agent pipeline to answer a market-research query and wants an independent audit before sending the result to their VP.

**Original query:**
> "Compare our top 3 US-based competitors (Northwind Analytics, Fenwick Data Co., and Arborlane) on pricing, product breadth, and recent funding. Flag anything that changed in the last 12 months."

**Planner's task breakdown:**
> Task 1 (Worker A): Research product breadth for Northwind, Fenwick, Arborlane.
> Task 2 (Worker B): Research recent funding events (last 12 months) for all three.
> Task 3 (Worker C): Summarize overall competitive positioning.

(Note: no task was ever assigned to research pricing — this is a planning gap baked into the setup.)

**Worker A raw output:**
> "Northwind Analytics offers a 3-tier SaaS platform (Starter/Pro/Enterprise) with strong analytics and weaker integrations. Fenwick Data Co. has a narrower single-tier offering focused on compliance reporting. Arborlane has the broadest suite, spanning analytics, compliance, and workflow automation, per their public product page (arborlane.com/products, accessed this week)."

**Worker B raw output:**
> "Arborlane raised a $40M Series C in March of this year, led by Kestrel Ventures (TechCrunch, March 14). Fenwick Data Co. has had no public funding events in the last 12 months. No information found on Northwind Analytics funding."

**Worker C raw output:**
> "Overall, Arborlane looks like the strongest competitor given its broad product suite and recent well-funded growth. Northwind and Fenwick are more niche players. This is a complete and well-supported picture of the competitive landscape."

(Note: Worker C's closing sentence is the orchestrator-style self-assessment the auditor must ignore — it's an in-pipeline self-claim, not evidence.)

## Expected output characteristics (pass/fail checklist)

- [ ] Decomposes the query into at least these distinct sub-questions: pricing comparison, product breadth comparison, funding events (last 12 months) for all three, "anything changed in last 12 months" (broader than just funding).
- [ ] Planning Coverage section flags that **no task was ever assigned to research pricing** — a PLANNING GAP, correctly distinguished from an execution gap.
- [ ] Sub-Question Audit marks **pricing comparison as MISSING** (no worker output anywhere addresses pricing for any of the three companies).
- [ ] Marks **product breadth as ANSWERED** (Worker A covers all three, with a cited source for Arborlane).
- [ ] Marks **funding events as PARTIAL or flags a gap**: Northwind's funding status is explicitly "no information found" — the audit should surface this as an unresolved sub-item, not silently treat Worker B's output as fully answering the funding sub-question for all three companies.
- [ ] Does **not** treat Worker C's "this is a complete and well-supported picture" as evidence toward the verdict — the audit must ignore or explicitly flag this as the kind of unverified self-assessment it's designed to override.
- [ ] Final verdict is **REPLAN**, not PASS, with a bounded list that names at minimum: (1) research pricing for all three companies, (2) resolve Northwind's funding status.
- [ ] Does not say "redo everything" or produce a vague re-run instruction.

## Fail conditions

- Marking this PASS.
- Treating Worker C's summary as sufficient evidence of completeness.
- Omitting the pricing gap entirely.
- Fabricating a pricing figure not present in any worker output.
