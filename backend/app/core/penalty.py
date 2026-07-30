from dataclasses import dataclass
from typing import Any

from backend.app.core.normalization import as_number, clamp


@dataclass
class Penalty:
    code: str
    name: str
    category: str
    severity: str
    value: float
    affected: str | None = None
    description: str | None = None
    justification: str | None = None
    reviewable: bool = True


def compute_total_penalties(
    penalties: list[Penalty],
    max_total: float = 100.0,
) -> float:
    """Sum penalty values and clamp to max_total."""
    total = sum(as_number(p.value) for p in penalties)
    return clamp(total, 0, max_total)


def as_penalty_dict(penalty: Penalty) -> dict[str, Any]:
    return {
        "code": penalty.code,
        "name": penalty.name,
        "category": penalty.category,
        "severity": penalty.severity,
        "value": penalty.value,
        "affected": penalty.affected,
        "description": penalty.description,
        "justification": penalty.justification,
        "reviewable": penalty.reviewable,
    }
