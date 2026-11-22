# Nyitott Herceghalom – szerkesztői útmutató

## Bejelentések felvétele a problématérképre

A lakosok bejelentései e-mailben érkeznek (a cím az `index.html`-ben, a `REPORT_EMAIL` változóban van beállítva). A térkép az `adatok/bejelentesek.json` fájlból dolgozik: ami ebben szerepel, az nyilvánosan megjelenik.

### Mielőtt felveszel egy bejelentést

1. Valós-e a probléma, és Herceghalomban van-e?
2. Távolítsd el a leírásból a személyes adatokat: nevet, telefonszámot, rendszámot, házszámot, ha az egy magánszemélyhez köthető.
3. Ne kerüljön fel sértő, vádaskodó vagy egy konkrét személyt minősítő szöveg. A probléma leírása tárgyszerű legyen.
4. A bejelentő nevét és elérhetőségét soha ne írd a fájlba.
5. Fénykép csak akkor kerüljön fel, ha nem látszik rajta arc vagy rendszám.

### Egy bejelentés mezői

```json
{
  "id": "2026-004",
  "cim": "Kátyú a Liget utca elején",
  "kategoria": "ut",
  "leiras": "Tárgyszerű leírás, személyes adatok nélkül.",
  "helyszin": "Liget utca 1. előtt",
  "lat": 47.4981,
  "lng": 18.7480,
  "allapot": "beerkezett",
  "bejelentve": "2026-11-22",
  "frissitve": "2026-11-22",
  "illetekes": "Herceghalom Község Önkormányzata",
  "megjegyzes": "Továbbítva a polghiv@herceghalom.hu címre.",
  "link": "",
  "forras": "lakossági bejelentés"
}
```

- `kategoria`: `ut`, `jarda`, `kozlekedesbiztonsag`, `vilagitas`, `viz`, `hulladek`, `zold`, `eszkoz`, `epulet`, `egyeb`
- `allapot`: `beerkezett`, `tovabbitva`, `folyamatban`, `megoldva`
- `lat`, `lng`: a bejelentő e-mailjében szereplő koordináta, vagy az OpenStreetMap-ről kimásolt érték.
- Állapotváltozáskor frissítsd az `allapot`, a `frissitve` és a `megjegyzes` mezőt.

## Dokumentumkereső frissítése

A dokumentumlista az `adatok/dokumentumok.json` fájlban van. A frissítést a herceghalom.hu rovataiból végezzük; a fájlt egészében cseréljük.

## Hatásköri jegyzék (`hataskori/`)

Az Önkormányzatok Elektronikus Hatásköri Jegyzékét a `.github/workflows/hataskori-jegyzek.yml` GitHub Actions-munkafolyamat minden hétfőn ellenőrzi a kormany.hu-n. Ha új negyedéves kiadás jelent meg, letölti, a PDF-eket a `hataskori/pdf` mappába teszi, újraépíti a kereshető `hataskori/hataskori.json`-t, és az eredményt a `main` ágra menti.

- Kézi indítás: GitHub → Actions → „Hatásköri jegyzék frissítése” → Run workflow.
- Kézi frissítés letöltött zip-ből: `python3 nyitott/tools/build_hataskori.py --zip <fájl.zip> --out nyitott/hataskori --kiadas 2026-IV --forras <zip-URL>`
- Ha a munkafolyamat hibával áll le, a kormany.hu valószínűleg megváltoztatta a letöltési címet, vagy elutasítja a GitHub szervereit. Ilyenkor a kézi frissítés működik.


## Közérthető költségvetés (`koltsegvetes/`)

- A lefordított oldal a `koltsegvetes/`, a forrása a `koltsegvetes-forras/` mappában van; a frissítés lépéseit a forrás README-je írja le.
- Az adatok ezer forintban (eFt) szerepelnek. Működési bevétel = B1+B3+B4+B6, működési kiadás = K1+K2+K3+K4+K512; a tartalék (K513) nincs benne.
- Új zárszámadás vagy költségvetési rendelet után egy új sor kerül az Excelbe, és az `alapEv` értéke a tervév.

## Aktuális rovat és Herceghalmi Hírmondó

- Az `index.html` `#aktualis` szakaszában vannak a futó felhívások (most: közösségi költségvetés, határidő 2026. november 30.). Ha lejár egy határidő, a kártyát vedd ki vagy írd át, és a hero „Közelgő időpontok” listájából is töröld.
- Új Hírmondó-szám megjelenésekor: a `#hirmondo` kártyán írd át a hónapot, a tartalmat és a PDF linkjét (`fid`); a dokumentumkeresőbe a `adatok/dokumentumok.json` fájlban vegyél fel egy új `"t":"Hírmondó"` tételt (`m` mezőben a hónap neve, pl. „2026. december”). Archívum: https://www.herceghalom.hu/?module=news&action=list&fname=hirmondo

## Lakossági kérdőív (`kerdoiv/`)

- A válaszok e-mailben érkeznek a gesztenyestisza@proton.me címre, tárgyuk: `[Kérdőív] Herceghalmi lakossági kérdőív – HK-2026-1`.
- A levelekben soronként `K01=…` formátumú adatok vannak. A számok az opciók sorszámai a `kerdoiv/index.html` fájl `Q` tömbjében; több választás esetén vesszővel elválasztva, a K07 rácskérdésnél `a:4 b:2 …` formában (`?` = nincs tapasztalata, `-` = nem válaszolt).
- Ha a gyűjtés közben módosítjátok a kérdéseket, írjátok át a `VERSION` értékét, hogy a régi és az új válaszok elkülöníthetők legyenek.
- Az összesítéshez a feladók e-mail-címét nem kell megőrizni; aki értesítést kért (K12, K13), azt külön listában tartsátok, és a gyűjtés lezárása után a többit töröljétek.
- Az eredményeket a kérdőív oldalának „Eredmények” szakaszában tegyétek közzé, a válaszok számával és a gyűjtés időszakával. Jelezzétek, hogy a felmérés nem reprezentatív.

## Döntéskövető (`dontesek/`)

Az oldal két fájlból dolgozik:
- `adatok/dokumentumok.json`: a határozatok listája (szám, cím, dátum, téma, PDF-link) és az ülések (meghívó, jegyzőkönyv, videó). Ezt a dokumentumkereső frissítésével együtt frissítjük, külön teendő nincs.
- `adatok/hatarozat-reszletek.json`: a határozatok részletei, a határozat számával kulcsolva (pl. `"169/2026"`).

### A részletek kitöltése

A herceghalom.hu-n a kivonatok szkennelt PDF-ek, ezért szövegfelismeréssel dolgozzuk fel őket:

1. Töltsd le a feldolgozandó kivonatokat egy mappába (a linkek a dokumentumkeresőben vagy a Döntéskövetőben vannak).
2. Futtasd: `python3 nyitott/tools/ocr_hatarozatok.py <mappa> --hatarido-azonnal`
   (kell hozzá: poppler-utils, tesseract-ocr, tesseract-ocr-hun).
3. **Ellenőrizd a PDF-fel** a felismert szöveget, a felelőst és a határidőt, majd a `forras` mezőt írd át erre: `határozati kivonat (szövegfelismeréssel, ellenőrizve)`.

A program nem írja felül a kézzel kitöltött mezőket. Ezeket kézzel töltsd:
- `hatarido_datum`: a határidő dátuma (ÉÉÉÉ-HH-NN). Ha a határidő „a következő ülés”, a következő ülés napját írd be. Ebből számolja az oldal, hogy lejárt-e a határidő; 30 nap türelmi idő után jelöli „nincs adat a végrehajtásról” állapottal.
- `szavazas`: a jegyzőkönyvből, például `{"igen": 5, "nem": 1, "tartozkodas": 1}`. Ha név szerinti szavazás volt: `"nev_szerint": {"Név": "igen", …}`.
- `vegrehajtas`: `teljesult`, `folyamatban`, `nem-teljesult` vagy `visszavonva`. Forrás lehet a polgármester beszámolója a lejárt határidejű határozatokról, egy újabb határozat, szerződés vagy hivatalos közlemény.
- `vegrehajtas_megjegyzes`: egy mondat a végrehajtásról, a forrással együtt (pl. „A szerződést 2026. november 20-án megkötötték (lásd: …).”).

Csak olyat írj be, ami hivatalos dokumentumból igazolható. Ha bizonytalan, hagyd üresen: az oldal ilyenkor „nincs még adat” állapotot mutat.
