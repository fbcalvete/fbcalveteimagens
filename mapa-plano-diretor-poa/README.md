# Mapa comparativo dos Planos Diretores de Porto Alegre

Comparação, terreno a terreno, entre o **plano antigo (PDDUA, LC 434/99)** e o **plano novo
(PDUS + LUOS, sancionados em 14/07/2026)**. O pacote tem:

- um mapa HTML que roda sozinho;
- os GIS de cada plano em arquivos independentes;
- um GIS da sobreposição, com o **ganho de área privativa** de cada área: (CA básico × 0,8) ÷ (IA × 1,2) − 1.

Dados extraídos em **29/10/2026** dos serviços oficiais da Prefeitura.

## 1. Abrir o mapa

Abra `mapa_planos_diretores_poa.html` com duplo clique (Chrome, Edge, Firefox ou Safari).

- **Funciona offline.** Geometria, base de ruas oficial, numeração predial e a biblioteca de mapa estão dentro do arquivo (6,4 MB).
- **Sem satélite.** O fundo é a malha de logradouros da Prefeitura. Com internet, dá para ligar por baixo um mapa de ruas da CARTO.

### Como consultar um terreno

1. Digite o endereço na busca (`Av. Ipiranga 1200`, `Padre Chagas 300`, `Dr. Timóteo 500`) ou uma coordenada (`-30.035, -51.22`). Também dá para clicar direto no mapa.
2. O painel mostra, para aquele ponto:
   - **Plano antigo:**
     - zona de uso, MZ/UEU/subunidade e código D·A·I·V;
     - IA básico e máximo, área privativa potencial (IA × 1,2), solo criado/TPC, quota ideal;
     - altura máxima, altura na divisa e na base, taxa de ocupação.
   - **Plano novo:**
     - ZOT e tipo de ocupação;
     - CA básico e máximo, área privativa potencial (CA × 0,8), altura máxima, lote mínimo, permeabilidade, recuo de jardim;
     - caracterização e finalidade da zona;
     - a ZOT que o ponto tinha no projeto pós-audiência, quando mudou.
   - **Ganho de área privativa** com o potencial básico, com a conta aberta, por exemplo `(CA 2,0 × 0,8) ÷ (IA 1,0 × 1,2) − 1 = +33%`. Mostra também o ganho com o potencial máximo e a diferença de altura.
3. **Copiar resumo** gera um texto pronto para colar na planilha de estudo.

### Camadas e cores

| Controle | O que faz |
|---|---|
| Plano antigo / Plano novo / Dinâmica | Liga e desliga cada mancha. Analise separado ou em conjunto. |
| Contorno | Mostra só o limite das zonas, para ver um plano sobre o outro. |
| Barra de opacidade | Transparência de cada camada. |
| Cores dos planos | Plano antigo pelo **IA básico**, plano novo pelo **CA básico**. Os dois usam a mesma escala de área privativa por m² de terreno, então a mesma cor indica a mesma área privativa. Exemplo: IA 1,3 (1,56) e CA 2,0 (1,60). |
| Cores da dinâmica | Ganho de área privativa com as **cores da tabela IA × CA do estudo**, do vermelho (−44% ou menos) ao verde-escuro (+140% ou mais). |
| Eficiência de projeto | Campos editáveis (padrão 1,2 e 0,8). Ao mudar, o mapa, a matriz e a consulta são recalculados. |
| Matriz IA × CA | Mostra todas as combinações reais, com o ganho e a área. Clique numa célula para ver no mapa só aquela combinação. |
| Passar o mouse | Mostra o **ganho percentual**, o **IA anterior** e o **CA futuro** sob o cursor. |

A busca por endereço segue esta ordem:

1. Procura o número no **cadastro predial da Prefeitura** (204 mil números de lote).
2. Se não achar, estima a posição entre os lotes vizinhos cadastrados do mesmo lado da rua.
3. Se não houver vizinhos, interpola na faixa de numeração do trecho.

O painel informa qual dos três casos ocorreu.

## 2. Arquivos

| Arquivo | Conteúdo |
|---|---|
| `mapa_planos_diretores_poa.html` | Mapa interativo independente. |
| `dados/pddua_antigo_zonas.gpkg` / `.geojson` | **GIS do plano antigo:** 1.548 subunidades do PDDUA com o regime urbanístico decodificado. |
| `dados/pdus_novo_zonas.gpkg` / `.geojson` | **GIS do plano novo:** 8.414 polígonos de ZOT da LUOS sancionada, com o regime de cada ZOT. |
| `dados/dinamica_sobreposicao.gpkg` / `.geojson` | **GIS sobreposto:** 12.516 peças da interseção antigo × novo, com atributos dos dois planos, deltas e classes. |
| `dados/planos_diretores_poa.kmz` | As 3 camadas para o **Google Earth**, com cores por zona e ficha em cada polígono. |
| `dados/tabelas/*.csv` | Anexos 5.1, 6 e 7.1 do PDDUA, regime por ZOT, **matriz IA × CA básico** (`matriz_ia_ca_basico.csv`), **dinâmica por bairro** e **IA das leis específicas** (`ia_leis_especificas.csv`). |
| `dados/fontes_originais/` | Cópia comprimida dos dados brutos baixados, com URLs e horário (`fontes.json`), e o link de cada lei e decreto consultado (`leis_especificas_fontes.csv`). |
| `scripts/` | Download, processamento e geração do HTML/KMZ (reprodutível). `scripts/ia_leis_especificas.csv` é a tabela curada à mão, lida norma a norma. |

Os GPKG e GeoJSON estão em WGS 84 (EPSG:4326). Abrem no QGIS, ArcGIS, Global Mapper e geojson.io.

### Campos principais

**Plano antigo** (`pddua_antigo_zonas`):

| Campo | Significado |
|---|---|
| `mz`, `ueu`, `subunid`, `cod_subun` | Macrozona, UEU e subunidade. |
| `dens_cod`, `ativ_cod`, `ia_cod`, `vol_cod` | Códigos D·A·I·V do regime urbanístico. |
| `zona_uso` | Zona de uso (Anexo 5.1). |
| `ia_bas`, `ia_max` | Índice de aproveitamento básico e máximo: do Anexo 6 ou, nos códigos não numéricos, da lei ou decreto específico. |
| `ia_fonte` | `Anexo 6 (código do IA)`, `Lei ou decreto específico` ou `Sem IA numérico (norma verificada)`. |
| `ia_lei`, `ia_lei_obs` | Norma e dispositivo de onde saiu o IA (ou que foi verificada e não fixa número), com observação. |
| `solo_cria`, `tpc`, `quota` | Solo criado, TPC e quota ideal. |
| `alt_max`, `alt_divisa`, `alt_base`, `tx_ocup` | Volumetria (Anexo 7.1). |
| `caeq_bas`, `caeq_max` | IA × 1,5, comparável ao CA novo. |

**Plano novo** (`pdus_novo_zonas`):

| Campo | Significado |
|---|---|
| `zot` | Zona de Ordenamento Territorial. |
| `ocupacao` | Tipo de ocupação (Intensiva, Equilíbrio etc.). |
| `ca_bas`, `ca_max` | CA numérico. |
| `ca_bas_txt`, `ca_max_txt` | CA como está na base oficial. |
| `alt_max` | Altura máxima. |
| `lote_min`, `mod_frac`, `perm_min`, `perm_max`, `recuo_jard` | Parcelamento, permeabilidade e recuo de jardim. |
| `zot_projeto` | ZOT na versão pós-audiência. |
| `fonte` | De qual base veio o polígono. |

**Dinâmica** (`dinamica_sobreposicao`):

| Campo | Significado |
|---|---|
| `priv_ant`, `priv_novo` | Área privativa potencial por m² de terreno: IA × 1,2 e CA × 0,8. |
| `ganho_bas` | Ganho de área privativa com o potencial básico, em %: (CA × 0,8) ÷ (IA × 1,2) − 1. Na Zona Rural é 0. |
| `base_calc` | `LUOS (CA)` ou `PDDUA (IA)` (Zona Rural). |
| `ia_fonte`, `ia_lei` | De onde veio o IA antigo e a norma (ver plano antigo). |
| `regime_ref`, `ia_teto` | Observação do DMWeb sobre o regime e o teto do Anexo 6 (códigos 23 e 25). |
| `ganho_max` | O mesmo cálculo com IA máximo e CA máximo. |
| `d_ca_bas`, `d_ca_max` | CA novo − CA equivalente antigo. |
| `d_alt` | Altura nova − altura antiga (m). |
| `r_ca_max` | Razão novo/antigo do CA máximo. |
| `din_cabas`, `din_camax`, `din_alt` | Classes Ampliou / Manteve / Reduziu / Sem comparação. |
| `id_ant`, `id_novo` | Chaves para as duas camadas de origem. |

## 3. Fontes

| Camada | Serviço oficial |
|---|---|
| PDDUA: subunidades com D·A·I·V | `mapaspoa-prod-2020.procempa.com.br/.../SMAMS_DM/TM_POA_SMAMS_Plano_Diretor/MapServer/16` (o mesmo serviço que alimenta o **DMWeb**) |
| PDDUA: Anexos 5.1, 6 e 7.1 | `gis-smamus.portoalegre.rs.gov.br/.../Hosted/PDDUA_ATVS_ANEXO_5_1`, `pddua_ia_anexo_6` e `pddua_vol_anexo_7_1` |
| LUOS sancionada: mapa das ZOTs, com emendas e polígonos vetados | ArcGIS Online da SMAMUS, item "LUOS Zoneamento POA" (`services3.arcgis.com/ArYIEKBXSSNP3WQG/.../zoneamento_min`, atualizado em 01/09/2026) |
| PDUS Anexo 5: regime por ZOT e quarteirões | `gis-smamus.portoalegre.rs.gov.br/.../Hosted/pdus_anexo5_zonasdeocupacao` (atualizado em 29/09/2026) |
| Logradouros, números prediais e limite municipal | Mesmo serviço do DMWeb (camadas 8, 3, 5 e 18) |
| Observações das subunidades (norma do regime) | Tabelas do DMWeb 2.0 no portal da SMAMUS (`dm_obs_tipo1`, `tipo2`, `tipo10`, `geral`) |
| Leis e decretos específicos (IA das áreas sem código numérico) | Legislação Municipal de Porto Alegre (SAPL, `legislacao.portoalegre.rs.gov.br`, API `/api/norma/normajuridica`) e Diário Oficial (DOPA, `dopaonlineupload.procempa.com.br`) |

O link do ArcGIS Experience indicado no pedido ("Pós Audiência – Zoneamento – PDUS") usa a camada `INTERSECT_PLAN_08_09_25_v2`, de set/2025. Ela é **anterior** às emendas da Câmara e aos vetos. Por isso a comparação usa o mapa da LUOS sancionada. A zona da versão pós-audiência fica registrada em `zot_projeto` e aparece na consulta quando difere.

## 4. Método

- **Área privativa potencial.** A base de cálculo muda entre os planos. O IA do PDDUA conta só áreas adensáveis; o CA novo soma adensáveis e não adensáveis. Por isso cada coeficiente leva uma eficiência de projeto:
  - plano antigo: `IA × 1,2`;
  - plano novo: `CA × 0,8`;
  - `ganho = (CA × 0,8) ÷ (IA × 1,2) − 1`.
- **Equivalência com a regra oficial.** 1,2 ÷ 0,8 = 1,5, a mesma equivalência que a SMAMUS usa no comparativo oficial (`CA equivalente = IA × 1,5`, campos `ia_b_atual` e `ia_m_atual` da base municipal). Os campos `caeq_*` e `d_ca_*` seguem essa regra.
- **Classes.** Diferenças de até ±0,05 no CA ou ±0,5 m na altura contam como **Manteve**.
- **CA máximo sem acréscimo.** Quando o CA máximo novo é "Não se aplica" ou "Ajuste/TDC", ele é tratado como igual ao básico.
- **Regime por ZOT.** Vem do Anexo 5, apenas dos quarteirões em que a zona antes e depois das emendas é a mesma. Nas linhas alteradas por emenda, a base oficial ainda traz o regime da zona anterior.
- **Emendas de CA básico aplicadas.** A base GIS ainda não as incorporou; ambas foram aprovadas em 13/05/2026:
  - **Emenda 91:** CA básico 3,0 nas ZOT 08.3-A, 08.3-B, 08.3-C, 12 e 13, mantidos os demais parâmetros;
  - **Subemenda 1 à Emenda 93:** CA básico 3,6 no Bom Fim e na Cidade Baixa (ZOT 08.3-D).

  O valor original da base fica em `ca_bas_gis` e a origem em `fonte_ca_bas`. Para mudar, edite `EMENDAS_CA_BAS` em `scripts/build_gis.py`.
- **Zona Rural.** A LUOS (LC 1.076/2026, art. 22) diz que a Zona Rural não é ZOT e segue lei própria. A LC 775/15 (art. 5º, §1º) mantém nela o regime do PDDUA da subunidade (Área de Produção Primária, IA 0,1). Por isso o "CA" rural é o próprio IA do PDDUA, com a mesma base de cálculo e eficiência 1,2 nos dois lados: ganho 0%.
- **IA não numérico (códigos 23, 25, 39, 41 e 999).** O IA foi lido na lei ou decreto específico de cada área (seção 5, "IA das leis específicas"). A norma de partida vem das observações da subunidade no DMWeb 2.0 (`dm_obs_tipo2`, campo `regime_ref`). Depois foi conferida no texto integral do SAPL/DOPA e na busca de decretos posteriores pela ementa. O resultado está em `scripts/ia_leis_especificas.csv`, com norma, artigo e observação de cada subunidade. Quando a norma vale só para parte de uma subunidade, a chave leva o polígono (`MZ-UEU-SUB@id_ant`). Sem máximo na norma, o IA máximo é igual ao básico (sem solo criado). Nos códigos 23 e 25 que continuam sem número, o Anexo 6 fixa teto de IA 2,5 (`ia_teto`).
- **Áreas fora do mapa da LUOS.** Onde o mapa sancionado não cobre (áreas ESPECIAIS, alguns quarteirões), a zona vem do Anexo 5. O campo `fonte` indica esses polígonos.
- **Sobreposição.** Interseção geométrica em SIRGAS 2000 / UTM 22S (EPSG:31982). Peças menores que 10 m² foram descartadas.

## 5. Leitura rápida dos resultados

### Combinações de IA × CA básico que existem na cidade

**IA do plano antigo:**

- **Anexo 6:** 0,1 · 0,2 · 0,5 · 0,65 · 1,0 · 1,3 · 1,6 · 1,9 · 2,4.
- **Só em leis específicas:**
  - 0,05 e 0,25 (Arado Velho, LC 935/22);
  - 0,8 (LC 324/94);
  - 3,0 (Hospitais Conceição e Mãe de Deus, LC 833/18 e LC 764/15).

**CA básico do plano novo:**

| CA | Onde |
|---|---|
| 0,3 | ZOT 15 e 16 |
| 0,5 | ZOT 14 |
| 1,15 | ZOT 08.1-F |
| 1,5 | ZOT 01 |
| 2,0 | ZOT 02, 03, 04 e 09 |
| 2,4 | ZOT 05, 06, 07, 08, 10 e 11 |
| **3,0** | ZOT 08.3-A/B/C, 12 e 13, pela Emenda 91 |
| 3,6 | ZOT 08.1, 08.2 e **08.3-D**, esta pela Subemenda 1 à Emenda 93 |
| Zona Rural | Mantém o IA do PDDUA (LC 775/15) |

Ganho de área privativa com o potencial básico e área de quarteirões em cada combinação, em km²:

| IA \ CA | 0,3 | 0,5 | 1,15 | 1,5 | 2,0 | 2,4 | 3,0 | 3,6 | Zona Rural |
|---|---|---|---|---|---|---|---|---|---|
| **0,05** | +300% · 0,6 | | | | | | | | |
| **0,1** | +100% · 105,1 | +233% · 5,7 | | +900% · 9,0 | +1.233% · 0,6 | | +1.900% · 0,1 | | **0% · 36,3** |
| **0,2** | 0% · 3,0 | +67% · 11,5 | | +400% · 8,0 | +567% · 0,5 | | | | |
| **0,25** | −20% · 0,5 | +33% · 0,8 | | | +433% · 0,4 | | | | |
| **0,5** | | −33% · 3,3 | +53% · 0,1 | +100% · 0,4 | | | | | |
| **0,65** | | | | | | | +208% · 0,1 | | |
| **0,8** | | | | | | | +150% · 1,2 | | |
| **1,0** | −80% · 0,8 | −67% · 1,0 | | 0% · 11,9 | **+33% · 20,1** | +60% · 0,9 | +100% · 0,9 | +140% · 0,3 | |
| **1,3** | −85% · 0,9 | −74% · 0,1 | | −23% · 7,5 | **+3% · 23,3** | **+23% · 21,7** | **+54% · 26,6** | +85% · 6,5 | |
| **1,6** | −88% · 0,01 | | | | −17% · 0,3 | **0% · 5,9** | +25% · 3,8 | +50% · 0,5 | |
| **1,9** | | | | | | **−16% · 4,3** | +5% · 3,7 | +26% · 1,2 | |
| **2,4** | | | | | | −33% · 0,6 | −17% · 0,9 | 0% · 2,0 | |
| **3,0** | | | | | | −47% · 0,05 | | | |

Combinações com menos de 0,01 km² foram omitidas. A matriz completa está no mapa e em `dados/tabelas/matriz_ia_ca_basico.csv`.

### IA das leis específicas (subunidades com código 23, 25, 39, 41 ou 999)

Nessas 414 subunidades (99 km²) o Anexo 6 não traz número. Cada uma foi conferida na norma que define o regime, lida no texto integral (SAPL da Câmara/PGM e DOPA, com OCR quando o arquivo era imagem). Também foram buscados decretos posteriores pela ementa no SAPL. Resultado:

| Situação | Subunidades | Área |
|---|---|---|
| **IA numérico encontrado na lei ou decreto** (entra na comparação) | 156 | 16,4 km² |
| Ilhas do Delta do Jacuí: parque e APA estaduais (Lei Estadual 12.371/05), sem IA municipal | 20 | 39,3 km² |
| Parques e áreas de proteção ambiental (códigos 25 e 39, regime próprio) | 45 | 20,0 km² |
| Áreas especiais institucionais (código 23: regime a critério do município, IA até 2,5) | 28 | 9,0 km² |
| AEIS sem regime definitivo (Dec 12.716/00 e 13.550/01: o regime sai no projeto de regularização) | 98 | 6,1 km² |
| Áreas de interesse cultural (inclusive Centro Histórico e 4º Distrito: LC 930/21 e LC 960/22 mantêm o código 25) | 45 | 5,1 km² |
| Leis que remetem o regime a decreto ou EVU sem fixar número (LC 717/13, LC 799/16 arts. 10/11 e 29–31, LC 736/14 etc.) | 22 | 3,2 km² |

Normas com mais área em que o IA foi encontrado:

| Norma | Subunidades | IA básico |
|---|---|---|
| LC 935/22 (Fazenda Arado Velho) | 11 | 1,3 nas áreas urbanizáveis; 0,05 a 0,25 nas de proteção |
| LC 624/09 (AEIS II de loteamentos irregulares) | 22 | 1,3 |
| LC 799/16 (AEIS e regularizações) | 30 | 1,0 a 1,9, por subunidade |
| LC 324/94 | 4 | 0,8 (máximo 2,5) |
| LC 847/19 e LC 919/21 (AEIS III) | 2 | 1,3 |
| LC 609/09 | 6 | 1,0 a 1,6 |
| LC 833/18 e LC 764/15 (Hospitais Conceição e Mãe de Deus) | 2 | 3,0 |
| LC 930/21 (armazéns do Cais Mauá) | 2 | 0,5 |
| Cerca de 50 decretos de AEIS (2003–2026) | 1 a 5 cada | 1,0 a 1,9 (quase sempre 1,3) |

Pontos que merecem atenção:

- **Decretos que o DMWeb ainda não reflete.** Três subunidades seguem como "regime próprio" na base da Prefeitura, mas já têm IA em decreto, e o mapa usa esse IA:
  - Dec 22.163/23: IA 1,3 em 10-002-16;
  - Dec 23.877/26: IA 1,0 no Núcleo Esperança, 7-006-04 e 7-012-03;
  - Dec 23.958/26: IA 1,3 em 7-012-05.
- **LC 935/22 (Arado Velho)** foi declarada nula em 1ª instância (06/2024), com recurso pendente. O mapa usa o IA da lei e avisa na consulta.
- **LC 930/21 (Centro Histórico).** Para quem adere ao programa, o IA básico do PDDUA é multiplicado por 1,5 e passa a contar a área total. Isso dá a mesma área privativa da conta usada aqui: IA × 1,5 × 0,8 = IA × 1,2.
- **Conflito no Cais Mauá (1-002-04).** A LC 930/21 fixa IA 0,5; o Anexo VI.B da LC 960/22 lista a subunidade com código 25. O mapa usa 0,5 e registra o conflito.
- **Normas que valem para parte da subunidade.**
  - Dec 16.612/10 (Beco Vila da Paz) foi aplicado só ao polígono certo de 3-114-06.
  - A LC 729/14 fixa IA 0,1 para um único imóvel na Ilha Grande dos Marinheiros. Por isso não foi estendida à subunidade 9-012-02.
- **LC 405/97 (PUCRS)** limita a área construída total a 1,5 vez o terreno, contando as áreas não computáveis. Isso equivale a IA 1,0 na base do PDDUA.

Onde a norma não fixa número, a consulta mostra a norma verificada. Nos códigos 23 e 25 mostra também o **pior caso**, com o IA no teto de 2,5. A lista completa, com artigo e observação de cada subunidade, está em `dados/tabelas/ia_leis_especificas.csv`.

### O que os números dizem

- **Cidade consolidada (IA ≥ 1,0, 146 km² com as áreas de lei específica).** Com as emendas, a área privativa potencial básica cresce **+20% no agregado** (antes das emendas eram +13%):
  - 16,4 km² perdem mais de 5%;
  - 43,1 km² ficam praticamente iguais;
  - 86,3 km² ganham mais de 5%.

  As áreas com IA de lei específica, quase todas AEIS com IA 1,3, ganham +15% no agregado.
- **A Emenda 91 muda bastante a leitura.** Os 26 km² de IA 1,3 que viraram CA 3,0 passam de +23% para +54%. As áreas de IA 1,9 nas ZOT 12/13 e 08.3 deixam de perder (−16%) e passam a ganhar 5%.
- **Maiores perdas que restam, com o potencial básico:**

  | Bairro | Ganho |
  |---|---|
  | Azenha | −13% |
  | Passo D'Areia | −8% |
  | Cristo Redentor | −7% |
  | Menino Deus | −7% |
  | Vila Ipiranga | −6% |

  São as quadras de IA 1,9 que ficaram em CA 2,4 (ZOT 05 a 08, 10 e 11) e as de IA 1,3 que foram para CA 1,5 (ZOT 01).
- **Maiores ganhos na malha urbana:**

  | Bairro | Ganho |
  |---|---|
  | Farrapos | +91% |
  | Navegantes | +85% |
  | Humaitá | +85% |
  | São Geraldo | +71% |
  | Costa e Silva | +67% |
  | Anchieta | +54% |
  | Parque Santa Fé | +54% |
  | Sarandi | +53% |

  Fora o 4º Distrito, esses bairros são as ZOT 12/13 que passaram a CA 3,0.
- **Atenção às áreas rarefeitas (IA 0,1 / 0,2).** O percentual é alto porque a base é pequena: IA 0,1 → CA 0,3 dá +100%, mas é 0,12 → 0,24 m² privativo por m² de terreno.

A tabela por bairro está em `dados/tabelas/dinamica_por_bairro.csv`, coluna `ganho_priv_bas_pct`, agregada por área.

## 6. Limitações (leia antes de decidir)

1. **Vigência.** As leis novas entram em vigor 180 dias após a publicação (14/07/2026), por volta de janeiro/2027. Até lá vale o PDDUA. Há ação judicial (MPF) questionando o processo de revisão.
2. **Vetos.** Polígonos vetados (≈4,6 km² na Lomba do Pinheiro) aparecem como "POLÍGONO VETADO". O regime depende da apreciação do veto pela Câmara.
3. **Emendas e ZOT 08.3-D.**
   - O CA básico das ZOT 08.3-A/B/C, 12, 13 e 08.3-D vem das emendas aprovadas, conforme a lista publicada da votação, e não da base GIS. Confira no texto final da LC 1.076/2026, Anexo 2.
   - A ZOT 08 propriamente dita (0,22 km² em Praia de Belas, Azenha e Menino Deus) não aparece na Emenda 91 e foi mantida em 2,4.
   - CA máximo e altura da ZOT 08.3-D seguem sem publicação.
4. **Regime vindo da base GIS.** O regime por ZOT vem da base GIS da SMAMUS, não do texto da lei. Confira na LUOS publicada no DOPA antes de usar em viabilidade.
5. **Só o zoneamento-base.** O mapa não traz gravames, recuos viários, AEIS, patrimônio cultural, APP, restrições do aeroporto (PBZPA), EVU nem outras condicionantes do lote. Para isso use o DMWeb (plano antigo) e a futura certidão do plano novo.
6. **Potencial máximo não é garantido.** No PDDUA o IA máximo depende de estoque de solo criado. No plano novo, o CA máximo depende de outorga onerosa / TDC.
7. **IA de leis específicas.**
   - A tabela foi montada lendo cada norma. Subunidades renumeradas depois da norma foram casadas pela observação do DMWeb e pela localização.
   - Só o IA foi trazido das normas: altura e taxa de ocupação dessas áreas seguem o código do Anexo 7.1.
   - Confira a norma citada antes de usar o número em viabilidade.
8. **Precisão da geometria.** O HTML usa geometria simplificada a 0,3 m. Os GPKG/GeoJSON mantêm a geometria original. Lotes na divisa entre zonas devem ser conferidos no DMWeb.

## 7. Atualizar os dados

```bash
cd mapa-plano-diretor-poa/scripts
pip install geopandas pyogrio
python3 download.py /tmp/raw                 # baixa tudo dos servidores oficiais (~15 min)
python3 build_gis.py /tmp/raw ../dados       # GIS antigo, novo e sobreposição
python3 build_kmz.py ../dados/planos_diretores_poa.kmz
python3 build_html.py /tmp/raw ../mapa_planos_diretores_poa.html
```

O servidor da SMAMUS recusa conexões quando está sobrecarregado. O `download.py` tenta de novo automaticamente.

Mapa feito com [Leaflet](https://leafletjs.com) 1.9.4 (licença BSD-2, em `scripts/vendor/`).
