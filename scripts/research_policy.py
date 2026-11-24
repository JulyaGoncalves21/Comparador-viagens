"""Evidence-based availability; no HTTP success or search price is promoted to inventory."""
import hashlib,datetime
from urllib.parse import urlsplit,parse_qs
def uid(prefix,*xs):return prefix+'_'+hashlib.sha256('|'.join(map(str,xs)).encode()).hexdigest()[:18]
def enrich_run(run_id,hs,ps,events,observations,rooms,ground):
 evidence={}
 for query in rooms:
  for room in query.get('result',{}).get('rooms',[]):
   for rate in room.get('rates',[]):
    u=rate.get('checkout_url','');args=query['args'];p=parse_qs(urlsplit(u).query);block=p.get('highlighted_blocks',[''])[0].split('_');n=query['guests'];units=query['units'];occ=int(block[2]) if len(block)>2 and block[2].isdigit() else None
    valid=units==1 and occ==n and (room.get('max_occupancy') or 0)>=n and (rate.get('availability_count') or 0)>=units and p.get('group_adults')==[str(n)] and p.get('no_rooms')==[str(units)] and p.get('checkin')==[args['checkin_date']] and p.get('checkout')==[args['checkout_date']]
    proof={'method':'room_rate_inventory','queryGuests':n,'queryUnits':units,'checkin':args['checkin_date'],'checkout':args['checkout_date'],'rateOccupancy':occ,'capacity':room.get('max_occupancy'),'inventory':rate.get('availability_count'),'url':u,'queriedAt':query['queriedAt'],'roomName':room['name']}
    evidence[(u,query['queriedAt'])]=(valid,proof,uid('lodging_product',query['propertyId'],room['name'],block[0] if block else '',n,units,args['checkin_date'],args['checkout_date'],rate.get('currency'),rate.get('cancellation_type'),rate.get('meal_plan'),block[1] if len(block)>1 else ''))
 for q in hs:
  q['runId']=run_id;q['origin']='CWB';q['availabilityStatus']='unverified';q['availabilityVerified']=False;q['availabilityReason']='Preço observado não comprova alocação nem estoque da tarifa.'
  match=evidence.get((q.get('url'),q.get('queriedAt')))
  if match:
   valid,proof,product=match;q['productId']=product;q['availabilityEvidence']=proof
   if valid and q.get('amount') is not None:q['availabilityVerified']=True;q['availabilityStatus']='available';q['availabilityReason']='Tarifa retornada para ocupação/datas/unidade exatas com estoque positivo na consulta.';q['availabilityCheckedAt']=q['queriedAt']
 for q in ps:q.update({'runId':run_id,'origin':'CWB','availabilityStatus':'unverified','availabilityVerified':False,'availabilityReason':'Sem segmentos completos, bagagem e confirmação integral de assentos.'})
 for q in events:
  q['runId']=run_id;q['origin']='CWB';q['availabilityVerified']=False;q['productId']=uid('event_product',q.get('eventKey'),q.get('date'),q.get('sector'),q.get('ticketCategory'),q.get('currency'))
  avail=q.get('availability',{});text=str(avail).lower();q['availabilityStatus']='unavailable_category' if ('esgotado' in text or 'sold_out' in text or 'unavailable' in text) else 'unverified';q['availabilityScope']=avail.get('scope','night_not_verified') if isinstance(avail,dict) else 'night_not_verified'
 byid={q['id']:q for q in hs+ps+events}
 for o in observations:
  q=byid.get(o.get('quoteId'));o['runId']=run_id;o['origin']='CWB'
  if q:
   for k in ['availabilityStatus','availabilityVerified','availabilityEvidence','productId','availabilityScope','taxes','cancellation','prepayment','luggagePolicy','priceObservedAt','priceObservationStatus']:o[k]=q.get(k)
   o['conditions']={'cancellation':q.get('cancellation'),'prepayment':q.get('prepayment'),'taxes':q.get('taxes'),'bag':q.get('luggagePolicy')};o['roomName']=q.get('roomName');o['units']=q.get('units');o['category']=q.get('ticketCategory',q.get('roomName'));o['sector']=q.get('sector')
 return hs,ps,events,observations
