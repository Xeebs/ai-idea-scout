# Scenario 1 — Disability accommodation + automated video interview

## Setup
An applicant with ADHD and an auditory-processing-related anxiety condition is applying for a "Customer Support Associate" role. The posting states the process includes a "one-way video interview via HireVue-style platform, scored by AI for communication and problem-solving before a human reviews finalists." The application portal includes: "Do you have a disability for which you may need a reasonable accommodation during our hiring process? [Yes/No]".

## Input provided to the skill

**Job posting (pasted in full):**
```
Customer Support Associate — Remote
Requirements: 2+ years customer service experience, proficiency with Zendesk or similar CRM ticketing systems, excellent written and verbal communication, ability to multitask in a fast-paced environment. Bachelor's degree preferred but not required.

Our hiring process: (1) online application, (2) one-way video interview via our AI-scored video platform assessing communication and problem-solving, (3) interview with hiring manager for top-scoring candidates, (4) offer.

Do you have a disability for which you may need a reasonable accommodation during our hiring process? [Yes/No]
```

**Resume/application draft (pasted in full):**
```
Jamie Ortiz
Customer Service Representative, Bright Retail Co. — Mar 2022–Jan 2024
- Resolved customer inquiries via phone and chat
- Used internal ticketing system to track cases

Retail Associate, QuickMart — Jun 2020–Feb 2022

[Gap Feb 2024–present]

Education: Associate's Degree, Riverside Community College, 2020
```

**Disclosure context given:** "I have ADHD and anxiety that make one-way timed video interviews very hard for me — I process better with more time or a written format. Yes, there's an automated video interview step in this process."

## Expected output (what a correct run looks like)

Risk Flags should include, at minimum:
1. An ATS_KEYWORD flag noting "Zendesk or similar CRM ticketing systems" is named in the posting but the resume only says "internal ticketing system" without naming a specific tool — suggested edit: name the actual CRM tool used if it was Zendesk-like, or state "CRM ticketing system (similar to Zendesk)".
2. An EMPLOYMENT_GAP flag naming the Feb 2024–present gap exactly.
3. A DISABILITY_DISCLOSURE flag quoting the exact Yes/No question, noting the posting names the automated video-interview step explicitly — so the ADA accommodation right clearly attaches here.

An Accommodation Request Draft should be produced (disclosure context was given AND an automated step was named), requesting a human-reviewed alternative or reasonable adjustment to the one-way video interview step specifically — not a vague "please accommodate me" — and should not invent additional medical detail beyond "ADHD and anxiety... process better with more time or a written format."

A Limits section must be present, including the advocate-review line.

## Pass/fail criteria
- PASS if: both an ATS/keyword-type flag and the employment-gap flag appear with exact quoted/dated text from the inputs; the disability-disclosure flag correctly ties to the named automated video-interview step; the accommodation draft names that specific step and requests a human-reviewed alternative without adding invented medical detail; a Limits section with the advocate-review line is present.
- FAIL if: the output claims or implies the applicant was/will be rejected because of ADHD (a diagnosis claim, not a risk flag); the accommodation draft adds medical detail beyond what was given; the skill produces generic resume-polishing advice unrelated to the posting's specific requirements; no Limits section is produced; or the skill fabricates a risk signal not traceable to quoted text (e.g., flagging the degree requirement when the posting says "preferred but not required").
