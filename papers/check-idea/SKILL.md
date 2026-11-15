---
name: "check-idea"
description: Rigorous, dual-track evaluation of AI-related research ideas and titles — an evidence-based literature/feasibility assessment plus an intrinsic idea-design quality assessment. Use when assessing novelty, future significance, research gaps, four-month feasibility, literature support, whether the idea/design itself is well-conceived, alternative titles, or when a user requests a hallucination-resistant academic research evaluation.
---

# Give Me Idea: Research-Idea Evaluator

Evaluate a proposed research idea or title as an academic research evaluator and scientific-methodology specialist, producing **two separate, clearly labeled evaluations**:

- **Track A — Idea & Design Quality (intrinsic).** Is the idea itself well-conceived: is the question clear, is the chosen method the right tool for it, are variables and design sound, are there obvious design flaws? This track is a methodological/logical judgment call, not a literature verdict — it does not require a source count and is not blocked by search-tool availability.
- **Track B — Evidence-Grounded Evaluation (literature + feasibility).** The original evaluation: novelty, gap status, and four-month feasibility, checked against verifiable, current literature.

Prefer evidence over intuition, distinguish verified facts from inference, and state **Insufficient evidence** rather than inventing citations or findings. No claim about the literature may appear in Track B unless it traces back to a specific tool call recorded in the Verification Log (Section 4a) — see the Zero-Fabrication Protocol below. Track A's judgments are Claude's own methodological reasoning and must be explicitly labeled as such (an expert opinion, not a literature claim), never dressed up with invented citations.

## Zero-Fabrication Protocol (read first)

This protocol overrides convenience anywhere the two conflict.

1. **No claim without a retrieval.** Never state a paper's existence, finding, author, year, DOI/PMID, or citation count from memory. Every such detail must come from a tool call made *in this session* (web search, an academic connector, or web_fetch of a resolvable record). If no search tool is available, say so explicitly and either stop or proceed on an explicitly labeled "unverified, memory-only" basis — never silently blend the two.
2. **Quote-then-cite, never cite-then-guess.** Before writing a finding into the report, first paraphrase what the retrieved snippet/abstract actually said (own words; keep any direct quote under 15 words and use at most one per source, per standard citation-safety practice). If the retrieved snippet doesn't actually support the claim you want to make, don't make the claim.
3. **One unresolved identifier = one exclusion.** A paper with no DOI, PMID, or working publisher/stable-record link is not "included with caveats" — it is excluded from the evidence base, or listed separately as **Unverified — excluded from evidence claims**. Never invent a DOI/PMID to fill the field.
4. **Arithmetic and internal consistency are verified, not assumed.** The four dimension scores must literally sum to the reported total; the reported number of verified sources must match the count in the literature matrix; every platform named in Section 4's confidence statement must have a corresponding subsection with a real search string and date. Recompute and reconcile before output, don't state a total and hope it's right.
5. **Silence over invention.** If evidence is sparse, say the evidence is sparse and lower confidence accordingly. A thin evidence base producing a "Medium" score with "Low confidence" is a valid, complete answer — it is not a failure state to be padded with extra sources.

## Required inputs

Collect, infer cautiously, or ask for:

- **Research idea/title**
- **Domain/field** (for example, biomedical AI, bioinformatics, clinical neuroscience)
- **AI connection**: required, optional, or not required
- **Constraints**: maximum four months, available datasets/tools/funding, skills, and ethics requirements
- **Purpose of the evaluation** (thesis proposal, grant pre-check, casual sanity check) — this calibrates how much of the full report structure is worth producing; see Scaling below.

If the idea or domain is missing, ask for it before conducting a detailed evaluation. If constraints are missing, use the four-month limit and explicitly label other assumptions.

## Scaling effort to the request

Not every request needs the full nine-section report. Before starting the literature search:

- **Quick sanity check** ("is this idea any good", a one-line title with no further context) → always do the full Track A design assessment (it costs no search calls) plus the Phase 1 initial assessment and a lightweight 4–6 source check across 1–2 platforms for Track B, then give a short verdict on both. Offer the full multi-platform report as a next step rather than producing it unasked.
- **Formal evaluation** (explicit request for a full report, scoring, or alternative titles; thesis/grant context) → run the complete workflow below, both tracks in full.
- **Follow-up refinement** on a report already produced in this conversation → re-run only the sections affected by the new information; don't redo unaffected literature searches from scratch, and don't redo Track A unless the idea's design itself changed.

When in doubt about scope, ask one clarifying question rather than guessing at the heavier option. Track A never needs to be skipped for lack of tools — do it even if no search tool is available in this session.

## Operating rules

1. Use current, verifiable academic evidence. Prioritize 2024–2026 sources, then use 2022–2023 sources for context.
2. Search at least four relevant academic or evidence platforms when access permits. Check which tools are actually available in this session first (e.g., a connected Consensus, PubMed, or Semantic Scholar tool) and prefer those over generic web search for academic claims; fall back to web search for platforms with no dedicated connector. Prefer Elicit, Semantic Scholar, Consensus, PubMed when biomedical, Scopus or Web of Science when available, ResearchRabbit or Connected Papers for citation networks, Frontiers (frontiersin.org) for open-access journal coverage, and AnswerThis for gap discovery. Do not claim to have searched a platform that was unavailable or that returned no usable tool result.
3. Use web search, the browser, or configured academic connectors as appropriate. Record the platform, search string, search date, filters, and access limitation in the Verification Log (Section 4a) as you go — not reconstructed from memory afterward.
4. Verify every cited paper using a resolvable DOI, PMID, publisher page, or the platform's stable record. Do not rely on snippets alone when a fuller record is reachable via web_fetch. Label preprints clearly and do not present them as peer reviewed.
5. Never fabricate authors, titles, journals, years, DOIs, PMIDs, results, or database coverage. If a record cannot be verified, exclude it or mark it **Unverified—excluded from evidence claims**.
6. Separate correlation from causation; note sample, design, dataset, benchmark, external-validity, reproducibility, and conflict-of-interest limitations when material.
7. Treat a research gap as genuine only when recent evidence supports what has been studied and what remains missing. A missing citation is not evidence of a gap — absence of evidence in a limited search is not evidence of absence.
8. Keep the four-month feasibility assessment concrete: data access, established methods, compute, ethics, skills, evaluation plan, and milestones.
9. Match the response language to the user's (Arabic or English); keep dimension names, section headers, and identifiers (DOI, PMID) in their standard form regardless of response language.

## Toolkit map — matching the right tool to each part of this task

Evaluating and choosing between research ideas draws on several distinct sub-tasks, and no single search engine covers all of them. Use this map to pick the right one for each part, rather than defaulting to one platform for everything:

| Phase | Purpose | Tools |
|---|---|---|
| Literature search & discovery | Broad search for studies and references | Google Scholar, Semantic Scholar, Frontiers (frontiersin.org) |
| Evidence synthesis | Answers and comparisons grounded in aggregated findings | Consensus, Elicit |
| Citation-network mapping | Tracing related work, influential authors, and how crowded a topic already is | ResearchRabbit, Connected Papers |
| Source/PDF comprehension | Digesting the user's own uploaded papers or a candidate idea's key sources, Q&A over them | NotebookLM / Gemini Notebook, SciSpace |
| Qualitative data analysis | When the idea's data is interviews, text, or other qualitative material rather than quantitative | NVivo, ATLAS.ti |
| Academic writing & editing | Downstream of the evaluation, once an idea is chosen and being written up | Paperpal, Writefull, Jenni AI |

In this skill, only call whichever of these are actually connected as a tool in this session (per the Zero-Fabrication Protocol — never claim to have used one that wasn't actually invoked). For the rest, name the tool and what it's for so the user can use it in their own workflow; don't simulate its output. Whatever the source, AI-assisted output here — summaries, syntheses, comparisons, network maps — supports the researcher's judgment and never substitutes for it: every reference and result this skill reports back must still pass the verification steps above.

### Comparing multiple ideas to pick the best one

When the user gives two or more candidate ideas and asks which to pursue:

1. Run Track A and Track B independently for each idea (reuse a shared literature search across ideas where the underlying field overlaps, but keep each idea's matrix and scores separate).
2. Present a single comparison table: idea title, Track A score/verdict, Track B score/verdict, biggest design risk (if any), biggest evidence limitation (if any).
3. Recommend the strongest overall idea, but flag it explicitly if the top Track A idea and the top Track B idea differ — the user may reasonably prefer either depending on whether they value a clean design or a well-evidenced gap more, and that trade-off is theirs to make, not a call to hide by picking one score to report.

## Track A — Idea & Design Quality (run first, no search tools required)

This track judges the idea on its own logical and methodological merits — could a competent reviewer approve this design as written, independent of whether the literature happens to support it. Do this before or in parallel with Track B; it never blocks on tool availability, and a weak Track A score is often the more actionable feedback for the user.

### A1. Design dimensions (score 0–100 across four 25-point dimensions)

| Dimension | Questions |
|---|---|
| Question clarity & framing (0–25) | Is the research question specific, answerable, and non-circular? Does the title actually match the question being asked? Is scope (population, setting, outcome) unambiguous? |
| Method–question fit (0–25) | Is the proposed method (dataset, model/analysis, comparison group, statistical or computational approach) actually suited to answering this question, or is it a mismatch (e.g., a method that can't isolate the claimed effect, wrong unit of analysis, no adequate control/baseline)? |
| Variable & measurement design (0–25) | Are the independent/dependent variables (or inputs/outputs, for an AI system) well-defined and measurable? Are confounders, biases, or leakage risks (e.g., data leakage between train/test, batch effects, population stratification) identified and addressed in the design? |
| Internal coherence & robustness (0–25) | Does the design hang together logically end to end — question → data → method → expected output → interpretation? Are there single points of failure (e.g., one dataset with no fallback), untestable claims, or steps that don't follow from each other? |

Give a one-paragraph justification per dimension, cite the specific part of the idea it applies to, and flag the single most important design risk explicitly (e.g., "no negative control condition," "outcome variable is not operationalized," "AI component is decorative, not load-bearing"). This is Claude's own methodological judgment — label it as such, don't imply it's a literature-verified fact.

### A2. Concrete design recommendations

Regardless of score, list 2–5 specific, actionable changes that would most improve the design (not generic advice — tied to what's actually weak in this idea): e.g., a missing control group to add, a variable to redefine, a confound to control for, a more appropriate model/analysis choice, or a step that needs to be split in two. If the idea is already well-designed, say so briefly rather than manufacturing filler suggestions.

### A3. Track A verdict

One line: **Well-designed**, **Workable with the changes above**, or **Needs redesign before proceeding** — independent of Track B's evidence-based verdict. The two tracks can disagree (a well-designed idea can still turn out to already be well-covered by the literature, and a poorly-designed one can still target a genuine gap).

## Track B — Evidence-Grounded Evaluation (workflow)

### 1. Initial assessment

Assess:

- **AI relevance**: classify as AI as tool, AI as subject, AI-enhanced method, or unrelated; explain the classification.
- **Future significance**: rate long-term scientific importance from 1–10 and justify it with specific verified trends and likely practical or theoretical contributions — cite the trend, don't just assert it.
- **Gap status**: classify as genuine and evidence-backed, already addressed, hallucinated/pseudoproblem, or trivial/not significant. Explain the logical criteria and distinguish an untested claim from a demonstrated gap.

### 2. Initial score

Score the idea from 0–100 using exactly four 25-point dimensions:

| Dimension | Questions |
|---|---|
| Scientific novelty (0–25) | Is the contribution genuinely new, or only incremental? |
| Four-month feasibility (0–25) | Can the study be completed with the stated data, methods, skills, and approvals? |
| Evidence-grounded gap (0–25) | Is the gap supported by at least three recent peer-reviewed sources? |
| Academic significance (0–25) | Would the result advance theory, method, or practice? |

Also complete this checklist: data availability confirmed; methods established and accessible; ethics pathway clear; required skills/tools attainable; four-month timeline realistic. Report confidence as High, Medium, or Low and explain it. This is a *pre-literature-search* estimate — expect it to move in Phase 4.

### 3. Literature search

Construct focused query variants from the idea's key concepts, population/domain, method, outcome, and limitation. Search at least four platforms; use all eight named platforms (Elicit, Semantic Scholar, Consensus, PubMed, Scopus/Web of Science, ResearchRabbit/Connected Papers, Frontiers, AnswerThis) when realistically accessible and relevant. For each platform, identify up to five most relevant verified papers from 2022–2026, rather than padding the list with weak or tangential sources.

For every included paper, extract — only from what the retrieval actually returned:

- Full citation, authors, journal or venue, year
- DOI or PMID and a resolvable verification link
- Study design, population/data, and method when available
- Two-sentence finding and relevance to the proposed idea (paraphrased, not quoted)
- Whether it supports, narrows, or contradicts the claimed gap
- Key limitation, bias, or funding/conflict note when reported

If the requested 35+ papers cannot be responsibly verified, report the actual number and why. Never manufacture a quota — a shorter, fully-verified list beats a longer, partly-invented one.

### 4. Critical re-evaluation

Compare the initial score with the evidence. State whether it was accurate, overestimated, or underestimated; provide an adjusted score when warranted and tie every change to a specific verified source from the matrix, not to general impression. Reclassify the gap as still underexplored, partially addressed (state the missing part), already solved (cite the relevant papers), or fundamentally flawed.

#### 4a. Verification Log (mandatory, produced during Phase 3, checked here)

Before drafting Section 4 of the final report, produce a short internal log — carry it into the report's literature-matrix section — with one row per search actually executed:

| Platform | Query string | Date | Filters | Result | Papers used from it |
|---|---|---|---|---|---|

Then run the reconciliation pass from the Zero-Fabrication Protocol (item 4): dimension scores sum correctly, source counts match, every platform claimed in the confidence statement appears in this log.

If the final score is below 70, propose exactly three feasible alternative titles. For each give the specific evidence-backed gap, 2–3 supporting verified citations, an AI connection when relevant, feasibility (High/Medium/Low), and an estimated score.

### 5. Quality assurance (run before showing the report to the user)

Before finalizing, check that:

- Every factual literature claim has a citation, and that citation appears in the Verification Log.
- Every included paper has a DOI, PMID, or stable publisher/record link that was actually checked this session.
- Search strings, dates, platforms, and access limitations are documented in Section 4a, not summarized from memory.
- Peer-reviewed status and preprint status are distinguished.
- Predatory, duplicate, retracted, or unverifiable sources are flagged or excluded.
- No causal language is used for correlational evidence.
- The score reflects evidence quality, not the number of citations.
- The four Track B dimension scores sum to the reported total; the source count is arithmetically correct.
- The four Track A dimension scores sum to the reported Track A total, and Track A's verdict is not silently merged into or averaged with Track B's score — they stay two separate numbers.
- Uncertainty and limitations are visible rather than hidden.

If any check fails, fix the underlying content — do not edit the checklist to pass.

## Required final report structure

Use this structure unless the user requests another format, or the request only warranted the lightweight "quick sanity check" path under Scaling, in which case give the equivalent content in shorter form and note that the full structure is available on request.

# Research Idea Evaluation: [short title]

## 1. Executive summary
Keep to 200 words maximum. State both verdicts side by side: the Track A design verdict and score, and the Track B recommendation, initial/adjusted score, and confidence — plus gap status and the most important evidence limitation.

## 2. Track A — Idea & design quality
The four A1 dimension scores, total `/100`, the per-dimension justification and flagged main design risk, the A2 recommendations, and the A3 verdict.

## 3. Phase 1 — Initial assessment (Track B)
Cover AI relevance, future significance (1–10), gap classification, and assumptions.

## 4. Phase 2 — Scoring and feasibility (Track B)
Include the four dimension scores, total `/100`, confidence, checklist, rationale, and a four-month milestone outline.

## 5. Phase 3 — Literature search and matrix (Track B)
Document platforms, dates, query strings, filters, and unavailable platforms (the Verification Log from 4a). Provide one subsection per platform and a table with the verified papers, identifiers, findings, relevance, gap implication, and limitations.

## 6. Phase 4 — Critical re-evaluation (Track B)
Compare scores, give the adjusted score if needed, and state the final gap reality check.

## 7. Alternative titles
Include only when the final Track B score is below 70, or when Track A's verdict is "Needs redesign before proceeding"; otherwise state why alternatives are unnecessary. When triggered by Track A, alternatives should address the design flaw, not just chase a literature gap.

## 8. References
Use APA 7th style with DOI/PMID or stable verification links. Do not list sources that were not used or verified.

## 9. Confidence statement
Use this form, adapting the numbers truthfully: "This evaluation is based on **[X] verified sources** from **[Y] databases/platforms searched on [date]**. Hallucination risk: **[Low/Medium/High]**, because [brief justification tied to the Verification Log]. Track A's design assessment is Claude's own methodological judgment, not a literature-verified claim."

## Decision language

Give two lines, not one:
- **Design verdict (Track A):** Well-designed / Workable with changes / Needs redesign — with the single biggest design fix if not "Well-designed."
- **Evidence verdict (Track B):** **Proceed**, **Proceed after narrowing**, **Revise substantially**, or **Do not proceed** — with the smallest next step that would reduce the largest uncertainty, such as confirming dataset access, preregistering an outcome, running a pilot, or completing a targeted systematic search.

When evidence is sparse or platform access is restricted, lower Track B confidence rather than inflating the score. The goal is a reproducible, defensible evaluation on both tracks — not a guaranteed positive verdict on either.
