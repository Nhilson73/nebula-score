from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.core.exceptions import ValidationError
from backend.app.models.evaluation import Evaluation
from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.evaluation import EvaluationCreate, EvaluationResponse, EvaluationUpdate
from backend.app.services.evaluation_service import (
    create_evaluation,
    get_evaluation,
    list_evaluations,
    recalculate_evaluation,
    update_evaluation,
)
from backend.app.services.report_service import export_evaluation_json

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])


@router.get("", response_model=PaginatedResponse)
def get_evaluations(
    skip: int = 0,
    limit: int = 100,
    product: str | None = None,
    db: Session = Depends(get_db),
) -> PaginatedResponse:
    items, total = list_evaluations(db, skip=skip, limit=limit, product=product)
    return PaginatedResponse(
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        page_size=limit,
        items=[_serialize_evaluation(item) for item in items],
    )


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
def get_single_evaluation(evaluation_id: str | int, db: Session = Depends(get_db)) -> Evaluation:
    evaluation = get_evaluation(db, evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation


@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
def post_evaluation(data: EvaluationCreate, db: Session = Depends(get_db)) -> Any:
    try:
        return create_evaluation(db, data)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.put("/{evaluation_id}", response_model=EvaluationResponse)
def put_evaluation(
    evaluation_id: str | int,
    data: EvaluationUpdate,
    db: Session = Depends(get_db),
) -> Any:
    evaluation = get_evaluation(db, evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return update_evaluation(db, evaluation, data)


@router.post("/{evaluation_id}/calculate", response_model=EvaluationResponse)
def calculate_evaluation(
    evaluation_id: str | int,
    db: Session = Depends(get_db),
) -> Any:
    evaluation = get_evaluation(db, evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return recalculate_evaluation(db, evaluation)


@router.get("/{evaluation_id}/report")
def report_evaluation(evaluation_id: str | int, db: Session = Depends(get_db)) -> dict[str, Any]:
    evaluation = get_evaluation(db, evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return export_evaluation_json(evaluation)


def _serialize_evaluation(evaluation: Any) -> dict[str, Any]:
    return EvaluationResponse.model_validate(evaluation).model_dump()
