---
name: low-resource-language-coding-context-pack
description: Generates a reusable "context pack" (idiom catalogue, known AI-assistant failure modes, reference card, test-harness pattern) for a low-resource or niche programming language/dialect, to drop into a CLAUDE.md or project skill so coding assistants stop defaulting to mainstream-language habits. Use when someone is about to work (or onboard a teammate) in a language like COBOL, Fortran, Pharo, a regional DSL, or an internal legacy dialect and wants better AI suggestions without fine-tuning.
---

# Low-Resource Language Coding Context Pack

## When to use this
Someone is about to do sustained work in a programming language or codebase dialect that mainstream AI coding assistants handle poorly — a legacy enterprise language (COBOL, Fortran, RPG), a niche language (Pharo/Smalltalk, Erlang, a regional DSL), or an internal dialect of a mainstream language with heavy custom conventions (a company's own COBOL copybook style, a DSL built on top of Python). They've noticed the assistant keeps suggesting syntax or idioms that don't exist in their language, or defaulting to patterns borrowed from Python/JavaScript/Java. They want a persistent, reusable fix — not a one-off correction they retype every session — and they have (or can get) a real sample of code and documentation in that language to learn from.

Do not use this for mainstream languages (Python, JavaScript, TypeScript, Java, Go, Rust, C#) where assistants are already strong — there's no gap to close. Do not use this if the user has fewer than roughly 5 representative code files/snippets available; say so and ask for more before generating a pack (see Guardrails).

## Inputs
**Data source**: Connected — the GitHub API (mature, widely used; accessible via `gh` CLI or the GitHub web UI) to pull a target repository's documentation and code as the corpus. Manual paste is the fallback for codebases not hosted on GitHub — most commonly internal/proprietary legacy systems (e.g., an internal COBOL mainframe codebase) that can never be pulled via API.

Specifically, gather:
1. **Language/dialect name** — e.g. "Pharo (Smalltalk)", "COBOL (IBM Enterprise COBOL, this company's copybook conventions)", "a regional DSL built on X".
2. **Corpus** — either:
   - A GitHub repo URL/owner-repo (Connected path) — fetch representative source files and any docs/README/style-guide files from it, or
   - Pasted code (Manual path) — at least 5-15 real files or substantial snippets, ideally from the actual codebase the user will work in, not textbook examples.
3. **Style guide or documentation**, if one exists (pasted or linked) — language reference, internal coding standards, or a README describing conventions.
4. *(Optional)* The specific AI assistant/tool this pack will be loaded into (Claude Code CLAUDE.md, a Claude Code skill file, a system prompt for another tool) — affects only the final formatting wrapper, not the content.

If the corpus has fewer than ~5 representative files/snippets and no style guide, say so explicitly and ask for more before proceeding. If the user confirms that's genuinely all they have or can share (common for proprietary/legacy systems with strict data policies — e.g. a bank's internal COBOL that can't be pasted further), proceed with a best-effort pack but set confidence to Low and flag the thinness prominently in both the Scope and Gaps sections — never refuse outright when more material simply isn't obtainable, but never present a thin-corpus pack as if it were well-grounded either.

## Procedure
1. **Confirm scope.** State the single language/dialect this pack covers. If the user describes multiple languages or dialects, ask them to pick one per pack — never blend two languages into one pack.
2. **Ingest the corpus.** For the Connected path, pull the repo's source files (prioritize files that look representative: core modules, not generated/vendored code) and any docs/README/CONTRIBUTING/style-guide files. For the Manual path, work only from what was pasted. Note explicitly which path was used and how much material was available.
3. **Extract the idiom & pattern catalogue.** Read across the corpus for recurring, language-specific patterns: naming conventions, error-handling idiom, module/include/import patterns, common control-flow shapes, and anything that looks deliberately conventional rather than incidental. List each as a short rule with one real example pulled from the corpus (quoted, not paraphrased into a different language).
4. **Probe for AI-assistant failure modes.** For 3-5 representative snippets from the corpus, reason through what a generic AI coding assistant (trained mostly on Python/JavaScript/Java) would most likely suggest in that spot, based on well-known cross-language failure patterns (assuming a construct that doesn't exist in this language, e.g. list comprehensions in a language without them; assuming garbage collection or exceptions where the language uses manual memory or return-code error handling; defaulting to camelCase/snake_case against the corpus's actual convention; inventing a standard-library function that doesn't exist). Compare that likely-wrong suggestion against the real idiom from the corpus and write up the mismatch as a named failure mode with a concrete "assistant might suggest X, but this language/codebase actually does Y" pair. Never invent a failure mode you can't ground in an actual contrast with corpus material — if the corpus doesn't give enough signal for a given risk area, state that it's untested rather than guessing.
5. **Draft the condensed reference card.** A short syntax/structure cheat sheet: how functions/procedures are declared, how error handling works, how modules/includes work, how comments/types are written, and any script/encoding quirks (e.g. fixed-column formatting in COBOL, Tonel file format in Pharo). Keep this to what's directly observable in the corpus or stated in the provided docs — flag anything taken from general knowledge about the language rather than the corpus itself as "general knowledge, not corpus-verified."
6. **Extract the test-harness pattern**, if the corpus includes tests: how a test file is structured, naming convention for test cases, and one trimmed real example. If no tests are present in the corpus, say so and omit this section rather than inventing a plausible-looking one.
7. **Assemble the pack** into the Output format below, and note (a) which path was used (Connected/Manual), (b) corpus size, and (c) a confidence flag (High if the corpus had 15+ files/docs and tests; Low if it was closer to the 5-file minimum or lacked a style guide).

## Output format
One markdown document, ready to paste into a `CLAUDE.md`/`AGENTS.md` file or save as a Claude Code project skill, with these sections in order:
1. **Scope** — language/dialect name, corpus source (repo URL or "manual paste"), corpus size, confidence flag.
2. **Idiom & Pattern Catalogue** — bulleted rules, each with one real quoted example from the corpus.
3. **Known AI-Assistant Failure Modes** — a table or list of "assistant might suggest X → this language/codebase actually does Y" pairs, each tied to a real corpus contrast.
4. **Reference Card** — the condensed syntax/structure cheat sheet, with general-knowledge items explicitly flagged as such.
5. **Test Harness Pattern** — the real example and structure notes, or "No tests found in corpus" if absent.
6. **Gaps & Next Review** — what the corpus didn't cover, and a suggestion for what additional code/docs would most improve the pack next time.

## Guardrails
- Never fabricate a syntax rule, standard-library function, or idiom that isn't grounded in the provided corpus or explicitly flagged as general knowledge not verified against this corpus.
- Never claim this pack has been measured to improve suggestion quality — generating the pack is this skill's whole job; verifying the before/after lift is a separate benchmarking step (see the parent idea's MVP) that this skill does not perform or claim to have performed.
- Never pull a private/proprietary repository via the GitHub API without the user having already granted access through their own authenticated session — and never scrape or guess at proprietary legacy code (e.g. internal COBOL) instead of asking for a manual paste.
- Never blend two languages or two unrelated dialects into a single pack in one run — scope is one pack per language/dialect.
- Never proceed silently with a corpus under ~5 representative files/snippets and no style guide — always flag the thinness and ask whether more is available first. If the user confirms more genuinely isn't obtainable, proceed but mark confidence Low and say so plainly in the output rather than refusing or padding with generic advice.
- Never include large verbatim chunks of proprietary source code in the final pack output beyond short illustrative snippets (a few lines) — the pack is meant to be the abstracted idiom/pattern summary, not a redistribution of the source corpus, especially for proprietary legacy systems.
