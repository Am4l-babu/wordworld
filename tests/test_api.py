import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app


def request(method, path, **kwargs):
    async def send():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            return await client.request(method, path, **kwargs)
    return asyncio.run(send())


def test_health():
    response = request("GET", "/api/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_between_api_and_explanation():
    response = request("POST", "/api/parse", json={"text": "Put a bridge between two houses"})
    assert response.status_code == 200
    result = response.json()
    assert result["actions"][0]["targets"] == ["house", "house"]
    assert result["grounding"] == "rules"
    assert any(span["role"] == "landmark" for span in result["highlights"])


def test_request_validation():
    for body in [{}, {"text": ""}, {"text": "x" * 1401}]:
        assert request("POST", "/api/parse", json=body).status_code == 422
    assert request("POST", "/api/parse", json={"text": "  "}).status_code == 400


def test_unknown_api_route_is_not_served_the_frontend():
    response = request("GET", "/api/does-not-exist")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")


def test_parse_returns_a_labelled_dependency_baseline_and_corpus_scores():
    result = request("POST", "/api/parse", json={"text": "Build two red houses next to the lake"}).json()
    assert result["grounding"] == "rules"
    if result["model"] == "spacy":
        assert result["baseline"] == [{"action": "add", "type": "house", "count": 2, "color": "red", "relation": "near", "target": "lake"}]
    scores = request("GET", "/api/extractors").json()
    assert scores["commands"] >= 550 and set(scores) >= {"rules", "baseline", "agreement", "rules_first_run_exact"}


BACKSLASH = bytes([92])


@pytest.mark.parametrize("body", [
    b'{"text":"' + BACKSLASH + b'ud800 build a house"}',
    b'{"text":"build ' + BACKSLASH + b'udc00 a house"}',
    b'{"text":"\xed\xa0\x80 build a house"}',
])
def test_lone_surrogates_are_rejected_not_a_server_error(body):
    response = request("POST", "/api/parse", content=body, headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/json")
    # FastAPI's default error body echoes the rejected input, which is what crashed serialisation before.
    detail = response.json()["detail"][0]
    assert "input" not in detail and detail["loc"] == ["body", "text"]


def test_valid_unicode_and_escaped_control_characters_still_parse():
    for escaped in (b"ud83d" + BACKSLASH + b"ude00", b"u0000", b"t"):
        body = b'{"text":"build ' + BACKSLASH + escaped + b' a house"}'
        assert request("POST", "/api/parse", content=body, headers={"Content-Type": "application/json"}).status_code == 200


def test_an_unexpected_parser_failure_still_answers_with_json(monkeypatch):
    from backend import main

    def explode(text, context=None):
        raise RuntimeError("boom")
    monkeypatch.setattr(main, "parse", explode)
    response = request("POST", "/api/parse", json={"text": "Add a tree"})
    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    assert "unexpected problem" in response.json()["detail"] and "boom" not in response.text
