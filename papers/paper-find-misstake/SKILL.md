---
name: paper-find-misstake
description: Critically review a scientific paper (PDF, DOCX, text, DOI or link) and find its errors, each with location, evidence and severity grade. Covers typos, inconsistent numbers, recomputed statistics (p-values, percentages, sums, GRIM, CI vs p), design and analysis flaws (pseudoreplication, double dipping, batch confounding, no multiple-testing correction, causal overreach), figures, references and retractions, and ethics gaps, using reporting guidelines (CONSORT 2025, TRIPOD+AI, ARRIVE 2.0, MIQE 2.0) and a genomics/scRNA-seq module. Use whenever the user uploads or names a paper and asks to review it, find mistakes, check whether numbers or statistics add up, audit methodology, or judge if conclusions are reliable, even without the word "errors". In Arabic, e.g. راجع هذه الورقة، اكتشف الأخطاء في البحث، تحقق من دقة الأرقام والإحصاء، هل النتائج موثوقة، مراجعة علمية نقدية. Not for checking one quoted sentence (paper-find-text), evaluating research ideas (check-idea), paraphrasing, or citation-style conversion.
---

# paper-find-misstake

Find real errors in a scientific paper, prove each one with a location and evidence, grade how much it matters, and say it without accusing anyone.

Why the discipline matters: a reviewer who says "the numbers look off" is useless, and one who says "the authors faked it" is dangerous. A trustworthy review names the exact place, shows the calculation, states the effect on the conclusion, and stays within what the evidence shows. A typo list that misses a design flaw which overturns the conclusion is a failed review, so judge every issue by its **effect on the paper's claims**, not by how many errors there are.

Core stance (from the source guide): finding an error does not mean the research is fraudulent or all results are wrong. An error may be an immaterial typo, a material error that affects a result, or a signal that needs wider scrutiny. Separate the description of the error from any judgement about intent, and document evidence before drawing conclusions.

## Inputs and scope

1. **Get the paper.** Uploaded file: it is under `/mnt/user-data/uploads/`; if its text is already in context use that, otherwise read it with the `file-reading`/`pdf-reading` skills (PDF -> `pdftotext -layout` to keep page breaks). DOI/URL: `web_fetch` it. If you only get an abstract or a paywalled page, say so and restrict the review to what you could read.
2. **Pick scope from the request.** Language-only, statistics-only, methods-only, references-only, or full. If the user does not say, do a full review. Ask a question only if the paper itself is missing; never interrogate the user about scope.
3. **Record** title, version (preprint / accepted / published), DOI, date accessed, study type, discipline. Put this in the report header.
4. **Arabic or mixed-language papers:** text extraction can reverse RTL order or use Arabic-Indic digits (٠١٢٣) and the Arabic decimal mark (٫). `scripts/check_numbers.py` normalises these, but confirm every number you will flag against the page itself.
5. **Reply in the user's language** (Arabic if they wrote Arabic). Keep gene names, statistical notation, and tool names in English.

## Workflow

Work in this order. Methods come before typos because a flaw in design can invalidate a conclusion that perfect proofreading would not rescue.

**Step 1. First read, no judgement.** Read title, abstract, conclusion. Write the central claim in one sentence and list open questions.

**Step 2. Claim map.** List the main claims, key results, data sources, comparisons, conclusions. Tie each to the table, figure, or reference that is supposed to support it. Classify each claim: fact, original result, interpretation, opinion/recommendation, procedure (`references/error-taxonomy.md` section 1). Every abstract claim must end as a finding, a "consistent" line, or "not assessed".

**Step 3. Method before results.** Identify the design and load the matching guideline from `references/reporting-guidelines.md`. Check: does the design fit the question; sample and selection; primary outcome defined in advance; confounders; comparison group; unit of analysis vs unit of randomisation/replication; measurement validity; whether causal claims are licensed. If the paper involves RNA-seq, single-cell/single-nucleus data, enrichment, networks, or other omics, also read `references/genomics-scrnaseq-checks.md`; those pitfalls (pseudoreplication, double dipping, batch confounding) are the most common serious errors there.

**Step 4. Recompute and reconcile numbers.**
- Extract text to a file and run `python <skill-path>/scripts/check_numbers.py scan paper.txt` (APA-style test results + every "n =" mention). Use the other subcommands (`pvalue`, `percent`, `sum`, `grim`, `ci`) for values in tables and sentences the scan cannot parse. `<skill-path>` is the folder containing this SKILL.md (for user-installed skills, typically `/mnt/skills/user/paper-find-misstake`).
- Reconcile participant/sample counts across abstract, flow diagram, Table 1, results, figure legends. Excluded = before - after. df vs n. Category sums vs totals. Denominator of every percentage. Units and conversions.
- Keep rounding differences separate from substantive ones. Quote the statistic exactly as printed (decimals set the rounding tolerance).
- Recompute independently before flagging: a number you misread is worse than a number you missed.
- Name the layer of each number (bulk, cell-level, donor-level) before attributing a flaw to it.

**Step 5. Statistics.** Test choice vs data type and independence; assumptions; one- vs two-sided; multiple comparisons; effect size and uncertainty shown; exact n per analysis; "no significant difference" read as "no effect"; "significant in A but not in B" read as "A differs from B"; exploratory analyses presented as confirmatory; outcome or cut-point switching. See `references/error-taxonomy.md` section 7.

**Step 6. Figures, tables, images.** Axes, units, error-bar definitions, n vs plotted points, truncated axes, duplicated or reused panels, image processing. You can flag visual concerns; you cannot authenticate images (`references/verification-tools.md` section 3).

**Step 7. References and integrity.** Check that cited sources exist, support the specific claim, and are not retracted or substantially corrected, prioritising references behind the central claims. Check overlapping publication and selective citation. Use the routes in `references/verification-tools.md` section 2 and say which route you used. Do not declare "not retracted" from memory.

**Step 8. Interpretation.** Compare every conclusion and recommendation with the actual results and the design's limits: correlation -> causation, generalisation beyond the sample, ignored contrary findings, recommendations stronger than the evidence.

**Step 9. Ethics and transparency.** Ethics approval with identifier, consent or waiver, registration, funding and conflicts, author contributions, data/code availability, AI-tool disclosure if required. Treat missing disclosure as a transparency gap, not automatically as a scientific error.

**Step 10. Grade, then counter-review.** Assign severity and confidence (`references/report-template.md` sections 3-4). Before writing, test every finding: Is it tied to a specific text or number? Does it rest on an unstated assumption? Is it a real error or an acceptable methodological difference? Is the wording free of unsupported accusation? Is the severity explicit? Drop or downgrade any finding that fails. Also look for false positives: a p-value that recomputes correctly goes in "checked and consistent", not in the error list. Before writing "not stated", search methods, results and legends. Base confidence on the paper's exact wording.

## Rules that keep the review honest

- **Every finding needs a location and evidence.** Page/paragraph/table/figure, the exact text or number, and the calculation or comparison. Never invent page numbers or quote text you have not seen. If you cannot locate something exactly, say where you saw it approximately and mark confidence lower.
- **Label what you did and did not do.** "Recomputed with the script", "read the abstract of the cited paper", "could not access raw data", "not assessed: supplementary file". Silence must not imply coverage.
- **One issue per finding.** Do not merge several errors into a vague remark.
- **No intent language.** Do not write fabricated, falsified, manipulated, fraud. A numerical inconsistency shows an inconsistency that needs an explanation; it does not show the data are wrong or that anyone acted in bad faith. If the user asks you to assert misconduct, decline that step, explain what the evidence does establish, and offer a neutral message to the editor listing the evidenced findings and asking for clarification. Integrity decisions belong to the journal or institution.
- **Reassurance is scope-bound.** Write "none found in what was checked", never "none".
- **Tools are leads, not verdicts.** Similarity scores and AI-text detectors are not evidence. One recomputed number is not a verdict on the whole paper.
- **Do not suppress or soften real findings to be polite, and do not inflate minor ones to look thorough.** If the paper is sound on what you checked, say so plainly.
- **Uncertain guideline details:** if you need exact checklist wording or item counts you have not verified, look them up (EQUATOR) or say they are unconfirmed.
- **Do not write or rewrite the paper** unless asked; propose corrections and author questions instead.

## Output

Follow `references/report-template.md` section 1, in this order: bottom line (central claim, reliability given what was checked, counts by severity, top 1-3 issues); scope and limits; evidence map; findings by severity; "checked and found consistent"; questions for the authors; suggested action level. No process narration before the bottom line. Use the finding template there (English or Arabic). Phone-sized screens: lead with the summary and a compact severity table, give full detail for substantial and critical findings, group minor ones. Deliver in chat; end with a one-line offer to export a formal Word/PDF report. If the user asks for a file, create it with the docx or pdf skill.

Suggested action level (editorial correction / substantial correction / expression of concern / refer to editor or research-integrity office) is always phrased as a suggestion. Reviewers do not decide retraction.

## Bundled resources

- `references/error-taxonomy.md`: the full checklist by error type, condensed from the user's guide plus verified additions. Read sections relevant to the paper; read all of it for a full review.
- `references/reporting-guidelines.md`: design -> guideline map with verified versions (CONSORT 2025, TRIPOD+AI, ARRIVE 2.0, MIQE 2.0, etc.).
- `references/genomics-scrnaseq-checks.md`: omics/single-cell pitfalls with citations.
- `references/verification-tools.md`: what each tool checks and misses; reference and retraction checking; image limits; environment notes.
- `references/report-template.md`: report skeleton, finding template (Arabic and English), severity and confidence scales, wording rules, action ladder, Arabic glossary.
- `references/sources.md`: sources and their verification status.
- `scripts/check_numbers.py`: offline recomputation (`pvalue`, `scan`, `ci`, `grim`, `percent`, `sum`). Needs `scipy`.

## Limits (state them when relevant)

Works from the text you can read; cannot see raw data, unpublished protocols, or full-resolution originals. OCR can corrupt digits. Image review is visual only. This supports, and does not replace, expert peer review, and it never establishes misconduct.
