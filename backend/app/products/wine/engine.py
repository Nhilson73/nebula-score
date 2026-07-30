"""Wine-specific evaluation entry point.

This module acts as a thin adapter that loads the Wine V1 methodology and
runs the generic Nebula Score engine.
"""

from backend.app.core.engine import ScoreResult, evaluate
from backend.app.core.exceptions import ValidationError
from backend.app.core.methodology import Methodology, load_methodology
from backend.app.core.penalty import Penalty

DEFAULT_METHODOLOGY_VERSION = "v1"


def evaluate_wine(
    *,
    quality_input: float,
    process_values: dict[str, float],
    integrity_values: dict[str, float],
    penalties: list[Penalty],
    equipment_model: str,
    origin_plan: str,
    evidence_quality: int,
    methodology: Methodology | None = None,
) -> ScoreResult:
    """Evaluate a Wine V1 Nebula Score."""
    if methodology is None:
        methodology = load_methodology("wine", DEFAULT_METHODOLOGY_VERSION)
    if methodology.product != "wine":
        raise ValidationError(f"Expected wine methodology, got {methodology.product}")
    return evaluate(
        methodology,
        quality_input=quality_input,
        process_values=process_values,
        integrity_values=integrity_values,
        penalties=penalties,
        equipment_model=equipment_model,
        origin_plan=origin_plan,
        evidence_quality=evidence_quality,
    )
