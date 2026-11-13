# Scenario 1: Solo freelancer, Claude Code, four concurrent clients

## Input (as the user would paste it)

> I'm a solo freelance backend developer. I currently have four active clients:
> - **Northwind** — a logistics startup, Postgres/Node backend, repo at `~/work/northwind` with git remote `git@github.com:northwind-inc/api.git`.
> - **Ferra** — a fintech client, Python/FastAPI, repo at `~/work/ferra-backend`, remote `git@github.com:ferra-labs/backend.git`. Under an NDA with explicit "no code or architecture details shared with third parties" language.
> - **Birchwood** — a small e-commerce client, repo at `~/work/birchwood-store`, no remote yet (local only).
> - **Glint** — a SaaS analytics client, repo at `~/work/glint-dash`, remote `git@github.com:glint-io/dashboard.git`.
>
> I use Claude Code for all four. I have one global `~/.claude/CLAUDE.md` file with my general preferences (I prefer TypeScript strict mode, I like small commits, I always write tests first). About two months ago I noticed that file also had a line in it saying "remember Ferra's rate-limiting middleware pattern uses a sliding window with Redis" — I think I added that myself after a session in Ferra's repo, not realizing it would apply globally. I removed that line once I spotted it, but I'm worried there's more like it I haven't noticed.
>
> I also keep a personal `~/dev/snippets` repo with reusable utility functions (retry wrappers, a logging helper, a date formatter) that I symlink into every client's `node_modules`-adjacent `utils/` folder for convenience. I wrote the retry wrapper originally while debugging a flaky API call in Northwind's codebase, but I've used it everywhere since.
>
> I usually have 2-3 terminal tabs open at once, one per active client, and I jump between them during the day without closing any.
>
> Nothing else has leaked that I know of, but the CLAUDE.md incident worried me.

## Pass criteria

- [ ] Correctly identifies the global `~/.claude/CLAUDE.md` file as a Critical (or at least high-severity) leak point, naming the specific mechanism (a client-specific fact — Ferra's Redis rate-limiting pattern — was absorbed into a file that applies to every session), and notes this is a *confirmed near-miss*, not theoretical.
- [ ] Flags the Ferra NDA explicitly as raising the stakes of that leak point (contractual exposure, not just internal mix-up) — demonstrates it used the NDA detail rather than ignoring it.
- [ ] Flags the `~/dev/snippets` retry wrapper as AMBIGUOUS (client-derived IP reused across clients), not silently classified as GLOBAL just because it "feels generic" — this is the specific trap the skill is designed to catch.
- [ ] Flags the practice of leaving 2-3 terminal tabs open across clients simultaneously as a leak point/risk factor (increases chance of cross-client context picking up facts), even though it's a human-behavior item, not a file.
- [ ] Produces a client tagging convention table mapping all four clients (Northwind, Ferra, Birchwood — noting it has no remote, Glint) to their directories/remotes.
- [ ] Produces a pre-session checklist that would have caught the CLAUDE.md incident (e.g., "before closing a session, scan global memory file diffs for client-specific content").
- [ ] States residual risk plainly — e.g., that this checklist depends on the user following it, and that symlinked snippets or terminal habits aren't something the policy document itself can block.
- [ ] Does not accept "nothing else has leaked that I know of" as proof the setup is otherwise safe — still surfaces the snippets repo and terminal-tab risk independent of self-report.

## Fail conditions

- Treats the retry wrapper as safely GLOBAL without flagging it as ambiguous.
- Omits the terminal-tab-switching behavior as a risk factor.
- Produces generic advice ("be more careful with your CLAUDE.md file") without naming the specific mechanism and severity.
- Fails to incorporate the NDA detail into severity ranking.
