# Configuração & Manutenção da Routine

## Identificação
- **Routine ID:** `trig_01TwnhMXTyoMKQUGC8D4i3WH`
- **Nome:** `Agente Aéreo & Pontos (08h/20h BRT)`
- **Disparo:** cria uma sessão nova a cada firing (`create_new_session_on_fire`).
- **Agenda (cron, UTC):** `0 11,23 * * *` → 08:00 e 20:00 de Brasília (UTC−3).
- **Prompt executado:** ver [`Prompt Base.md`](Prompt%20Base.md) (é o texto standalone da Routine).

## Gmail (envio de e-mail) — JÁ CONECTADO ✅
O conector **Gmail já está anexado à Routine** (`mcp_connections: Gmail`), então
as sessões disparadas conseguem enviar e-mail para `fbcalvete@gmail.com` quando
algum critério é satisfeito. Se algum dia o envio parar de funcionar, reanexe o
Gmail em **claude.ai → Routines → "Agente Aéreo & Pontos (08h/20h BRT)"**.

## Critérios de alerta
- **Pontos pra Voar:** alguma loja de varejo/eletro pagando **≥ 8 pontos/real**
  em promoção **vigente**, **somente nos programas Livelo e Esfera**.
- **Passagem Carnaval:** POA↔RIO, ida 04/02/2027, volta 10/02/2027, ida e volta,
  total **< R$ 1.000**.
- **Fim de semana POA↔CGH:** qualquer par sexta (voo ≥17h) → segunda seguinte
  (voo até ~08h), ida entre **40 e 140 dias** a partir de hoje, total **< R$ 500**.
- **Voos:** Google Flights → Kayak → Skyscanner → MaxMilhas/Decolar/cias/blogs;
  menor total ida+volta. Aceita preço sem horário/cia (marca `[a confirmar]`),
  mas só das datas pedidas — página genérica da rota/"a partir de" não vale.
- **Sem critério satisfeito → nenhum e-mail.**

## Como alterar
Use as ferramentas de Routine (ou a interface da claude.ai):
- **Mudar horários:** editar `cron_expression`. Lembre de converter para UTC
  (Brasília = UTC−3; some 3 horas). Ex.: 07:00 e 19:00 BRT → `0 10,22 * * *`.
- **Mudar critérios/datas/lojas:** editar o `prompt` da Routine **e** o
  [`Prompt Base.md`](Prompt%20Base.md) para manter os dois em sincronia.
- **Pausar:** desabilitar a Routine (`enabled = false`).
- **Testar agora:** disparar a Routine manualmente (fire) para ver uma rodada.

## Anti-repetição (implementado)
O Gmail é usado como memória: antes de enviar, o agente busca
`to:fbcalvete@gmail.com subject:Alerta newer_than:7d` e descarta alertas já
enviados com a mesma chave (pontos: loja + programa + pts/real + validade; voo:
rota + datas, salvo se o preço cair ≥ R$ 30). Para mudar a janela, troque
`newer_than:7d` no prompt.
