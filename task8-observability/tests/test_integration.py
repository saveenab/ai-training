import pytest
import requests

BASE_URL = "http://recall-agent-alb-1269439320.us-east-1.elb.amazonaws.com"

def post_query(query: str) -> requests.Response:
    return requests.post(
        f"{BASE_URL}/query",
        json={"query": query},
        timeout=60
    )

def test_health_check():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_valid_make_model_year():
    r = post_query("Are there any recalls for a 2020 Ford F-150?")
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    assert len(data["response"]) > 0
    assert "latency_ms" in data
    assert data["model"] == "claude-sonnet-4-6"

def test_vin_query():
    r = post_query("Check recalls for VIN 1FTFW1ET5DFC10312")
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    assert len(data["response"]) > 0

def test_empty_query():
    r = post_query("")
    assert r.status_code in [400, 422, 500]

def test_whitespace_only_query():
    r = post_query("   ")
    assert r.status_code in [200, 400, 422, 500]

def test_very_long_input():
    long_query = "What recalls exist for a 2020 Ford F-150? " * 50
    r = post_query(long_query)
    assert r.status_code in [200, 500]
    assert r.elapsed.total_seconds() < 60

def test_car_not_in_dataset():
    r = post_query("Are there any recalls for a 2022 Lamborghini Huracan?")
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    assert len(data["response"]) > 0

def test_vin_only_no_context():
    r = post_query("1HGBH41JXMN109186")
    assert r.status_code == 200
    data = r.json()
    assert "response" in data

def test_very_old_vehicle():
    r = post_query("Are there recalls for a 1985 Ford Mustang?")
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    assert len(data["response"]) > 0

def test_non_vehicle_question():
    r = post_query("What is the weather today in New York?")
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
