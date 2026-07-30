import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from backend.app.core.config import settings
from backend.app.core.exceptions import MethodologyNotFoundError


class RangeSpec(BaseModel):
    min: float
    max: float


class NormalizationSpec(BaseModel):
    type: str
    min_input: float
    max_input: float
    min_output: float
    max_output: float
    formula: str | None = None


class QualitySpec(BaseModel):
    label: str
    input_variable: str
    input_label: str | None = None
    input_range: RangeSpec
    normalization: NormalizationSpec
    warning: str | None = None


class ProcessFieldSpec(BaseModel):
    id: str
    label: str
    weight: float


class ProcessModelSpec(BaseModel):
    label: str
    equipment_capability: int
    formula: str
    fields: list[ProcessFieldSpec]

    @model_validator(mode="after")
    def weights_sum_to_one(self) -> "ProcessModelSpec":
        total = sum(field.weight for field in self.fields)
        if not (0.999 <= total <= 1.001):
            raise ValueError(f"Model {self.label} field weights must sum to 1.0, got {total}")
        return self


class ProcessSpec(BaseModel):
    label: str
    models: dict[str, ProcessModelSpec]


class IntegrityComponentSpec(BaseModel):
    label: str
    weight: float


class IntegritySpec(BaseModel):
    label: str
    components: dict[str, IntegrityComponentSpec]
    note: str | None = None

    @model_validator(mode="after")
    def weights_sum_to_one(self) -> "IntegritySpec":
        total = sum(component.weight for component in self.components.values())
        if not (0.999 <= total <= 1.001):
            raise ValueError(f"Integrity weights must sum to 1.0, got {total}")
        return self


class ConfidenceSpec(BaseModel):
    label: str
    range: RangeSpec
    note: str | None = None
    plan_caps: dict[str, int]


class PenaltiesSpec(BaseModel):
    label: str
    max_total: float
    categories: list[str]


class ClassificationBand(BaseModel):
    min: float
    label: str
    description: str


class ClassificationSpec(BaseModel):
    bands: list[ClassificationBand]


class WeightsSpec(BaseModel):
    quality: float
    process: float
    integrity: float

    @model_validator(mode="after")
    def weights_sum_to_one(self) -> "WeightsSpec":
        total = self.quality + self.process + self.integrity
        if not (0.999 <= total <= 1.001):
            raise ValueError(f"Component weights must sum to 1.0, got {total}")
        return self


class Methodology(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    product: str
    name: str
    version: str
    status: str
    note: str | None = None
    weights: WeightsSpec
    score_range: RangeSpec
    quality: QualitySpec
    process: ProcessSpec
    integrity: IntegritySpec
    confidence: ConfidenceSpec
    penalties: PenaltiesSpec
    classification: ClassificationSpec

    @field_validator("status")
    @classmethod
    def status_allowed(cls, value: str) -> str:
        allowed = {"draft", "experimental", "pilot", "validated", "retired"}
        if value not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return value


def load_methodology(product: str, version: str | None = None) -> Methodology:
    """Load a methodology JSON file from disk."""
    if version is None:
        version = "v1"
    path = settings.methodologies_path / product / f"{version}.json"
    if not path.exists():
        available = [p.stem for p in (settings.methodologies_path / product).glob("*.json")]
        raise MethodologyNotFoundError(
            f"Methodology not found for product '{product}' version '{version}'. Available: {available}"
        )
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return Methodology(**data)


def list_methodologies() -> dict[str, list[str]]:
    """List available methodology files grouped by product."""
    result: dict[str, list[str]] = {}
    if not settings.methodologies_path.exists():
        return result
    for product_dir in sorted(settings.methodologies_path.iterdir()):
        if product_dir.is_dir():
            result[product_dir.name] = sorted(p.stem for p in product_dir.glob("*.json"))
    return result


class MethodologyRegistry:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or settings.methodologies_path

    def get(self, product: str, version: str | None = None) -> Methodology:
        return load_methodology(product, version)

    def list(self) -> dict[str, list[str]]:
        return list_methodologies()
