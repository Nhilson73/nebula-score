from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class Product(str, Enum):
    COFFEE = "coffee"
    CACAO = "cacao"
    WINE = "wine"


class MethodologyStatus(str, Enum):
    DRAFT = "draft"
    EXPERIMENTAL = "experimental"
    PILOT = "pilot"
    VALIDATED = "validated"
    RETIRED = "retired"


class EvaluationStatus(str, Enum):
    DRAFT = "draft"
    PROVISIONAL = "provisional"
    VERIFIED = "verified"
    SUSPENDED = "suspended"
    INVALID = "invalid"


class AuditEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    evaluation_id: int
    action: str
    actor: str | None = None
    details: str | None = None
    created_at: datetime


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[dict[str, Any]]
