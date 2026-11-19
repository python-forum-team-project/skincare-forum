from fastapi import APIRouter
from services.stats_service import get_home_stats


home_router = APIRouter(prefix='/home', tags=['Home'])


@home_router.get('/stats', status_code=200)
def home() -> dict:
    return get_home_stats()