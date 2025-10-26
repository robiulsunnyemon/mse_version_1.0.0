from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.db import get_db
from app.request_and_report.report.model.report import ReportModel
from app.request_and_report.report.schemas.report import ReportRead,ReportCreate

report_router = APIRouter(prefix="/report", tags=["Report & Request"])


# 🔹 GET all
@report_router.get("/", response_model=List[ReportRead], status_code=status.HTTP_200_OK)
async def get_report(db: Session = Depends(get_db)):
    return db.query(ReportModel).all()


# 🔹 POST create
@report_router.post("/", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
async def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    new_report = ReportModel(**report.model_dump())
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report