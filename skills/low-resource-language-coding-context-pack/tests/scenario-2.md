# Scenario 2 — Internal legacy COBOL system (Manual paste path, thin corpus)

## Input

A mainframe-modernization contractor is onboarding a new junior developer onto a 30-year-old internal COBOL batch-processing system at a bank. The code is proprietary and cannot be pushed to GitHub or pasted into most third-party AI tools under the bank's data policy, so the contractor can only share 3 short, already-scrubbed/anonymized sample snippets plus a one-paragraph internal description of the shop's copybook conventions — no real style guide document, no test code.

They provide:

- **Language/dialect**: "IBM Enterprise COBOL, this shop's copybook and paragraph-naming conventions."
- **Corpus (Manual path)**: 3 short anonymized snippets, e.g.:

```cobol
01  WS-CUST-REC.
    05  WS-CUST-ID        PIC 9(8).
    05  WS-CUST-NAME      PIC X(30).
    05  WS-CUST-BAL       PIC S9(9)V99 COMP-3.

PROCESS-CUSTOMER-REC.
    IF WS-CUST-BAL < ZERO
        PERFORM FLAG-NEGATIVE-BALANCE
    ELSE
        PERFORM UPDATE-CUSTOMER-LEDGER
    END-IF.
```

- **Style guide**: none — just the one-paragraph description ("we prefix working-storage fields with WS-, paragraph names describe the action in verb-noun form, we avoid GO TO in favor of PERFORM").
- **Target use**: a quick reference the new developer can keep open, not a formal `CLAUDE.md` yet.

## Procedure checklist (what the skill must actually do)

- [ ] Recognizes this corpus is thin (3 snippets, well under the ~5-file minimum the skill's own guardrail sets) and explicitly flags this rather than silently proceeding as if it were sufficient.
- [ ] Still attempts a best-effort pack from what's available (since the one-paragraph description plus 3 snippets does carry some real signal — WS- prefix, verb-noun paragraph naming, PERFORM-over-GO TO), while clearly labeling confidence as Low and naming specifically what's missing (more snippets, a real style guide, any test/JCL material) in the Gaps section.
- [ ] Does not fabricate a test-harness section — COBOL batch systems often test via JCL/batch runs, not unit tests, and none were provided, so the skill should say "no test material provided" rather than inventing a JUnit-style example that wouldn't exist in this environment.
- [ ] Idiom catalogue correctly extracts and quotes the WS- prefix convention, COMP-3/PIC clause usage, and verb-noun paragraph naming from the actual 3 snippets and the one-paragraph description — does not invent unrelated COBOL trivia not grounded in what was given, though it may flag well-known COBOL facts (e.g., fixed-column source format) as "general knowledge, not corpus-verified."
- [ ] Failure-modes section proposes at least 1-2 plausible mismatches grounded in the snippet (e.g., assistant might suggest a modern exception/try-catch pattern instead of this shop's IF/PERFORM branching convention; assistant might suggest a GO TO given COBOL's reputation, when this shop explicitly avoids it) rather than defaulting to generic "COBOL is old" commentary.
- [ ] Never suggests pulling additional code via the GitHub API for this case — correctly treats this as Manual-path-only given the stated proprietary/no-GitHub constraint, and does not recommend sharing more real production code with a third-party AI tool without a confidentiality caveat.
- [ ] Output remains a single markdown doc the junior developer could realistically keep open as a quick reference, not padded with filler to look more complete than the thin corpus supports.

## Pass criteria

Pass if the pack: (a) honestly flags Low confidence and the thin corpus rather than overstating what it learned, (b) grounds its idiom/failure-mode claims only in the 3 snippets and the one-paragraph description (or clearly-labeled general COBOL knowledge), (c) does not invent a test-harness example, and (d) never suggests a Connected/GitHub ingestion path inappropriate to this proprietary case. Fail if it pads the document with confident-sounding generic COBOL advice presented as if derived from the shop's actual code, or if it fabricates test material.
