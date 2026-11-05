from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, model_validator
from .auth import verify_session_token
from sqlalchemy import Connection, text
from database import get_db

activities_router = APIRouter(prefix="/activities")

class ActivityBody(BaseModel):
    activity_name: str
    activity_type: str
    points: int
    max_points: int

    @model_validator(mode="after")
    def check_enum(self):
        if self.activity_type != "Activity" and self.activity_type != "Major Exam" and self.activity_type != "Final Output":
            raise ValueError("Invalid activity type")
        return self

    @model_validator(mode="after")
    def check_points_overflow(self):
        if self.points > self.max_points:
            raise ValueError("Points must be lesser than max points")
        return self


class ActivityResponseBody(ActivityBody):
    id: int


@activities_router.post("/")
def add_activity(user_id: int, subject_code: str, payload: ActivityBody, _ = Depends(verify_session_token), db_connection: Connection = Depends(get_db)):
    query = text("SELECT * FROM user_subjects WHERE user_id = :user_id AND subject_code = :subject_code")
    query_parameters = {"user_id": user_id, "subject_code": subject_code}
    existing_subject = db_connection.execute(query, query_parameters).first()

    if not existing_subject:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = "No such subject associated with this user")
    try:
        query = text("""INSERT INTO activities (activity_name, activity_type, points, max_points, user_id, subject_code)
                        VALUES (:activity_name, :activity_type, :points, :max_points, :user_id, :subject_code)""")
        query_parameters |= payload.model_dump()

        db_connection.execute(query, query_parameters)
        db_connection.commit()
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                            detail = str(e))

    return {"message": "Activity added successfully"}



@activities_router.get("/", response_model=list[ActivityResponseBody])
def get_activities(user_id: int, subject_code: str, _ = Depends(verify_session_token), db_connection: Connection = Depends(get_db)):
    query = text("SELECT * FROM user_subjects WHERE user_id = :user_id AND subject_code = :subject_code")
    query_parameters = {"user_id": user_id, "subject_code": subject_code}
    existing_subject = db_connection.execute(query, query_parameters).first()

    if not existing_subject:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
        detail = "No such subject associated with this user")

    query = text("SELECT * FROM activities WHERE user_id = :user_id AND subject_code = :subject_code")

    return db_connection.execute(query, {"user_id": user_id, "subject_code": subject_code}).mappings().all()


@activities_router.put("/{activity_id}")
def update_activity(user_id: int, subject_code: str, activity_id: int, payload: ActivityBody, _ = Depends(verify_session_token), db_connection: Connection = Depends(get_db)):
    query_parameters = {"activity_id": activity_id, "user_id": user_id, "subject_code": subject_code}
    try:
        query = text("""UPDATE activities SET activity_name = :activity_name, activity_type = :activity_type, points = :points, max_points = :max_points
                        WHERE id = :id AND user_id = :user_id AND subject_code = :subject_code""")
        query_parameters |= payload.model_dump()

        db_connection.execute(query, query_parameters)
        db_connection.commit()
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                            detail = str(e))




@activities_router.delete("/{activity_id}")
def delete_activity(user_id: int, subject_code: str, activity_id: int, db_connection: Connection = Depends(get_db), _ = Depends(verify_session_token)):
    try:
        query = text("DELETE FROM activities WHERE id = :id AND user_id = :user_id AND subject_code = :subject_code")
        query_parameters = {"id": activity_id, "user_id": user_id, "subject_code": subject_code}
        db_connection.execute(query, query_parameters)
        db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                            detail = str(e))
