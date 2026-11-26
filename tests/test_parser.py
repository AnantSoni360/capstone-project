import pytest
import pandas as pd
from src.parser import HTTPRequestParser

@pytest.fixture
def parser():
    return HTTPRequestParser(max_decode_depth=3)

def test_normal_get_request(parser):
    result = parser.parse_single_request(
        method="GET",
        raw_url="http://localhost:8080/tienda1/index.jsp?category=shoes&page=2 HTTP/1.1",
        body="",
        ground_truth=0
    )
    assert result["method"] == "GET"
    assert result["path"] == "/tienda1/index.jsp"
    assert "category" in result["params"]
    assert result["params"]["category"] == ["shoes"]
    assert result["params"]["page"] == ["2"]
    assert result["ground_truth"] == 0
    assert result["diagnostic_category"] == "BENIGN"

def test_recursive_double_url_decode(parser):
    # %2527 is double-encoded apostrophe (%25 -> %, so %2527 -> %27 -> ')
    double_encoded = "id=%2527%20OR%201%3D1--"
    decoded = parser.recursive_url_decode(double_encoded)
    assert "'" in decoded
    assert "OR" in decoded

def test_sqli_detection_diagnostic(parser):
    result = parser.parse_single_request(
        method="GET",
        raw_url="http://localhost:8080/products?id=1%27%20UNION%20SELECT%20username,password%20FROM%20users-- HTTP/1.1",
        body="",
        ground_truth=1
    )
    assert result["ground_truth"] == 1
    assert result["diagnostic_category"] == "SQL_INJECTION"

def test_xss_detection_diagnostic(parser):
    result = parser.parse_single_request(
        method="POST",
        raw_url="http://localhost:8080/comment.jsp HTTP/1.1",
        body="author=attacker&comment=%3Cscript%3Ealert(1)%3C/script%3E",
        ground_truth=1
    )
    assert result["ground_truth"] == 1
    assert result["diagnostic_category"] == "XSS"
    assert "author" in result["params"]
    assert "comment" in result["params"]

def test_path_traversal_diagnostic(parser):
    result = parser.parse_single_request(
        method="GET",
        raw_url="http://localhost:8080/view.jsp?file=../../../../etc/passwd HTTP/1.1",
        body="",
        ground_truth=1
    )
    assert result["ground_truth"] == 1
    assert result["diagnostic_category"] == "PATH_TRAVERSAL"

def test_deduplication_preserves_unique(parser):
    test_data = pd.DataFrame([
        {"Method": "GET", "URL": "http://localhost:8080/a?id=1", "content": None, "classification": 0},
        {"Method": "GET", "URL": "http://localhost:8080/a?id=1", "content": None, "classification": 0}, # duplicate
        {"Method": "POST", "URL": "http://localhost:8080/b", "content": "x=1", "classification": 1},
    ])
    processed = parser.process_dataframe(test_data, deduplicate=True)
    assert len(processed) == 2
    assert processed["ground_truth"].tolist() == [0, 1]

def test_malformed_input_safety(parser):
    # None and empty strings should not raise exceptions
    result = parser.parse_single_request(method=None, raw_url=None, body=None, ground_truth=0)
    assert result["method"] == "GET"
    assert result["payload_length"] == 0
