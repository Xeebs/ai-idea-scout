# Scenario 2 — Ambiguous and mixed-claim lines (edge cases)

## Input

```markdown
# CLAUDE.md

## API Rules
- The API currently uses v2 endpoints — v1 is deprecated, don't call it
- Don't touch the legacy auth module; migration to OAuth2 is in progress, ETA Q3 2026
- Always validate webhook signatures with the shared secret in `config/secrets.ts`
- We dropped support for IE11 last quarter, so no polyfills needed anymore

## Deploy
- Deploys go through `scripts/deploy.sh staging|prod` — never deploy manually
- Currently deploying twice a day while we stabilize the new pipeline

## Notes
- Remember we're a 4-person team right now, so keep PRs small
```

## Expected output criteria

- `"Always validate webhook signatures..."` and `"Deploys go through scripts/deploy.sh..."` are classified STABLE (durable policy, no dated instance attached).
- `"The API currently uses v2 endpoints..."` is flagged AMBIGUOUS (or, at minimum, explicitly discussed as mixed) — it states a durable-sounding fact ("use v2, not v1") using volatile phrasing ("currently"), and the output must not silently force it into one bucket without a rationale noting the tension. A reasonable lean (stable, since "don't call v1" is the durable instruction) must come with a one-line rationale, not a bare classification.
- `"Don't touch the legacy auth module; migration to OAuth2 is in progress, ETA Q3 2026"` is flagged AMBIGUOUS or split in reasoning — it mixes a durable-sounding instruction ("don't touch X") with a dated, task-tracking claim ("ETA Q3 2026"). The output must surface this tension rather than filing the whole line as cleanly stable.
- `"We dropped support for IE11 last quarter..."` is classified VOLATILE (tied to "last quarter", a specific past event) — it must not be misread as a permanent architecture fact just because the practical implication ("no polyfills") sounds durable.
- `"Currently deploying twice a day while we stabilize..."` is classified VOLATILE (explicitly temporary, "while we stabilize").
- `"Remember we're a 4-person team right now..."` is classified VOLATILE ("right now" + team-size snapshot), not treated as a permanent fact about the org.
- The ambiguous table for this scenario is non-empty — this scenario exists specifically to confirm the skill does NOT force-classify every line, and every ambiguous row has a real rationale referencing the specific words that caused the ambiguity.
- No line is dropped, and no new rule/fact is invented beyond what's in the input.
