from fastapi import APIRouter, Depends, HTTPException, status
from decimal import Decimal
from pydantic import BaseModel, Field, model_validator
from typing import Optional
from .auth import verify_session_token
from sqlalchemy import Connection, text
from database import get_db

user_subjects_router = APIRouter(prefix = "/subjects")

class UserSubjectBody(BaseModel):
    subject_code: str
    activity_split: Decimal = Field(max_digits=5, decimal_places=2)
    major_exam_split: Decimal = Field(max_digits=5, decimal_places=2)
    final_output_split: Decimal = Field(max_digits=5, decimal_places=2)

    @model_validator(mode="after")
    def validate_splits(self):
        if (self.activity_split + self.major_exam_split + self.final_output_split) != Decimal('1.00'):
            raise ValueError("Splits must equate to 100%")
        return self

class UserSubjectUpdateBody(UserSubjectBody):
    subject_code: Optional[str] = None


class SubjectResponse(UserSubjectBody):
    subject_name: str
    units: int


@user_subjects_router.post("/")
def add_user_subject(user_id: int, payload: UserSubjectBody, db_connection: Connection = Depends(get_db), _ = Depends(verify_session_token)):
    query_parameters = {"user_id": user_id}
    try:
        query = text("""INSERT INTO user_subjects (user_id, subject_code, activity_split, major_exam_split, final_output_split)
                        VALUES (:user_id, :subject_code, :activity_split, :major_exam_split, :final_output_split)""")
        query_parameters = payload.model_dump()
        
        db_connection.execute(query, query_parameters)
        db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR)
    return {"message": "Subject created successfully"}



@user_subjects_router.get("/", response_model = list[SubjectResponse])
def get_user_subjects(user_id: int, db_connection: Connection = Depends(get_db), _ = Depends(verify_session_token)):


    query = text("""SELECT subjects.subject_code, subjects.subject_name, subjects.units, user_subjects.activity_split, user_subjects.major_exam_split, user_subjects.final_output_split
                    FROM user_subjects
                    LEFT JOIN subjects ON subjects.subject_code = user_subjects.subject_code
                    WHERE user_subjects.user_id = :user_id""")
    query_parameters = {"user_id": user_id}
    
    return db_connection.execute(query,query_parameters).mappings().all()


@user_subjects_router.put("/{subject_code}")
def update_user_subject(user_id: int, subject_code: str, payload: UserSubjectUpdateBody, db_connection: Connection = Depends(get_db), _ = Depends(verify_session_token)):
    query_parameters = {"user_id": user_id, "subject_code": subject_code}
    try:
        query = text("""UPDATE user_subjects SET activity_split = :activity_split, major_exam_split = :major_exam_split, final_output_split = :final_output_split
                        WHERE user_id = :user_id AND subject_code = :subject_code""")
        query_parameters |= payload.model_dump()
        
        result = db_connection.execute(query, query_parameters)
        db_connection.commit()

        if (result.rowcount == 0):
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND)

    except Exception as e:
        db_connection.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR)

@user_subjects_router.delete("/{subject_code}")
def delete_user_subject(user_id: int, subject_code: str, db_connection: Connection = Depends(get_db), _ = Depends(verify_session_token)):
    try:
        query = text("DELETE FROM user_subjects WHERE user_id = :user_id AND subject_code = :subject_code")
        query_parameters = {"user_id": user_id, "subject_code": subject_code}
        db_connection.execute(query, query_parameters)
        db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR)