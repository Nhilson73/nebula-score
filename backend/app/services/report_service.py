import csv
import hashlib
import io
import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from backend.app.models.evaluation import Evaluation


def _flatten_evaluation(evaluation: Evaluation) -> dict[str, Any]:
    flat = {
        "public_id": evaluation.public_id,
        "product": evaluation.product,
        "methodology_id": evaluation.methodology_id,
        "methodology_version": evaluation.methodology_version,
        "status": evaluation.status,
        "lot_id": evaluation.lot_id,
        "producer": evaluation.producer,
        "farm": evaluation.farm,
        "country": evaluation.country,
        "region": evaluation.region,
        "geo_latitude": evaluation.geo_latitude,
        "geo_longitude": evaluation.geo_longitude,
        "variety": evaluation.variety,
        "harvest_date": evaluation.harvest_date,
        "process_start_date": evaluation.process_start_date,
        "process_end_date": evaluation.process_end_date,
        "equipment_model": evaluation.equipment_model,
        "origin_plan": evaluation.origin_plan,
        "evidence_quality": evaluation.evidence_quality,
        "protocol": evaluation.protocol,
        "sca_score": evaluation.sca_score,
        "nebula_score": evaluation.nebula_score,
        "quality_score": evaluation.quality_score,
        "process_score": evaluation.process_score,
        "integrity_score": evaluation.integrity_score,
        "total_penalties": evaluation.total_penalties,
        "confidence_level": evaluation.confidence_level,
        "classification": evaluation.classification,
        "interpretation": evaluation.interpretation,
        "created_at": evaluation.created_at.isoformat() if evaluation.created_at else None,
    }
    for key, value in evaluation.process_values.items():
        flat[f"process_{key}"] = value
    for key, value in evaluation.integrity_values.items():
        flat[f"integrity_{key}"] = value
    return flat


def export_evaluation_json(evaluation: Evaluation) -> dict[str, Any]:
    return {
        "schema": "nebula-score-evaluation-v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "hash": hashlib.sha256(json.dumps(evaluation.components, sort_keys=True, default=str).encode()).hexdigest()[
            :16
        ],
        "evaluation": {
            "public_id": evaluation.public_id,
            "product": evaluation.product,
            "methodology_id": evaluation.methodology_id,
            "methodology_version": evaluation.methodology_version,
            "status": evaluation.status,
            "lot_id": evaluation.lot_id,
            "producer": evaluation.producer,
            "farm": evaluation.farm,
            "country": evaluation.country,
            "region": evaluation.region,
            "geo_latitude": evaluation.geo_latitude,
            "geo_longitude": evaluation.geo_longitude,
            "variety": evaluation.variety,
            "harvest_date": evaluation.harvest_date,
            "process_start_date": evaluation.process_start_date,
            "process_end_date": evaluation.process_end_date,
            "equipment_model": evaluation.equipment_model,
            "origin_plan": evaluation.origin_plan,
            "evidence_quality": evaluation.evidence_quality,
            "protocol": evaluation.protocol,
            "sca_score": evaluation.sca_score,
            "process_values": evaluation.process_values,
            "integrity_values": evaluation.integrity_values,
            "penalties": evaluation.penalties,
            "nebula_score": evaluation.nebula_score,
            "quality_score": evaluation.quality_score,
            "process_score": evaluation.process_score,
            "integrity_score": evaluation.integrity_score,
            "total_penalties": evaluation.total_penalties,
            "confidence_level": evaluation.confidence_level,
            "classification": evaluation.classification,
            "interpretation": evaluation.interpretation,
            "components": evaluation.components,
            "created_at": evaluation.created_at.isoformat() if evaluation.created_at else None,
        },
        "disclaimer": "Nebula Score® es un modelo técnico en validación y no sustituye certificaciones oficiales.",
    }


def export_evaluations_csv(db: Session, *, limit: int = 1000) -> str:
    evaluations = db.query(Evaluation).order_by(Evaluation.created_at.desc()).limit(limit).all()
    if not evaluations:
        return ""
    rows = [_flatten_evaluation(ev) for ev in evaluations]
    fieldnames = list(rows[0].keys())
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def build_printable_report(evaluation: Evaluation) -> dict[str, Any]:
    return export_evaluation_json(evaluation)
