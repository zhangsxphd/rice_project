import csv,json,re,hashlib
from collections import Counter
from pathlib import Path
root=Path('stage_focus')
expected='4c25710d8d2c61c604949d71eabe782d49ad4cfb07cd0b85f29c5e22c17255e7'
if hashlib.sha256((root/'deduplicated.jsonl').read_bytes()).hexdigest()!=expected: raise ValueError('Curated row numbers only apply to the recorded frozen dataset')
records=[json.loads(l) for l in open(root/'deduplicated.jsonl')];out=[]
plant=['rice','oryza','wheat','maize','corn','barley','soybean','cotton','tomato','grape','sorghum','seedling','plant','crop','tree','cucumber','potato','canola','leaf','stomata','seedlings']
stress=['drought','water deficit','water stress','soil drying','soil moisture deficit','water limitation','water-limited']
flux=['transpiration','evapotranspiration','water use','water uptake','water consumption','water loss','water flux','water balance','sap flow']
method=['lysimeter','weighing','gravimetric','continuous weighing','weighable','sap flow','water balance']
rewet=['rewater','re-water','rehydrat','re-wet','rewetting']
cycle=re.compile(r'(?:drought|water deficit|water stress|soil drying).{0,45}(?:repeated|recurrent|cyclic|cycles|cycle|priming)|(?:repeated|recurrent|cyclic|cycles|cycle|priming).{0,45}(?:drought|water deficit|water stress|soil drying)',re.I|re.S)
curated={572:'水稻干燥过程的蒸腾动态和复水；复水后蒸腾是否连续测量待全文确认',585:'水稻盆栽干旱与复水，摘要报告蒸腾与耗水',589:'不同干旱持续时间与复水恢复，报告蒸腾变化',1057:'水稻及大豆干旱与复水气体交换，包含蒸腾',1251:'水稻盆栽干旱与复水阶段的蒸腾动态',1253:'盆栽称重累计蒸腾与土层水分提取比较，方法用途',1254:'水稻盆栽水分提取及称重估计累计蒸腾',1263:'小麦干旱与复水处理下叶片蒸腾响应',1265:'水稻与小麦干旱及复水前的蒸腾比较',1267:'水分波动与复水过程中根系及后续土层取水',1270:'水稻干旱后复水与蒸散及根系恢复',4606:'土壤水分波动、复水与根系吸水',4619:'水分波动复水及后续深层耗水',4620:'周期水分波动与深层取水；身份冲突须核查',4621:'干湿交替期间复水与水分吸收',4653:'树木反复干旱与生物滤池的蒸腾耗水',4665:'森林树木重复干旱及液流测量',4891:'大豆盆栽不同阶段缺水、复水后的蒸散过程',4985:'牛豇豆土壤干燥和复水试验含蒸腾测量',5159:'葡萄水分亏缺与复水期间叶片蒸腾及水分效率',5166:'葡萄干旱复水后蒸腾恢复过程',5234:'玉米和大豆盆径对缺水蒸腾测量的影响，方法用途',5516:'葡萄两次干旱循环，称重与液流测量整株蒸腾'}
for i,r in enumerate(records,1):
 title=(r.get('title') or '').lower();abstract=(r.get('abstract') or '').lower();text=title+' '+abstract
 hits=lambda words:[w for w in words if w in text]
 p,s,f,m,w=map(hits,(plant,stress,flux,method,rewet));cy=bool(cycle.search(text));uses=[]
 if any(w in text for w in ['nursery','seedling tray','transplant','育秧']):uses.append('A')
 if s and (w or cy):uses.append('B')
 if m:uses.append('C')
 if s and any(w in text for w in ['intensity','severity','duration','repeated','cyclic','cycle','rewater','recovery']):uses.append('D')
 if not abstract:decision='maybe';reason='缺摘要，信息不足；不得仅依据题名排除。'
 elif i in curated:decision='include';reason='助手逐篇题名摘要初核：'+curated[i]+'；仍须全文及人工复核。'
 elif p and s and f and (w or cy):decision='maybe';reason='关键词同时涉及亏缺、耗水和复水或循环，但关联性尚需逐篇确认。'
 elif p and s and m and f:decision='maybe';reason='题名或摘要显示植物水分亏缺和称重、水量平衡或液流等测量词；是否覆盖周期或恢复需复核。'
 elif s and (w or cy):decision='maybe';reason='出现亏缺和复水或反复亏缺词，但耗水测量或研究对象仍需核对。'
 elif not any(z in text for z in ['water','drought','dry','irrigat','moist','evapotranspiration','transpiration','weigh','lysimeter','nursery','seedling','tray','transplant','hydraulic','rewet','rehydrat']):decision='exclude';reason='已有摘要，但题名和摘要均未见宽泛的水分、育秧、干燥、测量或复水相关词；自动初筛暂排除，须人工复核。'
 else:decision='maybe';reason='可能涉及水分亏缺、耗水或测量方法，但缺少明确的周期与复水证据。'
 if r.get('dedup_conflicts'):reason+=' 身份存在待核冲突。'
 reason+=' 命中词：'+'; '.join(x+'='+','.join(v[:6]) for x,v in [('对象',p),('亏缺',s),('耗水',f),('复水',w),('方法',m)] if v)+('；检测到重复亏缺词组' if cy else '')+'。'
 out.append({'index':i,'doi':r.get('doi'),'title':r.get('title'),'year':r.get('publish_year'),'decision':decision,'reason':reason,'uses':';'.join(uses),'matched_queries':';'.join(r.get('matched_queries',[])),'abstract_status':'available' if abstract else 'missing','identity_conflicts':json.dumps(r.get('dedup_conflicts',[]),ensure_ascii=False)})
with open(root/'screening.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
print('decisions',dict(Counter(x['decision'] for x in out)),'abstracts',dict(Counter(x['abstract_status'] for x in out)))
for x in [x for x in out if x['decision']=='include'][:25]:print(x['index'],x['title'])
