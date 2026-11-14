# Low-Resource Language Coding Context Pack

A copy-paste prompt template for generating a reusable "context pack" that makes AI coding assistants noticeably less bad at a low-resource or niche programming language — COBOL, Fortran, Pharo, a regional DSL, or a company's own heavily-customized dialect of a mainstream language. It works in any chat tool: ChatGPT, Claude, Gemini, Copilot Chat, etc. No installation required.

## Why this exists

Mainstream AI coding assistants are strong on Python, JavaScript, Java, and similar high-resource languages, and meaningfully weaker on niche, legacy, or regional languages that make up a small fraction of their training data. The usual workaround — typing corrective examples into the chat every session, from memory — doesn't persist and doesn't transfer to a teammate. This prompt instead produces a single reusable document: an idiom catalogue, a list of specific mistakes the assistant is likely to make in this language, a condensed syntax reference, and a test-pattern example — built from a real sample of the target codebase. Save that document once, drop it at the top of future chats (or into a `CLAUDE.md`/system prompt), and every future session starts already knowing this language's quirks.

## When to use this

- You're about to do real work in a language or dialect that AI assistants keep getting wrong (suggesting syntax that doesn't exist, defaulting to Python/JavaScript-style patterns, inventing library functions).
- You're onboarding a teammate onto a legacy codebase (COBOL, Fortran, an old mainframe DSL) and want to hand them something more useful than "just get used to the quirks."
- You maintain an internal DSL or a heavily customized dialect of a mainstream language and the assistant keeps suggesting idioms from the "vanilla" version of that language instead of your actual conventions.

Skip this for mainstream languages (Python, JavaScript, TypeScript, Java, Go, Rust, C#) — assistants are already strong there, so there's no real gap to close.

## What you need to provide

**Data source: you provide it directly (manual).** This prompt doesn't connect to anything on its own — you paste or link the material yourself. Specifically:

1. **The language or dialect name** — be specific (e.g. "Pharo/Smalltalk," "IBM Enterprise COBOL with our team's copybook conventions," "our internal DSL built on top of Python").
2. **A real code sample** — at least 5-15 actual files or substantial snippets from the real codebase you'll be working in (not textbook examples). If the code lives in a public GitHub repo, you can paste the repo URL and ask the assistant to fetch representative files from it if your tool supports browsing/fetching URLs; otherwise, paste the code directly.
3. **Any style guide or documentation** you have — a README, internal coding standard, or language reference. Paste it or summarize its key points if it's long.
4. *(Optional)* Where you plan to use the finished pack — a `CLAUDE.md` file, a system prompt, or just as a reference doc you re-paste each session.

If you have fewer than about 5 real files/snippets and no style guide, gather more before running this — a pack built on too little material just repeats generic advice that doesn't actually help.

## The prompt

Paste this into your AI tool, filling in the bracketed parts:

```
I need you to build a "context pack" that will make you (and future AI sessions) noticeably better at working in [LANGUAGE/DIALECT NAME]. Here is a real sample of the codebase and any documentation I have:

[PASTE CODE SAMPLES AND/OR STYLE GUIDE / DOCS HERE, OR GIVE THE REPO URL]

Please produce a single markdown document with exactly these sections:

1. Scope — state the language/dialect, where the corpus came from (repo URL or "manual paste"), roughly how much material was provided, and a confidence flag (High if you had 15+ files plus docs and tests, Low if closer to the 5-file minimum or missing a style guide).

2. Idiom & Pattern Catalogue — the recurring, language-specific patterns you can actually see in the material I gave you: naming conventions, error-handling idiom, module/import patterns, control-flow shapes. For each one, quote one real example from what I pasted — don't paraphrase it into a different language's syntax.

3. Known AI-Assistant Failure Modes — think through what a generic AI coding assistant (trained mostly on Python/JavaScript/Java) would probably get wrong in 3-5 specific spots from my sample: assuming a construct that doesn't exist in this language, assuming garbage collection or exceptions where this language actually uses manual memory or return-code error handling, defaulting to the wrong naming convention, or inventing a standard-library function that doesn't exist. For each, write it as "an assistant might suggest X, but this language/codebase actually does Y," grounded in a real contrast from my material. If you don't have enough signal in what I gave you to identify a real failure mode in some area, say that area is untested rather than guessing.

4. Reference Card — a condensed syntax/structure cheat sheet (how functions are declared, how errors are handled, how modules/includes work, any formatting quirks like fixed-column layout or a special file format) based on what's in my material. If you add anything from general knowledge about this language rather than what I gave you, label it clearly as "general knowledge, not verified against this sample."

5. Test Harness Pattern — if my sample included any tests, show the real structure and one trimmed example. If it didn't, say "No tests found in the provided sample" instead of making one up.

6. Gaps & Next Review — what my sample didn't cover, and what additional code or docs would most improve this pack if I come back with more.

Rules for you to follow:
- Don't invent syntax rules, library functions, or idioms that aren't grounded in what I gave you or explicitly flagged as general knowledge.
- Don't claim this pack has been tested to actually improve suggestion quality — you're only building the reference document, not proving it works. That's a separate step I'd do myself by comparing suggestions with and without this pack loaded.
- Don't include large verbatim chunks of my code in the final pack beyond short illustrative snippets (a few lines) — I need the abstracted patterns, not a copy of my source.
- If what I gave you is too thin (fewer than ~5 real files/snippets and no style guide) to find real patterns, tell me that directly and ask if I have more. If I confirm this is genuinely all I can share (for example, a proprietary system I'm not allowed to paste more of), go ahead with a best-effort pack but mark confidence as Low and say so plainly — don't refuse outright, and don't pad it with generic advice to make it look more complete than it is.
```

## What you'll get back

A single markdown document in the six sections above, ready to save as a file and either paste at the start of future chat sessions, drop into a `CLAUDE.md`/`AGENTS.md` file, or save as a Claude Code project skill. It is not a benchmark result and does not claim to have measured anything — it's the reusable reference material itself. If you want to verify it actually helps, the simplest test is: give the assistant the same real task in this language twice, once with the pack loaded and once without, and compare the suggestions against what you know is correct for your codebase.

## Guardrails to keep in mind

- This produces one pack per language/dialect per run — don't try to cover two unrelated languages in a single pass.
- Don't feed it proprietary source code you're not authorized to paste into a third-party AI tool; check your organization's policy on pasting internal/legacy code into external chat tools before using the Connected (public GitHub repo) path or pasting proprietary snippets.
- Treat the "Known AI-Assistant Failure Modes" section as a living document — re-run this with more code once you've worked in the language a while and noticed new mistakes the pack didn't predict.
