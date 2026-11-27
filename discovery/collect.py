"""Metadata only; never clone or execute candidate code."""
import argparse, csv, json, os, re, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPO=re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
def normalize(value):
    value=value.strip().removeprefix("https://github.com/").rstrip("/").removesuffix(".git")
    if not REPO.fullmatch(value) or any(p in (".","..") for p in value.split("/")):
        raise ValueError("Expected owner/repo")
    return value
def import_csv(path):
    with open(path,encoding="utf-8-sig",newline="") as f:
        rows=csv.DictReader(f)
        field=next((k for k in ("repo","full_name","repository","url","html_url","github_url") if k in (rows.fieldnames or [])),None)
        if not field: raise ValueError("No supported repository column")
        result=set()
        for row in rows:
            try: result.add(normalize(row[field]))
            except (ValueError,AttributeError): continue
        return sorted(result,key=str.lower)
def metadata(repo):
    headers={"Accept":"application/vnd.github+json","User-Agent":"BRICK-YARD"}
    if os.getenv("GITHUB_TOKEN"): headers["Authorization"]="Bearer "+os.environ["GITHUB_TOKEN"]
    request=urllib.request.Request("https://api.github.com/repos/"+normalize(repo),headers=headers)
    with urllib.request.urlopen(request,timeout=20) as response: d=json.load(response)
    return {"repo":d["full_name"],"description":d.get("description"),"license":(d.get("license") or {}).get("spdx_id"),"language":d.get("language"),"archived":d.get("archived"),"pushed_at":d.get("pushed_at"),"stars":d.get("stargazers_count"),"level":0,"source":"GitHub API"}
def main():
    p=argparse.ArgumentParser();p.add_argument("--csv");p.add_argument("--limit",type=int,default=15);p.add_argument("--out",default="candidates.json");a=p.parse_args()
    repos=import_csv(a.csv) if a.csv else [x["repo"] for x in json.loads((ROOT/"docs/catalog.json").read_text())]
    seen=set(); records=[]; errors=[]
    for repo in repos:
        if repo.lower() in seen: continue
        if len(seen)>=max(0,min(a.limit,100)): break
        seen.add(repo.lower())
        try: records.append(metadata(repo))
        except (OSError,ValueError,KeyError) as e: errors.append({"repo":repo,"error":str(e)})
    Path(a.out).write_text(json.dumps({"records":records,"errors":errors},indent=2)+"\n")
    if errors: print(f"{len(errors)} metadata requests failed; inspect output")
if __name__=="__main__": main()
