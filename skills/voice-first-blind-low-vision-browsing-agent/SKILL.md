---
name: voice-first-blind-low-vision-browsing-agent
description: Audits a website's pages/flows for whether an autonomous voice-browsing agent acting on behalf of a blind or low-vision user could safely navigate them and correctly distinguish low-stakes actions (browse, search, filter) from high-stakes ones (payment, account changes, deletions) that must require explicit confirmation. Use when a site owner, developer, or accessibility reviewer asks "could a voice agent safely drive this page" or "would a voice agent know this button needs confirmation" — not a general WCAG compliance audit.
---

# Voice-Agent Stakes-Gating & Navigability Audit

## When to use this
A site owner, developer, QA engineer, or accessibility consultant is preparing (or evaluating) a flow that a voice-first browsing agent would drive on behalf of a blind or low-vision user — e.g., before integrating with an agent like a CoBrowse-style assistant, before a pilot with blind/low-vision testers, or when reviewing why an agent misfired on a checkout/account page. The trigger is specifically a question about agent-mediated navigation and confirmation safety, not a general "is my site accessible" request (route those to a standard WCAG/axe-core audit instead — this skill explicitly does not replace one).

## Inputs
**Data source**: Manual — the user pastes the raw HTML/DOM source (view-source or saved page source) for each page or step in the flow, and/or uploads screenshots of each step, plus a one-line description of the task flow being audited (e.g., "checkout: cart → shipping → payment → confirm"). If run inside a tool with its own browsing/fetch capability (e.g., Claude Code's WebFetch), the agent may optionally fetch a given URL's HTML directly as a convenience — but this is not a required or assumed connector, and the portable (non-Claude-Code) version of this skill always works from pasted/uploaded input alone. (Note: the source idea file for this skill did not carry an explicit Data Sources classification — this is the synthesizer's own best-justified read, flagged here per `.claude/rules/idea-format.md`.)

Minimum viable input: the HTML or a screenshot for at least one page, and a one-sentence statement of what the user is trying to accomplish on that page.

## Procedure
1. **Intake**: Collect HTML/DOM and/or screenshots for each page/step in the stated flow, plus the task description. If only a live URL is given and fetch capability exists, retrieve the HTML; otherwise ask the user to paste it rather than guessing at markup.
2. **Structural pass** (per page): Identify heading hierarchy, landmarks, labeled form fields, ARIA roles/labels, and whether every interactive element (button, link, custom control) has a derivable accessible name. Note elements with no accessible name or a generic one ("click here", "submit", icon-only with no `aria-label`).
3. **Stakes classification** (per interactive element): Sort every element into one of three buckets:
   - **LOW-STAKES** — read-only or reversible navigation: search, filter, sort, pagination, "view details," adding/removing items from a cart (pre-checkout).
   - **HIGH-STAKES** — must be gated behind explicit confirmation before any agent acts: payment submission, placing/cancelling an order, account/security changes (password, email, 2FA, payment method), deleting data, subscribing/cancelling, anything involving money, legal commitment, or irreversibility.
   - **AMBIGUOUS** — the markup/label alone doesn't make the stakes level unambiguous (e.g., a bare "Submit" button that could be a search or a purchase). Default here whenever uncertain — never downgrade an ambiguous element to LOW-STAKES.
4. **Disambiguation check** (HIGH-STAKES and AMBIGUOUS elements only): For each, check whether its accessible name/label itself signals its stakes level to something that can't see surrounding visual context (e.g., "Place Order — $84.50" vs. a bare "Submit" both styled identically). Flag any case where a stakes-classifier reading only the accessible name/role/nearby text could plausibly misjudge the stakes level.
5. **Voice-navigability pass** (all elements): Flag generic link/button text, missing form labels, icon-only controls without `aria-label`, dynamic content changes with no `aria-live` region (e.g., cart total updating silently), skipped heading levels, and focus traps — specifically noting where each would disorient a *conversational narration* of the page (not verbatim screen-reader output) rather than just a generic screen-reader pass.
6. **Verdict**: For each page/flow, assign READY / NEEDS-FIXES / NOT-READY for stakes-gating reliability — i.e., could a stakes-classifier gate this page's high-stakes actions correctly as currently built.
7. **Write the report** in the exact format below. Never silently skip a page that was provided.

## Output format
A single markdown report with four sections, in this order:

1. **Verdict table** — one row per page/step: `Page/Step | Verdict (READY/NEEDS-FIXES/NOT-READY) | Why (1 line)`.
2. **Findings table** — one row per issue: `Severity (Critical/High/Medium/Low) | Page | Element/Location | Issue | Why it matters for a voice agent (not generic a11y) | Concrete fix (exact markup/attribute change)`. Critical = a high-stakes action that could be misclassified as low-stakes; order the table by severity, most critical first.
3. **Stakes-Classification Map** — one row per HIGH-STAKES or AMBIGUOUS element found: `Page | Element | Current label/markup | Stakes bucket | Disambiguation recommendation`.
4. **Scope note** (2-3 sentences, fixed) — states this audit evaluates agent-mediated stakes-gating and conversational navigability, not WCAG/legal compliance, and recommends a separate axe-core/manual WCAG pass if one hasn't been run.

## Guardrails
- Never claim WCAG, ADA, or legal accessibility compliance — this audit's scope is strictly voice-agent stakes-gating and navigability; always include the scope note.
- Never invent markup, elements, or page behavior that wasn't in the provided HTML/screenshots. Findings based only on a screenshot (no DOM) must be marked "visual-inference, DOM unconfirmed" and given lower confidence than DOM-confirmed findings.
- Never classify an action LOW-STAKES by default or assumption — when stakes are unclear from the markup/label alone, classify AMBIGUOUS and flag it. A missed high-stakes flag (false negative) is the dangerous failure mode this skill exists to prevent; a false positive (over-flagging) is merely annoying.
- Never recommend removing or weakening a confirmation step to make the agent feel more autonomous or frictionless — the purpose is to surface where confirmation signaling is missing or ambiguous, not to minimize it.
- Never fabricate traffic, user, or usage statistics about the audited site; this is a structural audit of the specific pages/flow supplied, nothing more.
