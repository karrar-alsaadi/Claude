# Coverage audit: what did the review miss?

Contents
1. Must-check matrix by study type
2. Building the reference list
3. Grading omissions
4. False-reassurance spot-check
5. Edge cases

---

## 1. Must-check matrix (what an adequate review of this scope looks at)

Use the row matching the paper. Items marked * decide whether the central claim stands; missing one of those is a candidate for gate G3.

| Study type | Must-check items |
|---|---|
| Randomised trial | *randomisation/allocation concealment; *primary outcome pre-specified vs reported; flow diagram n vs analysed n; intention-to-treat; multiplicity; harms reporting; registration; CONSORT 2025 items |
| Observational / cohort / case-control | *confounding and adjustment set; *selection and survivor bias; exposure/outcome measurement; missing data; causal wording; STROBE |
| Omics, scRNA-seq / snRNA-seq | *unit of replication (donor vs cell); *double dipping; *batch/donor/sex/age/PMI confounding; *sex and age ratio by disease group; two-list overlap independence; cell-cell communication and ATAC tests; QC counts reconcile; FDR and thresholds; enrichment background; annotation support; trajectory exploratory status; accession and versions |
| In vitro / animal | *replicate definition (biological vs technical); randomisation and blinding; sample-size justification; exclusions; image integrity (visual flags only); ARRIVE 2.0 |
| Prediction / ML | *leakage and donor/patient overlap across splits; external validation; metrics suited to imbalance; calibration; baseline comparison; TRIPOD+AI |
| Meta-analysis | search and selection transparency; heterogeneity; risk-of-bias; publication bias; double counting; effect-size extraction |
| Any paper | every abstract claim mapped to a finding or "not assessed"; central claim vs evidence; numbers reconcile across abstract/tables/figures; units; test choice vs data type; exact n per analysis; references behind the central claims; ethics, funding, conflicts, data/code availability |

If the review declared a narrower scope (language-only, statistics-only), grade coverage against that scope, and separately note in D7 whether the bottom line wrongly implies the whole paper was checked.

## 2. Building the reference list (Step 2 of the workflow)

1. Write the central claim and the three results it depends on.
2. For each must-check item in the matrix, spend a few minutes finding the passage that settles it. Record: item, location, what you found (adequate / flawed / not reported).
3. Run `check_numbers.py scan paper.txt` and recompute the 3-5 most consequential numbers by hand (sample sizes, headline effect, headline p, percentages built on denominators).
4. List only items you can point to. A suspicion without a location goes under "not established", not in the reference list.
5. Do this before comparing with the review's findings, so the review does not anchor you.

Each reference item: `id | location | description | severity (your grade) | evidence`.

## 3. Grading omissions

For every reference item the review did not mention (neither as a finding nor in "checked and consistent"):
- Put it in `missed` with severity, location, evidence.
- Ask: was it within the review's declared scope? If not, do not count it.
- Ask: would a reasonable reviewer working from the paper alone have seen it? Items that need raw data are not omissions.
- Sound-paper case: if the reference list has no substantial items, a review with few or zero findings is not penalised; check instead that it states what it checked.

Weighted recall uses minor 1, moderate 2, substantial 4, critical 8. One missed substantial item moves D3 more than three missed minor ones, by design.

State plainly that recall is measured against your own reference list. It is a lower bound on omissions unless a seeded benchmark was run (`benchmark.md`).

## 4. False-reassurance spot-check

Open 2-3 items from the review's "Checked and found consistent" section, preferring those tied to the central claim. Re-verify each. A consistent-list item that is actually inconsistent is a serious fault: record it as `missed` (substantial, since it reassures the reader about something false) and reduce D6.

## 5. Edge cases

- **No findings, sound paper:** fine if the review lists what it checked and the limits. Test one or two high-risk items yourself.
- **No findings, flawed paper:** coverage 0 on those items; gate G3 if the flaw decides the central claim.
- **Very long review of a short paper:** padding is not coverage. Count only distinct, located items.
- **Paper unavailable (structural mode):** coverage is not scored; say that omissions cannot be assessed.
- **Supplement or raw data needed:** list as `unverifiable` and as a limit; do not count as omission.
- **Multiple versions of the paper (preprint vs published):** confirm the review used the version it states; mismatches are a D6 issue, and findings that exist only in another version are `partial` at best.
