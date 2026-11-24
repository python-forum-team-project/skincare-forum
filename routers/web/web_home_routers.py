from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.stats_service import get_home_stats, get_recent_topics, get_topics_by_replies
from common.auth import get_web_current_user
from common.csrf import csrf_context


web_home_router = APIRouter()
templates = Jinja2Templates(directory='templates', context_processors=[csrf_context])


@web_home_router.get('/', response_class=HTMLResponse)
def index(request: Request):
    current_user = get_web_current_user(request)

    stats = get_home_stats()
    recent_topics = get_recent_topics()
    popular_topics = get_topics_by_replies()

    return templates.TemplateResponse(request=request, name='index.html',
                                      context={'stats' : stats, 'current_user' : current_user, 'recent_topics': recent_topics, 'popular_topics': popular_topics})