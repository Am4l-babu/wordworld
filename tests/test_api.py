import asyncio
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
