#!/usr/bin/env python3
import csv, io, json, urllib.request
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"market.json"
URL_P="https://www.mimit.gov.it/images/exportCSV/prezzo_alle_8.csv"
URL_S="https://www.mimit.gov.it/images/exportCSV/anagrafica_impianti_attivi.csv"
TUSCANY={"AREZZO","FIRENZE","GROSSETO","LIVORNO","LUCCA","MASSA-CARRARA","MASSA CARRARA","PISA","PRATO","PISTOIA","SIENA"}
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"ToscanaMobility/1.0"})
    return urllib.request.urlopen(req,timeout=90).read().decode("utf-8-sig",errors="replace")
def reader(raw):
    lines=[x for x in raw.splitlines() if x.strip()]
    start=0
    for i,line in enumerate(lines[:5]):
        if "idimpianto" in line.lower():
            start=i;break
    return csv.DictReader(io.StringIO("\n".join(lines[start:])),delimiter="|")
stations=set()
for r in reader(get(URL_S)):
    prov=(r.get("Provincia") or "").strip().upper()
    if prov in TUSCANY: stations.add((r.get("idimpianto") or r.get("idImpianto") or "").strip())
buckets={"diesel_self_eur_l":[],"petrol_self_eur_l":[],"lpg_served_eur_l":[],"methane_served_eur_kg":[]}
for r in reader(get(URL_P)):
    sid=(r.get("idimpianto") or r.get("idImpianto") or "").strip()
    if sid not in stations: continue
    fuel=(r.get("descCarburante") or "").strip().lower()
    selfv=(r.get("isSelf") or "").strip()
    try: price=float((r.get("prezzo") or "0").replace(",","."))
    except: continue
    if not .2<price<5: continue
    if fuel=="gasolio" and selfv=="1": buckets["diesel_self_eur_l"].append(price)
    elif fuel=="benzina" and selfv=="1": buckets["petrol_self_eur_l"].append(price)
    elif fuel=="gpl" and selfv=="0": buckets["lpg_served_eur_l"].append(price)
    elif fuel=="metano" and selfv=="0": buckets["methane_served_eur_kg"].append(price)
old=json.loads(OUT.read_text()) if OUT.exists() else {}
fuel={}
for k,v in buckets.items(): fuel[k]=round(sum(v)/len(v),3) if v else old.get("fuel",{}).get(k)
data={"updated":datetime.now(timezone.utc).date().isoformat(),"region":"Toscana","fuel":fuel,"electricity":old.get("electricity",{}),"source":{"name":"MIMIT Open Data","license":"IODL 2.0","prices":URL_P,"stations":URL_S}}
OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(data,ensure_ascii=False,indent=2))
