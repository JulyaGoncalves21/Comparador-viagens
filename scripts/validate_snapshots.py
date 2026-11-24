"""Validate preservation and completeness without printing research records."""
from pathlib import Path
import json,hashlib,re
root=Path(__file__).resolve().parents[1];data=root/'data';index=json.loads((data/'snapshot-index.json').read_text(encoding='utf-8'));summary=index[-1];folder=data/'snapshots'/summary['id'];count=0
for name,expected in summary['preservedBaseSha256'].items():
 assert hashlib.sha256((data/name).read_bytes()).hexdigest()==expected,('Existing dataset changed',name);count+=1
records={name:json.loads((folder/(name+'.json')).read_text(encoding='utf-8')) for name in ['lodgings','transport','experiences','sources','observations','ground','transfers']}
for name,items in records.items():
 assert len({x['id'] for x in items})==len(items),('Duplicate identifiers',name)
 for x in items:
  if x.get('url'):assert x['url'].startswith('https://'),(name,x['id'])
  if x.get('queriedAt') and ('V3' in x['id']):assert 'T' in x['queriedAt'],x['id']
  assert not re.search(r'(?i)C:\\Users\\',json.dumps(x)),('Private path',name,x['id'])
h=records['lodgings'];assert len({(x['destinationId'],x['guests']) for x in h})==48
assert all(x.get('amount') is None or not x.get('returnedRateOccupancy') or x['returnedRateOccupancy']==x['guests'] for x in h)
assert all(x['amount'] is None for x in records['ground'])
print(json.dumps({'preservedOriginalFiles':count,'newLodgings':len(h),'newTransport':len(records['transport']),'experiences':len(records['experiences']),'snapshots':len(records['observations']),'coverageDestinationGroups':48,'valid':True}))
