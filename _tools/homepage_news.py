#!/usr/bin/env python3
"""Validate/import reviewed homepage-only expanded summaries; never edits digest posts.
Editorial input: list of entries, {"stories": [...]}, or URL-keyed entries.
Public output: exact source URL -> {url,date,summary_fr,summary_en,authors,contributors,author_type,outlet}.
Evidence/status/notes are validated where supplied, but never copied into public data.
Word counts and why-overlap are advisory; factual/source/byline audit remains editorial work.
Import with --output MERGES: earlier days already in the output file are kept, the current day is replaced
by the imported package, and the merged file is re-validated. --replace restores overwrite-only behaviour.
"""
from pathlib import Path
import argparse,datetime,json,re,sys
from urllib.parse import urlsplit
OPTIONAL={'why_fr','why_en'}
PUBLIC=OPTIONAL|{'url','date','summary_fr','summary_en','authors','contributors','author_type','outlet'}
TYPES={'person','agency','corporate','unavailable'}
CREDIT_TYPES={'individual_authors':'person','news_agency':'agency','corporate_publisher':'corporate','unavailable':'unavailable'}
def words(text):return re.findall(r"[^\W_]+(?:[’'\-][^\W_]+)*",text,re.UNICODE)
def post(path):
 raw=Path(path).read_text();fm=raw.split('---',2)[1];date=re.search(r'^date:\s*[\"\']?(\d{4}-\d{2}-\d{2})',fm,re.M).group(1)
 # gen.py writes each story as one JSON object in YAML; no YAML dependency needed.
 stories=[json.loads(x) for x in re.findall(r'^\s*-\s*(\{.*\})\s*$',fm,re.M)]
 if not stories:raise ValueError('Expected gen.py one-line JSON stories in post frontmatter')
 return date,stories

def entries(raw):
 if isinstance(raw,dict) and isinstance(raw.get('stories'),list):raw=raw['stories']
 if isinstance(raw,list):
  out={}
  for e in raw:
   if not isinstance(e,dict) or not isinstance(e.get('url'),str):raise ValueError('Every entry needs a URL string')
   if e['url'] in out:raise ValueError('Duplicate source URL '+e['url'])
   out[e['url']]=e
  return out
 if not isinstance(raw,dict):raise ValueError('Expected entry list or URL-keyed object')
 return raw

def http(value):
 if not isinstance(value,str):return False
 try:
  u=urlsplit(value);return u.scheme in ['http','https'] and bool(u.netloc) and not u.username and not u.password and not any(c.isspace() for c in value)
 except ValueError:return False

def validate(raw,day,stories,public_input=False):
 data=entries(raw);errors=[];warnings=[];counts={};current={s['url']:s for s in stories};output={}
 for url,e in data.items():
  if not isinstance(e,dict):errors.append(url+': entry must be object');continue
  e=dict(e)
  if not public_input:
   e.setdefault('contributors',[])
   if 'author_type' not in e and e.get('credit_type') in CREDIT_TYPES:e['author_type']=CREDIT_TYPES[e['credit_type']]
  if not http(url) or e.get('url')!=url:errors.append(url+': exact URL/key mismatch or invalid URL')
  try:
   if not isinstance(e.get('date'),str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',e['date']):raise ValueError('date format')
   datetime.date.fromisoformat(e['date'])
  except (ValueError,TypeError):errors.append(url+': date must be YYYY-MM-DD')
  for field in ['summary_fr','summary_en','outlet']:
   if not isinstance(e.get(field),str) or not e[field].strip():errors.append(url+': nonempty string required: '+field)
  for field in ['authors','contributors']:
   if not isinstance(e.get(field),list) or not all(isinstance(x,str) and x.strip() and x==x.strip() for x in e[field]):errors.append(url+': '+field+' must be an array of nonempty trimmed strings')
   elif len(set(e[field]))!=len(e[field]):errors.append(url+': duplicate '+field+' names')
  if e.get('author_type') not in TYPES:errors.append(url+': author_type must distinguish person/agency/corporate/unavailable')
  authors=e.get('authors',[]);contributors=e.get('contributors',[])
  if any(k in e for k in OPTIONAL):
   for k in OPTIONAL:
    if not isinstance(e.get(k),str) or not e[k].strip():errors.append(url+': optional why overrides require both nonempty language strings')
  if isinstance(authors,list) and isinstance(contributors,list):
   if set(x for x in authors if isinstance(x,str))&set(x for x in contributors if isinstance(x,str)):errors.append(url+': contributor is also listed as author')
   if e.get('author_type')=='unavailable' and authors:errors.append(url+': unavailable author credit must have empty authors')
   if e.get('author_type') in ['person','agency','corporate'] and not authors:errors.append(url+': credited author_type requires verified attribution')
  if public_input and set(e)-PUBLIC:errors.append(url+': private or unknown keys in public runtime data: '+', '.join(sorted(set(e)-PUBLIC)))
  if not public_input:
   if not http(e.get('byline_evidence_url')):errors.append(url+': source verification URL required in private input')
   if not isinstance(e.get('credit_status'),str) or not e['credit_status'].strip():errors.append(url+': private credit_status required')
  if e.get('date')==day:
   if url not in current:errors.append(url+': current-day entry not in current post')
   for lang in ['fr','en']:
    text=e.get('summary_'+lang,'')
    if not isinstance(text,str):continue
    n=len(words(text));counts[url+'#'+lang]=n
    if not 65<=n<=85:warnings.append(url+' '+lang+': '+str(n)+' words; advisory target65–85, do not pad')
    why=e.get('why_'+lang,current.get(url,{}).get('why_'+lang,''));numbers=lambda t:set(re.findall(r'\d+(?:[.,]\d+)?',t));overlap=numbers(text)&numbers(why)
    if overlap:warnings.append(url+' '+lang+': expanded summary repeats why-line figure(s): '+', '.join(sorted(overlap)))
    tokens=lambda t:{w.lower()[:5] for w in words(t) if len(w)>3};wt=tokens(why)
    if wt and len(wt&tokens(text))/len(wt)>=.5:warnings.append(url+' '+lang+': possible why-line factual overlap; requires editorial review')
  output[url]={k:e[k] for k in sorted(PUBLIC) if k in e}
 missing=set(current)-{url for url,e in data.items() if isinstance(e,dict) and e.get('date')==day}
 if missing:errors.append('Missing current-day expansions: '+', '.join(sorted(missing)))
 return output,errors,warnings,counts

def merge(existing,imported,day):
 """Keep earlier days' public entries; the imported package replaces the current day."""
 merged={url:e for url,e in existing.items() if not (isinstance(e,dict) and e.get('date')==day) and url not in imported}
 merged.update(imported)
 return merged

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--data');ap.add_argument('--editorial');ap.add_argument('--post',required=True);ap.add_argument('--output');ap.add_argument('--report')
 ap.add_argument('--replace',action='store_true',help='Overwrite --output with only the imported entries (default: merge, keeping earlier days)');a=ap.parse_args()
 if bool(a.data)==bool(a.editorial):ap.error('Provide exactly one of --data or --editorial')
 day,stories=post(a.post);data,errors,warnings,counts=validate(json.loads(Path(a.editorial or a.data).read_text()),day,stories,public_input=bool(a.data))
 merged_count=None
 if not errors and a.output and not a.replace and Path(a.output).exists():
  # Default import merges into existing public data, then re-checks the whole output contract.
  data=merge(json.loads(Path(a.output).read_text()),data,day)
  _,merge_errors,_,_=validate(data,day,stories,public_input=True);errors+=['merged output: '+x for x in merge_errors];merged_count=len(data)
 result={'result':'ERROR' if errors else 'PASS','date':day,'current_story_count':len(stories),'current_language_summary_count':len(counts),'errors':errors,'warnings':warnings,'word_counts':counts,'editorial_approval_required':'Validation does not establish factual accuracy or approve publication'}
 if merged_count is not None:result['merged_output_entry_count']=merged_count
 if a.report:Path(a.report).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False,indent=2))
 if errors:return 1
 if a.output:
  dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 return 0
if __name__=='__main__':sys.exit(main())
