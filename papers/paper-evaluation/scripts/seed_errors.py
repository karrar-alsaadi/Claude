#!/usr/bin/env python3
"""
seed_errors.py - plant known errors in a paper's plain text and write an answer key,
so recall of paper-find-misstake can be measured without relying on the evaluator's judgement.

  python seed_errors.py paper.txt --n 8 --seed 11 --out-dir bench/

Writes  <out-dir>/<name>_seeded.txt  and  <out-dir>/truth.json.
Operations (each used at most as often as candidates exist, round-robin):
  pvalue_flip   p-value moved across .05                      (statistical, substantial)
  n_change      one "n = N" altered by about 10%               (numerical, substantial)
  percent_shift one percentage shifted by 6-14 points          (numerical, moderate)
  direction     higher/lower, increased/decreased swapped      (interpretive, substantial)
  df_change     degrees of freedom in t(df)/F(df1,df2) altered (statistical, moderate)
  causal        "associated with" -> "causes"                  (interpretive, substantial)
  typo          two adjacent letters swapped in a long word    (typographical, minor)
Form feeds (\\f) are preserved so page numbers in truth.json match the seeded file.
Read the diff before use: a mutation can create a second, unintended inconsistency.
"""
import argparse
import json
import os
import random
import re

SWAPS = [("higher", "lower"), ("lower", "higher"), ("increased", "decreased"), ("decreased", "increased"),
         ("greater", "smaller"), ("smaller", "greater"), ("upregulated", "downregulated"), ("downregulated", "upregulated"),
         ("improved", "worsened"), ("more", "fewer")]

OPS = [
    ("pvalue_flip", "statistical", "substantial", re.compile(r"\bp\s*([=<])\s*(0?\.\d+)")),
    ("n_change", "numerical", "substantial", re.compile(r"\b[nN]\s*=\s*(\d{2,})")),
    ("percent_shift", "numerical", "moderate", re.compile(r"(\d{1,3}(?:\.\d+)?)\s?%")),
    ("direction", "interpretive", "substantial", re.compile(r"\b(" + "|".join(a for a, _ in SWAPS) + r")\b")),
    ("df_change", "statistical", "moderate", re.compile(r"\b[tT]\((\d+)\)")),
    ("causal", "interpretive", "substantial", re.compile(r"\b(?:was |were |is |are )?associated with\b")),
    ("typo", "typographical", "minor", re.compile(r"\b[a-z]{8,}\b")),
]


def mutate(op, m, rnd):
    g = m.group(0)
    if op == "pvalue_flip":
        v = float(m.group(2) if m.group(2).startswith("0") or m.group(2).startswith(".") else "0" + m.group(2))
        new = ".07" if v < 0.05 else ".03"
        lead = "0" if m.group(2).startswith("0") else ""
        return g.replace(m.group(2), lead + new)
    if op == "n_change":
        n = int(m.group(1))
        d = max(2, round(n * rnd.uniform(0.08, 0.12)))
        return g.replace(m.group(1), str(n + rnd.choice([-1, 1]) * d))
    if op == "percent_shift":
        v = float(m.group(1))
        nv = v + rnd.choice([-1, 1]) * rnd.uniform(6, 14)
        nv = min(99.0, max(1.0, nv))
        txt = f"{nv:.1f}" if "." in m.group(1) else f"{round(nv)}"
        return g.replace(m.group(1), txt)
    if op == "direction":
        w = m.group(1)
        return g.replace(w, dict(SWAPS)[w])
    if op == "df_change":
        return g.replace(m.group(1), str(int(m.group(1)) + rnd.choice([-6, -4, 5, 8])))
    if op == "causal":
        return "causes"
    if op == "typo":
        w = g
        i = rnd.randrange(2, len(w) - 2)
        return w[:i] + w[i + 1] + w[i] + w[i + 2:]
    return g


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paper")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out-dir", default="bench")
    a = ap.parse_args()
    rnd = random.Random(a.seed)
    text = open(a.paper, encoding="utf-8", errors="replace").read()
    cands = {}
    for op, cat, sev, rx in OPS:
        ms = list(rx.finditer(text))
        if op == "n_change" and len(ms) > 1:
            ms = ms[1:]                       # keep the first n as the anchor
        if op == "typo":
            ms = [m for m in ms if m.group(0).lower() not in {"associated"}]
        rnd.shuffle(ms)
        cands[op] = ms
    chosen, taken = [], []

    def free(m):
        return all(m.end() + 25 < s or m.start() - 25 > e for s, e in taken)

    order = [o[0] for o in OPS]
    rnd.shuffle(order)
    guard = 0
    while len(chosen) < a.n and guard < 200 and any(cands.values()):
        guard += 1
        for op in order:
            if len(chosen) >= a.n:
                break
            while cands[op]:
                m = cands[op].pop()
                if free(m):
                    taken.append((m.start(), m.end()))
                    chosen.append((op, m))
                    break
    chosen.sort(key=lambda x: x[1].start())
    meta = {o[0]: o for o in OPS}
    truth, out, pos = [], [], 0
    for k, (op, m) in enumerate(chosen, 1):
        new = mutate(op, m, rnd)
        out.append(text[pos:m.start()])
        out.append(new)
        pos = m.end()
        line = text.count("\n", 0, m.start()) + 1
        page = text.count("\f", 0, m.start()) + 1
        truth.append({"id": f"S{k}", "op": op, "category": meta[op][1], "severity": meta[op][2],
                      "line": line, "page": page, "original": text[max(0, m.start() - 30): m.end() + 30].replace("\n", " "),
                      "mutated": (text[max(0, m.start() - 30): m.start()] + new + text[m.end(): m.end() + 30]).replace("\n", " ")})
    out.append(text[pos:])
    os.makedirs(a.out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(a.paper))[0]
    sp = os.path.join(a.out_dir, base + "_seeded.txt")
    open(sp, "w", encoding="utf-8").write("".join(out))
    json.dump({"source": a.paper, "seed": a.seed, "issues": truth}, open(os.path.join(a.out_dir, "truth.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"planted {len(truth)} of requested {a.n}; wrote {sp} and {os.path.join(a.out_dir, 'truth.json')}")
    for t in truth:
        print(f"  {t['id']} {t['op']:<13} p{t['page']} L{t['line']}: ...{t['original']}...  ->  ...{t['mutated']}...")


if __name__ == "__main__":
    main()
