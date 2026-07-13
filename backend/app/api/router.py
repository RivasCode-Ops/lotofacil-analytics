from fastapi import APIRouter

from app.api.routes import analytics, closure, combinations, draws, filters, games, health, rules, score, statistics

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(draws.router)
api_router.include_router(statistics.router)
api_router.include_router(combinations.router)
api_router.include_router(rules.router)
api_router.include_router(filters.router)
api_router.include_router(score.router)
api_router.include_router(games.router)
api_router.include_router(closure.router)
api_router.include_router(analytics.router)
