"""Optional Excel review; website execution depends only on JSON. Python + openpyxl."""
import argparse,json
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill
from openpyxl.utils import get_column_letter
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();data=Path(__file__).resolve().parents[1]/'data';wb=Workbook();wb.remove(wb.active)
for name in ['properties','lodgings','transport','transfers','events','sources','price_history','research_runs']:
 rows=[]
 if name in ['research_runs','price_history']:
  obj=json.loads((data/(name+'.json')).read_text(encoding='utf-8'));rows=obj if isinstance(obj,list) else [record for shard in obj.get('shards',[]) for record in json.loads((data/shard['path']).read_text(encoding='utf-8'))]
 else:
  if (data/(name+'.json')).exists():rows.extend(json.loads((data/(name+'.json')).read_text(encoding='utf-8')))
  for batch in json.loads((data/'snapshot-index.json').read_text(encoding='utf-8')):
   path=data/'snapshots'/batch['id']/(('experiences' if name=='events' else name)+'.json')
   if path.exists():rows.extend(json.loads(path.read_text(encoding='utf-8')))
 rows=list({r['id']:r for r in rows if r.get('id')}.values()) if name not in ['price_history'] else rows;keys=list(dict.fromkeys(k for r in rows for k in r));ws=wb.create_sheet(name);ws.append(keys)
 for r in rows:
  cells=[]
  for k in keys:
   v=r.get(k);v=json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v
   if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@')):v="'"+v
   cells.append(v)
  ws.append(cells)
 ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
 for c in ws[1]:c.fill=PatternFill('solid',fgColor='142D3F');c.font=Font(color='FFFFFF',bold=True)
 for i,k in enumerate(keys,1):ws.column_dimensions[get_column_letter(i)].width=min(48,max(15,len(k)+2))
a.out.parent.mkdir(parents=True,exist_ok=True);wb.save(a.out);print(a.out.name)
