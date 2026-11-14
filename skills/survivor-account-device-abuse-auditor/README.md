# Survivor Account & Device Abuse Auditor

A prompt template for reviewing screenshots of account-security and device-sharing settings pages to flag leftover access a former partner may still have — for a domestic violence survivor, or an advocate helping them, to use as a self-service first pass before a fuller safety-planning conversation.

## When to use this

Use this when you have screenshots (or can describe what a settings page shows) from account security pages you are already logged into — not when you want general "how do I stay safe online" advice with nothing to look at. This tool never asks for a password or tries to log into anything; it only reads what you show it.

## What you need to provide

**Data source: Manual.** You paste or upload screenshots, or type out what a settings page says, from pages like:
- Google Security Checkup / "Your devices"
- Apple ID device list
- Find My device-sharing settings
- Life360 or similar location-sharing app's member list
- Smart-home app (Nest, Ring, SmartThings, etc.) shared-access or co-owner list
- Shared calendar or shared photo-album permission list

Also tell the reviewer: (1) which platforms your screenshots are from, and (2) whether you're currently on a device/account you believe your former partner can't see — if you're not sure, say so.

**Never provide a password or login link.** This tool only works from screenshots/descriptions of pages you're already logged into — it never logs in for you, and nothing about it stores credentials.

## The prompt

Paste the following into any AI chat tool, along with your screenshots and the platform list:

```
You are reviewing screenshots of my account-security and device-sharing
settings so I can see what a former partner might still have access to.
Follow this procedure exactly:

1. Before anything else, show me this safety note, in full, every time:
   "Before you read this: if you think your device or accounts might be
   monitored, review this on a device/account the other person has never
   had access to, and consider clearing your browser history or using a
   private/incognito window afterward. Making changes to a flagged item
   can alert the other person that you found it — some items below are
   marked 'likely detectable' for that reason. This review is based only
   on what's visible in the screenshots I shared; it cannot catch
   everything, and it is not a substitute for a safety plan from a DV
   advocate."

2. Do not ask me for a password or offer to log into anything. If I
   offer credentials, refuse and ask for a screenshot instead.

3. For each screenshot, tell me what platform/setting type it is
   (device list, shared family group, location-sharing members, smart-
   home co-owners, calendar/photo sharing, active login sessions).

4. Check each one against this known-tactics list and flag anything that
   matches:
   - A legacy shared Apple ID / Google family account still active
   - A device you don't recognize, or recognize as your former
     partner's
   - A wearable (smartwatch/tracker) still cloud-linked even if the
     physical device was returned
   - A location-sharing member who is your former partner or an alias
     of theirs
   - Smart-home co-owner/guest access (locks, cameras, thermostats)
     not removed
   - A shared calendar or photo album still granting them access
   - An active login session you don't recognize

5. For every flagged item, give me: what it is, why it's risky, your
   confidence level (High/Medium/Low, and why — screenshots are often
   partial), and whether revoking it would be "likely silent" or
   "likely detectable" by the other person.

6. Order the list: silent-and-high-risk items first, then detectable
   items — and for every "likely detectable" item, tell me to plan the
   timing with a safety consideration in mind rather than act
   immediately.

7. If nothing is flagged, say so, but explicitly remind me this is a
   partial, point-in-time view, not a clean bill of health.

8. Always end with: a note to screenshot/save the current state of
   anything flagged before I change it (it may matter as evidence and
   can't easily be un-revoked to re-check later), and these resources —
   National DV Hotline (US) 1-800-799-7233 or text START to 88788, and
   a suggestion to loop in a DV advocate before acting on anything
   marked "likely detectable."

Never suggest contacting law enforcement or taking legal action on my
behalf — that's my decision. Never guess at details you can't actually
see in what I've shared — ask for a clearer screenshot instead.

My screenshots and the platforms they're from:
[paste/describe screenshots here, noting which platform each is from]
```

## What you'll get back

A single report with, in order: the safety note; a line per screenshot naming the platform/setting reviewed; a numbered, priority-ordered list of flagged access points (each with what it is, why it's risky, confidence level, and whether revoking it is likely silent or likely detectable, plus a suggested action); an explicit hedge if nothing was flagged; and a closing section with the evidence-preservation reminder and hotline/advocate resources.

## Limits — read before relying on this

- This is pattern-matching against a known list of common tactics. It cannot catch a tactic that isn't on that list, and screenshots can be partial or outdated the moment you take them.
- This tool never logs into anything and never sees your actual accounts — only what you choose to show it. If an AI chat tool ever asks you for a password to "check directly," that is not this skill and you should not provide one.
- This is a first-pass self-checkup, not a safety plan. For anything the report marks "likely detectable," or if you have any doubt about your physical safety, involve a domestic violence advocate before changing settings — the National DV Hotline (US) is 1-800-799-7233, or text START to 88788.
