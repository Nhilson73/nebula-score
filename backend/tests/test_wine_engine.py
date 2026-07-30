from backend.app.core.engine import evaluate
from backend.app.core.methodology import load_methodology
from backend.app.products.wine.engine import evaluate_wine


def test_perfect_signature_score() -> None:
    result = evaluate_wine(
        quality_input=100,
        process_values={
            "temperature": 100,
            "ph": 100,
            "brix": 100,
            "maceration": 100,
            "biology": 100,
            "homogeneity": 100,
            "cellar": 100,
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


def test_wine_score_below_min_clamps_quality() -> None:
    methodology = load_methodology("wine", "v1")
    result = evaluate(
        methodology,
        quality_input=60,
        process_values={"temperature": 100, "ph": 100, "brix": 100},
        integrity_values={"mass_balance": 100, "documentation": 100},
        penalties=[],
        equipment_model="essential",
        origin_plan="enterprise",
        evidence_quality=5,
    )
    assert result.quality_score == 0.0
    assert result.total_score == 40.0


def test_wine_score_normalization() -> None:
    methodology = load_methodology("wine", "v1")
    result = evaluate(
        methodology,
        quality_input=85,
        process_values={"temperature": 100, "ph": 100, "brix": 100},
        integrity_values={"mass_balance": 100, "documentation": 100},
        penalties=[],
        equipment_model="essential",
        origin_plan="enterprise",
        evidence_quality=5,
    )
    assert result.quality_score == 50.0


def test_insight_model_weights() -> None:
    methodology = load_methodology("wine", "v1")
    result = evaluate(
        methodology,
        quality_input=85,
        process_values={"temperature": 80, "ph": 80, "brix": 80, "maceration": 80, "homogeneity": 80},
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


def test_confidence_limited_by_equipment() -> None:
    methodology = load_methodology("wine", "v1")
    result = evaluate_wine(
        quality_input=90,
        process_values={"temperature": 80, "ph": 80, "brix": 80},
        integrity_values={"mass_balance": 80, "documentation": 80},
        penalties=[],
        equipment_model="essential",
        origin_plan="enterprise",
        evidence_quality=5,
        methodology=methodology,
    )
    assert result.confidence_level == 2
