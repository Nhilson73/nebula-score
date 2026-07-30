"""Coffee-specific evaluation entry point.

This module acts as a thin adapter that loads the Coffee V1 methodology and
runs the generic Nebula Score engine.
"""

from backend.app.core.engine import ScoreResult, evaluate
from backend.app.core.exceptions import ValidationError
from backend.app.core.methodology import Methodology, load_methodology
from backend.app.core.penalty import Penalty

DEFAULT_METHODOLOGY_VERSION = "v1"


def evaluate_coffee(
    *,
    sca_score: float,
    process_values: dict[str, float],
    integrity_values: dict[str, float],
    penalties: list[Penalty],
    equipment_model: str,
    origin_plan: str,
    evidence_quality: int,
    methodology: Methodology | None = None,
) -> ScoreResult:
    """Evaluate a Coffee V1 Nebula Score."""
    if methodology is None:
        methodology = load_methodology("coffee", DEFAULT_METHODOLOGY_VERSION)
    if methodology.product != "coffee":
        raise ValidationError(f"Expected coffee methodology, got {methodology.product}")
    return evaluate(
        methodology,
        sca_score=sca_score,
        process_values=process_values,
        integrity_values=integrity_values,
        penalties=penalties,
        equipment_model=equipment_model,
        origin_plan=origin_plan,
        evidence_quality=evidence_quality,
    )
