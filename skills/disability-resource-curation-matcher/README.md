# Disability Resource Curation Matcher

A prompt template for disabled people, caregivers, or advocates trying to find a tool,
service, or community that fits **one specific disability profile and one specific task** —
not a generic "top resources for dyslexia" listicle, but an explained match to your actual
situation.

## The problem this solves

Mainstream recommendation lists assume a "typical" user with a given disability. In
practice, what actually works depends on the specific combination of disability profile,
the task at hand, and context that generic lists never ask about (budget, offline needs,
what's already been tried). Today, disabled people mostly solve this by trial-and-error or
by informally asking in peer communities (Reddit threads like r/accessibility are full of
people sharing their own personal, hand-built resource lists after giving up on generic
search results). This prompt does that same personalized-fit matching in one pass: it
reads your specific profile and task, matches it against a small tagged resource list, and
explains *why* each suggestion fits your situation specifically — not just that it's
popular for your disability in general.

**This is not a live, exhaustive database and not medical advice.** It matches you against
a small, fixed, bundled starter list (~35 well-known resources) unless you supply your own
list instead. If the bundled list doesn't have a good fit for your specific situation, a
good output says so honestly rather than forcing a weak match.

## How to use this

Copy the prompt below into any AI chat tool (Claude, ChatGPT, etc.) and fill in your
profile and task where indicated. If you have your own list of resources you want matched
against instead of the bundled one below, paste it in place of the bundled list.

---

### Prompt template

```
You are matching me to disability resources (tools, services, techniques, or communities)
that fit MY specific disability profile and MY specific task — not a generic "popular
resources for my disability" list. Here is my situation:

- My disability profile (in my own words, no diagnosis label required): [e.g. "I have
  dyslexia and ADHD" or "I lose focus and can't finish long documents, not formally
  diagnosed with anything"]
- My specific task/situation: [e.g. "I need to get through a 300-page assigned textbook
  by next month" — be specific, not "help with reading"]
- What I've already tried, and whether it helped: [or "nothing yet"]
- Relevant constraints: [e.g. "no budget for paid apps," "needs to work offline," "I
  already use a screen reader, I need help with comprehension on top of that" — or "none"]

Match me against this resource list (use this bundled starter list unless I've pasted my
own list above instead — if I pasted my own, use mine and ignore this one):

| Resource | Type | Disability tags | Task domain | Fit note | Basis |
|---|---|---|---|---|---|
| NVDA | Free screen reader (Windows) | Blind, low vision | Computer use, reading, work | Free alternative to JAWS; strong general app/web support | Widely known free standard in blind/low-vision community |
| JAWS | Paid screen reader (Windows) | Blind, low vision | Computer use, work, enterprise software | Long-standing enterprise standard; strong Office/legacy-app support | Widely known paid standard in blind/low-vision community |
| VoiceOver | Built-in screen reader (macOS/iOS) | Blind, low vision | Computer/mobile use | Free, pre-installed, tight iOS/Mac integration | Built-in Apple accessibility feature, broadly documented |
| Seeing AI | Free app (Microsoft) | Blind, low vision | Daily tasks, reading printed text, product ID | Uses phone camera to read text/describe scenes/identify products aloud | Free Microsoft accessibility app, broadly recommended |
| Be My Eyes | Free app | Blind, low vision | Daily tasks needing visual confirmation | Connects user via video call to a sighted volunteer for one-off visual tasks | Widely known free community-volunteer app |
| Aira | Paid visual interpreter service (free tiers via partners) | Blind, low vision | Navigation, daily tasks | On-demand professional visual interpreter, not volunteer-based like Be My Eyes | Known paid alternative/complement to Be My Eyes |
| Voice Dream Reader | Paid text-to-speech reading app | Dyslexia, low vision, ADHD | Reading long texts (books, PDFs, articles) | Strong highlighting/pacing controls often cited as helpful for sustained reading | Commonly recommended in dyslexia/ADHD reading-support discussions |
| Speechify | Freemium text-to-speech app | Dyslexia, ADHD, low vision | Reading | Browser/app TTS, popular lower-cost alternative to Voice Dream | Commonly recommended alongside Voice Dream Reader |
| Natural Reader | Freemium text-to-speech app | Dyslexia, low vision | Reading documents/PDFs | Browser extension + desktop app, free tier usable for short documents | Commonly recommended free-tier TTS option |
| Bookshare | Free accessible e-book library (verified print disability required) | Dyslexia, blind, low vision | Reading, especially students | Huge accessible-format catalog; requires documented qualifying disability to register | Established nonprofit library for people with print disabilities |
| Learning Ally | Subscription audiobook library, often school-provided | Dyslexia | Reading (K-12/college students) | Human-narrated audiobooks, often already licensed through a school | Established education-sector audiobook service for print disabilities |
| Grammarly | Freemium writing assistant | Dyslexia, dysgraphia, ADHD | Writing | Catches grammar/clarity issues beyond basic spellcheck; browser + doc integration | Broadly known general-purpose writing tool, commonly cited by dyslexic writers |
| Otter.ai | Freemium live transcription app | Deaf, hard of hearing, ADHD (note-taking) | Meetings, lectures | Real-time transcript + recording, searchable notes afterward | Commonly recommended for lecture/meeting access and ADHD note-taking |
| Google Live Transcribe | Free real-time captioning app (Android) | Deaf, hard of hearing | Everyday in-person conversation | Phone-based live captions for face-to-face talk, no account needed | Free Google accessibility app, broadly documented |
| Ava | Subscription captioning app | Deaf, hard of hearing | Group conversations, calls | Multi-speaker live captioning, geared to group settings not just 1:1 | Commonly cited alongside Live Transcribe for group use cases |
| CART captioning | Professional service, often requestable as an accommodation | Deaf, hard of hearing | Events, classes, meetings | Human stenographer-provided real-time captions; typically arranged through an accommodations office | Established professional accommodation service, not an app |
| Proloquo2Go | Paid AAC app | Nonverbal, minimally verbal | Communication | Widely used symbol-based AAC app, strong default vocabulary | Market-leading AAC app, broadly documented |
| CoughDrop | Subscription AAC app/platform | Nonverbal, minimally verbal | Communication | Open-format (OBF) AAC platform, supports custom vocabulary boards | Commonly cited AAC option with open export format |
| Loop earplugs | Commercial product | Autism, ADHD, migraine, misophonia | Noise sensitivity in daily environments | Partial-noise-reduction earplugs; widely discussed in neurodivergent sensory threads | Popular consumer product frequently recommended in sensory-sensitivity discussions |
| Tiimo | Subscription visual planner app | ADHD, autism | Daily planning, routines | Built specifically around visual schedules/timers for neurodivergent routines, not a generic to-do app | Purpose-built for ADHD/autism planning, commonly recommended in those communities |
| Finch | Freemium habit/self-care app | ADHD, anxiety | Routine-building, motivation | Gentle gamified habit tracker, often cited as lower-pressure than standard habit apps | Commonly recommended in ADHD self-care discussions |
| Forest | Freemium focus-timer app | ADHD | Task initiation, focus sessions | Gamified Pomodoro-style timer; blocks phone use during a session | Widely known focus app, frequently cited in ADHD productivity discussions |
| Todoist | Freemium task manager | ADHD, executive function differences | Daily/weekly task planning | Flexible reminders and recurring tasks; needs active setup, not plug-and-play structure | Broadly known general task manager, commonly adapted by ADHD users |
| Job Accommodation Network (JAN) | Free consulting service (US, ADA-funded) | Any disability | Workplace accommodation requests | Free phone/email consultations on specific accommodation ideas for a specific job/task | US federally funded service, specifically built for this exact task |
| Ticket to Work (SSA) | Free federal program (US) | Any disability receiving SSDI/SSI | Returning to work without losing benefits | Connects benefit recipients to employment support while protecting benefit status during transition | Official SSA program for this exact benefits-vs-work tension |
| Local Aging and Disability Resource Center (ADRC) | Free public service (US) | Any disability | Navigating local benefits and services | Single local entry point for benefits navigation; quality varies by county | Federally mandated no-wrong-door public resource network |
| Protection & Advocacy (P&A) agency | Free legal advocacy org (one per US state) | Any disability | Rights/benefits disputes, legal advocacy | Federally mandated disability rights legal advocacy, free in every state | Established legal-advocacy resource, not a consumer product |
| Through the Looking Glass | Nonprofit organization | Parents with disabilities | Parenting with a disability | Specializes specifically in disabled parents' adaptive parenting equipment/techniques | Established nonprofit with this specific, narrow focus |
| Parent to Parent USA | Nonprofit peer-support network | Parents of children with disabilities | Parenting a disabled child | Matches parents to peer-mentor parents with similar experience, state-by-state chapters | Established national peer-support network |
| r/disability, r/accessibility, r/ADHD, r/dyslexia (Reddit) | Free peer communities | Varies by subreddit | Informal resource-sharing, peer validation | Where much of the "what actually worked for me" informal sharing already happens today | Direct source of the gap this template responds to |
| Disabled And Here | Free representation/community project | Any disability | Identity, representation, finding community | Not a tool/service — a community and representation resource | Known disability-representation project |
| Bearable | Freemium symptom-tracking app | Chronic illness, invisible disability, mental health | Medical self-advocacy, pattern-spotting | Correlates symptoms with sleep/food/mood/meds to bring concrete patterns into a doctor visit | Commonly recommended in chronic-illness self-advocacy discussions |
| AbilityJobs | Free job board | Any disability | Job search | Disability-focused job board, candidate profile flags accommodation needs upfront | Established disability-specific job board |
| Local Center for Independent Living (CIL) | Free public service (US network) | Any disability | General skills/benefits/peer mentoring | In-person/local peer mentoring and skills training, federally funded network | Established CIL network |

This list is a small, fixed starter set — English-language, US/UK-centric, and weighted
toward reading/writing, employment, and communication resources. Tell me this up front in
your answer, every time.

Now:

1. Build a structured understanding of my profile + task + constraints — don't invent
   anything I didn't say (no assumed diagnosis, no assumed budget, no assumed severity).
2. Score every resource on the list against my profile on three things: does its
   disability tag overlap mine, does its task domain overlap mine, and does its fit note
   speak specifically to my stated context (not just a loose tag match).
3. Give me the top 3-5 matches that genuinely clear a relevance bar — if fewer than 3
   genuinely fit, give me fewer and tell me the list came up short for my combination.
   Never pad the list with weak matches just to hit a count.
4. For each match, explain specifically why it fits MY stated situation (tie it to what I
   actually said, not a generic description of the resource category).
5. Label each match's confidence: High (the fit note speaks directly to my context),
   Medium (solid tag match, no specific context evidence), or Low (plausible but thin,
   verify yourself).
6. Tell me honestly what part of my profile/task this list is thin on, and suggest a
   general search direction for that gap instead of forcing an unrelated match to look
   like coverage.
7. Ask me to report back which resource I actually tried and whether it worked for my
   specific situation.
8. Remind me this is not medical advice, no diagnosis was required, and nothing about my
   profile is being stored anywhere beyond this conversation.

Format your answer as:

## Profile Captured
(restate my profile, task, and constraints as you understood them — flag anything I didn't
specify rather than assuming it)

## Matched Resources
Table: Rank | Resource | Type | Why it fits YOUR situation | Confidence | Corpus fit note
(3-5 rows, or fewer — never padded)

## Gaps & Caveats
(what the list is thin on for my specific case, plus a general-search suggestion if
relevant; restate that this is a small, fixed starter list, not a live/exhaustive database)

## Try It & Report Back
(ask me to report back what I tried and whether it worked)

## Privacy Note
(confirm nothing about my profile is stored or shared beyond this conversation)

Never tell me a match is guaranteed to work, never require a diagnosis label from me,
never invent a "worked for someone" story that isn't in the fit note above, and never pad
the shortlist with weak matches just to reach 3-5 rows.
```

---

## What good output looks like

- A profile summary that reflects exactly what you described, not a generic disability
  stereotype with your condition name swapped in.
- 3-5 matches (or fewer, honestly) each explained against your specific stated task and
  constraints — not a repeat of the resource's generic marketing description.
- Confidence labels that actually vary (not everything marked "High") based on how
  specific the corpus fit note really is.
- An explicit, upfront statement of which resource list was used and its known skew/size.
- A gaps section that names what's missing rather than quietly ignoring it.
- A closing feedback prompt and a privacy statement, every time.

## What this does not do

- It is not medical, clinical, or legal advice, and it never requires a diagnosis label to
  work — a functional description is enough.
- It does not connect to any live resource database, AT3 Center directory, or app store —
  everything it matches against is the fixed list above (or a list you paste in yourself).
  As of today, no mature public API for a general disability-resource directory exists
  (the old AbleData federal directory is defunct, and the AT3 Center does not expose a
  documented public API) — if that changes, a connected version becomes possible, but this
  template is not that version.
- It does not grow or remember your profile across conversations — each run is a one-off
  match; if you want a persistent, shared, community-curated database that gets better over
  time, that's the larger platform this template is a lightweight stand-in for.
