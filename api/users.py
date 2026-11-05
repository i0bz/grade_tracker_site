from fastapi import APIRouter, Depends, HTTPException, status
from .auth import verify_session_token
from sqlalchemy import text, Connection
from sqlalchemy.exc import SQLAlchemyError
from database import get_db

users_router = APIRouter(prefix = "/users")



@users_router.post("/{user_id}/logout")
def logout(user_id: int, _ = Depends(verify_session_token), db_connection: Connection = Depends(get_db)):
    try:
        query = text("UPDATE users SET session_token = NULL, token_timestamp = NULL WHERE id = :id")
        db_connection.execute(query, {"id": user_id})
        db_connection.commit()
    except SQLAlchemyError as e:
        db_connection.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR)

