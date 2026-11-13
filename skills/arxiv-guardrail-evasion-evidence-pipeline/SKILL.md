---
name: arxiv-guardrail-evasion-evidence-pipeline
description: Drafts a reviewable PR/issue entry for a curated guardrail-evasion or jailbreak benchmark/awareness repo from a pasted arXiv paper and the repo's existing entry format. Use when a maintainer or red-teamer has found a new evasion paper and needs it reformatted into their repo's style without inventing any data the paper doesn't support.
---

# Paper-to-Evidence Draft

## When to use this
A maintainer of a curated "awesome-agentic-ai-security"-style benchmark/awareness repo (or a red-team/trust-safety engineer tracking guardrail-evasion research for their team) has just found or been pointed to an arXiv paper describing a new jailbreak, prompt-injection, or guardrail-evasion technique, and wants it turned into a PR- or issue-ready entry matching their repo's existing format — instead of manually re-reading the paper and reformatting it by hand each time a new paper surfaces.

## Inputs
**Data source**: Manual — the user pastes (1) the arXiv paper's abstract and, if the abstract omits them, any additional paragraph(s) containing the reported bypass/success rate or affected-systems list, and (2) one existing entry copied verbatim from their target repo, to anchor the exact field structure. This skill does not call the arXiv API or the GitHub API itself — it is the lightweight, paste-based companion to a separate, fully automated watcher-and-PR-bot project idea (which *is* Connected: arXiv's public API plus a GitHub API token with PR-create permission) that continuously scans arXiv and opens PRs on its own. Use this skill today, by hand, per paper; the automated version is a larger build for later.

Required from the user, every time:
1. The arXiv paper link or ID (even if full text isn't pasted, this is needed for citation).
2. The abstract text, pasted in full.
3. Optional but recommended: the specific paragraph reporting the bypass rate / success rate / affected models, if that detail isn't in the abstract (it usually isn't — abstracts rarely carry the number).
4. One full example entry pasted verbatim from the target repo, showing its exact field names, order, and markdown style.

If (4) is missing, ask for it before drafting anything — do not guess a generic "awesome-list" format.

## Procedure
1. From the pasted abstract/text, extract: paper title, arXiv ID, the specific evasion/bypass technique it names, the target system(s)/model(s) tested, and any reported quantitative bypass or success rate.
2. If a bypass rate or affected-systems list is not present in what was pasted, do not infer or estimate one. Mark it `Not reported in provided text` and ask the user to paste the relevant Results paragraph if they want it filled in.
3. Reverse-engineer the target repo's entry structure from the pasted example: exact field names, their order, bullet vs. table formatting, citation/link style, and typical entry length.
4. Draft the new entry matching that structure field-for-field, populating only facts traceable to the pasted source text.
5. Wrap the entry in a PR/issue body template: a one-paragraph plain-language technique summary, the entry block itself, a source citation with the arXiv link, and an explicit verification caveat line (e.g., "Source: arXiv:<id> — maintainer should verify the reported bypass rate against the paper before merging").
6. List every field the target format requires that the pasted source material could not support, under a separate "Needs maintainer input" section — never fill these with a plausible-sounding guess.
7. Return the draft as a single copy-pasteable block plus a one-line suggested PR title.

## Output format
```
### Suggested PR title
<one line>

### New entry (target repo format)
<entry formatted exactly per the pasted example's structure>

### PR/issue body
<technique summary paragraph>

<entry block repeated inside the body, as the proposed addition>

Source: arXiv:<id> (<link>)
Verification note: this is a proposed evidence addition only — please verify the reported figures against the paper before merging.

### Needs maintainer input
- <field>: not reported in provided text — paste the relevant paragraph if you want this filled in.
- <any other unsupported field>
```

## Guardrails
- Never invent a bypass rate, success percentage, CVE/CWE identifier, model name, or any other numeric or factual claim that is not present in the text the user pasted. Mark it as missing instead.
- Never open the PR or issue on GitHub directly — this skill only produces draft text; the user or maintainer submits it themselves. (It has no GitHub or arXiv API access and should not claim to.)
- Never fabricate or assume a target repo's entry format if no example entry was pasted — ask for one first.
- Always include the verification-caveat line in the output; omitting it defeats the entire "evidence changes only, maintainer verifies" pattern this skill exists to support.
- If the pasted abstract describes a *defense* or *detection* method rather than an evasion/bypass technique, say so plainly and ask the user to confirm this is still the paper they want drafted — don't silently force-fit it into an "evasion entry" format.
