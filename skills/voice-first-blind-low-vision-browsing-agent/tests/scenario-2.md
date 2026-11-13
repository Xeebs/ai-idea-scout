# Scenario 2 — SaaS account settings page (screenshot only, no HTML)

## Input

**Flow being audited**: account settings: update profile → change email → remove a team member → delete account

**Page 1 — screenshot description** (no HTML/DOM available, only a screenshot was captured by the user):
A settings page with a left sidebar of nav links: "Profile," "Team," "Billing," "Danger Zone." The main panel under "Profile" shows a form with "Display Name" and "Bio" text fields and a "Save Changes" button (standard blue, same visual style as every other button on the page). Under the "Team" tab, there's a table of team members, each row with a small trash-can icon on the right with no visible text label. At the bottom of the "Danger Zone" tab, there's a single link, styled identically to the sidebar nav links (plain blue text, no button styling, no icon, no warning color), reading just "Delete Account."

## Pass criteria

The output must:
1. Mark all screenshot-derived findings as "visual-inference, DOM unconfirmed" per the skill's confidence-labeling rule, since no HTML was provided for this scenario.
2. Flag the "Delete Account" link in the Stakes-Classification Map as HIGH-STAKES, and flag it as a Critical/High severity finding specifically because it is styled identically to ordinary low-stakes navigation links (plain blue text, no visual or semantic distinction, no confirmation step mentioned) — this is the single most important catch in this scenario, directly mirroring the CHI '26 study's "worried about hallucinations and payment/irreversible-action handoff" concern cited in the parent idea.
3. Flag the team-member removal trash-can icon as both a voice-navigability issue (icon-only, no accessible name mentioned) and a stakes-classification concern (removing a team member is at minimum AMBIGUOUS, arguably HIGH-STAKES — it should not be silently bucketed LOW-STAKES).
4. Classify "Save Changes" on the Profile tab as LOW-STAKES-leaning but still flag it in the findings if it's visually identical to higher-stakes buttons elsewhere (consistency risk) without over-flagging it as Critical.
5. Produce the verdict table with the "Danger Zone"/delete-account step marked NOT-READY.
6. Include the scope note disclaiming WCAG/legal compliance certification.

## Fail conditions

- Treating the "Delete Account" link as LOW-STAKES or not flagging it at all.
- Presenting screenshot-derived findings with the same confidence as DOM-confirmed findings (no "visual-inference, DOM unconfirmed" labeling).
- Refusing to produce output because no HTML was provided — the skill must work from screenshots per its stated inputs, just with a lower-confidence label on those findings, not a hard requirement for DOM.
