# Verification tools and procedures

Principle: a tool flag is a lead to verify, never a verdict. Say which tool produced which finding and what its blind spots are.

Contents
1. Numbers and statistics
2. References and retractions
3. Images
4. What not to use as evidence
5. Environment notes (what works in chat)

---

## 1. Numbers and statistics

| Tool | What it checks | Blind spots |
|---|---|---|
| `scripts/check_numbers.py pvalue` / `scan` | Recomputes p from t, F, chi-square, z, r with df, allowing for rounding of the statistic (statcheck-style). Flags consistent / inconsistent / "consistent only if one-tailed" / decision error at 0.05. | Only APA-style strings (`t(28) = 2.31, p = .03`). Misses tables, figures, other notations. Assumes the stated test type. |
| `check_numbers.py ci` | Whether a 95% CI is consistent with the point estimate and with the reported p (normal approximation; log scale for OR/HR/RR). | Small samples use t not z; inputs are rounded, so allow slack. |
| `check_numbers.py grim` | GRIM: whether a mean is attainable for integer data (Likert items, counts) given n. (Brown & Heathers) | Needs integer data; uninformative when n x items >= 10^decimals; missing data change effective n. |
| `check_numbers.py percent` / `sum` | Denominator, percentage, totals with rounding tolerance. | - |
| statcheck (R package / statcheck.io), GRIMMER, SPRITE | Published equivalents; GRIMMER checks SDs, SPRITE explores datasets compatible with summary statistics. | statcheck needs full APA-style reporting. |

Evidence on prevalence (context, not proof for any single paper): with statcheck, roughly half of psychology articles examined had at least one p-value inconsistent with its statistic and df, and about 12% had an error large enough to potentially change the conclusion (Nuijten et al. 2016). Running statcheck during peer review was later associated with a steep decline in such inconsistencies (Nuijten & Wicherts 2024). Brown & Heathers found about half of testable articles had at least one GRIM-inconsistent mean. They stress that failing the test is **not automatically** a sign of manipulation.

Usage:
```bash
# path = where this skill is installed (e.g. /mnt/skills/user/paper-find-misstake)
python <path>/scripts/check_numbers.py scan paper.txt        # whole text
python <path>/scripts/check_numbers.py pvalue --test t --stat 2.31 --df 28 --p .03
python <path>/scripts/check_numbers.py grim --mean 3.45 --n 28
python <path>/scripts/check_numbers.py percent --num 24 --den 120 --reported 25.0 --find-denominator
python <path>/scripts/check_numbers.py sum --parts 40,38,20 --total 100
python <path>/scripts/check_numbers.py ci --est 1.52 --lo 1.10 --hi 2.10 --ratio --p 0.01
```
For PDFs, extract text first: `pdftotext -layout paper.pdf paper.txt` (keep page breaks so you can report page numbers). Always quote the statistic exactly as printed, including trailing zeros; the decimals drive the rounding tolerance.

## 2. References and retractions

Order of effort: (1) references that support the central claim and any surprising claim; (2) all references if the list is short; (3) a sample if the list is long, and say it was a sample.

**Existence and metadata.** Use, in this order of preference and availability:
1. A connected PubMed/Consensus tool (load with `tool_search`, e.g. "PubMed article metadata", "lookup article by citation", "convert article ids"). These return authors, journal, year, DOI, PMID.
2. `web_search` on the exact title or DOI; open the publisher/PubMed page with `web_fetch` if the URL came from search.
3. If the user pasted a reference you cannot find, say "could not locate", not "does not exist".

**Retraction / correction status.** Retractions and corrections are available through Crossref: Retraction Watch data were acquired by Crossref in Sept 2023 and are served via the Crossref REST API (`works/{DOI}` exposes an `update-to` field; `filter=update-type:retraction` lists retractions) and as a downloadable CSV. The Retraction Watch database also contains corrections and expressions of concern, so filter by type. A Retraction Watch Hijacked Journal Checker also exists for checking whether a journal is an impostor. In the chat sandbox only some domains are reachable; if `api.crossref.org` is blocked, search the title + "retraction" or check the PubMed record's retraction notice, and tell the user which route you used. Never declare a reference "not retracted" from training knowledge; say "no retraction notice found in X on date Y".

**Does the reference support the claim?** Read the abstract at least; for central claims read the relevant results. Note mismatches of population, dose, endpoint, or direction of effect. Check that quoted numbers match the source.

## 3. Images
What chat can do: look for duplicated regions, reused panels across figures, inconsistent lane/background patterns, unexplained splices, and mismatch between legend n and visible points, then record location and description. What it cannot do: authenticate raw images, detect sophisticated manipulation, or judge intent.
Phrase as "Panels B and D appear to share an identical region (see description); raw images requested". Escalate to the journal/research-integrity office. Context: Bik et al. (2016, mBio 7:e00809-16) screened 20,621 papers from 40 journals and found ~3.8% with problematic duplications, at least half with features suggesting deliberate manipulation; honest error is also common, which is why wording matters.

## 4. What not to use as evidence
- AI-text detectors or similarity-score percentages as proof of misconduct or error (guide section 7).
- A single recomputed number generalised to the whole paper.
- Press releases or abstracts instead of methods/results/appendices.
- Comparison with another study without checking population, units, definitions.
- PubPeer or social-media threads as evidence; they can point to leads to check yourself.
- Rounding differences read as substantive contradictions without checking the underlying values.

## 5. Environment notes
- Sandbox network is restricted to a short allow-list; do not rely on live API calls from `bash`. Prefer `web_search`/`web_fetch` and connected tools; report any source you could not reach.
- Scanned PDFs need OCR; text extracted by OCR can invent or drop digits. Verify every number you will flag against the page image.
- Never guess page numbers. Use the PDF page index you actually extracted and, if a printed page number differs, say which one you mean.
