"""Read-only upstream documentation evidence. Never clone, install or execute candidate code."""
import argparse,base64,hashlib,json,os,urllib.request,urllib.error,urllib.parse
from pathlib import Path
from discovery.collect import normalize
TARGETS=["TokisanGames/Terrain3D","jrouwe/JoltPhysics","RodZill4/material-maker","recastnavigation/recastnavigation","Auburn/FastNoise2","zeux/meshoptimizer","guillaumeblanc/ozz-animation","effekseer/Effekseer","shinshin86/mesh-avatar-studio","shinyobjectz/raea"]
def get(path):
    headers={"Accept":"application/vnd.github+json","User-Agent":"BRICK-YARD"}
    if os.getenv("GITHUB_TOKEN"): headers["Authorization"]="Bearer "+os.environ["GITHUB_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request("https://api.github.com/repos/"+path,headers=headers),timeout=30) as response:
        return json.load(response)
def inspect(repo):
    repo=normalize(repo);meta=get(repo);canonical=normalize(meta["full_name"]);commit=get(canonical+"/commits/"+urllib.parse.quote(meta["default_branch"],safe=""))["sha"]
    out={"repo":canonical,"requested_repo":repo,"commit":commit,"level":0,"review_status":"evidence collected; human review pending","hardware":"unknown","dependencies":"unknown","interfaces":"unknown","license_reported":(meta.get("license") or {}).get("spdx_id"),"documents":[],"errors":[]}
    for kind in ("readme","license"):
        try:
            d=get(canonical+"/"+kind+"?ref="+commit)
            raw=base64.b64decode(d["content"])
            out["documents"].append({"kind":kind,"path":d["path"],"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"url":"https://github.com/"+canonical+"/blob/"+commit+"/"+urllib.parse.quote(d["path"],safe="/")})
        except (OSError,ValueError,KeyError) as e: out["errors"].append({"kind":kind,"error":str(e)})
    return out
def main():
    p=argparse.ArgumentParser();p.add_argument("--out",default="inventory/inspection-evidence.json");a=p.parse_args()
    records=[];errors=[]
    for repo in TARGETS:
        try: records.append(inspect(repo))
        except (OSError,ValueError,KeyError) as e: errors.append({"repo":repo,"error":str(e)})
    Path(a.out).write_text(json.dumps({"records":records,"errors":errors},indent=2)+"\n")
    print(json.dumps({"records":len(records),"errors":len(errors),"documents":sum(len(x["documents"]) for x in records)}))
if __name__=="__main__":main()
