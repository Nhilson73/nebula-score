import pytest

from backend.app.core.engine import evaluate
from backend.app.core.methodology import Methodology, load_methodology
from backend.app.products.cacao.engine import evaluate_cacao


@pytest.fixture
def cacao_methodology() -> Methodology:
    return load_methodology("cacao", "v1")


def test_perfect_signature_score(cacao_methodology: Methodology) -> None:
    result = evaluate_cacao(
        quality_input=100,
        process_values={
            "temperature": 100,
            "ph": 100,
            "brix": 100,
            "anaerobic": 100,
            "biology": 100,
            "homogeneity": 100,
            "drying": 100,
        },
        integrity_values={"mass_balance": 100, "documentation": 100},
        penalties=[],
        equipment_model="signature",
        origin_plan="enterprise",
        evidence_quality=5,
    )
    assert result.total_score == 100.0
    assert result.confidence_level == 5
    assert result.classification == "Sobresaliente"


def test_cacao_liquor_below_min_clamps_quality(cacao_methodology: Methodology) -> None:
    result = evaluate(
        cacao_methodology,
        quality_input=50,
        process_values={"temperature": 100, "ph": 100, "brix": 100},
        integrity_values={"mass_balance": 100, "documentation": 100},
        penalties=[],
        equipment_model="essential",
        origin_plan="enterprise",
        evidence_quality=5,
    )
    assert result.quality_score == 0.0
    assert result.total_score == 40.0


def test_cacao_liquor_normalization(cacao_methodology: Methodology) -> None:
    # liquor 80 -> (80-60)/40 * 100 = 50
    result = evaluate(
        cacao_methodology,
        quality_input=80,
        process_values={"temperature": 100, "ph": 100, "brix": 100},
        integrity_values={"mass_balance": 100, "documentation": 100},
        penalties=[],
        equipment_model="essential",
        origin_plan="enterprise",
        evidence_quality=5,
    )
    assert result.quality_score == 50.0


def test_insight_model_weights(cacao_methodology: Methodology) -> None:
    result = evaluate(
        cacao_methodology,
        quality_input=80,
        process_values={"temperature": 80, "ph": 80, "brix": 80, "anaerobic": 80, "homogeneity": 80},
        integrity_values={"mass_balance": 90, "documentation": 90},
        penalties=[],
        equipment_model="insight",
        origin_plan="pro",
        evidence_quality=4,
    )
    # Quality = 50.0; Process = 80.0; Integrity = 90.0
    # Total = 0.6*50 + 0.3*80 + 0.1*90 = 30 + 24 + 9 = 63
    assert result.quality_score == 50.0
    assert result.process_score == 80.0
    assert result.total_score == 63.0


def test_confidence_limited_by_equipment(cacao_methodology: Methodology) -> None:
    result = evaluate_cacao(
        quality_input=90,
        process_values={"temperature": 80, "ph": 80, "brix": 80},
        integrity_values={"mass_balance": 80, "documentation": 80},
        penalties=[],
        equipment_model="essential",
        origin_plan="enterprise",
        evidence_quality=5,
        methodology=cacao_methodology,
    )
    assert result.confidence_level == 2
