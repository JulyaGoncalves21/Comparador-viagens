import json,argparse,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8766/rota27-comparador-viagens/');a=ap.parse_args();checks=[]
with sync_playwright() as p:
 b=p.chromium.launch(channel='msedge',headless=True);context=b.new_context(viewport={'width':1440,'height':1000},accept_downloads=True);page=context.new_page();requests=[];errors=[];page.on('request',lambda r:requests.append(r.url));page.on('pageerror',lambda e:errors.append(str(e)));page.goto(a.url,wait_until='networkidle');expect(page.locator('.stay-card').first).to_be_visible(timeout=30000);assert not any('/sources.json' in u or '/history.json' in u or '/combinations.json' in u for u in requests);checks.append('lazy loading: full historical/source/combinations bases excluded initially')
 names=page.locator('.stay-card h3').all_text_contents();assert len(names)==len(set(names));checks.append('one card per property, no transport Cartesian product')
 for n in [2,3,5,6]:page.locator(f'[data-n="{n}"]').click();assert page.locator('.stay-card').count()>0
 page.locator('[data-n="2"]').click();checks.append('four groups preserved')
 for d in page.locator('#destination option').evaluate_all('(els)=>els.map(e=>e.value).filter(v=>v!=="all")'):
  page.locator('#destination').select_option(d);assert page.locator('.stay-card').count()>0
 page.locator('#destination').select_option('all');checks.append('all twelve destinations populated')
 links=page.locator('.card-links a').evaluate_all('(els)=>els.map(e=>({url:e.href,target:e.target,rel:e.rel}))');assert links and all(x['url'].startswith('https://') and x['target']=='_blank' and 'noopener' in x['rel'] for x in links);assert any('/hotel/' in x['url'] for x in links);checks.append('original property and transport links open safely')
 page.locator('.stay-card h3').first.click();expect(page.locator('#stayDialog')).to_be_visible();before=page.locator('#stayFlight').input_value();opts=page.locator('#stayFlight option').evaluate_all('(els)=>els.map(e=>e.value)');assert len(opts)>1;page.locator('#stayFlight').select_option(opts[1]);expect(page.locator('#stayFlight')).to_have_value(opts[1]);checks.append('modal supports independent flight selection and recalculates costs')
 page.locator('#stayDialog [data-add]').click();expect(page.locator('#navCount')).to_have_text('1');page.locator('[data-close="stayDialog"]').click();page.locator('.stay-card .offer-check').nth(1).check();page.locator('.stay-card .offer-check').nth(2).check();page.locator('.nav [data-view="compare"]').click();assert page.locator('.compare-card').count()==3;checks.append('comparison keeps three independent selections')
 for v in ['history','pending','database','destinations']:
  page.locator(f'.nav [data-view="{v}"]').click();expect(page.locator('#dynamic')).not_to_contain_text('Carregando esta base…')
 checks.append('historical and research pages load on demand')
 page.locator('.nav [data-view="dashboard"]').click();page.locator('#checkout').fill('2027-02-11');page.locator('#checkout').dispatch_event('change');expect(page.locator('#dateWarning')).to_be_visible();assert page.locator('.stay-card .offer-price b').first.inner_text()=='—';checks.append('new dates do not validate old fares')
 page.locator('#resetBtn').click();page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1');page.locator('.stay-card h3').first.click();expect(page.locator('#stayDialog')).to_be_visible();page.locator('[data-close="stayDialog"]').click();checks.append('mobile cards and modal without body overflow')
 assert not errors,errors;checks.append('no JavaScript runtime errors');context.close();b.close()
root=Path(__file__).resolve().parents[1];result={'passed':len(checks),'checks':checks,'runtimeErrors':errors};(root/'data/v2-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
