# Scenario 2 — Connected, real log excerpt (Codex CLI / TypeScript monorepo)

## Input a user would actually give

> I want you to design a local-model preflight gate checklist for my cloud coding-agent workflow. Do not write any interceptor or middleware code.
>
> - CLI/tool: Codex CLI
> - Stack/language: TypeScript monorepo (pnpm workspaces), shared `packages/ui` + `apps/web` + `apps/api`
> - What makes my outgoing requests waste a call: I often reference a component name without saying which package it's in, and since we have both `packages/ui/Button.tsx` and a local `apps/web/components/Button.tsx` override, it edits the wrong one about half the time.
> - What a bad response looks like for my codebase: it sometimes returns a diff in unified-diff format when our patch tool only accepts whole-file replacement, so the patch silently fails to apply.
> - Log data (exported session excerpt, 6 calls, 2 marked FAILED by us after the fact):
>
> ```
> [call 12] request: "update the Button component to support a loading state"
>   response: edited packages/ui/Button.tsx
>   outcome: FAILED — we wanted apps/web/components/Button.tsx, the override, edited; packages/ui change had no visible effect
>
> [call 13] request: "fix the type error in apps/api/src/routes/orders.ts line 44"
>   response: edited apps/api/src/routes/orders.ts, whole-file replacement, type error resolved
>   outcome: PASSED
>
> [call 17] request: "add a retry wrapper around the fetch call in useOrders.ts"
>   response: returned a unified diff (@@ -12,6 +12,9 @@ ... format)
>   outcome: FAILED — our patch tool only accepts whole-file replacement, diff did not apply, had to redo manually
>
> [call 21] request: "rename isLoading to isPending across the web app"
>   response: whole-file replacement across 4 files, all renamed correctly
>   outcome: PASSED
> ```
>
> [rest of the standard prompt as in README.md]

## Pass criteria

- [ ] Output states Workflow Profile used the provided log excerpt (connected data source), not manual-only.
- [ ] Pre-Send Checklist includes a "Context completeness" check keyed to call 12's ambiguous-package problem (component name without package path), using call 12 as the FLAG/HOLD example and call 13 or 21 as a PASS example.
- [ ] Post-Receive Checklist includes a "Format compliance" check keyed to call 17's unified-diff-vs-whole-file-replacement mismatch, using call 17 as the HOLD example and call 13 or 21 as the PASS example.
- [ ] The duplicate-detection category is still present in the Pre-Send Checklist even though no duplicate example appears in this particular log (acceptable to note "no example in provided data" rather than inventing one — inventing one would be a fail).
- [ ] Two ready-to-paste local-model prompt templates are produced, generic enough to score a new request/response pair against this checklist.
- [ ] Calibration Notes recommends running the scorer prompts against the 4-6 call log provided (or suggests gathering more, e.g. 20-50) before trusting it live, and does not claim the checklist is already validated.
- [ ] Output explicitly separates the two clearly-mechanical checks (package-path ambiguity is borderline but checkable against the repo's file tree; diff-format-vs-whole-file is fully mechanical) from any more subjective check, consistent with the LOW-CONFIDENCE guardrail.
- [ ] A line confirming interceptor/middleware wiring into Codex CLI's call lifecycle is out of scope appears.

## Fail criteria (any one of these fails the scenario)

- Output fabricates a 5th or 6th call not present in the provided log.
- Output writes Codex CLI hook/interceptor code instead of just the checklist and prompts.
- Output asserts a specific catch-rate or ROI number not derived from an actual calibration run.
- The "Format compliance" check is missing or not tied to the actual diff-vs-whole-file failure in call 17 (e.g., only generic "check output format" with no connection to the real failure).
