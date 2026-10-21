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

- **Programas válidos:** **somente Livelo e Esfera** (demais programas são ignorados).
- **Gatilho de alerta:** alguma loja pagando **≥ 8 pontos por real** em Livelo ou Esfera.
- **No e-mail:** loja, programa (Livelo/Esfera), quantos pontos por real e o link da promoção.

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
| Horizonte | ida entre **40 e 140 dias** a partir de hoje (pega o fim de semana mais barato) |

- **Gatilho de alerta:** total ida+volta **< R$ 500**.
- **No e-mail:** datas exatas (sexta/segunda), preço, companhia, horários e link.

### Regra dos voos (Verificações 2 e 3)
O agente consulta Google Flights, Kayak, Skyscanner, MaxMilhas/Decolar, sites
das cias e blogs de promoção, e usa o menor total ida+volta. **Aceita preços não
confirmados** (data próxima, "a partir de", horário desconhecido): alerta assim
mesmo, marcando `[a confirmar]` e dizendo o que conferir. **A confirmação final é
manual.** Preços da data exata vêm marcados `[confirmado]`.

### Anti-repetição
Antes de enviar, o agente lê no Gmail os alertas dos últimos 7 dias e descarta
o que já foi avisado. Só reenvia se a oferta **melhorar** (mais pontos/real ou
preço pelo menos R$ 30 menor).

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
- **Sem repetição.** O mesmo alerta não chega duas vezes em 7 dias, a menos que
  a oferta melhore.
- **Alertas de voo podem vir "a confirmar".** Os sites de passagem são dinâmicos;
  o agente prefere avisar com um preço indicativo a ficar em silêncio. Confira
  no link antes de comprar.
