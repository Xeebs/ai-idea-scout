# Voice-Agent Stakes-Gating & Navigability Audit

A self-contained prompt template. Paste the whole thing (including your HTML/screenshots) into any AI chat tool — ChatGPT, Claude, Gemini, Copilot Chat — to get a structured audit back. No prior context about any other project is required.

## What this is for

This is **not** a general "is my website accessible" (WCAG) audit. It answers a narrower, specific question: *if an autonomous voice-browsing agent were driving this page on behalf of a blind or low-vision user, could it reliably tell the difference between a safe, low-stakes action it can take on its own (search, filter, browse) and a high-stakes action (paying, deleting, changing account/security settings) that must stop and ask the user to confirm first?*

Use it when you are building, integrating with, or reviewing a flow meant to be driven by a voice agent on a user's behalf — e.g., before a pilot with blind/low-vision testers, before wiring up a browsing-agent integration, or after an agent misfired on a checkout or account page and you want to know why.

## What you need to provide

**Data source: Manual.** You paste or upload:
1. The raw HTML/DOM source for each page or step in the flow you're auditing (view-source, saved page, or copy of the relevant markup is fine), and/or screenshots of each step if HTML isn't available.
2. A one-line description of the task flow, e.g. "checkout: cart → shipping → payment → confirm" or "account settings: change email → change password → delete account."

If you're using this inside a tool that can browse the web itself, you may instead give it a URL and ask it to fetch the HTML first — but that's an optional shortcut, not a requirement. The core version below works entirely from what you paste.

Minimum input: HTML or a screenshot of at least one page, plus one sentence on what a user is trying to do there.

## The prompt

Copy everything between the lines below, fill in your HTML/screenshots and flow description where indicated, and send it.

---

You are auditing a website flow for **voice-agent stakes-gating and navigability** — not a general WCAG/accessibility compliance audit. The scenario: an autonomous voice-browsing agent is navigating this flow on behalf of a blind or low-vision user, narrating the page conversationally and acting on their behalf for low-stakes actions, but must stop and get explicit confirmation before any high-stakes action.

**Flow being audited**: [describe the task, e.g. "checkout: cart → shipping → payment → confirm"]

**Pages/steps** (HTML and/or screenshots):
[paste HTML per page/step here, or describe/attach screenshots, labeled Page 1, Page 2, etc.]

Follow this procedure exactly:

1. For each page, note the heading hierarchy, landmarks, labeled form fields, ARIA roles/labels, and whether every interactive element has a derivable accessible name. Flag any with no name or a generic one ("click here," "submit," unlabeled icon buttons).
2. Classify every interactive element into one of three buckets:
   - **LOW-STAKES**: read-only/reversible — search, filter, sort, pagination, view details, adding/removing cart items pre-checkout.
   - **HIGH-STAKES**: must require explicit confirmation before an agent acts — payment, placing/cancelling an order, account/security changes (password, email, 2FA, payment method), deleting data, subscribing/cancelling, anything involving money, legal commitment, or irreversibility.
   - **AMBIGUOUS**: the markup/label alone doesn't make the stakes level clear (e.g., a bare "Submit" that could be a search or a purchase). Default to this bucket whenever you're unsure — never downgrade an unclear case to LOW-STAKES.
3. For every HIGH-STAKES or AMBIGUOUS element, check whether its accessible name/label itself signals the stakes level without relying on surrounding visual context (e.g., "Place Order — $84.50" vs. a bare "Submit" styled the same as a search button). Flag any case where a stakes-classifier reading only the label/role/nearby text could plausibly misjudge the stakes level.
4. For every element, flag voice-navigability problems: generic link/button text, missing form labels, icon-only controls with no accessible name, dynamic updates (like a cart total) with no live-region announcement, skipped heading levels, focus traps — specifically noting where each would disorient a spoken, conversational narration of the page (not a verbatim screen-reader read-through).
5. Give each page/step a verdict: **READY**, **NEEDS-FIXES**, or **NOT-READY** for stakes-gating reliability.
6. Produce the report in exactly this structure:
   - **Verdict table**: Page/Step | Verdict | Why (1 line)
   - **Findings table**, ordered most severe first: Severity (Critical/High/Medium/Low) | Page | Element/Location | Issue | Why it matters for a voice agent (not generic accessibility) | Concrete fix (exact markup/attribute change). Critical = a high-stakes action that could be misread as low-stakes.
   - **Stakes-Classification Map**: Page | Element | Current label/markup | Stakes bucket | Disambiguation recommendation
   - **Scope note**: 2-3 sentences stating this audit covers agent stakes-gating and conversational navigability, not WCAG/legal compliance, and recommending a separate WCAG pass (e.g., axe-core) if one hasn't been run.

Rules you must follow:
- Never claim WCAG/ADA/legal compliance. Always include the scope note.
- Never invent markup or behavior not shown in what was provided. If a finding comes only from a screenshot (no DOM), label it "visual-inference, DOM unconfirmed" with lower confidence than DOM-confirmed findings.
- Never classify an unclear action as LOW-STAKES by default — classify AMBIGUOUS and flag it instead. Missing a high-stakes flag is the dangerous failure; over-flagging is merely annoying, and acceptable.
- Never recommend removing or weakening a confirmation step to make the agent seem more autonomous — the goal is to surface missing/ambiguous confirmation signaling, not reduce it.
- Never fabricate traffic, user counts, or usage statistics about the site being audited.

---

## What you get back

A single structured report: a verdict table (one row per page/step), a severity-ordered findings table with concrete fixes, a stakes-classification map listing every high-stakes/ambiguous element and how to disambiguate it, and a short scope note. It is explicitly not a WCAG compliance certificate — pair it with a standard axe-core/manual accessibility audit for that.

## Why this is different from a generic accessibility audit

Standard WCAG/axe-core audits ask "can a human using assistive technology perceive and operate this page." This audit asks a different, narrower question that generic tools don't cover: "can an *autonomous agent* acting on that user's behalf correctly tell which actions it's allowed to take itself and which ones it must stop and ask about." A page can pass a WCAG scan cleanly and still let a voice agent misfire on a payment button because nothing in the markup signals that it's high-stakes versus a routine action nearby.
