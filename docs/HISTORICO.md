# Histórico de alterações — Estudo Volumétrico

Linha do tempo destilada das mudanças feitas no `estudo-volumetrico.html`, com o
motivo de cada uma. Serve para o Claude Code (e para você) entenderem *por que* o
código está como está — complementa o `CLAUDE.md`, que descreve o *estado atual*.

> Este arquivo NÃO é lido automaticamente. Aponte para ele quando for mexer em algo
> sensível: "leia HISTORICO.md antes de alterar o cálculo de recuo / a torre
> implantada / as plantas".

---

## 1. Nomes das ruas de frente — de geocodificação para camada oficial
**Problema:** em alguns terrenos a rua de frente não aparecia no 3D.
**Causa:** geocodificava um único ponto ~7 m rua adentro (Nominatim). Falhava em
frentes curtas/esquinas, batia no limite de requisição, e os erros eram engolidos
em silêncio → a rua sumia.
**Solução:** passar a usar a camada oficial de eixos de logradouro da prefeitura
(serviço ArcGIS `eixos`, campo `nmidelog`). Para cada testada, acha o eixo mais
próximo e usa o nome dele. Robusto, sem limite, autoritativo. Abreviações comuns
expandidas (Gen→General, Dr→Doutor, etc.). Nominatim ficou só na busca de endereço.

## 2. Cotas e recuo lateral no 3D
Adicionadas as dimensões do terreno (comprimento de cada lado) e o recuo lateral,
como rótulos deitados no chão.

## 3. Rótulos de rua e cotas se sobrepondo → anti-sobreposição OBB
**Problema:** em lote de esquina os nomes de rua se cruzavam no meio; as cotas se
amontoavam.
**Solução:** em esquina, cada nome ancora no vértice comum e diverge (cada um para
o seu lado). Anti-sobreposição por caixas orientadas (OBB/SAT): nenhum rótulo é
posto onde encoste em outro.
**Lição de teste (importante):** os vértices de `PlaneGeometry` vêm em ordem de
grade [TL,TR,BL,BR]; a ordem de perímetro para SAT é [0,1,3,2]. Usar a ordem errada
dá falso positivo de sobreposição — foi um erro do *teste*, não do código, e me fez
perseguir um problema que não existia. Cuidado ao medir sobreposição.

## 4. Base isenta = 0 quebrava o 3D
**Problema:** ao zerar a altura da base, o modelo 3D ficava errado (bloco achatado).
**Causa:** digitar 0 caía no fallback 12,5 (o código tratava 0 como "vazio").
**Solução:** `ovBase = 0` significa 0 de verdade (sem embasamento, torre do chão);
o 12,5 só vale com o campo vazio.

## 5. Torre implantada em lotes irregulares
**Problema:** em terrenos de formato variado, os recuos inviabilizavam a torre
(laje ~0) e não se colocava nada.
**Solução:** quando a torre natural é inviável, o programa "reparte o terreno":
insere um retângulo compacto (~600 m²) na parte larga do lote voltada para a
frontagem, sem ocupar toda a base.

### 5a. …mas precisava respeitar o recuo lateral
**Correção:** a torre implantada passou a respeitar o recuo lateral da regra
(18% da altura, ou 15% se testada < 20 m).
**Descoberta técnica:** o envelope natural dava laje 0 mesmo com recuo pequeno
porque o lote tinha 22–46 vértices — o recorte por semiplanos (`recortar`) colapsa
o polígono (slivering). A torre implantada NÃO pode usar esse recorte; passou a
checar o recuo por **distância de cada canto/meio de aresta a cada divisa**
(robusto ao ruído do contorno). Sobe até a maior altura em que a laje ainda cabe.

### 5b. …e precisava cair na parte certa do lote
**Problema (lote em L, 46 vértices):** a torre caía no vértice reentrante, numa
faixa fina, porque a "maior frente" detectada tinha só 11 m (a frontagem estava
fragmentada em muitas arestas curtas).
**Solução:** trocar a ancoragem na maior aresta única por uma **busca em grade**
pela maior posição do retângulo, com orientação vinda da direção média das frentes.
Passou a cair na parte larga do corpo, junto à frontagem principal.

## 6. Plantas (situação + corte) — página "Ver Plantas"
Botão na etapa 3D abre uma página com duas plantas SVG, sempre geradas do
`resolver()` do momento (refletem o modelo atual):
- **Situação:** SEMPRE com o norte para cima; medida de cada face do terreno,
  empreendimento sobreposto, medidas da laje.
- **Corte:** altura atingida (cota), embasamento, torre recuada, subsolos, resumo.
Ajustes de layout: rótulos com anti-sobreposição (medidas das faces têm prioridade;
laje só quando distinta do terreno); usar o `hMax` efetivo no corte (antes mostrava
"de 0 m" quando o dado de altura da ZOT vinha zerado).

## 7. Recuos claros na planta de situação (como no modelo de referência)
**Problema:** não estava claro qual a distância de cada recuo.
**Solução:** linhas de eixo tracejadas (dash-dot) paralelas às faces, deslocadas
para dentro pela distância do afastamento — âmbar (recuo de jardim) e azul (recuo
lateral), na paleta do programa. Valor cotado uma vez por tipo (maior frente e
maior divisa) para não poluir em lotes de muitos vértices. Medidas das faces têm
prioridade na colisão.

## 8. Correções na planta de situação e na torre implantada (primeira rodada no Claude Code)
A partir de um print de uma planta real, três problemas foram reportados de uma vez:

**Recuo lateral com "linhas soltas" na planta de situação.** O tracejado de
recuo desenhava, para cada aresta ORIGINAL do terreno, sua própria linha
deslocada para dentro — sem juntar com a linha da aresta vizinha. Em cantos
(principalmente do lado da divisa, com várias arestas em sequência) isso
deixava segmentos desconectados. **Correção:** passou a desenhar o contorno
único que sai de `recortar(anel, recuos)` — a mesma função de recorte por
meio-planos já usada para calcular o envelope da torre — em vez de segmentos
independentes. Como é um único array de vértices ordenado, os cantos
compartilham vértice automaticamente. A cor de cada segmento (âmbar/jardim ou
azul/lateral) é decidida por distância perpendicular à reta de offset original
mais próxima.

**Área da laje divergente entre a planta e o texto.** A causa: `lajeReal` (usada
em toda a UI, na planta e no corte) era calculada como `best.acTorre/best.nT` —
uma MÉDIA da área computável ao longo dos pavimentos, que cai sempre que o CA
satura antes do último pavimento ou a torre afunila com a altura (cada nível
tem um envelope diferente, mais apertado no topo). Mas o polígono DESENHADO
(`best.anel`) sempre foi a área do pavimento mais alto (`best.laje`), o mais
restritivo — daí a divergência real vista no print (planta mostrando uma laje
maior que o número escrito). **Correção:** `lajeReal = best.laje` sempre, que é
por construção a área shoelace do próprio `best.anel` em todos os três casos
(torre natural, implantada, ou só a base) — 100% consistente com o desenho.

**Torre implantada: reposicionamento completo.** O algoritmo antigo buscava em
grade (varria centros x alturas) a posição de maior score, sem garantia de ficar
na testada principal nem de encostar no recuo de jardim. Reescrito para:
- Agrupar as arestas `frente` contíguas do anel (com wraparound) e escolher o
  grupo de maior comprimento total = a testada principal.
- Detectar esquina (mudança de direção > 25° dentro do grupo) — se houver,
  ancora no vértice da esquina; senão, no ponto médio do comprimento acumulado
  da testada (não a corda reta, para testadas com leve curvatura).
- Área-alvo virou parâmetro editável (`#ovLajeImplant`, default 600 m²) em vez
  de constante fixa no código.
- Retângulo sempre começa quadrado e encostado no recuo de jardim; encolhe
  mantendo a proporção até respeitar o recuo lateral; se ainda faltar área para
  o alvo, DEFORMA por busca radial (64 raios, busca binária por ponto) a partir
  do centro do melhor retângulo, seguindo o contorno legal real — depois escala
  de volta ao alvo se sobrar espaço.
- **Bug pego só depois de testar com um lote de esquina sintético:** a primeira
  versão do código de esquina centralizava a laje simetricamente sobre o vértice,
  jogando metade dela para fora do lote. A correção seguinte respeitava o recuo
  da frente de referência mas colava a laje em cima da OUTRA frente (a que faz
  esquina) — porque só afastava `rj` na direção de profundidade, não na de
  largura. Fórmula final desloca o centro por `rj + W/2` na largura E `rj + D/2`
  na profundidade, a partir do vértice — a laje fica a `rj` de QUALQUER uma das
  duas frentes da esquina.

**Sobre o teste desta rodada:** o Puppeteer/Playwright headless não conseguiu
completar handshake TLS com NENHUM host externo (nem CDN, nem o ArcGIS da
prefeitura) neste ambiente — o `curl` com o mesmo proxy funcionava normalmente,
então não é allowlist; o RESET acontecia a meio do TLS mesmo em hosts sem
proxy. Sem conseguir abrir o app no navegador de verdade, a validação foi feita
extraindo as funções de geometria puras (`torreImplantada`, `recortar`,
`pontoNoPoligono`, `areaAnel`, `distPtSeg` — nenhuma delas toca DOM) para um
módulo Node isolado e testando com lotes sintéticos (retângulo com testada
única, lote de esquina, lote estreito forçando deformação, e o mesmo lote de
esquina com alvo menor para confirmar o trade-off área↔altura). Os 4 cenários
passaram: área reportada bate exatamente com a área shoelace do polígono
desenhado, e todo vértice respeita `rj`/recuo lateral. **Falta a validação
visual num navegador real com o mapa e o ArcGIS ao vivo** — pendência do lado
do usuário ou de uma sessão sem essa restrição de proxy.

---

## Armadilhas recorrentes (não repetir)

- **Duas cópias do HTML** (trabalho × entregável): um `cp` errado reintroduzia
  código morto/apagava edições. Com git isso some — trabalhe num arquivo só e
  confie no diff.
- **Ambiente que reseta:** aqui o container apagava node_modules/Chrome entre
  tarefas, exigindo reinstalar o Puppeteer toda vez. No seu ambiente, deixe o
  Puppeteer instalado de forma persistente.
- **Ler screenshot de headless:** o basemap CARTO não renderiza em headless (fundo
  escuro). Valide por medição numérica, não por leitura da imagem.
- **Chromium headless sem HTTPS neste tipo de ambiente (Claude Code on the web):**
  o Playwright/Puppeteer não completa handshake TLS com host externo nenhum
  através do proxy do agente (RESET a meio do TLS; `curl` com o mesmo proxy
  funciona). Ver detalhe no CLAUDE.md, seção Testes. Nessas sessões, teste a
  geometria pura em Node isolado (sem DOM) em vez de insistir em abrir o browser.

## Pendências conhecidas

- Conferência pontual (do seu lado) de ~17,5% de divergência de ZOT contra uma
  camada externa.
- Conferência do visual final sobre o basemap CARTO ao vivo.
- Validação em navegador real da rodada de correções do item 8 (recuo na planta,
  laje física, torre implantada reancorada) — só testada com geometria pura nesta
  sessão, por causa da restrição de proxy/Chromium acima.
- Melhoria futura: agrupar faces colineares numa medida só na planta de situação,
  para lotes de contorno muito ruidoso.
