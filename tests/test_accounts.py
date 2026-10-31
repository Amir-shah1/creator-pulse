def test_list_accounts(client):
    assert len(client.get("/api/accounts").json()) == 6


def test_add_multiple_accounts_same_platform(client):
    for handle in ("@alpha.creator", "@beta.creator"):
        r = client.post("/api/accounts", json={"platform": "instagram", "handle": handle})
        assert r.status_code == 201
    assert client.get("/api/leaderboard", params={"platform": "instagram"}).json()["total"] == 4


def test_added_account_has_audience_and_posts(client):
    acc = client.post("/api/accounts", json={"platform": "youtube", "handle": "newguy"}).json()
    assert acc["audience"]["top_countries"]
    assert len(client.get(f"/api/accounts/{acc['id']}/posts").json()) == 5


def test_duplicate_rejected(client):
    body = {"platform": "facebook", "handle": "same_page"}
    assert client.post("/api/accounts", json=body).status_code == 201
    assert client.post("/api/accounts", json=body).status_code == 400


def test_remove_and_restore_seed_account(client):
    assert client.delete("/api/accounts/yt_zain").status_code == 200
    assert client.get("/api/accounts/yt_zain").status_code == 404
    r = client.post("/api/accounts", json={"platform": "youtube", "handle": "https://youtube.com/@techtalkszain/"})
    assert r.status_code == 201 and r.json()["id"] == "yt_zain"


def test_unknown_account_404(client):
    assert client.delete("/api/accounts/nope").status_code == 404


def test_handle_too_short_rejected(client):
    assert client.post("/api/accounts", json={"platform": "youtube", "handle": "x"}).status_code == 422


def test_thumbnail_placeholder_is_svg(client):
    r = client.get("/api/thumb/yt_zain_p1")
    assert r.status_code == 200 and r.headers["content-type"].startswith("image/svg+xml")
