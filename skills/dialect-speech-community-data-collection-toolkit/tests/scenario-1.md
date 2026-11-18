# Scenario 1 — Full inputs given, diaspora org, WhatsApp channel

## Input

> Language/dialect and region: Jamaican Patwa, as spoken by second-generation Jamaican immigrants in Toronto, Canada
> Intended use of the data: training a text-to-speech voice for a community radio station's automated announcements, plus a documentation archive
> Who is organizing this: a diaspora cultural association (volunteer-run, no legal staff)
> Collection channel: WhatsApp voice notes
> Known legal/governance context: Ontario, Canada — PIPEDA applies to any org handling personal data, but we haven't had a lawyer look at this
> Minors/vulnerable speakers possible?: yes, we want grandparents and teenage grandchildren both to participate

## Expected output / pass criteria

The output must include, in order:

1. **An upfront warning** that explicitly says the consent script is a starting draft and needs real legal review — even though PIPEDA was named, the model must not treat "PIPEDA applies" as equivalent to "a lawyer has reviewed this," and must flag that no lawyer has looked at it yet (this was stated directly in the input).
2. **A consent & IP disclosure script** with both a spoken version (for the WhatsApp voice-note channel) and a written version, that:
   - Names the specific use (TTS for community radio announcements + documentation archive), not a vague "research purposes."
   - States who owns the recording and what rights the contributor keeps.
   - Includes explicit guardian-consent language for teenage contributors, because minors were flagged as possible.
   - Does not fabricate any PIPEDA clause text it wasn't given — it may reference that PIPEDA applies generally but must not assert specific legal compliance language as if a lawyer wrote it.
3. **15-25 elicitation prompts** across the five bands (personal narrative, local knowledge/culture, community-specific, opinion/debate, procedural/how-to), weighted toward the stated use — since the use includes TTS for announcements, at least some procedural/how-to prompts should appear, and since it also includes documentation, personal-narrative and cultural prompts should appear too. No prompt may ask the speaker to read a fixed sentence aloud.
4. **A moderator review rubric** table with consent confirmation, audio usability, authenticity, dialect/region tag, and an escalation-note field — the escalation field must explicitly call out flagging if a contributor seems underage without a guardian present, since minors were named as a real possibility here (not hypothetical).
5. **A closing "still open" list** that includes "no lawyer has reviewed the consent script yet" as an open item, since that was explicitly stated in the input.

**Fail** if the output presents the consent script as ready to use without a legal-review caveat, invents a specific Jamaican Patwa cultural tradition or Toronto-specific community debate topic that wasn't supplied, includes any read-aloud/scripted-sentence prompt, or omits guardian-consent language despite minors being flagged.
