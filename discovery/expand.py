"""Bounded public GitHub search; metadata only, never execute candidate code."""
import argparse,json,os,time,urllib.request,urllib.parse,urllib.error
from pathlib import Path
from discovery.collect import normalize
TOPICS=("computer-vision","robotics","godot","procedural-generation","audio-processing","digital-forensics","embedded","geospatial","scientific-computing","3d-printing","webgl","data-visualization","speech-synthesis","network-monitoring","simulation","software-defined-radio")
def search(topic,page=1):
    q=urllib.parse.urlencode({"q":f"topic:{topic} archived:false fork:false stars:>10","sort":"stars","order":"desc","per_page":100,"page":page})
    headers={"Accept":"application/vnd.github+json","User-Agent":"BRICK-YARD"}
    if os.getenv("GITHUB_TOKEN"): headers["Authorization"]="Bearer "+os.environ["GITHUB_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request("https://api.github.com/search/repositories?"+q,headers=headers),timeout=40) as response: return json.load(response)
def merge(raw,records,items,topic):
    for x in items:
        repo=normalize(x["full_name"]);key=repo.lower()
        if key not in raw: raw[key]={"repo":repo,"level":0,"sources":[]}
        raw[key]["sources"]=sorted(set(raw[key].get("sources",[])+["github-topic:"+topic]))
        if key not in records:
            records[key]={"repo":repo,"description":x.get("description"),"license":(x.get("license") or {}).get("spdx_id"),"language":x.get("language"),"archived":x.get("archived"),"pushed_at":x.get("pushed_at"),"stars":x.get("stargazers_count"),"level":0,"source":"GitHub search API"}
def main():
    p=argparse.ArgumentParser();p.add_argument("--dir",default="inventory");p.add_argument("--target",type=int,default=1000);p.add_argument("--pages",type=int,default=2);a=p.parse_args()
    d=Path(a.dir);rp=d/"raw-discoveries.json";ep=d/"enriched.json"
    original=json.loads(rp.read_text());state=json.loads(ep.read_text())
    raw={x["repo"].lower():x for x in original};records={x["repo"].lower():x for x in state["records"]}
    initial=len(raw);report={"initial":initial,"target":a.target,"queries":[],"errors":[]}
    stop=False
    for page in range(1,max(1,min(a.pages,3))+1):
        for topic in TOPICS:
            if len(raw)>=a.target: stop=True;break
            try:
                result=search(topic,page);items=result.get("items",[])
                before=len(raw);merge(raw,records,items,topic)
                report["queries"].append({"topic":topic,"page":page,"returned":len(items),"added":len(raw)-before,"incomplete":result.get("incomplete_results")})
            except (OSError,ValueError,KeyError) as e:
                report["errors"].append({"topic":topic,"error":str(e)})
                if isinstance(e,urllib.error.HTTPError) and e.code in (403,429): stop=True;break
            time.sleep(3)
        if stop: break
    rp.write_text(json.dumps(sorted(raw.values(),key=lambda x:x["repo"].lower()),indent=2)+"\n")
    state["records"]=sorted(records.values(),key=lambda x:x["repo"].lower())
    ep.write_text(json.dumps(state,indent=2)+"\n")
    report.update(final=len(raw),added=len(raw)-initial,metadata=len(records),target_reached=len(raw)>=a.target)
    (d/"expansion-report.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
