from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import desc
from app.models.race import RaceModel
from app.schemas.race import RaceCreate, RaceUpdate, RaceResponse
from app.db.db import get_db

race_router = APIRouter(prefix="/race", tags=["Race"])


# 🔹 GET all
@race_router.get("/", response_model=List[RaceResponse], status_code=status.HTTP_200_OK)
async def get_races(db: Session = Depends(get_db)):
    return db.query(RaceModel).order_by(desc(RaceModel.serial_number)).all()


# 🔹 POST create
@race_router.post("/", response_model=RaceResponse, status_code=status.HTTP_201_CREATED)
async def create_race(race: RaceCreate, db: Session = Depends(get_db)):
    new_race = RaceModel(**race.model_dump())
    db.add(new_race)
    db.commit()
    db.refresh(new_race)
    return new_race


# 🔹 GET by ID
@race_router.get("/{race_id}", response_model=RaceResponse)
async def get_race(race_id: int, db: Session = Depends(get_db)):
    race = db.query(RaceModel).filter(RaceModel.id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    return race


# 🔹 PUT update
@race_router.put("/{race_id}", response_model=RaceResponse)
async def update_race(race_id: int, race_update: RaceUpdate, db: Session = Depends(get_db)):
    race = db.query(RaceModel).filter(RaceModel.id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    update_data = race_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(race, key, value)

    db.commit()
    db.refresh(race)
    return race


# 🔹 DELETE
@race_router.delete("/{race_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_race(race_id: int, db: Session = Depends(get_db)):
    race = db.query(RaceModel).filter(RaceModel.id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    db.delete(race)
    db.commit()
    return None
