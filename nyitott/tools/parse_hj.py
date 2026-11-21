"""Önkormányzatok Elektronikus Hatásköri Jegyzéke PDF-ek feldolgozása kereshető JSON-ná.
Használat: python3 parse_hj.py <pdf-mappa> <kimenet.json>"""
import re, sys, json, os, glob
import pdfplumber
COLS=['m','f','fk','mjv','v','k']
def is_heading(w): return 'Arial' in w['fontname'] and 'Narrow' not in w['fontname']
def parse_pdf(path):
    fn=os.path.basename(path); org=fn.split('_')[1]
    items=[]; cur=None; ag=None; cim=None; centers=None
    with pdfplumber.open(path) as pdf:
        for pno,pg in enumerate(pdf.pages,1):
            ws=pg.extract_words(extra_attrs=['fontname','size'])
            ws=[w for w in ws if 'Narrow' not in w['fontname'] and not ('Bold' in w['fontname'] and w['text'] in('FELADAT/HATÁSKÖR','SZERV','JOGSZABÁLY'))]
            # header columns
            hdr=[w for w in ws if w['text'] in COLS and 'Times' in w['fontname'] and w['x0']>250]
            if len(hdr)>=6:
                tops={}
                for w in hdr: tops.setdefault(round(w['top']),[]).append(w)
                row=max(tops.values(),key=len)
                if len(row)>=6:
                    centers={w['text']:(w['x0']+w['x1'])/2 for w in row}
                    htop=round(row[0]['top']); ws=[w for w in ws if abs(round(w['top'])-htop)>2 or w['text'] not in COLS]
            # group lines
            lines={}
            for w in ws:
                key=None
                for t in lines:
                    if abs(t-w['top'])<3: key=t;break
                lines.setdefault(key if key is not None else w['top'],[]).append(w)
            for top in sorted(lines):
                lw=sorted(lines[top],key=lambda w:w['x0'])
                if is_heading(lw[0]):
                    txt=' '.join(w['text'] for w in lw)
                    if lw[0]['size']>=13.5: ag=txt
                    elif re.match(r'^\d+\.',txt): cim=txt
                    elif cim and not cur: cim+=' '+txt
                    else: cim=(cim+' '+txt) if cim and cur is None else txt
                    cur=None; continue
                if not centers: continue
                mpos=centers['m']-8; kpos=centers['k']+8
                first=lw[0]
                if re.fullmatch(r'\d+\.',first['text']) and first['x0']<105:
                    cur={'o':org,'ag':ag,'c':cim,'n':int(first['text'][:-1]),'t':[],'j':[],'sz':set(),'f':fn,'p':pno,'small':0,'all':0,'it':0}
                    items.append(cur); lw=lw[1:]
                if cur is None: continue
                for w in lw:
                    cx=(w['x0']+w['x1'])/2
                    cur['all']+=1
                    if w['size']<11.5: cur['small']+=1
                    if 'Italic' in w['fontname']: cur['it']+=1
                    if w['text']=='*' and mpos-6<cx<kpos:
                        cur['sz'].add(min(centers,key=lambda c:abs(centers[c]-cx)))
                    elif w['x0']<mpos: cur['t'].append(w['text'])
                    elif w['x0']>=kpos-4: cur['j'].append(w['text'])
                    else: cur['t' if w['x0']<centers['m'] else 'j'].append(w['text'])
    return items
def join(ws):
    s=' '.join(ws)
    s=re.sub(r'(\w)- (?=[a-záéíóöőúüű])',r'\1',s)
    s=re.sub(r'\s+([,.;:)])',r'\1',s); s=re.sub(r'\(\s+','(',s)
    return s.strip()
if __name__=='__main__':
    out=[]
    files=sorted(glob.glob(os.path.join(sys.argv[1],'*_[TBPJU]_*.pdf')),key=lambda x:int(os.path.basename(x).split('_')[0]))
    for p in files:
        for it in parse_pdf(p):
            rep=it['all'] and it['small']/it['all']>0.6
            if rep: continue
            out.append({'o':it['o'],'ag':it['ag'],'c':it['c'],'n':it['n'],'t':join(it['t']),'j':join(it['j']),'sz':[c for c in COLS if c in it['sz']],'u':bool(it['all'] and it['it']/it['all']>0.3),'f':it['f'],'p':it['p']})
    json.dump(out,open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    print(len(out))
