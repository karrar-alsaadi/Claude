#!/usr/bin/env python3
"""
audit_report.py - lint a paper-review report (paper-find-misstake format, English or Arabic)
and, with --paper, check that quoted text, numbers and page references occur in the paper.

Everything printed is a LEAD for the evaluator to verify by hand, never a verdict:
a quote that is "not found" may be a paraphrase or an OCR/extraction difference, and a
clean lint does not show that the findings are right.

Usage:
  python audit_report.py review.md                       # JSON to stdout
  python audit_report.py review.md --paper paper.txt     # + quote/number/page checks
  python audit_report.py review.md --paper paper.txt --brief
  python audit_report.py review.md --out audit.json

Paper text with form feeds (\\f, as written by `pdftotext -layout`) enables page checks.
"""
import argparse
import json
import re
import sys

# ----------------------------------------------------------------- normalisation
_DIGITS = str.maketrans({
    **{chr(0x0660 + i): str(i) for i in range(10)},   # Arabic-Indic
    **{chr(0x06F0 + i): str(i) for i in range(10)},   # Persian
    "\u066b": ".", "\u066c": "", "\u060c": ",",
})
_DIAC = re.compile(r"[\u064b-\u065f\u0670\u0640]")     # tashkeel + tatweel
_QUOTES = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
                         "\u2013": "-", "\u2014": "-", "\u2212": "-", "\u00a0": " "})


def norm(s: str) -> str:
    s = s.translate(_DIGITS).translate(_QUOTES)
    s = _DIAC.sub("", s)
    s = s.replace("\u0623", "\u0627").replace("\u0625", "\u0627").replace("\u0622", "\u0627")
    s = s.replace("\u0649", "\u064a").replace("\u0629", "\u0647")
    s = re.sub(r"-\s*\n\s*", "", s)                    # hyphenated line breaks
    s = re.sub(r"\s+", " ", s.lower())
    return s.strip()


def words(s: str):
    return re.findall(r"[\w.%]+", norm(s), flags=re.UNICODE)


# ----------------------------------------------------------------- field labels
FIELDS = {
    "id": ["finding #", "finding no", "finding", "رقم الملاحظة"],
    "category": ["category", "تصنيف الخطأ"],
    "severity": ["severity", "درجة الأثر"],
    "location": ["exact location", "location", "الموضع الدقيق"],
    "text": ["text or number in question", "text in question", "النص أو الرقم محل الملاحظة"],
    "description": ["verifiable description of the problem", "description", "وصف المشكلة القابل للتحقق"],
    "evidence": ["evidence, calculation, or comparison source", "evidence", "الدليل أو الحساب أو المصدر المقارن"],
    "effect": ["possible effect on results or interpretation", "possible effect", "الأثر المحتمل في النتائج أو التفسير"],
    "fix": ["suggested correction or question for the authors", "suggested correction", "التصحيح المقترح أو السؤال المطلوب من المؤلف"],
    "confidence": ["confidence", "درجة الثقة في الملاحظة", "درجة الثقة"],
}
LABELS = sorted([(norm(l), k) for k, ls in FIELDS.items() for l in ls], key=lambda x: -len(x[0]))

SEV = {"minor": "minor", "moderate": "moderate", "substantial": "substantial", "critical": "critical",
       "طفيفه": "minor", "طفيف": "minor", "متوسطه": "moderate", "متوسط": "moderate",
       "جوهريه": "substantial", "جوهري": "substantial", "حرجه": "critical", "حرج": "critical"}
CONF = {"high": "high", "medium": "medium", "low": "low",
        "عاليه": "high", "عالي": "high", "متوسطه": "medium", "متوسط": "medium",
        "منخفضه": "low", "منخفض": "low"}

SECTIONS = {
    "bottom_line": ["bottom line", "summary", "central claim", "overall", "الخلاصه", "ملخص", "الادعاء المركزي", "الحكم العام"],
    "scope_limits": ["scope", "limits", "limitation", "not assessed", "could not assess", "نطاق", "حدود", "لم يتم تقييم", "لم يقيم", "لم اتمكن"],
    "evidence_map": ["evidence map", "claim map", "claim ->", "خريطه الادله", "خريطه الادعاءات"],
    "checked_consistent": ["checked and", "found consistent", "consistent", "تم التحقق", "متسق", "سليمه"],
    "author_questions": ["questions for the authors", "question for the authors", "اسئله للمؤلفين", "للمؤلفين"],
    "action_level": ["suggested action", "action level", "editorial correction", "expression of concern",
                     "substantial correction", "التعبير عن القلق", "مستوي الاجراء", "التصحيح الجوهري", "تصحيح تحريري"],
    "tools_stated": ["check_numbers", "statcheck", "grim", "recomputed", "recalculated", "script", "اعيد حساب", "سكربت", "اعادة حساب"],
    "not_assessed": ["not assessed", "could not", "unable to", "not available", "لم يتم تقييم", "لم اتمكن", "غير متاح", "لم يقيم"],
}

INTENT = [r"fabricat\w*", r"falsif\w*", r"manipulat\w*", r"\bfraud\w*", r"\bfaked?\b", r"\bforged?\b",
          r"\bcheat\w*", r"misconduct", r"deliberate\w*", r"intentional\w*", r"made up", r"\blied\b", r"\blying\b",
          "تزوير", "تلاعب", "احتيال", "فبرك", "تزييف", "مزور", "ملفق", "غش", "تضليل متعمد", "متعمد", "قصدا"]
NEGATION = re.compile(r"\b(no|not|never|without|nor|neither)\b|لا\s|ليس|لم\s|دون|بدون|لا يعني|لا يثبت|لا يدل", re.I)
OVERCONF = [r"\bclearly\b", r"\bobviously\b", r"\bundoubtedly\b", r"\bproves?\b", r"\bdefinitely\b", r"\bwithout doubt\b",
            "بالتاكيد", "بلا شك", "من الواضح", "واضح ان", "يثبت"]
ASSUMPTION = re.compile(r"\b(assum\w*|probably|likely|appears?|seems?|might|may be|could be|presumably|inferred)\b|يبدو|ربما|محتمل|يفترض|على الارجح", re.I)
LOC_MARK = re.compile(r"\b(page|pages|p\.|pp\.|table|figure|fig\.?|section|paragraph|line|supplement\w*|appendix|abstract|methods|results)\b"
                      r"|صفحه|ص\s?\d|جدول|شكل|فقره|سطر|قسم|ملحق|الملخص", re.I)
EVID_MARK = re.compile(r"[=×÷±%]|\bsum\b|recomput\w*|recalc\w*|check_numbers|statcheck|\bgrim\b|اعيد|حساب|المجموع|\bvs\.?\b|\bversus\b|مقابل|بينما", re.I)
SEVERE_ASSUM = ("critical",)


# ----------------------------------------------------------------- parsing
def clean_line(l: str) -> str:
    l = l.strip()
    l = re.sub(r"^[>\-\*\u2022#\s]+", "", l)
    l = l.replace("**", "").replace("__", "").replace("`", "")
    return l.strip()


def label_of(line: str):
    """Return (field_key, value) if the line starts with a known label followed by a colon
    (the id label may also be followed directly by a number: 'Finding 3')."""
    n = norm(line)
    for lab, key in LABELS:
        if not n.startswith(lab):
            continue
        tail = n[len(lab):]
        if tail and re.match(r"[a-z\u0600-\u06ff]", tail[0]):
            continue                                   # 'findings' is not the label 'finding'
        has_colon = re.match(r"^\s*[:\uff1a]", tail) is not None
        has_num = key == "id" and re.match(r"^\s*#?\s*\d", tail) is not None
        if not (has_colon or has_num):
            continue
        idx = re.search(r"[:\uff1a]", line)
        val = line[idx.end():].strip() if (idx and has_colon) else line[len(lab):].strip()
        return key, val
    return None, None


FIND_HEAD = re.compile(r"^\s*(?:#{1,4}\s*)?(?:\*\*)?\s*(?:finding|ملاحظه|الملاحظه|ملاحظة|الملاحظة)\s*#?\s*(\d+)", re.I)


def parse_findings(text: str):
    findings, cur, last_key = [], None, None
    for raw in text.splitlines():
        line = clean_line(raw)
        if not line:
            continue
        nline = norm(line)
        key, val = label_of(line)
        mh = FIND_HEAD.match(nline)
        starts_new = False
        if key == "id":
            starts_new = True
        elif mh and key is None:
            starts_new = True
        if starts_new:
            if cur:
                findings.append(cur)
            cur = {"fields": {}, "raw": []}
            num = re.search(r"(\d+)", (val.translate(_DIGITS) if key == "id" and val else nline))
            cur["fields"]["id"] = num.group(1) if num else str(len(findings) + 1)
            last_key = None
            if key == "id" and val and not num:
                cur["fields"]["id"] = val
            continue
        if cur is None:
            continue
        if key and key != "id":
            cur["fields"][key] = val
            last_key = key
        elif last_key and not re.match(r"^(#{1,4}\s|\|)", raw.strip()) and not FIND_HEAD.match(nline):
            cur["fields"][last_key] = (cur["fields"].get(last_key, "") + " " + line).strip()
        cur["raw"].append(line)
    if cur:
        findings.append(cur)
    return findings


def minor_group_rows(text: str):
    rows, in_minor = 0, False
    for raw in text.splitlines():
        n = norm(raw)
        if re.match(r"^\s*#{1,4}", raw) or n.startswith("**"):
            in_minor = any(w in n for w in ["minor", "طفيف"])
        if in_minor and raw.count("|") >= 3 and not re.match(r"^\s*\|?\s*[-: ]+\|", raw):
            rows += 1
    return max(0, rows - 1) if rows else 0   # drop header row


def norm_value(d, table):
    v = norm(d or "")
    for k, out in table.items():
        if v.startswith(k):
            return out
    return None


# ----------------------------------------------------------------- paper checks
def ngrams(ws, n):
    return {" ".join(ws[i:i + n]) for i in range(len(ws) - n + 1)}


class Paper:
    def __init__(self, text):
        self.pages = [norm(p) for p in text.split("\f")] if "\f" in text else [norm(text)]
        self.has_pages = "\f" in text
        self.full = " ".join(self.pages)
        self.ws = words(self.full)
        self.tri = ngrams(self.ws, 3)
        self.uni = set(self.ws)

    def find_text(self, quote):
        q = norm(quote).strip(" .\"'«»“”")
        if len(q) < 4:
            return None, None, []
        if q in self.full:
            pages = [i + 1 for i, p in enumerate(self.pages) if q in p] if self.has_pages else []
            return "found", 1.0, pages
        qw = words(q)
        if len(qw) >= 3:
            qt = ngrams(qw, 3)
            frac = len(qt & self.tri) / max(1, len(qt))
        else:
            frac = sum(1 for w in qw if w in self.uni) / max(1, len(qw))
        if frac >= 0.9:
            return "near", round(frac, 2), []
        if frac >= 0.6:
            return "partial", round(frac, 2), []
        return "not_found", round(frac, 2), []

    def numbers_missing(self, s):
        toks = re.findall(r"(?<![\w.])\d+(?:\.\d+)?", norm(s))
        toks = [t for t in toks if len(t.replace(".", "")) >= 2 or "." in t]   # skip lone digits
        paper_nums = set(re.findall(r"(?<![\w.])\d+(?:\.\d+)?", self.full)) | \
                     {t.lstrip("0") or "0" for t in re.findall(r"\.\d+", self.full)}
        return sorted({t for t in toks if t not in paper_nums and t.lstrip("0") not in paper_nums})


def quoted_strings(s):
    out = re.findall(r"[\"“«]([^\"”»]{6,})[\"”»]", s or "")
    return [o.strip() for o in out]


def cited_pages(loc):
    ps = []
    for m in re.finditer(r"(?:\bpp?\.?|\bpages?|صفحه|صفحة|ص)\s*(\d+)(?:\s*[-–]\s*(\d+))?", norm(loc or "") + " " + (loc or ""), re.I):
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        ps.extend(range(a, min(b, a + 5) + 1))
    return sorted(set(ps))


# ----------------------------------------------------------------- main audit
def audit(text: str, paper_text: str = None):
    nt = norm(text)
    ar_ratio = len(re.findall(r"[\u0600-\u06ff]", text)) / max(1, len(re.findall(r"[A-Za-z\u0600-\u06ff]", text)))
    lang = "ar" if ar_ratio > 0.5 else ("mixed" if ar_ratio > 0.1 else "en")

    secs = {k: any(w in nt for w in ws) for k, ws in SECTIONS.items()}
    first = norm(text[:700])
    bottom_first = any(w in first for w in SECTIONS["bottom_line"]) or bool(re.search(r"\b(critical|substantial|moderate|minor)\b.*\d|\d.*(جوهري|متوسط|طفيف|حرج)", first))

    paper = Paper(paper_text) if paper_text else None
    fs = parse_findings(text)
    out_f, sev_counts, conf_counts = [], {}, {}
    flags_global = []

    for f in fs:
        d = f["fields"]
        fid = d.get("id", "?")
        sev = norm_value(d.get("severity"), SEV)
        conf = norm_value(d.get("confidence"), CONF)
        sev_counts[sev or "missing"] = sev_counts.get(sev or "missing", 0) + 1
        conf_counts[conf or "missing"] = conf_counts.get(conf or "missing", 0) + 1
        required = ["category", "severity", "location", "text", "description", "evidence", "effect", "fix", "confidence"]
        minor_only = sev == "minor"
        missing = [k for k in required if not d.get(k)]
        if minor_only:                       # minor items may be grouped; do not demand all fields
            missing = [k for k in missing if k in ("location", "text")]
        hints = []
        loc = d.get("location", "")
        loc_specific = bool(LOC_MARK.search(norm(loc))) and bool(re.search(r"\d", loc))
        if loc and not loc_specific:
            hints.append("location is vague (no page/table/figure/section number)")
        if not loc:
            hints.append("no location")
        ev = d.get("evidence", "")
        ev_kind = "computed" if EVID_MARK.search(ev) and re.search(r"\d", ev) else ("textual" if quoted_strings(ev + d.get("text", "")) else ("thin" if ev else "none"))
        if ev_kind in ("thin", "none") and sev in ("moderate", "substantial", "critical"):
            hints.append("moderate+ finding with thin or no evidence")
        full_text = " ".join(d.get(k, "") for k in ("text", "description", "evidence", "effect", "fix"))
        if conf == "high" and ASSUMPTION.search(norm(full_text)):
            hints.append("high confidence but text hedges or states an assumption")
        if sev == "critical" and conf != "high":
            hints.append("critical severity without high confidence: critical needs strong independent evidence")
        if sev == "critical":
            hints.append("critical used: verify independent evidence and that it is not an integrity assertion")
        intent = []
        for pat in INTENT:
            for m in re.finditer(pat, norm(full_text), re.I):
                ctx = norm(full_text)[max(0, m.start() - 40): m.end() + 40]
                intent.append({"term": m.group(0), "context": ctx, "negated_context": bool(NEGATION.search(ctx))})
        over = [m.group(0) for pat in OVERCONF for m in re.finditer(pat, norm(full_text), re.I)]
        item = {"id": fid, "category": d.get("category"), "severity": sev, "confidence": conf,
                "location": loc, "missing_fields": missing, "location_specific": loc_specific,
                "evidence_kind": ev_kind, "hints": hints, "intent_terms": intent, "overconfident_terms": over}

        if paper:
            checks = {"quotes": [], "numbers_missing": [], "page_check": None}
            cand = []
            if d.get("text"):
                cand.append(d["text"])
            cand.extend(quoted_strings(d.get("description", "")) + quoted_strings(d.get("evidence", "")))
            seen_q = set()
            for c in cand:
                for piece in ([c] + quoted_strings(c)) if quoted_strings(c) else [c]:
                    if norm(piece).strip(' "') in seen_q:
                        continue
                    seen_q.add(norm(piece).strip(' "'))
                    if len(norm(piece)) < 6 or re.fullmatch(r"[\d\s.,%=<>()+\-/±]*", norm(piece)):
                        continue
                    st, fr, pgs = paper.find_text(piece)
                    if st:
                        checks["quotes"].append({"text": piece[:90], "status": st, "overlap": fr, "pdf_pages": pgs})
            nums_src = d.get("text", "") + " " + " ".join(quoted_strings(d.get("description", "")))
            checks["numbers_missing"] = paper.numbers_missing(nums_src)
            cp = cited_pages(loc)
            found_pages = sorted({p for q in checks["quotes"] for p in q["pdf_pages"]})
            if cp and found_pages:
                checks["page_check"] = {"cited": cp, "found_on_pdf_pages": found_pages,
                                        "match": bool(set(cp) & set(found_pages)),
                                        "note": "PDF page index vs printed page number can differ; compare both"}
            item["paper_checks"] = checks
            if any(q["status"] == "partial" for q in checks["quotes"]):
                item["hints"].append("quoted text only partly matches the paper: possible misquote or paraphrase presented as a quote")
            if any(q["status"] == "not_found" for q in checks["quotes"]):
                item["hints"].append("quoted text not found in paper: misquote, paraphrase, or extraction difference? verify by hand")
            if checks["numbers_missing"]:
                item["hints"].append("numbers not found anywhere in paper text: " + ", ".join(checks["numbers_missing"][:6]))
            if checks["page_check"] and not checks["page_check"]["match"]:
                item["hints"].append("cited page differs from where the quote was found")
        out_f.append(item)

    n = len(out_f)
    inflated = (sev_counts.get("critical", 0) + sev_counts.get("substantial", 0)) / n if n else 0
    if n >= 4 and inflated > 0.5:
        flags_global.append("more than half of findings graded substantial/critical: check for severity inflation")
    ids = [f["id"] for f in out_f]
    if len(ids) != len(set(ids)):
        flags_global.append("duplicate finding ids")
    texts = [norm(f["fields"].get("text", "")) for f in fs if f["fields"].get("text")]
    if len(texts) != len(set(texts)):
        flags_global.append("same text-in-question appears in more than one finding (one issue per finding?)")
    if n == 0:
        flags_global.append("no template-formatted findings parsed: report may use another layout; read it by hand")
    if not secs["checked_consistent"]:
        flags_global.append("no 'checked and found consistent' section detected")
    if not secs["not_assessed"] and not secs["scope_limits"]:
        flags_global.append("no scope/limits or 'not assessed' statement detected")
    if not secs["action_level"]:
        flags_global.append("no suggested action level detected")
    if not bottom_first:
        flags_global.append("bottom line does not appear first")
    if re.search(r"\bnot retracted\b|\bno retraction\b|لم تسحب|غير مسحوب", nt) and not re.search(r"retraction watch|crossref|pubmed|publisher|ريتراكشن|كروس", nt):
        flags_global.append("states 'not retracted' with no route named (gate G4 candidate)")
    all_intent = [t for f in out_f for t in f["intent_terms"]]
    for m in re.finditer("|".join(INTENT), nt, re.I):
        if not any(m.group(0) in t["term"] for t in all_intent):
            ctx = nt[max(0, m.start() - 40): m.end() + 40]
            all_intent.append({"term": m.group(0), "context": ctx, "negated_context": bool(NEGATION.search(ctx)), "where": "report body"})
    live_intent = [t for t in all_intent if not t["negated_context"]]
    if live_intent:
        flags_global.append(f"{len(live_intent)} intent-language hit(s) outside negated context (gate G2 candidates): read each in context")

    res = {
        "language": lang,
        "sections_detected": secs,
        "bottom_line_first": bottom_first,
        "findings_parsed": n,
        "minor_group_rows": minor_group_rows(text),
        "severity_counts": sev_counts,
        "confidence_counts": conf_counts,
        "global_flags": flags_global,
        "intent_language": all_intent,
        "findings": out_f,
        "paper_checked": bool(paper),
        "note": "All entries are leads for manual verification, not verdicts.",
    }
    if paper:
        q_total = sum(len(f["paper_checks"]["quotes"]) for f in out_f)
        q_bad = sum(1 for f in out_f for q in f["paper_checks"]["quotes"] if q["status"] == "not_found")
        res["paper_summary"] = {"has_page_breaks": paper.has_pages, "quotes_checked": q_total, "quotes_not_found": q_bad,
                                "findings_with_missing_numbers": sum(1 for f in out_f if f["paper_checks"]["numbers_missing"])}
    return res


def brief(r):
    L = []
    L.append(f"language={r['language']}  findings={r['findings_parsed']}  (+{r['minor_group_rows']} grouped minor rows)")
    L.append("severity: " + ", ".join(f"{k}={v}" for k, v in r["severity_counts"].items()))
    L.append("confidence: " + ", ".join(f"{k}={v}" for k, v in r["confidence_counts"].items()))
    L.append("sections: " + ", ".join(f"{k}={'Y' if v else 'n'}" for k, v in r["sections_detected"].items()))
    if r.get("paper_summary"):
        p = r["paper_summary"]
        L.append(f"paper: page_breaks={p['has_page_breaks']} quotes_checked={p['quotes_checked']} not_found={p['quotes_not_found']} findings_with_missing_numbers={p['findings_with_missing_numbers']}")
    for g in r["global_flags"]:
        L.append("FLAG: " + g)
    for f in r["findings"]:
        bits = []
        if f["missing_fields"]:
            bits.append("missing=" + ",".join(f["missing_fields"]))
        bits.extend(f["hints"])
        for t in f["intent_terms"]:
            if not t["negated_context"]:
                bits.append(f"INTENT:{t['term']}")
        if bits:
            L.append(f"  #{f['id']} [{f['severity']}/{f['confidence']}] " + " | ".join(bits))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report")
    ap.add_argument("--paper")
    ap.add_argument("--out")
    ap.add_argument("--brief", action="store_true")
    a = ap.parse_args()
    text = open(a.report, encoding="utf-8", errors="replace").read()
    paper = open(a.paper, encoding="utf-8", errors="replace").read() if a.paper else None
    r = audit(text, paper)
    if a.out:
        json.dump(r, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if a.brief:
        print(brief(r))
    elif not a.out:
        print(json.dumps(r, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
