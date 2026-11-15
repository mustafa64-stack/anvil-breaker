# tests/test_browser.py
import pytest
from app.api.endpoints.browser import open_browser_endpoint, OpenBrowserRequest, validate_http_url
from fastapi import HTTPException

def test_validate_http_url_security():
    """Confirms only http and https protocols are allowed, rejecting shell or script vectors."""
    assert validate_http_url("https://cses.fi/problemset/task/weird-algorithm") == "https://cses.fi/problemset/task/weird-algorithm"
    assert validate_http_url("http://leetcode.com/problems/two-sum") == "http://leetcode.com/problems/two-sum"

    with pytest.raises(HTTPException):
        validate_http_url("file:///etc/passwd")

    with pytest.raises(HTTPException):
        validate_http_url("javascript:alert(1)")

def test_open_browser_endpoint_cses_resolution():
    """Confirms that opening a CSES problem in core-path resolves to the true cses.fi URL, not leetcode."""
    req = OpenBrowserRequest(problem_id=11, sheet_slug="core-path")
    res = open_browser_endpoint(req)
    assert res["status"] == "ok"
    assert "cses.fi" in res["url"]
    assert "weird-algorithm" in res["url"]
