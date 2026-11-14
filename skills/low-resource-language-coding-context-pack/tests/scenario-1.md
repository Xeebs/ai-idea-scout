# Scenario 1 — Pharo/Smalltalk open-source repo (Connected path)

## Input

A small team is adopting Pharo for a new internal tool and keeps finding that their AI coding assistant suggests Java/Python-flavored code that doesn't compile. They want a context pack to drop into their project's `CLAUDE.md`.

They provide:

- **Language/dialect**: Pharo (Smalltalk-80 dialect).
- **Corpus (Connected path)**: the GitHub repo `pharo-project/pharo` (public, well-known Pharo core repo) — specifically they point to the `src/Kernel` and `src/Collections-Sequenceable` directories, plus the repo's top-level `README.md`.
- **Style guide**: none beyond the repo's own README and code comments.
- **Target use**: a `CLAUDE.md` section for their own small Pharo project.

Representative pasted snippet (one of several the user includes alongside the repo pointer, since not every tool can browse a URL live):

```smalltalk
OrderedCollection>>add: anObject
    "Add anObject to the end of the receiver. Answer anObject."
    self addLast: anObject.
    ^ anObject

Object>>error: aString
    "Display a walkback for the receiver and raise an error with the given message."
    ^ Error new signal: aString
```

Plus 6 more representative method snippets from the Kernel/Collections directories (class comments, method categories, `^` return syntax, keyword-message method signatures).

## Procedure checklist (what the skill must actually do)

- [ ] Confirms the single scope is "Pharo (Smalltalk)" and does not blend in Python/Java comparisons as if they were part of the pack's subject matter.
- [ ] Notes which path was used (Connected: GitHub repo pointer + pasted representative snippets) and the approximate corpus size (~7 snippets + README), and sets confidence to Low-to-Medium given the modest sample.
- [ ] Idiom catalogue correctly identifies and quotes real Smalltalk conventions: keyword-message method signatures (`add:`, `error:`), explicit `^` return statements, class-comment-as-first-line-string convention — each tied to a quoted example from the snippets provided, not invented.
- [ ] Failure-modes section names at least 2 concrete "assistant might suggest X, but Pharo actually does Y" pairs that make sense for a Python/Java-trained assistant meeting Smalltalk for the first time (e.g., assistant omitting the explicit `^` return and assuming implicit last-expression return like Python/Ruby; assistant writing `object.method(arg)` dot-call syntax instead of Smalltalk's keyword-message syntax; assistant assuming exceptions use `try/catch` rather than Smalltalk's `on:do:` pattern) — each grounded in or clearly consistent with the provided snippets, not fabricated unrelated claims.
- [ ] Reference card covers method declaration syntax, class comment convention, and explicitly flags anything about Pharo's Tonel file format or broader ecosystem facts not visible in the 7 pasted snippets as "general knowledge, not corpus-verified."
- [ ] Test harness section: since no test code was included in the pasted snippets, the output says so plainly rather than inventing a plausible-looking SUnit example.
- [ ] Gaps section recommends pulling in more files (e.g. an actual test directory, a style guide) to raise confidence.
- [ ] Output is a single markdown document following the six-section structure, short enough to actually paste into a `CLAUDE.md`.

## Pass criteria

Pass if the generated pack: (a) stays scoped to Pharo only, (b) grounds every idiom/failure-mode claim in the provided snippets rather than inventing unrelated syntax facts, (c) explicitly states "no tests found" rather than fabricating a test example, and (d) is usable as-is when pasted into a `CLAUDE.md`. Fail if it invents Pharo syntax not visible in the snippets and not flagged as general knowledge, or if it silently fabricates a test pattern.
