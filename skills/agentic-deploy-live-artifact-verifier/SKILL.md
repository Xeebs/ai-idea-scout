---
name: agentic-deploy-live-artifact-verifier
description: Reviews a pasted CI/CD pipeline configuration (GitHub Actions, GitLab CI, Harness, Azure DevOps YAML, etc.) and flags the specific anti-pattern where the pipeline reports "success" at the deploy-command-completed step instead of after an independent check that the live artifact actually reflects the change — with an exact insertion point for a verification gate. Use when someone is designing, reviewing, or auditing a CI/CD pipeline that an AI coding agent drives with minimal human review, especially after a "CI said it shipped but production didn't change" incident.
---

# Agentic Deploy Live-Artifact Verifier (Pipeline Review)

## When to use this
Reach for this when someone pastes a CI/CD pipeline/workflow definition and either (a) an AI coding agent authors, commits, and triggers deploys through this pipeline with little or no human review of each release, or (b) they've already hit a case where the pipeline reported a deploy as successful but the live site/service still served the old version. This is a **one-shot, static design review of a pipeline definition** — it reads the pasted config and reasons about what it proves, not what it's named. It does not run anything, does not call any live endpoint, and does not fix the pipeline for you. If the ask is "is my production site currently broken right now," that's a live incident check, not this skill — this skill only reviews whether the *pipeline's own design* would have caught that.

## Inputs
**Data source**: Manual — you paste the pipeline configuration file(s) (YAML, JSON, or equivalent: a GitHub Actions workflow, a GitLab `.gitlab-ci.yml`, a Harness pipeline spec, an Azure DevOps YAML pipeline, a Jenkinsfile, etc.) directly into the chat. There is no live connector in this skill. *(Note on the parent idea: the full idea this skill comes from is tagged Data Sources: Connected — a companion always-running project independently queries the CI/CD provider's live deploy-status API and fetches the production endpoint directly to verify artifacts in real time. That connected, always-on verifier is a separate, persistent build. This skill is the static, offline design-review half of the same idea: it works from a pasted config, not a live connection, because its job is reviewing pipeline *design* before a single deploy ever runs.)*

Before reviewing, collect:
1. **The full pipeline definition**, every stage from build through whatever currently counts as the success/notify step — a truncated snippet that's missing the deploy or post-deploy stage can't be reviewed; ask for the rest rather than guessing what's not shown.
2. **What the deployment target is** — a public web app/API behind a CDN or load balancer, a backend-only service with no public endpoint, a mobile build, etc. This determines whether a live-fetch check is even possible.
3. **How "success" is currently reported today** — a Slack/notification message, a status check on the PR, a dashboard flip to green — whichever signal a human or downstream agent would actually look at.
4. If available: **any prior incident** where this pipeline (or its predecessor) reported success without the live artifact actually changing. Optional, but sharpens the review — don't invent one if not given.

If item 1 is incomplete (e.g., only the build stage is pasted, with no deploy or later stages), say so explicitly and ask for the missing stage before producing a verdict — a partial pipeline cannot be scored as PASS or AT RISK, only as INSUFFICIENT INFO.

## Procedure
1. **Parse the pipeline into an ordered stage list** exactly as written (job/step names, what command or action each runs, and what each step's pass/fail condition is).
2. **Locate the current success checkpoint** — the exact step after which the pipeline (or a human/agent reading its output) would currently treat the release as done. Common checkpoints: the deploy/apply command exiting 0, an image push succeeding, a notification step firing.
3. **Scan every step after that checkpoint** for an independent live-artifact check. "Independent" means it does something with the live, deployed system itself — not a rerun of build/test logic, not a check of the deploy *tool's* own exit code. Check specifically for:
   - A step that fetches the live production URL/endpoint and compares a build-ID, content hash, version string, or commit SHA against the one just deployed.
   - A health-check step, and if present, whether it merely checks liveness (e.g., `curl .../health` expecting `200 OK`) versus asserting the *new* version is actually serving (e.g., the health response includes a build-ID/git-SHA/timestamp that's checked against the expected one).
   - An APM/observability query for a post-deploy error-rate or latency anomaly in a bounded window after the deploy.
4. **Classify the pipeline against this anti-pattern checklist** (a pipeline can match more than one):
   - **No post-deploy check at all** — success is declared at build/push/apply, full stop.
   - **Phantom-deploy health check** — a health/liveness check exists after deploy, but it only proves *something* is responding, not that the *new* artifact is what's responding (classic "old container still running, health check still returns 200" failure).
   - **Self-reported agent success** — the success signal is free-text output from an agent step ("Deployed successfully!") rather than a programmatic check of anything live.
   - **No cache/CDN awareness** — a live-fetch check exists but nothing accounts for edge-cache/CDN propagation lag, so transient mismatches would either be missed (check runs before propagation, passes falsely) or would hard-fail on normal lag.
5. **For every item flagged, cite the exact step name/line from the pasted config** it applies to — never describe an anti-pattern in the abstract if the pasted config doesn't actually exhibit it.
6. **For every item flagged, write the exact insertion point**: which existing step it goes after, what command/check it should run (fetch the live endpoint, compare against the deploy manifest's build-ID/hash; or add a version field to the existing health endpoint and assert it; or add a bounded post-deploy APM query), and a suggested grace period/retry count if CDN propagation is plausible for this target.
7. **If the deployment target is backend-only with no public endpoint** (per the user's answer to Inputs #2), say so explicitly: a direct live-fetch check isn't available, and suggest the closest substitute (an internal health/metadata endpoint if one exists, or a log-line/version-assertion check via the orchestrator) rather than inventing a fake external URL to check.
8. **If a prior incident was given (Inputs #4), explicitly cross-check it against the current pipeline as pasted**: state plainly whether the pipeline, as written today, would or would not have caught that specific incident, and tie that statement to the specific finding from step 4 that explains why. If no prior incident was given, skip this — never fabricate one to fill the section.
9. **Do not flag anything not evidenced in the pasted config.** If the pipeline already has an adequate independent check, say PASS and explain why it clears the bar — don't manufacture a finding to justify the review.

## Output format
A single Markdown report, in this order:
1. **Verdict** — one of `PASS` (independent live-artifact verification present and adequate), `AT RISK` (one or more anti-patterns found), or `INSUFFICIENT INFO` (pipeline definition incomplete).
2. **Stage Table** — columns: Step Name | What It Currently Proves | Anti-Pattern Matched (or "—") | Config Reference (step name/line).
3. **Findings** — one subsection per flagged anti-pattern: name, why it's risky (the concrete false-positive scenario it allows), and the exact insertion point (after which step, what to add, what it checks, suggested grace period if relevant).
4. **Prior Incident Cross-Check** — only if a prior incident was given; states explicitly whether the pipeline as pasted would or would not have caught it, tied to a specific finding above.
5. **Backend/No-Public-Endpoint Note** — only if applicable; states the limitation and the closest substitute check.
6. **If you do nothing else** — one sentence naming the single highest-leverage fix.

## Guardrails
- Never approve a step as sufficient verification just because of its name (a step called `verify-deploy` or `post-deploy-check` that only pings a generic liveness endpoint is not adequate — judge what it actually checks, not what it's labeled).
- Never recommend a hard-fail live-fetch check without naming a grace period or retry policy for CDN/edge-propagation lag — an instant hard-fail on normal propagation delay is itself a false positive this review should prevent, not cause.
- Never conflate a pre-deploy check (unit tests, build success, lint) with a post-deploy live-artifact check — they answer different questions; only the latter counts toward the verdict.
- Never invent specific line numbers, step names, or incident history not present in what was pasted — if the config is ambiguous or truncated, say so and ask for the missing stage rather than guessing.
- Never recommend one specific commercial vendor/SaaS product as the only fix — recommend the protocol-level check (HTTP fetch + hash/version compare, or APM query) so the fix is usable regardless of CI provider.
- If the target is backend-only with no public endpoint, never fabricate a URL to "check" — say the direct check isn't available and name the closest real substitute.
- This is a static review of pipeline design, not a live monitor — never imply the review itself detected a current production incident; it only judges whether the pipeline's design *would* catch one.
