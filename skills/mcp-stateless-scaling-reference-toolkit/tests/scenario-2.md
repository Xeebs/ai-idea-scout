# Scenario 2 — Python FastMCP server that's actually fine, plus a narrow miss

## Input

A different team hands over `server.py` from a Python MCP server built on
`FastMCP`, asking: "Someone on the team says we're already stateless because
we don't use any session objects. Can you confirm before we remove our
nginx `ip_hash` config?"

```python
from mcp.server.fastmcp import FastMCP
import time

mcp = FastMCP("internal-tools")

# Loaded once at process start from env/config file. Same on every instance.
TENANT_CONFIG = load_tenant_config_from_env()

# Per-tenant rate limiting — NOT keyed by session, keyed by tenant id,
# but still an in-process dict that only this instance sees.
_rate_limit_counters: dict[str, list[float]] = {}

def check_rate_limit(tenant_id: str, limit: int = 100, window_seconds: int = 60) -> bool:
    now = time.time()
    hits = _rate_limit_counters.setdefault(tenant_id, [])
    hits[:] = [t for t in hits if now - t < window_seconds]
    if len(hits) >= limit:
        return False
    hits.append(now)
    return True

@mcp.tool()
def run_report(tenant_id: str, report_name: str) -> str:
    if not check_rate_limit(tenant_id):
        raise ValueError("rate limit exceeded")
    # pure computation from arguments + TENANT_CONFIG, nothing session-scoped
    return f"generated {report_name} for {tenant_id}"
```

nginx excerpt (`infra/nginx.conf`):
```
upstream mcp_backend {
    ip_hash;
    server 10.0.1.10:8000;
    server 10.0.1.11:8000;
}
```

## Pass criteria

- [ ] Does **not** flag `TENANT_CONFIG` — it's env/config-loaded and
      identical across instances, correctly excluded per the skill's "do not
      flag" list.
- [ ] Does **not** flag `run_report`'s own body — it's pure per-request
      computation, no session scoping.
- [ ] **Does** flag `_rate_limit_counters` as an in-process, per-tenant
      cache with no externalization — correctly notes this is keyed by
      tenant, not by MCP session, but is still an in-process map that will
      silently under-count (allow more than the configured rate) once
      traffic is split across the two instances, which is a real
      correctness bug, not just a scaling nuisance.
- [ ] Recommends Redis for the rate-limit counters specifically because the
      data is small, short-lived, and latency-sensitive — a sliding-window
      counter is a textbook Redis use case — and names the TTL
      (`window_seconds`, i.e. 60s) explicitly.
- [ ] Correctly tells the team **not** to remove `ip_hash` yet — the
      counters still need to move to Redis first — directly answering their
      stated question rather than agreeing with the "we're already
      stateless" claim.
- [ ] Verdict is `NEEDS-MIGRATION (1 spot)`, explicitly correcting the
      team's assumption rather than rubber-stamping it.

## Fail criteria

- [ ] Agreeing that the server is `STATELESS-READY` because there's no
      "session object" by that name — the skill must recognize that
      tenant-keyed in-process state has the identical failure mode as
      session-keyed state once instances multiply.
- [ ] Flagging `TENANT_CONFIG` as a problem (false positive — it's identical
      across instances by construction).
- [ ] Recommending DynamoDB for a 60-second sliding-window counter (wrong
      store for the data's actual shape — this scenario exists specifically
      to test that the store recommendation isn't just "always Redis" or
      "always DynamoDB" applied without reasoning).
