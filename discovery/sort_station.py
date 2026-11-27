"""Build a review-only warehouse index from GitHub metadata and source identifiers."""
import json,re,argparse
from pathlib import Path
from discovery.collect import normalize
from discovery.rank import classify
EXTRA={"robotics":["robotics","ros2","robot arm"],"embedded":["esp32","raspberry pi","microcontroller"],"geospatial":["geospatial","gis","satellite"],"science":["scientific","simulation","research"],"vision":["computer vision","object detection","opencv"],"fabrication":["3d printing","cad","cnc"],"radio":["software defined radio","sdr"],"audio-dsp":["audio","dsp","synthesizer"],"networking":["network","protocol","packet"],"design":["design system","design token","graphics"]}
PERMISSIVE={"MIT","Apache-2.0","BSD-2-Clause","BSD-3-Clause","ISC","0BSD","CC0-1.0","Zlib"}
def build(raw,enriched,seed):
    rows={}
    for x in raw:
        repo=normalize(x["repo"]);rows[repo.lower()]={"repo":repo,"sources":x.get("sources",[]),"stage":"discovered","level":0,"tags":[],"license":None}
    for x in enriched:
        repo=normalize(x["repo"]);k=repo.lower();base=rows.get(k,{"repo":repo,"sources":["GitHub API"]})
        item=classify(x);blob=(repo+" "+str(x.get("description") or "")).lower()
        tags=sorted(set(item["tags"]+[k for k,words in EXTRA.items() if any(w in blob for w in words)]))
        lic=x.get("license")
        rows[k]=dict(base,**{k:x.get(k) for k in ("description","language","archived","pushed_at","stars","license")},repo=repo,tags=tags,stage="metadata",level=0,relevance=item["relevance"],license_group="permissive candidate" if lic in PERMISSIVE else "review required",review_required=True)
    for x in seed:
        k=normalize(x["repo"]).lower();base=rows.get(k,{});rows[k]=dict(base,**{key:value for key,value in x.items() if key not in ("tags","sources")},tags=sorted(set(base.get("tags",[])+[x["category"]])),stage="seed",review_required=True)
    return sorted(rows.values(),key=lambda x:x["repo"].lower())
def main():
    p=argparse.ArgumentParser();p.add_argument("--dir",default="inventory");p.add_argument("--out",default="docs/warehouse.json");a=p.parse_args()
    d=Path(a.dir);raw=json.loads((d/"raw-discoveries.json").read_text());enriched=json.loads((d/"enriched.json").read_text())["records"];seed=json.loads(Path("docs/catalog.json").read_text())
    rows=build(raw,enriched,seed)
    shortlist=sorted([x for x in rows if x["stage"]=="metadata" and not x.get("archived")],key=lambda x:(-x.get("relevance",0),x["repo"].lower()))[:50]
    Path(a.out).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n")
    (d/"shortlist.json").write_text(json.dumps(shortlist,ensure_ascii=False,indent=2)+"\n")
    report={"raw":len(raw),"metadata_records":len(enriched),"unique_metadata":len({x["repo"].lower() for x in enriched}),"warehouse_unique":len(rows),"shortlist":len(shortlist)}
    (d/"sorting-report.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
