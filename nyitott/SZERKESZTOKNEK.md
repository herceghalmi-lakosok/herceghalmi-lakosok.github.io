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
