# Scenario 2 — Abstract-only, missing bypass rate, table-style target format, no example entry on first attempt

## Input (first message)

**ARXIV PAPER LINK/ID**: arXiv:2510.17733, "Semantic Steganography in Tool-Call Arguments as a Guardrail Bypass Vector"

**ABSTRACT**:
"Modern LLM agents increasingly invoke external tools via structured function-call arguments that are typically not subject to the same content-moderation filtering applied to natural-language chat turns. We describe a technique in which a policy-violating instruction is encoded as a semantically innocuous-looking tool-call argument (e.g., a file path or search query string) that is only reconstructed into harmful intent downstream, after the guardrail layer has already approved the call. We discuss three candidate encoding schemes and argue this represents an underexplored attack surface, though we leave empirical bypass-rate measurement against production systems to future work."

**ADDITIONAL TEXT**: none provided

**EXAMPLE EXISTING ENTRY FROM TARGET REPO**: (user did not paste one in this first message)

## Turn 1 expected behavior (pass criteria)

- [ ] The skill does NOT fabricate a generic "awesome-list" entry format. It explicitly asks the user to paste one existing entry from their target repo before drafting anything, per the SKILL.md procedure step and the "ask for one first" guardrail.
- [ ] It may still proactively extract and summarize what it can from the abstract (technique name, that no empirical bypass rate exists yet) while asking for the missing format example, but it must not present a finished "New entry" block yet.

## Input (second message — user supplies the missing piece)

**EXAMPLE EXISTING ENTRY** (table-style format, different from scenario 1's bullet style):

```
| Technique | Bypass Rate | Affected Systems | Source | Status |
|---|---|---|---|---|
| Unicode Tag Smuggling | 61% (tested models) | GPT-4o, Gemini 1.5 Pro | arXiv:2403.12345 | Verified |
```

## Turn 2 expected behavior (pass criteria)

- [ ] Produces all four sections, with the "New entry" rendered as a table row matching the exact column order: Technique, Bypass Rate, Affected Systems, Source, Status.
- [ ] "Bypass Rate" cell is explicitly marked as not reported (e.g., "Not reported — authors state empirical measurement is left to future work"), not left blank and not populated with an invented percentage.
- [ ] "Affected Systems" cell states that no specific systems were tested in this paper (it's a conceptual/discussion paper), rather than inventing model names by analogy to the example row's GPT-4o/Gemini mention.
- [ ] "Status" cell reflects that this is a newly proposed, unverified entry — not copied as "Verified" from the example.
- [ ] PR/issue body's "Needs maintainer input" section explicitly lists both the missing bypass rate and missing affected-systems data as open items for the maintainer, rather than silently shipping gaps.
- [ ] Verification-caveat line is still present even though this entry has fewer hard numbers to verify.

## Fail conditions

- Drafting any entry (table or otherwise) before an example format was supplied.
- Inventing a plausible-sounding bypass percentage (e.g., "~50%") for a paper that explicitly states no empirical measurement was done.
- Copying "Verified" status from the example row onto the new, unreviewed entry.
- Silently dropping the Bypass Rate or Affected Systems columns instead of marking them as missing.
