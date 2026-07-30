import contextlib
import csv
import io
import json
from typing import Any

from sqlalchemy.orm import Session

from backend.app.schemas.evaluation import EvaluationCreate, PenaltyInput
from backend.app.services.evaluation_service import create_evaluation


def _parse_value(value: Any) -> Any:
    if value is None or value == "":
        return None
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            pass
        lower = value.lower()
        if lower in {"true", "false"}:
            return lower == "true"
    return value


def _flatten_record(record: dict[str, Any]) -> dict[str, Any]:
    """Convert a flat imported record into EvaluationCreate-like payload.

    Keys are expected to be prefixed with category, e.g. `process_temperature`
    or `integrity_mass_balance`. Penalties are provided as a JSON string in
    `penalties`.
    """
    payload: dict[str, Any] = {
        "lot_id": record.get("lot_id") or record.get("lot"),
        "producer": record.get("producer"),
        "farm": record.get("farm") or record.get("finca"),
        "country": record.get("country"),
        "region": record.get("region"),
        "geo_latitude": _parse_value(record.get("geo_latitude") or record.get("lat")),
        "geo_longitude": _parse_value(record.get("geo_longitude") or record.get("lon")),
        "variety": record.get("variety") or record.get("variedad"),
        "harvest_date": record.get("harvest_date"),
        "process_start_date": record.get("process_start_date"),
        "process_end_date": record.get("process_end_date"),
        "equipment_model": record.get("equipment_model") or record.get("model") or "insight",
        "origin_plan": record.get("origin_plan") or record.get("plan") or "pro",
        "evidence_quality": _parse_value(record.get("evidence_quality") or record.get("evidence")) or 4,
        "protocol": record.get("protocol"),
        "sca_score": _parse_value(record.get("sca_score") or record.get("sca")) or 0,
        "process_values": {},
        "integrity_values": {},
        "penalties": [],
    }

    if isinstance(record.get("process_values"), dict):
        payload["process_values"] = {
            k: _parse_value(v) for k, v in record["process_values"].items() if _parse_value(v) is not None
        }
    if isinstance(record.get("integrity_values"), dict):
        payload["integrity_values"] = {
            k: _parse_value(v) for k, v in record["integrity_values"].items() if _parse_value(v) is not None
        }

    for key, value in record.items():
        if key.startswith("process_") and key not in ("process_start_date", "process_end_date", "process_values"):
            field = key.replace("process_", "")
            parsed = _parse_value(value)
            if parsed is not None:
                payload["process_values"][field] = parsed
        elif key.startswith("integrity_") and key != "integrity_values":
            field = key.replace("integrity_", "")
            parsed = _parse_value(value)
            if parsed is not None:
                payload["integrity_values"][field] = parsed

    raw_penalties = record.get("penalties")
    if isinstance(raw_penalties, list):
        payload["penalties"] = raw_penalties
    elif raw_penalties and isinstance(raw_penalties, str):
        with contextlib.suppress(json.JSONDecodeError):
            payload["penalties"] = json.loads(raw_penalties)

    # Ensure required integrity keys exist if not provided
    if not payload["integrity_values"]:
        payload["integrity_values"] = {"mass_balance": 90, "documentation": 90}

    return payload


def import_evaluations_from_csv(db: Session, content: str | bytes) -> list[Any]:
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    created = []
    for row in reader:
        payload = _flatten_record(row)
        penalties = [PenaltyInput(**p) for p in payload.pop("penalties", []) if isinstance(p, dict)]
        payload["penalties"] = penalties
        evaluation = create_evaluation(db, EvaluationCreate(**payload))
        created.append(evaluation)
    return created


def import_evaluations_from_json(db: Session, content: str | bytes) -> list[Any]:
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    data = json.loads(content)
    if isinstance(data, dict):
        data = [data]
    created = []
    for item in data:
        payload = _flatten_record(item)
        penalties = [PenaltyInput(**p) for p in payload.pop("penalties", []) if isinstance(p, dict)]
        payload["penalties"] = penalties
        evaluation = create_evaluation(db, EvaluationCreate(**payload))
        created.append(evaluation)
    return created
