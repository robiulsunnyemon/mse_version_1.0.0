from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.db import get_db
from app.models.dropbox import DropboxModel
from app.schemas.dropbox import DropboxResponse, DropboxCreate, DropboxUpdate
from app.utils.cloudinary_config import upload_image_to_cloudinary
# from app.auth.oauth2 import get_current_user # Un-comment if authentication is required
# from app.models.user import UserModel # Un-comment if authentication is required

router = APIRouter(
    prefix="/dropbox",
    tags=["Dropbox"]
)

@router.post("/", response_model=DropboxResponse, status_code=status.HTTP_201_CREATED)
def create_dropbox(
    title: str = Form(...),
    subtitle: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    # current_user: UserModel = Depends(get_current_user) # Require admin auth if needed
):
    image_url = None
    if image:
        try:
            image_url = upload_image_to_cloudinary(image)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Image upload failed: {str(e)}")

    new_dropbox = DropboxModel(
        title=title,
        subtitle=subtitle,
        description=description,
        url=url,
        image_url=image_url
    )
    
    db.add(new_dropbox)
    db.commit()
    db.refresh(new_dropbox)
    
    return new_dropbox

@router.get("/", response_model=List[DropboxResponse])
def get_all_dropbox(db: Session = Depends(get_db)):
    dropbox_items = db.query(DropboxModel).all()
    return dropbox_items

@router.get("/{id}", response_model=DropboxResponse)
def get_dropbox_by_id(id: int, db: Session = Depends(get_db)):
    dropbox_item = db.query(DropboxModel).filter(DropboxModel.id == id).first()
    if not dropbox_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dropbox with id {id} not found")
    return dropbox_item

@router.put("/{id}", response_model=DropboxResponse)
def update_dropbox(
    id: int,
    title: Optional[str] = Form(None),
    subtitle: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    # current_user: UserModel = Depends(get_current_user) # Require admin auth if needed
):
    dropbox_query = db.query(DropboxModel).filter(DropboxModel.id == id)
    dropbox_item = dropbox_query.first()
    
    if not dropbox_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dropbox with id {id} not found")
        
    update_data = {}
    if title is not None: update_data["title"] = title
    if subtitle is not None: update_data["subtitle"] = subtitle
    if description is not None: update_data["description"] = description
    if url is not None: update_data["url"] = url
    
    if image:
        try:
            image_url = upload_image_to_cloudinary(image)
            update_data["image_url"] = image_url
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Image upload failed: {str(e)}")
            
    dropbox_query.update(update_data, synchronize_session=False)
    db.commit()
    db.refresh(dropbox_item)
    
    return dropbox_item

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dropbox(id: int, db: Session = Depends(get_db)):
    dropbox_item = db.query(DropboxModel).filter(DropboxModel.id == id).first()
    if not dropbox_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dropbox with id {id} not found")
        
    db.delete(dropbox_item)
    db.commit()
    return None
