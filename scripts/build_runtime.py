"""Run after import_workbook.py. Keeps full original JSON; strips legacy duplicates only in runtime copies."""
import json
from pathlib import Path
data=Path(__file__).resolve().parents[1]/'data'
for name in ['lodgings','transport','transfers','routes']:
 rows=json.loads((data/(name+'.json')).read_text(encoding='utf-8'))
 (data/(name+'-runtime.json')).write_text(json.dumps([{k:v for k,v in x.items() if k!='legacy'} for x in rows],ensure_ascii=False,separators=(',',':')),encoding='utf-8')
