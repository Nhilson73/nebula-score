from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base, PublicIdMixin, now_utc


class Evaluation(Base, PublicIdMixin):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=now_utc)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=now_utc, nullable=True)

    product: Mapped[str] = mapped_column(String(32), nullable=False, default="coffee")
    methodology_id: Mapped[str] = mapped_column(String(128), nullable=False)
    methodology_version: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")

    lot_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    producer: Mapped[str | None] = mapped_column(String(256), nullable=True)
    farm: Mapped[str | None] = mapped_column(String(256), nullable=True)
    country: Mapped[str | None] = mapped_column(String(128), nullable=True)
    region: Mapped[str | None] = mapped_column(String(256), nullable=True)
    geo_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    geo_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    variety: Mapped[str | None] = mapped_column(String(128), nullable=True)
    harvest_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    process_start_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    process_end_date: Mapped[str | None] = mapped_column(String(32), nullable=True)

    equipment_model: Mapped[str] = mapped_column(String(64), nullable=False, default="insight")
    origin_plan: Mapped[str] = mapped_column(String(64), nullable=False, default="pro")
    evidence_quality: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    protocol: Mapped[str | None] = mapped_column(String(256), nullable=True)

    sca_score: Mapped[float] = mapped_column(Float, nullable=False)
    process_values: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    integrity_values: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    penalties: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)

    quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    process_score: Mapped[float] = mapped_column(Float, nullable=False)
    integrity_score: Mapped[float] = mapped_column(Float, nullable=False)
    total_penalties: Mapped[float] = mapped_column(Float, nullable=False)
    nebula_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_level: Mapped[int] = mapped_column(Integer, nullable=False)
    classification: Mapped[str] = mapped_column(String(128), nullable=False)
    interpretation: Mapped[str | None] = mapped_column(Text, nullable=True)
    components: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
