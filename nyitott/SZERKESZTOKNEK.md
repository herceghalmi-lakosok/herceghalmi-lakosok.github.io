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

A szavazási arányokat a jegyzőkönyvekből a `python3 nyitott/tools/szavazasok_jkv.py <jegyzőkönyv-PDF-ek>` program tölti ki (csak az üres `szavazas` mezőket). Az „ELLENŐRIZD” sorokat nézd meg a PDF-ben. Zárt ülésen hozott döntésnél a szavazás nem nyilvános: ilyenkor a `szavazas_megjegyzes` mezőbe írd ezt.

Ha egy határozat magánszemély nevét tartalmazza (pl. ösztöndíjasok, felajánló magánszemély), a `szoveg` mezőt hagyd üresen, és a `szoveg_megjegyzes` mezőbe írd: „A határozat magánszemélyek nevét tartalmazza, ezért a szövegét itt nem közöljük. Az eredeti kivonat a hivatalos honlapon olvasható.” Vállalkozók, szerződő cégek és tisztségviselők neve maradhat.

Ha a hivatalos honlapon hibás a határozat száma, a tételt a dokumentumkereső szerinti számon hagyd, és a `megjegyzes` mezőben írd le az eltérést (példa: 38/2026.).

Csak olyat írj be, ami hivatalos dokumentumból igazolható. Ha bizonytalan, hagyd üresen: az oldal ilyenkor „nincs még adat” állapotot mutat.

## Ülésfigyelő (`ulesek/`)

Az oldal a napirendet (előterjesztések), a meghívót, a jegyzőkönyvet és a videólinkeket az `adatok/dokumentumok.json`-ból veszi. A szerkesztett tartalom az `adatok/ulesfigyelo.json`-ban van, az ülés dátumával kulcsolva:

- `elozetes`: 1–2 mondatos, közérthető összefoglaló arról, miről szól az ülés. Az ülés előtt, a meghívó megjelenésekor írd meg.
- `dontesek`: legfeljebb öt pont arról, mit döntöttek, mindegyik végén zárójelben a határozat száma, pl. `(162/2026.)`. A számokból az oldal automatikusan linket készít a Döntéskövetőre. Csak azt írd le, ami a határozat szövegében áll; nem egyhangú döntésnél add meg a szavazás arányát.
- `videok`: a Budakörnyéki TV-oldal címe a kulcs. Értéke: `{"youtube": "videóazonosító", "pontok": [{"t": "0:12:30", "cim": "1. napirendi pont: …"}]}`. A YouTube-azonosító a BTV-oldalon beágyazott videó címében van (`youtu.be/<azonosító>`). Az időbélyegeket a videó visszanézésével lehet rögzíteni.
- `kovetkezo` (a fájl tetején): a következő ülés adatai, amint a meghívó megjelent: `{"d": "2026-12-01", "ido": "18:00", "elozetes": "…", "meghivo": "PDF-link"}`. Az ülés után állítsd vissza `null`-ra, és az összefoglalót írd az ülés dátumához.

## Szerződéstár (`szerzodesek/`)

Az adatok az `adatok/szerzodesek.json`-ban vannak. Új szerződésnél:

1. Töltsd le a PDF-et, és olvasd ki: partner, típus, tárgy, érték (bruttó/nettó/havi – az `ertek_tipus` mezőbe), aláírás dátuma, időtartam, a hivatkozott határozat száma.
2. Vegyél fel egy új tételt a `szerzodesek` tömbbe (a meglévők mintájára; az `id` a PDF-link `fid` száma).
3. Ha a szerződés a `hianyzo` listán szereplő döntéshez tartozik, onnan töröld a tételt.
4. Szerződésmódosításnál a `modositasok` tömbbe írj egy sort: `{"datum": "…", "leiras": "…", "url": "…"}`.

Az oldal változástörténetét a GitHub mutatja (a „változástörténete” gomb a fájl commitjaira mutat), ezért minden módosításhoz írj érthető commit-üzenetet. Magánszemély vevő vagy eladó nevét ne írd be; a vállalkozók és cégek neve maradhat.

## Fejlesztéskövető (`fejlesztesek/`)

Az adatok az `adatok/fejlesztesek.json`-ban vannak. Az `allapot` lehetséges értékei a fájl tetején, az `allapotok` alatt. Állapotváltozáskor (szerződés megkötve, munka megkezdődött, elkészült) frissítsd az `allapot` és az `utolso_adat` mezőt, és a forrást írd a `leiras` mezőbe.

**Térképes jelölés:** nyisd meg az oldalt így: `fejlesztesek/?szerkeszt=1`. Kattints a térképen a fejlesztés helyére, és a megjelenő `"lat": …, "lng": …` értéket másold a tétel `lat` és `lng` mezőjébe. Ha egy tételnek nincs egyetlen helyszíne (pl. eszközbeszerzés), hagyd `null`-on: ilyenkor csak a listában jelenik meg.

## Herceghalom régen (`regen/index.html`)

Helytörténeti oldal, statikus HTML, nem kell hozzá adatfájl. A fejezetek: kezdetek, uradalom, legendák, 1916, Kísérleti Gazdaság és ÁKI, a Germinal forgatása (1962), önállóság, Talentis, régi fotók, források.

- **Szöveg:** csak saját szavainkkal összefoglalt tényt írj, és a bekezdés végén a `[n]` számmal hivatkozz a Források listára. Újságcikkből vagy könyvből ne másolj be szöveget.
- **Legenda:** új `<div class="legend">` blokk. Mindig jelezd, hogy hagyományról van szó, és add meg a forrást.
- **Kép:** csak közkincs (public domain) vagy szabad licencű (Fortepan: CC BY-SA 3.0) képet tegyél fel, és a képaláírásba írd be a szerzőt vagy adományozót és a licencet. Fortepan-jelölés: „FORTEPAN / adományozó neve”. Lakossági fotót csak a beküldő írásos hozzájárulásával közölj, az általa kért névvel.
- **Videó:** csak olyat ágyazz be, amelyhez a közzétevő maga ad beágyazókódot (YouTube, Filmhíradók Online). Minta a `<div class="video">` blokk: a gomb `data-embed` attribútumába a lejátszó címe kerül, így a videó csak kattintásra töltődik be.
- **Nem közölhető:** Arcanum-oldalak (pl. Tolnai Világlapja), MTVA-fotók, újságcikkek képei és szövege. Ezekre csak hivatkozz.
