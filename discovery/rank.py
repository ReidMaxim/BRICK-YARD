"""Rank independently fetched metadata; scores are heuristic, not verification."""
import argparse,json
from pathlib import Path
GROUPS={"animation":["animation","avatar","rigging","motion","lip sync"],"games":["game","godot","physics","terrain","voxel","navigation"],"media":["video","audio","render","speech","tts","blender"],"security":["security","forensic","network","sandbox"],"agents":["agent","automation","llm","inference"],"web":["web","javascript","typescript","dashboard"]}
def classify(row):
    text=(str(row.get("repo",""))+" "+str(row.get("description",""))+" "+str(row.get("language",""))).lower()
    tags=[k for k,words in GROUPS.items() if any(w in text for w in words)]
    license_id=row.get("license")
    score=10*len(tags)+(5 if license_id and license_id not in ("NOASSERTION","OTHER") else 0)-(30 if row.get("archived") else 0)
    return dict(row,tags=tags,relevance=score,review_required=True,level=0)
def main():
    p=argparse.ArgumentParser();p.add_argument("input");p.add_argument("--out",default="shortlist.json");p.add_argument("--limit",type=int,default=50);a=p.parse_args()
    data=json.loads(Path(a.input).read_text());rows=data.get("records",[]) if isinstance(data,dict) else data
    ranked=sorted(map(classify,rows),key=lambda x:(-x["relevance"],x["repo"].lower()))
    Path(a.out).write_text(json.dumps(ranked[:a.limit],indent=2)+"\n")
if __name__=="__main__":main()
