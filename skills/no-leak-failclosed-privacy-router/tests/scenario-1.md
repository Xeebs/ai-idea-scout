# Scenario 1: Solo therapy-practice AI scribe tool

## Input a user would actually paste

> I'm a developer building a session-note assistant for a solo-practice therapist friend. It runs Ollama locally and falls back to OpenAI's API if the local model times out or errors. Here's the routing function:

```python
import ollama
import openai
import time

def generate_note(transcript: str) -> str:
    try:
        response = ollama.chat(
            model="llama3-8b",
            messages=[{"role": "user", "content": transcript}],
            options={"timeout": 15},
        )
        return response["message"]["content"]
    except Exception as e:
        # local model timed out, crashed, or OOM'd — fall back to cloud
        print(f"local inference failed: {e}, falling back to cloud")
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": transcript}],
        )
        return response.choices[0].message.content

def is_sensitive(transcript: str) -> bool:
    # rough heuristic for now
    flags = ["suicidal", "diagnosis", "medication", "abuse"]
    return any(f in transcript.lower() for f in flags)
```

> `is_sensitive()` exists but isn't actually wired into `generate_note()` yet — I just haven't gotten to it. Sensitivity categories that matter: clinical/mental-health content generally, not just the four keywords above.

## Pass criteria

The audit output must:
- [ ] Identify the local path (`ollama.chat`) and cloud path (`openai.chat.completions.create`) correctly.
- [ ] Flag as **CRITICAL**: the `except Exception` block falls back to cloud on ANY local failure, with zero sensitivity check at all (since `is_sensitive()` isn't called) — this is a 100%-sensitive-content-eligible leak path, not a partial one.
- [ ] Flag as **WARNING** (not just dismiss or ignore): `is_sensitive()`'s keyword-list approach, explicitly noting that keyword matching alone is unreliable even if it were wired in, and that "clinical/mental-health content generally" is far broader than four keywords.
- [ ] Flag missing fallback logging/alerting — the `print()` is not a durable log/alert a practitioner or admin would ever see.
- [ ] Note that no default-deny exists because there is no deny path at all right now.
- [ ] Produce a draft YAML fail-closed config that hard-pins a "clinical" category to local-with-queue-or-error, not cloud, and defaults unknown classification to the clinical (most restrictive) category.
- [ ] End with a named red-team test (e.g., kill/timeout the local Ollama process while sending a planted sensitive transcript, confirm it never reaches the OpenAI call).
- [ ] NOT declare the system safe or "mostly fine" at any point — every real path here leaks.

## Fail criteria
- Treating `is_sensitive()` as if it's already protecting requests (it isn't wired in — this must be caught).
- Giving a clean bill of health because "there's a sensitivity function defined somewhere."
- Skipping the logging/alerting finding.
