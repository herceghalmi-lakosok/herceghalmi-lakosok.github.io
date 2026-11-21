import React, { useState, useEffect } from 'react';
import { fetchAndParseData } from './utils/excelParser';
import StatCards from './components/StatCards';
import BudgetChart from './components/BudgetChart';
import CategoryBreakdown from './components/CategoryBreakdown';
import KeyIndicators from './components/KeyIndicators';
import PlannedInvestments from './components/PlannedInvestments';
import MayorMessage from './components/MayorMessage';
import BudgetExplanation from './components/BudgetExplanation';
import { Activity } from 'lucide-react';
import config from './config/config.json';

// Szekció kapcsolók (ha nincs a configban, alapból true = megjelenik)
const show = (key) => config.szekciok?.[key] !== false;

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedYear, setSelectedYear] = useState(config.alapEv);

  useEffect(() => {
    const loadData = async () => {
      const parsedData = await fetchAndParseData();
      setData(parsedData);
      setLoading(false);

      if (parsedData.length > 0) {
        // Default to the planned year (alapEv from config) for immediate impact, fallback to latest
        const defaultYear = parsedData.find(d => d.year === config.alapEv) ? config.alapEv : parsedData[parsedData.length - 1].year;
        setSelectedYear(defaultYear);
      }
    };
    loadData();

    // Inject dynamic colors from config.json
    const root = document.documentElement;
    root.style.setProperty('--brand-primary', config.szinek.elsodleges);
    root.style.setProperty('--accent-income', config.szinek.masodlagos);
  }, []);

  if (loading) {
    return (
      <div className="app-container justify-center items-center" style={{ minHeight: '100vh' }}>
        <div className="loading-spinner"></div>
        <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>Adatok betöltése és feldolgozása…</p>
      </div>
    );
  }

  const selectedData = data.find(d => d.year === selectedYear);

  // Dinamikus évtartomány az adatokból
  const firstYear = data.length > 0 ? data[0].year : '?';
  const lastYear = data.length > 0 ? data[data.length - 1].year : '?';

  return (
    <div className="app-container">
      <div style={{ background: '#1c2420', color: '#f6f5f1', borderRadius: '0.75rem', padding: '0.75rem 1rem', marginBottom: '1.5rem', fontSize: '0.92rem', lineHeight: 1.5 }}>
        <strong>Nem hivatalos oldal.</strong> Ez nem Herceghalom Község Önkormányzatának kiadványa. Üzemelteti és szerkeszti: Herceghalmi Gesztenyés Tisza Sziget. A hivatalos költségvetési dokumentumok a <a href="https://www.herceghalom.hu/?module=news&action=list&fname=ktsgvetes" style={{ color: '#f6f5f1' }}>herceghalom.hu</a> oldalon érhetők el. · <a href="../" style={{ color: '#f6f5f1' }}>Vissza a Nyitott Herceghalomra</a>
      </div>
      <header className="header" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '1rem', padding: '0.5rem 1rem', background: 'var(--surface)', borderRadius: '2rem', border: '1px solid var(--brand-primary-glow)' }}>
          <Activity size={18} color="var(--brand-primary)" />
          <span style={{ fontSize: '0.9rem', color: 'var(--brand-primary)', fontWeight: 600 }}>Nem hivatalos lakossági összefoglaló</span>
        </div>
        <h1 style={{ fontSize: '2.5rem', lineHeight: 1.2 }}>{config.varosNeve} <br /><span className="gradient-text">költségvetése közérthetően</span></h1>
        <p style={{ marginTop: '0.5rem' }}>Herceghalom Község Önkormányzatának működési bevételei és kiadásai {firstYear}–{lastYear} között: a zárszámadások tényadatai és a {config.alapEv}. évi terv, a nyilvános önkormányzati rendeletek alapján.</p>
      </header>

      {/* Select Year Buttons */}
      <div className="flex justify-center" style={{ gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
        {data.map(item => (
          <button
            key={item.year}
            onClick={() => setSelectedYear(item.year)}
            style={{
              padding: '0.5rem 1.2rem',
              borderRadius: '2rem',
              border: item.year === selectedYear ? '1px solid var(--brand-primary)' : '1px solid var(--glass-border)',
              background: item.year === selectedYear ? 'var(--brand-primary)' : 'var(--surface)',
              color: item.year === selectedYear ? '#ffffff' : 'var(--text-main)',
              cursor: 'pointer',
              fontWeight: 600,
              transition: 'all 0.2s ease',
              outline: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '0.3rem'
            }}
          >
            {item.year} {item.isPlan && <span style={{ fontSize: '0.7rem', opacity: 0.8 }}>(terv)</span>}
          </button>
        ))}
      </div>

      {show('polgarmesteriUzenet') && <MayorMessage data={selectedData} />}

      <StatCards data={selectedData} />

      {show('beruhazasok') && <PlannedInvestments data={selectedData} />}

      {show('kulcsindikatorok') && <KeyIndicators data={selectedData} historicalData={data} />}

      <BudgetChart data={data} selectedYear={selectedYear} onYearClick={setSelectedYear} />

      <div className="grid-charts">
        {show('bevetelMegoszlas') && <CategoryBreakdown data={selectedData} type="income" />}
        {show('kiadasMegoszlas') && <CategoryBreakdown data={selectedData} type="expense" />}
      </div>

      {show('koltsegvetesiKisokos') && <BudgetExplanation />}

      <footer style={{ marginTop: '2rem', padding: '2rem', background: 'var(--surface)', borderRadius: 'var(--border-radius-lg)', border: '1px solid var(--glass-border)', display: 'flex', flexDirection: 'column', gap: '0.8rem', color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6 }}>
        <h4 style={{ color: 'var(--text-main)', fontSize: '1.1rem' }}>Az adatokról</h4>
        <p>A {firstYear}–{config.alapEv - 1}. évi adatok tényadatok az éves zárszámadási rendeletekből (9/2024., 14/2025., 8/2026.), a {config.alapEv}. évi adatok a 3/2026. (III.4.) költségvetési rendelet II. módosítás szerinti előirányzatai. Az összegek ezer forintban szerepelnek, kerekítve.</p>
        <p><strong>Működési bevétel</strong> = állami működési támogatások (B1) + közhatalmi bevételek (B3) + működési bevételek (B4) + átvett pénzeszközök (B6). <strong>Működési kiadás</strong> = személyi juttatások (K1) + járulékok (K2) + dologi kiadások (K3) + ellátottak juttatásai (K4) + egyéb működési kiadások (K512). A felhalmozási tételek (beruházások, felújítások), a finanszírozási tételek és a {config.alapEv}. évi tervben szereplő, közel 695 millió forintos tartalék nem része a működési összesítésnek. Az építményadót és a telekadót a rendeletek együtt, vagyoni típusú adóként közlik, ezért itt is együtt szerepelnek. A szolidaritási hozzájárulás az egyéb működési kiadások része, külön nem bontható ki.</p>
        <p>Üzemelteti és szerkeszti: Herceghalmi Gesztenyés Tisza Sziget · <a href="mailto:gesztenyestisza@proton.me" style={{ color: 'var(--brand-primary)' }}>gesztenyestisza@proton.me</a> · <a href="../" style={{ color: 'var(--brand-primary)' }}>Nyitott Herceghalom</a></p>
        <p style={{ fontSize: '0.82rem', opacity: 0.85 }}>Az oldal Törökbálint Önkormányzatának nyílt forráskódú sablonjára épül: <a href="https://github.com/lakatostotholiver/Atlathato-Koltsegvetes-Onkormanyzatoknak" style={{ color: 'var(--brand-primary)' }}>Átlátható Költségvetés Önkormányzatoknak</a> (MIT-licenc).</p>
      </footer>
    </div>
  );
}

export default App;
