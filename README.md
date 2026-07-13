# Lotofácil Analytics

Sistema de análise e geração de jogos da Lotofácil.

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

**Postgres (Supabase):** projeto `lotofacil` criado (org RivasCode-Ops's Org, `sa-east-1`, US$ 10/mês, ref `efdfggiearsnpzyjrith`). Pegue a senha do banco em https://supabase.com/dashboard/project/efdfggiearsnpzyjrith/settings/database e coloque em `backend/.env` (veja `backend/.env.example`) — as tabelas são criadas automaticamente no primeiro start (`Base.metadata.create_all`).

**Backend (Render):**
1. Suba este repositório pro GitHub.
2. No Render, "New > Web Service" apontando pro repo — ele detecta o `render.yaml` (usa `backend/Dockerfile`).
3. Configure as env vars `DATABASE_URL` (a do Supabase acima) e `CORS_ORIGINS` (a URL do frontend na Vercel, depois do passo seguinte).
4. Depois do primeiro deploy, chame `POST /api/draws/update` uma vez pra popular o banco.

**Frontend (Vercel):**
1. Import do repositório, root directory = `frontend`.
2. Framework preset: Vite.
3. Env var `VITE_API_URL` = URL pública do backend no Render (ex: `https://lotofacil-backend.onrender.com`).
4. Depois do deploy, volte no Render e ajuste `CORS_ORIGINS` pra URL da Vercel.

**Pendente:** push pro GitHub (repo local ainda não tem remote) e a criação das contas/projetos no Render e na Vercel — isso precisa ser feito por você, eu não tenho acesso a essas plataformas.

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
