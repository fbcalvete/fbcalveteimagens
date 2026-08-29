# Configuração & Manutenção da Routine

## Identificação
- **Routine ID:** `trig_01TwnhMXTyoMKQUGC8D4i3WH`
- **Nome:** `Agente Aéreo & Pontos (08h/20h BRT)`
- **Disparo:** cria uma sessão nova a cada firing (`create_new_session_on_fire`).
- **Agenda (cron, UTC):** `0 11,23 * * *` → 08:00 e 20:00 de Brasília (UTC−3).
- **Prompt executado:** ver [`PROMPT.md`](PROMPT.md) (é o texto standalone da Routine).

## ⚠️ Passo manual necessário: anexar o Gmail à Routine
As sessões disparadas por esta Routine **não herdam automaticamente o conector
do Gmail** nesta organização — logo, sem o passo abaixo o agente pesquisa mas
**não envia o e-mail**.

Para habilitar o envio:
1. Acesse **claude.ai → Settings/Configurações → Routines** (ou a lista de
   Rotinas/agendamentos).
2. Abra a rotina **"Agente Aéreo & Pontos (08h/20h BRT)"**.
3. Em conectores/integrações da rotina, **habilite o Gmail** e salve.

Depois disso, o agente passa a mandar e-mail para `fbcalvete@gmail.com` sempre
que um critério for satisfeito.

> Alternativa: recriar a rotina diretamente pela interface de Rotinas da
> claude.ai (colando o prompt de `PROMPT.md`, cron `0 11,23 * * *`) já com o
> Gmail anexado.

## Critérios de alerta
- **Pontos pra Voar:** alguma loja de varejo/eletro pagando **≥ 8 pontos/real**
  em promoção **vigente**.
- **MaxMilhas:** passagem POA↔RIO, ida 04/02/2027, volta 10/02/2027, ida e volta,
  total **< R$ 1.000**.
- **Sem critério satisfeito → nenhum e-mail.**

## Como alterar
Use as ferramentas de Routine (ou a interface da claude.ai):
- **Mudar horários:** editar `cron_expression`. Lembre de converter para UTC
  (Brasília = UTC−3; some 3 horas). Ex.: 07:00 e 19:00 BRT → `0 10,22 * * *`.
- **Mudar critérios/datas/lojas:** editar o `prompt` da Routine **e** o
  [`PROMPT.md`](PROMPT.md) para manter os dois em sincronia.
- **Pausar:** desabilitar a Routine (`enabled = false`).
- **Testar agora:** disparar a Routine manualmente (fire) para ver uma rodada.

## Reduzir e-mails repetidos (opcional)
Como a checagem é a cada 12h, uma promoção que fique dias ≥8 pts/real pode gerar
alerta em toda rodada. Para evitar, seria preciso o agente guardar estado entre
execuções (ex.: só alertar quando uma condição *nova* aparecer). Cada firing é
uma sessão limpa e sem memória, então isso exigiria uma fonte de estado externa
(um arquivo no repositório, uma planilha, etc.). Não implementado por padrão —
peça se quiser.
