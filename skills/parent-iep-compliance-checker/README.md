# IEP Compliance Flag & Letter Drafter

A self-contained prompt template for parents who have their child's actual IEP (Individualized Education Program) document in hand and want to check it against federal special-education law and their state's requirements before signing it, or get a specific written request instead of a vague complaint. Paste this whole template plus your inputs into any AI chat tool (ChatGPT, Claude, Gemini, Copilot, etc.).

## When to use this
Use this the moment you have your child's actual IEP — current, just-proposed at a meeting, or a draft the school sent ahead of one — and you want to know whether it meets the legal bar, or you have a vague sense something's off but don't know what to specifically ask for. This checks one document (optionally two, to compare against last year's) in a single sitting. It does not remember your child's history between conversations — paste what you need checked each time.

## What you need to provide
**Data source: Manual.** This only works from text you paste yourself — no tool can pull your child's actual IEP from anywhere, because it's protected by federal privacy law (FERPA) and controlled entirely by the school. You need:

1. **The full text of the IEP**, pasted verbatim — not a summary, not "it says he gets speech therapy." If you only have a PDF or a scan, transcribe/OCR it into text first, then paste that. The more complete the paste, the more complete the check.
2. **Your US state.**

Optional, if you want more:

3. **A prior year's IEP text**, pasted verbatim, if you want to check whether anything was reduced without explanation.
4. **Your child's age** as of this IEP's start date — this matters because transition-planning requirements kick in at 16.

Before you paste anything: pasting your child's IEP into a general AI chat tool shares that text with that tool's provider. If you're not comfortable with that, redact your child's full legal name, student ID number, and date of birth first — initials and a grade level are enough for this to work. This is a heads-up, not a requirement; proceed with whatever you're comfortable sharing.

## What it checks
Using the text you paste, the assistant will check, item by item, whether each of the following is actually present, present but vague, or missing from what you gave it:

- **Present levels of performance**: does it include actual baseline data (numbers, test names, dates) or just a narrative?
- **Each annual goal**: does it have a measurable baseline, a specific target, and a stated way of measuring progress?
- **Each service** (speech, OT, counseling, etc.): does it state frequency, session length, location, AND start date — all four?
- **Least-restrictive-environment (LRE) justification**: if your child is removed from general education for any part of the day, is that justified in writing?
- **Accommodations and modifications**: for both classroom work and testing.
- **Procedural safeguards notice**: is it dated?
- **Transition services** (only if your child is 16+): postsecondary goals and a transition plan.
- **Meeting, annual review, and triennial reevaluation dates.**

It will never assume something is fine just because it wasn't flagged as missing — if you didn't paste a section, it says "not found in the text provided," not "looks compliant."

## What you get back
A structured response with:

1. **A flag table** — one row per gap found, naming the IEP component, what's missing or vague, and whether the basis is a federal IDEA requirement (with the general regulation it relates to, e.g. 34 CFR §300.320) or a state-specific requirement (marked "verify" because no AI tool has a live, current feed of your state's regulations — always confirm state-specific flags with your state's Parent Training and Information (PTI) Center, which IDEA funds in every state, or a special-education advocate).
2. **A drafted request paragraph for each flag** — specific, polite, and framed as asking for clarification or documentation, never as an accusation.
3. **One combined, ready-to-send letter** stitching all the requests together, addressed to "IEP Team," that you can send as-is or edit.
4. **Regression notes**, only if you also pasted a prior year's IEP — any services, minutes, or accommodations that went down without a documented reason.
5. **A limits section**, every time: this only sees what you pasted, state-specific items need independent verification, and nothing here is a legal determination — it's a list of things worth asking about, not proof the school broke the law. Have an advocate or attorney review before filing any formal complaint.

## The prompt template

Paste the following into your AI tool of choice, filling in your own IEP text and state:

```
You are reviewing my child's IEP for likely compliance gaps against federal IDEA requirements and [MY STATE]'s specific special-education requirements. Here is the full text of the IEP:

[PASTE FULL IEP TEXT HERE]

My child's age as of this IEP's start date: [AGE, if you want the transition-services check]

(Optional — paste last year's IEP text here if you want a regression comparison: [PASTE PRIOR IEP TEXT])

Please:
1. Go component by component (present levels/baselines, each goal's measurability, each service's frequency/duration/location/start date, LRE justification, accommodations, procedural safeguards notice date, transition services if applicable, meeting/review/reevaluation dates) and tell me, for each, whether it's present, vague, or missing from the text I gave you — don't assume anything is fine if I simply didn't paste it.
2. Flag each gap, citing the general federal IDEA provision it relates to where you're confident of the citation, and separately flag anything specific to [MY STATE] as "verify" rather than guessing a state code section.
3. Draft one short, specific, non-accusatory request paragraph per flag, asking for clarification or documentation.
4. Combine them into one ready-to-send letter addressed to "IEP Team."
5. If I gave you last year's IEP too, flag any service/minute/accommodation reduction with no documented rationale.
6. Close with a limits section: this only reflects what I pasted, state-specific flags need independent verification via my state's Parent Training and Information Center or an advocate, and nothing here is a legal determination.

Before you start, give me a one-line heads-up that pasting this into an AI tool shares it with the tool's provider, and that I can redact my child's full name/student ID/DOB if I'd rather not share them — then proceed with what I gave you either way.
```

## Guardrails this is built with
- It will never tell you a flagged gap is a confirmed legal violation — only that it's something worth asking about.
- It will never invent a specific state statute or code section — unclear state items get marked "verify," not a made-up citation.
- It will never treat an un-pasted section as compliant — missing input means "not found," not "fine."
- It will never give clinical or therapy-method advice — it stays in the compliance/documentation lane, not treatment.
- It will always tell you upfront if you didn't give a state, and skip the state-specific flags rather than quietly doing federal-only and calling it complete.
