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

## Como está montado

- **Mecanismo:** uma *Routine* (agendamento recorrente do Claude Code) dispara
  uma sessão nova do agente a cada 12 horas.
- **Agenda (cron, UTC):** `0 11,23 * * *` — equivale a 08:00 e 20:00 de Brasília
  (UTC−3).
- **Envio de e-mail:** conector **Gmail** já autenticado na conta, remetente
  `fbcalvete@gmail.com`.
- **Instruções do agente:** [`agente/PROMPT.md`](agente/PROMPT.md) — é
  exatamente o texto que a Routine executa a cada disparo.
- **Detalhes de config e manutenção:** [`agente/CONFIG.md`](agente/CONFIG.md).

## Importante saber

- **Sem novidade = sem e-mail.** Se nada bater o critério, o agente encerra sem
  mandar nada. Você não recebe "relatório de que não há nada".
- **Enquanto a condição durar, o alerta pode repetir.** Como a verificação é a
  cada 12h, uma promoção que fique dias pagando ≥8 pts/real pode gerar e-mail em
  cada rodada. Veja em [`CONFIG.md`](agente/CONFIG.md) como reduzir repetição.
- **MaxMilhas é um site dinâmico.** O preço é carregado via JavaScript; o agente
  tenta ler a página de resultados e, quando não consegue o valor exato, usa
  busca/《fontes alternativas》e só alerta com um preço confiável abaixo de R$1.000.
