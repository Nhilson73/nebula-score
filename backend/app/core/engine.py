from dataclasses import dataclass
from typing import Any

from backend.app.core.confidence import compute_confidence
from backend.app.core.exceptions import ValidationError
from backend.app.core.integrity import compute_integrity_score
from backend.app.core.methodology import Methodology, ProcessModelSpec
from backend.app.core.normalization import as_number, clamp, linear_clamp, round_score
from backend.app.core.penalty import Penalty, compute_total_penalties


@dataclass
class ScoreResult:
    product: str
    methodology_id: str
    methodology_version: str
    quality_score: float
    process_score: float
    integrity_score: float
    penalties: float
    total_score: float
    confidence_level: int
    classification: str
    interpretation: str
    components: dict[str, Any]


def _validate_and_normalize_quality(methodology: Methodology, raw_value: float) -> float:
    quality = methodology.quality
    value = clamp(as_number(raw_value), quality.input_range.min, quality.input_range.max)
    normalized = linear_clamp(
        value,
        quality.normalization.min_input,
        quality.normalization.max_input,
        quality.normalization.min_output,
        quality.normalization.max_output,
    )
    return normalized


def _compute_process_score(model: ProcessModelSpec, values: dict[str, float]) -> float:
    total = 0.0
    for field in model.fields:
        raw = values.get(field.id, 0.0)
        total += clamp(raw) * field.weight
    return total


def _classify(methodology: Methodology, score: float) -> tuple[str, str]:
    for band in sorted(methodology.classification.bands, key=lambda b: b.min, reverse=True):
        if score >= band.min:
            return band.label, band.description
    return "Sin clasificación", ""


def evaluate(
    methodology: Methodology,
    *,
    quality_input: float,
    process_values: dict[str, float],
    integrity_values: dict[str, float],
    penalties: list[Penalty],
    equipment_model: str,
    origin_plan: str,
    evidence_quality: int,
) -> ScoreResult:
    """Compute a Nebula Score® evaluation for a methodology and set of inputs."""
    quality_score = _validate_and_normalize_quality(methodology, quality_input)

    process_model = methodology.process.models.get(equipment_model)
    if process_model is None:
        available = ", ".join(methodology.process.models.keys())
        raise ValidationError(f"Process model '{equipment_model}' not found. Available: {available}")
    process_score = _compute_process_score(process_model, process_values)

    integrity_score = compute_integrity_score(methodology.integrity, integrity_values)

    total_penalties = compute_total_penalties(penalties, max_total=methodology.penalties.max_total)

    raw_score = (
        quality_score * methodology.weights.quality
        + process_score * methodology.weights.process
        + integrity_score * methodology.weights.integrity
        - total_penalties
    )
    total_score = clamp(raw_score, methodology.score_range.min, methodology.score_range.max)

    confidence_level = compute_confidence(
        methodology,
        equipment_model=equipment_model,
        plan=origin_plan,
        evidence_quality=evidence_quality,
    )

    classification, interpretation = _classify(methodology, total_score)

    components = {
        "quality": {
            "label": methodology.quality.label,
            "raw_input": round_score(as_number(quality_input), 2),
            "normalized_score": round_score(quality_score),
            "weight": methodology.weights.quality,
            "weighted_score": round_score(quality_score * methodology.weights.quality),
            "warning": methodology.quality.warning,
        },
        "process": {
            "label": methodology.process.label,
            "model": process_model.label,
            "model_formula": process_model.formula,
            "score": round_score(process_score),
            "weight": methodology.weights.process,
            "weighted_score": round_score(process_score * methodology.weights.process),
            "inputs": {
                field.id: round_score(clamp(process_values.get(field.id, 0.0))) for field in process_model.fields
            },
        },
        "integrity": {
            "label": methodology.integrity.label,
            "score": round_score(integrity_score),
            "weight": methodology.weights.integrity,
            "weighted_score": round_score(integrity_score * methodology.weights.integrity),
            "components": {
                key: round_score(clamp(integrity_values.get(key, 0.0))) for key in methodology.integrity.components
            },
        },
        "penalties": {
            "total": round_score(total_penalties),
            "items": [p.__dict__ for p in penalties],
        },
    }

    return ScoreResult(
        product=methodology.product,
        methodology_id=methodology.id,
        methodology_version=methodology.version,
        quality_score=round_score(quality_score),
        process_score=round_score(process_score),
        integrity_score=round_score(integrity_score),
        penalties=round_score(total_penalties),
        total_score=round_score(total_score),
        confidence_level=confidence_level,
        classification=classification,
        interpretation=interpretation,
        components=components,
    )
