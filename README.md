# Lotofácil Analytics

Sistema de análise e geração de jogos da Lotofácil.

**No ar:** [lotofacil-analytics.vercel.app](https://lotofacil-analytics.vercel.app) — testado ponta a ponta (Dashboard, Gerar Jogos, Resultados) contra dados reais.

Stack: FastAPI (backend) + React/Tailwind (frontend) + PostgreSQL.

## Estrutura

```
backend/app/
  core/       configuração e conexão com banco
  data/       modelos e coleta de dados (concursos)
  engine/     motor de regras
  filters/    filtros eliminatórios
  scoring/    pontuação dos jogos
  generator/  geração de jogos
  closure/    fechamentos (18/19/20 números -> combinações de 15)
  analytics/  comparação com resultados reais
  api/        rotas FastAPI
frontend/src/
  components/ pages/ hooks/ services/
```

## Rodando localmente

Backend:
```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # ajustar DATABASE_URL
uvicorn app.main:app --reload --port 8001
```

Frontend:
```
cd frontend
npm install
npm run dev
```

## Fonte de dados (Etapa 2)

- `fetch_latest_draw()` / `fetch_draw_by_contest()` — API oficial da Caixa (`servicebus2.caixa.gov.br`), direto, sem chave.
- `fetch_results(last_n)` — busca os últimos N concursos direto na API oficial, em paralelo (1 request por concurso). **Não** usa mais o arquivo `guilhermeasn/loteria.json` para concursos recentes: testei e ele está travado no concurso 3246 (a automação do repositório parou), enquanto o concurso atual é 3733. `fetch_history()` continua disponível só para eventual carga de concursos antigos/imutáveis.
- `POST /api/draws/update` grava no banco (upsert, idempotente); `GET /api/draws/last` e `GET /api/draws` leem do banco.
- Dev local sem Postgres instalado: `backend/.env` está apontando para `sqlite:///./dev.db` (arquivo `dev.db`, ignorado no git) só para testes.

## Deploy

**Postgres (Supabase):** projeto `lotofacil` criado e em uso (org RivasCode-Ops's Org, `sa-east-1`, US$ 10/mês, ref `efdfggiearsnpzyjrith`). `backend/.env` já está apontando pra ele via **Session Pooler** (`aws-1-sa-east-1.pooler.supabase.com:5432`) — a conexão direta (`db.efdfggiearsnpzyjrith.supabase.co:5432`) dá timeout porque é IPv6-only e essa rede não tem rota IPv6 pra Supabase. Tabelas criadas automaticamente no startup (`Base.metadata.create_all`); RLS habilitado em `draws` (sem política — bloqueia acesso externo via API REST do Supabase, não afeta a conexão direta do backend). 50 concursos reais (3684–3733) já populados via `POST /api/draws/update`, testado ponta a ponta com o frontend.

**GitHub:** [github.com/RivasCode-Ops/lotofacil-analytics](https://github.com/RivasCode-Ops/lotofacil-analytics) (branch `master`).

**Backend (Render):** no ar em **https://lotofacil-backend-ih3h.onrender.com** — testado (`/api/health`, `/api/draws/last`, `/api/statistics`, `/api/games/generate`), respondendo com os 50 concursos reais do Postgres.
- Serviço `lotofacil-backend`, plano Free (dorme após inatividade — primeira requisição depois de um tempo parado pode levar ~50s).
- **Pegadinha do Render:** o fluxo "New > Web Service" (autodetect) não respeita todos os campos do `render.yaml` — o `dockerContext: ./backend` foi ignorado e o build falhava com `requirements.txt not found`. Corrigido configurando manualmente **Docker Build Context Directory = `backend`** nas settings do serviço no dashboard. Se recriar o serviço do zero, usar o fluxo "New > Blueprint" (que lê o `render.yaml` de verdade) evita esse problema.
- Env vars: `DATABASE_URL` (Session Pooler do Supabase) e `CORS_ORIGINS=http://localhost:5173,https://lotofacil-analytics.vercel.app`.

**Frontend (Vercel):** no ar em **https://lotofacil-analytics.vercel.app** — root directory `frontend`, framework Vite, env var `VITE_API_URL=https://lotofacil-backend-ih3h.onrender.com`. No import, o Vercel sugeriu o preset "Services" (monorepo automático, exigiria `vercel.json` extra) — descartado em favor de configurar o Root Directory manualmente.

**Ciclo fechado e validado:** Supabase (dados reais) → Render (backend) → Vercel (frontend), testado no browser em produção — Dashboard, Gerar Jogos e Resultados funcionando com dados reais, sem erros de console.

## Jogo do dia + conferência automática

- `POST /api/saved-games` salva os jogos gerados (concurso-alvo = último concurso no banco + 1, a não ser que você passe `target_contest` explícito).
- `GET /api/saved-games` lista; `POST /api/saved-games/check` confere os pendentes contra o resultado real (só marca como conferido quando o concurso-alvo já estiver no banco).
- Tela **Meus Jogos** no frontend faz isso pela interface.
- `POST /api/sync` roda `update_database` + `check_saved_games` numa chamada só — pensado pra automação, protegido por header `X-Cron-Secret` (não faz nada se o header não bater com `CRON_SECRET` no `.env`/env var do Render).

**Automação (GitHub Actions):** [.github/workflows/sync-draws.yml](.github/workflows/sync-draws.yml) roda `POST /api/sync` todo dia às 23:30 UTC (20:30 BRT, depois do sorteio), seg-sáb. **Falta configurar 2 coisas manualmente (eu não tenho acesso):**
1. No Render, adicionar a env var `CRON_SECRET` no serviço `lotofacil-backend` (mesmo valor usado no `backend/.env` local).
2. No GitHub, ir em `Settings > Secrets and variables > Actions` do repositório e criar o secret `CRON_SECRET` com o mesmo valor.

Sem isso, o workflow roda mas recebe 401 do backend (a chamada não tem efeito, mas também não quebra nada). Pode disparar manualmente pela aba "Actions" do GitHub (botão "Run workflow") pra testar sem esperar o horário agendado.

## Calibração estatística dos pesos (agente recorrente)

`POST /api/analytics/calibrate` (protegido por `X-Cron-Secret`) roda um backtest: gera milhares de jogos aleatórios contra cada um dos 50 concursos reais e testa correlação de Pearson entre cada critério do score (paridade, faixa, frequência, soma, repetição) e os acertos reais, com correção estatística pra múltiplas comparações. Só ajusta os pesos se achar correlação genuinamente significativa. `GET /api/analytics/weights` expõe o resultado atual; o Dashboard mostra isso com transparência total. [.github/workflows/calibrate.yml](.github/workflows/calibrate.yml) roda isso toda semana (domingo).

**Resultado real (25.000 pontos de amostra):** nenhuma correlação passou de ±0.02, nenhuma significativa. Pesos continuam em 1.0. Isso é o esperado — a Lotofácil é sorteio aleatório independente, sem padrão explorável nos dados históricos.

**Investigação nos repositórios de referência do prompt original:** conferi o que `Mekylei-Belchior/lotofacil`, `luizalaquini/LOTOFACIL-2.0` e `gugapinheiro/lotofacil` realmente fazem. Nenhum prevê números. O primeiro usa "rede neural" no nome mas a IA nunca é conectada a nenhuma previsão (só filtro por frequência histórica); o segundo é estatística descritiva básica (o próprio autor avisa que "não é milagre que vai te fazer ganhar"); o terceiro é só um dump das 3.268.760 combinações possíveis, sem nenhuma pretensão preditiva. Este app já cobre tudo que existe de legítimo nessa categoria (frequência, paridade, fechamentos) e vai além ao testar estatisticamente se algum critério tem correlação real — nenhum outro projeto pesquisado faz isso.

## Status

- [x] Etapa 1 — estrutura inicial
- [x] Etapa 2 — coleta de dados (validado: 50 concursos reais 3684–3733 gravados e lidos)
- [x] Etapa 3 — motor estatístico (`GET /api/statistics`; validado contra valores teóricos esperados)
- [x] Etapa 4 — base de combinações (`generate_combination`, `stream_combinations`, `filter_combination`, `filter_stream`; validado: geração preguiçosa e filtragem progressiva sem materializar as 3,27M combinações)
- [x] Etapa 5 — motor de regras (`validate_ranges`, `validate_parity`, `validate_primes`, `validate_frequency`, `validate_repetition`, `validate_sum`; `POST /api/rules/validate`; validado rejeitando jogo ruim, rejeitando "auto-comparação" óbvia e encontrando jogos 100% válidos por amostragem)
- [x] Etapa 6 — filtros eliminatórios (`has_sequence`, `is_balanced_distribution`, `is_valid_pattern`; `POST /api/filters/validate`; validado isolando sequência vs. distribuição — inclusive achou uma sequência real de 5 consecutivos no concurso 3733 que não era óbvia à primeira vista)
- [x] Etapa 7 — score (`calculate_score`, `rank_games`; `POST /api/score/rank`; validado: jogo válido da Etapa 5 pontuou 81.65 vs. 52.44 do jogo ruim, e ranking de 30 jogos aleatórios saiu corretamente ordenado)
- [x] Etapa 8 — gerador de jogos (`generate_games(n)`; `POST /api/games/generate`; junta Etapas 4+5+6+7. Correção feita durante o teste: a 1ª versão varria `stream_combinations` em ordem lexicográfica e os jogos saíam quase idênticos entre si — pouca diversidade. Troquei para amostragem aleatória independente via `generate_combination`; agora os jogos são de fato diferentes entre si e mais rápido: 0.9s para 5 jogos)
- [x] Etapa 9 — fechamentos (`generate_closure(base_numbers)`; `POST /api/closure/generate`; fechamento fechado/garantido — base de 18/19/20 números gera C(18,15)=816, C(19,15)=3876 ou C(20,15)=15504 jogos. Validado: contagens batem exatamente, e a garantia matemática foi confirmada — se os 15 números sorteados estão dentro da base, exatamente 1 jogo do fechamento crava os 15 pontos)
- [x] Etapa 10 — analytics (`calculate_hits`, `evaluate_performance`; `POST /api/analytics/evaluate`; validado com caso sintético incluindo o mínimo teórico de acertos possível (5, por princípio da casa dos pombos) e ponta a ponta gerando 5 jogos reais e avaliando contra o concurso 3733)
- [x] Etapa 11 — interface (React Router com 3 telas: Dashboard com gráfico de frequência + cards de estatísticas, Gerar Jogos, Resultados com bolinhas numeradas + score + critérios; validado no browser ponta a ponta — gerou 5 jogos reais e navegou automaticamente para os resultados, sem erros no console)
