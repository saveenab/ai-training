import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from nhtsa_fetcher import fetch_recalls, parse_recall, fetch_all_recalls
from db import get_connection, upsert_recalls, get_record_count

# --- nhtsa_fetcher tests ---

def test_parse_recall_returns_correct_fields():
    raw = {
        "NHTSACampaignNumber": "21V123000",
        "Component": "AIR BAGS",
        "Summary": "Airbag may not deploy",
        "Consequence": "Injury risk",
        "Remedy": "Replace airbag",
        "ReportReceivedDate": "/Date(1609459200000)/",
        "ModelYear": "2020"
    }
    result = parse_recall(raw, "Ford", "F-150")
    assert result["recall_id"] == "21V123000"
    assert result["make"] == "Ford"
    assert result["model"] == "F-150"
    assert result["component"] == "AIR BAGS"

@patch("nhtsa_fetcher.requests.get")
def test_fetch_recalls_returns_list(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"results": [{"NHTSACampaignNumber": "21V123000", "Component": "BRAKES", "Summary": "test", "Consequence": "test", "Remedy": "test", "ReportReceivedDate": "/Date(1609459200000)/", "ModelYear": "2020"}]}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    results = fetch_recalls("Ford", "F-150", 2020)
    assert isinstance(results, list)
    assert len(results) == 1

@patch("nhtsa_fetcher.requests.get")
def test_fetch_recalls_handles_http_error(mock_get):
    from requests.exceptions import HTTPError
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError("400 Bad Request")
    mock_get.return_value = mock_response
    results = fetch_recalls("Ford", "F-150", 2020)
    assert results == []

# --- db tests ---

@patch("db.psycopg2.connect")
def test_get_connection_called_with_env_vars(mock_connect):
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_NAME"] = "recalls_db"
    os.environ["DB_USER"] = "postgres"
    os.environ["DB_PASS"] = "postgres"
    get_connection()
    assert mock_connect.called

@patch("db.execute_values")
def test_upsert_recalls_calls_execute_values(mock_execute):
    mock_conn = MagicMock()
    records = [{
        "recall_id": "21V123000",
        "title": "Brake Recall",
        "category": "BRAKES",
        "component": "BRAKES",
        "description": "test description",
        "consequence": "test",
        "remedy": "test",
        "report_date": None,
        "make": "Ford",
        "model": "F-150",
        "year": "2020"
    }]
    upsert_recalls(mock_conn, records)
    assert mock_execute.called
    
@patch("db.psycopg2.connect")
def test_get_record_count_returns_int(mock_connect):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=MagicMock(fetchone=MagicMock(return_value=[271])))
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    count = get_record_count(mock_conn)
    assert isinstance(count, int)