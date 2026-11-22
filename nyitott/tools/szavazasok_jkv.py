#!/usr/bin/env python3
"""Szavazási arányok kiolvasása a képviselő-testületi jegyzőkönyvekből a Döntéskövetőhöz.

Használat:
    python3 nyitott/tools/szavazasok_jkv.py <jegyzőkönyv-PDF-ek vagy mappa> [--out nyitott/adatok/hatarozat-reszletek.json]

A jegyzőkönyvek mondatait keresi: „A Képviselő-testület jelenlévő 6 tagja 5 igen szavazattal,
1 nem szavazattal, tartózkodás nélkül az alábbi határozatot hozta: … NN/ÉÉÉÉ. (…) számú határozata”,
és a szavazást a határozat számához írja. Csak a meglévő tételeket frissíti, a kézi
szavazas-adatot nem írja felül. Szükséges hozzá ugyanaz, mint az ocr_hatarozatok.py-hoz.
A gyanús tételeket (pl. ha az összeg nem egyezik a jelenlévők számával) kiírja: ezeket a PDF-ben ellenőrizd.
"""
import argparse, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from ocr_hatarozatok import ocr_pdf  # noqa: E402

NUMW = r"(\d{1,3})\s*/\s*(20\d\d)\s*[.,]?\s*\([^)\n]{0,15}\)?\)?\s*sz[áa]m[úu]\s*hat[áa]rozat"
VOTE = (r"(?:Képviselő-?\s?testület\s+|,\s*)jelen\s?lévő\s+(\d+)\s+tagja,?\s*(egyhangúlag,?)?\s*(\d+)\s+igen\s+szavazattal,?\s*"
        r"(?:(\d+)\s+nem\s+szavazat(?:tal|\s+mellett)|nem\s+szavazat(?:\s+és\s+tartózkodás)?\s+nélkül)?,?\s*"
        r"(?:(\d+)\s+tartózkodás(?:sal|\s+mellett)|tartózkodás\s+nélkül)?,?\s*(?:\([^)]{0,160}\))?,?\s*(?:elfogadta,?\s*majd\s*)?(?=(.{0,120}))")


def votes(text):
    t = re.sub(r"\s+", " ", text)
    out, warn = {}, []
    for m in re.finditer(VOTE, t):
        tail = m.group(6)
        if "határozat" not in tail[:60] or "napirend" in tail[:60]:
            continue
        h = re.search(NUMW, t[m.end():m.end() + 500])
        if not h:
            continue
        nn = int(h.group(1))
        if nn > 200:  # gyakori szövegfelismerési hiba: 38/2026 -> 386/2026
            nn //= 10
        num = f"{nn}/{h.group(2)}"
        v = {"igen": int(m.group(3)), "nem": int(m.group(4) or 0), "tartozkodas": int(m.group(5) or 0)}
        if sum(v.values()) != int(m.group(1)):
            warn.append(f"{num}: jelenlévő {m.group(1)}, de {v}")
        out[num] = v
    return out, warn


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", default="nyitott/adatok/hatarozat-reszletek.json")
    a = ap.parse_args()
    files = []
    for p in a.inputs:
        files += [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.lower().endswith(".pdf")] if os.path.isdir(p) else [p]
    data = json.load(open(a.out, encoding="utf-8"))
    H = data["hatarozatok"]
    n = 0
    for f in files:
        v, warn = votes(ocr_pdf(f))
        for w in warn:
            print("ELLENŐRIZD", os.path.basename(f), w)
        for num, vv in v.items():
            if num in H and not H[num].get("szavazas"):
                H[num]["szavazas"] = vv
                if "jegyzőkönyv" not in H[num].get("forras", ""):
                    H[num]["forras"] = (H[num].get("forras", "") + " ; szavazás: ülés jegyzőkönyve").strip(" ;")
                n += 1
            elif num not in H:
                print("nincs ilyen tétel a részletek között:", num)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"{n} szavazás beírva → {a.out}")


if __name__ == "__main__":
    main()
