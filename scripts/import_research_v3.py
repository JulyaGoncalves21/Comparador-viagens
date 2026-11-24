"""Append-only research import. Inputs are real connector/web observations, never mock data.
Usage: python scripts/import_research_v3.py --input-dir ..
Run with a NEW batch identifier for later searches; existing snapshots cannot change.
"""
import argparse,json,hashlib,re,datetime
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
def uid(prefix,*xs):return prefix+'_'+hashlib.sha256('|'.join(map(str,xs)).encode()).hexdigest()[:18]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def canonical(u):
 p=urlsplit(u or '');return (p.netloc.lower().removeprefix('www.'),p.path.rstrip('/'))
def safe(x):
 if isinstance(x,dict):return {k:safe(v) for k,v in x.items() if k not in ['snapshot','priceSnippets']}
 if isinstance(x,list):return [safe(v) for v in x]
 if isinstance(x,str):return re.sub(r'(?i)(?<![a-z])[A-Z]:\\[^\n;]+','[arquivo local omitido]',x)
 return x
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-dir',type=Path,default=Path('..'));ap.add_argument('--batch',default='2026-11-23-v3');a=ap.parse_args();root=Path(__file__).resolve().parents[1];data=root/'data';folder=data/'snapshots'/a.batch;folder.mkdir(parents=True,exist_ok=True)
 old={n:load(data/(n+'.json')) for n in ['properties','lodgings','transport','transfers','history','sources']};oldprops={canonical(p.get('url')):p for p in old['properties']};hotel=load(a.input_dir/'v3_hospedagens_completas_raw.json');flights=load(a.input_dir/'v3_voos_raw.json');rooms=load(a.input_dir/'v3_quartos_raw.json');ground=safe(load(a.input_dir/'v3_terrestre_pesquisa.json')['records']);experiences=safe(load(a.input_dir/'v3_eventos_pesquisa.json')['records']);newprops={};hs=[];ps=[];ts=[];sources=[];observations=[];roommap={}
 def source(kind,name,url,at,notes):
  sid=uid('SV3',kind,name,url,at);sources.append({'id':sid,'category':kind,'title':name,'url':url,'queriedAt':at,'status':'Consulta real · cotação parcial','supports':notes,'pending':'Confirmar estoque, pagamento, alocação e taxas não discriminadas.'});return sid
 def observe(kind,q,identity):
  observations.append({'id':uid('snapshot',kind,q['id'],q.get('queriedAt')),'entityType':kind,'entityId':identity,'quoteId':q['id'],'destinationId':q.get('destinationId'),'guests':q.get('guests'),'units':q.get('units'),'checkin':q.get('checkin',q.get('departure',q.get('date'))),'checkout':q.get('checkout',q.get('return')),'amount':q.get('amount'),'currency':q.get('currency'),'roomName':q.get('roomName'),'conditionsKey':q.get('conditionsKey'),'sector':q.get('sector'),'ticketCategory':q.get('ticketCategory'),'queriedAt':q.get('queriedAt'),'status':q.get('status'),'url':q.get('url'),'sourceId':q.get('sourceId'),'rateVerified':q.get('rateVerified',False),'notes':q.get('notes')})
 for query in hotel:
  for x in query.get('result',{}).get('accommodations',[]):
   k=query['destinationId'];loc=x.get('location',{});expected='pe' if k=='lima' else 'cl' if k=='santiago' else 'ar' if k=='buenos' else 'br'
   if loc.get('country_code')!=expected:
    observations.append({'id':uid('rejected',x.get('id'),query['queriedAt']),'entityType':'lodging','entityId':str(x.get('id')),'status':'rejeitado','notes':'País retornado diverge do destino solicitado','url':x.get('url'),'queriedAt':query['queriedAt']});continue
   u=x['url'];oldp=oldprops.get(canonical(u));pid=oldp['id'] if oldp else uid('property',*canonical(u));props={**(oldp or {}),'id':pid,'destinationId':k,'name':x['name'],'platform':'Booking','type':x.get('accommodationType'),'address':loc.get('address'),'area':loc.get('district_name'),'country':loc.get('country_name'),'coordinates':loc.get('coordinates'),'review':x.get('rating',{}).get('review_score'),'reviewScale':10,'reviewCount':x.get('rating',{}).get('number_of_reviews'),'facilities':x.get('facilities',[]),'url':u,'queriedAt':query['queriedAt']};newprops[pid]=props
   # Photo URL retained as evidence only. No image is published without usage permission.
   sid=source('Booking · hospedagem',x['name'],u,query['queriedAt'],'Busca para ocupação/unidades exatas; total exibido, sem quarto/taxas finais discriminadas.')
   q={'id':uid('HV3',a.batch,x['id'],query['guests'],query['units'],query['queriedAt']),'propertyId':pid,'destinationId':k,'guests':query['guests'],'units':query['units'],'checkin':'2027-02-05','checkout':'2027-02-10','amount':x.get('price',{}).get('book'),'currency':x.get('price',{}).get('currency','BRL'),'priceBasis':'group','status':'pendente','priceStatus':'confirmado','queriedAt':query['queriedAt'],'url':u,'sourceId':sid,'capacity':None,'beds':None,'privacy':'A conferir','bathroom':'A conferir','privacyVerified':False,'rateVerified':False,'taxes':'Preço exibido; discriminação de taxas/limpeza/serviço e checkout final pendentes','cancellation':None,'prepayment':None,'roomName':None,'conditionsKey':None,'notes':'Consulta nova para grupo/unidades exatos. Não comprova alocação, estoque ou tarifa integral.','batchId':a.batch}
   hs.append(q);roommap[(x['id'],query['guests'])]=(pid,q);observe('lodging',q,pid)
 for query in rooms:
  base=roommap.get((query['propertyId'],query['guests']))
  if not base:continue
  pid,h=base;result=query.get('result',{})
  if not isinstance(result,dict):continue
  for room in result.get('rooms',[]):
   for rate in room.get('rates',[]):
    facilities=room.get('facilities',[]);text='; '.join(facilities);cap=room.get('max_occupancy');u=rate['checkout_url'];block=parse_qs(urlsplit(u).query).get('highlighted_blocks',[''])[0].split('_');occupancy=int(block[2]) if len(block)>2 and block[2].isdigit() else None;verified=occupancy==query['guests'] and cap is not None and cap>=query['guests'];dorm=bool(re.search(r'dormit[oó]rio|dormitory|cama em',room['name'],re.I));bath='Compartilhado' if re.search('banheiro compartilhado|toalete compartilhado',text,re.I) else 'Privativo' if re.search('banheiro privativo',text,re.I) else 'A conferir'
    q={**h,'id':uid('HRV3',a.batch,u,rate['price_total'],query['queriedAt']),'amount':rate['price_total'] if verified else None,'observedAmount':rate['price_total'],'returnedRateOccupancy':occupancy,'roomName':room['name'],'capacity':cap,'beds':room.get('bed_summary'),'facilities':facilities,'privacy':'Dormitório coletivo' if dorm else 'Unidade privativa','bathroom':bath,'privacyVerified':verified and not dorm,'rateVerified':verified,'cancellation':rate.get('cancellation_type'),'cancellationUntil':rate.get('free_cancellation_until'),'mealPlan':rate.get('meal_plan'),'availabilityCount':rate.get('availability_count'),'url':u,'queriedAt':query['queriedAt'],'notes':'Quarto consultado para ocupação exata; estoque/taxas/pagamento a conferir.' if verified else f'Tarifa retornada com ocupação {occupancy}; pedida {query["guests"]}. Preço observado preservado separadamente e não aplicado ao orçamento.','conditionsKey':None}
    hs.append(q);observe('lodging',q,pid)
 for query in flights:
  r=query.get('result',{});u=r.get('search_url');sid=source('Booking · voo',query['airport'],u,query['queriedAt'],'Busca I/V nova para o grupo; bagagem, segmentos e cobrança final pendentes.')
  for x in r.get('flight_offers',[]):
   q={'id':uid('PV3',a.batch,x['id'],query['guests']),'destinationId':query['destinationId'],'mode':'Avião','terminal':query['airport'],'guests':query['guests'],'departure':'2027-02-05','return':'2027-02-10','amount':x['total_price']['amount'],'currency':x['total_price']['currency'],'priceBasis':'group','companies':', '.join(x['airlines']),'stops':x['stops'],'departureSummary':x['departure_time'],'arrivalSummary':x['arrival_time'],'url':u,'queriedAt':query['queriedAt'],'sourceId':sid,'status':'pendente','priceStatus':'confirmado','itineraryVerified':False,'conditionsKey':None,'luggage':None,'luggagePolicy':'Não retornada: conferência manual','notes':'Resumo não separa ambos os segmentos. Não calcular duração nem dias úteis pela subtração desses horários.','batchId':a.batch}
   ps.append(q);observe('transport',q,query['airport']+'|'+str(query['guests']))
 oldair={re.search(r'/rooms/(\d+)',p.get('url') or '')[1]:p for p in old['properties'] if re.search(r'/rooms/(\d+)',p.get('url') or '')}
 for record in ground:
  r={**record,'id':uid('GV3',a.batch,record['id']),'batchId':a.batch};r['sourceId']=source(r['category'],r['id'],r.get('url'),r['queriedAt'],r.get('notes'));r['source']=safe(r.get('source'))
  if r['category']=='airbnb':
   p=oldair.get(str(r.get('propertyId')))
   if p:
    q={**r,'propertyId':p['id'],'units':1,'checkin':r['departure'],'checkout':r['return'],'privacyVerified':False,'rateVerified':False,'capacity':r.get('previousCapacity'),'roomName':None,'conditionsKey':None,'currency':'BRL'};hs.append(q);observe('lodging',q,p['id'])
  elif r['category'] in ['bus','onibus','ônibus']:
   q={**r,'mode':'Ônibus','terminal':'Rodoviária e conexões a conferir','itineraryVerified':False,'conditionsKey':None};ps.append(q);observe('transport',q,r['destinationId']+'|bus')
  elif r['category'] in ['transfer','transfers']:ts.append({**r,'terminal':r.get('terminal'),'stages':'; '.join(r.get('stages',[])) if isinstance(r.get('stages'),list) else r.get('stages'),'referenceAmount':None})
 for x in experiences:
  x['eventKey']=x['id'];x['id']=uid('EV3',a.batch,x['id']);x['batchId']=a.batch;x['conditionsKey']=None;x['sourceId']=source('Evento/experiência',x['name'],x.get('url'),x['queriedAt'],x.get('notes'));observe('experience',x,'event:'+x['eventKey'])
 # Old observations remain inspectable; they never acquire fabricated complete conditions.
 for h in old['lodgings']:observe('lodging',h,h['propertyId'])
 for p in old['transport']:observe('transport',p,p.get('terminal','')+'|'+str(p.get('guests')))
 for x in old['history']:
  if x.get('status')=='rejeitado':observations.append({**x,'entityType':'lodging','entityId':x.get('propertyName'),'quoteId':x['id'],'conditionsKey':None})
 priorindex=data/'snapshot-index.json'
 if priorindex.exists():
  for previous in load(priorindex):
   prior=data/'snapshots'/previous['id']/'observations.json'
   if previous['id']!=a.batch and prior.exists():observations.extend(load(prior))
 sources=list({x['id']:x for x in sources}.values());observations=list({x['id']:x for x in observations}.values())
 for q in hs:
  if q.get('amount') is None:q['priceStatus']='pendente'
 outputs={'properties':list(newprops.values()),'lodgings':hs,'transport':ps,'transfers':ts,'experiences':experiences,'sources':sources,'ground':ground,'observations':observations}
 for name,value in outputs.items():
  p=folder/(name+'.json');content=json.dumps(safe(value),ensure_ascii=False,separators=(',',':'))
  if p.exists() and p.read_text(encoding='utf-8')!=content:raise SystemExit('Immutable snapshot exists with different content: '+str(p))
  p.write_text(content,encoding='utf-8')
 for n in [2,3,5,6]:
  for name in ['lodgings','transport','transfers']:
   target=folder/(name+'-'+str(n)+'.json');content=json.dumps([x for x in outputs[name] if x.get('guests')==n],ensure_ascii=False,separators=(',',':'))
   if target.exists() and target.read_text(encoding='utf-8')!=content:raise SystemExit('Immutable shard differs: '+str(target))
   target.write_text(content,encoding='utf-8')
 summary={'id':a.batch,'label':'Pesquisa Carnaval 2027 · 23/11/2026','queriedAt':max(x.get('queriedAt','') or '' for x in observations),'clientDate':'2026-11-23','counts':{n:len(v) for n,v in outputs.items()},'requests':{'lodging':len(hotel),'rooms':len(rooms),'flights':len(flights)},'roomRatesOccupancyVerified':sum(bool(x.get('rateVerified')) for x in hs),'pendingCompleteTrips':True,'preservedBaseSha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.json') if p.name not in ['snapshot-index.json']},'photoPolicy':'Nenhuma foto de imóvel utilizada sem permissão de uso confirmada.'}
 indexpath=data/'snapshot-index.json';index=load(indexpath) if indexpath.exists() else []
 if not any(x['id']==a.batch for x in index):index.append(summary)
 else:index=[summary if x['id']==a.batch else x for x in index]
 indexpath.write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8');(folder/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(summary['counts'],ensure_ascii=False))
if __name__=='__main__':main()
