import {compatible,finite} from './core.js';
export function reservable(q,s,now=Date.now()){
 if(!q||!q.availabilityVerified||q.availabilityStatus!=='available'||!compatible(q,s))return false;
 const e=q.availabilityEvidence,at=Date.parse(q.availabilityCheckedAt||q.queriedAt||'');
 if(!e||!Number.isFinite(at)||now<at-60000||now-at>86400000)return false;
 return q.units===1&&e.method==='room_rate_inventory'&&e.queryGuests===s.n&&e.queryUnits===q.units&&e.checkin===s.checkin&&e.checkout===s.checkout&&e.rateOccupancy===s.n&&e.capacity>=s.n&&e.inventory>=q.units&&finite(q.amount);
}
export function availabilityState(q,s,now=Date.now()){
 if(q?.simulation||q?.status==='estimado')return 'estimate';
 if(reservable(q,s,now))return 'available';
 if(q?.availabilityStatus==='unavailable'||q?.availabilityStatus==='unavailable_category')return 'unavailable';
 if(q?.availabilityVerified||!compatible(q,s)||!q?.runId)return 'historical';
 return 'unverified';
}
export const availabilityLabels={available:'Disponibilidade verificada na consulta',unverified:'Disponibilidade não verificada',unavailable:'Indisponível no escopo consultado',historical:'Histórico / requer nova conferência',estimate:'Simulação manual',pending:'Informação pendente'};
export function eligibleRanking(o,s){return reservable(o.h,s)&&o.cost.projectionPP!==null&&!o.manual}
