# MCP Tool Semantic Drift Detector

Paste a before/after pair of MCP server tool-list snapshots into any AI chat tool and get back a classified compatibility report that catches the breaking changes a plain JSON-schema diff misses — reworded tool descriptions, narrowed enums, changed units, altered pagination — before you accept a server upgrade.

## Why this exists

An MCP (Model Context Protocol) server can change a tool's real behavior without changing its JSON schema at all: it can reword the description in a way that makes an agent pick a different tool, narrow an enum to drop a value your code still sends, switch a numeric field from kilobytes to megabytes, or start paginating results it used to return in full. None of that shows up in a structural schema diff. It shows up as your integration silently returning wrong answers after an upgrade you thought was safe. Existing schema-diff tools (several young, single-digit-star GitHub projects and a handful of thin skill-marketplace listings as of late 2026) catch the structural half of this. None of them reason about whether a description rewording would actually change which tool an agent picks, or cross-check a detected change against how *you* specifically call the tool — they report every schema delta with the same weight, leaving you to figure out which ones actually matter to your code.

This is the one-shot, no-infrastructure version of that check: paste two snapshots, describe how you call the affected tools, get back a report that tells you exactly what will break, what might break, and what's genuinely fine — with the specific mechanism named for every line.

This is a manual, paste-based check. It does not connect to anything automatically — you provide both snapshots and, ideally, a short description of your own calling pattern. There's no API key, no connector, nothing to configure.

## When to use it

- You're about to bump the version of an MCP server dependency (yours or a third party's) and want to know if it's safe before you deploy.
- You got a `list_changed` notification from a server you're connected to and want to assess the new tool catalog before accepting it.
- You're doing a one-time compatibility audit of a server you depend on in production, without setting up continuous CI monitoring.

Not for: ongoing, scheduled monitoring of a live server. That needs a persistent pipeline (a stored baseline, scheduled re-scans, and ideally live behavioral replay against the real server) — this is a single manual check against two static snapshots you already have in hand.

## What to hand over

1. **Baseline snapshot** — the full JSON output of the MCP server's `list_tools` call from the version you're running today (the array of tool objects, each with `name`, `description`, and `inputSchema`).
2. **Current snapshot** — the same JSON shape, captured from the version you're about to adopt.
3. **(Strongly recommended) Your calling pattern** — for each tool you actually use: which parameters you set, which specific enum values you pass, which fields of the response your code reads, and anything you assume about pagination, units, or error handling. A code snippet of your actual call works as well as a plain-English description. One or two example request/response pairs you currently rely on make the report sharper.

Without #3, the report still runs, but every change that *could* plausibly matter gets classified WARN at minimum, never SAFE, because there's no way to confirm it's safe without knowing what you actually depend on — the report will say this explicitly rather than guessing on your behalf.

## The procedure (what the AI should do with your paste)

1. Parse both snapshots into a map of tool name to `{description, inputSchema}`. If either fails to parse as valid tool-list JSON, stop and ask for a corrected paste instead of guessing.
2. **Diff the tool set**: which tools are only in baseline (removed), only in current (added), in both (go to step 3). If an added tool's name or description strongly overlaps a removed one, flag it as a likely rename rather than an unrelated add-plus-remove.
3. **Structural schema diff** for every tool present in both: required fields added or removed, type changes, enum values added/removed/renamed, default-value changes, and changes nested inside object/array parameters.
4. **Description-meaning diff** for every tool present in both: read the old and new description for actual meaning, not just literal text equality. Specifically call out: a changed side-effect claim, a changed unit (e.g. KB vs MB), changed pagination language, changed error-handling language, and any rewording significant enough that an agent picking between tools by description alone could now choose differently for the same user intent.
5. **Cross-check every change against your stated calling pattern.** A change to a field, enum value, or behavior you don't touch is SAFE for you specifically even if it would be BREAKING in general for someone who does — say so explicitly both ways.
6. **Classify each individual change** (never bundle several changes into one verdict):
   - **BREAKING** — something your stated usage depends on was removed, renamed, narrowed to exclude a value you use, had an incompatible type change, or had a unit/pagination/error-shape change on something your code reads or assumes; or a new required field appeared with no default.
   - **WARN** — an optional field changed, an enum changed on a value you didn't confirm using, a description rewording that could plausibly shift behavior or tool selection but doesn't contradict your explicit call, or a pagination/unit/error-shape change on a tool you use but described too loosely to confirm impact. Exception: if the change is to a field that's `required` in both versions, there's no unconfirmed-usage escape hatch — every caller must supply it — so an incompatible meaning change there (a unit change, a semantics change) escalates straight to BREAKING even with no calling pattern given at all.
   - **SAFE** — purely additive changes, cosmetic description edits with no meaning change, or anything explicitly confirmed as untouched by your stated usage.
7. Write the report (format below). Anything too ambiguous to classify goes under "Needs more info" with the specific question that would resolve it — never guessed at.

## Output you should get back

```
## MCP Compatibility Report

**Summary**: N tools added, N removed, N changed, N unchanged. X BREAKING, Y WARN, Z SAFE.

| Tool | Change | Classification | Why |
|------|--------|-----------------|-----|
| search_docs | enum `format` narrowed: removed "xml" | BREAKING | your stated usage passes format="xml" |
| search_docs | description reworded: "returns all matches" -> "returns first 20, use `cursor`" | WARN | pagination behavior changed; not confirmed whether your code paginates |
| get_user | added optional field `locale` | SAFE | purely additive |

### Needs more info
- <tool>: <what's ambiguous> — <specific follow-up question>

### Recommendation
<Safe to upgrade. / Upgrade only after addressing: <unresolved BREAKING items>. / Do not upgrade without further testing — behavior that depends on live execution (pagination, errors, side effects) can't be confirmed from schema and description text alone.>
```

Every row must name the specific mechanism — never just a bare label with no reason.

## Guardrails (what this should never do)

- Never report a change that isn't literally present between the two pasted snapshots — no inferring "probably changed" without seeing it.
- Never mark something SAFE just because you didn't mention it — with no calling-pattern description, every plausibly-impactful change defaults to WARN, and the report says so explicitly. The one exception: an incompatible meaning change (unit, semantics) on a field that's `required` in both versions defaults straight to BREAKING, since every caller is affected whether or not you confirmed it.
- Never recommend "safe to upgrade" while any BREAKING item is still unresolved, regardless of how eager you are to ship the upgrade.
- Never claim to have verified real runtime behavior — pagination, actual error responses, actual side effects can only be confirmed by executing a live call. This skill reasons over snapshot text only; anything behavior-dependent gets flagged as "needs a live test," not verified.
- Never treat this as a substitute for continuous monitoring. If you want this running on a schedule or gated in CI, that requires a persistent baseline-and-scan pipeline (and ideally live behavioral replay against the real server) — a different, larger build than this one-shot paste check.
- If the two snapshots clearly aren't a real before/after pair of the same server (wrong files, unrelated servers), say so and ask for a corrected pair instead of producing a report full of noise.
