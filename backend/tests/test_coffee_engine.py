import pytest

from backend.app.core.exceptions import ValidationError
from backend.app.core.methodology import Methodology, load_methodology
from backend.app.products.coffee.engine import evaluate_coffee


@pytest.fixture
def coffee_methodology() -> Methodology:
    return load_methodology("coffee", "v1")


def test_evaluate_coffee(coffee_methodology: Methodology) -> None:
    result = evaluate_coffee(
        quality_input=86,
        process_values={"temperature": 80, "ph": 80, "orp": 80},
        integrity_values={"mass_balance": 90, "documentation": 90},
        penalties=[],
        equipment_model="essential",
        origin_plan="pro",
        evidence_quality=4,
        methodology=coffee_methodology,
    )
    assert result.product == "coffee"
    assert result.total_score == 51.0


def test_evaluate_coffee_rejects_cacao_methodology(coffee_methodology: Methodology) -> None:
    cacao_methodology = load_methodology("cacao", "v1")
    with pytest.raises(ValidationError):
        evaluate_coffee(
            quality_input=80,
            process_values={"temperature": 80, "ph": 80, "orp": 80},
            integrity_values={"mass_balance": 80, "documentation": 80},
            penalties=[],
            equipment_model="essential",
            origin_plan="pro",
            evidence_quality=4,
            methodology=cacao_methodology,
        )
