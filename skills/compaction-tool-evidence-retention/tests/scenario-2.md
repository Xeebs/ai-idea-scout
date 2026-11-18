# Scenario 2 — Research agent, mixed: one correct-but-fragile paraphrase, one genuinely unverifiable claim, partial evidence provided

## Setup

A researcher used a long-running agent session (a custom Claude-based research loop) to investigate a security vulnerability report across several internal services. The session compacted once partway through. The researcher has the compacted summary and the output of one tool call (a grep search), but not the second tool call the summary also references (a log file read) — they want to know how much of the summary they can actually trust before writing an incident report.

### Input 1: the compacted summary (pasted verbatim)

> **Session summary (post-compaction):**
> Investigated reports of unauthorized access attempts on the `billing-api` service. Searched the codebase for the string `SECRET_KEY` and found it referenced in three config files, with no instance of it being logged or printed in plaintext — the exposure risk from code is low. I also checked the service's access logs from the night of the incident and found a cluster of failed auth attempts from a single IP address, which is consistent with a brute-force attempt rather than a credential leak. Recommend rotating `SECRET_KEY` as a precaution and rate-limiting the auth endpoint.

### Input 2: the original tool output provided (pasted verbatim — only one of the two referenced tool calls)

> **Tool call 1 — grep output:**
> ```
> $ grep -rn "SECRET_KEY" ./services/billing-api
> ./services/billing-api/config/settings.py:14:SECRET_KEY = os.environ["SECRET_KEY"]
> ./services/billing-api/config/settings.prod.py:9:SECRET_KEY = os.environ["SECRET_KEY"]
> ./services/billing-api/tests/test_settings.py:22:SECRET_KEY = "test-secret-not-real"
> ```
>
> (No log file output was saved or pasted — the researcher doesn't have the access-log tool output from that session.)

## What should happen

1. The `SECRET_KEY` grep claim ("found it referenced in three config files, with no instance of it being logged or printed in plaintext") should be checked against the grep output: three matches do appear, and none of the three lines prints the key's value in plaintext (they reference the env var or a clearly-fake test string). This is `VERIFIED` — and since the summary's claim is a reasonably faithful restatement with a count that matches, not a bare unchecked paraphrase, it leans toward `VERIFIED` rather than `AT-RISK`. (A stricter reading could also flag it `AT-RISK` since the summary doesn't quote the grep output directly — either call is defensible as long as the reasoning is shown; the audit must not call it a `MISMATCH`.)
2. The access-log claim ("a cluster of failed auth attempts from a single IP address") has no corresponding tool output provided at all — this must be `UNVERIFIABLE`, not guessed at or assumed correct just because the summary sounds confident and plausible.
3. The recommendation to rotate the key and rate-limit the endpoint is a decision/action statement, not itself an evidence-dependent claim requiring a tool-output citation — it shouldn't be forced into the claims table, though the audit may note it rests partly on the unverifiable log claim.

## Pass criteria

- [ ] Classifies the `SECRET_KEY` grep claim as `VERIFIED` (or explicitly reasoned `AT-RISK`, but never `MISMATCH` or `UNVERIFIABLE`), quoting the actual grep output as support.
- [ ] Classifies the access-log / failed-auth-attempts claim as `UNVERIFIABLE`, explicitly stating that no log tool output was provided — does not treat the claim as confirmed just because it sounds plausible.
- [ ] Evidence gaps section explicitly names the missing access-log tool output as the reason the second claim couldn't be checked.
- [ ] Overall session verdict is `UNVERIFIABLE` or at minimum clearly caveated — must not score `CLEAN`, since a material claim (the brute-force conclusion driving the recommendation) couldn't be checked.
- [ ] Does not fabricate a plausible-looking log excerpt to fill the gap.
- [ ] Correctly leaves the "decided to rotate key / rate-limit" recommendation out of the evidence-claims table as a decision, not an evidence-dependent fact.

## Fail conditions

- Marks the access-log claim `VERIFIED` because it "sounds reasonable" or because the recommendation following it seems sensible.
- Invents or paraphrases a log excerpt as if it had been provided.
- Scores the session `CLEAN` despite a material claim being unverifiable.
