import json

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_evaluation(client: TestClient) -> None:
    payload = {
        "quality_input": 86,
        "process_values": {"temperature": 80, "ph": 80, "orp": 80, "anaerobic": 80, "homogeneity": 80},
        "integrity_values": {"mass_balance": 90, "documentation": 90},
        "penalties": [],
        "equipment_model": "insight",
        "origin_plan": "pro",
        "evidence_quality": 4,
        "lot_id": "NF-2026-001",
        "producer": "Finca Paradero",
    }
    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nebula_score"] == 51.0
    assert data["confidence_level"] == 4
    assert data["classification"] == "En desarrollo"


def test_list_evaluations(client: TestClient) -> None:
    payload = {
        "quality_input": 86,
        "process_values": {"temperature": 80, "ph": 80, "orp": 80, "anaerobic": 80, "homogeneity": 80},
        "integrity_values": {"mass_balance": 90, "documentation": 90},
        "penalties": [],
        "equipment_model": "insight",
        "origin_plan": "pro",
        "evidence_quality": 4,
    }
    client.post("/api/v1/evaluations", json=payload)
    response = client.get("/api/v1/evaluations")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_methodology_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/methodologies/coffee/v1")
    assert response.status_code == 200
    data = response.json()
    assert data["product"] == "coffee"
    assert "process" in data


def test_import_csv(client: TestClient) -> None:
    csv_data = (
        "quality_input,equipment_model,origin_plan,evidence_quality,"
        "process_temperature,process_ph,process_orp,process_anaerobic,process_homogeneity,"
        "integrity_mass_balance,integrity_documentation,lot_id\n"
        "86,insight,pro,4,80,80,80,80,80,90,90,NF-CSV-001\n"
    )
    response = client.post(
        "/api/v1/import/csv",
        files={"file": ("evals.csv", csv_data, "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["imported"] == 1


def test_import_json(client: TestClient) -> None:
    payload = [
        {
            "quality_input": 88,
            "equipment_model": "signature",
            "origin_plan": "enterprise",
            "evidence_quality": 5,
            "process_values": {
                "temperature": 90,
                "ph": 90,
                "orp": 90,
                "anaerobic": 90,
                "biology": 90,
                "homogeneity": 90,
            },
            "integrity_values": {"mass_balance": 95, "documentation": 95},
            "lot_id": "NF-JSON-001",
        }
    ]
    response = client.post(
        "/api/v1/import/json",
        files={"file": ("evals.json", json.dumps(payload), "application/json")},
    )
    assert response.status_code == 200
    assert response.json()["imported"] == 1


def test_export_csv(client: TestClient) -> None:
    payload = {
        "quality_input": 86,
        "process_values": {"temperature": 80, "ph": 80, "orp": 80, "anaerobic": 80, "homogeneity": 80},
        "integrity_values": {"mass_balance": 90, "documentation": 90},
        "penalties": [],
        "equipment_model": "insight",
        "origin_plan": "pro",
        "evidence_quality": 4,
        "lot_id": "NF-EXPORT-001",
    }
    client.post("/api/v1/evaluations", json=payload)
    response = client.get("/api/v1/export/csv")
    assert response.status_code == 200
    assert "lot_id" in response.text
    assert "NF-EXPORT-001" in response.text


def test_evaluation_report(client: TestClient) -> None:
    payload = {
        "quality_input": 86,
        "process_values": {"temperature": 80, "ph": 80, "orp": 80, "anaerobic": 80, "homogeneity": 80},
        "integrity_values": {"mass_balance": 90, "documentation": 90},
        "penalties": [],
        "equipment_model": "insight",
        "origin_plan": "pro",
        "evidence_quality": 4,
        "lot_id": "NF-REPORT-001",
    }
    created = client.post("/api/v1/evaluations", json=payload)
    evaluation_id = created.json()["id"]
    response = client.get(f"/api/v1/evaluations/{evaluation_id}/report")
    assert response.status_code == 200
    data = response.json()
    assert data["schema"] == "nebula-score-evaluation-v1"
    assert data["evaluation"]["lot_id"] == "NF-REPORT-001"
    assert "disclaimer" in data


def test_update_and_recalculate(client: TestClient) -> None:
    payload = {
        "quality_input": 86,
        "process_values": {"temperature": 80, "ph": 80, "orp": 80, "anaerobic": 80, "homogeneity": 80},
        "integrity_values": {"mass_balance": 90, "documentation": 90},
        "penalties": [],
        "equipment_model": "insight",
        "origin_plan": "pro",
        "evidence_quality": 4,
        "lot_id": "NF-UPDATE-001",
    }
    created = client.post("/api/v1/evaluations", json=payload)
    evaluation_id = created.json()["id"]
    response = client.put(
        f"/api/v1/evaluations/{evaluation_id}",
        json={"status": "provisional", "lot_id": "NF-UPDATED-001"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "provisional"
    assert data["lot_id"] == "NF-UPDATED-001"

    recalc = client.post(f"/api/v1/evaluations/{evaluation_id}/calculate")
    assert recalc.status_code == 200
    assert recalc.json()["nebula_score"] == 51.0


def test_create_cacao_evaluation(client: TestClient) -> None:
    payload = {
        "product": "cacao",
        "quality_input": 80,
        "process_values": {"temperature": 80, "ph": 80, "brix": 80, "anaerobic": 80, "homogeneity": 80},
        "integrity_values": {"mass_balance": 90, "documentation": 90},
        "penalties": [],
        "equipment_model": "insight",
        "origin_plan": "pro",
        "evidence_quality": 4,
        "lot_id": "NF-CACAO-001",
        "producer": "Finca Cacao",
    }
    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["product"] == "cacao"
    assert data["nebula_score"] == 63.0


def test_products_lists_cacao(client: TestClient) -> None:
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    ids = {p["id"] for p in data}
    assert "coffee" in ids
    assert "cacao" in ids
    cacao = next(p for p in data if p["id"] == "cacao")
    assert cacao["available"] is True
