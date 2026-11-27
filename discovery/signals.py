"""Import repository identifiers only, never editorial text or executable code."""
import argparse,csv,io,json,re,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
from discovery.collect import normalize,metadata
URLS={"csv":"https://githubsignals.io/export.csv","rss":"https://githubsignals.io/feed.xml"}
LINK=re.compile(r"https://github\.com/([\w.-]+/[\w.-]+)",re.I|re.ASCII)
PAIR=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
def extract(value):
    value=(value or "").strip()
    match=LINK.search(value)
    if match: value=match.group(1)
    elif not PAIR.fullmatch(value): return None
    try:
        value=normalize(value)
        if value.split("/")[0].lower() in {"topics","orgs","users","settings","features","marketplace","collections","sponsors","search"}: return None
        return value
    except ValueError: return None
def csv_repos(raw):
    reader=csv.DictReader(io.StringIO(raw.lstrip("\ufeff")))
    found=set()
    for row in reader:
        fields={str(k).lower().strip().replace("-","_"):v for k,v in row.items() if k}
        owner=fields.get("owner") or fields.get("repo_owner") or fields.get("github_owner")
        name=fields.get("repo_name") or fields.get("name") or fields.get("repo") or fields.get("repository")
        candidates=[owner+"/"+name] if owner and name and "/" not in name else []
        candidates += [v for k,v in fields.items() if k in {"repo","repository","full_name","repo_full_name","github_repo","github_url","repo_url","repository_url","html_url","url","link","slug"}]
        for candidate in candidates:
            repo=extract(candidate)
            if repo: found.add(repo)
    return found,reader.fieldnames
def rss_repos(raw):
    root=ET.fromstring(raw)
    found=set()
    for item in root.iter():
        if item.tag.split("}")[-1] not in {"item","entry"}: continue
        for node in item.iter():
            for match in LINK.finditer((node.text or "")+" "+node.attrib.get("href","")):
                repo=extract(match.group(0))
                if repo: found.add(repo)
            if node.tag.split("}")[-1]=="title":
                repo=extract(node.text)
                if repo: found.add(repo)
    return found
def fetch(kind):
    req=urllib.request.Request(URLS[kind],headers={"User-Agent":"BRICK-YARD/0.1 (repository identifier discovery)"})
    with urllib.request.urlopen(req,timeout=60) as response:
        raw=response.read(32*1024*1024+1)
        if len(raw)>32*1024*1024: raise ValueError("Feed exceeds size limit")
        return raw.decode("utf-8-sig")
def merge(existing, additions):
    result={x["repo"].lower():x for x in existing}
    for kind,repos in additions.items():
        for repo in sorted(repos,key=str.lower):
            row=result.setdefault(repo.lower(),{"repo":repo,"level":0,"sources":[]})
            row["sources"]=sorted(set(row["sources"]+[kind]))
    return sorted(result.values(),key=lambda x:x["repo"].lower())
def main():
    p=argparse.ArgumentParser();p.add_argument("--out",default="raw-discoveries.json");p.add_argument("--csv-file");p.add_argument("--rss-file");p.add_argument("--existing");p.add_argument("--enrich",type=int,default=0);a=p.parse_args()
    existing=json.loads(Path(a.existing).read_text()) if a.existing else []
    report={"sources":{},"errors":[]}; additions={}
    for kind,local in (("csv",a.csv_file),("rss",a.rss_file)):
        try:
            raw=Path(local).read_text(encoding="utf-8-sig") if local else fetch(kind)
            if kind=="csv": repos,columns=csv_repos(raw);report["csv_columns"]=columns
            else: repos=rss_repos(raw)
            if not repos: raise ValueError("No repository identifiers parsed; inspect source format")
            additions[kind]=repos;report["sources"][kind]=len(repos)
        except (OSError,ValueError,ET.ParseError,csv.Error) as e: report["errors"].append({"source":kind,"error":str(e)})
    rows=merge(existing,additions);Path(a.out).write_text(json.dumps(rows,indent=2)+"\n")
    report["unique"]=len(rows)
    Path("signals-report.json").write_text(json.dumps(report,indent=2)+"\n")
    if not additions: raise SystemExit("No supplier source imported; see report")
if __name__=="__main__":main()
