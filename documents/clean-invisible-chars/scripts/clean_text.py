#!/usr/bin/env python3
"""
clean_text.py — strip invisible/control Unicode characters that commonly
leak into text copied from chat UIs, Word, Google Docs, or web pages.

Usage:
    python3 clean_text.py input.txt
    python3 clean_text.py input.txt -o output.txt
    python3 clean_text.py input.txt --report
    cat input.txt | python3 clean_text.py

See SKILL.md in this skill's directory for the full rationale behind
each character range, and for what is deliberately never touched
(combining marks / diacritics used by real scripts).
"""

import argparse
import re
import sys

# Always-removed: characters that are invisible in every context and
# never carry meaning in the *visible* text.
ALWAYS_STRIP = [
    ("Zero Width Space", re.compile("\u200B")),
    ("Zero Width Non-Joiner", re.compile("\u200C")),
    ("Zero Width Joiner", re.compile("\u200D")),
    ("Word Joiner", re.compile("\u2060")),
    ("Zero Width No-Break Space / BOM", re.compile("\uFEFF")),
    ("Soft Hyphen", re.compile("\u00AD")),
    ("Left-to-Right / Right-to-Left Mark", re.compile("[\u200E\u200F]")),
    ("Bidi Embedding/Override Controls", re.compile("[\u202A-\u202E]")),
    ("Bidi Isolate Controls", re.compile("[\u2066-\u2069]")),
    ("Invisible Math Operators", re.compile("[\u2061-\u2064]")),
    ("Variation Selectors", re.compile("[\uFE00-\uFE0F]")),
    ("Mongolian Vowel Separator", re.compile("\u180E")),
    ("Interlinear Annotation Controls", re.compile("[\uFFF9-\uFFFB]")),
    ("Non-character Codepoints", re.compile("[\uFFFE\uFFFF]")),
]

NBSP_RE = re.compile("\u00A0")
SEPARATORS_RE = re.compile("[\u2028\u2029]")

SMART_SINGLE_QUOTES_RE = re.compile("[\u2018\u2019\u201A\u201B]")
SMART_DOUBLE_QUOTES_RE = re.compile("[\u201C\u201D\u201E\u201F]")
SMART_DASHES_RE = re.compile("[\u2013\u2014]")


def clean(text: str, keep_nbsp: bool = False, keep_separators: bool = False,
          smart_quotes: bool = False):
    """Returns (cleaned_text, report) where report is a list of
    (label, count) tuples for anything actually found/changed."""
    report = []
    result = text

    for label, pattern in ALWAYS_STRIP:
        matches = pattern.findall(result)
        if matches:
            report.append((label, len(matches)))
        result = pattern.sub("", result)

    if not keep_nbsp:
        matches = NBSP_RE.findall(result)
        if matches:
            report.append(("Non-Breaking Space -> regular space", len(matches)))
        result = NBSP_RE.sub(" ", result)

    if not keep_separators:
        matches = SEPARATORS_RE.findall(result)
        if matches:
            report.append(("Line/Paragraph Separator -> newline", len(matches)))
        result = SEPARATORS_RE.sub("\n", result)

    if smart_quotes:
        count = 0
        count += len(SMART_SINGLE_QUOTES_RE.findall(result))
        result = SMART_SINGLE_QUOTES_RE.sub("'", result)
        count += len(SMART_DOUBLE_QUOTES_RE.findall(result))
        result = SMART_DOUBLE_QUOTES_RE.sub('"', result)
        count += len(SMART_DASHES_RE.findall(result))
        result = SMART_DASHES_RE.sub("-", result)
        if count:
            report.append(("Smart quotes/dashes -> plain ASCII", count))

    return result, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="Input file (reads stdin if omitted)")
    parser.add_argument("-o", "--output", help="Write cleaned text here instead of stdout")
    parser.add_argument("--report", action="store_true",
                         help="Print a summary of what was removed, to stderr")
    parser.add_argument("--keep-nbsp", action="store_true",
                         help="Leave non-breaking spaces (U+00A0) as-is")
    parser.add_argument("--keep-separators", action="store_true",
                         help="Leave U+2028/U+2029 line/paragraph separators as-is")
    parser.add_argument("--smart-quotes", action="store_true",
                         help="Also convert curly quotes and en/em dashes to plain ASCII")
    args = parser.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    cleaned, report = clean(
        text,
        keep_nbsp=args.keep_nbsp,
        keep_separators=args.keep_separators,
        smart_quotes=args.smart_quotes,
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(cleaned)
    else:
        sys.stdout.write(cleaned)

    if args.report:
        if not report:
            print("No invisible/control characters found — text was already clean.",
                  file=sys.stderr)
        else:
            total = sum(c for _, c in report)
            print(f"Removed/converted {total} character(s) across {len(report)} type(s):",
                  file=sys.stderr)
            for label, count in report:
                print(f"  - {label}: {count}", file=sys.stderr)


if __name__ == "__main__":
    main()
