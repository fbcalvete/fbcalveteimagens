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

**Limitação conhecida deste ambiente (Claude Code on the web, container isolado):**
o Chromium headless (Playwright, `/opt/pw-browsers`) não consegue completar o
handshake TLS de nenhum host HTTPS externo através do proxy do agente — o `curl`
com o mesmo proxy funciona normalmente, mas o Chromium recebe `ERR_CONNECTION_RESET`
a meio do TLS (confirmado via `--log-net-log`: o RESET vem depois do Client Hello,
antes do Server Hello — não é allowlist de host, pois acontece até com hosts em
`no_proxy`). Isso bloqueia o teste Puppeteer/Playwright end-to-end de verdade
(carregar o mapa, buscar lotes no ArcGIS, renderizar) **neste tipo de sessão**.
Se isso acontecer de novo: não insista em flags de TLS do Chromium — em vez disso,
extraia as funções de geometria puras (`areaAnel`, `pontoNoPoligono`, `recortar`,
`torreImplantada`, `distPtSeg`, etc. — todas sem DOM) para um módulo Node isolado
e teste com lotes sintéticos (ver `torreImplantada` acima). Isso cobre a lógica;
a verificação visual no navegador real (com mapa e ArcGIS ao vivo) fica pendente
do lado do usuário, ou de uma sessão local/self-hosted sem essa restrição de proxy.

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
  hMax`. `best = {nT, H, laje, anel, rDiv, acTorre, acTotal, sat, (W,D se implantada
  e a laje ficou retangular; ausentes se a laje foi deformada)}`.
  `T = {anel, arestas (tipo frente/divisa, a, b), area, testada, largura, prof, ...}`.
- **`lajeReal`** (área de laje mostrada em toda a UI/plantas/corte) é **sempre**
  `best.laje`, a área física do polígono `best.anel` (a mesma que é desenhada) —
  nunca `acTorre/nT`. Essa média por CA computável diverge do físico sempre que o
  coeficiente satura antes do último pavimento ou a torre afunila com a altura, e
  foi a causa de um bug real (planta mostrando uma laje e o texto mostrando outra
  área). Se mexer no cálculo de `lajeReal`, derive sempre do polígono, nunca do CA.

## Torre implantada (lotes irregulares)

Quando os recuos inviabilizam a torre natural (laje ~0, por slivering do recorte
em polígonos de muitos vértices), o programa **reparte o terreno**: insere uma
laje compacta (alvo editável em `#ovLajeImplant`, 600 m² por padrão) sempre
ancorada na **maior testada** do lote.

- Gatilho: maior laje da torre natural < 80 m² **e** a implantada rende mais.
- **Ancoragem**: centralizada na maior testada (`torreImplantada()` agrupa arestas
  `frente` contíguas no anel — com wraparound — e pega o grupo de maior soma de
  comprimento). Se essa testada faz esquina com outra frente (mudança de direção
  > 25° dentro do grupo), a laje ancora **no vértice da esquina** em vez do meio —
  nesse caso ela fica **a `rj` de distância de AMBAS as frentes**, não só da de
  referência (bug real: a primeira versão só afastava da frente de referência e
  colava a laje em cima da outra).
- **Formato**: começa quadrada no alvo, encostada no recuo de jardim. Se o recuo
  lateral não deixa fechar o alvo num retângulo, encolhe (mantendo quadrado/
  proporção) até caber. Se ainda faltar área para o alvo, **deforma**: busca radial
  (64 raios, busca binária) a partir do centro do melhor retângulo, seguindo o
  contorno legal real (não o recorte por semiplanos, que sliverriza em contornos
  ruidosos) — se sobrar área além do alvo, escala de volta para o alvo exato.
  A área de `ti.area` é sempre `Math.abs(areaAnel(ti.anel))` — casa 100% com o
  polígono desenhado.
- Sobe até a maior altura em que a laje (do tamanho que couber) ainda cabe
  respeitando o recuo no topo — **reduzir o alvo de área ganha altura**; aumentar
  exige altura menor (mesmo mecanismo, agora exposto ao usuário via `#ovLajeImplant`).
- Testado com funções puras extraídas (sem browser) em 4 cenários sintéticos:
  testada única sem esquina, lote de esquina, lote estreito forçando deformação, e
  o mesmo lote de esquina com alvo menor (confirma o trade-off área↔altura). Os 4
  passam com área reportada == área do polígono e distâncias de recuo respeitadas.

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
   tracejadas (dash-dot)** — âmbar (recuo de jardim) e azul (recuo lateral) — com o
   valor cotado uma vez por tipo (maior frente e maior divisa) para não poluir em
   lotes de muitos vértices. Anti-sobreposição dos rótulos por AABB; medidas das
   faces têm prioridade.
   **O tracejado é um contorno único por OFFSET LOCAL a cada vértice** (miter
   join com as duas arestas vizinhas — não o recorte global por meio-planos do
   `recortar()`, que é usado no cálculo do envelope mas **colapsa a zero
   vértices em lotes bem irregulares** — a mesma razão pela qual a torre
   implantada existe. Duas rodadas de bug real aqui: (1) antes cada aresta
   original desenhava sua própria linha offset sem juntar nos cantos ("linhas
   soltas"); (2) a primeira correção trocou para `recortar()` global, que
   junta os cantos mas em lotes com "pescoço" estreito colapsa e não desenha
   tracejado NENHUM — só apareceu com um lote em Z real do usuário. A versão
   atual calcula, para cada vértice do terreno, a interseção das retas
   offset das DUAS arestas vizinhas (miter); se a interseção dispara longe
   demais (reentrância apertada), cai para uma quina chanfrada (bevel) em vez
   do vértice de recorte. Como cada canto só depende das arestas vizinhas a
   ele, nunca colapsa globalmente — sempre desenha algo, em qualquer lote.
   A cor de cada segmento vem direto do tipo da aresta original que o gerou
   (sem precisar comparar distâncias).
2. **Corte esquemático** — altura atingida (cota), embasamento (base isenta),
   torre recuada acima (recuo lateral cotado), subsolos, e resumo textual.

---

## Estado atual / pendências conhecidas

- Concluído: ruas via eixos; base isenta editável+toggle; base=estacionamento;
  subsolo 0; otimizador de altura com laje-alvo; rótulos de chão OBB no 3D;
  `ovBase=0` corrigido; página "Ver Plantas" (situação norte-para-cima + corte)
  refletindo o modelo; recuos como linhas de eixo com valor na situação.
- Concluído (rodada de correções na planta de situação e na torre implantada):
  linha de recuo na planta de situação virou um contorno único conectado (era
  segmentos soltos por aresta); `lajeReal` agora sempre casa com a área física do
  polígono desenhado (era uma média por CA computável, podia divergir bastante);
  área-alvo da laje da torre implantada virou parâmetro editável
  (`#ovLajeImplant`, 600 m² por padrão); torre implantada reancorada — sempre na
  maior testada, centralizada nela ou no vértice se fizer esquina, encostada no
  recuo de jardim (de ambas as frentes na esquina), e deforma (busca radial) em
  vez de só encolher quando o alvo não fecha num retângulo.
- Em aberto (do lado do usuário): conferência pontual de ~17,5% de divergência de
  ZOT contra uma camada externa; conferência do visual final sobre o basemap CARTO
  ao vivo; **validação em navegador real** da rodada de correções acima (só foi
  possível testar a geometria pura nesta sessão — ver limitação de ambiente na
  seção de Testes).
- Ideia futura: agrupar faces colineares numa medida só, para lotes de contorno
  muito ruidoso (evita rótulos minúsculos espremidos).
