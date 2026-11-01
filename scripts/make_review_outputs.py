"""Derive review tables from frozen screening and OpenAlex raw pages; no network."""
import csv,json,collections,hashlib
from pathlib import Path

ROOT=Path('.')
OUT=ROOT/'review_v2_20261101'

def write(name,rows):
 if not rows:raise ValueError('empty '+name)
 p=OUT/name
 with p.open('x',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

s=list(csv.DictReader((OUT/'screening_v2.csv').open(encoding='utf-8')))
raw=[json.loads(line) for line in (ROOT/'deduplicated.jsonl').open(encoding='utf-8') if line.strip()]
assert len(s)==len(raw)==5576
priority=sorted((r for r in s if r['primary'] in ('P1','P2','P3','P4')),key=lambda r:('P1 P2 P3 P4'.split().index(r['primary']),r['abstract_status']=='missing',int(r['record_number'])))
write('priority_reading.csv',priority)
hist=[r for r in s if r['historical_include']=='historical_include'];assert len(hist)==23
write('historical_23_review.csv',hist)
# Document exact cases inspected in this audit. These are research-assistant observations,
# not a human expert confirmation; no thresholds are fitted to the cases.
observations={
 1132:'旧排除抽查：试验为稻田除草剂与杂草控制；早期 P4 草稿误将淹水与育秧词共现判为管理研究，现已收紧。',
 1394:'旧排除抽查：水稻昆虫圃通讯，摘要未显示缺水耗水或工程育秧水管理。',
 2661:'旧排除抽查：稻瘟病及稻曲病抗性评价；摘要未显示目标水分过程。',
 1115:'旧排除抽查：育秧害虫控制通讯，未显示目标水分过程。',
 3656:'旧排除抽查：作物害虫防治，摘要未显示目标水分过程。',
 1106:'旧排除抽查：水稻病害通讯，未显示目标水分过程。',
 1108:'旧排除抽查：肥料通讯，摘要概述不充分，需检查原文才能评价基质水分管理。',
 3762:'旧排除抽查：水稻遗传育种；不能仅因灌溉字样视作课题证据。',
 5080:'低优先级抽查：题名指出三次亏缺和耐受，但缺摘要，耗水或复水恢复观测尚不明。',
 4675:'低优先级抽查：题名有反复干旱和生理适应，缺摘要；具体指标与恢复尚不明。',
 4683:'低优先级抽查：橄榄周期干旱，缺摘要；生理指标、耗水或恢复需核查。',
 4695:'低优先级抽查：马铃薯周期干旱，缺摘要；耗水或恢复观测需核查。',
 4669:'低优先级抽查：葡萄跨生长季单次与两次干旱对照；是否报告动态耗水或复水恢复需核全文。',
 4793:'低优先级抽查：黑胡椒反复亏缺，缺摘要；过程指标需核查。',
 4705:'低优先级抽查：松树幼苗周期干旱，缺摘要；过程指标需核查。',
 5123:'低优先级抽查：题名明确反复土壤干旱及复水与生理适应，但缺摘要，实际观测指标需核查，可能漏入 P1。',
 1098:'低优先级抽查：水稻干旱后光合作用恢复；缺摘要，题名支持 P2 候选；早期规则要求复水字面词导致漏标，现已扩展。',
 1266:'低优先级抽查：水稻和番茄根际微生物群在干旱复水时的变化；摘要未显示耗水或植株生理恢复。',
 5234:'原23条复核：玉米和大豆盆栽，摘要明确通过不复水施加亏缺；早期规则误判为 P2。修正后作为盆径对蒸腾试验的方法参考 P3。',
 5516:'原23条复核：盆栽葡萄经历两轮十日干旱，采用重量法和液流测量整株蒸腾；P1 过程及方法候选，非水稻育秧直接证据。',
 1057:'原23条复核：摘要背景提及周期性，实际试验描述为一次亏缺及一次复水；P2 候选，不能只按背景词认定重复处理。',
 572:'原23条复核：水稻一次干燥过程测蒸腾和生长，复水后评价恢复；P2 候选。',
 4620:'原23条复核：水稻土壤水分波动和根系吸水；复水后再次干旱在摘要中部分属于背景，实际循环次数需核全文。',
 4653:'原23条复核：树木生物滤床反复干旱和蒸腾；P1 候选，为其他物种过程参考。',
}
spot=[]
for n,note in observations.items():
 r=s[n-1];assert int(r['record_number'])==n
 spot.append({'record_number':n,'doi':r['doi'],'title':r['title'],'historical_decision':r['historical_include'],'v2_primary':r['primary'],'abstract_status':r['abstract_status'],'evidence':r['evidence'],'audit_observation':note,'review_status':'助手题名摘要抽查，非领域专家人工确认'})
write('missed_screen_spotcheck.csv',spot)
# Raw per-page occurrences identify cross-page duplicates without deduplication by DOI.
pages=sorted((ROOT/'openalex_paginated/A').glob('page_*.json'))
occ=collections.defaultdict(list);page_rows=[]
for p in pages:
 x=json.loads(p.read_text());meta=x['meta'];result=x['results']
 for rank,item in enumerate(result,1):occ[item.get('id') or ''].append((p.name,rank))
 page_rows.append({'page':p.name,'meta_count':meta.get('count'),'received':len(result),'unique_ids_on_page':len({i.get('id') for i in result}),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
write('openalex_a_pages.csv',page_rows)
dup=[{'work_id':k,'occurrences':len(v),'locations':';'.join(f'{p}:{i}' for p,i in v)} for k,v in occ.items() if len(v)>1 or not k]
if dup:write('openalex_a_duplicates.csv',dup)
linked=[(i+1,r) for i,r in enumerate(raw) if 'OA_A_v3' in (r.get('matched_queries') or [])]
known_ids={str(r.get('openalex_id') or '') for _,r in linked}
metadata={'raw_page_count':len(pages),'reported_hit_counts':sorted({r['meta_count'] for r in page_rows}),'raw_records':sum(r['received'] for r in page_rows),'unique_work_ids':len([k for k in occ if k]),'missing_work_ids':len(occ.get('',[])),'duplicate_occurrences':sum(len(v)-1 for k,v in occ.items() if k),'deduplicated_papers_with_oa_a_v3_provenance':len(linked),'raw_unique_ids_matching_record_openalex_id':len(set(occ)&known_ids),'coverage_note':'经 DOI 合并后只有一个 openalex_id 字段；ID 直接匹配不足以判定其余未关联，按 matched_queries 独立统计去重论文。原检索标记 truncated，未核实完整性。'}
(OUT/'openalex_a_audit_summary.json').open('x',encoding='utf-8').write(json.dumps(metadata,ensure_ascii=False,indent=2))
print(json.dumps({'counts':dict(collections.Counter(r['primary'] for r in s)),'old23':dict(collections.Counter(r['primary'] for r in hist)),'priority':len(priority),'spotcheck':len(spot),'openalex':metadata},ensure_ascii=False,indent=2))
