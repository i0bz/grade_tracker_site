from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
from database import get_db
from pydantic import BaseModel
from sqlalchemy import text, Connection
import secrets
import hashlib
from datetime import datetime,timedelta, timezone

auth_router = APIRouter(prefix="/auth")

MAX_TOKEN_LIFE = 12



class AccountBody(BaseModel):
    username: str
    password: str



@auth_router.post("/register")
def register(payload: AccountBody, db_connection: Connection = Depends(get_db)):
    query = text("SELECT id FROM users WHERE username = :username")
    existing_user =  db_connection.execute(query, {"username": payload.username}).first()

    if existing_user:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    hashed_password = hashlib.sha512(payload.password.encode('utf-8')).hexdigest()

    try:
        query = text("INSERT INTO users (username, password_hash) VALUES (:username, :hashed_password)")
        
        db_connection.execute(query, {"username": payload.username,
                                        "hashed_password": hashed_password
                                        })
        db_connection.commit()
        
    except Exception as e:
        db_connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

        
    return {"message": "User registered successfully"}




@auth_router.post("/login")
def login(payload: AccountBody, db_connection: Connection = Depends(get_db)):

    query = text("SELECT id, password_hash FROM users WHERE username = :username")
    existing_user =  db_connection.execute(query, {"username": payload.username}).first()

    if not existing_user or existing_user.password_hash != hashlib.sha512(payload.password.encode('utf-8')).hexdigest():
        raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid login information"
            )
    

    session_token = secrets.token_urlsafe(48)
    token_timestamp = datetime.now(timezone.utc)

    try:
        query = text("UPDATE USERS SET session_token = :session_token, token_timestamp = :token_timestamp WHERE id = :id")
        db_connection.execute(query, {"session_token": session_token,
                                      "token_timestamp": token_timestamp,
                                      "id": existing_user.id})
        db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return {"session_token": session_token, "token_type": "bearer", "user_id": existing_user.id}


def verify_session_token(user_id: int, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db_connection: Connection = Depends(get_db)):

    if not credentials or credentials.scheme != "Bearer":
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail = "Missing or Invalid Authorization header") 

    session_token = credentials.credentials
    query = text("SELECT session_token, token_timestamp FROM users WHERE id = :id")
    token_details = db_connection.execute(query, {"id": user_id}).first()

    if not token_details:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                            detail = f"User with id \"{user_id}\" does not exist")


    if token_details.session_token != session_token:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,
                            detail = "Invalid session token")
    
    db_token_timestamp = token_details.token_timestamp.replace(tzinfo = timezone.utc)
    timestamp_diff = datetime.now(timezone.utc) - db_token_timestamp

    if timestamp_diff > timedelta(hours=MAX_TOKEN_LIFE):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail = "Session token has expired")
 
