from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.core.penalty import Penalty


class PenaltyInput(BaseModel):
    code: str
    name: str
    category: str = "Manual override"
    severity: str = "medium"
    value: float = Field(..., ge=0, le=100)
    affected: str | None = None
    description: str | None = None
    justification: str | None = None
    reviewable: bool = True

    def to_penalty(self) -> Penalty:
        return Penalty(**self.model_dump())


class EvaluationCreate(BaseModel):
    lot_id: str | None = Field(default=None, max_length=128)
    producer: str | None = Field(default=None, max_length=256)
    farm: str | None = Field(default=None, max_length=256)
    country: str | None = Field(default=None, max_length=128)
    region: str | None = Field(default=None, max_length=256)
    geo_latitude: float | None = None
    geo_longitude: float | None = None
    variety: str | None = None
    harvest_date: str | None = None
    process_start_date: str | None = None
    process_end_date: str | None = None
    equipment_model: str = "insight"
    origin_plan: str = "pro"
    evidence_quality: int = Field(default=4, ge=0, le=5)
    protocol: str | None = None

    sca_score: float = Field(..., ge=0, le=100)
    process_values: dict[str, float]
    integrity_values: dict[str, float]
    penalties: list[PenaltyInput] = Field(default_factory=list)

    @field_validator("geo_latitude")
    @classmethod
    def validate_latitude(cls, value: float | None) -> float | None:
        if value is None:
            return None
        if not -90 <= value <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return value

    @field_validator("geo_longitude")
    @classmethod
    def validate_longitude(cls, value: float | None) -> float | None:
        if value is None:
            return None
        if not -180 <= value <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        return value


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    public_id: str
    product: str
    methodology_id: str
    methodology_version: str
    status: str
    lot_id: str | None
    producer: str | None
    farm: str | None
    country: str | None
    region: str | None
    geo_latitude: float | None
    geo_longitude: float | None
    variety: str | None
    harvest_date: str | None
    process_start_date: str | None
    process_end_date: str | None
    equipment_model: str
    origin_plan: str
    evidence_quality: int
    protocol: str | None

    sca_score: float
    process_values: dict[str, float]
    integrity_values: dict[str, float]
    penalties: list[dict[str, Any]]

    quality_score: float
    process_score: float
    integrity_score: float
    total_penalties: float
    nebula_score: float
    confidence_level: int
    classification: str
    interpretation: str
    components: dict[str, Any]

    created_at: datetime
    updated_at: datetime | None = None


class EvaluationUpdate(BaseModel):
    status: str | None = None
    lot_id: str | None = None
    producer: str | None = None
    farm: str | None = None
