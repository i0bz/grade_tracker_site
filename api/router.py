from fastapi import APIRouter
from .auth import auth_router
from .users import users_router
from .user_subjects import user_subjects_router
from .activities import activities_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(user_subjects_router, prefix="/users/{user_id}")
router.include_router(activities_router, prefix="/users/{user_id}/subjects/{subject_code}")