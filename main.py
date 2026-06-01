# Saveena Boga - Task 3 FastAPI + SQLAlchemy

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Annotated

from database import engine, SessionLocal, Base
from models import Classification

from tasks import process_classification

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Pydantic models
class ClassifyRequest(BaseModel):
    text: str

class ClassifyResponse(BaseModel):
    id: int
    text: str
    label: str

class ResultResponse(BaseModel):
    id: int
    text: str
    label: str
    status: str

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# Endpoints
@app.post("/classify")
async def classify(request: ClassifyRequest, db: db_dependency):
    record = Classification(text=request.text, label="positive")
    db.add(record)
    db.commit()
    db.refresh(record)
    return ClassifyResponse(id=record.id, text=record.text, label=record.label)

@app.get("/results/{id}")
async def get_results(id: int, db: db_dependency):
    record = db.query(Classification).filter(Classification.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return ResultResponse(id=record.id, text=record.text, label=record.label, status="complete")

@app.post("/classify-async")
async def classify_async(request: ClassifyRequest):
    task = process_classification.delay(request.text)
    return {"task_id": task.id, "status": "processing"}