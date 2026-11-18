# Scenario 2: Small, uniform HR policy-manual corpus (does not justify building the router)

## Input

An HR software vendor wants to add a "search our policy templates" RAG feature. They supply 6 sample PDFs (uploaded as files, not a description table):

1. `employee-handbook-template-v3.pdf` — 48 pages, born-digital, standard text with a couple of simple bulleted tables (PTO accrual schedule, benefits summary) — no charts, no scans.
2. `remote-work-policy.pdf` — 12 pages, born-digital, plain text, no tables.
3. `code-of-conduct.pdf` — 20 pages, born-digital, plain text.
4. `benefits-enrollment-guide.pdf` — 30 pages, born-digital, one 2-page comparison table of plan tiers, otherwise plain text.
5. `pto-policy-addendum.pdf` — 8 pages, born-digital, plain text.
6. `signed-acknowledgment-form-scan.pdf` — 2 pages, scanned (a single employee's signed acknowledgment form, scanned for one historical compliance example) — this is the only non-born-digital file in the set, and the vendor says "this one scanned file is a one-off, not representative of our template library going forward."

They ask: "Is it worth building a smart router for this, or should we just use native text extraction and handle that one scanned form manually?"

## Pass criteria

- [ ] Per-document breakdown correctly identifies 5 of 6 documents as overwhelmingly Native-clean, with only small table-containing sections (employee handbook, benefits guide) that are simple comparison/accrual tables, not dense enough to clearly require vision-model routing — the tool should either classify these as borderline Native-clean/low-risk Vision-candidate and flag the ambiguity, or note the tables are simple enough that native/OCR+layout likely suffices, rather than overclassifying them as high-stakes vision cases.
- [ ] Identifies `signed-acknowledgment-form-scan.pdf` as the lone OCR-needed document and explicitly treats it as an outlier, consistent with the vendor's own framing that it isn't representative going forward.
- [ ] Does NOT flag any document as "mixed within document" in a way that would push toward building a router (none of these documents individually mix bucket types at meaningful scale — the one scanned file is a separate, standalone document, not a mixed-content document).
- [ ] Build-vs-pick-one-default verdict recommends NOT building a per-page router — with 1 outlier document out of 6 (not individually mixed documents), this is well under the ~15% mixed-within-document threshold — and instead recommends native text extraction as the default with manual/one-off OCR handling for the single scanned form, matching the vendor's own instinct.
- [ ] States clearly this recommendation came from actual file inspection (since files were uploaded, not described secondhand) rather than self-reported description.
- [ ] Does not recommend building vision-model routing infrastructure for a corpus this uniform and small, even though a couple of simple tables exist — correctly distinguishes "has a table" from "is table/chart-dense enough to need vision routing."

## Fail conditions

- Recommending a full automatic per-page router for a corpus this small and uniform (over-engineering relative to the actual mix shown).
- Treating the simple PTO/benefits comparison tables as clear vision-candidates requiring a vision-model call, without flagging that this is a judgment call on simple tables.
- Failing to call out the one scanned file as a one-off outlier, consistent with what the vendor already told it.
- Confidence note incorrectly saying this was self-reported when actual files were supplied.
