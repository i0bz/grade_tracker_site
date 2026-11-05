from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, model_validator
from typing import Optional
from sqlalchemy import Connection, text
from database import get_db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


subjects_router = APIRouter(prefix="/subjects")


class SubjectBody(BaseModel):
    subject_code: str
    subject_name: str
    units: int

    @model_validator(mode="after")
    def valid_units(self):
        if self.units < 1:
            raise ValueError("Invalid units amount")
        return self

    @model_validator(mode="after")
    def valid_string_size(self):
        if len(self.subject_code) > 50 or len(self.subject_name) > 50:
            raise ValueError("Subject code and subject name must be lesser than 50 characters")
        return self


@subjects_router.post("/")
def create_subject(payload: SubjectBody, db_connection: Connection = Depends(get_db)):
    try: 
        query = text("""INSERT INTO subjects (subject_code, subject_name, units)
                        VALUES (:subject_code, :subject_name, :units)""")
        query_parameters = payload.model_dump()

        db_connection.execute(query, query_parameters)
        db_connection.commit()

    except IntegrityError as e:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT,
                            detail = "Subject already exists")

    return {"message": "Subject created successfully"}


@subjects_router.get("/")
def get_subjects(db_connection: Connection = Depends(get_db)):
    query = text("SELECT * FROM subjects")
    return db_connection.execute(query).mappings().all()

@subjects_router.delete("/{subject_code}")
def delete_subject(subject_code: str, db_connection: Connection = Depends(get_db)):
    query = text("DELETE FROM subjects WHERE subject_code = :subject_code")
    query_parameters = {"subject_code": subject_code}

    try:
        db_connection.execute(query, query_parameters)
        db_connection.commit()

    except SQLAlchemyError as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR)

@subjects_router.put("/{subject_code}")
def update_subject(subject_code: str, payload: SubjectBody, db_connection: Connection = Depends(get_db)):
    query_parameters = {"subject_code" : subject_code}
    query_parameters |= payload.model_dump()
    query = text("""UPDATE subjects SET subject_code = :subject_code, subject_name = :subject_name, units = :units
                    WHERE subject_code = :subject_code""")

    try:
        result = db_connection.execute(query, query_parameters)
        db_connection.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)