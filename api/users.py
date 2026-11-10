from fastapi import APIRouter, Depends, HTTPException, status
from .auth import verify_session_token
from pydantic import BaseModel
from sqlalchemy import text, Connection
from sqlalchemy.exc import SQLAlchemyError
from database import get_db

users_router = APIRouter(prefix = "/users")

class ActivityResponse(BaseModel):
    id: int
    subject_code: str
    activity_name: str
    activity_type: str
    points: int
    max_points: int


@users_router.post("/{user_id}/logout")
def logout(user_id: int, _ = Depends(verify_session_token), db_connection: Connection = Depends(get_db)):
    try:
        query = text("UPDATE users SET session_token = NULL, token_timestamp = NULL WHERE id = :id")
        db_connection.execute(query, {"id": user_id})
        db_connection.commit()
    except SQLAlchemyError as e:
        db_connection.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR)


@users_router.get("/{user_id}/activities/", response_model=list[ActivityResponse])
def get_all_activities(user_id: int, _ = Depends(verify_session_token), db_connection: Connection = Depends(get_db)):
    query = text("SELECT id, subject_code, activity_name, activity_type, points, max_points FROM activities WHERE user_id = :user_id")
    query_params = {"user_id": user_id}
    return db_connection.execute(query,query_params).mappings().all()
