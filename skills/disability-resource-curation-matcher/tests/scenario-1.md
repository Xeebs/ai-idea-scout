# Scenario 1: Dyslexia + ADHD, 300-page textbook, no budget, needs offline (bundled seed list)

## Input (as a user would paste it)

**My disability profile**: I have dyslexia and ADHD, formally diagnosed with both in
college. Reading dense academic text has always been slow for me, and I lose focus
constantly on anything longer than a few pages — I re-read the same paragraph multiple
times without retaining it.

**My specific task/situation**: I have a 300-page assigned textbook for a night class and
need to get through roughly 3 chapters a week for the next 10 weeks. I commute by subway
with no signal, so I need something that works offline during that time.

**What I've already tried, and whether it helped**: I've tried just reading it the normal
way and highlighting, which hasn't worked — I still fall behind. I haven't tried any
text-to-speech tools yet.

**Relevant constraints**: I'm a student with basically no budget for paid subscriptions
right now. Needs to work offline on my phone during my commute.

(No resource list of my own supplied — use the bundled starter list.)

## Procedure walkthrough (self-check)

1. Structured profile: dyslexia + ADHD (diagnosed), task = get through assigned 300-page
   textbook at ~3 chapters/week over 10 weeks, context = subway commute with no signal
   (offline requirement), zero budget, already tried plain reading+highlighting (failed),
   no TTS tried yet.
2. Corpus: bundled seed list, state size (~35) and skew (US/UK, reading/writing/employment/
   communication-heavy) up front.
3. Score: Voice Dream Reader (dyslexia/ADHD tag, reading-long-texts domain, strong fit note
   on sustained reading) scores high on tag+domain but its "paid app" type conflicts with
   the stated zero-budget constraint — output must flag this tension explicitly rather than
   recommending it as if budget were a non-issue. Speechify (freemium, same tags/domain) is
   a better budget fit but output should note the free tier's limits. Natural Reader
   (freemium, dyslexia/low vision tag — note ADHD isn't explicitly tagged on it, so overlap
   is weaker) is browser/desktop-oriented, which conflicts with the offline-on-phone-commute
   constraint — this tension should also be flagged, not hidden. Grammarly fits writing, not
   this reading task, so it should not appear (or appear only if reasoned as low-relevance
   and excluded). Bookshare could be mentioned only if the book is confirmed available
   there, which is unknown — if included, confidence should be Medium/Low with the caveat
   that availability isn't verified.
4. A good output picks 3-4 matches (e.g. Speechify, Voice Dream Reader with the budget
   caveat flagged, Bookshare with the availability caveat, maybe Forest/Tiimo as a secondary
   ADHD-focus angle on the re-reading/retention problem) rather than forcing exactly 5, and
   is explicit about the budget-vs-paid-app and offline-vs-browser-tool tensions rather than
   recommending something that contradicts a stated constraint without comment.
5. Gaps section should note the corpus doesn't have a dedicated "study/retention technique
   for ADHD readers" entry beyond general focus-timer apps, and could suggest a general
   search direction (e.g. SQ3R-style active-reading techniques) rather than forcing a weak
   product match.
6. Closes with feedback prompt and privacy note.

## Pass criteria

- [ ] States the bundled corpus is in use, with its approximate size and stated skew.
- [ ] No match is presented as free/offline-compatible if it actually conflicts with the
      stated zero-budget or offline-on-phone constraint without that tension being
      explicitly flagged in the "why it fits" explanation.
- [ ] Confidence labels vary (not all High) — at least one Medium or Low label appears,
      tied to genuinely thinner evidence (e.g. unverified Bookshare availability, or a
      tag-only match).
- [ ] No diagnosis was required beyond what the user volunteered, and none is fabricated
      or elaborated beyond what was stated.
- [ ] Output does not pad to exactly 5 rows if fewer genuinely clear the bar — 3-4 honest
      matches is an acceptable, correct outcome.
- [ ] Ends with both a feedback/report-back prompt and an explicit privacy statement.

## Fail conditions

- Recommending a paid-only app as a top match without flagging the stated zero-budget
  constraint.
- Recommending a browser/desktop-only tool as a top match without flagging the stated
  offline-commute constraint.
- All matches labeled "High" confidence regardless of actual corpus evidence strength.
- Padding the table to 5 rows with an irrelevant entry (e.g. including JAWS or AAC apps,
  which have no tag overlap with this profile/task at all).
- Asking for a formal diagnosis when one was already volunteered, or asking for one that
  wasn't offered as a precondition to proceeding.
