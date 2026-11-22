#!/usr/bin/env python3
"""Szkennelt határozati kivonatok feldolgozása a Döntéskövetőhöz.

Használat:
    python3 nyitott/tools/ocr_hatarozatok.py <pdf-mappa vagy fájlok...> [--out nyitott/adatok/hatarozat-reszletek.json]

Mit csinál:
  1. Minden PDF-oldalt képpé alakít (pdftoppm), és magyar nyelvű szövegfelismerést futtat (tesseract, "hun").
  2. Kiolvassa a határozat számát, a szövegét, a felelőst és a határidőt.
  3. Beírja vagy frissíti a hatarozat-reszletek.json megfelelő tételét.
     A kézzel kitöltött mezőket (szavazas, vegrehajtas, vegrehajtas_megjegyzes, hatarido_datum)
     NEM írja felül, ha már van bennük érték.

Szükséges: poppler-utils (pdftoppm), tesseract-ocr és tesseract-ocr-hun.
    Ubuntu: sudo apt-get install poppler-utils tesseract-ocr tesseract-ocr-hun
    macOS:  brew install poppler tesseract tesseract-lang

A felismert szöveget mindig ellenőrizd a PDF-fel, mielőtt közzéteszed: a nevek és a számok
a leggyakoribb hibaforrások.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile

HONAPOK = {"január": 1, "február": 2, "március": 3, "április": 4, "május": 5, "június": 6,
           "július": 7, "augusztus": 8, "szeptember": 9, "október": 10, "november": 11, "december": 12}


def ocr_pdf(path):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", "300", "-png", path, os.path.join(tmp, "p")], check=True)
        texts = []
        for f in sorted(os.listdir(tmp)):
            r = subprocess.run(["tesseract", os.path.join(tmp, f), "-", "-l", "hun"],
                               capture_output=True, text=True, check=True)
            texts.append(r.stdout)
        return "\n".join(texts)


def clean(s):
    s = s.replace("=====OLDAL=====", "")
    s = re.sub(r"HERCEGHALOMI POLGÁRMESTERI HIVATAL[^\n]*\n[^\n]*Gesztenyés út 13\.[^\n]*\n[^\n]*Tel\.[^\n]*", "", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"-\n(?=[a-záéíóöőúüű])", "", s)  # elválasztás
    # számozott pontok és bekezdések új sorba, a többi sortörés szóköz
    s = re.sub(r"\s*\n\s*(?=\d{1,2}\.\s)", "\n", s)
    s = re.sub(r"(?<!\n)\s*\n\s*(?!\d{1,2}\.\s)", " ", s)
    return s.strip()


KT = re.compile(r"Herceghalom\s*[—–-]?\s*Község\s*[—–-]?\s*Önkorm[áa]n\s?y?zat(?:ának|a)\s*[—–-]?\s*Képviselő\s*-?\s*testülete")
ROLE = re.compile(r"polgármester|jegyző|igazgató|vezető|elnök|képviselő|előadó|pont", re.I)
# A határozat fejléce: "...Képviselő-testületének NN/ÉÉÉÉ. (..) számú határozata"
NUM = re.compile(r"testületének\s*\n?\s*(\d{1,3})\s*/\s*(20\d\d)\s*\.?[^\n]{0,25}?sz[áa]m[úu]\s*hat[áa]rozat", re.I)
NEVEK = [(re.compile(r"C[sz]i[sz]madia\s+Zsuzsann?a"), "Csizmadia Zsuzsanna"),
         (re.compile(r"(dr\.?\s*)?Verh[óo]c[zk]+i\s+Zita", re.I), "dr. Verhóczki Zita"),
         (re.compile(r"(dr\.?\s*)?S[zZ]elenc[zs]y\s+Gabriella", re.I), "dr. Szelenczy Gabriella")]


def fix_names(s):
    for rx, good in NEVEK:
        s = rx.sub(good, s)
    return s


def _good_line(ln):
    letters = sum(c.isalpha() for c in ln)
    words = re.findall(r"[a-záéíóöőúüű]{3,}", ln, re.I)
    if not ln or letters < 0.75 * len(ln.replace(" ", "")) or len(words) < 1:
        return False
    if re.search(r"HERCEGHALOMI POLGÁRMESTERI|kmf", ln):
        return False
    if re.fullmatch(r"(dr\.\s*)?[A-ZÁÉÍÓÖŐÚÜŰ][\w.]+\s+[A-ZÁÉÍÓÖŐÚÜŰ]\w+(\s+(dr\.\s*)?[A-ZÁÉÍÓÖŐÚÜŰ]\w+\s+[A-ZÁÉÍÓÖŐÚÜŰ]\w+)?", ln.strip()):
        return False  # aláírók nevei
    if re.fullmatch(r"(polgármester|jegyző|polgármester\s+jegyző)", ln.strip()):
        return False
    return True


def _field(text, label, stop):
    m = re.search(label + r"\s*:?\s*(.*)", text)
    if not m:
        return ""
    out = [m.group(1).strip()]
    for ln in text[m.end():].split("\n")[1:]:
        ln = ln.strip()
        if not ln or re.match(stop, ln) or not _good_line(ln):
            break
        out.append(ln)
    v = " ".join(out)
    return v


def _felelos(text):
    v = _field(text, r"Felel[őo]s(?=\s*:)", r"Hat[áa]rid")
    v = re.sub(r"^[\s—–-]+", "", v)
    return fix_names(v).rstrip(" .,")


def _hatarido(text):
    v = _field(text, r"Hat[áa]rid[őo](?=\s*:)", r"Felel[őo]s")
    v = re.split(r"\s{2,}|\s(?=[^\wáéíóöőúüű,.()/:;–-])", v)[0] if not re.search(r"\w\s+\w", v) else v
    # a sor végi szemét levágása
    v = re.sub(r"(\s+\S{1,3}){2,}\s*$", "", v) if re.search(r"[!?|\]\[]", v) else v
    v = re.sub(r"[\s.\"'’]+$", "", v)
    return v


def _body(block):
    fel = re.search(r"Felel[őo]s\s*:", block)
    body = block[:fel.start()] if fel else block
    body = KT.sub("A Képviselő-testület", body)
    m = re.search(r"(?:^|\n)\s*(?:\d{1,2}\.\)?\s|A Képviselő-testület|I\.\s)", body)
    title = clean(body[:m.start()]) if m else ""
    txt = clean(body[m.start():] if m else body)
    txt = re.sub(r"^(\d{1,2})\.\)", r"\1.", txt, flags=re.M)
    return title, fix_names(txt)


def parse(text):
    """Egy vagy több határozat kiolvasása egy kivonat szövegéből."""
    out = {}
    starts = list(NUM.finditer(text))
    for i, m in enumerate(starts):
        num = f"{int(m.group(1))}/{m.group(2)}"
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        block = text[m.end():end]
        if not re.search(r"Felel[őo]s\s*:", block) and len(starts) == 1:
            first = re.search(r"^\s*1\.\s", text, re.M)
            block = text[first.start():] if first else text
        block = block.split("=====OLDAL=====\nMelléklet")[0]
        title, szoveg = _body(block)
        hatarido = _hatarido(block)
        out[num] = {
            "cim_ocr": title,
            "szoveg": szoveg,
            "felelos": _felelos(block),
            "hatarido": hatarido,
            "hatarido_datum_javaslat": deadline_iso(hatarido),
        }
    return out


def deadline_iso(s):
    m = re.search(r"(20\d\d)\.\s*([a-záéíóöőúüű]+)\s*(\d{1,2})", s or "")
    if m and m.group(2) in HONAPOK:
        try:
            return dt.date(int(m.group(1)), HONAPOK[m.group(2)], int(m.group(3))).isoformat()
        except ValueError:
            return ""
    m = re.search(r"(20\d\d)\.\s*(\d{1,2})\.\s*(\d{1,2})", s or "")
    if m:
        try:
            return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
        except ValueError:
            return ""
    return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="PDF-fájlok vagy mappák")
    ap.add_argument("--out", default="nyitott/adatok/hatarozat-reszletek.json")
    ap.add_argument("--hatarido-azonnal", action="store_true",
                    help='"azonnal" határidőnél az ülés napját írja a hatarido_datum mezőbe (az ülés dátumát a PDF fejlécéből olvassa)')
    a = ap.parse_args()

    files = []
    for p in a.inputs:
        if os.path.isdir(p):
            files += [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.lower().endswith(".pdf")]
        else:
            files.append(p)

    data = {"frissitve": "", "hatarozatok": {}}
    if os.path.exists(a.out):
        data = json.load(open(a.out, encoding="utf-8"))
    H = data.setdefault("hatarozatok", {})

    found = 0
    for f in files:
        try:
            text = ocr_pdf(f)
        except Exception as e:  # noqa: BLE001
            print(f"HIBA {f}: {e}", file=sys.stderr)
            continue
        res = parse(text)
        if not res:
            print(f"nem találtam határozatszámot: {f}", file=sys.stderr)
        ulesnap = ""
        m = re.search(r"(20\d\d)\.\s*([a-záéíóöőúüű]+)\s*(\d{1,2})\.\s*napján", text)
        if m and m.group(2) in HONAPOK:
            ulesnap = dt.date(int(m.group(1)), HONAPOK[m.group(2)], int(m.group(3))).isoformat()
        for num, r in res.items():
            e = H.setdefault(num, {"szavazas": None, "vegrehajtas": "", "vegrehajtas_megjegyzes": "", "hatarido_datum": ""})
            for k in ("szoveg", "felelos", "hatarido"):
                if r[k]:
                    e[k] = r[k]
            if not e.get("hatarido_datum"):
                if r["hatarido_datum_javaslat"]:
                    e["hatarido_datum"] = r["hatarido_datum_javaslat"]
                elif a.hatarido_azonnal and r["hatarido"].lower().startswith("azonnal") and ulesnap:
                    e["hatarido_datum"] = ulesnap
            e.setdefault("szavazas", None)
            e["forras"] = "határozati kivonat (szövegfelismeréssel, ellenőrizendő)"
            found += 1
            print(f"{num}: {r['cim_ocr'][:60]} | felelős: {r['felelos'][:40]} | határidő: {r['hatarido'][:40]}")

    data["frissitve"] = dt.date.today().isoformat()
    data["hatarozatok"] = dict(sorted(H.items(), key=lambda kv: (kv[0].split("/")[1], int(kv[0].split("/")[0]))))
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"{found} határozat feldolgozva → {a.out}")


if __name__ == "__main__":
    main()
