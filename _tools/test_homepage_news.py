#!/usr/bin/env python3
"""Quick regression test: importing a day's package must keep earlier days in _data/homepage_news.json.
Run: python3 _tools/test_homepage_news.py  (uses temp copies; never writes repo files)"""
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;TOOL=ROOT/'_tools/homepage_news.py';DATA=ROOT/'_data/homepage_news.json'
def run(*args):return subprocess.run([sys.executable,str(TOOL),*args],capture_output=True,text=True)
def main():
 data=json.loads(DATA.read_text());day=max(e['date'] for e in data.values())
 post=ROOT/'_posts'/(day+'-digest.md');assert post.exists(),post
 # Rebuild an editorial package for the latest day from public data (adds required private fields).
 editorial=[dict(e,byline_evidence_url=e['url'],credit_status='test') for e in data.values() if e['date']==day]
 older={u:e for u,e in data.items() if e['date']!=day};assert older,'need earlier-day entries to test merge'
 with tempfile.TemporaryDirectory() as t:
  t=Path(t);ed=t/'editorial.json';ed.write_text(json.dumps(editorial,ensure_ascii=False))
  out=t/'out.json';shutil.copy(DATA,out)
  r=run('--editorial',str(ed),'--post',str(post),'--output',str(out));assert r.returncode==0,r.stdout+r.stderr
  merged=json.loads(out.read_text());assert merged==data,'merge changed or dropped entries'
  # Earlier days survive even when the output only held older entries (simulates the next day's import).
  out.write_text(json.dumps(older,ensure_ascii=False))
  r=run('--editorial',str(ed),'--post',str(post),'--output',str(out));assert r.returncode==0,r.stdout
  assert json.loads(out.read_text())==data,'older days lost on import'
  # --replace keeps the old overwrite-only behaviour.
  r=run('--editorial',str(ed),'--post',str(post),'--output',str(out),'--replace');assert r.returncode==0,r.stdout
  assert {e['date'] for e in json.loads(out.read_text()).values()}=={day}
  # Contract checks still apply to the public data.
  r=run('--data',str(DATA),'--post',str(post));assert r.returncode==0,r.stdout
 print('homepage_news merge test: PASS')
if __name__=='__main__':main()
