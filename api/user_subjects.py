from fastapi import APIRouter, Depends, HTTPException, status
from decimal import Decimal
from pydantic import BaseModel, Field, model_validator
from typing import Optional
from .auth import verify_session_token
from sqlalchemy import Connection, text
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from database import get_db

user_subjects_router = APIRouter(prefix = "/subjects")

class UserSubjectBody(BaseModel):
    subject_code: str
    activity_split: Decimal = Field(max_digits=5, decimal_places=2)
    major_exam_split: Decimal = Field(max_digits=5, decimal_places=2)
    final_output_split: Decimal = Field(max_digits=5, decimal_places=2)

    @model_validator(mode="after")
    def validate_splits(self):
        if (self.activity_split + self.major_exam_split + self.final_output_split) != Decimal('100.00'):
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
        query_parameters |= payload.model_dump()
        
        db_connection.execute(query, query_parameters)
        db_connection.commit()
    except IntegrityError as e:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT,
                            detail = "User subject already exists")
    except SQLAlchemyError as e:
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
    try:
        query = text("""UPDATE user_subjects SET activity_split = :activity_split, major_exam_split = :major_exam_split, final_output_split = :final_output_split
                        WHERE user_id = :user_id AND subject_code = :subject_code""")
        query_parameters = payload.model_dump()
        query_parameters |= {"user_id": user_id, "subject_code": subject_code}
        
        result = db_connection.execute(query, query_parameters)
        db_connection.commit()

        if (result.rowcount == 0):
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND)

    except SQLAlchemyError as e:
        db_connection.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR)

@user_subjects_router.delete("/{subject_code}")
def delete_user_subject(user_id: int, subject_code: str, db_connection: Connection = Depends(get_db), _ = Depends(verify_session_token)):
    try:
        query = text("DELETE FROM user_subjects WHERE user_id = :user_id AND subject_code = :subject_code")
        query_parameters = {"user_id": user_id, "subject_code": subject_code}
        db_connection.execute(query, query_parameters)
        db_connection.commit()
    except SQLAlchemyError as e:
        db_connection.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR)


def percent_to_grade(val: Decimal) -> Decimal:
    if val >= 97:
        return Decimal('1.0')
    if val >= 92:
        return Decimal('1.25')
    if val >= 86:
        return Decimal('1.50')
    if val >= 80:
        return Decimal('1.75')
    if val >= 74:
        return Decimal('2.0')
    if val >= 68:
        return Decimal('2.25')
    if val >= 62:
        return Decimal('2.50')
    if val >= 56:
        return Decimal('2.75')
    if val >= 50:
        return Decimal('3.00')
    if val >= 40:
        return Decimal('4.00')
    else:
        return Decimal('5.00')



class GradeResponse(BaseModel):
    subject_code: str
    subject_name: str
    units: int
    grade: Decimal = Field(max_digits=2,decimal_places=1)

def calculate_grade(points: int, max_points: int) -> Decimal:
    if points == 0:
        return Decimal(0)
    return Decimal(points / max_points)

@user_subjects_router.get("/grades", response_model=list[GradeResponse])
def get_grades(user_id: int, db_connection: Connection = Depends(get_db), _ = Depends(verify_session_token)):
    query_params = {"user_id": user_id};
    query = text("""SELECT * FROM user_subjects 
                    LEFT JOIN subjects ON user_subjects.subject_code = subjects.subject_code
                    WHERE user_id = :user_id""")

    result = db_connection.execute(query, query_params)



    response_data: list[GradeResponse] = []

    for subject_row in result:
        query_params |= {"subject_code": subject_row.subject_code}
        query = text("SELECT * FROM activities WHERE user_id = :user_id AND subject_code = :subject_code")

        subject_info = {"subject_code": subject_row.subject_code, "subject_name": subject_row.subject_name, "units": subject_row.units}
        
        activities = db_connection.execute(query, query_params)
        if (activities.rowcount == 0):
            response_data.append(subject_info | {"grade": Decimal('0')})
            continue

        activity_points: int = 0
        activity_max_points: int = 0
        major_exam_points: int = 0
        major_exam_max_points: int = 0
        final_output_points: int = 0
        final_output_max_points: int = 0

        for activity_row in activities:
            match activity_row.activity_type:
                case "Activity":
                    activity_points += activity_row.points
                    activity_max_points += activity_row.max_points
                case "Major Exam":
                    major_exam_max_points += activity_row.max_points
                    major_exam_points += activity_row.points
                case "Final Output":
                    final_output_max_points += activity_row.max_points
                    final_output_points += activity_row.points

        activity_grade = calculate_grade(activity_points, activity_max_points)
        major_exam_grade = calculate_grade(major_exam_points, major_exam_max_points)
        final_output_grade = calculate_grade(final_output_points, final_output_max_points)

        act_split = Decimal(str(subject_row.activity_split))
        major_split = Decimal(str(subject_row.major_exam_split))
        final_split = Decimal(str(subject_row.final_output_split))

        weighted_grade = (activity_grade * act_split) + (major_exam_grade * major_split) + (final_output_grade * final_split)

        response_data.append(subject_info | {"grade": percent_to_grade(weighted_grade)})

    return response_data

