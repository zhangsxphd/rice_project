"""Export canonical Wos_Agent JSONL records to RIS without inventing metadata."""
import argparse
import json
from pathlib import Path


def ris(records):
    result=[]
    def line(tag, value):
        if value is not None and str(value).strip():
            result.append(f'{tag}  - ' + ' '.join(str(value).splitlines()))
    for r in records:
        types = {str(t).lower() for t in (r.get('document_types') or [])}
        result.append('TY  - JOUR' if types & {'article', 'journal-article', 'review', 'review article'} else 'TY  - GEN')
        line('TI',r.get('title'))
        for a in r.get('author_names') or []: line('AU', a)
        line('JO',r.get('source_title'))
        line('PY',r.get('publish_year'))
        line('DO',r.get('doi'))
        line('AB',r.get('abstract'))
        for k in r.get('author_keywords') or []: line('KW',k)
        line('UR',r.get('record_url'))
        result.extend(('ER  - ',''))
    return '\n'.join(result)+'\n' if result else ''


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('input'); p.add_argument('output'); a=p.parse_args()
    rows=[json.loads(x) for x in Path(a.input).read_text(encoding='utf-8').splitlines() if x.strip()]
    Path(a.output).write_text(ris(rows),encoding='utf-8')
    print(f'exported {len(rows)} records')

if __name__=='__main__': main()
