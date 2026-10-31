import json

from app.services import ai_strategist as ai


def test_strategy_offline_fallback(client):
    r = client.post("/api/ai/channel-strategy", json={"account_id": "yt_zain"})
    assert r.status_code == 200
    d = r.json()
    assert d["source"] == "offline-demo"
    assert d["audience_profile"]["primary_segment"] and len(d["recommendations"]) == 3
    assert d["conclusion"]


def test_analyze_offline_fallback(client):
    d = client.post("/api/ai/analyze", json={"post_id": "yt_zain_p1"}).json()
    assert 1 <= d["hook_strength"] <= 10 and len(d["key_takeaways"]) == 3


def test_ideas_count_and_scope(client):
    d = client.post("/api/ai/ideas", json={"count": 4}).json()
    assert len(d["ideas"]) == 4 and d["scope"] == "All accounts"
    d = client.post("/api/ai/ideas", json={"account_id": "ig_hira", "count": 2}).json()
    assert len(d["ideas"]) == 2 and d["scope"] == "Fit with Hira"


def test_ai_404s(client):
    assert client.post("/api/ai/analyze", json={"post_id": "nope"}).status_code == 404
    assert client.post("/api/ai/channel-strategy", json={"account_id": "nope"}).status_code == 404


def test_gemma_json_is_parsed_when_available(client, monkeypatch):
    reply = "```json\n" + json.dumps({
        "audience_profile": {"primary_segment": "Test segment", "key_traits": ["a"], "inferred_interests": ["b"]},
        "what_worked": ["x"], "recommendations": [{"format": "Short", "topic": "t", "hook": "h", "why": "w"}],
        "posting_advice": "p", "conclusion": "c"}) + "\n```"
    monkeypatch.setattr(ai, "_call_gemma", lambda prompt, image=None: reply)
    d = client.post("/api/ai/channel-strategy", json={"account_id": "yt_zain"}).json()
    assert d["source"] == "gemma" and d["audience_profile"]["primary_segment"] == "Test segment"


def test_bad_gemma_output_falls_back(client, monkeypatch):
    monkeypatch.setattr(ai, "_call_gemma", lambda prompt, image=None: "sorry, I cannot do that")
    d = client.post("/api/ai/ideas", json={"count": 3}).json()
    assert d["source"] == "offline-demo" and len(d["ideas"]) == 3
