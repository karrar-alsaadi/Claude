---
name: paper-find-text
description: Verify whether a quote, sentence or paragraph really appears in an uploaded paper (PDF, DOCX, TXT) and where. Classifies the text as VERBATIM, NEAR-VERBATIM, REPHRASED, or NOT FOUND, reports the exact page number (PDF page and printed journal page), and builds a citation to the paper's lead (first) author, flagging when the passage is itself attributed to other researchers. Use this skill whenever the user uploads a paper and gives a sentence or quote to check, asks "is this text in the paper", "where does the paper say this", "find this sentence", "which page", "was this reworded or copied", "verify this quote/citation", "is this claim actually in the source", or wants a page-accurate citation for a passage. Also use it to catch fabricated or misattributed quotes, even if the user never says "verify". Arabic requests such as "ابحث عن النص في الملف" or "هل هذا الكلام موجود في الورقة" should trigger it too.
---

# paper-find-text

Check whether a piece of text truly comes from an uploaded paper, decide how faithfully it reproduces the source, locate it by page, and produce a correct citation.

The whole point is trust: a user relies on this answer to decide whether they can quote or cite a source. A wrong page number or a "found" verdict on text that is not there is worse than saying "not found". So report only what the file supports, and say so plainly when the evidence is weak.

## Inputs

- **File**: an uploaded paper. It is at `/mnt/user-data/uploads/` (check with `ls`). PDF is the normal case; DOCX/TXT work with limits (see "Limits").
- **Text to check**: a sentence, quote or paragraph, in any language.

If either is missing, ask for it in one short message. If several files are uploaded and the user did not say which one, check the text against each and report per file.

## Workflow

### 1. Run the search script

```bash
python /mnt/skills/user/paper-find-text/scripts/find_text.py "<file>" --query "<text>" --per-sentence
```

(If the skill is installed elsewhere, use the path where this SKILL.md lives.)

- Use `--per-sentence` for anything longer than one sentence. Users often paste a paragraph where some sentences are verbatim and others are reworded; the whole-passage score hides that.
- For long queries, write the text to a file and use `--query-file`.
- The script prints JSON. It normalizes case, hyphenation at line breaks, ligatures, curly quotes, spacing and Arabic diacritics, so a match is not lost to typography.
- If `warnings` says the PDF is scanned, rerun with `--ocr --lang eng` (or `--lang eng+ara` for mixed Arabic/English) and mention in the answer that the text came from OCR, so small character errors are possible.

### 2. Judge each result. Do not just forward the script's label

The script measures similarity; you decide meaning. Read the returned `passage` / `original_text` yourself.

| Verdict | Meaning | Evidence you need |
|---|---|---|
| **VERBATIM** | The words are the paper's own | Script status `VERBATIM` (exact match after normalization) |
| **NEAR-VERBATIM** | Same sentence with small edits (a dropped word, changed tense, altered number, inserted bracket) | High `sequence_similarity`; list the edits from `word_changes` |
| **REPHRASED** | Different wording, same meaning and same claim | You read the candidate passage and the ideas, numbers and qualifiers match. The script labels these `CANDIDATE_REPHRASE` or `WEAK_CANDIDATE` (paraphrases with very different vocabulary land here); always read the passage to confirm |
| **PARTIAL / DISTORTED** | Related passage exists but the claim is stronger, weaker, or different (e.g. "may reduce" became "reduces", different number, different population) | Explain exactly what differs |
| **NOT FOUND** | Nothing in the file supports it | Weak candidates only, after a check that extraction was not the problem |

Rules that keep the verdict honest:
- **Check numbers, units, and hedges** (`may`, `suggests`, `significantly`). The script lists `numbers_in_query_not_in_passage`; a changed figure means the text is not a faithful reproduction, even if the words are otherwise close.
- **Rephrased needs a meaning check, not a vocabulary check.** High keyword overlap with a different claim is a false match. If you are unsure, say "possibly rephrased of page X" and show the passage so the user can decide.
- **Do not claim NOT FOUND too fast.** Text may sit in a table, figure caption, footnote, supplementary file, or an image. If the extraction looked poor (garbled columns, very short pages), say the search may have missed it and suggest `--ocr`.
- **Never fill gaps from memory.** If the file does not contain it, do not confirm it because the claim sounds like something the paper would say, or because you know the literature.
- If the same text appears more than once, report all occurrences (the script returns up to 5).
- A hit inside the reference list (`reference_list_starts_on_pdf_page`) is a bibliography entry and not a statement by the authors. Say so.

### 3. Report the page correctly

The script returns two numbers, and they often differ:
- `pdf_page`: position in the PDF file (page 1 = first sheet, including cover/title pages).
- `printed_page` / `page_label`: the number printed on the page, i.e. the journal pagination. `printed_page_source` says whether it was read from the header/footer or inferred from neighbouring pages.

Citations use the **printed page**, so give it when available. Always also give the PDF page so the user can jump to it. If the printed number was only inferred, say "(inferred)". If the passage spans two pages, give the range (e.g. pp. 412-413). If no printed number can be found, cite the PDF page and say it is a PDF page.

### 4. Identify the paper and cite the lead author

Run `--meta-only` (or use the `metadata` block already returned) and read `first_page_text` to get the title, journal, year, DOI and the author list. PDF `Author` metadata is frequently wrong (uploader name, software name), so trust the printed title page, not the metadata.

**Cite the primary (lead) author**, meaning the first-listed author of the paper being checked, not the co-authors:
- Single author: `Surname (Year)`
- Two authors: `Surname & Surname (Year)` (only the first is "lead", but two-author convention lists both)
- Three or more: `Surname et al. (Year)`
- Add the page: `Surname et al. (Year, p. 412)`; range `pp. 412-413`.
- If the first author is not the corresponding author, mention the corresponding author separately, only when the title page shows it. Do not swap them.
- If the author list or year cannot be read from the file, say what is missing. Do not guess names or years.

**Watch for secondary attribution.** The passage may report someone else's finding, for example "Smith et al. (2019) showed that..." or "...[12]". In that case:
1. Cite the uploaded paper as the place where the text appears (lead author, year, page).
2. State that the paper attributes the claim to another work, quoting the in-text marker from `citation_markers_in_passage`.
3. If the user needs to cite the finding itself, the original study is the right source. Look up the marker in the paper's reference list, give the reference entry as printed, and recommend citing it as "Original (Year), as cited in Lead (Year, p. X)" unless the user has read the original. Do not build details of the original study from memory.

This keeps the user from crediting the wrong researcher, which is the most common citation error this skill exists to prevent.

### 5. Answer format

Write the answer in the user's language (Arabic, English, or mixed) but keep the quoted passage in its original language. Lead with the verdict. Keep it compact:

```
**Verdict:** VERBATIM | NEAR-VERBATIM | REPHRASED | PARTIAL | NOT FOUND
**Location:** p. 412 (PDF page 5)   [printed page read from footer]
**Paper:** Surname et al. (2021). Title. Journal.
**Citation:** (Surname et al., 2021, p. 412)

**Passage in the paper:**
> "...exact text as it appears, with original casing..."

**Differences from your text:** (only for near-verbatim / rephrased / partial)
- your "significantly reduced" -> paper "reduced" (the word "significantly" is not in the paper)
- your "45%" -> paper "43%"

**Note:** (only if needed) passage is attributed to Jones et al. (2018) inside the paper; cite as ...
```

For multi-sentence input, give one compact line per sentence (verdict + page), then expand only on the ones that are not verbatim. For NOT FOUND, say which parts of the file were searched (page count, text or OCR) and what the closest passage was, if any, without presenting it as a match.

Quote the paper's text only as much as needed to prove the match; a sentence or two is enough.

## Limits (state them when they matter)

- **DOCX/TXT**: no reliable page numbers. DOCX is converted to PDF when LibreOffice exists, and the page numbers then reflect that layout and not Word's; say so.
- **Scanned PDFs**: need `--ocr`; OCR errors can create or hide small differences.
- **Two-column layouts** can reorder text in extraction; a sentence split by a column break may show as near-verbatim rather than verbatim. Check `word_changes` before blaming the user's text.
- **Figures, images and equations** are not searchable text.
- **Titles and abstracts repeated on several pages** (headers, preprint cover sheets) can produce duplicate hits; report the body-text occurrence first.
- Arabic text: extraction from Arabic PDFs sometimes stores letters in visual order or reversed. If an Arabic query gets no hit but the paper clearly contains it, try `--ocr --lang ara` before concluding.

## Example

**User:** (uploads `smith2021.pdf`) Is this in the paper? "Microglial activation precedes tau pathology in the hippocampus."

**Process:** run the script, get status `CANDIDATE_REPHRASE` on PDF page 6; read the passage: "Activated microglia were observed before the appearance of hyperphosphorylated tau in hippocampal sections." Meaning matches, wording differs. Title page: first author Smith, 2021; footer shows page 1873.

**Answer:** REPHRASED, p. 1873 (PDF page 6). The paper says activated microglia appeared *before* hyperphosphorylated tau in hippocampal sections. Your sentence generalizes "hyperphosphorylated tau" to "tau pathology" and drops "sections" (a sampling detail). Cite as (Smith et al., 2021, p. 1873), and paraphrase rather than quote it.
