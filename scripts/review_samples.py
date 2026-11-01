"""Generate a seeded, inspectable sample of automatically excluded records."""
import csv,random
from pathlib import Path
out=Path('review_v2_20261101')
with (out/'screening_v2.csv').open(encoding='utf8',newline='') as f:rows=list(csv.DictReader(f))
rng=random.Random(20261101)
sample=rng.sample([r for r in rows if r['primary']=='不相关'],12)
notes={2684:'稻纹枯病治理',1217:'除草剂在蒸渗仪中的迁移与残留，不是称重耗水试验',1233:'除草剂在稻田蒸渗仪中的多年残留，不是称重耗水试验',1966:'稻瘟病真菌相关研究',1122:'育秧田除草剂和杂草控制',2555:'杀虫剂对有益动物的影响',1106:'稻纹枯病通讯，题录摘要有限',1115:'育秧害虫防治通讯，题录摘要有限',2475:'杀虫剂及除草剂施用影响',1549:'稻瘟病菌遗传多样性',1622:'稻瘟病菌遗传多样性',1862:'稻瘟病抗性资源'}
for r in sample:
 r['assistant_spotcheck']=notes.get(int(r['record_number']),'抽样条目需复核')+'；仍需人工复核'
with (out/'automatic_exclusion_sample.csv').open('x',encoding='utf8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(sample[0]));w.writeheader();w.writerows(sample)
missing=[r for r in rows if r['abstract_status']=='missing']
with (out/'missing_abstract_queue.csv').open('x',encoding='utf8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(missing[0]));w.writeheader();w.writerows(missing)
print('excluded sample',len(sample),'missing abstracts',len(missing))
