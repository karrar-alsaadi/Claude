# Failure patterns -> likely cause -> fix in paper-find-misstake

Use in Step 8 when the same weakness appears in more than one report, or when the user asks how to improve the first skill. These are suggestions to the skill's author; do not edit the installed skill unprompted (its folder is read-only: copy to `/tmp/paper-find-misstake`, edit there, package from the copy, keep the original name).

Contents
1. Table
2. How to propose a change
3. Re-test after a change

---

## 1. Table

| Pattern seen in the evaluation | Likely cause in the first skill | Suggested fix |
|---|---|---|
| Quotes or page numbers not found in the paper | Review written from memory of the paper, or text extraction without page breaks | In Inputs, require `pdftotext -layout` and quoting from the extracted file; add: "copy the quoted string from the extracted text, never retype"; lower confidence when location is approximate |
| Recomputed numbers wrong or one-tailed misread | Script output summarised without reading its note | Add a rule to read `status` and notes in the script output and to restate the test assumption in the finding |
| Severity inflation (critical used once or twice) | Severity scale read as "how bad it sounds" | Add a one-line decision rule from `finding-audit.md` section 3 and an example of each level to `report-template.md` |
| Design flaws missed, typos found | Step 3 skipped or genomics module not loaded | Make Step 3 produce a written claim-to-design table before Step 4; add "load the matching reference" as an explicit sub-step |
| False positives on pseudoreplication or double dipping | Checklist applied without reading Methods | Add a "find the sentence that shows the paper did or did not do it" requirement and list the legitimate alternatives (finding-audit.md section 6) |
| "Checked and consistent" contains inconsistencies | Section filled for completeness | Require each consistent item to state the recomputation or comparison done; no item without one |
| Number blamed on the wrong analysis layer | Source of the number not traced | Add to Step 4: "name the layer of each number before blaming a flaw on it" |
| "Not stated" contradicted elsewhere in the paper | Only one section searched | Add to Step 10: "search methods, results and legends before writing not stated" |
| Abstract claims with no finding | No claim-to-finding map | Add to Step 2: "every abstract claim ends as a finding, a consistent line, or not assessed" |
| Confidence ignores the paper's exact wording | Wording not read | Add to `report-template.md` section 4: "wording that settles the point raises confidence" |
| Process narration before the bottom line | Working notes left in the output | Add to Output: "no process narration before the bottom line" |
| Intent language | Pressure from the user's wording | Add the model refusal sentence and the neutral-message-to-editor offer near the top of the output section |
| "Not retracted" with no route | Memory used for integrity claims | State a route or write "not assessed"; link to `verification-tools.md` section 2 |
| Report ignores the user's language or is not phone-friendly | Template followed literally | Add the compact severity table first; group minor items |
| High confidence on assumption-dependent findings | Confidence scale not applied | Require one clause "what would raise or lower this" per finding |

## 2. How to propose a change

Give: pattern, evidence (2-3 finding ids from this evaluation), the section of the first skill to change, the exact replacement sentence, and the expected effect on a named metric (precision, recall, D4). Prefer explaining why over adding capitalised rules; the first skill's style is reasons first.

## 3. Re-test after a change

Run the benchmark in `benchmark.md` on 3 seeds or papers with the old and new version; compare counts of found/missed per category. If the user does not want a benchmark, re-evaluate the same paper with `score.py aggregate` and compare totals and gates.
