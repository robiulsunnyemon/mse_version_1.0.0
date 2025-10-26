from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.db import get_db
from app.request_and_report.request.model.request import RequestModel
from app.request_and_report.request.schemas.request import RequestRead,RequestCreate

request_router = APIRouter(prefix="/request", tags=["Report & Request"])


# 🔹 GET all
@request_router.get("/", response_model=List[RequestRead], status_code=status.HTTP_200_OK)
async def get_request(db: Session = Depends(get_db)):
    return db.query(RequestModel).all()


# 🔹 POST create
@request_router.post("/", response_model=RequestRead, status_code=status.HTTP_201_CREATED)
async def create_request(request: RequestCreate, db: Session = Depends(get_db)):
    new_request = RequestModel(**request.model_dump())
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request