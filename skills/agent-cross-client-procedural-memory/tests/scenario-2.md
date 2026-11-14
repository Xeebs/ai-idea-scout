# Scenario 2 — Match/Recall mode, pasted candidate cards

## Setup
Dana starts a new engagement for a different client. The new task: "Set up CI for a Remix + Postgres app, deployed on Fly.io, tests need a real Postgres instance." She has two previously saved, already-sanitized procedure cards (from past, unrelated clients) and pastes both, asking: "have I solved something like this before?"

### Candidate card A
```
# Procedure: CI pipeline setup for a Next.js + Postgres monorepo on Vercel
Stack signature: Next.js 14, Postgres 16, GitHub Actions, Prisma, Vercel

## Steps
1. checkout -> setup node 20 -> npm ci
2. start postgres:16 as a service container with a healthcheck
3. wait-for-postgres retry loop before running migrations
4. npx prisma migrate deploy -> npm test

## Rejected approaches
- Running tests against a hosted free-tier Postgres (Supabase) in CI — hit rate-limit 429s under load.

## Gotchas
- Service container reports "started" before accepting connections; healthcheck/retry is required.
- DATABASE_URL must point at localhost:5432 in CI, not the service hostname used in docker-compose.

## Adapt per engagement
- [REPO_SLUG], [ORG_NAME], specific Postgres/Prisma versions.
```

### Candidate card B
```
# Procedure: Migrating a legacy jQuery admin panel to React incrementally
Stack signature: jQuery, Webpack 4, React 18, no TypeScript

## Steps
1. Introduce React via a single mount point inside an existing jQuery page.
2. Port one widget at a time, leaving jQuery event handlers for unported widgets.
3. Remove jQuery dependency only after all widgets ported.

## Rejected approaches
- Full rewrite in one branch — abandoned after merge conflicts became unmanageable.

## Gotchas
- jQuery event delegation can fire twice if a React-ported widget still has a lingering jQuery handler.

## Adapt per engagement
- [REPO_SLUG], specific widget list, Webpack config specifics.
```

## Expected output (what a pass looks like)
- Classifies **Card A as PARTIAL MATCH** (same technique family — CI with a Postgres service container and a wait-for-ready step — but different framework/host: Remix/Fly.io vs. Next.js/Vercel, so real adaptation is flagged, not a clean copy).
- Classifies **Card B as NO MATCH** and excludes it from the ranked recommendation (different problem class entirely — a frontend migration, not a CI/Postgres setup).
- Surfaces Card A's steps, the Supabase rejected-approach note, and both gotchas (service-container readiness, DATABASE_URL hostname) as the starting recipe, with the adapt-per-engagement checklist re-flagged for the new client (Remix env var conventions, Fly.io-specific networking instead of Vercel).
- Includes an explicit "verify before using" line calling out that Fly.io's networking/hostname behavior for service-equivalent databases should be checked, since it differs from Vercel/GitHub Actions' service-container model and wasn't validated in the original card.
- Does not claim the recipe is guaranteed to work on Fly.io as-is.
- Fails if: Card B is presented as a match or included in the ranked list; Card A is presented as a CLEAN MATCH (it isn't — the host/framework differ); the output omits the reasoning sentence per candidate; the output asserts the recipe will work without a verification caveat.
