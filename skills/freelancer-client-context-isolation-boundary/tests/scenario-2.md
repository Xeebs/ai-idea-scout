# Scenario 2: Six-person agency, Cursor, shared memory/MCP server across clients

## Input (as the user would paste it)

> We're a 6-person dev agency doing contract work for 7 active clients at once, mostly web/mobile builds. Everyone on the team uses Cursor. A few months ago we set up a shared internal MCP server that indexes all of our client repos into one vector store, so when someone asks Cursor "have we solved a problem like this before," it can search across every client's codebase for similar patterns and surface snippets — including the actual code, not just descriptions. It's been great for onboarding new team members quickly.
>
> We also have one shared `.cursorrules` file that every team member uses regardless of which client repo they have open — it has our team's commit message format, our preferred testing library, and (we just realized while answering this) a paragraph describing "Client Meridian's preferred auth flow (OAuth with PKCE, custom token refresh logic)" that someone wrote in there six weeks ago to remind the team how Meridian likes things done.
>
> Client repos: Meridian (fintech, strict NDA, remote `git@github.com:meridian-fin/app.git`), Darkwood (gaming studio, remote `git@github.com:darkwood-games/client.git`), five others we manage via a shared company GitHub org under per-client private repos, all named `<clientname>-prod`.
>
> We don't currently track which team member works on which client — anyone can pick up any ticket from our shared Linear board, which is connected to Cursor via an integration so the AI can read ticket descriptions across all clients when someone asks "what's in my queue."
>
> Nothing has gone wrong yet as far as we know, but we got nervous when we found the Meridian paragraph in the shared rules file.

## Pass criteria

- [ ] Identifies the shared vector-store/MCP server indexing all client repos together as a Critical leak point — names the mechanism precisely (semantic search can surface one client's actual code as a "similar pattern" answer while a session is rooted in a different client's repo), not just "shared storage is risky."
- [ ] Identifies the shared `.cursorrules` file's Meridian paragraph as a Critical, *confirmed* leak point (not theoretical — the user already found it) and flags Meridian's strict NDA as elevating severity.
- [ ] Identifies the shared Linear integration (readable across all clients regardless of which repo is open) as a leak point distinct from the two above — ticket descriptions can contain client-specific business/product detail and are reachable cross-client.
- [ ] Identifies the lack of per-team-member client assignment ("anyone can pick up any ticket from any client") as a structural risk factor that compounds the other leak points, even though it isn't itself a file or tool config.
- [ ] Separates GLOBAL content (team's commit message format, testing library preference) from the CLIENT-SCOPED Meridian paragraph within the same `.cursorrules` file — doesn't treat the whole file as uniformly safe or uniformly unsafe.
- [ ] Produces a client tagging convention covering at least Meridian and Darkwood by name, and acknowledges the other five by their `<clientname>-prod` naming pattern without requiring the user to re-paste all seven individually.
- [ ] Explicitly notes that the MCP/vector-store leak point is the kind of structural, per-client-scoping problem this one-time audit can flag but cannot itself fix — fixing retrieval-time scoping requires engineering work (or the separate enforcement mechanism), not just a checklist.
- [ ] Residual Risk section acknowledges that with 6 people and no per-client assignment, a checklist-based policy is weaker here than for a solo freelancer, and says so rather than presenting the same confidence level as scenario 1.

## Fail conditions

- Treats the shared `.cursorrules` file as entirely safe or entirely unsafe instead of separating the GLOBAL and CLIENT-SCOPED content within it.
- Misses the Linear integration as a distinct leak point from the MCP server.
- Implies the audit/checklist alone fixes the vector-store retrieval problem, rather than flagging it as needing real engineering work.
- Fails to note that team size and unassigned ticket-picking materially weaken how much a human-followed checklist can actually achieve here.
