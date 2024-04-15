from fastapi import APIRouter

from .users import user_router
from .events import event_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(router=user_router, prefix="/user")
api_router.include_router(router=event_router, prefix="/events")
