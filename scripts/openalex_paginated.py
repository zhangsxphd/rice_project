"""Independent anonymous OpenAlex discovery with raw pages and failure audit."""
import json,sys,time,urllib.parse,urllib.request,urllib.error
from datetime import datetime,timezone
from pathlib import Path
QUERIES={'A':'rice nursery','B':'rice drought priming','C':'rice lysimeter','D':'rice rewatering drought'}
root=Path(sys.argv[1] if len(sys.argv)>1 else 'openalex_paginated');root.mkdir(parents=True,exist_ok=False)
manifest=[]
for key,query in QUERIES.items():
 folder=root/key;folder.mkdir(); row={'query_id':'OA_'+key,'database':'OpenAlex','query':query,'version':3,'retrieved_at':datetime.now(timezone.utc).isoformat(),'total_hits':None,'collected':0,'pages':0,'truncated':True,'attempts':[],'page_files':[],'per_page':200,'sort':'default relevance','year_filter':None};manifest.append(row);page=1
 while True:
  url='https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':'title_and_abstract.search:'+query,'per-page':200,'page':page})
  response=None
  for attempt in range(1,3):
   entry={'page':page,'attempt':attempt,'at':datetime.now(timezone.utc).isoformat()};row['attempts'].append(entry)
   try:
    with urllib.request.urlopen(url,timeout=45) as f:raw=f.read();entry['http_status']=f.status
    response=json.loads(raw);file=folder/('page_%04d.json'%page);file.write_bytes(raw);row['page_files'].append(str(file));break
   except urllib.error.HTTPError as e:
    entry['http_status']=e.code;file=folder/('error_%04d_%d.bin'%(page,attempt));file.write_bytes(e.read());entry['error_file']=str(file)
    if e.code not in (429,500,502,503,504) or attempt==2:break
    retry=e.headers.get('Retry-After');delay=int(retry) if retry and retry.isdigit() else 2
    if delay>20:entry['retry_aborted_seconds']=delay;break
    time.sleep(delay)
   except Exception as e:entry['error']=type(e).__name__+': '+str(e)[:200];break
  if response is None:row['stop_reason']='request_failed';break
  total=response.get('meta',{}).get('count');hits=response.get('results')
  if not isinstance(total,int) or not isinstance(hits,list):row['stop_reason']='invalid_response';break
  if row['total_hits'] is None:row['total_hits']=total
  elif row['total_hits']!=total:row.setdefault('warnings',[]).append('reported count changed during pagination')
  row['pages']+=1;row['collected']+=len(hits)
  (root/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
  if page*200>=total:row['stop_reason']='total_exhausted';row['truncated']=bool(row.get('warnings'));break
  if not hits:row['stop_reason']='empty_page_before_total';break
  page+=1;time.sleep(.2)
 ids=[]
 for page_file in row['page_files']:
  ids.extend(item.get('id') for item in json.loads(Path(page_file).read_text()).get('results',[]))
 duplicate_count=len([value for value in ids if value])-len(set(value for value in ids if value))
 row['pagination_validation']={'unique_ids':len(set(value for value in ids if value)),'duplicate_id_occurrences':duplicate_count,'missing_ids':sum(not value for value in ids)}
 if duplicate_count or row['pagination_validation']['missing_ids']:
  row['truncated']=True;row.setdefault('warnings',[]).append('Duplicate or missing IDs; completeness uncertain.')
 row['collection_complete']=row.get('stop_reason')=='total_exhausted' and not row['truncated']
 (root/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(key,'hits',row['total_hits'],'collected',row['collected'],'pages',row['pages'],'truncated',row['truncated'],row.get('stop_reason'),flush=True)
