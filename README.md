# ROTA27 V3 — pesquisa, viagens e experiências

Publicado em https://julyagoncalves21.github.io/Comparador-viagens/ . A aplicação continua estática e usa caminhos relativos. Portfólio e projeto antigo não são alterados.

## Pesquisa de 23/11/2026 (horário de Brasília)

Foram realizadas 78 buscas válidas de hospedagem (quatro grupos, duas unidades para5/6 e Recife/Olinda separados),48 consultas a quartos e56 buscas aéreas I/V para2/3/5/6 adultos. Os registros estão em `data/snapshots/2026-11-23-v3/`:

-1.311 observações de hospedagem: incluem preços exibidos, tarifas de quarto e48 consultas Airbnb sem total verificável.883 observações têm valor aplicável à ocupação consultada;111 tarifas de quarto tiveram o código de ocupação retornado compatível. Tarifas retornadas para outra ocupação têm valor observado separado e não entram no orçamento.
-656 observações de transporte:560 ofertas aéreas e96 consultas rodoviárias por sentido. Ônibus sem total verificável continua pendente.
-52 registros de transfer e328 registros de pesquisa terrestre/custos locais (incluem ônibus, Airbnb e referências de transporte). São consultas para fevereiro com valores finais pendentes; referências atuais ficam em campo separado.
-37 eventos/experiências nos12 destinos, incluindo arquibancadas/cadeiras/frisas/camarotes do Rio, Série Ouro, abadás/camarotes de Salvador, circuitos gratuitos, atrações turísticas regulares e programação não divulgada. Frisa de seis lugares é pacote inteiro, não preço de assento.
-3.999 snapshots normalizados, incluindo o histórico anterior. Datas e horas UTC são preservadas. HTTP200 não significa estoque, preço final ou disponibilidade.

As taxas, pagamento, bagagem e parte da programação ainda precisam de conferência. Nenhuma viagem integral foi declarada confirmada. Preços turísticos atuais de2026 podem ser usados somente como referência simulada, com rótulo próprio; não são ingressos confirmados do Carnaval2027. Shows fora das datas permanecem separados.

## Interface e cálculos

As sete telas seguem o HTML aprovado: Visão geral, Explorar destinos, Hospedagens, Montar viagem, Comparar, Histórico e Dados/fontes. CSS e ilustrações de destinos foram extraídos do conceito; nenhum preço demonstrativo foi importado. Ilustrações não são fotos de imóveis. Sem permissão de imagem confirmada, hospedagens usam placeholder identificado.

DM Sans e Instrument Serif são hospedadas em `assets/fonts/`, com as respectivas licenças SIL Open Font License. Origem dos arquivos: repositório oficial google/fonts.

Hospedagem, tarifa, passagem e transfer são escolhas independentes. Experiências oficiais ou manuais usam preço unitário × quantidade, somam ao grupo e dividem pelo grupo uma única vez. A contingência é aplicada uma vez ao acréscimo. Moeda estrangeira sem conversão documentada, data incompatível, preço ausente e taxas desconhecidas ficam pendentes. O usuário pode comprar apenas alguns ingressos; quantidade não é presumida após edição.

Favoritos, cotações manuais, preferências e experiências são locais ao navegador. A exportação JSON inclui as bases completas e os snapshots, a importação valida cotações/experiências locais. O limite é50MB. A versão não promete sincronização automática nem consulta de preços em tempo real.

## Atualização reproduzível e preservação

1. Faça consultas reais para as datas/ocupações desejadas. Salve as respostas estruturadas e evidências nos arquivos de entrada documentados em `scripts/import_research_v3.py`. Não use o HTML conceitual como fonte de valores.
2. Execute `python scripts/import_research_v3.py --input-dir PASTA --batch NOVO_ID`. Use um identificador novo por rodada. O importador recusa alterar um snapshot existente com conteúdo diferente e cria automaticamente os arquivos por grupo.
3. Execute `python scripts/validate_snapshots.py` e os testes. Revise preços, URLs, país/identidade, ocupação dos códigos de tarifa, condições, taxas e pendências. Nenhum valor anterior é sobrescrito.
4. Faça commit/push apenas neste repositório e aguarde o workflow Pages. Confirme o site público.

Entradas: `v3_hospedagens_completas_raw.json`, `v3_quartos_raw.json`, `v3_voos_raw.json`, `v3_eventos_pesquisa.json`, `v3_terrestre_pesquisa.json`. São respostas de pesquisa, não exemplos a preencher com valores estimados. Os arquivos brutos locais não são publicados. Caminhos locais são removidos sem alterar URLs HTTPS.

`snapshot-index.json` referencia cada rodada. Hospedagens e transportes são carregados por grupo, com índices reutilizados; observações, fontes, eventos e bases completas são carregados por demanda. Histórico só calcula variação com condições conhecidas e equivalentes. Condições ausentes nunca são consideradas iguais; no estado atual não há pares integralmente comprovados para desenhar uma tendência, embora todas as observações permaneçam visíveis.

Validação: `node --test tests/core.test.mjs tests/v3.test.mjs` e `python tests/v3-smoke.py --url URL`. A opção `--production` faz uma checagem reduzida da publicação. Os testes V1/V2 anteriores permanecem arquivados para referência; seus seletores de layout não descrevem as sete telas novas.

---

Documentação V2 preservada abaixo:

# ROTA27 V2 — Comparador de viagens

Aplicação independente. A versão anterior e o portfólio não são alterados.

## Evolução V2

Resultados agrupados por propriedade e ocupação, com escolha independente de tarifa de quarto e passagem no modal. Todas as cotações originais continuam nas bases; agrupamento visual não exclui registros. Links originais são preservados. Fallback para a URL da propriedade somente quando a referência de identidade do registro corresponde à propriedade. Fotos não foram copiadas sem licença: os cards usam placeholder identificado. Mapas abrem coordenadas presentes na pesquisa, sem calcular distâncias em linha reta.

As bases completas permanecem em `data/`. Histórico, eventos, fontes e detalhes são carregados ao abrir suas telas. Cópias `*-runtime.json` removem apenas o campo redundante `legacy`; não removem entidades nem preços. Índices reutilizáveis e uma opção ativa por propriedade evitam reconstruir o produto cartesiano de hospedagens e voos. A exportação completa carrega os dados originais antes de gerar o arquivo.

`data/link-audit.json` registra resultados HTTP, redirecionamentos, caminhos genéricos e pendências, sem substituir anúncios. HTTP 200 não confirma disponibilidade. Datas e ocupações incompatíveis continuam bloqueando valores no cálculo.

Para atualizar: execute o importador original preservando os dados de 2 adultos e depois `python scripts/build_runtime.py`. Teste, faça commit e push. O workflow `.github/workflows/pages.yml` publica a raiz deste repositório. A aplicação usa caminhos relativos. Pages pode precisar ser habilitado pelo proprietário caso as permissões do workflow não permitam habilitação automática.

O cadastro manual e as preferências são locais ao navegador. A chave V2 não modifica as preferências da versão antiga. É possível importar as cotações manuais exportadas na V1.

`data/projects.json` identifica o primeiro projeto salvo: Carnaval 2027, origem Curitiba. Outros projetos/origens ainda dependem de uma base própria de cotações; não se reutilizam preços de Curitiba para outra origem.

Testes V2: `node --test tests/core.test.mjs`, `python tests/v2-smoke.py` e `python tests/smoke.py --url URL_LOCAL_OU_PUBLICA`.

Auditoria HTTP: 587 caminhos, 4.601 refer?ncias preservadas; 550 HTTP v?lidos, 37 pendentes e zero respostas 404/410 nesta checagem. Confira `data/link-audit.json`. Resposta HTTP n?o comprova tarifa ou disponibilidade.

---

Documentação preservada da versão anterior:

# ROTA27 — Carnaval 2027

Aplicação estática em `/rota27-comparador-viagens/`, sem compilação ou serviços externos em tempo de execução. Mantém o HTML, CSS e o layout de resultados do protótipo aprovado; os cálculos foram separados em módulos testáveis. O workflow Pages existente publica esta pasta junto ao portfólio, sem alterações fora dela.

## Uso

Escolha 2, 3, 5 ou 6 viajantes, destino, datas e modal. Em **Mais filtros**, refine bairro, tipo, privacidade documentada, banheiro, avaliação, quartos, metrô, faixa de custo e estado da cotação. **Ajustar gastos** controla despesas por pessoa, despesas compartilhadas, contingência e pesos do ranking. Valores vazios são pendências, não serviços gratuitos. O orçamento começa sem teto.

Selecione até três alternativas para comparar. O comparador preserva as datas e o grupo da seleção. Custos diários e pesos continuam editáveis. Todas as páginas usam a base normalizada, com fontes acessíveis. A faixa econômico/intermediário/caro usa terços das projeções parciais para o tamanho do grupo; não indica um limite de gasto universal.

**Custo conhecido** é o valor exibido pela fonte para a ocupação/data pesquisada, não uma garantia de reserva nem validação integral. A **projeção parcial** só aparece quando hospedagem e passagem estão precificadas no cenário. Campos desconhecidos continuam listados. Estimativas, contingência e simulações locais são separadas do custo observado. Mudanças de datas não recalculam tarifas: exigem nova pesquisa.

O ranking não cria notas de localização, limpeza ou tempo ausentes. Mostra a cobertura dos critérios e deixa pesos sem evidência sem pontuação. A evidência de limpeza datada não substitui a leitura da avaliação. Notas antigas de localização da planilha foram conservadas nos registros de pesquisa, mas não usadas como notas factuais do ranking.

## Base migrada e pesquisa nova

`data/meta.json` registra contagens, SHA-256 da planilha, origem e atualização. Foram preservadas 1.019 observações de hospedagem, 613 transportes e 2.875 combinações de 3/5/6 pessoas, além de fontes, rotas, histórico, documentos, eventos, detalhes e parâmetros das 25 abas. Abas derivadas continuam como registros de pesquisa; não viram produtos duplicados. A ocorrência de identidade errada na Holanda fica apenas no histórico rejeitado.

Pesquisa inédita em 23/11/2026 para **2 adultos**, 05–10/02/2027:

- 12 buscas Booking; 120 resultados de hospedagem com preços exibidos para a ocupação/datas solicitadas.
- 12 consultas adicionais a quartos; 77 tarifas retornadas de quartos com capacidade informada de pelo menos 2. Podem existir quartos diferentes no mesmo imóvel. Capacidade máxima não prova o regime de ocupação do checkout: confirmar categoria, alocação, camas, cobrança final e taxas.
- 12 anúncios reais Airbnb, com descrição/capacidade consultadas; preço final e disponibilidade para as datas não verificáveis, mantidos pendentes.
- 14 buscas aéreas, incluindo GIG/SDU, CFB e JJD/FOR; 140 opções I/V com preço exibido do grupo de dois. Não há confirmação integral de bagagem, dois itinerários ou cobrança final. Horários resumidos não permitem calcular duração ou dias aproveitáveis.
- 68 acessos adicionais efetivos a Airbnb, Google Flights, Skyscanner, LATAM e ClickBus. Páginas genéricas, bloqueios e conteúdo dinâmico não foram convertidos em cotações. Nenhuma tarifa final dessas páginas foi validada. Mais 12 fontes de transfer e transporte local foram consultadas; nove responderam HTTP 200. O serviço regular desde hotel em Fortaleza tem referência atual de R$400 I/V por pessoa, sem confirmar fevereiro, acesso desde FOR ou serviço desde JJD. Ônibus: consultas de ida/volta, sem preço 2027 validado.

Todos os destinos têm preços observados para 2 adultos. **Nenhuma viagem integral está validada**, em qualquer grupo. Tarifas podem mudar ou desaparecer. Eventos confirmados fora da viagem, especialmente CasaBloco de janeiro, permanecem identificados fora de 05–10/02. Camarote não entra como despesa obrigatória. Gigóia permanece acesso por barco; Parque Olímpico não é Gigóia.

## Atualizar as cotações

1. Atualize a planilha, mantendo os cabeçalhos e os links reais das células. Registre datas, grupo, unidades e condições exatas. O importador não pesquisa preços.
2. Com Python 3.10+ e `openpyxl` instalados, execute na pasta do projeto:

   ```powershell
   python scripts/import_workbook.py "CAMINHO/DA/PLANILHA.xlsx" --research-dir "PASTA_DAS_PESQUISAS" --out data
   ```

   A pasta de pesquisas pode conter `rota27_research_2_hotels.json`, `rota27_research_2_rooms.json`, `rota27_research_2_flights.json`, `rota27_airbnb2.json` `rota27_research_2_web.json` e `rota27_research_2_transfers.json`. São respostas reais das consultas, não arquivos de exemplo. **Para reimportar a planilha sem esses arquivos e preservar a pesquisa já publicada de 2 pessoas, use `--preserve-existing-two`**. Não copie a planilha nem arquivos brutos pessoais para o site.

3. Revise `data/meta.json`, preços, vínculos, ocupações e pendências. Execute os testes. Faça commit/push somente de `carnaval-2027/`. Aguarde o workflow `Deploy GitHub Pages` e confira a URL final.

O cadastro manual salva **somente neste navegador**, sempre como simulação. Exporte a base JSON para fazer backup. A interface importa a coleção `manual` de um JSON ROTA27 v1 (até 1.000 registros), validando grupo, datas, preços e URLs HTTPS. Não altera a base pública nem sincroniza dispositivos. Para publicar cotações manuais, revise as informações e integre-as à planilha/base, depois faça novo commit. Os arquivos públicos não contêm a planilha, caminhos locais, conversas privadas ou credenciais.

Histórico de variações exige mesma propriedade, ocupação, unidades, datas, moeda, quarto e condições conhecidas. Quando esses dados faltam, a aplicação lista observações sem fabricar uma curva de preços. Câmbio documental da planilha é referência PTAX com fonte/data: preços já exibidos em BRL não são convertidos novamente. O ledger deixa moedas estrangeiras pendentes até existir conversão explicitamente documentada.

## Desenvolvimento e testes

Sirva a raiz do repositório: `python -m http.server 8765 --bind 127.0.0.1`, abra `http://127.0.0.1:8765/rota27-comparador-viagens/`.

`node --test carnaval-2027/tests/core.test.mjs` testa datas, divisão de custos, contingência, valores ausentes, grupo/datas incompatíveis, moedas, barco/metrô, ranking, histórico, importação e preservação. `python carnaval-2027/tests/smoke.py --url http://127.0.0.1:8765/rota27-comparador-viagens/` executa o smoke test com Playwright instalado. Os resultados documentados estão em `data/validation.json`.

Limitações: sem backend, reserva, API de cotação automática ou atualização agendada; disponibilidade não é garantida. Os custos de transfer exato, bagagem, impostos adicionais e horários de ida/volta ainda exigem conferência manual. Alimentação e transporte local são hipóteses editáveis, não pesquisa de preços de refeições.
