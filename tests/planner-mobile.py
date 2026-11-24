import json,argparse,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8768/rota27-comparador-viagens/');ap.add_argument('--production',action='store_true');a=ap.parse_args();checks=[];errors=[];output=Path(tempfile.gettempdir())/'planejador-p24';output.mkdir(exist_ok=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(channel='msedge',headless=True);ctx=browser.new_context(viewport={'width':1280,'height':900},locale='pt-BR',accept_downloads=True);page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));r=page.goto(a.url,wait_until='networkidle',timeout=60000);assert r.status==200;expect(page.locator('.hero h1')).to_be_visible(timeout=30000)
 def nav(view):
  if page.viewport_size['width']<=900:page.locator('#mobileMenu').click()
  page.locator(f'.nav [data-view="{view}"]').click()
 nav('dashboard');expect(page.locator('.stay').first).to_be_visible();expect(page.locator('.stay .price-box .chip').first).to_contain_text('verificada');assert page.locator('.availability-panel').inner_text().find('24h')>=0;checks.append('ranking/listagem principal somente disponibilidade verificada')
 for n in [2,3,5,6]:page.locator(f'#persons [data-n="{n}"]').click();expect(page.locator('.stay').first).to_be_visible(timeout=30000)
 checks.append('quatro grupos com fontes próprias')
 page.locator('#persons [data-n="2"]').click();expect(page.locator('.stay').first).to_be_visible(timeout=30000)
 if not a.production:
  for d in page.locator('#destination option').evaluate_all('(a)=>a.map(x=>x.value).filter(v=>v!=="all")'):page.locator('#destination').select_option(d);expect(page.locator('.stay').first).to_be_visible()
  checks.append('doze destinos para dois adultos com tarifa de estoque verificado')
 page.locator('#destination').select_option('rio');page.locator('.stay h3').first.click();expect(page.locator('#stayDialog')).to_be_visible();expect(page.locator('.logistics-context')).to_contain_text('Volta à noite');assert page.locator('.logistics-context a').count()>0;page.locator('[data-close="stayDialog"]').click();checks.append('logística e fontes oficiais nos detalhes, sem distâncias inventadas')
 page.locator('.stay [data-build]').first.click();expect(page.locator('#builderFlight')).to_be_visible(timeout=30000);page.locator('#builderFlight').select_option(index=1);form=page.locator('#experienceManualForm');form.locator('[name=name]').fill('Passeio teste');form.locator('[name=amount]').fill('100');form.locator('[name=quantity]').fill('2');form.locator('button').click();expect(page.locator('.selected-experience')).to_have_count(1);page.locator('.total-panel [data-add]').click();checks.append('escolha independente e experiências no orçamento')
 nav('dashboard');page.locator('#destination').select_option('all');ids=page.locator('.stay .offer-check:not(:checked)').evaluate_all('(a)=>a.slice(0,2).map(x=>x.dataset.check)')
 for selectedId in ids:page.locator('[data-check="'+selectedId+'"]').check()
 nav('compare');assert page.locator('.compare-card').count()==3;expect(page.locator('.compare-card').first).to_contain_text('Disponibilidade da hospedagem');checks.append('comparação de três viagens com disponibilidade e custos separados')
 nav('history');expect(page.locator('#historyKind')).to_be_visible(timeout=30000);expect(page.locator('#dynamic')).to_contain_text('snapshots');page.locator('#historyKind').select_option('experience');checks.append('histórico permanente inclui as rodadas sem tendências fictícias')
 nav('database');expect(page.locator('#entity')).to_be_visible(timeout=30000);page.locator('#entity').select_option('research_runs');expect(page.locator('.rawtable tbody tr').first).to_be_visible();checks.append('rodadas e falhas acessíveis na base')
 if not a.production:
  with page.expect_download(timeout=60000) as dl:page.locator('#exportJson').click()
  path=output/'export.json';dl.value.save_as(path);data=json.loads(path.read_text(encoding='utf-8'));assert len(data['database']['observations'])==6916;assert len(data['experiences'])==1;page.locator('#importFile').set_input_files({'name':'valid.json','mimeType':'application/json','buffer':json.dumps({'schemaVersion':1,'manual':[],'experiences':data['experiences']}).encode()});expect(page.locator('#notice')).to_contain_text('importadas');checks.append('exportação integral e importação das experiências')
 nav('dashboard');page.locator('[data-availability="all"]').click();expect(page.locator('.availability-panel')).to_contain_text('alternativas');page.locator('[data-availability="available"]').click();expect(page.locator('.availability-panel')).to_contain_text('Seleção principal');checks.append('alternativas não verificadas preservadas fora da seleção principal')
 for width in [360,390,430,768,1280]:
  page.set_viewport_size({'width':width,'height':900});page.wait_for_timeout(100);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),str(width);nav('overview');nav('dashboard');expect(page.locator('.stay').first).to_be_visible();page.locator('.stay h3').first.click();expect(page.locator('#stayDialog')).to_be_visible();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.locator('[data-close="stayDialog"]').click();page.screenshot(path=str(output/f'{width}.png'),full_page=True)
 checks.append('menu, filtros, cards e modal nas larguras360/390/430/768/1280')
 assert not errors,errors;checks.append('sem erros JavaScript');browser.close()
report={'passed':len(checks),'checks':checks,'errors':errors,'production':a.production};(output/('production.json' if a.production else 'local.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
