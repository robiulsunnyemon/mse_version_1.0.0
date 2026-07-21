from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import asc
from app.models.race import RaceModel
from app.schemas.race import RaceResponse
from app.db.db import get_db
from app.utils.cloudinary_config import upload_image_to_cloudinary

race_router = APIRouter(prefix="/race", tags=["Race"])


# 🔹 GET all
@race_router.get("/", response_model=List[RaceResponse], status_code=status.HTTP_200_OK)
async def get_races(db: Session = Depends(get_db)):
    return db.query(RaceModel).order_by(asc(RaceModel.serial_number)).all()


# 🔹 POST create with Form data & Cloudinary Image Upload
@race_router.post("/", response_model=RaceResponse, status_code=status.HTTP_201_CREATED)
async def create_race(
    serial_number: int = Form(...),
    name: str = Form(...),
    image_logo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # ১. ডাটাবেসে চেক করা হচ্ছে এই সিরিয়াল নাম্বারটি অলরেডি আছে কি না
    existing_race = db.query(RaceModel).filter(RaceModel.serial_number == serial_number).first()

    if existing_race:
        # ২. যদি সিরিয়াল নাম্বারটি পাওয়া যায়, তবে ৪০০ স্ট্যাটাস কোড থ্রো করা হবে
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Serial number {serial_number} is already taken at {existing_race.name}. Please provide a unique one."
        )

    # ৩. ইমেজ ফাইল পাঠানো হয়ে থাকলে ক্লাউডিনারিতে আপলোড করা হবে
    image_url = None
    if image_logo:
        try:
            image_url = upload_image_to_cloudinary(image_logo, folder="races")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Image upload failed: {str(e)}"
            )

    # ৪. সিরিয়াল নাম্বার ইউনিক হলে ডাটা সেভ করা হবে
    new_race = RaceModel(
        serial_number=serial_number,
        name=name,
        image_logo=image_url
    )
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


# 🔹 PUT update with Duplicate Serial Number check & Cloudinary Image Upload
@race_router.put("/{race_id}", response_model=RaceResponse)
async def update_race(
    race_id: int,
    serial_number: Optional[int] = Form(None),
    name: Optional[str] = Form(None),
    image_logo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # ১. প্রথমে চেক করি এই আইডির রেসটি আছে কি না
    race = db.query(RaceModel).filter(RaceModel.id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    # ২. চেক করি অন্য কোনো রেসের এই সিরিয়াল নাম্বারটি আছে কি না (নিজের আইডি বাদে)
    if serial_number is not None:
        existing_serial = db.query(RaceModel).filter(
            RaceModel.serial_number == serial_number,
            RaceModel.id != race_id
        ).first()

        if existing_serial:
            raise HTTPException(
                status_code=400,
                detail=f"Serial number {serial_number} already exists at {existing_serial.name}. Please use a unique number."
            )
        race.serial_number = serial_number

    if name is not None:
        race.name = name

    # ৩. নতুন ইমেজ দেওয়া হলে ক্লাউডিনারিতে আপলোড করে লিঙ্ক আপডেট করা হবে
    if image_logo:
        try:
            image_url = upload_image_to_cloudinary(image_logo, folder="races")
            race.image_logo = image_url
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Image upload failed: {str(e)}"
            )

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

