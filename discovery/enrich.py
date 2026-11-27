"""Bounded metadata enrichment with resumable output and explicit failures."""
import argparse,json,time,urllib.error
from pathlib import Path
from discovery.collect import metadata
def main():
    p=argparse.ArgumentParser();p.add_argument("input");p.add_argument("--out",default="enriched.json");p.add_argument("--limit",type=int,default=100);a=p.parse_args()
    path=Path(a.out);state=json.loads(path.read_text()) if path.exists() else {"records":[],"errors":[]}
    done={x["repo"].lower() for x in state["records"]};attempts=0
    for row in json.loads(Path(a.input).read_text()):
        repo=row["repo"]
        if repo.lower() in done: continue
        if attempts>=max(0,min(a.limit,500)): break
        attempts+=1
        try:
            result=metadata(repo);state["records"].append(result);done.add(repo.lower())
        except (OSError,ValueError,KeyError) as e:
            state["errors"].append({"repo":repo,"error":str(e)})
            if isinstance(e,urllib.error.HTTPError) and e.code in (403,429): break
        finally:
            path.write_text(json.dumps(state,indent=2)+"\n")
        time.sleep(.25)
    path.write_text(json.dumps(state,indent=2)+"\n")
if __name__=="__main__":main()
