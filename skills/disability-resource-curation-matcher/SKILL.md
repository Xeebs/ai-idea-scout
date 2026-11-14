---
name: disability-resource-curation-matcher
description: Matches a person's free-text disability profile and specific task (reading, employment, parenting, benefits navigation, etc.) against a tagged corpus of community-reviewed disability resources, and returns a short, individually-explained shortlist instead of a generic "popular resources for X disability" list — for disabled people, caregivers, or advocates trying to find a tool/service/community that fits one specific situation.
---

# Disability Resource Curation Matcher

## When to use this

Use this the moment someone describes their own (or a person they support's) disability
profile *and* a concrete task or life-domain they're stuck on, shaped like: "I have
dyslexia and ADHD and I'm trying to get through a 300-page textbook," "my client is deaf
and starting a new job, what should she ask for," "I'm a disabled parent and need
equipment that actually works for someone with my mobility limits," or "has anyone
actually found something that works for [specific combination], not just generic advice."
This is specifically for **matching to existing resources for one individual situation** —
not for inventing a new assistive technology, not for general disability-rights
information, and not for a generic "top 10 tools for dyslexia" listicle that ignores the
person's specific combination of disability + task + context. If the person hasn't named
both a disability-related profile and a specific task, ask for the missing one before
matching — a profile with no task, or a task with no profile, produces generic advice,
which is exactly what this skill exists to avoid.

## Inputs

**Data source**: Manual — the person describes their disability profile and the specific
task or situation in their own words (e.g. "I have dyslexia and ADHD, I'm trying to read a
300-page textbook for a class"), optionally pasting an existing diagnosis or accommodation
letter for more precision. The resources matched against come from a small bundled seed
list (`resources/seed-resources.md`, ~35 entries) included with this skill, or from a
resource list the user supplies themselves (their own CSV, markdown table, or pasted list
of tools/services with notes on what they're for) — never from a live external API. No
mature public API for a general disability-resource directory exists today (AbleData, the
former US federal directory, is defunct; its successor, the AT3 Center, does not expose a
documented public API), so this is a static-corpus matcher, not a connected lookup, and
every output must say so plainly.

Ask for, if not already given:
1. **Disability profile, in the person's own words** — functional description is enough
   ("I lose focus halfway through long documents and reading has always been slow for me"),
   a diagnosis label is never required to proceed.
2. **The specific task or situation** — not "help with my dyslexia" but "I need to get
   through a 300-page assigned textbook by next month."
3. *(Optional)* Relevant context already tried — what they've already attempted and
   whether it helped, existing devices/apps/accommodations in place, severity/constraints
   that change what would actually work (e.g. "no budget for paid apps," "needs to work
   offline," "already has a screen reader, just needs reading-comprehension help on top of
   that").
4. *(Optional)* A resource list of their own to match against instead of the bundled seed
   list — useful if they're testing their own curated database rather than this skill's
   starter set.

## Procedure

1. **Build a structured profile** from input (1)+(2)+(3): disability type(s) or functional
   description, the task/domain, and any already-tried context — never assume unstated
   specifics (don't infer severity, a specific diagnosis, or a budget that wasn't given).
2. **Select the corpus**: if the user supplied their own resource list, use it and say so;
   otherwise use `resources/seed-resources.md` and state its size (~35 entries) and its
   known skew (English-language, US/UK-centric, weighted toward reading/writing,
   employment, and communication resources) up front, every time — never present it as
   comprehensive.
3. **Score every corpus entry** against the structured profile on three axes: disability-tag
   overlap, task-domain overlap, and whether the entry's fit note specifically addresses the
   person's stated context (not just a generic tag match). Rank by combined fit, not by tag
   overlap alone.
4. **Select the shortlist**: return the top 3-5 entries that clear a genuine relevance bar.
   If fewer than 3 entries clear the bar, return fewer — never pad with low-relevance
   entries just to hit a count, and say explicitly that the corpus came up short for this
   combination.
5. **Write an individual "why this fits" explanation per match** that ties back to the
   person's specific stated profile and task (e.g. "you said you need this to work
   offline — Voice Dream Reader's offline mode covers that; a browser-only tool like
   Natural Reader's free tier would not"), not a generic description of the resource
   category.
6. **Assign a confidence label per match**: `High` if the corpus fit note speaks directly
   to the person's specific context, `Medium` if it's a solid tag match without specific
   context evidence, `Low` if it's a plausible but thin match the person should verify
   themselves before relying on it.
7. **Surface gaps honestly**: name any part of the person's profile the corpus is thin on
   (e.g. a disability type, region, or domain barely represented), and suggest adjacent
   corpus categories or a general search strategy for that gap — don't force-fit an
   unrelated entry to look like coverage.
8. **Close with a feedback prompt and a privacy note** (see Output format) — never end
   without both.

## Output format

```
## Profile Captured
- Disability profile (as understood):
- Task/situation:
- Already tried / relevant context: (or "none given")
- Corpus used: bundled seed list (~35 entries, skewed US/UK, reading/writing/employment/
  communication-heavy) OR user-supplied list (<N> entries)

## Matched Resources
| Rank | Resource | Type | Why it fits YOUR situation | Confidence | Corpus fit note |
|---|---|---|---|---|---|
(3-5 rows, or fewer if the corpus didn't clear the bar — never padded)

## Gaps & Caveats
- What part of the profile/task the corpus is thin on, if any, and a general-search
  suggestion for that gap instead of a forced match.
- A reminder that this is a fixed, bundled (or user-supplied) snapshot, not a live or
  exhaustive database.

## Try It & Report Back
- Ask the person to note which resource(s) they actually tried and whether it worked for
  their specific situation — frame this as exactly the kind of "who it worked for" note
  that would make a future, larger version of this corpus more useful to the next person
  with a similar profile.

## Privacy Note
- Nothing about this profile is stored, logged, or shared beyond generating this response;
  no diagnosis or identifying detail was required to produce it.
```

## Guardrails

- Never require a diagnosis label to proceed — a purely functional description is a valid
  and sufficient input; asking "what's your official diagnosis" when the person didn't
  volunteer one is itself a failure of this skill's purpose.
- Never present a match as a guarantee or as medical/clinical advice — language is always
  "may fit," "commonly recommended for," or "worked for people with a similar profile,"
  never "this will fix your [condition]."
- Never fabricate a "who it worked for" testimonial not present in the corpus entry's fit
  note — if a corpus entry's evidence is thin (tag match only), label it `Low` confidence
  and say so, rather than inventing supporting detail to make it sound stronger.
- Never pad a shortlist to 3-5 entries by including matches that didn't clear the relevance
  bar — a shorter, honest list beats a padded one, and an explicit "the corpus came up
  short here" is a valid, useful output.
- Never present the bundled seed list (or any user-supplied list) as a live, exhaustive, or
  continuously updated database — always state its size and known skew in every response.
- Never retain, log, or repeat the person's disability profile outside of generating this
  one response.
- Never silently substitute a generic "popular resources for [disability]" answer when the
  person gave a specific task/context — if a task is missing, ask for it rather than
  defaulting to generic advice.
