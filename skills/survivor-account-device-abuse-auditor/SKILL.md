---
name: survivor-account-device-abuse-auditor
description: Reviews screenshots of account-security and device-sharing settings pages (Google, Apple, smart-home apps, location-sharing apps) to flag leftover ex-partner access points, in priority order, for a domestic violence survivor or the advocate helping them. Use when someone hands over settings screenshots and asks "what here can my ex still see/control" rather than asking for general digital-safety advice.
---

# Survivor Account & Device Abuse Auditor

## When to use this
Use this when a user (a DV survivor, or an advocate working alongside one) pastes or uploads one or more screenshots of account-security or device-sharing settings pages and asks something like "what can my ex still access," "is anyone else linked to this account," or "what should I turn off first." Do not use this for general "how do I stay safe online" questions with no screenshots — that's a different, broader conversation. Do not use this if the user asks you to log into an account, enter credentials, or connect to an API on their behalf — this skill never does that.

## Inputs
**Data source**: Manual — the user pastes or uploads screenshots (or types out what a settings page says) from account security-checkup pages they are already logged into on their own: Google Security Checkup / "Your devices," Apple ID device list, Find My device-sharing, Life360 or similar location-sharing app member lists, smart-home app (Nest, Ring, SmartThings, etc.) shared-access/co-owner lists, and shared calendar or shared photo-album permission lists. There is no live-login or OAuth-connected version of this skill — the user never hands over a password, and this skill never asks for one.

Also ask the user (if not already stated):
1. Which platforms the screenshots are from (so the right tactics checklist is applied).
2. Whether they are currently on a device/account they believe is NOT visible to the former partner, or whether they're unsure. This answer gates the safety banner below.

## Procedure
1. **Safety banner first, always, before analyzing anything.** Output the safety banner (see Output format) before any screenshot analysis, every single time, even on a repeat request in the same conversation. Never skip it to save space.
2. **Do not ask for or accept credentials.** If the user offers a password, login link, or asks you to "just log in and check," refuse, restate that this is screenshot-only, and ask for a screenshot/description instead.
3. **Classify each screenshot** by platform and setting type (device list, shared household/family group, location-sharing member list, calendar/photo permission list, smart-home co-owner list, active-sessions list).
4. **Pattern-match against the known tactics checklist** for that platform/setting type:
   - Legacy "family" or shared Apple ID / Google account still active post-separation
   - A device in the list the user doesn't recognize, or recognizes as the ex-partner's
   - A wearable (smartwatch, fitness tracker) still cloud-linked even if the physical device was returned/destroyed
   - A location-sharing app member who is the ex-partner, or an account alias of theirs
   - Smart-home co-owner/guest access (locks, cameras, thermostats) not removed post-separation
   - Shared calendar or shared photo album still granting view/edit access
   - An active login session from an unrecognized device or IP-adjacent location, especially a session with no recent explicit sign-in by the user
5. **For every flagged item**, assess and record: what it is, why it's risky, how confident the pattern-match is given what's visible in the screenshot (screenshots are often partial — say so when they are), and a **detectability rating**: will removing/revoking this be silent, or will the other party likely notice (e.g., a shared photo album losing a member is usually silent; losing smart-lock access is often immediately obvious).
6. **Order the flagged list**: highest-risk-and-silent-to-revoke first, then highest-risk-but-detectable items — and for every detectable item, attach an explicit note to plan the timing/safety context before acting, don't just revoke it immediately.
7. **Never declare a clean bill of health.** If nothing is flagged, say so but explicitly hedge: screenshots are a partial, point-in-time view and pattern-matching against a known-tactics list cannot catch a tactic not yet in that list.
8. **Close every report** with the resource line and the evidence-preservation note (see Output format) — never omit these even if the user doesn't ask for them.

## Output format
A single Markdown report, in this order, every time:

1. **Safety banner** (fixed text, see below) — always first.
2. **What was reviewed** — one line per screenshot: platform, setting type, and a note if the image was partial/hard to read.
3. **Flagged access points**, as a numbered list ordered per step 6, each item formatted:
   - **Item**: what was found
   - **Why it's risky**: one line
   - **Confidence**: High / Medium / Low, with the reason (e.g., "Low — device name was partially cropped in the screenshot")
   - **Revoking this is**: Likely silent / Likely detectable
   - **Suggested action**: what to do, and if detectable, a note to plan timing/safety first rather than act immediately
4. **Nothing else flagged in this batch** — only if applicable, with the hedge from step 7.
5. **Evidence note**: before revoking or deleting anything flagged, screenshot/export the current state first — it may be useful as evidence, and removing access can't be easily undone to re-check later.
6. **Resources**: National DV Hotline (US) 1-800-799-7233 or text START to 88788; suggest involving a DV advocate for anything marked "likely detectable" before acting alone.

Fixed safety banner text (step 1, always verbatim at the top):
> **Before you read this**: if you think your device or accounts might be monitored, review this on a device/account the other person has never had access to, and consider clearing your browser history or using a private/incognito window afterward. Making changes to a flagged item can alert the other person that you found it — some items below are marked "likely detectable" for that reason. This review is based only on what's visible in the screenshots you shared; it cannot catch everything, and it is not a substitute for a safety plan from a DV advocate.

## Guardrails
- Never accept, request, or process actual account credentials, login sessions, or API/OAuth access — this skill is screenshot/description-only, by design, forever. If asked to go further, say no and explain why (a live-login tool becomes a new attack surface, and the consent flow itself can be visible to someone with device access).
- Never output the safety banner as optional, abbreviated, or only-on-first-use — repeat it in full every time this skill runs, because a new session with no memory of a prior warning is exactly the failure mode the NYU 2026 chatbot-safety study found in GPT-4o and Claude: models skipping the warning that changes can alert an abuser.
- Never tell the user to revoke a "likely detectable" item immediately without the timing/safety-planning caveat.
- Never say "nothing was found, you're clear" — always hedge that a screenshot review is partial and point-in-time.
- Never suggest contacting law enforcement, filing a report, or taking any legal action on the user's behalf — that decision belongs to the user and their advocate, not this skill.
- Never fabricate platform-specific settings-page details you weren't shown; if a screenshot is unreadable or ambiguous, say so and ask for a clearer one rather than guessing.
- Never skip the resources/evidence-preservation closing section, even for a short or single-screenshot request.
