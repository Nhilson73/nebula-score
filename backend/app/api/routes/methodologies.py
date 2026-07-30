from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.core.exceptions import MethodologyNotFoundError
from backend.app.core.methodology import list_methodologies, load_methodology

router = APIRouter(prefix="/api/v1/methodologies", tags=["methodologies"])


class MethodologyListResponse(BaseModel):
    products: dict[str, list[str]]


@router.get("", response_model=MethodologyListResponse)
def list_available_methodologies() -> MethodologyListResponse:
    return MethodologyListResponse(products=list_methodologies())


@router.get("/{product}/{version}")
def get_methodology(product: str, version: str = "v1") -> dict[str, Any]:
    try:
        methodology = load_methodology(product, version)
    except MethodologyNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return methodology.model_dump()
