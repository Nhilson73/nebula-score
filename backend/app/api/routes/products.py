from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/products", tags=["products"])

PRODUCTS = [
    {
        "id": "coffee",
        "name": "Nebula Score® Coffee",
        "description": "Evaluación de calidad sensorial, fermentación e integridad para café.",
        "available": True,
    },
    {
        "id": "cacao",
        "name": "Nebula Score® Cacao",
        "description": "Evaluación de fermentación, defectos, calidad física y trazabilidad para cacao.",
        "available": False,
    },
    {
        "id": "wine",
        "name": "Nebula Score® Wine",
        "description": "Evaluación sensorial, cinética fermentativa y estabilidad para vinos.",
        "available": False,
    },
]


@router.get("")
def list_products() -> list[dict[str, Any]]:
    return PRODUCTS
