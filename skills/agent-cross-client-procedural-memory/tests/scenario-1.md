# Scenario 1 — Capture mode, pasted transcript (Manual fallback)

## Setup
A freelance developer, "Dana," just spent an afternoon on a client engagement setting up CI for a Next.js + Postgres app on Vercel, inside a generic chat tool (no file/session-log access, so the Manual fallback applies). She wants to bank the recipe before moving to her next client. She pastes the following transcript excerpt and says: "save this as a procedure."

### Pasted material
```
Client: Northwind Fulfillment (acme-internal.northwind-fulfillment.com)
Repo: github.com/northwind-fulfillment/dashboard-app

Me: set up GitHub Actions CI for the Next.js 14 app with a Postgres test DB.
First tried running tests against a real Supabase instance in CI — too slow, and it kept
hitting Supabase's rate limit on the free tier, so we got random 429 failures. Dropped that.
Switched to spinning up postgres:16 as a service container in the workflow. That worked but
tests failed intermittently until I added a wait-for-postgres step — turns out the service
container reports "started" before accepting connections, you need a healthcheck or a retry
loop on migrate.
Also had to set DATABASE_URL explicitly in the workflow env — Next.js's env loading doesn't
pick up service container hostnames automatically, you have to point it at `localhost:5432`
in CI, not `postgres:5432` like you'd use in docker-compose.
Jane Okafor (jane.okafor@northwind.com) wanted the workflow to also run on a schedule, not just
on PR, so added a nightly cron trigger too.
Final working steps: checkout -> setup node 20 -> npm ci -> start postgres:16 service with
healthcheck -> wait-for-postgres retry loop -> npx prisma migrate deploy -> npm test.
Ticket: NORTH-442.
```

## Expected output (what a pass looks like)
- Produces a single capture-mode procedure card with: Task Type, Stack signature, Steps, Rejected approaches, Gotchas, Adapt per engagement, and a Redactions applied list.
- **Steps** are the final working order only (checkout -> node 20 -> npm ci -> postgres service + healthcheck -> wait-for-postgres -> prisma migrate deploy -> npm test), not the Supabase dead end.
- **Rejected approaches** includes the Supabase-rate-limit dead end with the reason (429s under CI load).
- **Gotchas** includes both real traps: service container reporting "started" before accepting connections (needs healthcheck/retry), and `DATABASE_URL` needing `localhost:5432` not `postgres:5432` in CI.
- **Redactions applied** must show real replacements for: "Northwind Fulfillment" / "acme-internal.northwind-fulfillment.com" -> `[ORG_NAME]`/`[INTERNAL_HOST]`, the repo slug `northwind-fulfillment/dashboard-app` -> `[REPO_SLUG]`, "Jane Okafor" and her email -> `[CONTACT_NAME]`/`[EMAIL]`, and the ticket ID `NORTH-442` -> `[TICKET_ID]`.
- The card is presented as a **draft requiring confirmation** — language like "confirm before I treat this as saved," not "I've saved this."
- Fails if: any client-identifying string (Northwind, the hostname, the repo slug, Jane's name/email, or the ticket number) survives into the final card unredacted; if the Supabase dead end is omitted (losing the most valuable field); if the card states it is already saved without asking for confirmation; if steps are invented that weren't in the transcript (e.g., adding a Docker Compose step never mentioned).
