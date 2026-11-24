from pathlib import Path
import json,hashlib,datetime,collections,re
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--input-dir',type=Path,required=True);ap.add_argument('--batch',default='2026-11-24-r1');a=ap.parse_args();root=Path(__file__).resolve().parents[1];data=root/'data';batch=a.batch;folder=data/'snapshots'/batch
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
ground=load(a.input_dir/'p24_terrestre.json');events=load(a.input_dir/'p24_eventos.json');hotel=load(a.input_dir/'p24_hospedagens.json');rooms=load(a.input_dir/'p24_quartos_completos.json');flights=load(a.input_dir/'p24_voos.json');h=load(folder/'lodgings.json');p=load(folder/'transport.json');exp=load(folder/'experiences.json');obs=load(folder/'observations.json')
counts=collections.Counter(x['availabilityStatus'] for x in h);pairs={ (x['destinationId'],x['guests']) for x in h if x.get('availabilityVerified')};baseline=load(data/'lodgings.json');previous=load(data/'snapshots/2026-11-23-v3/lodgings.json');audit={'baselineCommit':'6f9009a63929e1a2dd77e48c8500116946b76329','existingLodgingObservations':len(baseline)+len(previous),'availabilityExplicitlyVerifiedBeforeRun':sum(bool(x.get('availabilityVerified')) for x in baseline+previous),'rule':'HTTP200 e preço de busca nunca provam disponibilidade. Histórico preservado; apenas resposta de tarifa/quarto com estoque positivo, datas, unidades e ocupação exatas pode entrar no ranking principal.'}
failures=[]
for kind,queries in [('lodging',hotel),('room',rooms),('flight',flights)]:
 for q in queries:
  if q.get('error') or q.get('result',{}).get('error') or q.get('result',{}).get('error_code'):failures.append({'category':kind,'destinationId':q['destinationId'],'guests':q['guests'],'queriedAt':q['queriedAt'],'error':q.get('error') or q.get('result')})
  elif kind=='room' and not q.get('result',{}).get('rooms'):failures.append({'category':'room_evidence','destinationId':q['destinationId'],'guests':q['guests'],'queriedAt':q['queriedAt'],'error':'Nenhuma tarifa retornada. Não prova esgotamento; disponibilidade não verificada.'})
for r in ground['records']:
 source=r.get('source') or {};code=source.get('httpStatus')
 if source.get('error') or isinstance(code,int) and code>=400:failures.append({'category':r['category'],'destinationId':r['destinationId'],'guests':r.get('guests'),'url':r.get('url'),'queriedAt':r.get('queriedAt'),'error':source.get('error') or 'HTTP '+str(code)})
newrun={'id':batch,'startedAt':min(q['queriedAt'] for q in hotel+rooms+flights),'completedAt':max(q['queriedAt'] for q in hotel+rooms+flights),'origin':'CWB','checkin':'2027-02-05','checkout':'2027-02-10','guests':[2,3,5,6],'destinations':12,'requests':{'lodging':len(hotel),'room':len(rooms),'flight':len(flights),'ground':len(ground['records']),'eventUrls':len(events.get('consultationLog',[]))},'newRecords':{'lodgings':len(h),'transport':len(p),'transfers':len(load(folder/'transfers.json')),'events':len(exp),'ground':len(ground['records']),'price_history':len(obs)},'availability':{'rateObservationsVerified':counts['available'],'rateObservationsUnverified':counts['unverified'],'destinationGroupsVerified':len(pairs),'destinationGroupsResearched':48,'eventsExactAvailabilityVerified':0,'eventsUnavailableCategory':sum(x.get('availabilityStatus')=='unavailable_category' for x in exp)},'failureCount':len(failures),'status':'completed_with_pending_information','limitations':['Custos finais/taxas, bagagem e itinerários a conferir','Sete combinações destino/grupo não tiveram tarifa com estoque exato comprovado','Ausência de tarifa retornada não significa esgotamento','Categorias esgotadas na landing do evento não comprovam cada noite'],'initialAudit':audit}
for failure in failures:failure['id']='failure_'+hashlib.sha256(json.dumps(failure,ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:18];failure['runId']=batch
for name,value in [('research_run',newrun),('failures',failures),('availability_audit',audit),('destination_contexts',ground.get('poleAndNightAssessment',{}))]:
 (folder/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
prior=load(data/'snapshot-index.json');runs=[];shards=[]
for run in prior:
 path=data/'snapshots'/run['id']
 item=newrun if run['id']==batch else {'id':run['id'],'origin':'CWB','checkin':'2027-02-05','checkout':'2027-02-10','guests':[2,3,5,6],'requests':run['requests'],'newRecords':run['counts'],'status':'historical_completed_with_pending_information','queriedAt':run['queriedAt']}
 runs.append(item);shards.append({'runId':run['id'],'path':'snapshots/'+run['id']+'/observations.json','count':len(load(path/'observations.json')),'appendOnly':True})
(data/'research_runs.json').write_text(json.dumps(runs,ensure_ascii=False,indent=2),encoding='utf-8');(data/'price_history.json').write_text(json.dumps({'schemaVersion':1,'shards':shards,'totalSnapshots':sum(x['count'] for x in shards),'rule':'Compare somente dimensões e condições comprovadamente equivalentes.'},ensure_ascii=False,indent=2),encoding='utf-8')
latest={}
for shard in shards:
 for x in load(data/shard['path']):
  key=x.get('productId') or x.get('quoteId') or x['id']
  if key not in latest or (x.get('queriedAt') or '')>(latest[key].get('queriedAt') or ''):latest[key]=x
(data/'latest_prices.json').write_text(json.dumps([{'productId':k,'snapshotId':v['id'],'queriedAt':v.get('queriedAt'),'priceObservedAt':v.get('priceObservedAt',v.get('queriedAt')),'amount':v.get('amount'),'currency':v.get('currency'),'availabilityStatus':v.get('availabilityStatus','unverified'),'runId':v.get('runId')} for k,v in latest.items()],ensure_ascii=False,separators=(',',':')),encoding='utf-8')
manifest={'schemaVersion':1,'entities':{name:{'base':name+'.json','snapshots':[f"snapshots/{x['id']}/{('experiences' if name=='events' else name)}.json" for x in prior] if name not in ['destinations'] else []} for name in ['destinations','properties','lodgings','transport','transfers','events','sources']},'price_history':'price_history.json','research_runs':'research_runs.json','latest_prices':'latest_prices.json','availabilityPolicy':'Disponibilidade expira em24h; requer estoque de tarifa, ocupação e unidades exatas. Nunca inferida deHTTP200.'};(data/'database.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'new':newrun['newRecords'],'availability':newrun['availability'],'snapshots':sum(x['count'] for x in shards),'failures':len(failures)},ensure_ascii=False))
