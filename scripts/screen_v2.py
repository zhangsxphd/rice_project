"""Conservative, reproducible title/abstract triage; labels are review candidates."""
import argparse
import csv
import html
import json
import re
import unicodedata
from pathlib import Path

VERSION='2.0.0'
PATTERNS={
 'plant':r'\b(?:plant(?:s)?|crop(?:s)?|seedling(?:s)?|rice|oryza|wheat|maize|corn|soybean|soybeans|soyabean|barley|sorghum|grapevines?|grape|vitis|cowpea|vigna|cotton|tomato|tobacco|cucumber|trees?|forest|forests|grass|ryegrass|seedling|leaf|leaves|stomata|canopy|orchard|paddy|seedlings)\b|水稻|作物|秧苗|植物|果树',
 'rice':r'\b(?:rice|oryza|paddy)\b|水稻',
 'nursery':r'\b(?:nurser(?:y|ies)|seedling\s+trays?|tray[- ]grown|mat[- ]type\s+seedling|mechaniz(?:ed|ation)\s+(?:rice\s+)?nurser(?:y|ies)|mechanical\s+transplant(?:ing|ed)?\s+seedling|rice\s+seedling\s+(?:production|raising))\b|育秧|机插育秧|苗盘|秧盘',
 'rice_nursery':r'\b(?:(?:rice|oryza|paddy)(?:\s+\w+){0,8}\s+(?:nurser(?:y|ies)|seedling\s+trays?|seedling\s+mats?|seedling\s+production)|(?:nurser(?:y|ies)|seedling\s+trays?)(?:\s+\w+){0,8}\s+(?:rice|oryza|paddy))\b|水稻育秧|水稻秧盘|水稻苗盘',
 'nursery_engineering':r'\b(?:mechaniz\w*|mechanical\s+transplant\w*|seedling\s+trays?|seedling\s+mats?|tray[- ]grown|mat[- ]type|substrat\w*|growing\s+media|nursery\s+irrigation|nursery\s+water\s+management|irrigation\s+schedul\w*)\b|机插|机械移栽|苗盘|秧盘|育秧基质|育秧灌水',
 'nursery_context':r'\b(?:water|irrigat\w*|moisture|substrate|soil|media|medium|hydric|watering|peat|growth\s+medium|water\s+management)\b|水分|基质|灌水|灌溉',
 'stress':r'\b(?:drought\w*|water[- ]deficit\w*|water[- ]stress\w*|soil[- ]drying|water\s+deprivation|water\s+with(?:holding|drawal)|withholding\s+(?:of\s+)?water|withheld\s+(?:of\s+)?water|withheld\s+irrigation|withholding\s+irrigation|limited\s+water|dry[- ]down|soil\s+moisture\s+deficit|deficit\s+irrigation|dehydration)\b|干旱|水分亏缺|水分胁迫|控水',
 'rewater':r'\b(?:re[- ]?water\w*|re[- ]?wet\w*|rehydrat\w*|water\s+resupply|water\s+re[- ]?supply|irrigation\s+resumption|water\s+restoration|restoration\s+of\s+water|rewatering|water\s+replenishment)\b|复水|复灌',
 'recovery':r'\b(?:recover\w*|resilien\w*|restor\w*|rebound|reversal)\b|恢复|复苏',
 'repeated':r'\b(?:(?:repeated|recurrent|recurring|cyclic|cyclical|multiple|successive|intermittent)\s+(?:episodes?\s+of\s+|periods?\s+of\s+)?(?:drought|water[- ]deficit|water[- ]stress|soil\s+drying)|(?:drought|water[- ]deficit|water[- ]stress|drying|dry[- ]down)(?:[- /–—]+(?:re[- ]?water\w*|re[- ]?wet\w*|rehydrat\w*))?\s+cycles|(?:drought|water[- ]deficit|water[- ]stress)\s*(?:[-–—/]\s*)?(?:re[- ]?water\w*|re[- ]?wet\w*|rehydrat\w*)\s+cycles|(?:cycles\s+of\s+)(?:drought|drying|water[- ]deficit|water[- ]stress)|(?:alternate|alternating)\s+wetting\s+and\s+drying|(?:drying\s+and\s+rewetting\s+cycles))\b|反复干旱|反复水分亏缺|周期性水分亏缺|多次干旱|干湿循环|干旱复水循环',
 'flux':r'\b(?:evapotranspiration|transpiration|water[- ]use|water[- ]uptake|water\s+consumption|water\s+loss|water\s+flux(?:es)?|water\s+extraction|sap\s+flow|actual\s+evaporation|water\s+balance)\b|耗水|蒸散|蒸腾|吸水|水量平衡|液流',
 'physiology':r'\b(?:photosynth\w*|stomatal\s+conductance|gas\s+exchange|leaf\s+water\s+potential|plant\s+water\s+potential|relative\s+water\s+content|leaf\s+expansion|growth\s+rate|biomass|root\s+growth|hydraulic\s+conductance|chlorophyll\s+fluorescence)\b|生理恢复|气孔导度|光合速率|叶水势|根系生长',
 'method':r'\b(?:weigh(?:ing|able)\s+lysimeter\w*|weigh(?:ing|able)[- ]based\s+lysimeter\w*|continuous(?:ly)?\s+weigh(?:ing|ed)|gravimetric\s+(?:lysimeter\w*|system\w*|method\w*|measurement\w*|monitoring)|automated\s+(?:weighing|irrigation|water(?:ing)?\s+control)|automatic\s+(?:weighing|irrigation|soil\s+moisture\s+control)|soil\s+water\s+balance|water\s+balance\s+(?:method|model|approach|measurement)|pot\s+weighing|weighing\s+(?:pots?|systems?|scales?))\b|连续称重|称重式蒸渗|称重法|水量平衡|自动水分控制',
 'pot_method':r'\bpot\s+(?:size|volume)\b',
 'offtopic_title':r'\b(?:insecticides?|herbicides?|sheath\s+blight|rice\s+blast|armyworms?|insect\s+nurseries|insect\s+pests?)\b',
 'clinical':r'\b(?:clinical\s+trial|clinical\s+patients?|hospital\s+patients?|cancer\s+patients?|surgical\s+patients?|neonatal\s+intensive\s+care|dental\s+patients?|psychiatric\s+patients?)\b|临床试验|住院患者',
 'efficiency':r'\b(?:water[- ]use\s+efficiency|intrinsic\s+water[- ]use\s+efficiency|wue)\b|水分利用效率',
}
RX={k:re.compile(v,re.I) for k,v in PATTERNS.items()}
SPLIT=re.compile(r'(?<=[.!?。！？])\s+|\n+')

def normalize(s):
 return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',html.unescape(re.sub(r'<[^>]+>',' ',str(s or ''))))).strip()

def matches(text):
 return {k:[m.group(0) for m in list(rx.finditer(text))[:4]] for k,rx in RX.items()}

def evidence(title,abstract,keys):
 snippets=[]
 for kind,text in [('title',title),('abstract',abstract)]:
  for sentence in SPLIT.split(text):
   hit=[k for k in keys if RX[k].search(sentence)]
   if hit:
    snippets.append({'field':kind,'signals':hit,'excerpt':sentence[:300]})
    if len(snippets)>=4:return snippets
 return snippets or ([{'field':'title','signals':[],'excerpt':title[:300]}] if title else [])

def classify(record):
 title=normalize(record.get('title'));abstract=normalize(record.get('abstract'));text=title+' '+abstract
 h=matches(text);has=lambda name:bool(h[name]);
 # Recognize explicit recurrent drought rather than seed/chemical priming or generic recovery.
 cycle=any(not re.match(r'[- ](?:responsive|related|tolerant|resistance|tolerance)\b',text[m.end():],re.I) for m in RX['repeated'].finditer(text));stress=has('stress');plant=has('plant');flux=has('flux');rewet=any(not re.search(r'\b(?:not|without|never|avoid(?:ed|ing)?)\s*$',text[max(0,m.start()-24):m.start()],re.I) for m in RX['rewater'].finditer(text));recover=has('recovery');phys=has('physiology');meth=has('method') or (has('pot_method') and flux)
 strong_flux=bool(RX['flux'].search(RX['efficiency'].sub('',text)))
 labels=[]
 if plant and stress and cycle and (flux or (rewet and (recover or phys))):labels.append('P1')
 if plant and stress and (rewet or recover) and (flux or phys):labels.append('P2')
 if meth and (plant or stress):labels.append('P3')
 rice_context=re.sub(r'\brice\s+(?:husk|husks|hull|hulls|bran|straw|straws|husk-derived)\b',' ',text,flags=re.I)
 if RX['rice_nursery'].search(rice_context) and has('nursery_context') and has('nursery_engineering'):labels.append('P4')
 if labels:category=labels[0]
 elif abstract and ((has('clinical') and not plant and not meth) or (RX['offtopic_title'].search(title) and not (stress or rewet or recover or flux or meth or has('nursery_engineering')))):category='不相关'
 else:category='信息不足'
 if RX['rice_nursery'].search(rice_context):object_relation='水稻育秧或苗盘候选；是否工程化及水分管理待核'
 elif RX['rice'].search(title):object_relation='题名涉及水稻；是否实际研究对象及育秧阶段待核'
 elif has('rice'):object_relation='摘要提及水稻；可能仅为背景或比较对象，物种与阶段待核'
 elif plant:object_relation='其他作物、树木或植物过程/方法参考，需核对物种和阶段'
 else:object_relation='研究对象未充分识别，需人工核对'
 reasons={'P1':'文本提示反复亏缺并涉及耗水、蒸腾或复水恢复；是否同一实验及重复循环待核。','P2':'文本提示缺水与复水或恢复及耗水/生理指标；时序与是否单次处理待核。','P3':'文本提示称重、蒸渗、自动控制或水量平衡相关方法；适用性待核。','P4':'文本同时提示水稻、育秧环境及水分或基质管理；工程化条件待核。','不相关':'题名及摘要提示临床、病虫害或除草剂研究，未检出相关水分过程或方法信号；暂排除并复核。','信息不足':'现有题名摘要不足以可靠归入各类；不能以缺少关键词证明不相关。'}
 notes=[]
 if not abstract:notes.append('缺摘要；不能据此排除')
 if has('efficiency') and not strong_flux:notes.append('仅见水分利用效率，不可等同实际耗水量')
 if record.get('dedup_conflicts'):notes.append('身份冲突待核')
 types=' '.join(map(str,record.get('document_types') or [])).lower()
 if any(x in types for x in ('review','editorial','preprint')):notes.append('综述、编辑或预印本类型需核对')
 keys=['repeated','stress','rewater','recovery','flux','method','nursery','rice','physiology','clinical','offtopic_title']
 return {'primary':category,'secondary':labels,'object_relation':object_relation,'reason':reasons[category]+(' '+ '；'.join(notes)+'。' if notes else ''),'evidence':evidence(title,abstract,keys),'signals':{k:v for k,v in h.items() if v},'abstract_status':'available' if abstract else 'missing','review_required':'yes','decision_method':'deterministic_rules_v'+VERSION,'needs_fulltext':'yes'}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('output');p.add_argument('--history',help='Optional historical CSV for audit only');args=p.parse_args()
 inp=Path(args.input).resolve();out=Path(args.output).resolve()
 if inp==out or out.exists():raise FileExistsError('Output must be a new file; history is never overwritten')
 history=list(csv.DictReader(Path(args.history).open(encoding='utf-8-sig',newline=''))) if args.history else []
 fields=['record_number','uid','openalex_id','doi','title','year','primary','secondary','object_relation','reason','evidence','signals','abstract_status','historical_include','matched_queries','decision_method','review_required','needs_fulltext']
 with inp.open(encoding='utf-8') as source,out.open('x',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for i,line in enumerate(source,1):
   if not line.strip():continue
   r=json.loads(line);v=classify(r);prior='not_available'
   if history:
    if i>len(history):raise ValueError('History has fewer records')
    old=history[i-1]
    if old.get('index')!=str(i) or normalize(old.get('title'))!=normalize(r.get('title')) or (old.get('doi') or '').lower()!=(r.get('doi') or '').lower():raise ValueError('History does not match input at record '+str(i))
    prior='historical_include' if old.get('decision')=='include' else 'historical_'+str(old.get('decision','unknown'))
   w.writerow({'record_number':i,'uid':r.get('uid') or '', 'openalex_id':r.get('openalex_id') or '', 'doi':r.get('doi') or '', 'title':r.get('title') or '', 'year':r.get('publish_year') or '', **{k:json.dumps(v[k],ensure_ascii=False) if k in ('secondary','evidence','signals') else v[k] for k in v}, 'historical_include':prior, 'matched_queries':';'.join(r.get('matched_queries') or [])})
 print('wrote',out)
if __name__=='__main__':main()
