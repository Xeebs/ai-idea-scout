# Scenario 1 — Weather/geocoding MCP server minor version bump

## Setup
A team runs an internal agent that depends on a third-party MCP server `weather-tools` for forecasts. They're deciding whether to accept v2.3 → v2.4.

## Input provided to the skill

**Baseline snapshot (v2.3)**:
```json
[
  {
    "name": "get_forecast",
    "description": "Returns a 5-day weather forecast for the given coordinates. Temperature is in Celsius.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "lat": {"type": "number"},
        "lon": {"type": "number"},
        "units": {"type": "string", "enum": ["metric", "imperial", "standard"]}
      },
      "required": ["lat", "lon"]
    }
  },
  {
    "name": "geocode_address",
    "description": "Converts a free-text address into lat/lon coordinates. Returns the single best match.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "address": {"type": "string"}
      },
      "required": ["address"]
    }
  }
]
```

**Current snapshot (v2.4)**:
```json
[
  {
    "name": "get_forecast",
    "description": "Returns a 5-day weather forecast for the given coordinates. Temperature is in Fahrenheit by default; pass units=metric for Celsius.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "lat": {"type": "number"},
        "lon": {"type": "number"},
        "units": {"type": "string", "enum": ["metric", "imperial"]}
      },
      "required": ["lat", "lon"]
    }
  },
  {
    "name": "geocode_address",
    "description": "Converts a free-text address into lat/lon coordinates. Returns up to 5 candidate matches ranked by confidence; use the first for the previous single-match behavior.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "address": {"type": "string"}
      },
      "required": ["address"]
    }
  }
]
```

**Calling pattern provided**: "Our code calls `get_forecast` without ever setting `units` explicitly — we rely on the default. We call `geocode_address` and read `response.lat`/`response.lon` directly as if it's a single object, not a list."

## Pass criteria

- [ ] Report identifies the `get_forecast` default-unit change (Celsius → Fahrenheit when `units` is omitted) as **BREAKING**, naming it as a changed-units issue, and correctly ties it to the fact that the caller never sets `units`.
- [ ] Report identifies the `units` enum narrowing (`standard` removed) and classifies it SAFE or WARN with correct reasoning that the caller never used `standard` — must not be marked BREAKING, since this specific caller never passes it.
- [ ] Report identifies the `geocode_address` description/behavior change (single match → list of up to 5) as **BREAKING**, correctly reasoning that the caller reads `response.lat`/`response.lon` as a single object, which will now fail or silently read the wrong shape against a list response.
- [ ] Report explicitly names the mechanism for each row (changed units, enum narrowed, response shape changed from object to list) — no bare label without a "Why."
- [ ] Final recommendation is "do not upgrade" or "upgrade only after addressing" given the two BREAKING items — must not say "safe to upgrade."

## Fail criteria (any of these = skill failed)
- Classifies the default-unit change as SAFE or WARN (it is a live BREAKING data-correctness bug for this caller).
- Misses the geocode response-shape change entirely, or treats it as a cosmetic description edit.
- Recommends upgrading without flagging both BREAKING items.
