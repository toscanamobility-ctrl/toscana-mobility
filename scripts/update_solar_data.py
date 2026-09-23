#!/usr/bin/env python3
import json, urllib.request, urllib.parse
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"data"/"solar.json"
C={"Pisa":(43.7167,10.4000),"Firenze":(43.7696,11.2558),"Lucca":(43.8429,10.5027),"Livorno":(43.5485,10.3106),"Prato":(43.8777,11.1022),"Pistoia":(43.9333,10.9167),"Arezzo":(43.4633,11.8796),"Siena":(43.3188,11.3308),"Grosseto":(42.7635,11.1124),"Massa-Carrara":(44.0354,10.1393)}
vals={}
for city,(lat,lon) in C.items():
    q=urllib.parse.urlencode({"lat":lat,"lon":lon,"peakpower":1,"loss":14,"optimalangles":1,"outputformat":"json"})
    req=urllib.request.Request("https://re.jrc.ec.europa.eu/api/v5_3/PVcalc?"+q,headers={"User-Agent":"ToscanaMobility/1.0"})
    try:
        d=json.loads(urllib.request.urlopen(req,timeout=60).read())
        vals[city]=round(float(d["outputs"]["totals"]["fixed"]["E_y"]))
    except Exception as e: print(city,e)
if vals: OUT.write_text(json.dumps({"updated":date.today().isoformat(),"source":"European Commission JRC PVGIS 5.3","yield_kwh_per_kwp":vals},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
