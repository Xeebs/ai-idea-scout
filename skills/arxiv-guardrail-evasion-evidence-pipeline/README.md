# Paper-to-Evidence Draft

A self-contained prompt template for turning a newly-found arXiv paper about a guardrail-evasion, jailbreak, or prompt-injection bypass technique into a reviewable PR/issue entry for a curated benchmark or "awesome-*-security" awareness repo — matching that repo's existing format, without you having to manually re-read the paper and reformat it by hand.

## Who this is for

Maintainers of curated community benchmark/awareness repos (the "awesome-agentic-ai-security" style lists) and AI red-team/trust-safety engineers who track guardrail-evasion research to know what to test their own stack against. If you've ever found a new jailbreak paper on arXiv and thought "I should add this to our list" and then put it off because reformatting it by hand is tedious, this is for you.

## What you need to hand over

This is a **manual, paste-based** workflow — it does not connect to arXiv's API or GitHub's API on your behalf. Every time you use it, paste:

1. **The arXiv paper link or ID.**
2. **The abstract text, in full.**
3. **(Recommended) The specific paragraph reporting the bypass rate, success rate, or affected models** — if that number isn't in the abstract (it usually isn't), paste the Results paragraph that has it.
4. **One existing entry copied verbatim from your target repo** — this is how the output matches your repo's exact format instead of guessing at a generic template. If you skip this, you'll be asked for it before anything is drafted.

## The prompt template

Paste this into any AI chat tool, filling in the four items above:

```
You are drafting a reviewable evidence entry for a curated guardrail-evasion/jailbreak
benchmark repo, following the "evidence changes only, maintainer verifies before
merging" pattern. Do not invent any fact, number, or claim not present in the text
I give you.

ARXIV PAPER LINK/ID: <paste>
ABSTRACT: <paste full abstract>
ADDITIONAL TEXT (bypass rate / affected systems, if not in abstract): <paste or write "none provided">
EXAMPLE EXISTING ENTRY FROM MY TARGET REPO (copy one verbatim, exact formatting): <paste>

Do the following:
1. Extract from my pasted text: paper title, arXiv ID, the specific evasion/bypass
   technique named, the target system(s)/model(s) tested, and any reported
   quantitative bypass/success rate. If a bypass rate or affected-systems list isn't
   present in what I pasted, mark it "Not reported in provided text" rather than
   estimating one.
2. Reverse-engineer the exact field structure of my pasted example entry: field
   names, their order, bullet vs. table formatting, citation/link style, typical
   length.
3. Draft a new entry matching that structure field-for-field, using only facts
   traceable to what I pasted.
4. Wrap it in a PR/issue body: a one-paragraph plain-language technique summary,
   the entry itself, a source citation with the arXiv link, and an explicit
   verification caveat line telling the maintainer to verify the reported figures
   against the paper before merging.
5. List, under a separate "Needs maintainer input" section, every field my target
   format requires that my pasted text couldn't support — do not guess at these.

Output exactly these four sections: "Suggested PR title", "New entry (target repo
format)", "PR/issue body", and "Needs maintainer input".
```

## What you get back

- A suggested one-line PR title.
- The new entry, formatted to match your repo's existing style exactly.
- A full PR/issue body: technique summary, the entry, the arXiv source citation, and a verification-caveat line.
- A "Needs maintainer input" list of any field the pasted material couldn't support — never filled in with a guess.

You then review it, verify the claims against the paper yourself, and open the PR or issue in your own repo. This tool never does that submission step for you.

## What this does not do

This is the manual, one-paper-at-a-time companion to a larger idea for a fully automated bot that continuously watches arXiv's cs.CR/cs.AI listings and opens PRs on its own, using arXiv's and GitHub's APIs directly. That automated version doesn't exist yet as a packaged tool — this skill is usable today, by hand, the moment you find a paper worth adding.

## Guardrails this template enforces

- It will never invent a bypass rate, percentage, CVE/CWE number, or affected-system name that isn't in your pasted text.
- It will never claim to have opened anything on GitHub — it only drafts text for you to submit yourself.
- It will never assume a generic "awesome-list" format if you didn't paste an example entry — it will ask first.
- It always includes the verification-caveat line, because the entire point of this pattern is "evidence changes only, maintainer verifies" — never silent auto-acceptance.
- If what you pasted is actually about a *defense* or *detection* method rather than an evasion/bypass technique, it will flag that and ask you to confirm before drafting an "evasion entry" for it.
