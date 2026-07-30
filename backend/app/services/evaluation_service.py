import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.core.exceptions import MethodologyNotFoundError, ValidationError
from backend.app.core.methodology import load_methodology
from backend.app.core.penalty import Penalty
from backend.app.models.audit import AuditLog
from backend.app.models.evaluation import Evaluation
from backend.app.products.coffee.engine import evaluate_coffee
from backend.app.schemas.common import EvaluationStatus
from backend.app.schemas.evaluation import EvaluationCreate, EvaluationUpdate


def _build_audit(
    db: Session, evaluation_id: int, action: str, actor: str | None = None, details: str | None = None
) -> None:
    log = AuditLog(
        evaluation_id=evaluation_id,
        action=action,
        actor=actor,
        details=details,
    )
    db.add(log)


def _status(value: str | None) -> str:
    if value is None:
        return EvaluationStatus.DRAFT.value
    allowed = {e.value for e in EvaluationStatus}
    if value not in allowed:
        raise ValidationError(f"Invalid status '{value}'. Allowed: {sorted(allowed)}")
    return value


def create_evaluation(db: Session, data: EvaluationCreate) -> Evaluation:
    try:
        methodology = load_methodology("coffee", "v1")
    except MethodologyNotFoundError as exc:
        raise ValidationError(str(exc)) from exc

    penalties = [item.to_penalty() for item in data.penalties]
    result = evaluate_coffee(
        sca_score=data.sca_score,
        process_values=data.process_values,
        integrity_values=data.integrity_values,
        penalties=penalties,
        equipment_model=data.equipment_model,
        origin_plan=data.origin_plan,
        evidence_quality=data.evidence_quality,
        methodology=methodology,
    )

    evaluation = Evaluation(
        public_id=str(uuid.uuid4()),
        product="coffee",
        methodology_id=methodology.id,
        methodology_version=methodology.version,
        status=_status(None),
        lot_id=data.lot_id,
        producer=data.producer,
        farm=data.farm,
        country=data.country,
        region=data.region,
        geo_latitude=data.geo_latitude,
        geo_longitude=data.geo_longitude,
        variety=data.variety,
        harvest_date=data.harvest_date,
        process_start_date=data.process_start_date,
        process_end_date=data.process_end_date,
        equipment_model=data.equipment_model,
        origin_plan=data.origin_plan,
        evidence_quality=data.evidence_quality,
        protocol=data.protocol,
        sca_score=data.sca_score,
        process_values=data.process_values,
        integrity_values=data.integrity_values,
        penalties=[p.__dict__ for p in penalties],
        quality_score=result.quality_score,
        process_score=result.process_score,
        integrity_score=result.integrity_score,
        total_penalties=result.penalties,
        nebula_score=result.total_score,
        confidence_level=result.confidence_level,
        classification=result.classification,
        interpretation=result.interpretation,
        components=result.components,
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    _build_audit(db, evaluation.id, "created", details="Evaluation created and scored")
    db.commit()
    return evaluation


def get_evaluation(db: Session, evaluation_id: int | str) -> Evaluation | None:
    if isinstance(evaluation_id, int) or (isinstance(evaluation_id, str) and evaluation_id.isdigit()):
        return db.query(Evaluation).filter(Evaluation.id == int(evaluation_id)).first()
    return db.query(Evaluation).filter(Evaluation.public_id == evaluation_id).first()


def list_evaluations(
    db: Session, *, skip: int = 0, limit: int = 100, product: str | None = None
) -> tuple[list[Evaluation], int]:
    query = db.query(Evaluation)
    if product:
        query = query.filter(Evaluation.product == product)
    total = query.count()
    items = query.order_by(Evaluation.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def update_evaluation(
    db: Session, evaluation: Evaluation, data: EvaluationUpdate, *, actor: str | None = None
) -> Evaluation:
    if data.status is not None:
        evaluation.status = _status(data.status)
    if data.lot_id is not None:
        evaluation.lot_id = data.lot_id
    if data.producer is not None:
        evaluation.producer = data.producer
    if data.farm is not None:
        evaluation.farm = data.farm
    evaluation.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(evaluation)
    _build_audit(db, evaluation.id, "updated", actor=actor, details=data.model_dump_json(exclude_none=True))
    db.commit()
    return evaluation


def recalculate_evaluation(db: Session, evaluation: Evaluation) -> Evaluation:
    """Recalculate an existing evaluation using the methodology version it was created with."""
    methodology = load_methodology(evaluation.product, f"v{evaluation.methodology_version.split('.')[0]}")
    result = evaluate_coffee(
        sca_score=evaluation.sca_score,
        process_values=evaluation.process_values,
        integrity_values=evaluation.integrity_values,
        penalties=[Penalty(**p) for p in evaluation.penalties],
        equipment_model=evaluation.equipment_model,
        origin_plan=evaluation.origin_plan,
        evidence_quality=evaluation.evidence_quality,
        methodology=methodology,
    )
    evaluation.quality_score = result.quality_score
    evaluation.process_score = result.process_score
    evaluation.integrity_score = result.integrity_score
    evaluation.total_penalties = result.penalties
    evaluation.nebula_score = result.total_score
    evaluation.confidence_level = result.confidence_level
    evaluation.classification = result.classification
    evaluation.interpretation = result.interpretation
    evaluation.components = result.components
    evaluation.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(evaluation)
    _build_audit(db, evaluation.id, "recalculated", details="Recalculated with stored methodology")
    db.commit()
    return evaluation
