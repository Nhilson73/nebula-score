from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.services.import_service import (
    import_evaluations_from_csv,
    import_evaluations_from_json,
)
from backend.app.services.report_service import export_evaluations_csv

router = APIRouter(prefix="/api/v1", tags=["import-export"])


@router.post("/import/csv")
def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict[str, Any]:
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Expected a CSV file")
    content = file.file.read()
    evaluations = import_evaluations_from_csv(db, content)
    return {
        "imported": len(evaluations),
        "ids": [ev.public_id for ev in evaluations],
    }


@router.post("/import/json")
def import_json(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict[str, Any]:
    if not file.filename or not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Expected a JSON file")
    content = file.file.read()
    evaluations = import_evaluations_from_json(db, content)
    return {
        "imported": len(evaluations),
        "ids": [ev.public_id for ev in evaluations],
    }


@router.get("/export/csv", response_class=PlainTextResponse)
def export_csv(db: Session = Depends(get_db)) -> PlainTextResponse:
    csv_text = export_evaluations_csv(db, limit=1000)
    return PlainTextResponse(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=nebula-score-evaluations.csv"},
    )
