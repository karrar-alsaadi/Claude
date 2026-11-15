---
name: "paper-change-citation-style"
description: Convert a manuscript's numbered citations ([1], [2], superscripts) and its reference list into author-year APA 7th edition, with verified DOIs and optional DOI hyperlinks on the in-text citations. Use this skill whenever the user wants to change, convert, reformat, standardize, clean up, or fix citations or references, including phrases like "convert my references to APA", "change citation style", "replace [1] with author-year", "add DOI links to citations", "fix my reference list", or when the user pastes text containing numbered citations plus a reference list. Also use it when a reference list has duplicates, merged entries, missing DOIs, or preprint/published versions that need reconciling, even if the user never says "APA".
---

# Change Citation Style

Convert a text with numbered citations and a raw reference list into a clean APA 7th edition document. The hard part is not formatting; it is keeping every in-text citation attached to the *right* reference while never inventing bibliographic data. A wrong DOI or a guessed author list is worse than a flagged gap, because readers will trust it.

## Core principles

1. **Never fabricate.** If a DOI, year, volume, page range, or author is missing or unverifiable, leave a visible placeholder (`[DOI MISSING]`) and report it. Do not guess from memory.
2. **Verify before asserting.** If web search or fetch tools are available, confirm each DOI resolves to the paper with the matching title and authors (e.g., search Crossref or `https://doi.org/<DOI>`). If no tools are available, state clearly that DOIs were checked for format only, not resolved.
3. **Stop on structural problems, don't paper over them.** Mismatched counts, merged entries, and duplicates change what the in-text numbers mean. Surface them first, then proceed with the user's confirmation or with clearly stated assumptions if the user asked for a one-shot result.
4. **Log every change.** Keep a change log (what changed and why) so the user can audit the result.

## Inputs to collect

Gather from the message or ask once, briefly:

- The body text with numbered citations (`[1]`, `[1,3]`, `[2–5]`, or superscripts)
- The raw reference list
- Target style (default: APA 7th)
- Hyperlink preference: none / in-text citations link to DOI / DOI shown in reference list (default: DOI in reference list, in-text links if the output format supports them)
- Output format (default: plain text/Markdown in chat; produce .docx only if the user asks, following the docx skill)

## Workflow

### Phase 0 — Intake checks

1. Extract every citation number used in the text, expanding ranges (`[2–5]` → 2, 3, 4, 5).
2. Count the entries in the reference list.
3. Compare. Report:
   - numbers cited in text but absent from the list
   - list entries never cited in text
   - duplicate or skipped numbers
4. Fix obvious typos in the body text (author names, technical terms, statistics) only when unambiguous; note each in the change log. Do not alter the raw references yet.

### Phase 1 — Build the mapping table

Create a table before converting anything:

| # | Where cited (para/sentence) | Raw reference (short) | Status |
|---|---|---|---|

**Merged references.** If one numbered entry contains several papers (e.g., "1. Smith et al., … AND Jones et al., …"), split them into 1a, 1b, … and decide with the user (or state your assumption) which in-text uses of [1] point to which paper. Update the table.

**Duplicates.** If several numbers describe the same paper (e.g., [2], [4], [5] are all Wang et al., 2024), keep the lowest number as canonical, and redirect every duplicate's in-text uses to it. Compare title, year, and DOI, not just first author, since same-author papers in the same year are common (these need 2024a/2024b suffixes).

**Preprint vs. published.** If the list holds both a preprint and its published version, cite the published version and drop the preprint, unless the text explicitly discusses the preprint. Log the merge.

### Phase 2 — Completeness and DOI verification

For each unique reference, check the fields: authors, year, title, journal/publisher, volume, issue (if the journal uses issues), pages or article number, DOI.

- Missing fields → attempt to resolve via a trustworthy source when tools allow (Crossref, PubMed, publisher page). Only fill a field if the source clearly matches the same paper.
- DOI format: `10.<registrant>/<suffix>`, no trailing punctuation, no spaces.
- A resolved DOI must match the reference's title and first author. If it points elsewhere, flag it as wrong; do not silently swap in another.
- Misspellings that break lookup (author names, title words) can be corrected once the paper is positively identified; log the correction.

Anything unresolved goes into the **Problems report** (see below) rather than being guessed.

### Phase 3 — Format the reference list (APA 7th)

Journal article template:

```
Author, A. A., Author, B. B., & Author, C. C. (Year). Title of article in sentence case. *Journal Name in Title Case*, *Volume*(Issue), pages or Article number. https://doi.org/xxxxx
```

Rules that matter and are easy to get wrong:

- **Authors:** list up to 20 authors, with `&` before the last one. For 21 or more, list the first 19, then an ellipsis (`. . .`), then the final author. Do **not** truncate at 6 with "et al." in the reference list; that is a common mistake and not APA 7. If the user's source list is already truncated and the full author list cannot be verified, keep what is known and flag it in the Problems report rather than inventing names.
- **Title:** sentence case (capitalize first word, first word after a colon, and proper nouns). No italics, no quotation marks for articles.
- **Journal and volume:** journal name and volume number in italics; issue number in parentheses, not italic; no "Vol." or "No."
- **Pages/article numbers:** `270–279` with an en dash; for article-numbered journals use `Article 5815` (or the journal's e-locator).
- **DOI:** always as `https://doi.org/…` URL, no "DOI:" label, no period after it.
- **Ordering:** alphabetical by first author's surname, then by year; same author-year gets a, b, c suffixes assigned by title order.
- **Books, chapters, preprints, websites:** use the corresponding APA 7th pattern. Preprints keep the repository name and identifier. Never force a journal template onto a non-journal source.

Worked example:

Raw: `Kreiser, S.; Eckhardt, J.; et al. 2015. Murine CD83-positive T cells mediate suppressor functions in vitro and in vivo. Immunobiology 220, 270–279.`

After verification, complete author list and DOI filled in from the resolved record:
`Kreiser, S., Eckhardt, J., Kuhnt, C., … (2015). Murine CD83-positive T cells mediate suppressor functions in vitro and in vivo. *Immunobiology*, *220*(2), 270–279. https://doi.org/10.1016/j.imbio.2014.12.008`
(The full author list must come from the verified record, not from this example.)

### Phase 4 — Rewrite in-text citations

Replace each `[n]` using the mapping table (after de-duplication and splits).

| Authors | First and later citations |
|---|---|
| 1 author | (Smith, 2020) |
| 2 authors | (Smith & Jones, 2020) |
| 3+ authors | (Smith et al., 2020) |

- **Narrative vs. parenthetical:** if the sentence already names the authors or the citation serves as the sentence's subject ("As shown in [4], …"), use narrative form: "Wang et al. (2024) showed…". Otherwise use parenthetical form at the end of the clause, before the period.
- **Multiple sources in one parenthesis:** APA 7th orders them **alphabetically** by first author, separated by semicolons: `(Gazestani et al., 2023; Wang et al., 2024)`. If the user or target journal asks for chronological order, use oldest → newest instead and say so in the change log.
- **Same first author, same year:** use the a/b suffixes consistently in the list and text.
- **Ranges:** `[2–5]` expands into individual author-year entries; never keep the range.
- Do not change the surrounding wording beyond what the citation form requires.

### Phase 5 — Hyperlinks (only if requested)

- Reference list: DOI as a live `https://doi.org/…` URL.
- In-text: link the citation text (e.g., "(Wang et al., 2024)") to that reference's DOI URL. In Markdown: `[(Wang et al., 2024)](https://doi.org/…)`. In a .docx, use real hyperlinks via the docx skill.
- Combined citations `(A, 2020; B, 2021)` link each author-year segment separately.
- Only link references whose DOI was verified; leave unverified ones unlinked and listed in the Problems report.

### Phase 6 — Final audit

Run this checklist and report the results:

- [ ] No `[n]` markers remain in the text
- [ ] Every in-text citation has exactly one matching reference-list entry, and vice versa
- [ ] Reference list is alphabetized; a/b suffixes consistent
- [ ] Every entry follows the APA 7th patterns above
- [ ] Every DOI is formatted as a URL and was verified (or is listed as unverified)
- [ ] Three random spot checks: pick three citations, confirm author, year, and title match between text and list

## Output structure

Deliver in this order, keeping each part compact:

1. **Problems report** — a short list of items needing the user's attention, each with the reference number and the exact issue (missing DOI, unresolved DOI, incomplete authors, missing year, count mismatch, ambiguous merged entry). Put this first if anything blocks a trustworthy result; otherwise say "No blocking issues."
2. **Converted text** — body with author-year citations.
3. **Reference list (APA 7th)** — alphabetized.
4. **Change log** — merges, splits, dedupes, typo fixes, reorderings, and anything assumed.

For long manuscripts, save the converted text and reference list to a file (`.md`, or `.docx` if requested) and give only the Problems report and a summary in chat.

## Stop-and-report conditions

Do not silently continue past these; state each one explicitly:

- Citation numbers in the text with no matching list entry, or list entries never cited
- A reference with no identifiable authors, no year, or no DOI/URL that can be verified
- A DOI that fails to resolve or resolves to a different paper
- A merged entry whose in-text uses cannot be attributed to one of its papers
- Two candidate papers that both fit a truncated raw reference

When the user wants a complete result anyway, proceed with clearly marked placeholders (`[DOI MISSING]`, `[YEAR MISSING]`) instead of guessing.

## Other styles

If the user targets a style other than APA 7th (Vancouver, Harvard, Chicago author-date, IEEE, etc.), keep Phases 0–2 and 6 identical, since they concern data integrity, and swap in that style's reference and in-text rules for Phases 3–4. If unsure about a rule of a less common style, say so rather than guessing.
