"""Bounded link checks, separate from editorial review. Never changes review dates.
Run: python3 tools/check_resources.py [--output path]
A blocked probe is an instruction for browser review, not proof of a broken link.
"""
import argparse,concurrent.futures,json,subprocess
from datetime import date,datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def check(r):
    result=subprocess.run(['curl','--silent','--show-error','--location','--max-time','25','--max-redirs','5','--proto','=https','--proto-redir','=https','--output','/dev/null','--write-out','%{http_code}\n%{url_effective}',r['url']],capture_output=True,text=True)
    lines=result.stdout.splitlines();status=int(lines[0]) if lines and lines[0].isdigit() else 0
    disposition='reachable' if 200<=status<300 else 'broken' if status in (404,410) else 'needs browser review'
    return {'id':r['id'],'url':r['url'],'http_status':status,'result':disposition,'final_url':lines[1] if len(lines)>1 else '', 'editorial_review_due':(date.today()-date.fromisoformat(r['reviewed'])).days>=180}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'.cache/research-links.json');args=parser.parse_args()
    data=json.loads((ROOT/'content/research/resources.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(check,data))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({'checked_at':datetime.now(timezone.utc).isoformat(),'results':results},indent=2)+'\n')
    print(json.dumps({'checked':len(results),'attention':[r for r in results if r['result']!='reachable' or r['editorial_review_due']]},indent=2))
    return 1 if any(r['result']=='broken' for r in results) else 0
if __name__=='__main__':raise SystemExit(main())
