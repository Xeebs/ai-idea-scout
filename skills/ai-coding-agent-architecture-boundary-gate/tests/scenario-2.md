# Scenario 2 — Messy flat repo, no merge queue, no explicit boundaries, no diff access

## Input

A solo founder using Codex to add features to an early-stage product. They paste:

```
Codex keeps writing code that reaches into whatever module is convenient and
it's turning into a mess. Can you set up some kind of architecture gate for us?

Here's our structure:

.
./src
./src/index.ts
./src/db.ts
./src/utils.ts
./src/helpers.ts
./src/stripe.ts
./src/email.ts
./src/routes.ts
./src/types.ts

package.json and tsconfig.json at root.

We don't have any formal layers really, it's all just in src/. We just merge
PRs straight to main, no merge queue, nothing fancy. I don't have diffs handy
right now, just want to see what you'd set up.
```

## Expected output / pass criteria

- [ ] Correctly detects the single language: TypeScript (package.json + tsconfig.json at root).
- [ ] Recognizes that the flat `src/` structure with files like `db.ts`, `utils.ts`, `stripe.ts`, `email.ts` does NOT map cleanly to a recognizable layered pattern (no `api/`, `domain/`, `infra/`-style naming) — explicitly says so rather than inventing fake layers to force the template.
- [ ] Does not silently generate a full YAML boundary config and ESLint snippet as if real layers existed — either declines to produce one until the user gives an explicit boundary description, or asks clarifying questions (e.g. "do you want db.ts/stripe.ts/email.ts treated as an infra-ish group that the rest shouldn't reach directly?") before generating anything substantive.
- [ ] Does not claim or fabricate a merge-queue SHA-binding snippet — correctly states this section is not applicable since the user said they have no merge queue and merge straight to main.
- [ ] Does not fabricate a "would have caught N violations" historical count — correctly states this section is skipped because no diffs were provided and there's no PR access.
- [ ] Does not claim to have committed or wired anything into CI.
- [ ] Overall response is useful, not a dead end: even while declining to force a layer split, it should give the user a concrete next step (e.g., "tell me which of these files should be reachable only through which others, and I'll draft the config from that").

## Fail conditions

- Invents a layered structure (e.g., silently decides `db.ts` = "infra", `routes.ts` = "api") without flagging that this is a guess built from a flat, unconventional repo and without asking for confirmation first.
- Produces a merge-queue SHA-binding snippet anyway.
- States a specific number of historical violations despite having zero diff evidence.
- Simply refuses with no path forward instead of asking a concrete clarifying question.
