"""Pone a la bibliografia el formato de J.UCS: etiqueta [Apellido, AA] en cada entrada y orden alfabetico.

Se ejecuta despues de bibtex (estilo ieeetr) y antes de las dos ultimas pasadas de lualatex:
    lualatex main && bibtex main && python jucs_labels.py && lualatex main && lualatex main
"""
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent


def fields(bib):
    out = {}
    for m in re.finditer(r"@\w+\{([^,]+),(.*?)\n\}", bib, re.S):
        f = dict((k.lower(), v) for k, v in re.findall(r"(\w+)\s*=\s*\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}", m.group(2)))
        out[m.group(1).strip()] = f
    return out


def surname(author):
    first = re.split(r"\s+and\s+", author.strip())[0]
    if first.startswith("{") and first.endswith("}"):
        name = first[1:-1]
    else:
        name = first.split(",")[0] if "," in first else first.split()[-1]
    name = re.sub(r"\\[a-zA-Z]+\s*|[{}\\'`^\"~]", "", name)
    return unicodedata.normalize("NFC", name).strip()


bib = fields((HERE / "refs.bib").read_text(encoding="utf-8"))
bbl = (HERE / "main.bbl").read_text(encoding="utf-8")
head, rest = bbl.split("\\bibitem", 1)
items = [x for x in re.split(r"(?=\\bibitem)", "\\bibitem" + rest) if x.strip()]
tail = ""
if "\\end{thebibliography}" in items[-1]:
    items[-1], tail = items[-1].split("\\end{thebibliography}")
    tail = "\\end{thebibliography}" + tail

labelled = []
for it in items:
    key = re.match(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", it).group(1)
    f = bib[key]
    who = surname(f.get("author") or f.get("organization") or f.get("institution") or key)
    yy = re.sub(r"\D", "", f.get("year", ""))[-2:]
    labelled.append([who, yy, key, it])

# Desempate: misma etiqueta -> a, b, ...
seen = {}
for row in sorted(labelled, key=lambda r: (r[0].lower(), r[1], r[2])):
    seen.setdefault((row[0], row[1]), []).append(row)
out = []
for (who, yy), rows in sorted(seen.items(), key=lambda kv: (kv[0][0].lower(), kv[0][1])):
    for i, (w, y, key, it) in enumerate(rows):
        suf = chr(97 + i) if len(rows) > 1 else ""
        label = f"{w}, {y}{suf}"
        out.append(re.sub(r"\\bibitem(?:\[[^\]]*\])?\{" + re.escape(key) + r"\}", lambda m: f"\\bibitem[{label}]{{{key}}}", it, count=1))
(HERE / "main.bbl").write_text(head.replace("\\begin{thebibliography}{10}", "\\begin{thebibliography}{}") + "".join(out).rstrip() + "\n\n" + tail,
                               encoding="utf-8")
print(len(out), "referencias con etiqueta")
