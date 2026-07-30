import json

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_evaluation(client: TestClient) -> None:
    payload = {
        "sca_score": 86,
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
        "sca_score": 86,
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
        "sca_score,equipment_model,origin_plan,evidence_quality,"
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
            "sca_score": 88,
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
