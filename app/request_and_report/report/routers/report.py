from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.db import get_db
from app.request_and_report.report.model.report import ReportModel
from app.request_and_report.report.schemas.report import ReportRead,ReportCreate
from app.auth.model.auth_user import AuthUserModel

report_router = APIRouter(prefix="/report", tags=["Report & Request"])


# 🔹 GET all
@report_router.get("/", response_model=List[ReportRead], status_code=status.HTTP_200_OK)
async def get_report(db: Session = Depends(get_db)):
    return db.query(ReportModel).all()


@report_router.post("/", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
async def create_report(report: ReportCreate, db: Session = Depends(get_db)):

    db_auth_user = db.query(AuthUserModel).filter(AuthUserModel.email == report.user_email).first()

    if not db_auth_user:
        raise HTTPException(status_code=404, detail="User not found")

    new_report = ReportModel(
        user_name=db_auth_user.first_name,
        user_email=report.user_email,
        report_details=report.report_details
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return new_report
