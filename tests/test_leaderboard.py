def get(client, **params):
    r = client.get("/api/leaderboard", params=params)
    assert r.status_code == 200, r.text
    return r.json()


def test_default_returns_all_six_accounts(client):
    data = get(client)
    assert data["total"] == 6
    assert [row["rank"] for row in data["rows"]] == [1, 2, 3, 4, 5, 6]


def test_rows_sorted_by_views_descending(client):
    for window in ("24h", "36h", "7d", "30d"):
        views = [r["views"] for r in get(client, window=window)["rows"]]
        assert views == sorted(views, reverse=True)


def test_rows_sorted_by_conversions_descending(client):
    gains = [r["follower_gain"] for r in get(client, metric="conversions")["rows"]]
    assert gains == sorted(gains, reverse=True)


def test_platform_filter(client):
    for platform in ("youtube", "instagram", "facebook"):
        rows = get(client, platform=platform)["rows"]
        assert len(rows) == 2
        assert all(r["account"]["platform"] == platform for r in rows)


def test_rank_change_is_zero_for_conversions(client):
    assert all(r["rank_change"] == 0 for r in get(client, metric="conversions")["rows"])


def test_each_row_has_top_post(client):
    assert all(r["top_post"] for r in get(client)["rows"])


def test_invalid_window_rejected(client):
    assert client.get("/api/leaderboard", params={"window": "1y"}).status_code == 422
