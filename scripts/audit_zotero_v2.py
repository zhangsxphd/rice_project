"""Read-only Zotero/RIS reconciliation and non-destructive cleanup preview."""
import argparse,csv,json,re,urllib.request,collections,hashlib
from pathlib import Path

def norm(doi):return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi\s*:\s*)','',(doi or '').strip().lower()).strip()
def get(path):
 with urllib.request.urlopen('http://127.0.0.1:23119/api/users/0/'+path,timeout=25) as f:return json.load(f),f.headers.get('Total-Results')
def pages(path):
 items=[];expected=None;start=0
 while True:
  sep='&' if '?' in path else '?';chunk,total=get(path+sep+'limit=100&start='+str(start));items+=chunk
  if expected is None and total is not None:expected=int(total)
  if len(chunk)<100:break
  start+=len(chunk)
 return items,{'received':len(items),'reported_total':expected,'complete':expected is None or expected==len(items)}
def parse_ris(path):
 records=[];cur=None
 for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
  if len(line)<6 or line[2:6]!='  - ':continue
  tag,value=line[:2],line[6:].strip()
  if tag=='TY':cur={'type':value}
  elif cur is not None and tag=='ER':records.append(cur);cur=None
  elif cur is not None and tag in ('DO','TI','PY','DA'):cur.setdefault(tag,value)
 if cur is not None:raise ValueError('Unterminated RIS record')
 return records

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--broad-key',required=True);p.add_argument('--focus-key',required=True);p.add_argument('--ris',required=True);p.add_argument('--actions',required=True);p.add_argument('--screening',required=True);p.add_argument('--output-dir',required=True);args=p.parse_args()
 out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
 for n in ('zotero_cleanup_preview.csv','ris_reconciliation.csv','zotero_audit_summary.json'):
  if (out/n).exists():raise FileExistsError('refuse to overwrite '+str(out/n))
 broad,broad_meta=pages('collections/'+args.broad_key+'/items/top');focus,focus_meta=pages('collections/'+args.focus_key+'/items/top');attachments,attach_meta=pages('items?itemType=attachment');notes,note_meta=pages('items?itemType=note');annotations,ann_meta=pages('items?itemType=annotation');collections_list,col_meta=pages('collections')
 if not all(x['complete'] for x in [broad_meta,focus_meta,attach_meta,note_meta,ann_meta,col_meta]):raise RuntimeError('Local API paging incomplete, no cleanup preview emitted')
 focuses={x['key'] for x in focus}; bkeys={x['key'] for x in broad};cname={x['key']:x['data'].get('name','') for x in collections_list}
 child=collections.defaultdict(list);pdfparents={}
 for x in attachments:
  d=x['data'];parent=d.get('parentItem')
  if parent in bkeys:
   child[parent].append(d)
   pdfparents[x['key']]=parent
 notecount=collections.Counter(x['data'].get('parentItem') for x in notes)
 anncount=collections.Counter(pdfparents.get(x['data'].get('parentItem')) for x in annotations if pdfparents.get(x['data'].get('parentItem')))
 actions=list(csv.DictReader(Path(args.actions).open(encoding='utf-8',newline='')));bykey=collections.defaultdict(list)
 for action in actions:
  if action.get('item_key') and ';' not in action['item_key']:bykey[action['item_key']].append(action)
 screen=list(csv.DictReader(Path(args.screening).open(encoding='utf-8',newline='')));bydoi=collections.defaultdict(list)
 for x in screen:
  if norm(x['doi']):bydoi[norm(x['doi'])].append(x)
 ris=parse_ris(args.ris);rd=collections.defaultdict(list)
 for i,x in enumerate(ris,1):rd[norm(x.get('DO'))].append(i)
 ris_unique={k for k in rd if k}; broad_dois=collections.defaultdict(list)
 for x in broad:
  doi=norm(x['data'].get('DOI'))
  if doi:broad_dois[doi].append(x['key'])
 preview=[]
 for x in broad:
  d=x['data'];key=x['key'];doi=norm(d.get('DOI'));events=bykey.get(key,[]); kinds=[a.get('action','') for a in events]; origin=next((k for k in ('created_test','created_local','associated_existing') if k in kinds),'unknown');matches=bydoi.get(doi,[]);other=[c for c in d.get('collections',[]) if c not in (args.broad_key,args.focus_key)];pdf=[z for z in child[key] if z.get('contentType')=='application/pdf'];user_tags=[t.get('tag','') for t in d.get('tags',[]) if t.get('type',0)==0];risk=[]
  if 'identity_review' in kinds:risk.append('identity_conflict_review')
  if key in focuses:risk.append('in_focus_collection')
  if other:risk.append('other_collection_membership')
  if pdf:risk.append('pdf_attachment_present')
  if notecount[key]:risk.append('child_notes')
  if anncount[key]:risk.append('pdf_annotations')
  if user_tags:risk.append('nonautomatic_tag_type_origin_unverified')
  if d.get('relations'):risk.append('relations_present')
  if d.get('extra'):risk.append('extra_field_present')
  if d.get('dateModified')!=d.get('dateAdded'):risk.append('modified_after_creation_origin_unknown')
  if len(matches)!=1:risk.append('candidate_identity_ambiguous')
  category=matches[0]['primary'] if len(matches)==1 else '未匹配或多重匹配'
  proposal='待人工复核，不执行变更'
  if category=='不相关' and not risk:proposal='可讨论仅从宽泛分类移除；仍需用户明确批准'
  preview.append({'item_key':key,'doi':doi,'title':d.get('title',''),'origin_from_session_log':origin,'session_actions':';'.join(dict.fromkeys(kinds)),'in_1122_ris_snapshot':'yes' if doi in ris_unique else 'no_or_no_doi','in_focus':'yes' if key in focuses else 'no','screening_v2_primary':category,'other_collection_keys':';'.join(other),'other_collection_names':';'.join(cname.get(k,k) for k in other),'pdf_attachment_count':len(pdf),'other_attachment_count':len(child[key])-len(pdf),'child_note_count':notecount[key],'pdf_annotation_count':anncount[key],'nonautomatic_tag_count':len(user_tags),'date_added':d.get('dateAdded',''),'date_modified':d.get('dateModified',''),'protection_flags':';'.join(risk),'proposed_action':proposal,'approval_required':'yes'})
 with (out/'zotero_cleanup_preview.csv').open('x',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(preview[0]));w.writeheader();w.writerows(preview)
 rr=[]
 for i,r in enumerate(ris,1):
  doi=norm(r.get('DO'));keys=broad_dois.get(doi,[]) if doi else []
  rr.append({'ris_record':i,'doi':doi,'title':r.get('TI',''),'matching_broad_keys':';'.join(keys),'match_state':'unique_doi' if len(keys)==1 else ('multiple_doi' if keys else 'not_found_or_missing_doi')})
 with (out/'ris_reconciliation.csv').open('x',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
 unmatched=[x for x in broad if norm(x['data'].get('DOI')) not in ris_unique]
 summary={'ris_file_sha256':hashlib.sha256(Path(args.ris).read_bytes()).hexdigest(),'ris_records':len(ris),'ris_records_with_doi':sum(bool(norm(r.get('DO'))) for r in ris),'ris_distinct_dois':len(ris_unique),'ris_duplicate_doi_groups':sum(1 for k,v in rd.items() if k and len(v)>1),'ris_match_states':dict(collections.Counter(x['match_state'] for x in rr)),'broad_count':len(broad),'focus_count':len(focus),'focus_subset_of_broad':focuses.issubset(bkeys),'broad_not_in_snapshot_count':len(unmatched),'broad_not_in_snapshot_keys':[x['key'] for x in unmatched],'proposed_actions':dict(collections.Counter(x['proposed_action'] for x in preview)),'origin':dict(collections.Counter(x['origin_from_session_log'] for x in preview)),'flags':{v:sum(v in x['protection_flags'].split(';') for x in preview) for v in ['identity_conflict_review','in_focus_collection','other_collection_membership','pdf_attachment_present','child_notes','pdf_annotations','nonautomatic_tag_type_origin_unverified','modified_after_creation_origin_unknown']},'pagination':{'broad':broad_meta,'focus':focus_meta,'attachments':attach_meta,'notes':note_meta,'annotations':ann_meta,'collections':col_meta}}
 (out/'zotero_audit_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in summary.items() if k!='broad_not_in_snapshot_keys'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
