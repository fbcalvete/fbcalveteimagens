# Agente de Aéreo & Pontos

Agente de IA que roda **automaticamente 2x por dia** (08:00 e 20:00, horário de
Brasília) e faz duas verificações. Ele **só envia e-mail** para
`fbcalvete@gmail.com` quando alguma das condições abaixo for satisfeita — em
silêncio no resto do tempo.

## O que ele monitora

### 1. Pontos em compras de varejo — site [Pontos pra Voar](https://pontospravoar.com)
Procura promoções **vigentes** de acúmulo de pontos em lojas de varejo e
eletrodomésticos (Casas Bahia, Ponto, Fast Shop, Magazine Luiza/Magalu, Amazon,
Mercado Livre, Extra, etc.).

- **Gatilho de alerta:** alguma loja pagando **≥ 8 pontos por real**.
- **No e-mail:** loja, programa de fidelidade (Livelo, Esfera, Azul Fidelidade,
  TudoAzul, LATAM Pass, Smiles…), quantos pontos por real e o link da promoção.

### 2. Passagem de Carnaval 2027 — site [MaxMilhas](https://www.maxmilhas.com.br)
Monitora uma passagem específica:

| Campo | Valor |
|---|---|
| Origem | Porto Alegre (POA) |
| Destino | Rio de Janeiro (RIO — GIG/SDU) |
| Ida | quinta-feira, **04/02/2027** |
| Volta | quarta-feira, **10/02/2027** |
| Tipo | ida e volta |

- **Gatilho de alerta:** total ida+volta **< R$ 1.000**.
- **No e-mail:** preço encontrado, companhia/horários (se disponível) e o link.

### 3. Fim de semana POA ↔ São Paulo/Congonhas (CGH)
Monitora um fim de semana **em qualquer data**, desde que seja sempre um par
**sexta → segunda seguinte** (3 noites):

| Campo | Valor |
|---|---|
| Origem | Porto Alegre (POA) |
| Destino | São Paulo / Congonhas (CGH) |
| Ida | uma **sexta-feira**, voo partindo **a partir das 17h** |
| Volta | a **segunda-feira** seguinte, voo partindo **até ~08h** |
| Tipo | ida e volta |
| Horizonte | próximos ~60 dias (varre os fins de semana e pega o mais barato) |

- **Gatilho de alerta:** total ida+volta **< R$ 500**.
- **No e-mail:** datas exatas (sexta/segunda), preço, companhia, horários e link.

### Regra dos voos (Verificações 2 e 3)
Para passagens, o agente consulta **MaxMilhas, Skyscanner e Google Flights** e
repassa os preços que encontrar (indicando a fonte) — sem travar por "fonte
confiável". Usa o menor preço para comparar com o critério.

## Como está montado

- **Mecanismo:** uma *Routine* (agendamento recorrente do Claude Code) dispara
  uma sessão nova do agente a cada 12 horas.
- **Agenda (cron, UTC):** `0 11,23 * * *` — equivale a 08:00 e 20:00 de Brasília
  (UTC−3).
- **Envio de e-mail:** conector **Gmail** já autenticado na conta, remetente
  `fbcalvete@gmail.com`.
- **Instruções do agente:** [`Prompt Base.md`](agente%20de%20passagens%20e%20pontos/Prompt%20Base.md)
  — exatamente o texto que a Routine executa a cada disparo.
- **Detalhes de config e manutenção:** [`CONFIG.md`](agente%20de%20passagens%20e%20pontos/CONFIG.md).

## Importante saber

- **Sem novidade = sem e-mail.** Se nada bater o critério, o agente encerra sem
  mandar nada. Você não recebe "relatório de que não há nada".
- **Enquanto a condição durar, o alerta pode repetir.** Como a verificação é a
  cada 12h, uma promoção que fique dias pagando ≥8 pts/real pode gerar e-mail em
  cada rodada. Veja em [`CONFIG.md`](agente%20de%20passagens%20e%20pontos/CONFIG.md) como reduzir repetição.
- **MaxMilhas é um site dinâmico.** O preço é carregado via JavaScript; o agente
  tenta ler a página de resultados e, quando não consegue o valor exato, usa
  busca/《fontes alternativas》e só alerta com um preço confiável abaixo de R$1.000.
