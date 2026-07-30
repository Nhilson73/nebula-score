from backend.app.core.methodology import Methodology
from backend.app.core.normalization import clamp


def compute_confidence(
    methodology: Methodology,
    *,
    equipment_model: str,
    plan: str,
    evidence_quality: int,
) -> int:
    """Compute confidence level as the minimum of equipment, plan and evidence caps.

    Parameters are intentionally left as named arguments because they are
    semantically different and order-sensitive.
    """
    process_model = methodology.process.models.get(equipment_model)
    equipment_cap = 0 if process_model is None else process_model.equipment_capability

    plan_cap = methodology.confidence.plan_caps.get(plan.lower(), 0)
    evidence_cap = int(clamp(evidence_quality, 0, methodology.confidence.range.max))

    return min(equipment_cap, plan_cap, evidence_cap)
