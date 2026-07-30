import pytest

from backend.app.core.engine import evaluate
from backend.app.core.exceptions import ValidationError
from backend.app.core.methodology import Methodology, load_methodology
from backend.app.core.penalty import Penalty


@pytest.fixture
def coffee_methodology() -> Methodology:
    return load_methodology("coffee", "v1")


def test_perfect_insight_score(coffee_methodology: Methodology) -> None:
    result = evaluate(
        coffee_methodology,
        sca_score=100,
        process_values={"temperature": 100, "ph": 100, "orp": 100, "anaerobic": 100, "homogeneity": 100},
        integrity_values={"mass_balance": 100, "documentation": 100},
        penalties=[],
        equipment_model="insight",
        origin_plan="enterprise",
        evidence_quality=5,
    )
    assert result.total_score == 100.0
    assert result.confidence_level == 4
    assert result.classification == "Sobresaliente"


def test_sca_below_min_clamps_quality(coffee_methodology: Methodology) -> None:
    result = evaluate(
        coffee_methodology,
        sca_score=70,
        process_values={"temperature": 100, "ph": 100, "orp": 100, "anaerobic": 100, "homogeneity": 100},
        integrity_values={"mass_balance": 100, "documentation": 100},
        penalties=[],
        equipment_model="insight",
        origin_plan="enterprise",
        evidence_quality=5,
    )
    assert result.quality_score == 0.0
    assert result.total_score == 40.0


def test_sca_above_max_uses_max(coffee_methodology: Methodology) -> None:
    result = evaluate(
        coffee_methodology,
        sca_score=105,
        process_values={"temperature": 100, "ph": 100, "orp": 100, "anaerobic": 100, "homogeneity": 100},
        integrity_values={"mass_balance": 100, "documentation": 100},
        penalties=[],
        equipment_model="insight",
        origin_plan="enterprise",
        evidence_quality=5,
    )
    assert result.quality_score == 100.0


def test_penalty_exceeds_subtotal_clamps_zero(coffee_methodology: Methodology) -> None:
    result = evaluate(
        coffee_methodology,
        sca_score=80,
        process_values={"temperature": 0, "ph": 0, "orp": 0, "anaerobic": 0, "homogeneity": 0},
        integrity_values={"mass_balance": 0, "documentation": 0},
        penalties=[Penalty(code="P1", name="Big penalty", category="Critical failure", severity="critical", value=200)],
        equipment_model="insight",
        origin_plan="enterprise",
        evidence_quality=5,
    )
    assert result.total_score == 0.0


def test_confidence_limited_by_plan(coffee_methodology: Methodology) -> None:
    result = evaluate(
        coffee_methodology,
        sca_score=90,
        process_values={"temperature": 80, "ph": 80, "orp": 80, "anaerobic": 80, "homogeneity": 80},
        integrity_values={"mass_balance": 80, "documentation": 80},
        penalties=[],
        equipment_model="insight",
        origin_plan="freemium",
        evidence_quality=5,
    )
    assert result.confidence_level == 1


def test_confidence_limited_by_equipment(coffee_methodology: Methodology) -> None:
    result = evaluate(
        coffee_methodology,
        sca_score=90,
        process_values={"temperature": 80, "ph": 80, "orp": 80},
        integrity_values={"mass_balance": 80, "documentation": 80},
        penalties=[],
        equipment_model="essential",
        origin_plan="enterprise",
        evidence_quality=5,
    )
    assert result.confidence_level == 2


def test_invalid_equipment_model_raises(coffee_methodology: Methodology) -> None:
    with pytest.raises(ValidationError):
        evaluate(
            coffee_methodology,
            sca_score=86,
            process_values={"temperature": 80},
            integrity_values={"mass_balance": 80, "documentation": 80},
            penalties=[],
            equipment_model="nonexistent",
            origin_plan="pro",
            evidence_quality=4,
        )


def test_essential_weights_sum_and_score(coffee_methodology: Methodology) -> None:
    result = evaluate(
        coffee_methodology,
        sca_score=86,
        process_values={"temperature": 80, "ph": 80, "orp": 80},
        integrity_values={"mass_balance": 90, "documentation": 90},
        penalties=[],
        equipment_model="essential",
        origin_plan="pro",
        evidence_quality=4,
    )
    # SCA 86 -> (86-80)/20 * 100 = 30.0
    assert result.quality_score == 30.0
    # Process = 0.35*80 + 0.35*80 + 0.30*80 = 80.0
    assert result.process_score == 80.0
    # Integrity = 0.6*90 + 0.4*90 = 90.0
    assert result.integrity_score == 90.0
    # Total = 0.6*30 + 0.3*80 + 0.1*90 = 18 + 24 + 9 = 51
    assert result.total_score == 51.0
