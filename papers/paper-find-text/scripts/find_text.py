#!/usr/bin/env python3
"""paper-find-text: locate a piece of text inside a paper (PDF/DOCX/TXT).

Outputs JSON describing (1) match status (verbatim / near-verbatim /
candidate-rephrase / not-found), (2) page numbers (PDF index + printed
page), (3) context, (4) markers that the passage cites other work, and
(5) bibliographic metadata of the file itself (for citing the lead author).

The script gives evidence; the final verdict is made by reading the
returned passage. Usage:
  python find_text.py FILE --query "text" [--per-sentence] [--ocr --lang eng]
  python find_text.py FILE --query-file q.txt
  python find_text.py FILE --meta-only
"""
import argparse, json, re, shutil, subprocess, sys, tempfile, unicodedata, os
from bisect import bisect_right
from collections import Counter
from difflib import SequenceMatcher

STOP = set("""a an the of to in on at by for with from as is are was were be been being this that these those
it its and or but if then than so such not no can could may might will would should has have had do does did
which who whom whose we our they their he she his her you your i also more most other into over under between
within about using used use based both each any all one two""".split())

# ---------------------------------------------------------------- extraction
def _pdftotext(path):
    if not shutil.which("pdftotext"):
        return None
    out = subprocess.run(["pdftotext", "-enc", "UTF-8", path, "-"],
                         capture_output=True)
    if out.returncode != 0:
        return None
    pages = out.stdout.decode("utf-8", "replace").split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages

def _pdfplumber(path):
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            return [(p.extract_text() or "") for p in pdf.pages]
    except Exception:
        return None

def _pypdf(path):
    try:
        from pypdf import PdfReader
        return [(p.extract_text() or "") for p in PdfReader(path).pages]
    except Exception:
        return None

def _ocr(path, lang):
    if not (shutil.which("pdftoppm") and shutil.which("tesseract")):
        sys.exit("OCR requested but pdftoppm/tesseract not installed")
    tmp = tempfile.mkdtemp()
    subprocess.run(["pdftoppm", "-r", "300", "-png", path, f"{tmp}/p"], check=True)
    pages = []
    for f in sorted(os.listdir(tmp)):
        r = subprocess.run(["tesseract", f"{tmp}/{f}", "-", "-l", lang],
                           capture_output=True)
        pages.append(r.stdout.decode("utf-8", "replace"))
    return pages

def extract_pages(path, ocr=False, lang="eng"):
    """Return (pages, method, warnings)."""
    warnings = []
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md"):
        txt = open(path, encoding="utf-8", errors="replace").read()
        pages = txt.split("\f") if "\f" in txt else [txt]
        if len(pages) == 1:
            warnings.append("Plain text has no page structure; page numbers unavailable.")
        return pages, "text", warnings
    if ext in (".docx", ".doc", ".odt", ".rtf"):
        soffice = shutil.which("soffice") or shutil.which("libreoffice")
        if soffice:
            tmp = tempfile.mkdtemp()
            subprocess.run([soffice, "--headless", "--convert-to", "pdf",
                            "--outdir", tmp, path], capture_output=True)
            pdf = os.path.join(tmp, os.path.splitext(os.path.basename(path))[0] + ".pdf")
            if os.path.exists(pdf):
                warnings.append("Converted to PDF for pagination; page numbers reflect the "
                                "converted layout and may differ from Word's.")
                path = pdf
                ext = ".pdf"
        if ext != ".pdf":
            try:
                import docx
                d = docx.Document(path)
                warnings.append("DOCX pages cannot be determined; page numbers unavailable.")
                return ["\n".join(p.text for p in d.paragraphs)], "docx", warnings
            except Exception as e:
                sys.exit(f"Cannot read document: {e}")
    if ocr:
        return _ocr(path, lang), "ocr", warnings
    for name, fn in (("pdftotext", _pdftotext), ("pdfplumber", _pdfplumber), ("pypdf", _pypdf)):
        pages = fn(path)
        if pages and sum(len(p.strip()) for p in pages) > 0:
            avg = sum(len(p) for p in pages) / max(1, len(pages))
            if avg < 200:
                warnings.append("Very little text per page - the PDF is probably scanned. "
                                "Re-run with --ocr (and --lang, e.g. eng+ara).")
            return pages, name, warnings
    warnings.append("No extractable text - scanned PDF? Re-run with --ocr.")
    return [""], "none", warnings

# ------------------------------------------------------------- normalization
AR_DIAC = re.compile("[\u064B-\u065F\u0670\u0640]")
LIG = {"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi", "\ufb04": "ffl"}

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    for k, v in LIG.items():
        s = s.replace(k, v)
    s = re.sub(r"(\w)[-\u2010\u2011\u00ad]\s*\n\s*(\w)", r"\1\2", s)   # de-hyphenate line breaks
    s = s.replace("\u00ad", "")
    s = s.translate({0x2018: "'", 0x2019: "'", 0x201C: '"', 0x201D: '"',
                     0x2013: "-", 0x2014: "-", 0x2212: "-"})
    s = AR_DIAC.sub("", s)
    s = s.lower()
    s = re.sub(r"[^\w\s%.\-/]", " ", s)          # keep digits, decimal points, % and hyphens
    s = re.sub(r"(?<!\d)\.|\.(?!\d)", " ", s)    # drop sentence periods, keep 3.14
    s = re.sub(r"\s+", " ", s).strip()
    return s

def build_index(pages):
    """Concatenate normalized pages; keep char offsets and word->page map."""
    parts, starts, cur = [], [], 0
    words, wpage = [], []
    for i, p in enumerate(pages):
        n = norm(p)
        starts.append(cur)
        parts.append(n)
        cur += len(n) + 1
        for w in n.split():
            words.append(w); wpage.append(i + 1)
    return " ".join(parts), starts, words, wpage

# ------------------------------------------------------------ page numbering
def printed_pages(pages):
    guess = {}
    for i, p in enumerate(pages):
        lines = [l.strip() for l in p.splitlines() if l.strip()]
        for l in lines[:3] + lines[-3:]:
            m = re.fullmatch(r"(?:page\s*)?(\d{1,4})(?:\s*(?:of|/)\s*\d+)?", l, re.I)
            if m:
                guess[i + 1] = int(m.group(1)); break
    offs = Counter(v - k for k, v in guess.items())
    return guess, (offs.most_common(1)[0][0] if offs else None)

def page_labels(path):
    try:
        from pypdf import PdfReader
        r = PdfReader(path)
        labels = list(r.page_labels)
        if any(l != str(i + 1) for i, l in enumerate(labels)):
            return labels
    except Exception:
        pass
    return None

def page_info(pg, guess, off, labels):
    d = {"pdf_page": pg}
    if labels and pg - 1 < len(labels):
        d["page_label"] = labels[pg - 1]
    if pg in guess:
        d["printed_page"] = guess[pg]; d["printed_page_source"] = "read from page header/footer"
    elif off is not None:
        d["printed_page"] = pg + off; d["printed_page_source"] = "inferred from neighbouring pages"
    return d

# ---------------------------------------------------------------- matching
CITE_PAT = re.compile(
    r"\[\s*\d+(?:\s*[-,\u2013]\s*\d+)*\s*\]"                           # [12], [3-5]
    r"|\([^()]*?(?:et al\.?|&|and)?[^()]*?\b(?:19|20)\d{2}[a-z]?\)"   # (Smith et al., 2019)
    r"|\b[A-Z][a-z]+(?: et al\.?| and [A-Z][a-z]+| & [A-Z][a-z]+)?\s*\(\s*(?:19|20)\d{2}[a-z]?\s*\)")

def cite_markers(raw):
    return sorted(set(m.group(0).strip() for m in CITE_PAT.finditer(raw)))[:12]

def nums(s):
    return set(re.findall(r"\d+(?:\.\d+)?", s))

def stem(w):
    return w[:5] if len(w) > 5 and w.isalpha() else w   # crude: activated/activation -> activ

def content(ws):
    return [stem(w) for w in ws if w not in STOP and len(w) > 1]

def context(words, a, b, pad=25):
    return " ".join(words[max(0, a - pad):a]), " ".join(words[a:b]), " ".join(words[b:b + pad])

def raw_passage(pages, pg, win):
    """Recover original-case text (with citation markers) for a matched word window."""
    if not win:
        return None
    raw = re.sub(r"\s+", " ", pages[pg - 1])
    def rx(ws): return r"\W*".join(re.escape(w) for w in ws)
    m1 = re.search(rx(win[:4]), raw, re.I)
    if not m1:
        return None
    m2 = re.search(rx(win[-4:]), raw[m1.start():], re.I)
    end = m1.start() + m2.end() if m2 else min(len(raw), m1.start() + 700)
    return raw[m1.start():end]

def check(query, pages, full, starts, words, wpage, pg_info):
    q = norm(query)
    qw = q.split()
    res = {"query_words": len(qw)}
    if len(qw) < 4:
        res["status"] = "TOO_SHORT"; res["note"] = "Query under 4 words - matches would be meaningless."
        return res

    # 1) exact (after normalization)
    hits = [m.start() for m in re.finditer(re.escape(q), full)]
    if hits:
        def pg_of(off): return bisect_right(starts, off)
        occ = []
        for h in hits[:5]:
            p1, p2 = pg_of(h), pg_of(h + len(q) - 1)
            wi = len(full[:h].split())
            b, m, a = context(words, wi, wi + len(qw))
            rp = raw_passage(pages, p1, qw)
            occ.append({"original_text": rp, "citation_markers_in_passage": cite_markers(rp or ""),
                        "pages": pg_info(p1) if p1 == p2 else
                        {"start": pg_info(p1), "end": pg_info(p2), "spans_pages": True},
                        "before": b, "match": m, "after": a})
        res.update(status="VERBATIM", occurrences=len(hits), matches=occ,
                   note="Exact match after normalizing case, hyphenation, quotes, spacing and ligatures.")
        return res

    # 2) fuzzy windows
    qset = set(content(qw)) or set(qw)
    n = len(qw)
    cands = []
    for L in sorted({n, max(4, int(n * 1.3)), max(4, int(n * 0.8))}):
        step = max(1, L // 5)
        for i in range(0, max(1, len(words) - L + 1), step):
            win = words[i:i + L]
            cov = len(qset & set(content(win))) / len(qset)
            if cov >= 0.3:
                cands.append((cov, i, L))
    cands.sort(reverse=True)
    scored, used = [], []
    for cov, i, L in cands[:60]:
        # refine start position around i
        best = None
        for s in range(max(0, i - L // 5), min(len(words) - 1, i + L // 5) + 1):
            win = words[s:s + L]
            r = SequenceMatcher(None, qw, win, autojunk=False).ratio()
            if best is None or r > best[0]:
                best = (r, s, L)
        r, s, L = best
        if any(abs(s - u) < n * 0.6 for u in used):
            continue
        used.append(s)
        win = words[s:s + L]
        scored.append((r, cov, s, L, win))
        if len(scored) >= 3:
            break
    scored.sort(key=lambda t: (t[0] + t[1]), reverse=True)

    out = []
    for r, cov, s, L, win in scored:
        sm = SequenceMatcher(None, qw, win, autojunk=False)
        changes = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                changes.append({"op": tag, "query": " ".join(qw[i1:i2]), "paper": " ".join(win[j1:j2])})
        b, m, a = context(words, s, s + L)
        pgs = sorted({wpage[k] for k in range(s, min(s + L, len(wpage)))})
        missing_nums = sorted(nums(q) - nums(m))
        out.append({
            "sequence_similarity": round(r, 3), "keyword_coverage": round(cov, 3),
            "pages": pg_info(pgs[0]) if len(pgs) == 1 else
                     {"start": pg_info(pgs[0]), "end": pg_info(pgs[-1]), "spans_pages": True},
            "before": b, "passage": m, "after": a,
            "word_changes": changes[:25],
            "numbers_in_query_not_in_passage": missing_nums,
            "original_text": (rp := raw_passage(pages, pgs[0], win)),
            "citation_markers_in_passage": cite_markers(rp or "")})
    if not out:
        res.update(status="NOT_FOUND", candidates=[],
                   note="No passage shares meaningful vocabulary with the query.")
        return res
    top = out[0]
    if top["sequence_similarity"] >= 0.88:
        status = "NEAR_VERBATIM"
    elif top["keyword_coverage"] >= 0.55 and top["sequence_similarity"] >= 0.30:
        status = "CANDIDATE_REPHRASE"
    elif top["keyword_coverage"] >= 0.4:
        status = "WEAK_CANDIDATE"
    else:
        status = "NOT_FOUND"
    res.update(status=status, candidates=out)
    res["note"] = {
        "NEAR_VERBATIM": "Almost identical wording; see word_changes for edits.",
        "CANDIDATE_REPHRASE": "Shared vocabulary but different wording/order - READ the passage and judge whether the meaning is the same.",
        "WEAK_CANDIDATE": "Low lexical overlap. Could be a paraphrase using different vocabulary, or unrelated. READ the passage before deciding; if the meaning does not match, the verdict is NOT FOUND.",
        "NOT_FOUND": "Best candidates are weak - treat as absent unless a manual read shows otherwise."}[status]
    return res

# ---------------------------------------------------------------- metadata
def metadata(path, pages):
    m = {}
    try:
        from pypdf import PdfReader
        info = PdfReader(path).metadata or {}
        m["pdf_metadata"] = {k.strip("/"): str(v) for k, v in info.items()
                             if k.strip("/") in ("Title", "Author", "Subject", "CreationDate")}
    except Exception:
        pass
    head = "\n".join(pages[:2])
    m["doi_candidates"] = sorted(set(re.findall(r"10\.\d{4,9}/[^\s\"<>]+", head)))[:3]
    m["year_candidates"] = dict(Counter(re.findall(r"\b(?:19|20)\d{2}\b", head)).most_common(4))
    m["first_page_text"] = re.sub(r"[ \t]+", " ", pages[0])[:2000] if pages else ""
    m["note"] = ("Read first_page_text to identify the title and the FIRST-listed author. "
                 "pdf_metadata is often wrong (may hold the uploader or software name).")
    return m

# -------------------------------------------------------------------- main
def sentences(t):
    parts = re.split(r"(?<=[.!?\u061F])\s+(?=[A-Z\u0621-\u064A0-9\"'(\[])", t.strip())
    return [p for p in parts if len(p.split()) >= 4]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--query"); ap.add_argument("--query-file")
    ap.add_argument("--per-sentence", action="store_true")
    ap.add_argument("--ocr", action="store_true"); ap.add_argument("--lang", default="eng")
    ap.add_argument("--meta-only", action="store_true")
    a = ap.parse_args()

    pages, method, warns = extract_pages(a.file, a.ocr, a.lang)
    result = {"file": os.path.basename(a.file), "pages_total": len(pages),
              "extraction": method, "warnings": warns,
              "metadata": metadata(a.file, pages)}
    if a.meta_only:
        print(json.dumps(result, ensure_ascii=False, indent=2)); return

    q = a.query or (open(a.query_file, encoding="utf-8").read() if a.query_file else None)
    if not q:
        sys.exit("Provide --query or --query-file")

    full, starts, words, wpage = build_index(pages)
    guess, off = printed_pages(pages)
    labels = page_labels(a.file) if a.file.lower().endswith(".pdf") else None
    pi = lambda pg: page_info(pg, guess, off, labels)

    # locate the start of a reference list so hits there can be flagged
    ref_page = None
    for i, p in enumerate(pages):
        if re.search(r"^\s*(references|bibliography|literature cited|المراجع|المصادر)\s*$", p, re.I | re.M):
            ref_page = i + 1
    result["reference_list_starts_on_pdf_page"] = ref_page

    result["whole_query"] = check(q, pages, full, starts, words, wpage, pi)
    if a.per_sentence:
        result["sentences"] = [{"sentence": s, **check(s, pages, full, starts, words, wpage, pi)}
                               for s in sentences(q)]
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
