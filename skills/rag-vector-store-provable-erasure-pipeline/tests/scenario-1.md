# Scenario 1 — Manual fallback, SaaS support-bot RAG stack on Pinecone

## Setup
A backend engineer at a mid-size SaaS company runs a customer-support RAG assistant that indexes transcripts of past support tickets (which contain customer names, emails, and account details) into Pinecone for retrieval. Legal just asked engineering whether the team can actually honor a GDPR erasure request if one comes in. The engineer has no live connector access in this chat tool — plain manual paste — and says:

"We need to figure out if we're exposed on right-to-erasure for our support bot. Here's what I know:

1. We use Pinecone. When a customer asks to be deleted, we run a script that calls `index.delete(ids=[...])` with the vector IDs tied to their ticket transcripts. We don't double check it afterward.
2. We back up the whole Pinecone namespace to S3 nightly via Pinecone's export feature. I have no idea how long those exports sit around — I don't think anyone set a lifecycle policy on that bucket.
3. At ingestion, we do tag each chunk with the `ticket_id` and `customer_id` metadata field, so we can find all of a customer's vectors.
4. Right now, deletion requests come in over email to our support lead and she just forwards them to me. There's no ticket or log — I just do it and reply 'done.'"

## Expected output (what a pass looks like)
- A stack summary table with at least two layers assessed separately: the live Pinecone index, and the S3 nightly export/backup. Does not lump them into one row.
- Live Pinecone index scored **CLAIMED** (addressable via `customer_id`/`ticket_id` tag — yes; a delete call is made — yes; but no re-query/verification step — explicitly stated "we don't double check"), not PROVABLE.
- S3 nightly backup scored **UNKNOWN** or **MISSING**-leaning given no known lifecycle policy and no indication the backup is ever purged of the deleted customer's data — the report must flag that an unbounded/unknown-retention backup is the realistic exposure, not the live index.
- Headline gap names the S3 backup specifically as the weakest link, tying it to the fact that retention is unknown/unbounded.
- Manual stopgap runbook includes at minimum: re-querying Pinecone post-delete to confirm absence, finding out (from whoever owns the S3 bucket) whether a lifecycle/retention policy exists and setting one if not, and starting some durable log of requests (even a shared doc) instead of email-then-forget.
- Explicitly notes that ingestion-time tagging (`customer_id`) is a strength, not a gap — the report should not penalize this layer since it's the one thing already done correctly.
- Includes the mandatory disclaimer that this is a technical audit, not a legal compliance determination.
- Fails if: the live Pinecone index is scored PROVABLE despite no verification step being described; the S3 backup is omitted from the table entirely; the report asserts a specific retention period for the S3 bucket that was never stated (fabrication); the report states or implies this satisfies GDPR outright without the disclaimer; the report recommends an actual delete/mutation action be performed by the assistant itself rather than by the user's own systems.
