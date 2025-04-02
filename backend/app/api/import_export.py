# app/api/import_export.py
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db, Item as ItemDB, Container as ContainerDB  # Import SQLAlchemy models
from app.models_db import Item
from app.services.import_export_service import ImportExportService
from typing import Container, List

router = APIRouter()

@router.post("/import/items")
async def import_items(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    import_export_service: ImportExportService = Depends()
):
    """Imports items from a CSV file."""
    try:
        contents = await file.read()
        decoded_contents = contents.decode("utf-8")
        return import_export_service.import_items_from_csv(decoded_contents, db)
    except Exception as e:
        return {"success": False, "itemsImported": 0, "errors": [{"row": 0, "message": f"File processing error: {e}"}]}

@router.post("/import/containers")
async def import_containers(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    import_export_service: ImportExportService = Depends()
):
    """Imports containers from a CSV file."""
    try:
        contents = await file.read()
        decoded_contents = contents.decode("utf-8")
        return import_export_service.import_containers_from_csv(decoded_contents, db)
    except Exception as e:
        return {"success": False, "containersImported": 0, "errors": [{"row": 0, "message": f"File processing error: {e}"}]}

@router.get("/import/check-items", response_model=List[Item])
async def check_items(db: Session = Depends(get_db)):
    """
    Temporary endpoint to check if items were imported.
    """
    items = db.query(ItemDB).all()
    return items

@router.get("/import/check-containers", response_model=List[Container])
async def check_containers(db: Session = Depends(get_db)):
    """
    Temporary endpoint to check if containers were imported.
    """
    containers = db.query(ContainerDB).all()
    return containers