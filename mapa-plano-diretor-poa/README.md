# Mapa comparativo dos Planos Diretores de Porto Alegre

Comparação, terreno a terreno, entre o **plano antigo (PDDUA, LC 434/99)** e o **plano novo
(PDUS + LUOS, sancionados em 14/07/2026)**. O pacote tem:

- um mapa HTML que roda sozinho;
- os GIS de cada plano em arquivos independentes;
- um GIS da sobreposição, com a dinâmica de cada área (ampliou / manteve / reduziu o potencial construtivo).

Dados extraídos em **29/10/2026** dos serviços oficiais da Prefeitura.

## 1. Abrir o mapa

Abra `mapa_planos_diretores_poa.html` com duplo clique (Chrome, Edge, Firefox ou Safari).

- **Funciona offline.** Geometria, base de ruas oficial, numeração predial e a biblioteca de mapa estão dentro do arquivo (6,3 MB).
- **Sem satélite.** O fundo é a malha de logradouros da Prefeitura. Com internet, dá para ligar por baixo um mapa de ruas da CARTO.

### Como consultar um terreno

1. Digite o endereço na busca (`Av. Ipiranga 1200`, `Padre Chagas 300`, `Dr. Timóteo 500`) ou uma coordenada (`-30.035, -51.22`). Também dá para clicar direto no mapa.
2. O painel mostra, para aquele ponto:
   - **Plano antigo:**
     - zona de uso, MZ/UEU/subunidade e código D·A·I·V;
     - IA básico e máximo, CA equivalente, solo criado/TPC, quota ideal;
     - altura máxima, altura na divisa e na base, taxa de ocupação.
   - **Plano novo:**
     - ZOT e tipo de ocupação;
     - CA básico e máximo, altura máxima, lote mínimo, permeabilidade, recuo de jardim;
     - caracterização e finalidade da zona;
     - a ZOT que o ponto tinha no projeto pós-audiência, quando mudou.
   - **Dinâmica:** Δ CA básico, Δ CA máximo e Δ altura, com a classificação ampliou / manteve / reduziu.
3. **Copiar resumo** gera um texto pronto para colar na planilha de estudo.

### Camadas e cores

| Controle | O que faz |
|---|---|
| Plano antigo / Plano novo / Dinâmica | Liga e desliga cada mancha. Analise separado ou em conjunto. |
| Contorno | Mostra só o limite das zonas, para ver um plano sobre o outro. |
| Barra de opacidade | Transparência de cada camada. |
| Colorir os planos por | **Zona** (cada plano com sua legenda), **CA máximo**, **CA básico** ou **Altura**. CA e altura usam a mesma escala nos dois planos, para comparação visual direta. |
| Colorir a dinâmica por | Δ CA máximo, Δ CA básico, Δ altura ou classe (ampliou/reduziu). |
| Passar o mouse | Mostra, ao mesmo tempo, a zona antiga e a nova sob o cursor. |

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
| `dados/tabelas/*.csv` | Anexos 5.1, 6 e 7.1 do PDDUA, regime por ZOT e **dinâmica por bairro**. |
| `dados/fontes_originais/` | Cópia comprimida dos dados brutos baixados, com URLs e horário (`fontes.json`). |
| `scripts/` | Download, processamento e geração do HTML/KMZ (reprodutível). |

Os GPKG e GeoJSON estão em WGS 84 (EPSG:4326). Abrem no QGIS, ArcGIS, Global Mapper e geojson.io.

### Campos principais

**Plano antigo** (`pddua_antigo_zonas`):

| Campo | Significado |
|---|---|
| `mz`, `ueu`, `subunid`, `cod_subun` | Macrozona, UEU e subunidade. |
| `dens_cod`, `ativ_cod`, `ia_cod`, `vol_cod` | Códigos D·A·I·V do regime urbanístico. |
| `zona_uso` | Zona de uso (Anexo 5.1). |
| `ia_bas`, `ia_max` | Índice de aproveitamento básico e máximo (Anexo 6). |
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

O link do ArcGIS Experience indicado no pedido ("Pós Audiência – Zoneamento – PDUS") usa a camada `INTERSECT_PLAN_08_09_25_v2`, de set/2025. Ela é **anterior** às emendas da Câmara e aos vetos. Por isso a comparação usa o mapa da LUOS sancionada. A zona da versão pós-audiência fica registrada em `zot_projeto` e aparece na consulta quando difere.

## 4. Método

- **CA equivalente.** O CA do plano novo soma áreas adensáveis e não adensáveis. O IA do PDDUA conta só as adensáveis. Para comparar, `CA equivalente = IA × 1,5`, a mesma regra que a SMAMUS usa no comparativo oficial (campos `ia_b_atual` e `ia_m_atual` da base municipal; conferido, por exemplo IA 1,9 → 2,85).
- **Classes.** Diferenças de até ±0,05 no CA ou ±0,5 m na altura contam como **Manteve**.
- **CA máximo sem acréscimo.** Quando o CA máximo novo é "Não se aplica" ou "Ajuste/TDC", ele é tratado como igual ao básico.
- **Regime por ZOT.** Vem do Anexo 5, apenas dos quarteirões em que a zona antes e depois das emendas é a mesma. Nas linhas alteradas por emenda, a base oficial ainda traz o regime da zona anterior.
- **Áreas fora do mapa da LUOS.** Onde o mapa sancionado não cobre (áreas ESPECIAIS, alguns quarteirões), a zona vem do Anexo 5. O campo `fonte` indica esses polígonos.
- **Sobreposição.** Interseção geométrica em SIRGAS 2000 / UTM 22S (EPSG:31982). Peças menores que 10 m² foram descartadas.

## 5. Leitura rápida dos resultados

Área de quarteirões comparáveis, pelo CA máximo:

| Resultado | Área |
|---|---|
| Ampliou | 250,5 km² |
| Manteve | 16,2 km² |
| Reduziu | 13,7 km² |
| Sem comparação | 137,2 km² (regime próprio, áreas especiais, zona rural) |

Pelo **CA básico**, 19,7 km² reduziram. Pela **altura**, 81,4 km² ampliaram e 8,6 km² reduziram.

**Maior ampliação média do CA máximo:** Farrapos (+3,6), Humaitá (+3,5), Centro Histórico (+3,4), Independência (+3,3), São Geraldo (+3,2), Floresta (+3,1) e Navegantes (+3,0). É o eixo 4º Distrito / Centro.

**Mais área com redução do CA máximo:**

| Bairro | Área do bairro com redução |
|---|---|
| Camaquã | 55% |
| Cavalhada | 43% |
| Glória | 38% |
| Tristeza | 33% |
| Rubem Berta | 22% |
| Medianeira | 20% |
| Menino Deus | 17% |

Em Menino Deus e Santa Cecília o CA **máximo** sobe, mas o **básico** cai em parte das quadras. Ou seja, há mais potencial, porém mais dele passa a ser **oneroso**.

A tabela completa está em `dados/tabelas/dinamica_por_bairro.csv`.

## 6. Limitações (leia antes de decidir)

1. **Vigência.** As leis novas entram em vigor 180 dias após a publicação (14/07/2026), por volta de janeiro/2027. Até lá vale o PDDUA. Há ação judicial (MPF) questionando o processo de revisão.
2. **Vetos.** Polígonos vetados (≈4,6 km² na Lomba do Pinheiro) aparecem como "POLÍGONO VETADO". O regime depende da apreciação do veto pela Câmara.
3. **ZOT 08.3 - D.** Foi criada por emenda (Cidade Baixa e Bom Fim) e ainda não tem parâmetros na base GIS da Prefeitura. Fica como "sem comparação".
4. **Regime vindo da base GIS.** O regime por ZOT vem da base GIS da SMAMUS, não do texto da lei. Confira na LUOS publicada no DOPA antes de usar em viabilidade.
5. **Só o zoneamento-base.** O mapa não traz gravames, recuos viários, AEIS, patrimônio cultural, APP, restrições do aeroporto (PBZPA), EVU nem outras condicionantes do lote. Para isso use o DMWeb (plano antigo) e a futura certidão do plano novo.
6. **Potencial máximo não é garantido.** No PDDUA o IA máximo depende de estoque de solo criado. No plano novo, o CA máximo depende de outorga onerosa / TDC.
7. **Precisão da geometria.** O HTML usa geometria simplificada a 0,3 m. Os GPKG/GeoJSON mantêm a geometria original. Lotes na divisa entre zonas devem ser conferidos no DMWeb.

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
