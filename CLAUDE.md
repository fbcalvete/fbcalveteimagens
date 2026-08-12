# Estudo Volumétrico — LUOS Porto Alegre (LC 1.076/2026)

Ferramenta web de estudo de viabilidade volumétrica a partir de terrenos de
Porto Alegre. Arquivo único, autossuficiente: **`estudo-volumetrico.html`**
(~800 KB). Todo o trabalho é em português. Contexto: incorporadora Melnick.

> Este arquivo é lido pelo Claude Code no início de cada sessão. Ele carrega o
> conhecimento acumulado do projeto — leia antes de mexer em qualquer cálculo.

---

## Princípios de trabalho

- Reportar incerteza com honestidade; nunca "maquiar" um resultado.
- Testar em navegador real (Puppeteer) antes de considerar pronto.
- A lei governa: a LUOS (LC 1.076/2026) e o Anexo II são a fonte da verdade.

## Armadilha nº 1 — não repetir o erro das duas cópias

Historicamente havia duas cópias do HTML (uma de trabalho e a entregável) e um
`cp` errado reintroduzia código morto. **Com git isso deixa de ser problema:**
trabalhe em um arquivo só, versione, e confie no diff. Se mantiver cópias, sempre
confirme com `md5sum` que estão idênticas antes de terminar.

## Como validar a sintaxe do JS embutido

Há dois blocos `<script>`: o primeiro tem constantes + um PNG base64 da grade de
ZOTs; o último tem o app. Para checar a sintaxe:
```
python3 -c "import re;h=open('estudo-volumetrico.html').read();open('app.js','w').write(re.findall(r'<script>(.*?)</script>',h,re.S)[-1])"
node --check app.js
```

## Testes (Puppeteer)

Padrão: abrir `file://` do HTML, esperar `GRADE` carregar, `mapa.setView([lat,lng],18)`,
esperar as camadas de lotes, ~3,5 s, selecionar um lote via `cacheLotes.find`,
`selecionar(lote,{className:'',textContent:''})` (ATENÇÃO: `selecionar` alterna —
chamar de novo desmarca), depois `$('irEstudo').click()`. O basemap CARTO não
renderiza em headless (fundo escuro), então valide por medição numérica, não por
leitura de screenshot.

Baseline de regressão (todos devem passar): base 3 pav 12,5 m; base estacionamento
não computa CA; subsolo 0; ruas via eixos aparecem; cotas+recuo no 3D; toggle
desliga base; rótulo é plano (não sprite); 3D desenha; mancha bege em z15 = 0,0%;
plantas abrem (situação + corte).

---

## Fontes de dados (ArcGIS da prefeitura, CORS aberto)

Base: `https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/01_PUBLICACOES`
- **LOTES**: `dmweb_lotes_fiscais/FeatureServer/0` — geometria dos lotes.
- **NÚMEROS**: `nro_imovel/FeatureServer/0` — números de imóvel.
- **EIXOS**: `eixos/FeatureServer/0` — eixos de logradouro. Campo `nmidelog`
  (nome limpo, MAIÚSCULO) e `nmideabr` (abreviado com tipo, ex.: "R PE CHAGAS").
  **É a fonte dos nomes das ruas de frente** (substituiu o Nominatim, que falhava
  em frentes curtas/esquinas e por limite de requisição). O Nominatim só é usado
  na caixa de busca de endereço.
- **Grade de ZOTs embutida** (PNG base64): amostragem de 7×7 pontos internos do
  lote, voto majoritário, para achar a ZOT.

---

## Motor de cálculo (`resolver()`, em metros)

Regras-chave da LUOS embutidas:

- **Base isenta** (dispensa de afastamentos até a cota) = 12,5 m por padrão,
  editável (`#ovBase`) e com toggle (`#baseIsOn`). Modelada como 3 pavimentos de
  ~4,17 m ocupando o lote todo até a divisa. **`ovBase = 0` significa 0** (sem
  base, torre do chão) — o fallback 12,5 só vale quando o campo está vazio.
- **Recuo lateral**: `fLat = usar15 ? 0.15 : R.lat`, onde `usar15` é verdadeiro
  quando a testada ≤ 20 m (`R.d15`). Ou seja: **18% da altura, ou 15% se a testada
  < 20 m** (Emenda 88 / Jessé Sangalli). Aplica-se acima da base isenta:
  `rDiv = fLat * H`.
- **Uso da base** = estacionamento por padrão (`#usoBase = 'gar'`, não computa CA);
  `'com'` = uso computável.
- **Subsolo** padrão 0 (`#nSub`).
- **Otimizador** padrão = altura máxima; toggle `#modoLaje` respeita uma laje-alvo
  (torre mais baixa). `trava` pode ser: 'ia', 'altura', 'recuo', 'tp', 'laje',
  'implantada'.
- **Retorno** inclui, entre outros: `R, T, best, trava, lajeReal, nSub, areaSubsolo,
  nBase, pdBase, Hbase, baseComputa, envB, pd, rj, rjEfetivo, baseIsenta, implantada,
  hMax`. `best = {nT, H, laje, anel, rDiv, acTorre, acTotal, sat, (W,D se implantada)}`.
  `T = {anel, arestas (tipo frente/divisa, a, b), area, testada, largura, prof, ...}`.

## Torre implantada (lotes irregulares)

Quando os recuos inviabilizam a torre natural (laje ~0, por slivering do recorte
em polígonos de muitos vértices), o programa **reparte o terreno**: insere um
retângulo compacto (alvo ~600 m²) na parte larga do corpo voltada para a frontagem.

- Gatilho: maior laje da torre natural < 80 m² **e** a implantada rende mais.
- **Respeita o recuo lateral** (18%/15% da altura) — checado por distância de cada
  canto/meio de aresta a cada divisa (robusto ao slivering; NÃO usa o recorte por
  semiplanos, que colapsa em contornos ruidosos).
- **Posição por busca em grade**: varre centros no lote e acha a maior posição do
  retângulo que respeita o recuo; orientação vem da direção média das frentes
  (não da maior aresta única — que, fragmentada, caía no vértice reentrante do L).
- Sobe até a maior altura em que a laje ainda cabe respeitando o recuo no topo.

## 3D (Three.js r128, `desenhar(s)`)

Extruda o polígono real do lote: base (nBasePav pavimentos até a divisa) + torre
(best.nT pavimentos a partir de best.anel) + wireframe do envelope máximo.

Rótulos de chão (ruas, cotas do terreno, recuo lateral): são **planos deitados**
(`rotuloChao`), não sprites — não giram com a câmera e se alinham à rua/aresta.
Anti-sobreposição por **caixas orientadas (OBB/SAT)**: cada rótulo é uma caixa
girada e nenhum é posto onde encoste em outro. Em esquina, os nomes de rua ancoram
no vértice comum e divergem (cada um para o seu lado).

CUIDADO ao medir sobreposição em teste: os vértices de `PlaneGeometry` vêm em ordem
de grade [TL, TR, BL, BR] — a ordem de perímetro para SAT é [0,1,3,2]. Usar a ordem
errada dá falso positivo (foi um erro real de teste, não do código).

## Plantas (página "Ver Plantas", na etapa 3D)

Botão `#btnPlantas` abre `#telaPlantas` com duas plantas SVG **geradas do
`resolver()` do momento** (sempre refletem o modelo atual):

1. **Situação** — SEMPRE com o **norte para cima** (o Y projetado cresce para o
   Norte; a tela espelha Y). Mostra a medida de cada face do terreno, o
   empreendimento sobreposto, as medidas da laje, e os **recuos como linhas de eixo
   tracejadas (dash-dot)** paralelas às faces — âmbar (recuo de jardim) e azul
   (recuo lateral) — com o valor cotado uma vez por tipo (maior frente e maior
   divisa) para não poluir em lotes de muitos vértices. Anti-sobreposição dos
   rótulos por AABB; medidas das faces têm prioridade.
2. **Corte esquemático** — altura atingida (cota), embasamento (base isenta),
   torre recuada acima (recuo lateral cotado), subsolos, e resumo textual.

---

## Estado atual / pendências conhecidas

- Concluído: ruas via eixos; base isenta editável+toggle; base=estacionamento;
  subsolo 0; otimizador de altura com laje-alvo; rótulos de chão OBB no 3D;
  `ovBase=0` corrigido; torre implantada respeitando recuo lateral e posicionada
  na parte larga por busca em grade; página "Ver Plantas" (situação norte-para-cima
  + corte) refletindo o modelo; recuos como linhas de eixo com valor na situação.
- Em aberto (do lado do usuário): conferência pontual de ~17,5% de divergência de
  ZOT contra uma camada externa; conferência do visual final sobre o basemap CARTO
  ao vivo.
- Ideia futura: agrupar faces colineares numa medida só, para lotes de contorno
  muito ruidoso (evita rótulos minúsculos espremidos).
