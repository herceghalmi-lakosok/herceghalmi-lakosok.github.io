"""Az Önkormányzatok Elektronikus Hatásköri Jegyzékének frissítése a Nyitott Herceghalom oldalhoz.

Használat:
  python3 build_hataskori.py --zip <letöltött.zip> --out <nyitott/hataskori> --kiadas 2026-III
A zip PDF-jeit a <out>/pdf mappába teszi (a régieket törli), és elkészíti a <out>/hataskori.json-t.
"""
import argparse, json, os, re, shutil, subprocess, sys, zipfile, unicodedata, datetime
sys.path.insert(0, os.path.dirname(__file__))
from parse_hj import parse_pdf, join, COLS
ORG={'A':'Általános','T':'Képviselő-testület','B':'Bizottság','P':'Polgármester','J':'Jegyző','U':'Ügyintéző','V':'Jogszabályok'}
def safe(name):
    name=name.replace('#U00e9','e')
    name=unicodedata.normalize('NFD',name); name=''.join(c for c in name if unicodedata.category(c)!='Mn')
    return re.sub(r'[^A-Za-z0-9_.-]','_',name)
def clean(s):
    s=s.replace(' - és','- és').replace('feladat - ','feladat- ')
    s=re.sub(r'^(\d+) \.',r'\1.',s)
    return s
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--zip',required=True); ap.add_argument('--out',required=True); ap.add_argument('--kiadas',required=True); ap.add_argument('--forras',default='')
    a=ap.parse_args()
    pdfdir=os.path.join(a.out,'pdf')
    if os.path.isdir(pdfdir): shutil.rmtree(pdfdir)
    os.makedirs(pdfdir)
    with zipfile.ZipFile(a.zip) as z:
        for info in z.infolist():
            if info.is_dir() or not info.filename.lower().endswith('.pdf'): continue
            with z.open(info) as src, open(os.path.join(pdfdir,safe(os.path.basename(info.filename))),'wb') as dst: shutil.copyfileobj(src,dst)
    pdfs=sorted(os.listdir(pdfdir),key=lambda x:int(x.split('_')[0]) if x.split('_')[0].isdigit() else 999)
    # issue info from table of contents
    meta={'kiadas':a.kiadas,'forras':a.forras,'frissitve':datetime.date.today().isoformat(),'szam':'','lezarva':''}
    toc=[p for p in pdfs if '_tartalomjegyzek' in p]
    if toc:
        t=subprocess.run(['pdftotext','-l','1',os.path.join(pdfdir,toc[0]),'-'],capture_output=True,text=True).stdout
        m=re.search(r'([IVXLC]+\. évfolyam \d+\. szám)',t); meta['szam']=m.group(1) if m else ''
        m=re.search(r'lezárva:\s*([^)]+)\)',t); meta['lezarva']=m.group(1).strip() if m else ''
    files=[];sections=[];secidx={};items=[]
    for p in pdfs:
        o=p.split('_')[1] if '_' in p else 'A'
        size=os.path.getsize(os.path.join(pdfdir,p))
        title=None
        if o in 'TBPJU':
            for it in parse_pdf(os.path.join(pdfdir,p)):
                if it['all'] and it['small']/it['all']>0.6: continue
                ag=clean(it['ag'] or ''); c=clean(it['c'] or '')
                title=title or ag
                key=(ag,c)
                if key not in secidx: secidx[key]=len(sections); sections.append([ag,c])
                mask=sum(1<<i for i,col in enumerate(COLS) if col in it['sz'])
                items.append([o,secidx[key],it['n'],clean(join(it['t'])),join(it['j']),mask,1 if it['all'] and it['it']/it['all']>0.3 else 0,len(files),it['p']])
        if not title:
            title={'1':'Szerkesztési alapelvek','2':'Tartalomjegyzék'}.get(p.split('_')[0]) or ('Jogszabályok jegyzéke' if 'jogszabaly' in p else p)
        files.append({'f':p,'o':o,'org':ORG.get(o,o),'cim':title,'kb':round(size/1024)})
    json.dump({'meta':meta,'oszlopok':COLS,'fajlok':files,'cimek':sections,'tetelek':items},open(os.path.join(a.out,'hataskori.json'),'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    print(f"{len(files)} fájl, {len(items)} tétel, {len(sections)} cím")
if __name__=='__main__': main()
