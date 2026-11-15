---
name: clean-invisible-chars
description: Strip invisible/hidden Unicode characters (zero-width spaces, BOM, bidi control marks, variation selectors, non-breaking spaces, smart quotes) from text that was copied from an AI chat, Word, Google Docs, or a web page. Use this whenever the user reports "hidden characters", "weird invisible marks", "watermark-like characters", pasted text breaking code/LaTeX/JSON, mojibake-looking gaps, or text that looks fine but fails string comparison, grep, or diff. Also trigger for requests to "clean this text", "make this plain text", "remove formatting artifacts from this paste", or "sanitize this text for pasting into X". Works on plain text and inside code files, JSON, CSV, or markdown that the user pastes or uploads.
---

# Clean Invisible Characters

## What this actually removes

There is no single "AI watermark" character. What people run into is a
grab-bag of invisible or control Unicode characters that leak in when text
is copied out of rich-text sources (chat UIs, Word, Google Docs, PDFs,
web pages). This skill detects and removes the specific, named ranges
below — it never silently rewrites visible text.

Removed unconditionally (always invisible, never carries meaning in the
visible text):
- `U+200B` Zero Width Space
- `U+200C` Zero Width Non-Joiner
- `U+200D` Zero Width Joiner
- `U+2060` Word Joiner
- `U+FEFF` Zero Width No-Break Space / BOM
- `U+00AD` Soft Hyphen
- `U+200E`, `U+200F` Left-to-Right / Right-to-Left Marks
- `U+202A`–`U+202E` Bidi Embedding/Override controls
- `U+2066`–`U+2069` Bidi Isolate controls
- `U+2061`–`U+2064` Invisible math operators (invisible times, plus, etc.)
- `U+FE00`–`U+FE0F` Variation Selectors
- `U+180E` Mongolian Vowel Separator
- `U+FFF9`–`U+FFFB` Interlinear annotation controls
- `U+FFFE`, `U+FFFF` Non-character codepoints

Removed only when the user opts in, because they are visible/semantic
and some workflows need them kept as-is:
- `U+00A0` Non-breaking space → normal space
- `U+2028`, `U+2029` Line/Paragraph separator → `\n`
- Curly quotes (`\u2018\u2019\u201C\u201D` etc.) and en/em dashes → straight
  quotes and `-`

**Never touched**: combining marks used by real scripts (Arabic tashkeel,
Hebrew niqqud, Latin diacritics, Zalgo-style combining marks a user added
on purpose), emoji, or any visible character. This skill removes control
characters, not diacritics — don't add diacritic ranges to the strip list
even if asked, since that would corrupt real text in Arabic, Vietnamese,
Hebrew, etc. If someone's actual concern turns out to be a base64
watermark or statistical token-selection watermark rather than a literal
character, tell them plainly: those aren't literal characters you can
strip from text, and there is no reliable tool to detect or remove them
after the fact.

## How to run it

Prefer running the bundled script over hand-writing regex inline — it's
already tested against the full range list above and reports exactly
what it removed.

```bash
python3 scripts/clean_text.py path/to/input.txt
```

- Prints the cleaned text to stdout by default.
- Add `-o path/to/output.txt` to write to a file instead of stdout.
- Add `--report` to print a per-character-type removal count to stderr
  (useful to show the user what was actually found).
- Add `--keep-nbsp`, `--keep-separators`, or `--smart-quotes` to adjust
  the opt-in behaviors described above (smart-quotes is off by default;
  the other two opt-in categories are ON by default — pass the `--keep-*`
  flags to leave them alone).
- Reads stdin if no input file is given: `cat file.txt | python3 scripts/clean_text.py`.

For a single pasted snippet inside the conversation (no file involved),
it's fine to run the same logic inline with the container's Python
rather than creating a file first — pipe the text through
`python3 -c` calling the same character ranges, or write it to a temp
file and call the script. Either way, always report back to the user
what was found and removed (or confirm the text was already clean) —
don't just silently return cleaned text with no explanation.

## When the user wants this as a reusable tool, not a one-off

If the user wants to clean text repeatedly themselves (not just this one
paste), point them to — or build — an interactive page instead of running
this skill: a self-contained HTML tool with an input/output textarea
that runs the same logic client-side is a better fit for repeat personal
use than asking them to come back to Claude each time. Use this SKILL.md's
character list as the source of truth for that page's cleaning logic so
the two stay consistent.

## Output expectations

- If nothing was found, say so plainly — don't claim to have "cleaned"
  text that was already clean.
- If something was found, name what was found (using the names above,
  not raw codepoints) and how many, before or alongside handing back the
  cleaned text.
- Never claim this removes an "AI detection watermark" or any statistical
  watermarking scheme — it only removes the literal invisible characters
  listed above.
