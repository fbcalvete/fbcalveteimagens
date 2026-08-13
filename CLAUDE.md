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
- **Otimizador**: por padrão mira a **laje alvo** (`#ovLajeAlvo`, 600 m² editável,
  campo único que rege torre natural E implantada — decisão explícita do
  usuário, ver seção "Laje alvo" abaixo) e sobe até a maior altura em que
  ela ainda cabe dentro do CA disponível (`best = cUser || alto`). Só cai
  para o gabarito de altura/CA máximos (`alto`, o pavimento mais alto viável,
  sem mirar área nenhuma) quando NENHUM pavimento comporta a laje alvo
  (`cUser` nulo — ex.: lote pequeno onde até o térreo já é menor que o alvo).
  `trava` pode ser: 'ia', 'altura', 'recuo', 'tp', 'laje', 'implantada'.
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

## Laje alvo (`#ovLajeAlvo`, painel esquerdo, 600 m² por padrão)

Parâmetro **único** que rege o dimensionamento da torre, **natural ou
implantada** — decisão explícita do usuário (havia um checkbox "Respeitar a
área de laje alvo" separado, ligado a unidades×privativa, só para a torre
natural, e um campo em m² separado só para a torre implantada; unificados
num só campo depois que o usuário pediu que valesse sempre, mesmo com CA
sobrando). Reduzir a área ganha recuo e permite subir mais; aumentar exige
altura menor para caber — o mesmo mecanismo em ambos os casos:
- **Torre natural**: `lajeDesejada = alvoLaje`; percorre `curva` (um envelope
  por altura) e escolhe o `nT` mais alto cujo `laje >= lajeDesejada` **e**
  caiba no CA (`cUser`). `best = cUser || alto` — só cai para `alto` (o
  pavimento mais alto viável, sem mirar área nenhuma) quando NENHUM
  pavimento comporta o alvo dentro do CA disponível.
- **Torre implantada**: mesmo campo (`alvoLaje`) passado como `alvo` para
  `torreImplantada()`, ver seção abaixo.
- Testado com dados sintéticos de `curva` (lote grande com laje encolhendo
  por altura, lote pequeno onde nada cabe no alvo, mesmo lote grande com
  alvo menor): confirma que o padrão troca de "maximizar altura, laje
  resultante" para "mirar o alvo, altura resultante", sem regressão nos
  lotes onde o alvo não cabe em nenhum pavimento.

## Torre implantada (lotes irregulares)

Quando os recuos inviabilizam a torre natural (laje ~0, por slivering do recorte
em polígonos de muitos vértices), o programa **reparte o terreno**: insere uma
laje compacta (alvo = **laje alvo**, ver seção acima) sempre ancorada na
**maior testada** do lote.

- **Gatilho**: maior laje da torre natural < 80 m² **OU** a laje do pavimento
  ESCOLHIDO (`best.laje`) < 80 m² — **e** a implantada rende mais. Cuidado:
  checar só a maior laje entre TODOS os pavimentos (`maxLajeNat`) não basta — um
  lote pode ter laje boa num pavimento baixo mas só um fiapo no pavimento
  mais alto escolhido pelo otimizador (a laje encolhe com a altura, recuo
  cresce com H). Nesse caso `maxLajeNat` ficava ≥80 e o gatilho antigo nunca
  disparava, mesmo com o resultado final sendo um fiapo — bug real: a torre
  implantada e o botão "Laje retangular" pareciam não fazer nada nesses
  lotes, porque nunca eram nem tentados.
- **Ancoragem**: centralizada na maior testada (`torreImplantada()` agrupa arestas
  `frente` contíguas no anel — com wraparound — e pega o grupo de maior soma de
  comprimento). Se essa testada faz esquina com outra frente (mudança de direção
  > 25° dentro do grupo), a laje ancora **no vértice da esquina** em vez do meio —
  nesse caso ela fica **a `rj` de distância de AMBAS as frentes**, não só da de
  referência (bug real: a primeira versão só afastava da frente de referência e
  colava a laje em cima da outra).
- **Formato**: começa quadrada no alvo, encostada no recuo de jardim. Se o recuo
  lateral não deixa fechar o alvo num retângulo, encolhe (mantendo quadrado/
  proporção) até caber. Se ainda faltar área para o alvo, **deforma**.
  Botão **`#tgRetangular`** (barra de cima da massa 3D, "Laje retangular") força
  a laje a ficar sempre no maior retângulo que couber, nunca deformando — passa
  `soRetangular=true` para `torreImplantada()`, que pula a deformação inteira.
- **Deformação — cuidado, já teve dois bugs reais de recuo sendo violado**:
  1. Busca radial pura (raio legal por ângulo via busca binária a partir do
     centro do retângulo) só garante que os **vértices** respeitam o recuo — a
     **corda reta** entre dois raios vizinhos pode cortar por dentro da zona
     proibida perto de uma reentrância do contorno, mesmo com as duas pontas
     legais. Corrigido verificando o segmento inteiro por amostragem
     (`segmentoSeguro`) e subdividindo o ângulo (não aceitando a corda) onde não
     for seguro — refino adaptativo, só onde precisa.
  2. A própria busca binária por raio assume legalidade **monotônica** ao
     longo do raio (uma vez ilegal, nunca mais legal) — falso perto de uma
     reentrância (o raio pode sair da faixa de recuo de uma divisa e reentrar
     na de outra mais adiante). Corrigido trocando por varredura em passos até
     achar a **primeira** falha (garantidamente a mais próxima do centro), só
     então refinando esse último trecho com busca binária.
  Ambos os bugs só apareceram testando um lote em L sintético com reentrância
  perto de onde a torre é centralizada — os lotes "simples" (retângulo, esquina,
  faixa estreita) sempre passaram. **Se mexer nisso de novo, sempre valide por
  ARESTA (amostrando pontos ao longo de cada segmento do polígono resultante),
  nunca só pelos vértices** — um polígono pode ter todo vértice legal e ainda
  assim violar o recuo no meio de uma aresta.
- Perto de uma reentrância bem apertada o raio legal por ângulo pode ter um
  "degrau" quase vertical (uma esquina real do contorno) onde a subdivisão
  adaptativa não converge — bate no limite de profundidade e sobra muita gente
  vértice (chegou a >1000 num teste sintético). Simplificação por remoção seguro
  (`segmentoSeguro` de novo) com limiar de **área do triângulo** (não só
  "seguro", que sozinho colapsa a laje pra um núcleo bem menor que o legal —
  outro bug real: a área após "simplificar" caía abaixo da própria área do
  retângulo original) escala o limiar aos poucos até caber num número razoável
  de vértices; se mesmo assim sobrar complexidade demais (~140+ vértices), a
  rede de segurança final é **manter o retângulo simples** em vez de entregar
  um polígono impraticável — sempre seguro, mesmo no pior caso.
  A área de `ti.area` é sempre `Math.abs(areaAnel(ti.anel))` — casa 100% com o
  polígono desenhado.
- Sobe até a maior altura em que a laje (do tamanho que couber) ainda cabe
  respeitando o recuo no topo — **reduzir o alvo de área ganha altura**; aumentar
  exige altura menor (mesmo mecanismo da laje alvo, ver seção acima).
- Testado com funções puras extraídas (sem browser) em 6 cenários sintéticos:
  testada única sem esquina, lote de esquina, lote estreito forçando deformação,
  o mesmo lote de esquina com alvo menor (trade-off área↔altura), um lote em L
  com reentrância (o cenário que pegou os dois bugs acima), e o mesmo lote em L
  com `soRetangular=true`. Os 6 passam validando **arestas inteiras** (não só
  vértices) contra o recuo, com área reportada == área shoelace do polígono.

## 3D (Three.js r128, `desenhar(s)`)

Extruda o polígono real do lote: base (nBasePav pavimentos até a divisa) + torre
(best.nT pavimentos a partir de best.anel) + wireframe do envelope máximo.

Barra de cima: `#tbMassa`/`#btnPlantas` (troca de visão), `#tgRetangular`
("Laje retangular" — força a torre implantada a não deformar, ver seção acima),
`#tgEnv` (mostra/esconde o wireframe do envelope máximo).

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
   **O tracejado tenta primeiro `recortar()`** (o mesmo recorte por
   meio-planos usado no cálculo do envelope) — é o método CORRETO, bate
   exatamente com a laje desenhada quando não colapsa. Só cai para um
   **offset local por vértice** (miter join com as duas arestas vizinhas, com
   quina chanfrada/bevel se o miter disparar longe demais) quando `recortar()`
   colapsa a zero vértices — lotes bem irregulares, a mesma razão pela qual a
   torre implantada existe.
   **Três rodadas de bug real aqui, cuidado se mexer de novo:**
   1. Cada aresta original desenhava sua própria linha offset independente,
      sem juntar nos cantos ("linhas soltas").
   2. Trocou para `recortar()` global sempre — junta os cantos, mas em lotes
      com "pescoço" estreito colapsa e não desenha tracejado NENHUM (só
      apareceu com um lote em Z real do usuário).
   3. Trocou para offset local sempre — funciona (nunca colapsa), mas o
      miter pode disparar um "bico" quando o recuo é grande e o lote é
      pequeno (o limite do miter era só proporcional ao recuo, não à escala
      do próprio lote — só apareceu com um lote losangular real, recuo
      lateral de 15,8 m num lote de ~30 m).
   **Versão atual = híbrida**: `recortar()` primeiro (correto, e cobre a
   maioria dos lotes — inclusive o losangular do bug 3, resolvendo-o de graça
   por não precisar mais do offset local ali); offset local só como fallback,
   com o limite do miter preso tanto ao recuo quanto a `diagonal do lote × 0,5`
   (nunca mais que a metade da diagonal do próprio lote, resolve o bug 3
   quando o fallback É usado).
   **4º bug real**: numa torre NATURAL (sem torre implantada) que ocupa o
   envelope inteiro, `best.anel` é literalmente o mesmo polígono que o
   tracejado desenha — a linha tracejada cai EM CIMA do contorno sólido da
   torre, numa cor quase igual (azul do tracejado `#6fb2ff` vs azul do
   contorno da torre `#4da3ff`), ficando praticamente invisível. Corrigido
   desenhando um halo de contraste (linha grossa `#0e141b`, cor do fundo)
   atrás de cada segmento tracejado — garante contraste em cima de qualquer
   coisa desenhada embaixo, incluindo a própria torre.
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
- Concluído (2ª rodada, depois que o usuário testou a 1ª num navegador real):
  a laje deformada da torre implantada podia cortar por dentro do recuo perto
  de reentrâncias (dois bugs na busca radial, ver seção "Torre implantada" —
  corrigido com verificação por ARESTA inteira, não só vértice, mais rede de
  segurança que volta pro retângulo se a forma ficar complexa demais); o
  tracejado de recuo tinha voltado a quebrar (virava um "bico" gigante) num
  lote losangular simples — virou híbrido, `recortar()` primeiro (correto) e
  offset local só de fallback, com limite de miter preso à escala do lote;
  novo botão `#tgRetangular` ("Laje retangular") força a torre implantada a
  nunca deformar, sempre o maior retângulo que couber.
- Concluído (3ª rodada, dois bugs vistos pelo usuário num lote real): o
  gatilho da torre implantada só olhava a MAIOR laje entre todos os
  pavimentos, não a do pavimento efetivamente ESCOLHIDO — num lote onde a
  laje encolhe bastante no pavimento mais alto, o gatilho nunca disparava e
  o botão "Laje retangular" parecia não ter efeito (corrigido, ver seção
  "Torre implantada"); e o tracejado ficava invisível numa torre NATURAL que
  ocupa o envelope inteiro, por cair exatamente em cima do contorno sólido
  da torre numa cor quase igual — corrigido com um halo de contraste atrás
  do tracejado (ver seção "Plantas").
- Concluído (4ª rodada, mudança de escopo pedida explicitamente pelo
  usuário): o campo de área-alvo (renomeado `#ovLajeImplant` → `#ovLajeAlvo`,
  "Laje alvo") deixou de valer só para a torre implantada — agora rege
  também a torre natural, sempre (não mais atrás do checkbox "Respeitar a
  área de laje alvo", que foi removido, nem via unidades×privativa). O campo
  "Unidades por pavimento" (`uniPav`) também foi removido — ficou órfão
  depois que `lajeDesejada` passou a vir direto de `#ovLajeAlvo` em m², não
  mais de `uniPav × m2Uni ÷ fator`. Ver seção "Laje alvo".
- Em aberto (do lado do usuário): conferência pontual de ~17,5% de divergência de
  ZOT contra uma camada externa; conferência do visual final sobre o basemap CARTO
  ao vivo; **validação em navegador real** da 2ª, 3ª e 4ª rodadas de correções (só
  foi possível testar a geometria pura/lógica extraída nesta sessão — ver
  limitação de ambiente na seção de Testes).
- Ideia futura: agrupar faces colineares numa medida só, para lotes de contorno
  muito ruidoso (evita rótulos minúsculos espremidos).
