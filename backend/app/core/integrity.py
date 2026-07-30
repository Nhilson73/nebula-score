from backend.app.core.methodology import IntegritySpec
from backend.app.core.normalization import as_number, clamp


def compute_integrity_score(integrity: IntegritySpec, values: dict[str, float]) -> float:
    """Compute integrity score from weighted components.

    Missing components default to 0. Values are clamped to 0-100.
    """
    total = 0.0
    for key, component in integrity.components.items():
        value = as_number(values.get(key, 0.0))
        total += clamp(value) * component.weight
    return total
