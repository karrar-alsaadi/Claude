---
name: scientific-paraphrasing
description: Paraphrase English academic/scientific sentences and paragraphs in medical, biological, biochemistry, and neuroscience fields (e.g. Alzheimer's disease, neurodegeneration, molecular biology text) while preserving exact meaning, technical terms, gene/protein names, and abbreviations. Use this skill whenever the user asks to paraphrase, rewrite, reword, or rephrase scientific/academic English text, wants to avoid plagiarism-detector flags on a manuscript sentence, or asks for "academic paraphrasing", "scientific rewriting", "إعادة صياغة علمية", or similar, even if they don't explicitly mention this skill by name.
---

# Scientific Paraphrasing (Medical / Bio / Neuroscience)

Paraphrase English scientific text with controlled vocabulary level, controlled tense usage, and strict preservation of technical content. Optimized for medical, biological, biochemistry, and neuroscience writing (e.g. Alzheimer's disease / neurodegeneration manuscripts).

## Non-negotiable priorities (never violate)

1. **Exact meaning** — zero change in scientific content.
2. **Logical flow** — preserve the sequence and structure of ideas.
3. **Keywords unchanged** — technical terms stay exactly as written.
4. **Abbreviations unchanged** — AD, Aβ, APP, BACE1, TREM2, CSF, MRI, etc. Keep the first-use definition if the original defines it.
5. **Compound / gene / protein names unchanged** — e.g. amyloid-beta, tau protein, microglia, astrocytes, interleukin-6, tumor necrosis factor-alpha.
6. **Latin species names unchanged** — e.g. Mus musculus, Homo sapiens, Escherichia coli.
7. **Numbers and percentages unchanged** — never round unless asked; keep exact precision.
8. **Citations unchanged** — (Author, Year) stays exactly as given.
9. **Length** — paraphrase stays within ±10% of the original word count.

## Vocabulary level distribution

- ~90% B1–B2 level words (clear, intermediate, comprehensible)
- ~7% A1–A2 level words (basic, simple)
- ~3% C1–C2 level words (advanced, only when scientifically necessary — i.e. when no simpler synonym exists for a precise concept)

Do not inflate the register with unnecessary advanced vocabulary. Prefer the plainest word that still conveys the exact scientific meaning.

## Allowed tenses only

- **Past Simple** — completed actions: methods ("We analyzed…", "The samples were collected…"), results ("The treatment reduced…"), prior studies ("Smith et al. (2023) reported…").
- **Present Simple** — established facts, generalizations, figure/table descriptions ("Alzheimer's disease is a neurodegenerative disorder…", "Figure 1 shows…").
- **Present Perfect** — connecting past research to the present state of knowledge ("Several studies have investigated…", "Research has demonstrated that…").

### Strictly prohibited
- Past Perfect (had + past participle) — except when strictly necessary for chronological sequence.
- Future tenses (will, shall) — except in a future-recommendations section.
- Continuous/progressive forms (is doing, was analyzing) — avoid unless absolutely necessary.
- Complex conditionals (would have done, could have been).

## Style rules

- Clear, direct sentences: Subject + Verb + Object.
- Prefer active voice when it stays clear: "We measured…" over "Measurements were performed…".
- No rhetorical, literary, narrative, or storytelling phrasing.
- No colloquial or informal words. No archaic/obsolete words.
- Use academic connectors naturally: However, Therefore, Consequently, Furthermore, Moreover, In addition, In contrast, Similarly, Notably, Specifically, Particularly, Importantly.
- Output must read naturally and human-written, not mechanical or robotic.

## Process to follow for every paraphrase

1. Read the source sentence/paragraph fully; understand the complete meaning first.
2. Mark the elements that cannot change: technical terms, scientific/species names, abbreviations, numbers, citations.
3. Rebuild the sentence:
   - Swap non-technical words for B1–B2 synonyms.
   - Convert passive↔active voice where it improves clarity, without changing meaning.
   - Reorder clauses/elements where useful, while preserving logical sequence.
   - Merge or split sentences if it improves clarity, staying within the ±10% length budget.
4. Review the result against the checklist below before finalizing.

## Final checklist (verify before responding)

- [ ] Meaning is 100% preserved — no scientific content added, dropped, or altered.
- [ ] Only Past Simple / Present Simple / Present Perfect are used (no banned tenses).
- [ ] Vocabulary roughly follows the 90% B1-B2 / 7% A1-A2 / 3% C1-C2 distribution.
- [ ] All technical terms, gene/protein names, Latin names, abbreviations, numbers, and citations are unchanged.
- [ ] No grammatical errors.
- [ ] Length is within ±10% of the original.
- [ ] Reads naturally, not mechanically.

## Output format

Unless the user asks otherwise, return only the paraphrased text (no restatement of the original, no meta-commentary). If the user gives a full paragraph, paraphrase it as a coherent paragraph rather than sentence-by-sentence in isolation. If a request would require breaking one of the non-negotiable priorities to satisfy the ±10% length or vocabulary targets, keep the priorities and note the trade-off briefly.

## Worked examples

**Original:** "The investigation of the pathological mechanisms underlying Alzheimer's disease progression has been conducted by numerous researchers."
**Paraphrased:** "Many researchers have investigated the pathological mechanisms underlying Alzheimer's disease progression."

**Original:** "It was observed that the administration of the compound resulted in a significant reduction in amyloid-beta plaque formation."
**Paraphrased:** "The compound administration significantly reduced amyloid-beta plaque formation."

**Original:** "The microglial cells, which are the resident immune cells of the central nervous system, were found to be activated in the vicinity of the plaques."
**Paraphrased:** "Microglial cells, the resident immune cells of the central nervous system, were activated near the plaques."
