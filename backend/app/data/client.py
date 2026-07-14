import concurrent.futures

import httpx

CAIXA_LATEST_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/"
CAIXA_CONTEST_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/{contest}"
MIRROR_LATEST_URL = "https://loteriascaixa-api.herokuapp.com/api/lotofacil/latest"
MIRROR_CONTEST_URL = "https://loteriascaixa-api.herokuapp.com/api/lotofacil/{contest}"
HISTORY_URL = "https://raw.githubusercontent.com/guilhermeasn/loteria.json/master/data/lotofacil.json"

HEADERS = {"Accept": "application/json", "User-Agent": "lotofacil-analytics/0.1"}


class DataSourceError(Exception):
    pass


def _normalize_caixa_payload(payload: dict) -> dict:
    numbers = sorted(int(n) for n in payload["listaDezenas"])
    return {
        "contest": payload["numero"],
        "draw_date": payload.get("dataApuracao"),
        "numbers": numbers,
    }


def _normalize_mirror_payload(payload: dict) -> dict:
    numbers = sorted(int(n) for n in payload["dezenas"])
    return {
        "contest": payload["concurso"],
        "draw_date": payload.get("data"),
        "numbers": numbers,
    }


def fetch_latest_draw() -> dict:
    """Concurso mais recente. Tenta a API oficial da Caixa primeiro; ela
    bloqueia (403) requisições de fora do Brasil / IPs de datacenter (ex: o
    Render), então cai pro mirror `loteriascaixa-api` nesses casos."""
    try:
        resp = httpx.get(CAIXA_LATEST_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return _normalize_caixa_payload(resp.json())
    except httpx.HTTPError:
        pass

    try:
        resp = httpx.get(MIRROR_LATEST_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise DataSourceError(f"falha ao buscar concurso mais recente: {exc}") from exc
    return _normalize_mirror_payload(resp.json())


def fetch_draw_by_contest(contest: int) -> dict:
    """Concurso específico. Mesma lógica de fallback de `fetch_latest_draw`."""
    try:
        resp = httpx.get(CAIXA_CONTEST_URL.format(contest=contest), headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return _normalize_caixa_payload(resp.json())
    except httpx.HTTPError:
        pass

    try:
        resp = httpx.get(MIRROR_CONTEST_URL.format(contest=contest), headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise DataSourceError(f"falha ao buscar concurso {contest}: {exc}") from exc
    return _normalize_mirror_payload(resp.json())


def fetch_history() -> dict[str, list[str]]:
    """Histórico completo em lote (guilhermeasn/loteria.json). Útil para carga
    profunda de concursos antigos (imutáveis); NÃO usar para concursos recentes —
    o arquivo pode ficar meses atrasado em relação à API oficial."""
    try:
        resp = httpx.get(HISTORY_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise DataSourceError(f"falha ao buscar histórico: {exc}") from exc
    return resp.json()


def fetch_results(last_n: int = 50) -> list[dict]:
    """Últimos `last_n` concursos, direto da API oficial da Caixa (um request por
    concurso, em paralelo). Concursos individuais que falharem são ignorados."""
    latest = fetch_latest_draw()
    start = max(1, latest["contest"] - last_n + 1)
    remaining = range(start, latest["contest"])

    results = {latest["contest"]: latest}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch_draw_by_contest, c): c for c in remaining}
        for future in concurrent.futures.as_completed(futures):
            contest = futures[future]
            try:
                results[contest] = future.result()
            except DataSourceError:
                continue

    return [results[c] for c in sorted(results.keys())]
