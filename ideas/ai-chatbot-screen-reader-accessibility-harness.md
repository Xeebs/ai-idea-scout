# Screen Reader Ready: An Automated Accessibility Test Harness for AI Chatbot/Assistant UIs

- **Status**: EXPLORING
- **Date**: 2026-11-14
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-14-applied-ai-for-underserved-domains.md · P2
- **Maturity verdict**: OPEN — WebSearch found only measurement evidence (a 2026 study where a blind tester passed only 6/30 popular AI tools' basic accessibility checks; a literature review finding critical accessibility issues in >80% of 106 deployed chatbots) and zero fix/certification/audit products or GitHub projects (gh search for "chatbot accessibility screen reader" returned zero results) targeting general-purpose AI tool UI accessibility specifically.
- **Format**: BOTH
- **Data Sources**: CONNECTED — Playwright (browser automation, mature) drives the target chatbot's live web UI directly, paired with Guidepup (an existing open-source library that drives real screen readers — NVDA, VoiceOver, JAWS — and captures their actual spoken/announced output, mature enough to be used in several production a11y test suites today). No manual paste of the UI is required; the harness tests the real running product.

## The Gap
Purpose-built assistive apps (Be My AI, Seeing AI, Envision) are mature and widely adopted for description tasks, but general-purpose AI chatbot interfaces are frequently broken for screen-reader users — a 2026 study found only 6 of 30 popular AI tools passed basic accessibility checks for a blind tester, and a separate literature review found critical accessibility issues in over 80% of 106 deployed chatbots (both cited via WebSearch in the digest). No certification, standard, or audit product exists that specifically targets the AI-chatbot UI pattern (streaming text, dynamic "thinking" states, regenerate/stop controls, multi-turn history) the way WCAG/VPAT conformance reports do for static vendor products — every existing report is written per-vendor and ignores the chatbot-UI pattern as its own test category.

## The Project
A test harness purpose-built for the specific interaction patterns that break in AI chatbot UIs and that generic WCAG scanners don't check well: are new streamed-in assistant messages announced via a live region without spamming every token; does focus return sensibly after "regenerate"/"stop generating"; is the "thinking/typing" indicator exposed to assistive tech; can the input box, send button, and message history all be operated by keyboard alone; are code blocks and markdown tables in responses navigable. The harness runs Playwright against the live product combined with Guidepup driving a real screen reader, producing a pass/fail scorecard per pattern plus the literal captured screen-reader announcement transcript as evidence (not just a pass/fail guess).

## Tangible Impact
**Population**: Blind and low-vision screen-reader users who use AI chatbot tools directly — WebAIM's annual Screen Reader Survey consistently finds tens of thousands of active respondents, and the CDC estimates roughly 7-8 million visually impaired adults in the U.S. alone who are candidates for this population as AI chat tools become a default interface for search, coding, and daily tasks.
**Mechanism**: Vendors and procurement teams (enterprise accessibility offices, government IT buyers subject to Section 508) get a concrete, evidence-backed scorecard instead of a vague "please check accessibility" ask — turning accessibility from an unverifiable claim into a re-runnable, comparable number that can gate a release or a vendor-selection decision, closing specific breakages (silent streaming updates, keyboard traps on regenerate) before they ship.
**Measure**: (1) number of chatbot-UI-specific pattern failures caught on a sample of popular AI tools, benchmarked against the "6/30 passed" baseline; (2) time-to-fix after a vendor is shown a specific failing pattern + transcript vs. a vague bug report; (3) adoption as a CI gate by at least one AI product team building a chat UI.

## Why Now
Guidepup and similar screen-reader-automation tooling matured enough in the last two years to make real (not simulated) screen-reader testing scriptable and CI-friendly; the explosion of AI chatbot products in the last 30 days (per the digest's own scope) means the pattern-specific failure modes (streaming live regions, dynamic "thinking" states) are now common across dozens of products rather than one-off, making a shared harness far more valuable than it would have been a year ago.

## Skill Angle
A companion skill takes a description or short recording of a specific chatbot UI's interaction pattern (e.g. "here's how our streaming response and regenerate button work") and reviews it against the known chatbot-UI accessibility failure modes, drafting the specific ARIA live-region/focus-management fix — a design-review aid usable before a team ever stands up the full automated harness.

## MVP Sketch
Scope: pick 5 chatbot-UI-specific checks (streaming live-region announcement, regenerate focus handling, keyboard-only send, thinking-state exposure, code-block navigability). Build a Playwright + Guidepup script that runs these 5 checks against any URL and outputs a scorecard with captured screen-reader transcripts. Single experiment: run it against the same 30 tools from the cited 2026 study and see whether the pattern-specific scorecard explains *why* each tool passed or failed, where the original study only reported pass/fail.

## Risks & Open Questions
- Screen-reader automation (even via Guidepup) is less mature on macOS/VoiceOver than Windows/NVDA; cross-platform coverage may need to start Windows-only.
- Vendors may treat a public scorecard as reputational risk and push back rather than fix issues, as already happens with WCAG VPATs.
- Overlaps conceptually with P1's scanner-divergence gap-map but targets a structurally different failure class (chatbot-specific dynamic UI patterns, not static WCAG criteria coverage) — worth confirming they stay separate products rather than merging prematurely.
- Risk of chasing a moving target as chat UI patterns (new "thinking" animations, agentic tool-call displays) keep evolving faster than a fixed check list.
