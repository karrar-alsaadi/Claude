---
name: "arabic-rtl-mixed-text"
description: "Use whenever a response, file, or artifact contains Arabic, or mixed Arabic and English text, so it displays RTL and stays readable, using the fewest possible invisible marks and no decorative stretching."
---

# Arabic / English mixed text: correct RTL display, minimal marks

## Goal
Text containing Arabic is RTL overall. English fragments (scientific terms, names, gene symbols, file names, numbers with units) stay LTR inside it and the line must read naturally, e.g.:

`اسم الطالب: Karrar ، اسم الجامعة: Babylon`

## Core principle: least marks possible
Write clean text first. Add a direction mark only where the display would otherwise break. Most lines need none.

### Allowed marks, in order of preference
1. **No mark** (default). Use it when the English run sits between Arabic words with spaces only, or at the end of the line.
2. **One RLM (U+200F)**, only in these cases:
   - an English/number run is followed by punctuation and then more Arabic (e.g. `Karrar<RLM> ، بعدها`);
   - a line or list item starts with an English word inside an Arabic paragraph.
   Never put two marks in a row. Never add RLM to lines with no Arabic.
3. **LRI/PDI isolates (U+2066/U+2069), last resort**, only for an English phrase that contains its own punctuation or brackets and still renders wrong after rule 2. Do not use RLI/PDI around whole Arabic lines unless a specific line is proven broken.

## Punctuation and stretching: one symbol, never a run
- **Tatweel (kashida) U+0640:** do not use it for decoration or emphasis. Never write runs like `ـــــ`. If one is unavoidable (e.g. justification in a title), use exactly one `ـ`.
- Collapse repeated punctuation to one: `!!!` becomes `!`, `؟؟؟` becomes `؟`, `......` becomes `…` or `.`, `-----` or `=====` separators become one `-` or a markdown rule `---` on its own line.
- No decorative symbol strings (`***`, `~~~`, emoji chains) inside Arabic prose.
- No repeated spaces; no leading/trailing spaces on lines.

## Other rules for chat text
1. Reply in the language the person wrote in. Keep scientific terms in English inside Arabic sentences; technical answers follow the stored preference for English.
2. Use Arabic punctuation after Arabic words: `،` `؟` `؛`. Use Latin punctuation only inside English fragments.
3. Numbers: Western digits; attach units with a no-break space (U+00A0), e.g. `5 µm`.
4. Code, file paths, URLs, commands go in code formatting, on their own lines, with no Arabic inside the code block. Arabic explanation stays outside.
5. Lists: one idea per item. `label: value` pairs one per line, Arabic label, English value after the colon.
6. Tables with Arabic: 2-3 columns, Arabic label first, short English values; avoid mixed directions in one cell.
7. Do not strip U+200F or U+2066 to U+2069 from Arabic text when cleaning. Remove only zero-width space (U+200B), BOM (U+FEFF), stray variation selectors, and duplicated direction marks.

## HTML / artifacts
- `<html lang="ar" dir="rtl">`; use `unicode-bidi: plaintext` on free-text blocks that vary in direction.
- Wrap English fragments in `<bdi>` (preferred over inline marks); code and pre blocks `dir="ltr"`, `text-align:left`.
- Logical CSS properties (`margin-inline-start`, `padding-inline-end`, `text-align:start`).
- Fonts: `'Noto Naskh Arabic','Cairo','Tajawal',system-ui,sans-serif`, line-height at least 1.7. No `text-decoration` or letter-stretching that mimics tatweel.
- Theme: dark background with high-contrast text (white, yellow, bright accents); avoid white or light interfaces.

## Files
- DOCX: paragraph `w:bidi`, run `w:rtl` on Arabic runs, complex-script font set, right alignment; English runs stay LTR. No marks needed in the text itself.
- PDF/plots: `import arabic_reshaper; from bidi.algorithm import get_display; get_display(arabic_reshaper.reshape(raw))` per Arabic string, with a TTF Arabic font. No marks needed.
- Plain `.md`/`.txt`: apply the chat rules.

## Optional helper (scripts that generate text)
```python
import re
RLM = "\u200f"
ARABIC = re.compile(r"[\u0600-\u06FF]")
# English/number run directly followed by punctuation and then Arabic
NEEDS_RLM = re.compile(r"([A-Za-z0-9][A-Za-z0-9_\-./+]*)(?=\s*[\u060c\u061b\u061f:.)\]]\s*[\u0600-\u06FF])")

def normalize(text: str) -> str:
    text = re.sub(r"\u0640+", "\u0640", text)            # tatweel runs -> one
    text = re.sub(r"([!\u061f?.,\u060c])\1+", r"\1", text) # repeated punctuation -> one
    text = re.sub(r"([-=_*~])\1{2,}", r"\1", text)       # separator runs -> one
    text = re.sub(r"\u200f{2,}", RLM, text)               # duplicate RLM -> one
    text = re.sub(r"[ \t]{2,}", " ", text)                # repeated spaces
    return text

def rtl_fix(line: str) -> str:
    if not ARABIC.search(line):
        return line
    line = NEEDS_RLM.sub(lambda m: m.group(1) + RLM, normalize(line))
    return RLM + line if line and not ARABIC.match(line[0]) and ARABIC.search(line) and line[0].isascii() and line[0].isalnum() else line
```

## Self-check before sending
- Could any mark be removed without breaking the line? Remove it.
- Any run of tatweel, repeated punctuation, or separator characters? Collapse to one.
- Does each `label: English value` pair read in the right order?
- Are code, paths and URLs in code formatting, separate from Arabic prose?
- HTML: is `dir="rtl"` set and are English spans in `<bdi>`?