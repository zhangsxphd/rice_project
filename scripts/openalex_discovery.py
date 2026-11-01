import json, time, urllib.parse, urllib.request, urllib.error, sys
from datetime import datetime,timezone
from pathlib import Path
queries={'A':'rice nursery','B':'rice drought priming','C':'rice lysimeter','D':'rice rewatering drought'}
out=Path(sys.argv[1] if len(sys.argv)>1 else 'openalex')
out.mkdir(parents=True,exist_ok=False)
manifest=[]
for key, query in queries.items():
 row={'query_id':key,'database':'OpenAlex','query':query,'version':2,'retrieved_at':datetime.now(timezone.utc).isoformat(),'total_hits':None,'collected':0,'pages':0,'truncated':True,'attempts':[],'limit':'one page of 50; shared anonymous free budget; title and abstract search'}
 url='https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':'title_and_abstract.search:'+query,'per-page':50,'page':1})
 try:
  with urllib.request.urlopen(url,timeout=35) as res: raw=res.read(); row['attempts'].append({'status':res.status}); data=json.loads(raw)
  (out/(key+'.json')).write_bytes(raw)
  row.update(total_hits=data['meta']['count'],collected=len(data['results']),pages=1,truncated=data['meta']['count']>len(data['results']))
 except urllib.error.HTTPError as e:
  body=e.read(); (out/(key+'_error.json')).write_bytes(body); row['attempts'].append({'status':e.code,'error_file':str(out/(key+'_error.json'))})
 except Exception as e: row['attempts'].append({'error':str(e)})
 manifest.append(row); (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)); print(key,row['total_hits'],row['collected'],row['attempts'],flush=True)
 time.sleep(0.2)
