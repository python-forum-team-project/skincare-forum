from fastapi import APIRouter
from services import stats_service

stats_router = APIRouter(prefix='/stats', tags=['Stats'])


@stats_router.get('/home')
def home_stats():
    return stats_service.get_home_stats()


@stats_router.get('/recent-topics')
def recent_topics():
    return stats_service.get_recent_topics()


@stats_router.get('/top-topics')
def top_topics():
    return stats_service.get_topics_by_replies()