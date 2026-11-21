"""Megnézi, megjelent-e újabb Önkormányzati Elektronikus Hatásköri Jegyzék a kormany.hu-n,
és ha igen, letölti és újraépíti a nyitott/hataskori mappát. A GitHub Actions futtatja hetente."""
import json, os, re, subprocess, sys, tempfile, urllib.request
HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(HERE,'..','hataskori')
PAGE='https://kormany.hu/onkormanyzatok-elektronikus-hataskori-jegyzeke'
PAT='https://cdn.kormany.hu/uploads/onkormanyzatok_elektronikus_hataskori_jegyzeke_{y}_{q}_ne.zip'
QS=['I','II','III','IV']
UA={'User-Agent':'Mozilla/5.0 (Nyitott Herceghalom frissito; +https://herceghalmi-lakosok.github.io/nyitott/)'}
def key(y,q): return int(y)*10+QS.index(q)+1
def fetch(url):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=120) as r: return r.read()
def candidates(cur):
    found={}
    try:
        html=fetch(PAGE).decode('utf-8','ignore')
        for m in re.finditer(r'(https?://cdn\.kormany\.hu/uploads/onkormanyzatok_elektronikus_hataskori_jegyzeke_(\d{4})_([IV]+)_ne\.zip)',html):
            found[(m.group(2),m.group(3))]=m.group(1).replace('http://','https://')
    except Exception as e: print('Az oldal nem olvasható:',e)
    y,q=cur.split('-'); y=int(y); i=QS.index(q)
    for _ in range(4):
        i+=1
        if i==4: i=0; y+=1
        found.setdefault((str(y),QS[i]),PAT.format(y=y,q=QS[i]))
    return sorted(((k,u) for k,u in found.items() if key(*k)>key(*cur.split('-'))),key=lambda x:-key(*x[0]))
def main():
    meta=json.load(open(os.path.join(OUT,'hataskori.json'),encoding='utf-8'))['meta']
    cur=meta['kiadas']; print('Jelenlegi kiadás:',cur)
    for (y,q),url in candidates(cur):
        try: data=fetch(url)
        except Exception as e: print('Nincs még:',y,q,e); continue
        if data[:2]!=b'PK': print('Nem zip:',url); continue
        with tempfile.NamedTemporaryFile(suffix='.zip',delete=False) as f: f.write(data); zp=f.name
        subprocess.run([sys.executable,os.path.join(HERE,'build_hataskori.py'),'--zip',zp,'--out',OUT,'--kiadas',f'{y}-{q}','--forras',url],check=True)
        print('Frissítve:',y,q); return
    print('Nincs újabb kiadás.')
if __name__=='__main__': main()
