#!/usr/bin/env python3
"""
score.py - scoring helpers for the paper-evaluation skill.

  aggregate eval.json [--out result.json]   weighted 0-100 score, derived D1/D3/D4, gates, band
  bench truth.json matches.json             precision / recall / weighted recall vs planted errors
  html result.json out.html [--rtl]         dark, high-contrast, self-contained scorecard

All outputs are JSON (except html). The numbers summarise judgements the evaluator already
made; they do not replace reading the paper. See references/rubric.md for anchors and gates.
"""
import argparse
import html as H
import json
import sys

DIMS = {
    "D1": ("Accuracy of findings (precision)", "دقة الملاحظات", 25),
    "D2": ("Evidence and traceability", "الدليل وقابلية التتبع", 15),
    "D3": ("Coverage of material issues", "تغطية المشكلات المهمة", 20),
    "D4": ("Severity and confidence calibration", "معايرة الأثر والثقة", 10),
    "D5": ("Neutral wording, integrity boundary", "الصياغة المحايدة", 10),
    "D6": ("Honest scope and transparency", "صدق النطاق والشفافية", 8),
    "D7": ("Interpretation and actionability", "الاستنتاج وقابلية التنفيذ", 7),
    "D8": ("Format and language fit", "الشكل واللغة", 5),
}
SEV_W = {"minor": 1, "moderate": 2, "substantial": 4, "critical": 8}
SEV_LVL = {"minor": 0, "moderate": 1, "substantial": 2, "critical": 3}
VERDICT_W = {"confirmed": 1.0, "misgraded": 1.0, "partial": 0.5, "not_error": 0.0,
             "false_positive": 0.0, "overreach": 0.0}   # unverifiable excluded
CAPS = {"fabricated_evidence": 60, "misconduct_assertion": 70,
        "missed_overturning_flaw": 75, "unverified_integrity_claim": 80}
GATE_TEXT = {
    "fabricated_evidence": "G1 fabricated evidence",
    "misconduct_assertion": "G2 misconduct asserted without official finding",
    "missed_overturning_flaw": "G3 missed a flaw that decides the central claim",
    "unverified_integrity_claim": "G4 integrity claim without a stated route",
    "precision_below_half": "auto: precision below 0.50",
}


def band(total, provisional):
    b = "Excellent" if total >= 90 else "Good" if total >= 75 else "Needs revision" if total >= 60 else "Unreliable"
    return ("Provisional " + b) if provisional else b


def thresholds(x, cuts):
    for lim, sc in cuts:
        if x >= lim:
            return sc
    return 0


def derive_precision(findings):
    num = den = 0.0
    unver = 0
    counts = {}
    for f in findings:
        v = f.get("verdict", "").strip().lower()
        counts[v] = counts.get(v, 0) + 1
        if v == "unverifiable":
            unver += 1
            continue
        if v not in VERDICT_W:
            raise SystemExit(f"finding {f.get('id')}: unknown verdict '{v}' (use {', '.join(list(VERDICT_W) + ['unverifiable'])})")
        den += 1
        num += VERDICT_W[v]
    return (num / den if den else None), counts, unver


def derive_recall(findings, missed):
    found = missed_w = 0.0
    for f in findings:
        v = f.get("verdict", "").lower()
        sev = (f.get("severity_true") or f.get("severity_claimed") or "moderate").lower()
        if v in ("confirmed", "misgraded"):
            found += SEV_W.get(sev, 2)
        elif v == "partial":
            found += 0.5 * SEV_W.get(sev, 2)
            missed_w += 0.5 * SEV_W.get(sev, 2)
    for m in missed:
        missed_w += SEV_W.get((m.get("severity") or "moderate").lower(), 2)
    tot = found + missed_w
    return (found / tot if tot else None)


def derive_calibration(findings):
    ok = n = 0
    for f in findings:
        if f.get("verdict", "").lower() in ("unverifiable", "false_positive", "overreach", "not_error"):
            continue
        sev_ok = None
        if f.get("severity_claimed") and f.get("severity_true"):
            sev_ok = abs(SEV_LVL[f["severity_claimed"].lower()] - SEV_LVL[f["severity_true"].lower()]) <= 1
        elif "severity_ok" in f:
            sev_ok = bool(f["severity_ok"])
        conf_ok = f.get("confidence_ok")
        if sev_ok is None and conf_ok is None:
            continue
        n += 1
        if sev_ok is False or conf_ok is False:
            continue
        ok += 0.5 if conf_ok == "under" else 1
    return (ok / n if n else None)


def aggregate(e):
    mode = e.get("mode", "full")
    structural = mode == "structural"
    findings = e.get("findings", [])
    missed = e.get("missed", [])
    manual = e.get("scores", {})
    notes = e.get("notes", {})
    scores, source = {}, {}
    prec = recall = calib = None
    counts, unver = {}, 0

    if not structural:
        prec, counts, unver = derive_precision(findings)
        recall = derive_recall(findings, missed)
        calib = derive_calibration(findings)

    for d in DIMS:
        if d in manual:
            scores[d] = float(manual[d])
            source[d] = "manual"
        elif d == "D1" and prec is not None and not structural:
            scores[d] = thresholds(prec, [(0.95, 4), (0.85, 3), (0.70, 2), (0.50, 1)])
            source[d] = "derived from precision %.2f" % prec
        elif d == "D3" and recall is not None and not structural:
            scores[d] = thresholds(recall, [(0.90, 4), (0.75, 3), (0.55, 2), (0.35, 1)])
            source[d] = "derived from reference-set recall %.2f" % recall
        elif d == "D4" and calib is not None and not structural:
            scores[d] = thresholds(calib, [(0.90, 4), (0.75, 3), (0.60, 2), (0.40, 1)])
            source[d] = "derived from severity agreement %.2f" % calib
        else:
            scores[d] = None
            source[d] = "not scored"
    for d in DIMS:
        if scores[d] is not None and not 0 <= scores[d] <= 4:
            raise SystemExit(f"{d}: score must be 0-4")
    required = ["D2", "D5", "D6", "D7", "D8"]
    miss = [d for d in required if scores[d] is None]
    if miss:
        raise SystemExit("missing manual scores for: " + ", ".join(miss))
    if not structural:
        need = [d for d in ("D1", "D3", "D4") if scores[d] is None]
        if need:
            raise SystemExit("full mode needs findings (to derive) or manual scores for: " + ", ".join(need))

    active = [d for d in DIMS if scores[d] is not None]
    wsum = sum(DIMS[d][2] for d in active)
    raw = sum(DIMS[d][2] * scores[d] / 4 for d in active) * (100.0 / wsum)

    caps = []
    for g, cap in CAPS.items():
        if e.get("gates", {}).get(g):
            caps.append((GATE_TEXT[g], cap))
    if prec is not None and prec < 0.5:
        caps.append((GATE_TEXT["precision_below_half"], 60))
    if structural:
        caps.append(("structural mode: findings not verified against the paper", 85))
    final = raw
    if caps:
        final = min(raw, min(c for _, c in caps))
    rows = [{"id": d, "name": DIMS[d][0], "name_ar": DIMS[d][1], "weight": DIMS[d][2],
             "score": scores[d], "points": None if scores[d] is None else round(DIMS[d][2] * scores[d] / 4 * (100.0 / wsum), 1),
             "source": source[d], "note": notes.get(d, "")} for d in DIMS]
    sev_dir = {"inflated": 0, "deflated": 0}
    for f in findings:
        if f.get("severity_claimed") and f.get("severity_true"):
            diff = SEV_LVL[f["severity_claimed"].lower()] - SEV_LVL[f["severity_true"].lower()]
            if diff > 0:
                sev_dir["inflated"] += 1
            elif diff < 0:
                sev_dir["deflated"] += 1
    return {
        "title": e.get("title", ""), "mode": mode, "lang": e.get("lang", "en"),
        "raw_total": round(raw, 1), "final_total": round(final, 1),
        "band": band(final, structural),
        "caps_applied": [{"gate": g, "cap": c} for g, c in caps],
        "dimensions": rows,
        "precision": None if prec is None else round(prec, 3),
        "reference_set_recall": None if recall is None else round(recall, 3),
        "severity_agreement": None if calib is None else round(calib, 3),
        "verdict_counts": counts, "unverifiable": unver,
        "severity_direction": sev_dir,
        "findings": findings, "missed": missed,
        "fixes": e.get("fixes", []), "limits": e.get("limits", []),
        "note": ("Recall is measured against the evaluator's own reference list and is an upper bound; "
                 "structural mode does not verify findings."),
    }


def bench(truth, matches):
    issues = truth["issues"] if isinstance(truth, dict) else truth
    fnd = matches["findings"] if isinstance(matches, dict) else matches
    tid = {i["id"]: i for i in issues}
    hit = {}
    for f in fnd:
        t = f.get("truth_id")
        if t:
            if t not in tid:
                raise SystemExit(f"unknown truth_id {t}")
            hit.setdefault(t, f)
    n = len(issues)
    found = len(hit)
    w_all = sum(SEV_W.get(i.get("severity", "moderate"), 2) for i in issues)
    w_hit = sum(SEV_W.get(tid[t].get("severity", "moderate"), 2) for t in hit)
    assessed = [f for f in fnd if f.get("verdict", "confirmed") != "unverifiable"]
    good = [f for f in assessed if f.get("truth_id") or f.get("verdict") in ("confirmed", "misgraded")]
    prec = len(good) / len(assessed) if assessed else None
    rec = found / n if n else None
    f1 = (2 * prec * rec / (prec + rec)) if prec and rec else 0.0 if (prec is not None and rec is not None) else None
    cats = {}
    for i in issues:
        c = i.get("category", "other")
        d = cats.setdefault(c, {"planted": 0, "found": 0})
        d["planted"] += 1
        d["found"] += 1 if i["id"] in hit else 0
    sev_agree = [abs(SEV_LVL[hit[t].get("severity_claimed", tid[t]["severity"]).lower()] - SEV_LVL[tid[t]["severity"]]) <= 1
                 for t in hit if hit[t].get("severity_claimed")]
    return {
        "planted": n, "found": found, "recall": None if rec is None else round(rec, 3),
        "severity_weighted_recall": None if not w_all else round(w_hit / w_all, 3),
        "precision": None if prec is None else round(prec, 3), "f1": None if f1 is None else round(f1, 3),
        "by_category": {c: {**v, "recall": round(v["found"] / v["planted"], 2)} for c, v in cats.items()},
        "missed": [{"id": i["id"], "category": i.get("category"), "severity": i.get("severity"),
                    "line": i.get("line"), "page": i.get("page"), "mutated": i.get("mutated"), "original": i.get("original")}
                   for i in issues if i["id"] not in hit],
        "severity_agreement_on_hits": None if not sev_agree else round(sum(sev_agree) / len(sev_agree), 2),
        "caution": "Small planted sets give coarse numbers (one miss moves recall by 100/planted points). Use counts, rotate seeds, and read benchmark.md section 5.",
    }


CSS = """
:root{--bg:#0b0f14;--panel:#141b24;--line:#2a3646;--fg:#ffffff;--mut:#c9d4e2;--y:#ffd400;--g:#3ddc84;--r:#ff5c5c;--o:#ffa940;--c:#4cc9f0}
html,body{height:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.55 system-ui,"Segoe UI",Tahoma,Arial,sans-serif;padding:max(16px,env(safe-area-inset-top)) 16px max(24px,env(safe-area-inset-bottom))}
.wrap{max-width:860px;margin:0 auto}
h1{font-size:1.25rem;margin:.2rem 0;color:var(--y)} h2{font-size:1.05rem;margin:1.4rem 0 .5rem;color:var(--y)}
.big{font-size:3rem;font-weight:800;line-height:1} .tag{display:inline-block;padding:.15rem .6rem;border-radius:999px;border:2px solid var(--y);color:var(--y);font-weight:700;margin-inline-start:.5rem}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:10px 0}
.row{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:center;margin:10px 0} .bar{height:12px;background:#243041;border-radius:6px;overflow:hidden;grid-column:1/-1} .bar>i{display:block;height:100%}
.mut{color:var(--mut);font-size:.92rem} table{border-collapse:collapse;width:100%} th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:start;vertical-align:top} th{color:var(--y)}
.scroll{overflow-x:auto} .v-confirmed{color:var(--g)} .v-partial,.v-misgraded,.v-unverifiable{color:var(--o)} .v-false_positive,.v-overreach,.v-not_error{color:var(--r)}
.warn{border-color:var(--r)} li{margin:.25rem 0}
"""


def colour(s):
    return "#3ddc84" if s >= 3.5 else "#ffd400" if s >= 2.5 else "#ffa940" if s >= 1.5 else "#ff5c5c"


def render_html(r, rtl=False):
    ar = rtl or r.get("lang") == "ar"
    t = (lambda en, a: a if ar else en)
    e = H.escape
    out = [f'<!doctype html><html lang="{"ar" if ar else "en"}" dir="{"rtl" if ar else "ltr"}"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
           f"<title>{e(t('Paper evaluation', 'تقييم المراجعة'))}</title><style>{CSS}</style></head><body><div class=\"wrap\">",
           f"<h1>{e(t('Paper evaluation scorecard', 'بطاقة تقييم المراجعة'))}</h1>"]
    if r.get("title"):
        out.append(f'<div class="mut">{e(r["title"])}</div>')
    out.append(f'<div class="card"><span class="big">{r["final_total"]:g}</span><span class="mut"> / 100</span>'
               f'<span class="tag">{e(r["band"])}</span>')
    out.append(f'<div class="mut">{e(t("Mode", "النمط"))}: {e(r["mode"])}'
               + (f' · {e(t("uncapped", "قبل السقف"))} {r["raw_total"]:g}' if r["caps_applied"] else "") + "</div>")
    for c in r["caps_applied"]:
        out.append(f'<div style="color:var(--r)">⚠ {e(c["gate"])} ({e(t("cap", "السقف"))} {c["cap"]})</div>')
    out.append("</div>")
    out.append(f"<h2>{e(t('Dimensions', 'الأبعاد'))}</h2><div class=\"card\">")
    for d in r["dimensions"]:
        sc = d["score"]
        name = d["name_ar"] if ar else d["name"]
        if sc is None:
            out.append(f'<div class="row"><span>{e(d["id"])} {e(name)}</span><span class="mut">{e(t("not scored", "غير مُقيَّم"))}</span></div>')
            continue
        out.append(f'<div class="row"><span>{e(d["id"])} {e(name)} <span class="mut">({d["weight"]})</span></span>'
                   f'<b style="color:{colour(sc)}">{sc:g}/4</b><div class="bar"><i style="width:{sc / 4 * 100:.0f}%;background:{colour(sc)}"></i></div></div>')
        if d.get("note"):
            out.append(f'<div class="mut">{e(d["note"])}</div>')
    out.append("</div>")
    stats = []
    if r["precision"] is not None:
        stats.append(f'{t("Precision", "الدقة")} {r["precision"]:.2f}')
    if r["reference_set_recall"] is not None:
        stats.append(f'{t("Reference-set recall", "التغطية مقابل القائمة المرجعية")} {r["reference_set_recall"]:.2f}')
    if r["severity_agreement"] is not None:
        stats.append(f'{t("Severity agreement", "اتفاق درجة الأثر")} {r["severity_agreement"]:.2f}')
    if stats:
        out.append(f'<div class="card mut">{" · ".join(stats)} · {e(t("unverifiable", "تعذّر التحقق"))}: {r["unverifiable"]}</div>')
    if r["findings"]:
        out.append(f"<h2>{e(t('Finding audit', 'تدقيق الملاحظات'))}</h2><div class=\"card scroll\"><table><tr><th>#</th><th>{e(t('Verdict', 'الحكم'))}</th><th>{e(t('Severity', 'الأثر'))}</th><th>{e(t('Note', 'ملاحظة'))}</th></tr>")
        for f in r["findings"]:
            v = f.get("verdict", "")
            sev = f.get("severity_claimed", "") + (f" → {f['severity_true']}" if f.get("severity_true") and f.get("severity_true") != f.get("severity_claimed") else "")
            out.append(f'<tr><td>{e(str(f.get("id", "")))}</td><td class="v-{e(v)}">{e(v)}</td><td>{e(sev)}</td><td>{e(f.get("note", ""))}</td></tr>')
        out.append("</table></div>")
    if r["missed"]:
        out.append(f"<h2>{e(t('Missed issues', 'ما فات المراجعة'))}</h2><div class=\"card warn\"><ul>")
        for m in r["missed"]:
            out.append(f'<li><b>{e(m.get("severity", ""))}</b> · {e(m.get("location", ""))}: {e(m.get("desc", ""))}'
                       + (f' <span class="mut">[{e(m["evidence"])}]</span>' if m.get("evidence") else "") + "</li>")
        out.append("</ul></div>")
    if r["fixes"]:
        out.append(f"<h2>{e(t('Fix list', 'قائمة الإصلاح'))}</h2><div class=\"card\"><ol>" + "".join(f"<li>{e(x)}</li>" for x in r["fixes"]) + "</ol></div>")
    if r["limits"]:
        out.append(f"<h2>{e(t('Limits of this evaluation', 'حدود هذا التقييم'))}</h2><div class=\"card mut\"><ul>" + "".join(f"<li>{e(x)}</li>" for x in r["limits"]) + "</ul></div>")
    out.append(f'<p class="mut">{e(r["note"])}</p></div></body></html>')
    return "".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("aggregate"); a.add_argument("eval"); a.add_argument("--out")
    b = sub.add_parser("bench"); b.add_argument("truth"); b.add_argument("matches"); b.add_argument("--out")
    h = sub.add_parser("html"); h.add_argument("result"); h.add_argument("out"); h.add_argument("--rtl", action="store_true")
    x = ap.parse_args()
    if x.cmd == "aggregate":
        res = aggregate(json.load(open(x.eval, encoding="utf-8")))
        s = json.dumps(res, ensure_ascii=False, indent=2)
        if x.out:
            open(x.out, "w", encoding="utf-8").write(s)
            print(json.dumps({k: res[k] for k in ("final_total", "raw_total", "band", "caps_applied", "precision", "reference_set_recall", "severity_agreement")}, ensure_ascii=False, indent=2))
        else:
            print(s)
    elif x.cmd == "bench":
        res = bench(json.load(open(x.truth, encoding="utf-8")), json.load(open(x.matches, encoding="utf-8")))
        s = json.dumps(res, ensure_ascii=False, indent=2)
        if x.out:
            open(x.out, "w", encoding="utf-8").write(s)
        print(s)
    else:
        r = json.load(open(x.result, encoding="utf-8"))
        open(x.out, "w", encoding="utf-8").write(render_html(r, x.rtl))
        print("wrote", x.out)


if __name__ == "__main__":
    main()
