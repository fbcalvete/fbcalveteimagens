# Levar o Estudo Volumétrico para o Claude Code

Guia de migração do projeto (`estudo-volumetrico.html`) e do contexto das nossas
conversas para o Claude Code — com os ganhos e as perdas de forma honesta.

---

## O ponto central antes de tudo

Existem **duas coisas** que você pode querer levar, e elas se comportam diferente:

1. **O código** — o arquivo `estudo-volumetrico.html`. Esse migra 100%. É só
   colocar numa pasta.
2. **O "histórico das conversas"** — aqui é preciso separar:
   - O **conhecimento** que geramos (decisões, regras da LUOS, armadilhas, o
     porquê de cada solução): isso migra, **desde que registrado num arquivo**.
     É o que o `CLAUDE.md` (que já preparei) faz.
   - A **transcrição turn-a-turn** desta conversa e a **memória automática** que
     eu mantenho no app: isso **não** atravessa para o Claude Code. Ele é uma
     sessão nova, com outro mecanismo de contexto. Ele não "lembra" do que
     falamos aqui — ele lê os arquivos que estiverem na pasta.

Ou seja: o Claude Code não puxa o histórico sozinho. O histórico vira útil para
ele **na forma de arquivos** que você deixa no projeto. Por isso o `CLAUDE.md`.

---

## Passo a passo da migração

### 1. Instalar o Claude Code
Requer Node.js recente. No terminal:
```
npm install -g @anthropic-ai/claude-code
```
(Confirme o comando e os requisitos atuais em https://docs.claude.com — a forma
de instalar pode ter mudado desde que este guia foi escrito.)

### 2. Criar a pasta do projeto
```
mkdir estudo-volumetrico
cd estudo-volumetrico
```
Copie para dentro dela:
- `estudo-volumetrico.html`  (o programa)
- `CLAUDE.md`                (o contexto do projeto — arquivo que preparei)

### 3. (Recomendado) Versionar com git
Assim você nunca mais perde uma versão boa — e resolve de vez a armadilha das
"duas cópias" que nos atrapalhou várias vezes:
```
git init
git add estudo-volumetrico.html CLAUDE.md
git commit -m "importa estudo volumetrico + contexto"
```

### 4. Abrir o Claude Code na pasta
```
claude
```
Ele lê o `CLAUDE.md` automaticamente no início da sessão e já entra sabendo o que
é o projeto, quais as regras e onde estão as armadilhas.

### 5. (Opcional) Levar a transcrição como referência
Se quiser que o Claude Code possa consultar o detalhe fino do que fizemos, exporte
esta conversa e salve como `docs/historico.md` na pasta. O Claude Code não lê isso
sozinho, mas você pode apontar: "leia `docs/historico.md` antes de mexer no cálculo
de recuo". É um anexo de consulta, não uma memória viva.

---

## Ganhos de ir para o Claude Code

- **Arquivos de verdade, versionados.** Fim das "duas cópias" (scratch × output)
  que reintroduziram bugs aqui. Com git, cada mudança é um commit reversível.
- **Trabalha direto no seu ambiente.** Ele edita o arquivo na sua máquina, roda
  comandos, instala dependências, executa testes — sem o vaivém de copiar e colar.
- **Testes de verdade no seu setup.** Dá para deixar o Puppeteer instalado de forma
  persistente e rodar a suíte de regressão quando quiser, sem reinstalar a cada vez
  (aqui o ambiente reseta entre tarefas e eu reinstalo o Chrome toda hora).
- **Iteração mais rápida em código grande.** O arquivo já passou de 800 KB. O
  Claude Code lida melhor com edições cirúrgicas em arquivos grandes e com dividir
  o projeto em vários arquivos, se você quiser modularizar.
- **Contexto do projeto que persiste.** O `CLAUDE.md` fica na pasta e vale para
  toda sessão futura — não depende de eu "lembrar".
- **Integra com o seu fluxo.** Terminal, editor (VS Code / JetBrains), CI, scripts.

## Perdas / custos de ir para o Claude Code

- **A memória automática não vai junto.** O arquivo de contexto que mantenho de
  você (Melnick, seus projetos, preferências) fica neste app. No Claude Code, o
  contexto é só o que estiver nos arquivos da pasta.
- **O histórico turn-a-turn não migra como conversa.** Vira um anexo estático
  (`historico.md`) que você precisa apontar, não uma continuidade automática.
- **É uma ferramenta de desenvolvedor.** Exige terminal, Node, git. Tem curva de
  aprendizado se você não vive nesse ambiente. Aqui no chat é mais direto para
  pedir e ver o resultado.
- **Sem o mapa / a visualização integrada do chat.** Aqui eu te mostro capturas e
  a gente conversa sobre elas. No Claude Code o loop visual é você abrir o HTML no
  navegador e reportar o que vê (o programa em si funciona igual — é um HTML
  standalone, roda em qualquer navegador).
- **Uso e limites são de outra natureza.** Claude Code consome de acordo com o seu
  plano/uso de API; vale conferir em https://docs.claude.com como isso se aplica ao
  seu caso.

---

## Recomendação prática

Para **este** projeto (um HTML único, já maduro, com suíte de testes e várias
armadilhas conhecidas), o Claude Code é um bom lar: git elimina o problema das
cópias, os testes ficam persistentes e o `CLAUDE.md` carrega o conhecimento.

O que você perde — a memória automática e a continuidade da conversa — dá para
mitigar com os dois arquivos deste pacote (`CLAUDE.md` + `historico.md` opcional).

Sugestão de meio-termo: mantenha o **código e a evolução técnica no Claude Code
com git**, e continue usando **este chat** quando quiser discutir de forma mais
visual (analisar uma captura, decidir uma regra da LUOS, ver o 3D). As duas coisas
convivem — o HTML é o mesmo arquivo nos dois lugares.

---

## Checklist rápido

- [ ] Node.js instalado
- [ ] `npm install -g @anthropic-ai/claude-code` (confira o comando atual nos docs)
- [ ] Pasta criada com `estudo-volumetrico.html` + `CLAUDE.md`
- [ ] `git init` + primeiro commit
- [ ] `claude` na pasta e confirmar que ele leu o `CLAUDE.md`
- [ ] (opcional) `docs/historico.md` com a transcrição desta conversa
- [ ] (opcional) Puppeteer instalado para a suíte de regressão
