#!/usr/bin/env python3
"""
check_numbers.py - offline consistency checks for numbers reported in papers.

Every check answers ONE narrow question: "is this reported number arithmetically
compatible with the other numbers next to it?"  A failed check is a REPORTING
INCONSISTENCY that needs an explanation from the authors. It is not proof of
error in the underlying data and says nothing about intent.

Subcommands (all print JSON):
  pvalue   recompute p from a test statistic + df (statcheck-style, rounding-aware)
  grim     GRIM test: can this mean exist for integer data with n participants?
  percent  does num/den reproduce the reported percentage? (can also search denominators)
  sum      do the parts add up to the reported total (rounding-aware)?
  ci       is a 95% CI consistent with the point estimate and the reported p?
  scan     extract APA-style test results from a text file and check each one

Examples:
  python check_numbers.py pvalue --test t --stat 2.31 --df 28 --p .03
  python check_numbers.py pvalue --test F --stat 3.10 --df 2 --df2 45 --p "<.05"
  python check_numbers.py grim --mean 3.45 --n 28
  python check_numbers.py percent --num 24 --den 96 --reported 25.0 --find-denominator
  python check_numbers.py sum --parts 12,15,30 --total 60
  python check_numbers.py ci --est 1.52 --lo 1.10 --hi 2.10 --ratio --p 0.01
  python check_numbers.py scan paper.txt
"""
import argparse
import json
import math
import re
import sys
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_HALF_DOWN, InvalidOperation

try:
    from scipy import stats
except ImportError:  # pragma: no cover
    sys.exit("scipy is required: pip install scipy --break-system-packages")

ALPHA = 0.05


# ----------------------------------------------------------------- helpers
def dec_places(s: str) -> int:
    s = norm_num(s)
    return len(s.split(".")[1]) if "." in s else 0


_DIGITS = str.maketrans({
    **{chr(0x0660 + i): str(i) for i in range(10)},   # Arabic-Indic digits
    **{chr(0x06F0 + i): str(i) for i in range(10)},   # Persian digits
    "\u066b": ".",   # Arabic decimal separator
    "\u066c": ",",   # Arabic thousands separator
    "\u2212": "-", "\u2013": "-",
})


def norm_num(s: str) -> str:
    """Normalise Arabic-Indic/Persian digits, Arabic decimal mark and unicode minus."""
    return str(s).translate(_DIGITS).strip()


def parse_p(s: str):
    """'.03' -> ('=', 0.03, 2); '<.001' -> ('<', 0.001, 3)."""
    s = norm_num(s).replace("\u2264", "<=").replace("\u2265", ">=")
    m = re.match(r"^(<=|>=|<|>|=)?\s*(\d*\.?\d+)$", s)
    if not m:
        raise ValueError(f"cannot parse p-value: {s!r}")
    rel = m.group(1) or "="
    rel = {"<=": "<", ">=": ">"}.get(rel, rel)
    return rel, float(m.group(2)), dec_places(m.group(2))


def p_from_stat(test, x, df1, df2=None):
    """Two-tailed p for t / z / r, upper-tail p for F / chi2 (x >= 0 for the latter)."""
    if test == "t":
        return 2 * stats.t.sf(abs(x), df1)
    if test == "z":
        return 2 * stats.norm.sf(abs(x))
    if test == "r":
        r = min(abs(x), 0.999999999)
        t = r * math.sqrt(df1 / (1 - r * r))
        return 2 * stats.t.sf(t, df1)
    if test == "F":
        return stats.f.sf(x, df1, df2)
    if test == "chi2":
        return stats.chi2.sf(x, df1)
    raise ValueError(test)


# ----------------------------------------------------------------- pvalue
def check_pvalue(test, stat_str, df1, df2, p_str):
    stat_str = norm_num(stat_str)
    x = float(stat_str)
    d = dec_places(stat_str)
    h = 0.5 * 10 ** (-d)
    ax = abs(x)
    lo_x, hi_x = max(ax - h, 0.0), ax + h
    if test == "r":
        hi_x = min(hi_x, 0.999999999)
    # p decreases as |stat| increases
    p_nom = p_from_stat(test, ax, df1, df2)
    p_hi = p_from_stat(test, lo_x, df1, df2)
    p_lo = p_from_stat(test, hi_x, df1, df2)

    rel, rep, dp = parse_p(p_str)
    hp = 0.5 * 10 ** (-dp)

    def consistent(plo, phi):
        if rel == "=":
            return plo <= rep + hp and phi >= rep - hp
        if rel == "<":
            return plo < rep
        return phi > rep  # '>'

    ok = consistent(p_lo, p_hi)
    status = "CONSISTENT" if ok else "INCONSISTENT"
    note = None
    if not ok and test in ("t", "z", "r") and consistent(p_lo / 2, p_hi / 2):
        status = "CONSISTENT_IF_ONE_TAILED"
        note = ("Matches only if the test was one-tailed. Check whether the paper "
                "states and justifies a one-tailed test.")

    decision_error = False
    if status == "INCONSISTENT":
        rep_sig = (rel == "<" and rep <= ALPHA) or (rel == "=" and rep < ALPHA)
        calc_sig = bool(p_nom < ALPHA)
        decision_error = bool(rep_sig != calc_sig)

    return {
        "test": test,
        "stat": x,
        "df": [df1] if df2 is None else [df1, df2],
        "reported_p": f"{rel}{p_str.strip().lstrip('=<>')}",
        "recomputed_p_nominal": round(p_nom, 6),
        "recomputed_p_range_given_rounding": [round(p_lo, 6), round(p_hi, 6)],
        "status": status,
        "decision_error_at_0.05": decision_error,
        "note": note,
    }


# ------------------------------------------------------------------- grim
_ROUNDINGS = {"half_up": ROUND_HALF_UP, "half_even": ROUND_HALF_EVEN, "half_down": ROUND_HALF_DOWN}


def check_grim(mean_str, n, items=1):
    decimals = dec_places(mean_str)
    mean = Decimal(mean_str)
    N = n * items
    if N >= 10 ** decimals:
        return {
            "mean": mean_str, "n": n, "items": items, "status": "NOT_INFORMATIVE",
            "note": (f"With n*items={N} and {decimals} decimals every mean is attainable, "
                     "so GRIM cannot detect anything. Needs integer data and small n."),
        }
    q = Decimal(1).scaleb(-decimals)
    centre = float(mean) * N
    matched = {}
    for name, mode in _ROUNDINGS.items():
        for S in range(max(0, math.floor(centre) - 1), math.ceil(centre) + 2):
            cand = (Decimal(S) / Decimal(N)).quantize(q, rounding=mode)
            if cand == mean:
                matched[name] = S
                break
    if "half_up" in matched:
        status, note = "CONSISTENT", None
    elif matched:
        status = "CONSISTENT_ONLY_UNDER_ALT_ROUNDING"
        note = f"Attainable only with rounding mode(s): {sorted(matched)}."
    else:
        status = "INCONSISTENT"
        nearest = sorted({round(S / N, decimals) for S in
                          range(max(0, math.floor(centre) - 1), math.ceil(centre) + 2)})
        note = ("No integer total gives this mean. Nearest attainable means: "
                f"{nearest}. Possible causes: non-integer data, missing values so the "
                "true n is smaller, wrong n, or a typo.")
    return {"mean": mean_str, "n": n, "items": items, "status": status,
            "matched_rounding": matched, "note": note}


# ---------------------------------------------------------------- percent
def check_percent(num, den, reported_str, find_den=False):
    reported_str = norm_num(reported_str).rstrip("%")
    dp = dec_places(reported_str)
    rep = Decimal(reported_str)
    q = Decimal(1).scaleb(-dp)
    calc = Decimal(num) / Decimal(den) * 100
    rounded = calc.quantize(q, rounding=ROUND_HALF_UP)
    out = {
        "num": num, "den": den, "reported": reported_str,
        "recomputed": float(calc), "recomputed_rounded": float(rounded),
        "status": "CONSISTENT" if rounded == rep else "INCONSISTENT",
    }
    if find_den and out["status"] == "INCONSISTENT":
        cands = [d for d in range(max(num, 1), 5001)
                 if (Decimal(num) / Decimal(d) * 100).quantize(q, rounding=ROUND_HALF_UP) == rep]
        out["denominators_that_reproduce_reported_value"] = cands[:15]
        out["note"] = ("A percentage that fits a different denominator often means the "
                       "percentage was computed on a subgroup or on n before exclusions.")
    return out


# -------------------------------------------------------------------- sum
def check_sum(parts, total, decimals=None):
    dps = [dec_places(p) for p in parts] + [dec_places(total)]
    dp = decimals if decimals is not None else max(dps)
    vals = [Decimal(norm_num(p)) for p in parts]
    tot = Decimal(norm_num(total))
    s = sum(vals)
    tol = Decimal(len(vals)) * Decimal("0.5") * Decimal(1).scaleb(-dp) if dp else Decimal(0)
    diff = s - tot
    within_rounding = abs(diff) <= tol
    if diff == 0:
        status = "CONSISTENT"
    elif within_rounding:
        status = "CONSISTENT_WITHIN_ROUNDING"
    else:
        status = "INCONSISTENT"
    return {"parts": [str(v) for v in vals], "sum_of_parts": str(s), "reported_total": str(tot),
            "difference": str(diff), "rounding_tolerance": str(tol), "status": status}


# --------------------------------------------------------------------- ci
def check_ci(est, lo, hi, ratio=False, p_str=None, level=0.95):
    z_crit = stats.norm.ppf(1 - (1 - level) / 2)
    out = {"estimate": est, "ci": [lo, hi], "ratio_measure": ratio, "level": level}
    if lo >= hi:
        out["status"] = "INCONSISTENT"
        out["note"] = "Lower bound is not below upper bound."
        return out
    if not (lo <= est <= hi):
        out["status"] = "INCONSISTENT"
        out["note"] = "Point estimate lies outside its own confidence interval."
        return out
    if ratio:
        if min(est, lo, hi) <= 0:
            out["status"] = "INCONSISTENT"
            out["note"] = "Ratio measures (OR/HR/RR) must be > 0."
            return out
        se = (math.log(hi) - math.log(lo)) / (2 * z_crit)
        z = math.log(est) / se
        centre = math.sqrt(lo * hi)
        out["geometric_midpoint_of_ci"] = round(centre, 4)
    else:
        se = (hi - lo) / (2 * z_crit)
        z = est / se
        out["arithmetic_midpoint_of_ci"] = round((lo + hi) / 2, 4)
    p_calc = 2 * stats.norm.sf(abs(z))
    out.update({"implied_se": round(se, 6), "implied_p_normal_approx": round(p_calc, 6)})
    out["status"] = "CONSISTENT"
    if p_str is not None:
        rel, rep, dp = parse_p(p_str)
        hp = 0.5 * 10 ** (-dp)
        ok = {"=": abs(p_calc - rep) <= hp + 0.15 * rep,  # loose: inputs are rounded
              "<": p_calc < rep * 1.15, ">": p_calc > rep * 0.85}[rel]
        if not ok:
            out["status"] = "INCONSISTENT"
            out["note"] = (f"Reported p ({p_str}) does not match the p implied by the CI "
                           f"(~{p_calc:.4f}). Normal approximation; small samples use t, so "
                           "treat small gaps with caution.")
        # CI excluding null but p >= .05 (or vice-versa)
        null = 1.0 if ratio else 0.0
        excludes_null = not (lo <= null <= hi)
        if (rel == "=" and (rep < ALPHA) != excludes_null) or (rel == "<" and rep <= ALPHA and not excludes_null):
            out["status"] = "INCONSISTENT"
            out["note"] = ("CI and p disagree about significance at 0.05 "
                           f"(CI {'excludes' if excludes_null else 'includes'} the null value {null}).")
    return out


# ------------------------------------------------------------------- scan
_P = r"[pP]\s*(<=|>=|<|>|=|\u2264|\u2265)\s*(\d*\.\d+|\d+)"
_SEP = r"\s*[,;\u060c\u061b]\s*"
_NUM = r"(-?\d*\.\d+|-?\d+)"
PATTERNS = [
    ("t", re.compile(r"\bt\s*\(\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*" + _NUM + _SEP + _P)),
    ("F", re.compile(r"\bF\s*\(\s*(\d+)\s*,\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*" + _NUM + _SEP + _P)),
    ("chi2", re.compile(r"(?:\u03c7\s*[\u00b22]?|chi\s*-?\s*(?:square|squared)?\s*[\u00b22]?)\s*\(\s*(\d+)"
                        r"(?:\s*,\s*[Nn]\s*=\s*\d+)?\s*\)\s*=\s*" + _NUM + _SEP + _P, re.I)),
    ("r", re.compile(r"\br\s*\(\s*(\d+)\s*\)\s*=\s*" + _NUM + _SEP + _P)),
    ("z", re.compile(r"\bz\s*=\s*" + _NUM + _SEP + _P)),
]
_NMENT = re.compile(r"\b[nN]\s*=\s*(\d[\d,]*)")


def scan_text(text):
    text = norm_num(text)
    results, seen = [], set()
    for test, rx in PATTERNS:
        for m in rx.finditer(text):
            g = m.groups()
            try:
                if test == "F":
                    df1, df2, stat, rel, pv = int(g[0]), float(g[1]), g[2], g[3], g[4]
                elif test == "z":
                    df1, df2, stat, rel, pv = None, None, g[0], g[1], g[2]
                else:
                    df1, df2, stat, rel, pv = float(g[0]), None, g[1], g[2], g[3]
                    df1 = int(df1) if float(df1).is_integer() else df1
                if test in ("F", "chi2") and float(stat) < 0:
                    continue
                res = check_pvalue(test, stat, df1, df2, f"{rel}{pv}")
            except Exception as e:  # keep scanning
                res = {"test": test, "status": "PARSE_ERROR", "error": str(e)}
            s, e = m.span()
            key = (test, s)
            if key in seen:
                continue
            seen.add(key)
            res["offset"] = s
            res["context"] = re.sub(r"\s+", " ", text[max(0, s - 50): e + 30])
            results.append(res)
    results.sort(key=lambda r: r["offset"])
    n_mentions = [{"n": m.group(1), "offset": m.start(),
                   "context": re.sub(r"\s+", " ", text[max(0, m.start() - 40): m.end() + 30])}
                  for m in _NMENT.finditer(text)]
    summary = {}
    for r in results:
        summary[r["status"]] = summary.get(r["status"], 0) + 1
    return {"tests_found": len(results), "summary": summary,
            "decision_errors": sum(1 for r in results if r.get("decision_error_at_0.05")),
            "results": results, "n_mentions": n_mentions,
            "caveat": ("Only APA-style results (e.g. 't(28) = 2.31, p = .03') are detected. "
                       "Results in tables, figures, other notations, or split across lines may be missed. "
                       "A flag means 'needs explanation', not 'wrong'.")}


# ------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("pvalue")
    a.add_argument("--test", required=True, choices=["t", "F", "chi2", "z", "r"])
    a.add_argument("--stat", required=True, help="as printed in the paper (decimals matter)")
    a.add_argument("--df", type=float, required=False, help="df (t, chi2, r) or numerator df (F)")
    a.add_argument("--df2", type=float, help="denominator df for F")
    a.add_argument("--p", required=True, help="as printed, e.g. .03 or '<.001'")

    g = sub.add_parser("grim")
    g.add_argument("--mean", required=True, help="as printed, e.g. 3.45")
    g.add_argument("--n", type=int, required=True)
    g.add_argument("--items", type=int, default=1, help="items per scale if the mean is over items")

    c = sub.add_parser("percent")
    c.add_argument("--num", type=int, required=True)
    c.add_argument("--den", type=int, required=True)
    c.add_argument("--reported", required=True)
    c.add_argument("--find-denominator", action="store_true")

    s = sub.add_parser("sum")
    s.add_argument("--parts", required=True, help="comma separated, as printed")
    s.add_argument("--total", required=True)
    s.add_argument("--decimals", type=int)

    ci = sub.add_parser("ci")
    ci.add_argument("--est", type=float, required=True)
    ci.add_argument("--lo", type=float, required=True)
    ci.add_argument("--hi", type=float, required=True)
    ci.add_argument("--ratio", action="store_true", help="OR / HR / RR (log scale)")
    ci.add_argument("--p", help="reported p-value, optional")
    ci.add_argument("--level", type=float, default=0.95)

    sc = sub.add_parser("scan")
    sc.add_argument("file", help="plain-text file (use pdftotext -layout for PDFs)")

    args = ap.parse_args(argv)
    if args.cmd == "pvalue":
        if args.df is None and args.test != "z":
            ap.error("--df is required for this test")
        if args.test == "F" and args.df2 is None:
            ap.error("--df2 is required for F")
        df1 = int(args.df) if args.df is not None and float(args.df).is_integer() else args.df
        out = check_pvalue(args.test, args.stat, df1, args.df2, args.p)
    elif args.cmd == "grim":
        out = check_grim(args.mean, args.n, args.items)
    elif args.cmd == "percent":
        out = check_percent(args.num, args.den, args.reported, args.find_denominator)
    elif args.cmd == "sum":
        out = check_sum([x.strip() for x in args.parts.split(",")], args.total, args.decimals)
    elif args.cmd == "ci":
        out = check_ci(args.est, args.lo, args.hi, args.ratio, args.p, args.level)
    else:
        with open(args.file, encoding="utf-8", errors="replace") as f:
            out = scan_text(f.read())
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
